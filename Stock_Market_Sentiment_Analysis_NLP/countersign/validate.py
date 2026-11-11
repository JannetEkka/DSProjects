"""Check every model reply before any code trusts it.

A reply is either parsed into exactly the fields and values allowed here, or
rejected with a reason. Nothing downstream reads raw model text.
"""
from __future__ import annotations

import json
import re

ALLOWED_LABELS = (-1, 0, 1)
ALLOWED_METRICS = ("week_open", "week_close", "week_high", "week_low", "week_change_pct")
ALLOWED_KINDS = ("news", "price")
ALLOWED_VERDICTS = ("supported", "not_supported")
MAX_CLAIMS = 8
MAX_CLAIM_CHARS = 320


class BadReply(ValueError):
    pass


def extract_json(text: str):
    """Find the one JSON object in a reply (models often wrap it in prose or fences)."""
    if not isinstance(text, str) or not text.strip():
        raise BadReply("empty reply")
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.I)
    start = t.find("{")
    if start < 0:
        raise BadReply("no JSON object in reply")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(t)):
        c = t[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(t[start:i + 1])
                except ValueError as e:
                    raise BadReply(f"invalid JSON: {e}") from e
    raise BadReply("JSON object never closes")


def parse_label(text: str) -> int:
    """Classifier reply: {"label": -1 | 0 | 1} and nothing else counts."""
    obj = extract_json(text)
    if not isinstance(obj, dict) or "label" not in obj:
        raise BadReply("missing field: label")
    v = obj["label"]
    if isinstance(v, bool) or not isinstance(v, int) or v not in ALLOWED_LABELS:
        raise BadReply(f"label must be -1, 0 or 1, got {v!r}")
    return v


def parse_claims(text: str) -> list[dict]:
    """Writer reply: {"claims": [{text, kind, headline_ids, numbers}]}.

    Only the shape is checked here. Whether the ids exist and the numbers are
    right is the decision rule's job, because those are reasons to remove one
    claim, not to throw the whole reply away.
    """
    obj = extract_json(text)
    if not isinstance(obj, dict) or not isinstance(obj.get("claims"), list):
        raise BadReply("missing field: claims (a list)")
    if not obj["claims"]:
        raise BadReply("claims is empty")
    if len(obj["claims"]) > MAX_CLAIMS:
        raise BadReply(f"more than {MAX_CLAIMS} claims")
    out = []
    for i, c in enumerate(obj["claims"]):
        if not isinstance(c, dict):
            raise BadReply(f"claim {i + 1} is not an object")
        txt = c.get("text")
        if not isinstance(txt, str) or not txt.strip():
            raise BadReply(f"claim {i + 1}: text missing")
        if len(txt) > MAX_CLAIM_CHARS:
            raise BadReply(f"claim {i + 1}: text longer than {MAX_CLAIM_CHARS} characters")
        kind = c.get("kind")
        if kind not in ALLOWED_KINDS:
            raise BadReply(f"claim {i + 1}: kind must be one of {ALLOWED_KINDS}")
        ids = c.get("headline_ids", [])
        if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
            raise BadReply(f"claim {i + 1}: headline_ids must be a list of strings")
        nums = c.get("numbers", [])
        if not isinstance(nums, list):
            raise BadReply(f"claim {i + 1}: numbers must be a list")
        clean_nums = []
        for n in nums:
            if not isinstance(n, dict) or n.get("metric") not in ALLOWED_METRICS:
                raise BadReply(f"claim {i + 1}: number metric must be one of {ALLOWED_METRICS}")
            val = n.get("value")
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                raise BadReply(f"claim {i + 1}: number value must be a number")
            clean_nums.append({"metric": n["metric"], "value": float(val)})
        out.append({"text": txt.strip(), "kind": kind,
                    "headline_ids": [x.strip().upper() for x in ids], "numbers": clean_nums})
    return out


def parse_verdict(text: str) -> dict:
    """Checker reply: {"verdict": "supported" | "not_supported", "quote": str, "reason": str}."""
    obj = extract_json(text)
    if not isinstance(obj, dict):
        raise BadReply("verdict reply is not an object")
    v = obj.get("verdict")
    if v not in ALLOWED_VERDICTS:
        raise BadReply(f"verdict must be one of {ALLOWED_VERDICTS}, got {v!r}")
    quote = obj.get("quote", "")
    reason = obj.get("reason", "")
    if not isinstance(quote, str) or not isinstance(reason, str):
        raise BadReply("quote and reason must be strings")
    if v == "not_supported" and not reason.strip():
        raise BadReply("not_supported needs a reason")
    return {"verdict": v, "quote": quote.strip(), "reason": reason.strip()[:300]}


def parse_sandbox(stdout: str, expected_weeks: list[str]) -> dict:
    """Sandbox output: one JSON object, week -> the five recomputed figures."""
    obj = extract_json(stdout)
    if not isinstance(obj, dict):
        raise BadReply("sandbox output is not an object")
    for wk in expected_weeks:
        fig = obj.get(wk)
        if not isinstance(fig, dict):
            raise BadReply(f"sandbox output has no figures for week {wk}")
        for m in ALLOWED_METRICS:
            if isinstance(fig.get(m), bool) or not isinstance(fig.get(m), (int, float)):
                raise BadReply(f"sandbox figure {m} missing for week {wk}")
    return {wk: {m: float(obj[wk][m]) for m in ALLOWED_METRICS} for wk in expected_weeks}
