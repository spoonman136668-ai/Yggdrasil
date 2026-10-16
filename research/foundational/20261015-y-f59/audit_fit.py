"""Y-F59 source-free public graph, compact-byte and predeclared FIT recount.

Does not import scientific source. The unfair oracle and trainable policy are
NOT executed by the FIT feasibility source, so cannot be used as accepted
scientific results. The four explicitly observed public controls are audited.
"""
import json,sys
OBS=("qualified_fixed_component_buffer","frozen_F58_causal_frontier",
 "frozen_F57_incremental","public_full_graph_offline_noncompetitive")
def solve(records,query):
 want=tuple(2*r+(dr==-1) for r,dr in query["ops"])
 state={(query["start"],0)}
 for t in range(len(want)):
  nxt=set(state)
  for at,i in state:
   for a,b,c in records:
    for x,y,z in ((a,b,c),(b,a,tuple(v^1 for v in reversed(c)))):
     if at==x and want[i:i+len(z)]==z:nxt.add((y,i+len(z)))
  if nxt==state:break
  state=nxt
 return int((query["answer"],len(want)) in state)
def audit(result,pre):
 d=json.load(open(result));p=json.load(open(pre))
 assert d["schema"]=="yggdrasil.f59.deferred-attachment-FIT-source.v1"
 assert d["stage"]=="F59_NEW_FIT_SOURCE_ONLY_NO_LEARNED_USE"
 assert d["fit_seeds"]==p["fit"]["seeds"]
 assert d["fit_families"]==p["fit"]["families"]
 assert d["cases"]==len(d["rows"])==p["fit"]["expected_cases"]==64
 assert d["DIAG_untouched"] and d["originals_untouched"]
 assert d["native_total_576B_unverified"] and d["accepted_refs_unchanged"] and not d["independent_F3"]
 assert d["offline_extra_work_noncompetitive"] and d["online_query_hidden_until_retention_complete"]
 assert set(d["correct"])==set(OBS)
 # Future learner, pair/triple, FIFO/hash and unfair oracle were not run.
 assert OBS[0] in p["controls"] and OBS[-1] in p["controls"]
 seen=set();scores={a:0 for a in OBS};regimes=set()
 for row in d["rows"]:
  seed,fam=row["seed"],row["family"]
  assert (seed,fam) not in seen;seen.add((seed,fam))
  assert p["fit"]["seeds"][0]<=seed<p["fit"]["seeds"][1] and fam in p["fit"]["families"]
  assert row["regime"] in p["fit"]["arrival_regimes"];regimes.add(row["regime"])
  public=[tuple(x) for x in row["public_events"]]
  assert len(public)==72 and len(set(public))==72
  q=row["question"]
  assert len(q["ops"]) in p["memory"]["future_query_hops"]
  assert set(row["predictions"])==set(OBS)
  assert set(row["retained_records"])==set(OBS)
  assert set(row["serialized_bytes"])==set(OBS)
  for name in OBS:
   raw=row["retained_records"][name]
   assert len(raw)<=12 and row["serialized_bytes"][name]==12*len(raw)<=144
   records=[]
   for h in raw:
    data=bytes.fromhex(h);assert len(data)==12
    a=int.from_bytes(data[:4],"little");b=int.from_bytes(data[4:8],"little")
    bits=int.from_bytes(data[8:11],"little");length=data[11]
    assert 1<=length<=4 and bits>>(3*length)==0
    codes=tuple((bits>>(3*i))&7 for i in range(length))
    reachable={a}
    for code in codes:
     r=code//2;direction=-1 if code&1 else 1
     reachable={e[2] if direction==1 else e[0] for at in reachable for e in public
       if e[1]==r and (e[0] if direction==1 else e[2])==at}
     assert reachable
    assert b in reachable
    records.append((a,b,codes))
   if name==OBS[-1]:assert len(records)==12
   ans=solve(records,q)
   assert ans==row["predictions"][name]
   scores[name]+=ans
 assert len(seen)==64 and len(regimes)==2 and scores==d["correct"]
 gate=(scores[OBS[-1]]/64>=p["FIT_source_requirements"]["public_full_graph_offline_accuracy_min"]
  and scores[OBS[0]]/64>=p["FIT_source_requirements"]["causal_fixed_frontier_online_accuracy_min"])
 assert gate==d["frozen_FIT_source_gate_met"]
 print("Y_F59_SOURCE_AUDIT",json.dumps(dict(scores=scores,qualified=gate,regimes=sorted(regimes),unexecuted_controls=list(set(p["controls"])-set(OBS))),sort_keys=True))
if __name__=="__main__":
 assert len(sys.argv)==3
 audit(sys.argv[1],sys.argv[2])
