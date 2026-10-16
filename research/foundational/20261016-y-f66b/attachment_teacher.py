"""F66B pre-frozen attachment opportunity-cost teacher (synthetic only).

This is a distinct, preregistered teacher correction to F66.
Offline training may inspect future TRAIN public edges. The actual online
two-head policy is an immutable import, with no future-question or oracle.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def load(name,path,expected):
 assert gitblob(path)==expected,(name,"FROZEN_METHOD_IDENTITY_DRIFT")
 spec=importlib.util.spec_from_file_location(name,path)
 obj=importlib.util.module_from_spec(spec)
 sys.modules[name]=obj
 spec.loader.exec_module(obj)
 return obj
POLICY=load("f66b_immutable_F66_online",P.parent/"20261016-y-f66"/"two_head_continuation.py",
            "fa08d72d79380a82814c86482e98b206b69b4d4a")
prereg=json.loads((P/"prereg.json").read_text())
assert prereg["stage"]=="PRECODE_FROZEN_NO_FIT_USE"
assert prereg["teacher_frozen_terms"]["compression_coeff"]==.18
assert prereg["teacher_frozen_terms"]["future_attachment_coeff"]==.55
assert prereg["teacher_frozen_terms"]["endpoint_flexibility_coeff"]==.28

def teacher_utility(records,future_public):
 """Exactly frozen utility; unique endpoints are public and lossless."""
 degrees={}
 for a,_r,b in future_public:
  degrees[a]=degrees.get(a,0)+1
  degrees[b]=degrees.get(b,0)+1
 ends={n for a,b,_ in records for n in (a,b)}
 compression=sum(len(codes)**2 for _,_,codes in records)
 attachment=sum(min(2,degrees.get(n,0)) for n in ends)
 return (.18*compression+.55*attachment+.28*len(ends))/12

def choices_with_teacher(memory,event,index,future):
 candidates=POLICY.ACTION.actions(memory,event,index,POLICY.PACK)
 best={}
 for j,(action,_old,drop,after,_orig) in enumerate(candidates):
  value=teacher_utility(after,future)
  if action not in best or (value,-j)>best[action][0]:
   best[action]=((value,-j),after,drop)
 return best,candidates

def supervised_case(public):
 assert len(public)==72 and all(len(x)==3 for x in public)
 gate=[];rank=[];positive=negative=0
 memory=()
 for index,event in enumerate(public):
  future=public[index+1:]
  best,options=choices_with_teacher(memory,event,index,future)
  if "merge" in best:
   merged=best["merge"]
   appended=best["append"]
   gf=POLICY.gate_features(memory,merged[1],appended[1],event,index)
   delta=merged[0][0]-appended[0][0]
   label=max(-1,min(1,delta*8))
   positive+=int(delta>1e-8)
   negative+=int(delta< -1e-8)
   gate.append((gf,label))
  for action in ("append","merge"):
   if action not in best:continue
   anchor=best[action]
   features=POLICY.rank_features(anchor[1],action,anchor[2],index,len(memory))
   for a,_old,drop,after,_oldfeat in options:
    if a!=action or after==anchor[1]:continue
    other=POLICY.rank_features(after,a,drop,index,len(memory))
    diff=tuple(x-y for x,y in zip(features,other))
    gap=anchor[0][0]-teacher_utility(after,future)
    target=max(-1,min(1,gap*8))
    if any(abs(z)>1e-10 for z in diff):
     rank.append((diff,target))
  memory=POLICY.ACTION._f60_step(memory,event,POLICY.PACK)
 return gate,rank,positive,negative

def train(public_cases):
 gate=[];rank=[];positive=negative=0
 for public in public_cases:
  g,r,p,n=supervised_case(public)
  gate.extend(g);rank.extend(r);positive+=p;negative+=n
 if not (gate and rank and positive and negative):
  raise AssertionError("F66B_TRADEOFF_TEACHER_CLASS_BALANCE_REQUIRED")
 gw=[0.0]*POLICY.GATE_PARAMS
 rw=[0.0]*POLICY.RANK_PARAMS
 for _ in range(3):
  for x,target in gate:
   error=target-math.tanh(sum(w*f for w,f in zip(gw,x)))
   for j,f in enumerate(x):gw[j]+=.03*error*f
  for x,target in rank:
   error=target-math.tanh(sum(w*f for w,f in zip(rw,x)))
   for j,f in enumerate(x):rw[j]+=.01*error*f
 weights=tuple(max(-127,min(127,round(w*32))) for w in gw+rw)
 assert len(weights)==POLICY.TOTAL_PARAMS
 return weights,dict(gate_examples=len(gate),rank_examples=len(rank),
                     positive_merges=positive,negative_merges=negative)

def synthetic_guard():
 synthetic=[]
 for i in range(8):
  public,_q,_meta=POLICY.SOURCE.source(-2101-i,(-2,-1)[i%2])
  synthetic.append(public)
 weights,stats=train(synthetic)
 guards=[]
 for i in range(4):
  seed=-2111-i;family=(-2,-1)[i%2]
  public,q,meta=POLICY.SOURCE.source(seed,family)
  retained,trace,merges=POLICY.online(public,weights,True)
  auditor=POLICY.AUDITOR.verify(public,q,trace)
  assert auditor["prefixes"]==72 and auditor["max_payload_bytes"]<=144
  disabled,trace_ab,merges_ab=POLICY.online(public,weights,True,False)
  assert POLICY.AUDITOR.verify(public,q,trace_ab)["prefixes"]==72
  guards.append(dict(seed=seed,family=family,kind=meta["question_type"],
    trained_merges=merges,no_continuation_merges=merges_ab,
    trained_correct=int(POLICY.PACK.solve(retained,q)==q["answer"])))
 result=dict(schema="yggdrasil.f66b.attachment-cost-teacher.synthetic.v1",
    stage="SYNTHETIC_ONLY",fit_seed_count=8,guard_count=4,
    weights=list(weights),counts=stats,
    learned_merge_count=sum(x["trained_merges"] for x in guards),
    positive_and_negative_evidence=True,
    causal_prefix_audit_pass=True,
    model_merge_gate_pass=sum(x["trained_merges"] for x in guards)>0,
    registered_fit_used=False,heldout_used=False,diag_used=False,original_used=False,
    F3=False,optimizer_mutation=False,guards=guards)
 print(json.dumps(result,sort_keys=True))
 if not result["model_merge_gate_pass"]:
  raise AssertionError("F66B_SYNTHETIC_MODEL_NO_LEARNED_MERGE")
 return result
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 synthetic_guard()
