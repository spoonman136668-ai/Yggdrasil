"""Y-F51 independent evidence audit: memory receipts and future query separation."""
import json,math,sys
def audit(path,prereg):
 d=json.load(open(path));p=json.load(open(prereg))
 t=p["fit"];v=p["diagnostic"];st=p["stream"];arms=p["controls"]
 assert d["schema"]=="yggdrasil.f51.neutral-tags-structural-memory.trainonly.v1"
 assert d["stage"]=="TRAIN_ONLY_UNSEEN_DISTRACTOR_GRAPH_TOPOLOGY_NOT_ORIGINAL"
 assert d["fit_seeds"]==t["seeds"] and d["fit_families"]==t["families"]
 assert d["diagnostic_seeds"]==v["seeds"] and d["diagnostic_families"]==v["families"]
 assert set(t["families"]).isdisjoint(v["families"])
 assert d["cases"]==len(d["rows"])==v["expected_streams"]==64
 assert d["train_examples"]==t["expected_streams"]*st["events"]==4096
 assert d["events_per_stream"]==st["events"]==64
 assert d["memory_cap_edges"]==st["memory_edges_max"]==12
 assert d["future_question_hidden_until_retention_complete"]
 assert d["original_seeds_NOT_RESERVED"]==p["future_original_NOT_RESERVED"]["seeds"]
 assert len(d["weights"])==7
 assert d["tag_core_rate"]==st["tag_probability_core"]==.5
 assert d["tag_distractor_rate"]==st["tag_probability_distractor"]==.5
 assert not d["source_independent_F3"] and not d["original_executed"]
 assert not d["native_576_bytes_residency_qualified"] and not d["accepted_ref_mutation"]
 assert d["paid_api_calls"]==0
 count={a:0 for a in arms};seen=set()
 for row in d["rows"]:
  key=row["seed"],row["family"]
  assert key not in seen;seen.add(key)
  assert 531100<=row["seed"]<531116 and row["family"] in v["families"]
  assert len(row["public_events"])==64
  assert len(row["question"]["chain"])==4
  assert set(row["results"])==set(arms)
  assert set(row["retained_indices"])==set(arms)-{"private_future_question_oracle_unfair"}
  assert len({tuple(e[:3]) for e in row["public_events"]})==64
  for arm,indices in row["retained_indices"].items():
   assert len(indices)==12 and len(set(indices))==12
   assert all(isinstance(i,int) and 0<=i<64 for i in indices)
   held=[row["public_events"][i] for i in indices]
   at=row["question"]["start"];valid=True
   for role,direction in row["question"]["chain"]:
    candidate=[e for e in held if e[1]==role and (e[0] if direction==1 else e[2])==at]
    if len(candidate)!=1:valid=False;break
    at=candidate[0][2] if direction==1 else candidate[0][0]
   assert row["results"][arm]==int(valid and at==row["question"]["answer"])
  assert row["results"]["private_future_question_oracle_unfair"]==1
  for arm in arms:
   assert row["results"][arm] in (0,1)
   count[arm]+=row["results"][arm]
 assert len(seen)==64
 for arm in arms:
  assert d["scores"][arm]["correct"]==count[arm] and d["scores"][arm]["total"]==64
  assert math.isclose(d["scores"][arm]["accuracy"],count[arm]/64,abs_tol=1e-12)
 for f in v["families"]:
  sub=[r for r in d["rows"] if r["family"]==f]
  assert len(sub)==16
  for arm in arms:assert d["by_family"][str(f)][arm]==sum(r["results"][arm] for r in sub)
 fair=arms[1:-1];best=max(fair,key=lambda a:count[a])
 gain=(count["learned_topology_retention"]-count[best])/64
 nonreg=all(d["by_family"][str(f)]["learned_topology_retention"]>=max(
   d["by_family"][str(f)][a] for a in fair) for f in v["families"])
 passed=gain>=p["thresholds"]["gain_vs_strongest_fair_min"] and nonreg
 assert d["strongest_fair_control"]==best
 assert math.isclose(d["candidate_gain"],gain,abs_tol=1e-12)
 assert d["per_family_nondegradation"]==nonreg and d["frozen_gate_met"]==passed
 assert d["verdict"]==("TRAIN_ONLY_STRUCTURAL_MEMORY_SUPPORTED" if passed else
                       "TRAIN_ONLY_STRUCTURAL_MEMORY_NEGATIVE")
 print("Y_F51",d["verdict"],"correct",count,"gain",gain,"family_guard",nonreg,
       "tag_rates",(d["tag_core_rate"],d["tag_distractor_rate"]))
if __name__=="__main__":
 assert len(sys.argv)==3
 audit(sys.argv[1],sys.argv[2])
