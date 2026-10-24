"""Request-intent classification: does `request_text` authorize deletion?

Two independent classifiers vote:
  * an LLM (Gemini, JSON-constrained, temperature 0) when GEMINI_API_KEY is set;
  * a deterministic multilingual rule model (negation-aware) that always runs.
A third, independent signal is the privacy-intake CLASSIFY_REQUEST activity in system_activity.csv.
The LLM decides when present, within a strict schema, and the deterministic rule model breaks ties,
asymmetrically in favour of not deleting:
  * veto - the LLM says "deletion" but the rule model finds a negated deletion cue (multilingual
    negation tokens inside the cue's clause) or a non-deletion purpose without a cue: authorizing a
    non-deletion would be irreversible, so the rules win;
  * override - the LLM says "not deletion": the rules may overrule it only when the text has a deletion
    cue, no other purpose and no negation-like token anywhere. Otherwise the refusal stands, flagged
    `needs_human_review` (refusing a genuine deletion is a recoverable compliance miss; a wrong
    deletion is not).
Disagreements are recorded in the trace (`override`, `confidence: low`, the LLM's own vote). The rule
model itself needs a positive deletion cue to authorize anything. On this dataset the two models agree on
all 550 texts, so neither rule changes the output.
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
# Negation-like tokens across the request languages. Broad on purpose: used (a) anywhere in the text to
# decide whether the rule model may overrule an LLM refusal, and (b) inside the deletion cue's own
# clause to detect a negated deletion ("Bitte löschen Sie mein Konto nicht", "削除しないでください").
NEGATION_TOKEN_RE = re.compile(
    r"\b(?:not|never|no longer|cannot|rather not|don'?t|didn'?t|doesn'?t|won'?t|wouldn'?t|shouldn'?t|can'?t)\b"
    r"|n['’]t\b"                                                       # en (incl. typographic apostrophe)
    r"|\b(?:nicht|kein|keine|keinen|keinesfalls|niemals|nie)\b"        # de
    r"|\b(?:ne|pas|jamais)\b|\bn['’]"                                 # fr
    r"|\b(?:no|nunca|jamás)\b"                                         # es
    r"|\b(?:non|mai)\b"                                                # it
    r"|\b(?:não|nunca)\b"                                              # pt
    r"|\b(?:niet|nooit|geen)\b"                                        # nl
    r"|しないで|ないで|しない|ません|不要"                                # ja
    r"|하지\s?마|않"                                                     # ko
    r"|不要|别|勿"                                                       # zh
    r"|\b(?:не|нельзя|никогда)\b"                                      # ru
    r"|नहीं|मत\b"                                                       # hi
    r"|(?<![\u0600-\u06FF])لا(?![\u0600-\u06FF])",                    # ar
    re.I)
# phrases that contain a negation token but do not negate the request ("not just the profile")
NEGATION_EXEMPT_RE = re.compile(r"\bnot (?:just|only)\b|\bno matter\b|\bno later than\b", re.I)
CLAUSE_SPLIT_RE = re.compile(r"[.,;:!?\n。、，；！？]")


def has_negation_token(text: str) -> bool:
    """Any negation-like token anywhere in the text (exempt phrases removed)."""
    return bool(NEGATION_TOKEN_RE.search(NEGATION_EXEMPT_RE.sub(" ", text or "")))


def negated_deletion(text: str) -> bool:
    """A deletion cue whose own clause carries a negation token within a few words of it."""
    t = NEGATION_EXEMPT_RE.sub(" ", (text or "").lower())
    for cue in DELETION_PATTERNS:
        for m in re.finditer(cue, t):
            end = m.end() + len(re.match(r"[a-zà-ɏа-яё]*", t[m.end():]).group())  # rest of an alphabetic word ("lösch" -> "löschen"); CJK has no word breaks
            starts = [b.end() for b in CLAUSE_SPLIT_RE.finditer(t, 0, m.start())]
            lo = starts[-1] if starts else 0
            nxt = CLAUSE_SPLIT_RE.search(t, end)
            hi = nxt.start() if nxt else len(t)
            before, after = t[lo:m.start()], t[end:hi]
            window = " ".join(before.split()[-4:]) + " " + before[-8:] + " | " + after[:10] + " " + " ".join(after.split()[:4])
            if NEGATION_TOKEN_RE.search(window):
                return True
    return False


NON_DELETION_HINTS = {
    "ACCESS": r"what personal information|copy of the information|information request|what data|copy of|invoices"
              r"|kopie meiner daten|copia de mis datos|copie de mes données|cópia dos meus dados",
    "PORTABILITY": r"download my|portable format|export my",
    "CORRECTION": r"out of date|misspelled|correct it|replace it|change the email|update my",
    "MARKETING_OPT_OUT": r"promotional emails|marketing|unsubscribe|newsletter",
    "ACCOUNT_SUPPORT": r"resetting the login|reset (my )?password|can't access|cannot access",
}


def rule_signals(text: str) -> tuple[list[str], list[str], str | None]:
    """(deletion cues, negations, non-deletion purpose) found in the text by the rule model."""
    t = (text or "").lower()
    neg = [p for p in NEGATION_PATTERNS if re.search(p, t)]
    pos = [p for p in DELETION_PATTERNS if re.search(p, t)]
    if negated_deletion(t):
        neg.append("negated deletion cue")
    rtype = next((k for k, p in NON_DELETION_HINTS.items() if re.search(p, t)), None)
    return pos, neg, rtype


def rule_classify(text: str) -> dict:
    """Requests arrive through the deletion workflow, so deletion is the prior. A request is
    NOT a deletion when it explicitly negates deletion, or states a non-deletion purpose
    (access, export, correction, opt-out, login help) without any deletion cue."""
    if not (text or "").strip():
        # an empty request states no purpose at all, so it cannot authorize deletion
        return {"authorizes_deletion": False, "request_type": "OTHER", "engine": "rules",
                "rationale": "empty request text"}
    pos, neg, rtype = rule_signals(text)
    # a destructive action needs positive evidence: a deletion cue that is not negated
    authorizes = bool(pos) and not neg
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
                result = {**rules, "engine": f"rules (veto over {llm['model']})", "veto": True,
                          "override": "rules_over_llm", "confidence": "low"}
            elif not result["authorizes_deletion"] and rules["authorizes_deletion"]:
                pos, neg, rtype = rule_signals(clean)
                vote = {"request_type": llm["request_type"], "rationale": llm["rationale"]}
                if pos and not neg and rtype is None and not has_negation_token(clean):
                    # override: a clear deletion request with no other purpose and no negation-like token
                    # anywhere in the text (any doubt keeps the refusal)
                    result = {**rules, "engine": f"rules (override of {llm['model']})",
                              "override": "rules_over_llm", "confidence": "low", "llm_vote": vote}
                else:
                    # the LLM's refusal stands, but the models disagree: a human should look
                    result = {**result, "confidence": "low", "needs_human_review": True}
        result["rules_vote"] = rules["authorizes_deletion"]
        result["agreement"] = (result["authorizes_deletion"] == rules["authorizes_deletion"]
                               and "override" not in result)
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
