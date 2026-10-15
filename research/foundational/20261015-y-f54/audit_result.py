"""Y-F54 independent decoder/reconstruction audit from source-free records."""
import json,math,sys
def inverse(r):
 return r["to_node"],tuple((role,-d) for role,d in reversed(r["steps"])),r["from_node"]
def answer(memory,q):
 states={(q["start"],0)}
 seq=tuple(tuple(k) for k in q["chain"])
 for _ in range(len(seq)):
  updated=set()
  for node,i in states:
   for r in memory:
    possibilities=((r["from_node"],tuple(tuple(z) for z in r["steps"]),r["to_node"]),inverse(r))
    for u,steps,v in possibilities:
     if u==node and seq[i:i+len(steps)]==steps:updated.add((v,i+len(steps)))
  states|=updated
 return int((q["answer"],len(seq)) in states)
def check(x,p):
 assert x["schema"]=="yggdrasil.f54.query-blind-multihop-composition.trainonly.v1"
 assert x["stage"]=="FRESH_EQUAL_PAYLOAD_TRAIN_ONLY_NO_ORIGINAL"
 assert x["fit_seeds"]==p["fit_seeds"] and x["diagnostic_seeds"]==p["diagnostic_seeds"]
 assert x["diagnostic_families"]==p["diagnostic_families"]
 assert x["original_seeds_NOT_RESERVED"]==p["proposed_originals_NOT_RESERVED"]
 assert x["total_native_576B_residency_qualified"] is False
 assert x["future_question_hidden_during_ingestion"] is True
 assert x["independent_F3"] is False and x["original_executed"] is False
 assert x["accepted_ref_mutation"] is False and x["paid_api_calls"]==0
 assert x["serialized_payload_bytes_per_record"]==12 and x["serialized_payload_budget_bytes"]==144
 assert len(x["learned_fit_weights"])==8
 assert x["cases"]==64 and len(x["rows"])==64
 arms=p["controls"];assert set(x["scores"])==set(arms)
 seen=set();counts={a:0 for a in arms}
 for r in x["rows"]:
  key=r["seed"],r["family"]
  assert key not in seen and 611100<=key[0]<611116 and key[1] in p["diagnostic_families"]
  seen.add(key)
  events=r["public_events"];q=r["question"]
  assert len(events)==64 and len(q["chain"])==4
  assert set(r["results"])==set(arms) and set(r["retained_records"])==set(arms[:-1])
  for arm,records in r["retained_records"].items():
   assert len(records)<=12
   for z in records:
    assert z["serialized_payload_bytes"]==12
    assert len(z["steps"]) in ((1,2,3) if arm=="fixed_public_three_link_composition" else
                 (1,2) if arm in ("fit_public_two_link_composition","fixed_public_two_link_composition") else (1,))
    ix=z["witness_indices"]
    assert len(ix)==len(z["steps"]) and len(set(ix))==len(ix)
    assert all(0<=i<64 for i in ix)
    first=events[ix[0]];assert z["from_node"]==first[0] or z["from_node"]==first[2]
    at=z["from_node"]
    for (role,d),i in zip(z["steps"],ix):
     edge=events[i]
     assert role==edge[1]
     assert (edge[0] if d==1 else edge[2])==at
     at=edge[2] if d==1 else edge[0]
    assert at==z["to_node"]
   assert answer(records,q)==r["results"][arm]
  assert r["results"][arms[-1]]==1
  for a in arms:counts[a]+=r["results"][a]
 assert len(seen)==64
 for a in arms:assert x["scores"][a]["correct"]==counts[a] and x["scores"][a]["total"]==64
 by={}
 for family in p["diagnostic_families"]:
  sub=[r for r in x["rows"] if r["family"]==family]
  assert len(sub)==16
  by[str(family)]={a:sum(r["results"][a] for r in sub) for a in arms}
  assert by[str(family)]==x["by_family"][str(family)]
 cand=arms[0];fair=p["fair_controls"];best=max(fair,key=lambda a:counts[a])
 gain=(counts[cand]-counts[best])/64
 no_reg=all(by[str(f)][cand]>=max(by[str(f)][a] for a in fair) for f in p["diagnostic_families"])
 passed=gain>=p["threshold_gain_pp"]/100 and no_reg
 assert x["strongest_fair_control"]==best and math.isclose(x["candidate_gain"],gain,abs_tol=1e-12)
 assert x["per_family_nondegradation"]==no_reg and x["frozen_gate_met"]==passed
 return dict(candidate=counts[cand],strongest=best,strongest_correct=counts[best],
   gain_pp=100*gain,no_family_regression=no_reg,criterion_met=passed)
if __name__=="__main__":
 assert len(sys.argv)==3
 print("Y_F54_INDEPENDENT_RECOUNT_PASS",json.dumps(check(json.load(open(sys.argv[1])),json.load(open(sys.argv[2]))),sort_keys=True))
