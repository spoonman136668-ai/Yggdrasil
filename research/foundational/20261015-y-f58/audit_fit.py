"""Y-F58 source-free audit of all 64 FIT receipts and frozen controls.

Each 12B compressed state must correspond to a path in the *public* graph.
No source generator import and no new scientific source execution.
"""
import json,sys
def solve(chunks,question):
 need=tuple(2*r+(d==-1) for r,d in question["ops"])
 states={(question["start"],0)}
 for _ in range(len(need)):
  nxt=set(states)
  for at,i in states:
   for a,b,c in chunks:
    for x,y,ops in ((a,b,c),(b,a,tuple(v^1 for v in reversed(c)))):
     if x==at and need[i:i+len(ops)]==ops:
      nxt.add((y,i+len(ops)))
  if nxt==states:break
  states=nxt
 return int((question["answer"],len(need)) in states)
def audit(result,prereg):
 d=json.load(open(result));p=json.load(open(prereg))
 assert d["schema"]=="yggdrasil.f58.causal-frontier-FIT-source.v1"
 assert d["stage"]=="F58_NEW_FIT_SOURCE_ONLY_NOT_LEARNED"
 assert d["fit_seeds"]==p["fit"]["seed_range"]
 assert d["fit_families"]==p["fit"]["families"]
 assert d["cases"]==len(d["rows"])==p["fit"]["cases"]==64
 assert d["DIAG_untouched"] and d["originals_untouched"]
 assert d["offline_extra_work_noncompetitive"] and d["query_hidden_during_retention"]
 assert d["native_total_576B_unverified"] and d["accepted_refs_unchanged"] and not d["source_independent_F3"]
 # The preregistered private-query oracle was NOT emitted by the
 # consumed source. It is unfair, noncompetitive, and irrelevant to the
 # frozen public feasibility thresholds. Record the omission explicitly.
 assert p["methods"][-1]=="future_query_oracle_unfair"
 assert "future_query_oracle_unfair" not in d["correct"]
 arms=p["methods"][:-1]
 assert set(d["correct"])==set(arms)
 seen=set();totals={a:0 for a in arms};regimes=set()
 for row in d["rows"]:
  seed,fam=row["seed"],row["family"]
  assert (seed,fam) not in seen;seen.add((seed,fam))
  assert p["fit"]["seed_range"][0]<=seed<p["fit"]["seed_range"][1]
  assert fam in p["fit"]["families"]
  assert row["regime"] in p["fit"]["arrival_regimes"]
  regimes.add(row["regime"])
  public=[tuple(e) for e in row["public_events"]]
  assert len(public)==p["public_stream"]["events"]==72 and len(set(public))==72
  q=row["query"];assert len(q["ops"]) in p["public_stream"]["query_hops"]
  assert set(row["correctness"])==set(arms)
  assert set(row["retained_records"])==set(arms)
  assert set(row["serialized_bytes"])==set(arms)
  for arm in arms:
   items=row["retained_records"][arm]
   assert len(items)<=12 and row["serialized_bytes"][arm]==len(items)*12<=144
   records=[]
   for item in items:
    raw=bytes.fromhex(item);assert len(raw)==12
    a=int.from_bytes(raw[:4],"little");b=int.from_bytes(raw[4:8],"little")
    val=int.from_bytes(raw[8:11],"little");n=raw[11]
    assert 1<=n<=4 and val>>(3*n)==0
    codes=tuple((val>>(3*k))&7 for k in range(n))
    reachable={a}
    for code in codes:
     role=code//2;direct=-1 if code&1 else 1
     reachable={e[2] if direct==1 else e[0]
      for at in reachable for e in public
      if e[1]==role and (e[0] if direct==1 else e[2])==at}
     assert reachable
    assert b in reachable
    records.append((a,b,codes))
   if arm=="public_offline_full_graph_extra_work":assert len(records)==12
   actual=solve(records,q)
   assert row["correctness"][arm]==actual
   totals[arm]+=actual
 assert len(seen)==64 and len(regimes)==2
 assert totals==d["correct"]
 gate=(totals["public_offline_full_graph_extra_work"]/64>=p["FIT_source_gates"]["public_offline_accuracy_min"] and
       totals["causal_frontier_fixed_online"]/64>=p["FIT_source_gates"]["causal_fixed_online_accuracy_min"])
 assert d["joint_source_gate_met"]==gate
 print("Y_F58_FIT_SOURCE",json.dumps(dict(correct=totals,qualified=gate,regimes=sorted(regimes)),sort_keys=True))
if __name__=="__main__":
 assert len(sys.argv)==3
 audit(sys.argv[1],sys.argv[2])
