"""Tiny process-wide token/cost ledger for model calls (written to evaluation/usage_report.md)."""
from __future__ import annotations

from collections import defaultdict

# USD per 1M tokens (input, output). Update if pricing changes.
PRICES = {
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
    "gemini-2.5-pro": (1.25, 10.00),
}

CALLS = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "purposes": defaultdict(int)})
CACHE_HITS = defaultdict(int)


def record(provider: str, model: str, purpose: str, tokens_in: int, tokens_out: int):
    c = CALLS[(provider, model)]
    c["calls"] += 1
    c["input"] += int(tokens_in)
    c["output"] += int(tokens_out)
    c["purposes"][purpose] += 1


def record_cache_hit(kind: str):
    CACHE_HITS[kind] += 1


def cost(model: str, tin: int, tout: int) -> float:
    pi, po = PRICES.get(model, (0.0, 0.0))
    return tin / 1e6 * pi + tout / 1e6 * po


def snapshot():
    return {f"{p}/{m}": {"calls": v["calls"], "input": v["input"], "output": v["output"],
                         "purposes": dict(v["purposes"]), "cost_usd": cost(m, v["input"], v["output"])}
            for (p, m), v in CALLS.items()}, dict(CACHE_HITS)
