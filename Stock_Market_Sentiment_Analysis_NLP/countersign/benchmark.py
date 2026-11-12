"""How much does the check catch, and how much does it remove by mistake?

The 18 weekly briefs cannot answer that: nobody has labelled their 108 claims.
HaluEval (Li et al., 2023, https://github.com/RUCAIBox/HaluEval) can. Its
summarization set pairs a news article with one faithful summary and one
summary that contains a planted, plausible error. This script runs the same
rule as the "Check a brief" app (functions/api/check.js and _rules.js, ported
line for line) on a fixed random sample and counts:

  caught        summaries with a planted error where at least one sentence was removed
  false alarms  faithful summaries where at least one sentence was removed

    python benchmark.py path/to/summarization_data.json   # about $0.05 through Otari

The guardrail step is left out: the benchmark has no investment advice in it.
"""
from __future__ import annotations

import json
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import validate as V
from otari import CHECKER_MODEL, BudgetRefused, OtariError
from pipeline import RUNS, ask

N_ARTICLES, SEED, MAX_DOC_CHARS, MAX_SENTENCES = 60, 42, 6000, 8

SYSTEM = (  # the app's checker instruction, word for word
    "You are a strict fact checker. You get one claim and the source text. You did not write the claim.\n"
    "Look for anything in the claim that the sources do not state: a wrong name, number, date, cause or direction, "
    "or a detail that is simply not there. Outside knowledge does not count as support.\n"
    'If every part of the claim is stated in the sources, the verdict is "supported"; otherwise "not_supported".\n'
    "Reply with only this JSON:\n"
    '{"verdict": "supported" or "not_supported", "quote": "for supported, a passage copied word for word from the sources", '
    '"reason": "for not_supported, what is missing or wrong, in one sentence"}')


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'“$])", re.sub(r"\s+", " ", text).strip())
    return [p.strip() for p in parts if len(p.strip()) > 8]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9%$.]+", " ", s.lower()).strip()


def numbers_not_in_sources(sentence: str, sources: str) -> list[str]:
    src = sources.replace(",", "")
    found = re.findall(r"\d+(?:\.\d+)?", sentence.replace(",", ""))
    return [n for n in found if not re.search(rf"(^|[^\d.]){re.escape(n)}(?!\d)", src)]


def quote_in_sources(quote: str, sources: str) -> bool:
    src = _norm(sources)
    parts = [_norm(p).strip(". ") for p in re.split(r"\.{3,}|…", quote)]
    parts = [p for p in parts if p]
    return bool(parts) and max(len(p) for p in parts) >= 12 and all(p in src for p in parts)


def check_sentence(sentence: str, sources: str) -> dict:
    missing = numbers_not_in_sources(sentence, sources)
    if missing:
        return {"keep": False, "reason": "number_not_in_sources"}
    verdict, _, _ = ask(CHECKER_MODEL, SYSTEM, f"Claim: {sentence}\n\nSources:\n{sources}",
                        "benchmark", V.parse_verdict, max_tokens=300)
    if verdict is None:
        return {"keep": False, "reason": "no_verdict"}
    if verdict["verdict"] != "supported":
        return {"keep": False, "reason": "not_supported"}
    if not quote_in_sources(verdict["quote"], sources):
        return {"keep": False, "reason": "quote_not_found"}
    return {"keep": True, "reason": None}


def check_summary(summary: str, doc: str) -> dict:
    sents = sentences(summary)[:MAX_SENTENCES]
    res = [check_sentence(s, doc) for s in sents]
    return {"sentences": len(sents), "removed": sum(not r["keep"] for r in res),
            "reasons": [r["reason"] for r in res if not r["keep"]]}


def main(path: str) -> None:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if all(isinstance(r.get(k), str) for k in ("document", "right_summary", "hallucinated_summary")) \
                    and len(r["document"]) <= MAX_DOC_CHARS:
                rows.append(r)
    random.Random(SEED).shuffle(rows)
    sample = rows[:N_ARTICLES]

    def one(r):
        try:
            return {"faithful": check_summary(r["right_summary"], r["document"]),
                    "planted": check_summary(r["hallucinated_summary"], r["document"])}
        except (BudgetRefused, OtariError) as e:
            return {"error": str(e)}

    with ThreadPoolExecutor(8) as ex:
        out = list(ex.map(one, sample))
    done = [o for o in out if "error" not in o]
    n = len(done)
    caught = sum(o["planted"]["removed"] > 0 for o in done)
    false_alarm = sum(o["faithful"]["removed"] > 0 for o in done)
    reasons: dict[str, int] = {}
    for o in done:
        for k in o["planted"]["reasons"]:
            reasons[k] = reasons.get(k, 0) + 1
    res = {
        "dataset": "HaluEval summarization (RUCAIBox/HaluEval, data/summarization_data.json)",
        "sample": f"{N_ARTICLES} articles of at most {MAX_DOC_CHARS} characters, random.Random({SEED}).shuffle",
        "checker": CHECKER_MODEL, "articles_scored": n, "articles_failed": len(out) - n,
        "planted_error_summaries": n, "caught": caught, "caught_rate": round(caught / n, 3) if n else None,
        "faithful_summaries": n, "false_alarms": false_alarm,
        "false_alarm_rate": round(false_alarm / n, 3) if n else None,
        "missed": n - caught,
        "sentences_checked": sum(o["faithful"]["sentences"] + o["planted"]["sentences"] for o in done),
        "faithful_sentences": sum(o["faithful"]["sentences"] for o in done),
        "faithful_sentences_removed": sum(o["faithful"]["removed"] for o in done),
        "planted_removed_by_reason": reasons,
        "complete": n == N_ARTICLES,
    }
    with open(f"{RUNS}/benchmark.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
