"""Countersign: the run.

    python pipeline.py all         # sentiment, 18 briefs, drills, live week, page
    python pipeline.py sentiment   # classify 349 headlines, score F1
    python pipeline.py briefs      # write, check, recompute and decide 18 weekly briefs
    python pipeline.py drills      # forced fallback, guardrail block, budget refusal
    python pipeline.py live        # this week's Apple headlines, fetched through Otari
    python pipeline.py page        # rebuild site/index.html from runs/results.json

Each stage writes its part of runs/results.json. Model replies are cached in
runs/cache/ so a rerun costs nothing; delete the folder to pay for a fresh run.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from sklearn.metrics import accuracy_score, f1_score

import data
import validate as V
from decide import REASONS, decide
from otari import (CHECKER_MODEL, CLASSIFIER_MODEL, FALLBACK_DRILL_POLICY, WRITER_FALLBACK_MODEL,
                   WRITER_MAIN_MODEL, WRITER_POLICY, BudgetRefused, GuardrailBlocked, Otari,
                   OtariError)

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
CACHE = os.path.join(RUNS, "cache")
RESULTS = os.path.join(RUNS, "results.json")
CALL_LOG = os.path.join(RUNS, "otari_calls.jsonl")
GUARD_URL = os.environ.get("COUNTERSIGN_GUARD_URL", "https://countersign-6my.pages.dev")
GUARD = [{"profile": "no-investment-advice", "mode": "block", "url": GUARD_URL}]
OWN_SPEND_STOP_USD = 1.20  # our own stop, below the key's $1.50 cap
NO_ANSWER = 99

os.makedirs(CACHE, exist_ok=True)
otari = Otari(log_path=CALL_LOG)


# ---- cache: survives a damaged or half-written file ----------------------
def _cache_path(*parts) -> str:
    h = hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:24]
    return os.path.join(CACHE, h + ".json")


def cached_chat(model, system, user, purpose, max_tokens, attempt=0, guardrails=None,
                stream=False) -> dict:
    """Return {"text", "served", "provider", "fallback", "cost", "cached"}."""
    path = _cache_path("chat", model, system, user, max_tokens, attempt, bool(guardrails))
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                hit = json.load(f)
            if isinstance(hit, dict) and isinstance(hit.get("text"), str):
                hit["cached"] = True
                return hit
        except (ValueError, OSError):
            pass  # damaged cache entry: ignore it and ask again
    if otari.spent_usd() > OWN_SPEND_STOP_USD:
        raise BudgetRefused(403, "own_stop", f"our own stop at ${OWN_SPEND_STOP_USD} was reached")
    r = otari.chat(model, system, user, purpose, max_tokens=max_tokens, guardrails=guardrails,
                   stream=stream)
    out = {"text": r.text, "served": r.model_served, "provider": r.provider,
           "fallback": r.fallback, "attempts": r.attempts, "cost": r.cost_usd,
           "guardrails": r.guardrails, "request_id": r.request_id}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f)
    os.replace(tmp, path)
    out["cached"] = False
    return out


def ask(model, system, user, purpose, parse, max_tokens, guardrails=None, stream=False):
    """Ask, validate, retry once with the rejection named. -> (parsed | None, meta, errors)."""
    errors, meta = [], None
    for attempt in (0, 1):
        u = user if attempt == 0 else (
            user + f"\n\nYour previous reply was rejected: {errors[-1]}. Reply with only the JSON object.")
        meta = cached_chat(model, system, u, purpose, max_tokens, attempt, guardrails, stream)
        try:
            return parse(meta["text"]), meta, errors
        except V.BadReply as e:
            errors.append(str(e))
    return None, meta, errors


def load_results() -> dict:
    try:
        with open(RESULTS, encoding="utf-8") as f:
            r = json.load(f)
        return r if isinstance(r, dict) else {}
    except (ValueError, OSError):
        return {}


def save_results(r: dict) -> None:
    r["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = RESULTS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1)
    os.replace(tmp, RESULTS)


# ---- 1. sentiment --------------------------------------------------------
CLASSIFY_SYSTEM = (
    "You label the sentiment of one financial news item from early 2019. "
    "The items come from a set collected around Apple stock; many are about other companies, "
    "markets or the economy. Label every item, whatever it is about.\n"
    "-1 = negative news, 0 = neutral or mixed news, 1 = positive news.\n"
    'Always reply with only this JSON and nothing else: {"label": -1} or {"label": 0} or {"label": 1}.')


def run_sentiment() -> None:
    df = data.load()
    test_ids = set(data.test_ids_2024(df))

    def one(row):
        try:
            label, meta, errors = ask(CLASSIFIER_MODEL, CLASSIFY_SYSTEM, row.News,
                                      "classify", V.parse_label, max_tokens=800)
        except BudgetRefused:
            return row.id, None, ["budget refused"]
        except OtariError as e:
            return row.id, None, [str(e)]
        return row.id, label, errors

    with ThreadPoolExecutor(16) as ex:
        out = list(ex.map(one, df.itertuples()))
    pred = {i: (lab if lab is not None else NO_ANSWER) for i, lab, _ in out}
    retried = sum(1 for _, _, e in out if e)
    no_answer = [i for i, lab, _ in out if lab is None]

    def score(ids):
        y = [int(df.loc[df.id == i, "Label"].iloc[0]) for i in ids]
        p = [pred[i] for i in ids]
        return {"n": len(ids),
                "weighted_f1": round(float(f1_score(y, p, labels=[-1, 0, 1], average="weighted",
                                                    zero_division=0)), 4),
                "accuracy": round(float(accuracy_score(y, p)), 4)}

    order = list(df.id)
    res = load_results()
    res["sentiment"] = {
        "model": CLASSIFIER_MODEL,
        "prompt": CLASSIFY_SYSTEM,
        "split_2024": score([i for i in order if i in test_ids]),
        "all_349": score(order),
        "baseline_2024": data.BASELINE_2024,
        "replies_rejected_once": retried,
        "no_answer_counted_wrong": len(no_answer),
        "label_counts": {str(k): int(v) for k, v in df.Label.value_counts().items()},
        "predicted_counts": {str(k): sum(1 for x in pred.values() if x == k) for k in (-1, 0, 1)},
    }
    save_results(res)
    print("sentiment:", json.dumps(res["sentiment"]["split_2024"]), json.dumps(res["sentiment"]["all_349"]),
          "| rejected once:", retried, "| no answer:", len(no_answer))


# ---- 2. the sandbox recomputes the price figures -------------------------
SANDBOX_CODE = '''import json
weeks = json.loads(%r)
out = {}
for week, days in weeks.items():
    days = sorted(days, key=lambda d: d["date"])
    week_open = days[0]["open"]
    week_close = days[-1]["close"]
    out[week] = {
        "week_open": round(week_open, 2),
        "week_close": round(week_close, 2),
        "week_high": round(max(d["high"] for d in days), 2),
        "week_low": round(min(d["low"] for d in days), 2),
        "week_change_pct": round((week_close - week_open) / week_open * 100, 2),
    }
print(json.dumps(out))
'''


def recompute(weeks: list[dict], purpose: str) -> tuple[dict | None, str]:
    """Run the arithmetic in Otari's sandbox. -> (week -> figures, note)."""
    with_prices = {w["week"]: w["prices"] for w in weeks if w["prices"]}
    if not with_prices:
        return None, "no price rows"
    code = SANDBOX_CODE % json.dumps(with_prices)
    path = _cache_path("sandbox", code)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return V.parse_sandbox(json.load(f)["stdout"], list(with_prices)), "cached"
        except (ValueError, OSError, KeyError, V.BadReply):
            pass
    try:
        out = otari.run_code(code, purpose)
        if out.get("return_code") != 0:
            return None, "sandbox exit code %s: %s" % (out.get("return_code"), (out.get("stderr") or "")[:200])
        figs = V.parse_sandbox(out.get("stdout", ""), list(with_prices))
    except (OtariError, V.BadReply) as e:
        return None, f"sandbox failed: {e}"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"stdout": out["stdout"]}, f)
    return figs, "ran in Otari's sandbox"


# ---- 3. writer, checker, decision, guardrail -----------------------------
WRITER_SYSTEM = (
    "You write the factual core of a weekly market brief about Apple for a general reader.\n"
    "You get one week's news items, each with an id, and that week's daily price rows.\n"
    "Write 5 to 7 claims. Each claim is one plain sentence of fact.\n"
    '- A "news" claim reports what the news items say and must list the ids of the 1 to 3 items it comes from in headline_ids.\n'
    '- A "price" claim states price figures for the week. Write 1 or 2 of these, only if price rows are given. '
    "Every figure in it must also be listed in numbers, with metric one of: week_open (first day's open), "
    "week_close (last day's close), week_high (highest high), week_low (lowest low), "
    "week_change_pct (percent change from week_open to week_close).\n"
    "Report only. No advice, no forecasts.\n"
    "Reply with only this JSON:\n"
    '{"claims": [{"text": "...", "kind": "news", "headline_ids": ["H001"], "numbers": []},\n'
    '            {"text": "...", "kind": "price", "headline_ids": [], "numbers": [{"metric": "week_change_pct", "value": -1.2}]}]}')

CHECKER_SYSTEM = (
    "You are a strict fact checker. You get one claim and the evidence it cites. You did not write the claim.\n"
    "Look for anything in the claim that the evidence does not state: a wrong name, number, date, cause or direction, "
    "or a detail that is simply not there. Outside knowledge does not count as support.\n"
    'If every part of the claim is stated in the evidence, the verdict is "supported"; otherwise "not_supported".\n'
    "Reply with only this JSON:\n"
    '{"verdict": "supported" or "not_supported", "quote": "for a supported news claim, a passage copied word for word from one cited item", '
    '"reason": "for not_supported, what is missing or wrong, in one sentence"}')

TONE_SYSTEM = (
    "You get the confirmed sentences of one week's market brief about Apple. "
    "Label the overall tone of the week for someone holding the stock: -1 negative, 0 neutral or mixed, 1 positive.\n"
    'Reply with only this JSON: {"label": -1} or {"label": 0} or {"label": 1}.')


def writer_input(week: dict) -> str:
    lines = [f"Week ending {week['week']}.", "", "News items:"]
    lines += [f"{h['id']} ({h['date']}): {h['text']}" for h in week["headlines"]]
    lines += ["", "Daily price rows (date, open, high, low, close):"]
    if week["prices"]:
        lines += [f"{p['date']}, {p['open']:.2f}, {p['high']:.2f}, {p['low']:.2f}, {p['close']:.2f}"
                  for p in week["prices"]]
    else:
        lines += ["none: write no price claims"]
    return "\n".join(lines)


def checker_input(claim: dict, week: dict, by_id: dict, figures: dict | None) -> str:
    """What the checker sees: the claim and its evidence, never the writer's reasoning.

    For price figures the evidence is the sandbox's recomputation, not the raw
    rows: in the first run the checker was given the rows and wrongly rejected
    correct figures, because it was doing the arithmetic itself.
    """
    lines = [f"Claim: {claim['text']}", "", "Evidence:"]
    for i in claim["headline_ids"]:
        if i in by_id:
            lines.append(f"{i}: {by_id[i]}")
    if (claim["kind"] == "price" or claim["numbers"]) and figures:
        lines.append("Price figures for the week, computed by code from the daily price rows (treat as exact; "
                     "a figure in the claim may be rounded): "
                     f"week opened at {figures['week_open']:.2f}, closed at {figures['week_close']:.2f}, "
                     f"high {figures['week_high']:.2f}, low {figures['week_low']:.2f}, "
                     f"change from open to close {figures['week_change_pct']:+.2f}%.")
    return "\n".join(lines)


def brief_for_week(week: dict, figures: dict | None, writer_model: str = WRITER_POLICY,
                   purpose: str = "write") -> dict:
    """Write one week's brief and decide every claim. Raises BudgetRefused."""
    out = {"week": week["week"], "n_headlines": len(week["headlines"]), "status": "complete",
           "figures": figures, "claims": [], "writer": {}, "tone": None, "notes": []}
    if not week["headlines"]:
        out["status"] = "no_brief"
        out["notes"].append("No headlines this week, so no brief was written.")
        return out
    by_id = {h["id"]: h["text"] for h in week["headlines"]}

    claims, meta, errors = ask(writer_model, WRITER_SYSTEM, writer_input(week), purpose,
                               V.parse_claims, max_tokens=1600, stream=True)
    out["writer"] = {"asked": writer_model, "served": meta["served"], "provider": meta["provider"],
                     "fallback": meta["fallback"], "attempts": meta.get("attempts", 1),
                     "replies_rejected": errors}
    if claims is None:
        out["status"] = "writer_reply_rejected"
        out["notes"].append("The writer's reply failed validation twice: " + "; ".join(errors))
        return out

    def check(claim):
        known = [i for i in claim["headline_ids"] if i in by_id]
        if not known and not (claim["kind"] == "price" and claim["numbers"]):
            return None, ["checker not asked: nothing valid is cited"]
        verdict, _, errs = ask(CHECKER_MODEL, CHECKER_SYSTEM, checker_input(claim, week, by_id, figures),
                               "check", V.parse_verdict, max_tokens=300)
        return verdict, errs

    with ThreadPoolExecutor(6) as ex:
        verdicts = list(ex.map(check, claims))

    for claim, (verdict, errs) in zip(claims, verdicts):
        d = decide(claim, by_id, figures, verdict)
        out["claims"].append({**claim, "verdict": verdict, "checker_rejections": errs,
                              "keep": d["keep"], "reason": d["reason"], "detail": d["detail"]})

    # Guardrail on the final text: Otari sends it to the guardrail service
    # before the model. A block removes the sentences it names; if it names
    # none we can find, the whole brief is withheld.
    for _ in range(3):
        kept = [c for c in out["claims"] if c["keep"]]
        if not kept:
            break
        final_text = "\n".join(c["text"] for c in kept)
        try:
            tone, tmeta, _ = ask(CLASSIFIER_MODEL, TONE_SYSTEM, final_text, "tone+guardrail",
                                 V.parse_label, max_tokens=300, guardrails=GUARD)
            out["tone"] = tone
            out["guardrail"] = {"status": "passed", "verdicts": tmeta.get("guardrails", [])}
            break
        except GuardrailBlocked as e:
            phrase = (re.search(r'reads as advice: \\?"(.+?)\\?"', e.detail) or [None, ""])[1].lower()
            hit = [c for c in kept if phrase and phrase in c["text"].lower()]
            for c in (hit or kept):
                c.update(keep=False, reason="guardrail",
                         detail=REASONS["guardrail"] + (f" (“{phrase}”)" if phrase else ""))
            out["guardrail"] = {"status": "blocked", "phrase": phrase}
    return out


def run_briefs(stop_after: int | None = None, inflate_from: int | None = None) -> dict:
    """All 18 weeks. A budget refusal stops the run and the missing weeks are listed."""
    df = data.load()
    weeks = data.weeks(df)
    figures, sandbox_note = recompute(weeks, "recompute 18 weeks")
    briefs, stopped = [], None
    for n, wk in enumerate(weeks):
        if stopped:
            briefs.append({"week": wk["week"], "n_headlines": len(wk["headlines"]),
                           "status": "missing", "claims": [],
                           "notes": ["Not written: the run was stopped by the budget before this week."]})
            continue
        try:
            if inflate_from is not None and n >= inflate_from:
                # Budget drill: ask for an output limit the key's cap cannot cover.
                otari.chat(WRITER_MAIN_MODEL, WRITER_SYSTEM, writer_input(wk), "budget drill",
                           max_tokens=16_000_000)
            briefs.append(brief_for_week(wk, (figures or {}).get(wk["week"])))
            print(" ", wk["week"], briefs[-1]["status"],
                  "kept %d / removed %d" % (sum(c["keep"] for c in briefs[-1]["claims"]),
                                            sum(not c["keep"] for c in briefs[-1]["claims"])))
        except BudgetRefused as e:
            stopped = {"at_week": wk["week"], "detail": e.detail}
            briefs.append({"week": wk["week"], "n_headlines": len(wk["headlines"]), "status": "missing",
                           "claims": [], "notes": ["Not written: Otari refused the request (budget)."]})
            print("  budget refusal at", wk["week"], "->", e.detail)
    return {"briefs": briefs, "sandbox": sandbox_note, "stopped_by_budget": stopped,
            "complete": stopped is None and all(b["status"] in ("complete", "no_brief") for b in briefs)}


def summarise(briefs: list[dict]) -> dict:
    claims = [c for b in briefs for c in b["claims"]]
    by_reason: dict[str, int] = {}
    for c in claims:
        if not c["keep"]:
            by_reason[c["reason"]] = by_reason.get(c["reason"], 0) + 1
    return {"weeks": len(briefs),
            "weeks_with_brief": sum(1 for b in briefs if b["status"] == "complete"),
            "weeks_missing": [b["week"] for b in briefs if b["status"] not in ("complete", "no_brief")],
            "claims_written": len(claims),
            "claims_kept": sum(1 for c in claims if c["keep"]),
            "claims_removed": sum(1 for c in claims if not c["keep"]),
            "removed_by_reason": dict(sorted(by_reason.items(), key=lambda kv: -kv[1])),
            "per_week": [{"week": b["week"], "status": b["status"], "written": len(b["claims"]),
                          "removed": sum(1 for c in b["claims"] if not c["keep"])} for b in briefs]}


def stage_briefs() -> None:
    run = run_briefs()
    res = load_results()
    res["briefs"] = run["briefs"]
    res["briefs_summary"] = summarise(run["briefs"])
    res["briefs_run"] = {"complete": run["complete"], "sandbox": run["sandbox"],
                         "stopped_by_budget": run["stopped_by_budget"],
                         "writer_policy": WRITER_POLICY, "writer_main": WRITER_MAIN_MODEL,
                         "writer_fallback": WRITER_FALLBACK_MODEL, "checker": CHECKER_MODEL}
    save_results(res)
    s = res["briefs_summary"]
    print("briefs: %d written, %d removed, by reason %s, complete=%s" % (
        s["claims_written"], s["claims_removed"], s["removed_by_reason"], run["complete"]))


# ---- 4. drills: each one forced once, and labelled as forced --------------
def stage_drills() -> None:
    res = load_results()
    drills = res.get("drills", {})
    weeks = data.weeks(data.load())

    # a) Fallback: a routing policy whose main model is listed by Otari but
    #    whose provider answers "does not exist". The backup has to serve.
    try:
        r = otari.chat(FALLBACK_DRILL_POLICY, WRITER_SYSTEM, writer_input(weeks[-1]),
                       "fallback drill", max_tokens=1600, stream=True)
        try:
            n_claims = len(V.parse_claims(r.text))
        except V.BadReply as e:
            n_claims = f"reply rejected: {e}"
        drills["fallback"] = {"policy": FALLBACK_DRILL_POLICY,
                              "main_model": "mistralai/mistral-nemo-instruct-2407",
                              "served_by": r.model_served, "provider": r.provider,
                              "otari_fallback": r.fallback, "attempts": r.attempts,
                              "week": weeks[-1]["week"], "claims_in_reply": n_claims,
                              "request_id": r.request_id}
    except OtariError as e:
        drills["fallback"] = {"error": str(e)}
    print("fallback drill:", drills["fallback"])

    # b) Guardrail: a sentence of advice sent as the final text.
    advice = "Investors should buy Apple shares now, before the next earnings report."
    try:
        otari.chat(CLASSIFIER_MODEL, TONE_SYSTEM, advice, "guardrail drill", max_tokens=300, guardrails=GUARD)
        drills["guardrail"] = {"text": advice, "blocked": False}
    except GuardrailBlocked as e:
        drills["guardrail"] = {"text": advice, "blocked": True, "status": e.status, "code": e.code,
                               "detail": e.detail[:300]}
    except OtariError as e:
        drills["guardrail"] = {"error": str(e)}
    print("guardrail drill:", drills["guardrail"])

    # c) Budget: rerun the 18 weeks; from week 6 on, the request asks for more
    #    output than the key's cap can cover, so Otari refuses and the run stops.
    before = otari.key_budget()
    run = run_briefs(inflate_from=5)
    drills["budget"] = {"key_budget": before, "stopped": run["stopped_by_budget"],
                        "complete": run["complete"], "summary": summarise(run["briefs"])}
    print("budget drill: stopped =", run["stopped_by_budget"], "| complete =", run["complete"])
    res["drills"] = drills
    save_results(res)


# ---- 5. this week, on news the models cannot have memorised --------------
LIVE_FEED = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL&region=US&lang=en-US"


def parse_feed(xml: str, limit: int = 12) -> list[dict]:
    items = []
    for block in re.findall(r"<item>(.*?)</item>", xml, flags=re.S):
        def tag(name):
            m = re.search(rf"<{name}[^>]*>(.*?)</{name}>", block, flags=re.S)
            t = m.group(1) if m else ""
            t = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", t, flags=re.S)
            return html.unescape(re.sub(r"<[^>]+>", " ", html.unescape(t))).strip()
        title, desc, link, pub = tag("title"), tag("description"), tag("link"), tag("pubDate")
        if not title:
            continue
        text = title if not desc or desc.lower().startswith(title.lower()[:40]) else f"{title}. {desc}"
        items.append({"title": title, "text": re.sub(r"\s+", " ", text)[:600], "link": link, "published": pub})
        if len(items) >= limit:
            break
    return items


LIVE_PRICES = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=5d&interval=1d"


def parse_prices(text: str) -> list[dict]:
    """Yahoo's chart JSON -> daily rows. Any missing or odd field drops that day."""
    try:
        res = json.loads(text)["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        rows = []
        for i, ts in enumerate(res["timestamp"]):
            vals = [q[k][i] for k in ("open", "high", "low", "close")]
            if all(isinstance(v, (int, float)) and v > 0 for v in vals):
                rows.append({"date": time.strftime("%Y-%m-%d", time.gmtime(ts)),
                             "open": float(vals[0]), "high": float(vals[1]),
                             "low": float(vals[2]), "close": float(vals[3])})
        return rows
    except (ValueError, KeyError, IndexError, TypeError):
        return []


def stage_live() -> None:
    res = load_results()
    live: dict = {"feed": LIVE_FEED, "price_source": LIVE_PRICES,
                  "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        page = otari.fetch(LIVE_FEED, "fetch live headlines", max_chars=40000)
        items = parse_feed(page.get("text") or "")
    except OtariError as e:
        live.update(status="fetch_failed", error=str(e))
        res["live"] = live
        save_results(res)
        print("live: fetch failed:", e)
        return
    try:
        prices = parse_prices(otari.fetch(LIVE_PRICES, "fetch live prices", max_chars=20000).get("text") or "")
    except OtariError as e:
        prices = []
        live["price_error"] = str(e)
    week = {"week": time.strftime("%Y-%m-%d", time.gmtime()),
            "headlines": [{"id": f"L{i + 1:02d}", "date": (it["published"] or "")[5:16], "text": it["text"]}
                          for i, it in enumerate(items)],
            "prices": prices}
    figures, note = recompute([week], "recompute live week")
    live["fetch_tool"] = page.get("fetch_tool")
    live["prices"] = prices
    live["sandbox"] = note
    live["headlines"] = [{"id": f"L{i + 1:02d}", **it} for i, it in enumerate(items)]
    try:
        brief = brief_for_week(week, (figures or {}).get(week["week"]), purpose="write live")
        live.update(status=brief["status"], brief=brief, summary=summarise([brief]))
    except BudgetRefused as e:
        live.update(status="stopped_by_budget", error=e.detail)
    res["live"] = live
    save_results(res)
    print("live:", live.get("status"), live.get("summary", {}), "| price rows:", len(prices), "| sandbox:", note)


# ---- 6. what Otari did, for the page -------------------------------------
def stage_evidence() -> None:
    res = load_results()
    calls = []
    try:
        with open(CALL_LOG, encoding="utf-8") as f:
            for line in f:
                try:
                    calls.append(json.loads(line))
                except ValueError:
                    continue  # a half-written log line is skipped, not fatal
    except OSError:
        pass
    by_model: dict[str, dict] = {}
    for c in calls:
        if c.get("path") == "/chat/completions" and c.get("status") == 200:
            k = c.get("model_served") or c.get("model_asked")
            m = by_model.setdefault(k, {"calls": 0, "cost_usd": 0.0, "providers": set(), "purposes": set()})
            m["calls"] += 1
            m["cost_usd"] += float(c.get("cost_usd") or 0)
            m["providers"].add(c.get("provider"))
            m["purposes"].add(c.get("purpose"))
    res["otari"] = {
        "base_url": "https://api.otari.ai/api/v1",
        "requests_logged": len(calls),
        "by_model": {k: {"calls": v["calls"], "cost_usd": round(v["cost_usd"], 6),
                         "providers": sorted(x for x in v["providers"] if x),
                         "purposes": sorted(x for x in v["purposes"] if x)} for k, v in by_model.items()},
        "fallbacks_seen": sum(1 for c in calls if c.get("fallback")),
        "sandbox_runs": sum(1 for c in calls if c.get("path") == "/code/execute" and c.get("status") == 200),
        "fetches": sum(1 for c in calls if c.get("path") == "/fetch" and c.get("status") == 200),
        "guardrail_checks": sum(1 for c in calls if c.get("guardrails")),
        "guardrail_blocks": sum(1 for c in calls if c.get("code") == "guardrail_violation"),
        "budget_refusals": sum(1 for c in calls if c.get("code") == "budget_exceeded"),
        "key_budget": otari.key_budget(),
        "key_usage_totals": (otari.key_usage().get("totals") or {}),
    }
    save_results(res)
    print("otari:", json.dumps({k: v for k, v in res["otari"].items() if k not in ("by_model",)})[:600])


def stage_page() -> None:
    res = load_results()
    # The page needs each week's news items (for the source marks) and the
    # first run's totals (kept for the record).
    res["headlines"] = {w["week"]: {h["id"]: {"text": h["text"], "date": h["date"]} for h in w["headlines"]}
                        for w in data.weeks(data.load())}
    try:
        with open(os.path.join(RUNS, "first_run_results.json"), encoding="utf-8") as f:
            first = json.load(f)
        fs = first["briefs_summary"]
        res["first_run"] = {
            "claims_written": fs["claims_written"], "claims_removed": fs["claims_removed"],
            "price_false_rejections": sum(1 for b in first["briefs"] for c in b["claims"]
                                          if c["kind"] == "price" and c["reason"] in ("not_supported", "no_verdict"))}
    except (OSError, ValueError, KeyError):
        pass
    with open(os.path.join(HERE, "site", "template.html"), encoding="utf-8") as f:
        tpl = f.read()
    blob = json.dumps(res).replace("</", "<\\/")
    with open(os.path.join(HERE, "site", "index.html"), "w", encoding="utf-8") as f:
        f.write(tpl.replace("/*__RESULTS__*/null", blob))
    print("page: site/index.html written (%d KB)" % (len(blob) // 1024))


STAGES = {"sentiment": run_sentiment, "briefs": stage_briefs, "drills": stage_drills,
          "live": stage_live, "evidence": stage_evidence, "page": stage_page}

if __name__ == "__main__":
    what = sys.argv[1:] or ["all"]
    if what == ["all"]:
        what = ["sentiment", "briefs", "drills", "live", "evidence", "page"]
    for name in what:
        STAGES[name]()
    print("spent this process: $%.4f" % otari.spent_usd())
