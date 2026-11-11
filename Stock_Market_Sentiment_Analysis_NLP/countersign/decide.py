"""The decision rule. Models describe; this file decides.

A claim is shown only if all of these hold:
  1. it cites something: at least one headline id, or at least one price figure;
  2. every headline id it cites exists in that week's headlines;
  3. every price figure it states matches what the sandbox recomputed from the
     price rows, and its text contains no other number that looks like a price
     figure the sandbox did not confirm;
  4. the checker model (a different family from the writer) said "supported",
     and for a news claim the sentence it quoted really is in a cited headline;
  5. the guardrail did not flag it as buy/sell advice.

The first failed condition is the recorded reason. No model can keep a claim:
a "supported" verdict is necessary, never sufficient.
"""
from __future__ import annotations

import re

# How far a stated figure may be from the recomputed one: writers round.
PRICE_TOLERANCE = 0.011  # dollars: two decimals
PCT_TOLERANCE = 0.051  # percentage points: one decimal

REASONS = {
    "cites_nothing": "Cites no headline and no price figure.",
    "unknown_headline": "Cites a headline that is not in this week's news.",
    "number_mismatch": "A number does not match the recomputed price data.",
    "unverified_number": "States a price figure the sandbox was not asked to confirm.",
    "not_supported": "The checker model found the cited headlines do not support it.",
    "quote_not_found": "The checker's supporting quote is not in the cited headlines.",
    "no_verdict": "The checker gave no usable verdict, so nothing confirms it.",
    "guardrail": "Blocked by the guardrail: reads as buy or sell advice.",
    "sandbox_unavailable": "The price figures could not be recomputed, so its numbers are unconfirmed.",
}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9%$.]+", " ", s.lower()).strip()


def quote_in_headlines(quote: str, headline_texts: list[str]) -> bool:
    q = _norm(quote).strip(". ")
    if len(q) < 12:  # too short to be evidence
        return False
    return any(q in _norm(h) for h in headline_texts)


def numbers_in_text(text: str) -> list[float]:
    """Dollar amounts and percentages written in a price claim's text."""
    found = []
    for m in re.finditer(r"\$\s?(\d+(?:\.\d+)?)|(-?\d+(?:\.\d+)?)\s?(?:%|percent)", text):
        found.append(float(m.group(1) or m.group(2)))
    return found


def number_ok(metric: str, value: float, recomputed: dict) -> bool:
    truth = recomputed[metric]
    if metric == "week_change_pct":
        return abs(value - truth) <= PCT_TOLERANCE
    return abs(value - truth) <= PRICE_TOLERANCE


def decide(claim: dict, week_headlines: dict[str, str], recomputed: dict | None,
           verdict: dict | None, guardrail_flagged: bool = False) -> dict:
    """Return {"keep": bool, "reason": code or None, "detail": str}.

    claim           a validated claim (validate.parse_claims)
    week_headlines  id -> text for this week only
    recomputed      the sandbox's figures for this week, or None if it failed
    verdict         a validated checker verdict, or None if the checker's
                    replies were rejected twice
    """
    ids, nums = claim["headline_ids"], claim["numbers"]

    if not ids and not nums:
        return _remove("cites_nothing")

    unknown = [i for i in ids if i not in week_headlines]
    if unknown:
        return _remove("unknown_headline", "No such headline this week: " + ", ".join(unknown))

    if nums or claim["kind"] == "price":
        if recomputed is None:
            return _remove("sandbox_unavailable")
        for n in nums:
            if not number_ok(n["metric"], n["value"], recomputed):
                return _remove(
                    "number_mismatch",
                    f"{n['metric']}: the brief says {n['value']:g}, "
                    f"the price rows give {recomputed[n['metric']]:.2f}")
        if claim["kind"] == "price":
            declared = [abs(n["value"]) for n in nums]
            for x in numbers_in_text(claim["text"]):
                confirmed = any(abs(abs(x) - d) <= PCT_TOLERANCE for d in declared)
                if not confirmed:
                    return _remove("unverified_number", f"{x:g} appears in the text but was not declared")

    if verdict is None:
        return _remove("no_verdict")
    if verdict["verdict"] != "supported":
        return _remove("not_supported", verdict.get("reason", ""))
    if claim["kind"] == "news":
        if not ids:
            return _remove("cites_nothing", "A news claim must cite a headline.")
        cited = [week_headlines[i] for i in ids]
        if not quote_in_headlines(verdict.get("quote", ""), cited):
            return _remove("quote_not_found", f"Quoted: “{verdict.get('quote', '')[:120]}”")

    if guardrail_flagged:
        return _remove("guardrail")

    return {"keep": True, "reason": None, "detail": ""}


def _remove(code: str, detail: str = "") -> dict:
    return {"keep": False, "reason": code, "detail": detail or REASONS[code]}
