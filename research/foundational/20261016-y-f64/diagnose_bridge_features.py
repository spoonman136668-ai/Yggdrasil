"""F64 diagnosis of zero-accuracy causal mechanism on synthetic identities ONLY."""
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(P/"bridge_features.py")=="75d952228c53cf9d41d1cb557fee27e421a96972"
assert gitblob(P/"frozen_model_receipt.json")=="bc4672326454bceeabc4374afa2b55fbcdae3e65"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
policy=load("f64_frozen_forensics_policy",P/"bridge_features.py")
receipt=json.loads((P/"frozen_model_receipt.json").read_text())
weights=tuple(receipt["frozen_int8_weights"])
assert weights==(6,-5,13,0,2,2,1,-1)
def replay(public,bridge):
 memory=()
 diag={"available_merge_actions":0,"candidate_explicit_bridge_preservations":0,
       "chosen_explicit_bridge_preservations":0,"chosen_merges":0,
       "chosen_score_zero":0,"total_candidates":0}
 history=[]
 for index,event in enumerate(public):
  choices=policy.BASE.actions(memory,event,index,policy.PACK)
  diag["total_candidates"]+=len(choices)
  diag["available_merge_actions"]+=sum(int(c[0]=="merge") for c in choices)
  available_preserved=0
  best=None
  chosen=None
  for j,(action,_old,_drop,after,_f) in enumerate(choices):
   feat=policy.features(memory,event,after,action,index)
   if feat[3]>0:
    available_preserved+=1
   score_features=feat if bridge else feat[:3]+(0.0,0.0)+feat[5:]
   score=sum(w*f for w,f in zip(weights,score_features))
   key=(score,-j)
   if best is None or key>best:
    best=key
    chosen=(action,after,feat,score)
  action,memory,feat,score=chosen
  diag["candidate_explicit_bridge_preservations"]+=int(available_preserved>0)
  diag["chosen_explicit_bridge_preservations"]+=int(feat[3]>0)
  diag["chosen_merges"]+=int(action=="merge")
  diag["chosen_score_zero"]+=int(score==0)
  history.append(tuple(policy.PACK.pack(*r).hex() for r in memory))
 return memory,tuple(history),diag
cases=[]
for n in range(24):
 seed=-901-n;family=(-2,-1)[n%2]
 public,q,meta=policy.SOURCE.source(seed,family)
 regular,trace,d1=replay(public,True)
 ablated,trace_abl,d2=replay(public,False)
 actual,actualtrace=policy.online(public,weights,True,True)
 actual_ab,actualtrace_ab=policy.online(public,weights,True,False)
 assert regular==actual and trace==actualtrace
 assert ablated==actual_ab and trace_abl==actualtrace_ab
 assert policy.AUDIT.verify(public,q,trace)["prefixes"]==72
 assert policy.AUDIT.verify(public,q,trace_abl)["prefixes"]==72
 cases.append({"seed":seed,"family":family,"kind":meta["question_type"],
   "model_correct":int(policy.PACK.solve(regular,q)==q["answer"]),
   "no_bridge_correct":int(policy.PACK.solve(ablated,q)==q["answer"]),
   "prefix_differences":sum(int(a!=b) for a,b in zip(trace,trace_abl)),
   "diagnostics":d1,"ablation_diagnostics":d2})
keys=("available_merge_actions","candidate_explicit_bridge_preservations",
      "chosen_explicit_bridge_preservations","chosen_merges","chosen_score_zero","total_candidates")
summary={name:sum(r["diagnostics"][name] for r in cases) for name in keys}
out=dict(schema="yggdrasil.f64.synthetic-mechanism-forensics.v1",
 status="READ_ONLY_SYNTHETIC",frozen_weights=list(weights),
 explicit_bridge_weight=weights[3],cases=24,
 model_correct=sum(x["model_correct"] for x in cases),
 ablated_correct=sum(x["no_bridge_correct"] for x in cases),
 cases_with_differing_online_decisions=sum(x["prefix_differences"]>0 for x in cases),
 divergent_prefixes=sum(x["prefix_differences"] for x in cases),
 mechanism_counts=summary,
 protected_fit_train_rerun=False,heldout_consumed=False,F3=False,policy_promoted=False,
 rows=cases)
print(json.dumps(out,sort_keys=True))
