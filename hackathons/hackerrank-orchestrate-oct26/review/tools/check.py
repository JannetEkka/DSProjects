import csv, json, sys, re
from datetime import datetime
D = sys.argv[1]; OUT = sys.argv[2]; REQ = sys.argv[3] if len(sys.argv) > 3 else D + "/deletion_requests.csv"
TABLE = [("FINDING","REPORT_REMAINING_RECORD","PRESENT"),("FINDING","REPORT_EXPOSED_PII","PRESENT"),
 ("FINDING","REPORT_ACTIVE_DATA_FLOW","ACTIVE"),("FINDING","REPORT_RESTORE_RISK","ACTIVE"),
 ("REMEDIATION","DISABLE_DATA_FLOW","DISABLED"),("REMEDIATION","BLOCK_RESTORE","BLOCKED"),
 ("REMEDIATION","DELETE_RECORD","ABSENT"),("REMEDIATION","REDACT_RECORD","REDACTED"),
 ("REMEDIATION","ANONYMIZE_RECORD","ANONYMIZED"),("VERIFICATION","VERIFY_RECORD_ABSENT","ABSENT"),
 ("VERIFICATION","VERIFY_RECORD_PRESENT","PRESENT"),("VERIFICATION","VERIFY_RECORD_REDACTED","REDACTED"),
 ("VERIFICATION","VERIFY_RECORD_ANONYMIZED","ANONYMIZED"),("VERIFICATION","VERIFY_DATA_FLOW_DISABLED","DISABLED"),
 ("VERIFICATION","VERIFY_RESTORE_BLOCKED","BLOCKED")]
OPI = {op:i for i,(_,op,_) in enumerate(TABLE)}; OPS = {op:(ph,st) for ph,op,st in TABLE}
PH = {"FINDING":0,"REMEDIATION":1,"VERIFICATION":2}
T = lambda s: datetime.fromisoformat(s.replace("Z","+00:00"))
ev_time = {}
for r in csv.DictReader(open(D+"/evidence_files.csv")): ev_time[r["file_id"]] = (T(r["captured_at"]), r["file_path"])
act = {r["activity_id"]: T(r["event_time"]) for r in csv.DictReader(open(D+"/system_activity.csv"))}
aud = {r["audit_id"]: T(r["event_time"]) for r in csv.DictReader(open(D+"/user_audit_log.csv"))}
reqs = {r["case_id"]: r for r in csv.DictReader(open(REQ, encoding="utf-8-sig"))}
issues = []; late_ok = 0; late_bad = []
raw = open(OUT, newline="").read()
rows = list(csv.reader(raw.splitlines()))
if rows[0] != ["case_id","deletion_status","steps_json"]: issues.append(("HEADER", rows[0]))
body = rows[1:]
print("rows", len(body), "expected", len(reqs))
ids = [r[0] for r in body]
key = lambda c: int(re.sub(r"\D","",c))
if ids != sorted(ids, key=key): issues.append(("SORT_NUMERIC", "not numeric-sorted"))
if ids != sorted(ids): print("note: not lexicographically sorted (numeric sort used)" if ids == sorted(ids,key=key) else "note: neither sort")
if set(ids) != set(reqs) or len(ids) != len(set(ids)): issues.append(("IDSET", len(set(ids)^set(reqs))))
counts = {}
for cid, st, sj in body:
    counts[st] = counts.get(st,0)+1
    try: steps = json.loads(sj)
    except Exception as e: issues.append((cid,"JSON",str(e))); continue
    if st not in ("COMPLETE","INCOMPLETE","NOT_APPLICABLE"): issues.append((cid,"STATUS",st))
    if st == "NOT_APPLICABLE" and steps != []: issues.append((cid,"NA_NONEMPTY"))
    if st != "NOT_APPLICABLE" and not steps: issues.append((cid,"EMPTY_STEPS"))
    audit_at = T(reqs[cid]["audit_at"]) if cid in reqs else None
    prev = None
    for i, s in enumerate(steps, 1):
        if set(s) != {"step_no","phase","system_id","resource_id","operation","state","evidence_id"}: issues.append((cid,"KEYS",sorted(s)))
        if s.get("step_no") != i: issues.append((cid,"STEPNO",i,s.get("step_no")))
        op = s.get("operation")
        if op not in OPS or OPS[op] != (s.get("phase"), s.get("state")): issues.append((cid,"TABLE",s)); continue
        k = (PH[s["phase"]], OPI[op], s["system_id"], s["resource_id"])
        if prev and k <= prev: issues.append((cid,"ORDER",i,prev,k))
        prev = k
        ev = s["evidence_id"]
        if st == "COMPLETE":
            if s["phase"] != "VERIFICATION": issues.append((cid,"COMPLETE_NONVERIF",i))
            if not ev: issues.append((cid,"COMPLETE_NOEVID",i))
        if st == "INCOMPLETE":
            if s["phase"] in ("REMEDIATION","VERIFICATION") and ev: issues.append((cid,"INCOMPLETE_FUTURE_EVID",i,ev))
            if s["phase"] == "FINDING" and not ev: issues.append((cid,"FINDING_NOEVID",i))
        if ev:
            if ev in ev_time: t = ev_time[ev][0]
            elif ev in act: t = act[ev]
            elif ev in aud: t = aud[ev]
            else: issues.append((cid,"UNKNOWN_EVID",ev)); continue
            if audit_at and t > audit_at:
                if ev.startswith("evidence_"): late_bad.append((cid, ev, ev_time[ev][1], str(t), str(audit_at), s["resource_id"]))
                else: issues.append((cid,"LATE_ACTIVITY",ev))
print("status counts", counts)
print("hard issues", len(issues)); [print(" ", x) for x in issues[:30]]
print("evidence files captured after audit_at (need per-line check):", len(late_bad))
json.dump(late_bad, open("/tmp/rv/late.json","w"))
