"""F67A read-only causal bridge opportunity trace; only negative seeds.

Distinguish 'the correct edge was not offered' from 'offered then rejected'
and 'selected but eventually evicted'. Frozen method and weights unmodified.
"""
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"train_structural_junction.py")=="edbd46327fa9368e2f02346d48ede5a01207eb65"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
teacher=load("f67a_frozen_structural_labeler",P/"train_structural_junction.py")
m=teacher.m
synthetic=[]
for k in range(8):
 public,_q,_meta=m.SOURCE.source(-2501-k,(-2,-1)[k%2])
 synthetic.append(public)
weights,_stats=teacher.train(synthetic)
rowdetails=[]
for k in range(8):
 seed=-2511-k;family=(-2,-1)[k%2]
 public,q,meta=m.SOURCE.source(seed,family)
 truth=teacher.full_public_bridge_edges(public)
 state=()
 seen=[]
 activity=[]
 for i,event in enumerate(public):
  all_choices=m.ACTION.actions(state,event,i,m.PACK)
  available={tuple(record[3]) for record in all_choices}
  nxt,chosen,after=m.ACTION._f60_step(state,event,m.PACK),None,None
  next_state=None;best=None
  for j,(action,_old,drop,candidate,_other) in enumerate(all_choices):
   features=m.features(state,event,i,action,drop,candidate)
   score=sum(w*x for w,x in zip(weights,features))
   key=(score,-j)
   if best is None or key>best[0]:best=(key,action,candidate)
  chosen=best[1];next_state=best[2]
  incoming=tuple(event) in truth
  if incoming:
   exact=m.PACK.edge_record(event)
   valid_candidates=sum(int(exact in candidate) for _a,_o,_d,candidate,_f in all_choices)
   public_signal=m.public_junction_signal(state,event)
   activity.append(dict(index=i,
    exact_bridge_legal_candidate_count=valid_candidates,
    selected_exact_bridge=int(exact in next_state),
    signal=list(public_signal),
    selected_action=chosen,
    initial_memory_records=len(state),
    chosen_after_records=len(next_state)))
  seen.append(tuple(next_state))
  state=next_state
 assert len(activity)==2
 for row in activity:
  exact=m.PACK.edge_record(public[row["index"]])
  later=[i for i in range(row["index"],72) if exact in seen[i]]
  row["remaining_prefix_count"]=len(later)
  row["present_at_final"]=int(exact in seen[-1])
 rowdetails.append(dict(seed=seed,kind=meta["question_type"],bridges=activity,
    learned_correct=int(m.PACK.solve(state,q)==q["answer"])))
totals=dict(bridge_observation_count=sum(len(x["bridges"]) for x in rowdetails),
 true_bridge_with_causal_legal_storage=sum(int(y["exact_bridge_legal_candidate_count"]>0) for x in rowdetails for y in x["bridges"]),
 true_bridge_selected_on_arrival=sum(y["selected_exact_bridge"] for x in rowdetails for y in x["bridges"]),
 true_bridge_retained_at_final=sum(y["present_at_final"] for x in rowdetails for y in x["bridges"]),
 available_separate_component_signal=sum(int(y["signal"][0]) for x in rowdetails for y in x["bridges"]),
 available_frontier_signal=sum(int(y["signal"][1]) for x in rowdetails for y in x["bridges"]))
out=dict(schema="yggdrasil.f67a.synthetic-bridge-choice-forensics.v1",
 status="READ_ONLY",frozen_model_weights=list(weights),
 source_model_unchanged=True,negative_seed_cases=len(rowdetails),
 evidence=totals,heldout_consumed=False,FIT_consumed=False,
 diagnostic_consumed=False,original_consumed=False,F3=False,
 optimizer_promotion=False,rows=rowdetails)
print(json.dumps(out,sort_keys=True))
