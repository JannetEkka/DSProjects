"""Request-intent classification: does `request_text` authorize deletion?

Two independent classifiers vote:
  * an LLM (Gemini, JSON-constrained, temperature 0) when GEMINI_API_KEY is set;
  * a deterministic multilingual rule model (negation-aware) that always runs.
A third, independent signal is the privacy-intake CLASSIFY_REQUEST activity in system_activity.csv.
The LLM decides when present, within a strict schema; the rule model vetoes an LLM 'authorizes deletion'
when the text negates deletion or states another purpose, and disagreements are surfaced in the trace.
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
from .prompts import as_untrusted, load_prompt

CACHE = Path(__file__).resolve().parent.parent / "cache" / "intent.json"

INTENT_PROMPT = load_prompt("intent_single")

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
    "ACCESS": r"what personal information|copy of the information|information request|what data|copy of|invoices"
              r"|kopie meiner daten|copia de mis datos|copie de mes données|cópia dos meus dados",
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

BATCH_PROMPT = load_prompt("intent_batch")

CHUNK_SIZE = int(os.environ.get("GEMINI_INTENT_CHUNK", "10"))


REQUEST_TYPES = {"DELETION", "ACCESS", "PORTABILITY", "CORRECTION", "MARKETING_OPT_OUT", "ACCOUNT_SUPPORT", "OTHER"}


def _clean(data, model: str) -> dict | None:
    """Strict schema check of one LLM answer. Anything off-schema (wrong types, a request_type outside
    the enum, authorizes_deletion inconsistent with request_type) is rejected -> the rule model decides."""
    if not isinstance(data, dict):
        return None
    auth, rtype = data.get("authorizes_deletion"), data.get("request_type")
    lang, why = data.get("language", ""), data.get("rationale", "")
    if not isinstance(auth, bool) or rtype not in REQUEST_TYPES or auth != (rtype == "DELETION"):
        return None
    if not isinstance(lang, str) or not isinstance(why, str):
        return None
    return {"authorizes_deletion": auth, "request_type": rtype, "language": lang[:8], "rationale": why[:300],
            "model": model}


INJECTION_RE = re.compile(
    r"^\s*(system|assistant|developer|tool)\s*:.*$"                       # forged role lines
    r"|[^.!?\n]*\b(ignore|disregard|forget)\b[^.!?\n]*\b(previous|prior|above|earlier|all)\b[^.!?\n]*"
    r"\b(instructions?|rules|prompt)\b[^.!?\n]*[.!?]?"
    r"|[^.!?\n]*\b(ignorez|ignorer|ignoriere|ignorieren|ignora|ignore)\b[^.!?\n]*"
    r"\b(instructions|anweisungen|instrucciones|istruzioni|instruções)\b[^.!?\n]*[.!?]?",
    re.I | re.M)


def strip_injection(text: str) -> tuple[str, int]:
    """Remove forged role lines ("SYSTEM: ...") and "ignore previous instructions" sentences: they are
    addressed to a model, not a statement of the customer's purpose, so the rule model must not score
    them. Returns (text without them, number removed)."""
    return INJECTION_RE.subn(" ", text or "")


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
        clean, injected = strip_injection(text)
        rules = rule_classify(clean)
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
            llm = _clean(llm, llm.get("model", "llm"))  # cached answers are re-validated too
        if llm is not None:
            result = {**{k: v for k, v in llm.items() if k != "model"}, "engine": llm["model"]}
            if result["authorizes_deletion"] and not rules["authorizes_deletion"]:
                # veto: the text negates deletion or states a non-deletion purpose without a deletion cue
                result = {**rules, "engine": f"rules (veto over {llm['model']})", "veto": True}
        result["rules_vote"] = rules["authorizes_deletion"]
        result["agreement"] = result["authorizes_deletion"] == rules["authorizes_deletion"] and not result.get("veto")
        if injected:
            result["injection_markers"] = injected
        return result

    def _ask(self, text: str) -> dict:
        raw, model = self.chain.generate(INTENT_PROMPT.format(text=as_untrusted(text)), "intent_classification", json_mode=True)
        res = _clean(json.loads(raw), model)
        if res is None:
            raise ValueError("off-schema intent answer")
        return res

    def _ask_batch(self, texts: list[str]) -> dict:
        items = as_untrusted([{"id": i, "text": t} for i, t in enumerate(texts)])
        raw, model = self.chain.generate(BATCH_PROMPT.format(items=items), "intent_classification_batch", json_mode=True)
        data = json.loads(raw)
        if isinstance(data, dict):  # tolerate {"results": [...]}
            data = next((v for v in data.values() if isinstance(v, list)), [])
        out = {}
        for d in data if isinstance(data, list) else []:
            try:
                idx = int(d.get("id")) if not isinstance(d.get("id"), bool) else -1
            except (TypeError, ValueError, AttributeError):
                continue
            res = _clean(d, model)
            if 0 <= idx < len(texts) and res is not None:
                out[texts[idx]] = res
        return out
