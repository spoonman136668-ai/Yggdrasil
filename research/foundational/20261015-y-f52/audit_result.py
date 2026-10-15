"""Independent Y-F52 raw public event, 12-item retention, and role-chain recount."""
import json,math,sys
def solve(edges,path):
 at=path["start"]
 for role,d in path["chain"]:
  matches=[e for e in edges if e[1]==role and
           (e[0] if d==1 else e[2])==at]
  if len(matches)!=1:return None
  e=matches[0]
  at=e[2] if d==1 else e[0]
 return at
def verify(d,p):
 assert d["schema"]=="yggdrasil.f52.bridge-aware-neutral-tags.trainonly.v1"
 assert d["stage"]=="TRAIN_ONLY_UNSEEN_DISTRACTOR_GRAPH_TOPOLOGY_NOT_ORIGINAL"
 assert d["fit_seeds"]==p["fit_seeds"] and d["diagnostic_seeds"]==p["diagnostic_seeds"]
 assert d["fit_families"]==p["fit_families"] and d["diagnostic_families"]==p["diagnostic_families"]
 assert d["original_seeds_NOT_RESERVED"]==p["future_originals_proposed_only"]
 assert d["source_independent_F3"] is False and d["original_executed"] is False
 assert d["accepted_ref_mutation"] is False and d["paid_api_calls"]==0
 assert d["events_per_stream"]==p["events_per_stream"] and d["memory_cap_edges"]==p["memory_cap"]
 assert d["future_question_hidden_until_retention_complete"] is True
 arms=[p["candidate"],*p["baseline_controls"],p["unfair_control"]]
 assert len(arms)==len(set(arms)) and set(d["scores"])==set(arms)
 assert d["train_examples"]==4096 and d["cases"]==64 and len(d["rows"])==64
 assert len(d["weights"])==8
 counts={a:0 for a in arms};seen=set()
 for row in d["rows"]:
  key=(row["seed"],row["family"])
  assert key not in seen and 571100<=row["seed"]<571116
  assert row["family"] in p["diagnostic_families"]
  seen.add(key)
  events=row["public_events"];question=row["question"]
  assert len(events)==64 and len(question["chain"])==4
  assert set(row["results"])==set(arms)
  assert set(row["retained_indices"])==set(arms)-{p["unfair_control"]}
  assert all(len(e)==4 and e[1] in (0,1,2,3) and e[3] in (0,1) for e in events)
  assert sum(e[3] for e in events)==32
  for arm,indices in row["retained_indices"].items():
   assert len(indices)==12 and len(set(indices))==12
   assert all(type(i)==int and 0<=i<64 for i in indices)
   actual=int(solve([events[i] for i in indices],question)==question["answer"])
   assert row["results"][arm]==actual
  assert row["results"][p["unfair_control"]]==1
  for arm in arms:counts[arm]+=row["results"][arm]
 assert len(seen)==64
 for arm in arms:
  assert d["scores"][arm]["correct"]==counts[arm] and d["scores"][arm]["total"]==64
  assert math.isclose(d["scores"][arm]["accuracy"],counts[arm]/64,abs_tol=1e-12)
 for f in p["diagnostic_families"]:
  sub=[r for r in d["rows"] if r["family"]==f];assert len(sub)==16
  for arm in arms:
   assert d["by_family"][str(f)][arm]==sum(r["results"][arm] for r in sub)
 assert math.isclose(d["tag_core_rate"],.5,abs_tol=1e-12)
 assert math.isclose(d["tag_distractor_rate"],.5,abs_tol=1e-12)
 fair=p["baseline_controls"];best=max(fair,key=lambda a:counts[a])
 gain=(counts[p["candidate"]]-counts[best])/64
 nonreg=all(d["by_family"][str(f)][p["candidate"]]>=max(d["by_family"][str(f)][a] for a in fair)
            for f in p["diagnostic_families"])
 passed=gain>=p["threshold_absolute_gain_pp"]/100 and nonreg
 assert d["strongest_fair_control"]==best
 assert math.isclose(d["candidate_gain"],gain,abs_tol=1e-12)
 assert d["per_family_nondegradation"]==nonreg and d["frozen_gate_met"]==passed
 return {"candidate":counts[p["candidate"]],"fair":counts[best],"strongest":best,
         "gain_pp":100*gain,"no_family_regression":nonreg,"threshold_met":passed}
if __name__=="__main__":
 assert len(sys.argv)==3
 print("Y_F52_INDEPENDENT_RECOUNT_PASS",json.dumps(verify(json.load(open(sys.argv[1])),
         json.load(open(sys.argv[2]))),sort_keys=True))
