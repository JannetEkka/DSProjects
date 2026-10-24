"""Request-intent classification: does `request_text` authorize deletion?

Two independent classifiers vote:
  * an LLM (Gemini, JSON-constrained, temperature 0) when GEMINI_API_KEY is set;
  * a deterministic multilingual rule model (negation-aware) that always runs.
A third, independent signal is the privacy-intake CLASSIFY_REQUEST activity in system_activity.csv.
The LLM decides when present; disagreements are surfaced in the run trace for review.
LLM answers are cached by text hash (code/cache/intent.json) so re-runs cost nothing.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from . import usage

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
    neg = [p for p in NEGATION_PATTERNS if re.search(p, t)]
    pos = [p for p in DELETION_PATTERNS if re.search(p, t)]
    rtype = next((k for k, p in NON_DELETION_HINTS.items() if re.search(p, t)), None)
    authorizes = not (neg or (rtype and not pos))
    return {"authorizes_deletion": authorizes, "request_type": "DELETION" if authorizes else (rtype or "OTHER"),
            "engine": "rules", "rationale": f"deletion cues={len(pos)} negations={len(neg)} purpose={rtype}"}


# ----------------------------------------------------------------------------- LLM

class IntentClassifier:
    def __init__(self, model: str | None = None, use_llm: bool = True):
        self.model = model or os.environ.get("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
        self.use_llm = use_llm and bool(os.environ.get("GEMINI_API_KEY"))
        self.cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
        self._client = None

    def _save(self):
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(self.cache, indent=1, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def classify(self, text: str) -> dict:
        rules = rule_classify(text)
        result = dict(rules)
        llm = None
        key = hashlib.sha256(f"{self.model}|{text}".encode()).hexdigest()
        if key in self.cache:
            llm = self.cache[key]
            usage.record_cache_hit("intent")
        elif self.use_llm:
            try:
                llm = self._ask(text)
                self.cache[key] = llm
                self._save()
            except Exception as exc:
                print(f"[intent] LLM failed, using rules: {exc!r}")
        if llm is not None:
            result = {**llm, "engine": f"gemini:{self.model}"}
        result["rules_vote"] = rules["authorizes_deletion"]
        result["agreement"] = result["authorizes_deletion"] == rules["authorizes_deletion"]
        return result

    def _ask(self, text: str) -> dict:
        from google import genai
        from google.genai import types

        if self._client is None:
            self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        resp = self._client.models.generate_content(
            model=self.model,
            contents=INTENT_PROMPT.format(text=text),
            config=types.GenerateContentConfig(temperature=0, response_mime_type="application/json"),
        )
        um = getattr(resp, "usage_metadata", None)
        usage.record("gemini", self.model, "intent_classification",
                     getattr(um, "prompt_token_count", 0) or 0, getattr(um, "candidates_token_count", 0) or 0)
        data = json.loads(resp.text)
        return {"authorizes_deletion": bool(data.get("authorizes_deletion")),
                "request_type": data.get("request_type", "OTHER"),
                "language": data.get("language", ""), "rationale": data.get("rationale", "")}
