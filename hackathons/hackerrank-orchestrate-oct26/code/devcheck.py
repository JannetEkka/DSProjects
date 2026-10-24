"""Developer loop: run the deterministic engine on the sample requests and diff against sample_output."""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from audit.evidence import EvidenceStore
from audit.engine import AuditEngine, IdentityResolver

DS = Path(__file__).resolve().parent.parent / "dataset"
from audit.media import MediaExtractor
store = EvidenceStore(DS, MediaExtractor())
eng = AuditEngine(DS, store, IdentityResolver(DS))
eng.prepare(list(csv.DictReader(open(DS / "sample_deletion_requests.csv"))) + list(csv.DictReader(open(DS / "deletion_requests.csv"))))
gold = {r["case_id"]: r for r in csv.DictReader(open(DS / "sample_output.csv"))}
ok = 0
only = sys.argv[1:]
for case in csv.DictReader(open(DS / "sample_deletion_requests.csv")):
    cid = case["case_id"]
    if only and cid not in only:
        continue
    g = gold[cid]
    if g["deletion_status"] == "NOT_APPLICABLE":
        continue
    st, steps, trace = eng.audit(case)
    gs = json.loads(g["steps_json"])
    fmt = lambda s: f'{s["phase"][:4]} {s["system_id"]} {s["resource_id"]} {s["operation"]} {s["evidence_id"]}'
    same = st == g["deletion_status"] and [fmt(s) for s in steps] == [fmt(s) for s in gs]
    ok += same
    if not same or only:
        print("=====", cid, "pred", st, "gold", g["deletion_status"], trace["user_id"])
        P, G = [fmt(s) for s in steps], [fmt(s) for s in gs]
        for x in G:
            print(("   " if x in P else " - ") + x)
        for x in P:
            if x not in G:
                print(" + " + x)
        for r in trace["resources"]:
            print("      ", r)
print("exact", ok)
