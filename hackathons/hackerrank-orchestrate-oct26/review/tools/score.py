import csv,json,sys
g={r["case_id"]:r for r in csv.DictReader(open(sys.argv[1]))}; p={r["case_id"]:r for r in csv.DictReader(open(sys.argv[2]))}
F=["phase","system_id","resource_id","operation","state","evidence_id"]
st=ex=0; tp=fp=fn=0; tp5=fp5=fn5=0; diffs=[]
for c,gr in g.items():
    pr=p.get(c); 
    if not pr: diffs.append((c,"MISSING")); continue
    st+=gr["deletion_status"]==pr["deletion_status"]
    gs=json.loads(gr["steps_json"]); ps=json.loads(pr["steps_json"])
    if gs==ps: ex+=1
    G=[tuple(s[f] for f in F) for s in gs]; P=[tuple(s[f] for f in F) for s in ps]
    G5={x[:5] for x in G}; P5={x[:5] for x in P}
    tp+=len(set(G)&set(P)); fp+=len(set(P)-set(G)); fn+=len(set(G)-set(P))
    tp5+=len(G5&P5); fp5+=len(P5-G5); fn5+=len(G5-P5)
    if gs!=ps: diffs.append((c,gr["deletion_status"],pr["deletion_status"],"missing:",sorted(set(G)-set(P)),"extra:",sorted(set(P)-set(G)), "order_only" if set(G)==set(P) else ""))
n=len(g); f1=lambda a,b,c: 2*a/(2*a+b+c)
print(f"status {st}/{n}  exact {ex}/{n}  step-F1(all fields) {f1(tp,fp,fn):.3f}  step-F1(no evidence) {f1(tp5,fp5,fn5):.3f}  tp={tp} fp={fp} fn={fn}")
for d in diffs: print(d)
