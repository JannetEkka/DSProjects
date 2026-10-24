"""Request-intent classification: does `request_text` authorize deletion?

Two independent classifiers vote:
  * an LLM (Gemini, JSON-constrained, temperature 0) when GEMINI_API_KEY is set;
  * a deterministic multilingual rule model (negation-aware) that always runs.
A third, independent signal is the privacy-intake CLASSIFY_REQUEST activity in system_activity.csv.
The LLM decides when present; disagreements are surfaced in the run trace for review.
LLM answers are cached by text hash (code/cache/intent.json) so re-runs cost nothing. Uncached texts are
sent in chunks (prefetch) over a model chain with retries (audit.llm: Gemini, then Mistral / Groq / NVIDIA
when their keys are set), so one bad model doesn't end the run.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from . import usage
from .llm import LLMChain, any_key

CACHE = Path(__file__).resolve().parent.parent / "cache" / "intent.json"

INTENT_PROMPT = """You classify customer privacy requests for an e-commerce company.
Decide whether the request AUTHORIZES DELETION / ERASURE of the person's account or personal data.

Return JSON: {{"authorizes_deletion": true|false, "request_type": one of
["DELETION","ACCESS","PORTABILITY","CORRECTION","MARKETING_OPT_OUT","ACCOUNT_SUPPORT","OTHER"],
"language": ISO-639-1 code, "rationale": short English sentence}}

Rules:
- Deletion, erasure, account closure, "remove my profile/personal data", or follow-ups asking to finish
  or verify a deletion all authorize deletion (request_type DELETION).
- Access/copy of data, data download/export, correcting or updating details, stopping marketing,
  login help, invoices are NOT deletion, even if words like "remove" or "delete" appear in a negated or
  limited sense ("remove me from marketing lists only", "don't delete anything").
- The request may be in any language.

Request:
\"\"\"{text}\"\"\""""

# ----------------------------------------------------------------------------- rule model

DELETION_PATTERNS = [
    r"\b(delet\w*|eras\w*|clos\w* (my|this|the) account|remov\w*|account[- ]deletion|forget me|gone)\b",
    r"supprim|suppression|effacer",              # fr
    r"elimin|borrar|suprimir",                    # es
    r"exclus[aã]o|excluir|apagar",                # pt
    r"l[öo]sch|entfern",                          # de
    r"cancell|cancellaz",                         # it
    r"削除|退会|消去",                             # ja
    r"삭제|탈퇴",                                  # ko
    r"删除|注销",                                  # zh
    r"удал",                                      # ru
    r"हटा|मिटा",                                  # hi
    r"احذف|حذف",                                  # ar
]
NEGATION_PATTERNS = [
    r"not asking for (deletion|erasure)", r"not a request to (erase|delete)", r"(do not|don't|dont) (close|delete|remove|erase)",
    r"without (removing|deleting|closing)", r"(keep|leave) (the|my) (account|profile)", r"leave the account active",
    r"continue using", r"still (want|need|use)", r"marketing lists only", r"keep the account as it is",
    r"no (borren|eliminen)", r"ne (supprimez|fermez) pas", r"não (excluam|apaguem)",
]
NON_DELETION_HINTS = {
    "ACCESS": r"what personal information|copy of the information|information request|what data|copy of|invoices",
    "PORTABILITY": r"download my|portable format|export my",
    "CORRECTION": r"out of date|misspelled|correct it|replace it|change the email|update my",
    "MARKETING_OPT_OUT": r"promotional emails|marketing|unsubscribe|newsletter",
    "ACCOUNT_SUPPORT": r"resetting the login|reset (my )?password|can't access|cannot access",
}


def rule_classify(text: str) -> dict:
    """Requests arrive through the deletion workflow, so deletion is the prior. A request is
    NOT a deletion when it explicitly negates deletion, or states a non-deletion purpose
    (access, export, correction, opt-out, login help) without any deletion cue."""
    t = (text or "").lower()
    if not t.strip():
        # an empty request states no purpose at all, so it cannot authorize deletion
        return {"authorizes_deletion": False, "request_type": "OTHER", "engine": "rules",
                "rationale": "empty request text"}
    neg = [p for p in NEGATION_PATTERNS if re.search(p, t)]
    pos = [p for p in DELETION_PATTERNS if re.search(p, t)]
    rtype = next((k for k, p in NON_DELETION_HINTS.items() if re.search(p, t)), None)
    authorizes = not (neg or (rtype and not pos))
    return {"authorizes_deletion": authorizes, "request_type": "DELETION" if authorizes else (rtype or "OTHER"),
            "engine": "rules", "rationale": f"deletion cues={len(pos)} negations={len(neg)} purpose={rtype}"}


# ----------------------------------------------------------------------------- LLM

BATCH_PROMPT = """You classify customer privacy requests for an e-commerce company.
For EACH request decide whether it AUTHORIZES DELETION / ERASURE of the person's account or personal data.

Return a JSON object {{"results": [...]}} with one entry per request, in any order:
[{{"id": <request id>, "authorizes_deletion": true|false, "request_type": one of
["DELETION","ACCESS","PORTABILITY","CORRECTION","MARKETING_OPT_OUT","ACCOUNT_SUPPORT","OTHER"],
"language": ISO-639-1 code, "rationale": short English sentence}}]

Rules:
- Deletion, erasure, account closure, "remove my profile/personal data", or follow-ups asking to finish
  or verify a deletion all authorize deletion (request_type DELETION).
- Access/copy of data, data download/export, correcting or updating details, stopping marketing,
  login help, invoices are NOT deletion, even if words like "remove" or "delete" appear in a negated or
  limited sense ("remove me from marketing lists only", "don't delete anything").
- Each request may be in any language. Judge every request on its own.

Requests (JSON):
{items}"""

CHUNK_SIZE = int(os.environ.get("GEMINI_INTENT_CHUNK", "10"))


def _clean(data: dict, model: str) -> dict:
    return {"authorizes_deletion": bool(data.get("authorizes_deletion")),
            "request_type": data.get("request_type", "OTHER"),
            "language": data.get("language", ""), "rationale": data.get("rationale", ""), "model": model}


class IntentClassifier:
    def __init__(self, model: str | None = None, use_llm: bool = True):
        self.chain = LLMChain(model or os.environ.get("GEMINI_TEXT_MODEL"), tag="intent")
        self.use_llm = use_llm and any_key()
        self.use_cache = use_llm  # --no-llm means rules only, even when cached LLM answers exist
        self.cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    def _save(self):
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(self.cache, indent=1, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def _lookup(self, text: str):
        """Model-agnostic key first, then legacy per-model keys (sha256("model|text"))."""
        key = hashlib.sha256(text.encode()).hexdigest()
        if key in self.cache:
            return self.cache[key]
        for m in self.chain.models:
            legacy = self.cache.get(hashlib.sha256(f"{m[1]}|{text}".encode()).hexdigest())
            if legacy is not None:
                return {**legacy, "model": legacy.get("model", f"{m[0]}:{m[1]}")}
        return None

    def prefetch(self, texts) -> None:
        """Classify every uncached text in chunks of CHUNK_SIZE per call; each chunk is cached as soon as
        it returns, so a run that loses Gemini part-way keeps everything done so far."""
        if not self.use_llm:
            return
        todo = list(dict.fromkeys(t for t in texts if t and t.strip() and self._lookup(t) is None))
        for i in range(0, len(todo), CHUNK_SIZE):
            if not self.chain.available:
                return
            chunk = todo[i:i + CHUNK_SIZE]
            try:
                got = self._ask_batch(chunk)
            except (RuntimeError, ValueError, json.JSONDecodeError):
                continue  # this chunk falls back to per-item calls / rules in classify()
            for text, res in got.items():
                self.cache[hashlib.sha256(text.encode()).hexdigest()] = res
            self._save()

    def classify(self, text: str) -> dict:
        rules = rule_classify(text)
        result = dict(rules)
        if not (text or "").strip():  # nothing to ask a model about
            return {**result, "rules_vote": False, "agreement": True}
        llm = self._lookup(text) if self.use_cache else None
        if llm is not None:
            usage.record_cache_hit("intent")
        elif self.use_llm and self.chain.available:
            try:
                llm = self._ask(text)
                self.cache[hashlib.sha256(text.encode()).hexdigest()] = llm
                self._save()
            except (RuntimeError, ValueError, json.JSONDecodeError):
                pass  # rule model decides this one
        if llm is not None:
            result = {**{k: v for k, v in llm.items() if k != "model"}, "engine": llm.get("model", "llm")}
        result["rules_vote"] = rules["authorizes_deletion"]
        result["agreement"] = result["authorizes_deletion"] == rules["authorizes_deletion"]
        return result

    def _ask(self, text: str) -> dict:
        raw, model = self.chain.generate(INTENT_PROMPT.format(text=text), "intent_classification", json_mode=True)
        return _clean(json.loads(raw), model)

    def _ask_batch(self, texts: list[str]) -> dict:
        items = json.dumps([{"id": i, "text": t} for i, t in enumerate(texts)], ensure_ascii=False, indent=1)
        raw, model = self.chain.generate(BATCH_PROMPT.format(items=items), "intent_classification_batch", json_mode=True)
        data = json.loads(raw)
        if isinstance(data, dict):  # tolerate {"results": [...]}
            data = next((v for v in data.values() if isinstance(v, list)), [])
        out = {}
        for d in data:
            try:
                idx = int(d.get("id"))
            except (TypeError, ValueError):
                continue
            if 0 <= idx < len(texts) and "authorizes_deletion" in d:
                out[texts[idx]] = _clean(d, model)
        return out
