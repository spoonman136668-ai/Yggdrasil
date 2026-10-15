"""Independent per-row role-chain, 12-edge bounded-memory audit for Y F53."""
import json,math,sys
def solve(events,indices,q):
 selected=[events[i] for i in indices];at=q["start"]
 for role,d in q["chain"]:
  choices=[e for e in selected if e[1]==role and (e[0] if d==1 else e[2])==at]
  if len(choices)!=1:return None
  e=choices[0];at=e[2] if d==1 else e[0]
 return at
def check(x,p):
 assert x["schema"]=="yggdrasil.f53.cross-role-path-memory.trainonly.v1"
 assert x["stage"]=="TRAIN_ONLY_UNSEEN_DISTRACTOR_GRAPH_TOPOLOGY_NOT_ORIGINAL"
 assert x["fit_seeds"]==p["fit_seeds"] and x["diagnostic_seeds"]==p["diagnostic_seeds"]
 assert x["fit_families"]==p["fit_families"] and x["diagnostic_families"]==p["diagnostic_families"]
 assert x["original_seeds_NOT_RESERVED"]==p["proposed_original_seeds_NOT_RESERVED"]
 assert x["original_executed"] is False and x["source_independent_F3"] is False
 assert x["accepted_ref_mutation"] is False and x["paid_api_calls"]==0
 assert x["events_per_stream"]==p["events_per_stream"] and x["memory_cap_edges"]==p["memory_capacity_edges"]
 assert x["future_question_hidden_until_retention_complete"] is True
 assert x["train_examples"]==4096 and x["cases"]==64 and len(x["rows"])==64
 assert len(x["weights"])==9
 arms=[p["candidate"],*p["controls"],p["unfair_control"]]
 assert len(arms)==len(set(arms)) and set(x["scores"])==set(arms)
 seen=set();counts={a:0 for a in arms}
 for r in x["rows"]:
  key=r["seed"],r["family"]
  assert key not in seen and 591100<=key[0]<591116 and key[1] in p["diagnostic_families"]
  seen.add(key)
  events=r["public_events"];q=r["question"]
  assert len(events)==64 and len(q["chain"])==4
  assert sum(e[3] for e in events)==32
  assert set(r["results"])==set(arms) and set(r["retained_indices"])==set(arms[:-1])
  for arm,indices in r["retained_indices"].items():
   assert len(indices)==12 and len(set(indices))==12
   assert all(type(i) is int and 0<=i<64 for i in indices)
   assert r["results"][arm]==int(solve(events,indices,q)==q["answer"])
  assert r["results"][p["unfair_control"]]==1
  for a in arms:counts[a]+=r["results"][a]
 assert len(seen)==64
 for a in arms:
  assert x["scores"][a]["correct"]==counts[a] and x["scores"][a]["total"]==64
  assert math.isclose(x["scores"][a]["accuracy"],counts[a]/64,abs_tol=1e-12)
 by={}
 for family in p["diagnostic_families"]:
  sub=[r for r in x["rows"] if r["family"]==family]
  assert len(sub)==16
  by[str(family)]={a:sum(r["results"][a] for r in sub) for a in arms}
  assert x["by_family"][str(family)]==by[str(family)]
 assert math.isclose(x["tag_core_rate"],.5,abs_tol=1e-12)
 assert math.isclose(x["tag_distractor_rate"],.5,abs_tol=1e-12)
 fair=p["controls"];winner=max(fair,key=lambda a:counts[a])
 gain=(counts[p["candidate"]]-counts[winner])/64
 nonreg=all(by[str(f)][p["candidate"]]>=max(by[str(f)][a] for a in fair)
            for f in p["diagnostic_families"])
 passed=gain>=p["threshold_gain_pp"]/100 and nonreg
 assert x["strongest_fair_control"]==winner
 assert math.isclose(x["candidate_gain"],gain,abs_tol=1e-12)
 assert x["per_family_nondegradation"]==nonreg and x["frozen_gate_met"]==passed
 return {"candidate_correct":counts[p["candidate"]],"strongest_fair":winner,
         "strongest_correct":counts[winner],"gain_pp":round(100*gain,5),
         "no_family_regression":nonreg,"passed_frozen_train":passed}
if __name__=="__main__":
 assert len(sys.argv)==3
 print("Y_F53_INDEPENDENT_RECOUNT_PASS",json.dumps(check(json.load(open(sys.argv[1])),json.load(open(sys.argv[2]))),sort_keys=True))
