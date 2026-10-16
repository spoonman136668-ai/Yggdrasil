"""F66B dense offline public-continuation opportunity-cost learning.

PRECODE synthetic ONLY. Unlike the rejected F66 teacher, losing a retained
intermediate endpoint that could connect to a future public edge incurs
explicit opportunity cost. The online policy never sees future edges.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert gitblob(HERE/"prereg.json")=="fc3283f28ab307b6834c93d530fffce98ad7c0de"
assert gitblob(HERE/"prereg-opportunity-cost-amendment.json")=="3502d23f503cb0fdc798b2ac7db3f5cdb09c254d"
assert gitblob(HERE/"two_head_continuation.py")=="fa08d72d79380a82814c86482e98b206b69b4d4a"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 return module
POLICY=load("f66b_sha_frozen_two_head_runtime",HERE/"two_head_continuation.py")
AMEND=json.loads((HERE/"prereg-opportunity-cost-amendment.json").read_text())
M=AMEND["fixed_new_method"]
def future_public_utility(records,later_public):
 endpoint_degree={}
 for a,_r,b in later_public:
  endpoint_degree[a]=endpoint_degree.get(a,0)+1
  endpoint_degree[b]=endpoint_degree.get(b,0)+1
 path_reward=0.
 future_relevance=0.
 for a,b,codes in records:
  path_reward+=M["role_chain_reward_coefficient"]*len(codes)**2/36
  endpoint_support=min(M["public_future_incident_cap"],
                       endpoint_degree.get(a,0)+endpoint_degree.get(b,0))
  future_relevance+=M["future_endpoint_support_coefficient"]*endpoint_support/M["public_future_incident_cap"]
 slack=M["capacity_slack_reward_coefficient"]*(12-len(records))/12
 return (path_reward+future_relevance+slack)/12
def case_supervision(public):
 gate=[];retention=[];positive=negative=neutral=0
 memory=()
 for index,event in enumerate(public):
  later=public[index+1:]
  actions=POLICY.ACTION.actions(memory,event,index,POLICY.PACK)
  winners={}
  for j,(name,_old,drop,after,_features) in enumerate(actions):
   util=future_public_utility(after,later)
   key=(util,-j)
   if name not in winners or key>winners[name][0]:
    winners[name]=(key,after,drop)
  if "merge" in winners:
   topmerge=winners["merge"];topappend=winners["append"]
   delta=topmerge[0][0]-topappend[0][0]
   if delta>1e-8:positive+=1
   elif delta< -1e-8:negative+=1
   else:neutral+=1
   gx=POLICY.gate_features(memory,topmerge[1],topappend[1],event,index)
   gate.append((gx,max(-1.,min(1.,delta*6))))
  for name,teacher in winners.items():
   tf=POLICY.rank_features(teacher[1],name,teacher[2],index,len(memory))
   for a,_old,drop,after,_f in actions:
    if a!=name or after==teacher[1]:continue
    feat=POLICY.rank_features(after,a,drop,index,len(memory))
    diff=tuple(x-y for x,y in zip(tf,feat))
    delta=teacher[0][0]-future_public_utility(after,later)
    if any(abs(v)>1e-9 for v in diff):
     retention.append((diff,max(-1.,min(1.,delta*6))))
  memory=POLICY.ACTION._f60_step(memory,event,POLICY.PACK)
 return gate,retention,positive,negative,neutral
def fit(publics):
 gate=[];ranking=[];positive=negative=neutral=0
 for public in publics:
  g,r,p,n,z=case_supervision(public)
  gate.extend(g);ranking.extend(r)
  positive+=p;negative+=n;neutral+=z
 counts=dict(gate_samples=len(gate),rank_samples=len(ranking),
             positive_merge_labels=positive,negative_merge_labels=negative,
             neutral_merge_labels=neutral)
 if not (positive>0 and negative>0 and gate and ranking):
  return None,counts
 weights_gate=[0.0]*POLICY.GATE_PARAMS
 weights_rank=[0.0]*POLICY.RANK_PARAMS
 for _ in range(M["training_sgd_epochs"]):
  for x,y in gate:
   pred=math.tanh(sum(w*v for w,v in zip(weights_gate,x)))
   for i,v in enumerate(x):
    weights_gate[i]+=M["fixed_gate_step"]*(y-pred)*v
  for x,y in ranking:
   pred=math.tanh(sum(w*v for w,v in zip(weights_rank,x)))
   for i,v in enumerate(x):
    weights_rank[i]+=M["fixed_retention_step"]*(y-pred)*v
 scale=M["weight_quantization_scale"]
 quant=tuple(max(-127,min(127,round(w*scale))) for w in weights_gate+weights_rank)
 assert len(quant)==POLICY.TOTAL_PARAMS
 return quant,counts
def synthetic_guard():
 training=[]
 for i in range(8):
  seed=-2101-i;family=(-2,-1)[i%2]
  public,_q,_meta=POLICY.SOURCE.source(seed,family)
  training.append(public)
 weights,counts=fit(training)
 guards=[]
 if weights is not None:
  for i in range(8):
   seed=-2111-i;family=(-2,-1)[i%2]
   public,q,meta=POLICY.SOURCE.source(seed,family)
   retained,trace,merges=POLICY.online(public,weights,True)
   proof=POLICY.AUDITOR.verify(public,q,trace)
   assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
   ablated,trace_ab,ablmerges=POLICY.online(public,weights,True,False)
   assert POLICY.AUDITOR.verify(public,q,trace_ab)["prefixes"]==72
   guards.append(dict(seed=seed,kind=meta["question_type"],
        learned_merge_steps=merges,ablation_merge_steps=ablmerges,
        learned_correct=int(POLICY.PACK.solve(retained,q)==q["answer"])))
 qualified=bool(weights is not None and sum(g["learned_merge_steps"] for g in guards)>0)
 return dict(schema="yggdrasil.f66b.public-future-opportunity-cost.synthetic.v1",
   status=("SYNTHETIC_MECHANISM_ELIGIBLE" if qualified else "SYNTHETIC_METHOD_BLOCKED"),
   qualified=qualified,teacher_counts=counts,
   synthetic_training_cases=len(training),independent_guard_cases=len(guards),
   frozen_synthetic_weights=list(weights) if weights is not None else None,
   guard_learned_merges=sum(g["learned_merge_steps"] for g in guards),
   protected_fit_train_executed=False,fit_validation_executed=False,
   diagnostic_executed=False,original_executed=False,F3=False,guards=guards)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(synthetic_guard(),sort_keys=True))
