"""Evaluation workflow.

    python3 code/evaluation/main.py            # metrics + metamorphic suite + ablations -> evaluation_report.md

1. Scores the agent on dataset/sample_deletion_requests.csv against sample_output.csv:
   case status accuracy, step-level precision/recall/F1, field-level accuracy, sequence accuracy,
   evidence-citation accuracy.
2. Runs a metamorphic / adversarial suite of team-authored cases (see custom_cases) whose expected
   behaviour follows from invariants of the task (identity, time cutoff, intent, decoys).
3. Runs ablations (components switched off) to show what each part of the engine contributes.
"""
from __future__ import annotations

import csv
import io
import json
import sys
import time
from contextlib import redirect_stdout
from difflib import SequenceMatcher
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE.parent
ROOT = CODE.parent
sys.path.insert(0, str(CODE))

from audit.engine import AuditEngine, IdentityResolver  # noqa: E402
from audit.evidence import EvidenceStore  # noqa: E402
from audit.intent import IntentClassifier  # noqa: E402
from audit.media import MediaExtractor  # noqa: E402

DS = ROOT / "dataset"
FIELDS = ["phase", "system_id", "resource_id", "operation", "state", "evidence_id"]


# ----------------------------------------------------------------------------- scoring

def step_key(s):
    return tuple(s[f] for f in FIELDS)


def score(pred: dict, gold: dict) -> dict:
    """pred/gold: case_id -> (status, steps)."""
    n = len(gold)
    status_ok = sum(pred[c][0] == gold[c][0] for c in gold)
    tp = fp = fn = 0
    field_hits = {f: 0 for f in FIELDS}
    field_total = 0
    seq_exact = 0
    seq_ratio = 0.0
    case_exact = 0
    ev_hits = ev_total = 0
    for c, (gs, gsteps) in gold.items():
        ps, psteps = pred[c]
        P = [step_key(s) for s in psteps]
        G = [step_key(s) for s in gsteps]
        Pm = list(P)
        for g in G:
            if g in Pm:
                tp += 1
                Pm.remove(g)
            else:
                fn += 1
        fp += len(Pm)
        # field-level: positional alignment (gold step k vs predicted step k), the strictest reading
        pidx = {(s["operation"], s["resource_id"]): s for s in psteps}
        for k, g in enumerate(gsteps):
            field_total += 1
            p_pos = psteps[k] if k < len(psteps) else None
            for f in FIELDS:
                if p_pos is not None and p_pos[f] == g[f]:
                    field_hits[f] += 1
            p = pidx.get((g["operation"], g["resource_id"]))
            if g["evidence_id"]:
                ev_total += 1
                ev_hits += int(p is not None and p["evidence_id"] == g["evidence_id"])
        common_p = [x for x in P if x in G]
        common_g = [x for x in G if x in P]
        seq_exact += int(common_p == common_g)
        seq_ratio += SequenceMatcher(None, P, G).ratio() if (P or G) else 1.0
        case_exact += int(ps == gs and P == G)
    prec = tp / (tp + fp) if tp + fp else 1.0
    rec = tp / (tp + fn) if tp + fn else 1.0
    return {
        "cases": n,
        "status_accuracy": status_ok / n,
        "case_exact_match": case_exact / n,
        "step_precision": prec, "step_recall": rec,
        "step_f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0,
        "field_accuracy": {f: field_hits[f] / field_total for f in FIELDS},
        "sequence_accuracy_relative_order": seq_exact / n,
        "sequence_similarity_mean": seq_ratio / n,
        "evidence_citation_accuracy": ev_hits / ev_total if ev_total else 1.0,
    }


# ----------------------------------------------------------------------------- harness

class Agent:
    """In-process agent (shares parsed evidence across runs for speed)."""

    def __init__(self, use_llm=False):
        self.store = EvidenceStore(DS, MediaExtractor(prefer="auto" if use_llm else "ocr"))
        self.ids = IdentityResolver(DS)
        self.intent = IntentClassifier(use_llm=use_llm)
        self._engine = None

    def run(self, cases, universe_extra=(), **ablate):
        if self._engine is None:
            self._engine = AuditEngine(DS, self.store, self.ids)
        eng = self._engine
        for k in ("DISABLE_WORKFLOW", "TRUST_CATALOG", "DISABLE_ERAS", "DISABLE_TIMING"):
            setattr(eng, k, ablate.get(k, False))
        universe = {}
        for p in (DS / "deletion_requests.csv", DS / "sample_deletion_requests.csv"):
            for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
                universe[r["case_id"]] = r
        for r in list(cases) + list(universe_extra):
            universe[r["case_id"]] = r
        self.intent.prefetch(r["request_text"] for r in universe.values())
        intents = {cid: self.intent.classify(r["request_text"]) for cid, r in universe.items()}
        eng.prepare([r for cid, r in universe.items() if intents[cid]["authorizes_deletion"]])
        out = {}
        for c in cases:
            if not intents[c["case_id"]]["authorizes_deletion"]:
                out[c["case_id"]] = ("NOT_APPLICABLE", [])
            else:
                st, steps, _ = eng.audit(c)
                out[c["case_id"]] = (st, steps)
        return out


def load_gold():
    return {r["case_id"]: (r["deletion_status"], json.loads(r["steps_json"]))
            for r in csv.DictReader(open(DS / "sample_output.csv", newline="", encoding="utf-8"))}


def sample_cases():
    return list(csv.DictReader(open(DS / "sample_deletion_requests.csv", newline="", encoding="utf-8")))


# ----------------------------------------------------------------------------- metamorphic suite

def _case(cid):
    for p in (DS / "sample_deletion_requests.csv", DS / "deletion_requests.csv"):
        for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
            if r["case_id"] == cid:
                return dict(r)
    raise KeyError(cid)


def custom_cases():
    """Team-authored adversarial cases. Each derives a new request from a real one and states the
    invariant the agent must respect. Expected outputs are derived from the invariant, not the agent."""
    gold = load_gold()
    tests = []

    # 1. Identity: the same subject addressed through a HISTORICAL email must give the same audit.
    base = _case("case_12")
    t = dict(base, case_id="eval_hist_email", email="minjun.kim90@gmail.com")
    tests.append(("Historical email resolves to same subject (user_audit_log)", t,
                  {"status": gold["case_12"][0], "steps": gold["case_12"][1]}))

    # 2. Identity normalisation: upper-case / padded email.
    base = _case("case_22")
    t = dict(base, case_id="eval_upper_email", email="  SEOYEON-HAN@GMAIL.COM ")
    tests.append(("Upper-case, padded email is the same subject", t,
                  {"status": gold["case_22"][0], "steps": gold["case_22"][1]}))

    # 3. Intent: mixed-language NON-deletion request containing a negated 'delete'.
    base = _case("case_22")
    t = dict(base, case_id="eval_de_access",
             request_text="Bitte schicken Sie mir eine Kopie meiner Daten. Do not delete anything, I still use the account.")
    tests.append(("Negated deletion / access request -> NOT_APPLICABLE", t, {"status": "NOT_APPLICABLE", "steps": []}))

    # 4. Intent: deletion request in Hindi must authorize deletion (same audit as the original).
    base = _case("case_24")
    t = dict(base, case_id="eval_hi_delete", request_text="कृपया मेरा खाता और उससे जुड़ा सारा व्यक्तिगत डेटा स्थायी रूप से हटा दें।")
    tests.append(("Hindi deletion request is authorized", t,
                  {"status": gold["case_24"][0], "steps": gold["case_24"][1]}))

    # 5. Time cutoff: audit the same request BEFORE its evidence existed -> no step may cite
    #    evidence observed after the new audit_at.
    base = _case("case_24")
    t = dict(base, case_id="eval_time_cutoff", audit_at="2026-09-14T00:00:00Z")
    tests.append(("Earlier audit_at never cites later evidence", t, {"no_evidence_after": "2026-09-14T00:00:00Z"}))

    # 6. Decoy: catalog says marketing_001 belongs to the subject, but the screenshot shows another
    #    person -> marketing_001 must not be reported.
    t = _case("case_63")
    tests.append(("Catalog link contradicted by screenshot is rejected", t, {"absent_resource": "marketing_001"}))

    # 7. Decoy: a similar-looking email (g.silva76.jr@) belongs to someone else.
    t = _case("case_35")
    tests.append(("Similar-email decoy search hit is not attributed", t, {"absent_resource": "search_1874"}))

    # 8. Retention: security audit records are verified PRESENT, never deleted.
    t = _case("case_11")
    tests.append(("Security audit log retained, never deleted", t, {"retained": "security_service"}))

    # 9. Workflow timing: case_25 and case_26 report at the same minute, so both workflow windows
    #    cover both orphan (identifier-free) analytics rows. analytics_4566 sits at an exact chain gap
    #    from case_26's own support record -> it must NOT attach to case_25; analytics_1895 is in phase
    #    only with case_25's account job -> it must attach.
    t = _case("case_25")
    tests.append(("Orphan record follows its workflow chain, not a co-timed request", t,
                  {"absent_resource": "analytics_4566", "present_resource": "analytics_1895"}))
    return tests


def check(test, result, store):
    name, case, exp = test
    status, steps = result
    if "status" in exp:
        ok = status == exp["status"] and [step_key(s) for s in steps] == [step_key(s) for s in exp["steps"]]
        detail = f"status={status} steps={len(steps)} (expected {exp['status']}/{len(exp['steps'])})"
    elif "no_evidence_after" in exp:
        cutoff = exp["no_evidence_after"]
        bad = []
        for s in steps:
            ev = s["evidence_id"]
            if ev.startswith("evidence_"):
                obs = [o for o in store.observations if o.evidence_id == ev and o.resource_id == s["resource_id"]]
                if obs and min(o.time for o in obs) > cutoff:
                    bad.append(ev)
        ok = not bad
        detail = f"status={status}, later-evidence citations={bad or 'none'}"
    elif "absent_resource" in exp:
        rids = {s["resource_id"] for s in steps}
        ok = exp["absent_resource"] not in rids and exp.get("present_resource") in rids | {None}
        detail = f"status={status}, resources={', '.join(sorted(rids))}"
    else:
        sec = [s for s in steps if s["system_id"] == exp["retained"]]
        ok = bool(sec) and all(s["operation"] == "VERIFY_RECORD_PRESENT" for s in sec)
        detail = f"security steps={[(s['resource_id'], s['operation']) for s in sec]}"
    return ok, detail


# ----------------------------------------------------------------------------- report

def fmt_pct(x):
    return f"{100 * x:.1f}%"


def main():
    t0 = time.time()
    with redirect_stdout(io.StringIO()):
        agent = Agent(use_llm=True)  # final configuration: cached LLM/VLM answers, no calls without a key
    gold = load_gold()
    cases = sample_cases()
    pred = agent.run(cases)
    m = score(pred, gold)
    (HERE / "sample_metrics.json").write_text(json.dumps(m, indent=1))

    ablations = [
        ("Full engine", {}),
        ("- workflow attribution (evidence-only linking)", {"DISABLE_WORKFLOW": True}),
        ("- artifact verification of catalog links", {"TRUST_CATALOG": True}),
        ("- workflow timing model (lattice + chain)", {"DISABLE_TIMING": True}),
        ("- per-subject request eras", {"DISABLE_ERAS": True}),
    ]
    abl_rows = [(name, score(agent.run(cases, **flags), gold)) for name, flags in ablations]
    agent.run(cases)  # restore full configuration

    suite_res = []
    for test in custom_cases():
        name, case, exp = test
        res = agent.run([case], universe_extra=[case])[case["case_id"]]
        ok, detail = check(test, res, agent.store)
        suite_res.append((name, case["case_id"], ok, detail))

    failures = []
    for c, (gs, gsteps) in gold.items():
        ps, psteps = pred[c]
        P, G = [step_key(s) for s in psteps], [step_key(s) for s in gsteps]
        if ps != gs or P != G:
            failures.append((c, gs, ps, [g for g in G if g not in P], [p for p in P if p not in G]))

    write_report(m, abl_rows, suite_res, failures, time.time() - t0)
    print(json.dumps({k: v for k, v in m.items() if k != "field_accuracy"}, indent=1))
    print(f"metamorphic suite: {sum(r[2] for r in suite_res)}/{len(suite_res)} passed")
    for r in suite_res:
        print("  ", "PASS" if r[2] else "FAIL", r[0], "|", r[3])


def write_report(m, abl_rows, suite_res, failures, secs):
    L = []
    L.append("# Evaluation Report - Ghost Data Deletion Audit Agent\n")
    L.append("Generated by `python3 code/evaluation/main.py` (deterministic: LLM and VLM answers come from the response cache, so every number "
             "here is reproducible without an API key). Gold = `dataset/sample_output.csv` (32 public cases).\n")
    L.append("## 1. Headline metrics (32 sample cases)\n")
    L.append("| Metric | Value |\n|---|---|")
    L.append(f"| Case-level status accuracy | **{fmt_pct(m['status_accuracy'])}** |")
    L.append(f"| Case exact match (status + every step, in order) | {fmt_pct(m['case_exact_match'])} |")
    L.append(f"| Step precision | {fmt_pct(m['step_precision'])} |")
    L.append(f"| Step recall | {fmt_pct(m['step_recall'])} |")
    L.append(f"| Step F1 | **{fmt_pct(m['step_f1'])}** |")
    L.append(f"| Sequence accuracy (shared steps in identical relative order) | {fmt_pct(m['sequence_accuracy_relative_order'])} |")
    L.append(f"| Sequence similarity (mean difflib ratio of full step lists) | {fmt_pct(m['sequence_similarity_mean'])} |")
    L.append(f"| Evidence-citation accuracy (gold steps that cite evidence) | {fmt_pct(m['evidence_citation_accuracy'])} |")
    L.append("\n### Field-level accuracy\nPositional alignment: gold step *k* is compared with predicted step *k* "
             "(the strictest reading - one missing step shifts every later step).\n")
    L.append("| Field | Accuracy |\n|---|---|")
    for f, v in m["field_accuracy"].items():
        L.append(f"| `{f}` | {fmt_pct(v)} |")
    L.append("\n## 2. Ablations - what each component buys\n")
    L.append("| Configuration | Status acc. | Step F1 | Exact cases |\n|---|---|---|---|")
    for name, mm in abl_rows:
        L.append(f"| {name} | {fmt_pct(mm['status_accuracy'])} | {fmt_pct(mm['step_f1'])} | {fmt_pct(mm['case_exact_match'])} |")
    L.append("\n## 3. Team-authored evaluation cases (metamorphic / adversarial suite)\n")
    L.append("Each case is derived from a real request and checks an invariant the task demands. "
             "Expected behaviour comes from the invariant (or the public gold of the source case), "
             "never from the agent's own output.\n")
    L.append("| # | Invariant | Case | Result | Detail |\n|---|---|---|---|---|")
    for i, (name, cid, ok, detail) in enumerate(suite_res, 1):
        L.append(f"| {i} | {name} | `{cid}` | {'PASS' if ok else 'FAIL'} | {detail} |")
    L.append(f"\n**{sum(r[2] for r in suite_res)}/{len(suite_res)} passed.**\n")
    L.append("## 4. Remaining sample mismatches (error analysis)\n")
    L.append("| Case | Gold | Pred | Missing steps | Extra steps |\n|---|---|---|---|---|")
    for c, gs, ps, miss, extra in failures:
        fm = "<br>".join(f"{x[3]} {x[2]}" for x in miss) or "-"
        fe = "<br>".join(f"{x[3]} {x[2]}" for x in extra) or "-"
        L.append(f"| {c} | {gs} | {ps} | {fm} | {fe} |")
    notes = HERE / "report_notes.md"
    if notes.exists():
        L.append("\n" + notes.read_text(encoding="utf-8"))
    L.append(f"\n_Evaluation runtime: {secs:.1f}s._\n")
    (HERE / "evaluation_report.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
