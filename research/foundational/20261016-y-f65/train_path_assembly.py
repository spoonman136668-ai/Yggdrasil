"""F65 fixed role-path assembly objective and signed-int8 fitting.

The *offline only* trainer uses future-task path fragments from FIT TRAIN
receipts for action labels; the online learned policy never receives q,
private labels, later events or source node-role identities.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
TRAIN_ROW_SHA256="69c4d6344c24c4fdffcbed636b09dee73a73b79e1e48383e189080fb7eb21245"
def gitblob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(P/"prereg.json")=="9bbfd50b740be2c9d4ec891b3b360cd9650b7e23"
assert gitblob(P/"path_assembly.py")=="10c2ba041c1d3e3063e1e98ba5726fa458db5f3a"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
METHOD=load("f65_frozen_role_path_assembler",P/"path_assembly.py")
def reversed_rec(rec):
 a,b,c=rec
 return b,a,tuple(x^1 for x in reversed(c))
def valid_task_path_fragments(public,q):
 """Offline-only full observed public graph plus future task."""
 codes=tuple(2*role+(direction==-1) for role,direction in q["ops"])
 paths={(q["start"],)}
 for code in codes:
  role,direction=code//2,code&1
  continuations=set()
  for path in paths:
   current=path[-1]
   for a,r,b in public:
    if r!=role:continue
    src,dst=(b,a) if direction else (a,b)
    if src==current:continuations.add(path+(dst,))
  paths=continuations
  assert 0<len(paths)<10000,"AMBIGUOUS_OR_UNGROUNDED_TASK_PATH"
 good_paths=[p for p in paths if p[-1]==q["answer"]]
 assert good_paths,"NO_POSTRETENTION_PUBLIC_WITNESS"
 fragments=set()
 for nodes in good_paths:
  for start in range(len(codes)):
   for size in range(1,min(6,len(codes)-start)+1):
    rec=(nodes[start],nodes[start+size],codes[start:start+size])
    fragments.add(rec);fragments.add(reversed_rec(rec))
 return fragments
def credit(records,target,full_size):
 """Future-task label only; no call from METHOD.online()."""
 total=sum(len(r[2])**2 for r in records if r in target)
 return min(total/(2*full_size*full_size),1.0)
def label_training_case(public,q):
 assert len(public)==72 and all(len(e)==3 for e in public)
 fragments=valid_task_path_fragments(public,q)
 mem=()
 samples=[];positive_merge=0
 for index,event in enumerate(public):
  candidates=METHOD.BASE.actions(mem,event,index,METHOD.PACK)
  fixed=METHOD.BASE._f60_step(mem,event,METHOD.PACK)
  matches=[c for c in candidates if c[3]==fixed]
  assert matches,"F60_BASELINE_NOT_IN_CAUSAL_ACTION_SPACE"
  baseline=matches[0]
  base_credit=credit(fixed,fragments,len(q["ops"]))
  base_features=METHOD.features(mem,event,index,baseline[0],baseline[2],fixed)
  for action,_old,drop,after,_original in candidates:
   if after==fixed:continue
   x=METHOD.features(mem,event,index,action,drop,after)
   features=tuple(a-b for a,b in zip(x,base_features))
   value=credit(after,fragments,len(q["ops"]))-base_credit
   if all(abs(v)<1e-9 for v in features):continue
   samples.append((features,value))
   if action=="merge" and value>0:positive_merge+=1
  mem=fixed
 assert len(samples)>0
 return samples,positive_merge
def train(rows):
 examples=[];useful_merges=0
 for public,q in rows:
  group,positive=label_training_case(public,q)
  examples.extend(group)
  useful_merges+=positive
 assert len(examples)>0 and useful_merges>0,"NO_SUPERVISED_PATH_ASSEMBLY_SIGNAL"
 weights=[0.0]*METHOD.PARAMS
 # Frozen chronological order, three deterministic epochs, no selection.
 for _ in range(3):
  for features,y in examples:
   x=tuple(max(-1.0,min(1.0,v)) for v in features)
   expected=max(-1.0,min(1.0,y))
   error=expected-math.tanh(sum(w*v for w,v in zip(weights,x)))
   for i,v in enumerate(x):
    weights[i]+=.025*error*v
 quant=tuple(max(-127,min(127,round(w*16))) for w in weights)
 assert len(quant)==METHOD.PARAMS
 return quant,len(examples),useful_merges
def synthetic_guard():
 training=[]
 for i in range(8):
  seed=-1201-i;family=(-2,-1)[i%2]
  public,q,_=METHOD.SOURCE.source(seed,family)
  training.append((public,q))
 weights,n,pos=train(training)
 guards=[]
 for i in range(4):
  seed=-1211-i;family=(-2,-1)[i%2]
  public,q,meta=METHOD.SOURCE.source(seed,family)
  memory,trace,merges=METHOD.online(public,weights,trace=True)
  claim=METHOD.AUDITOR.verify(public,q,trace)
  assert claim["prefixes"]==72 and claim["max_payload_bytes"]<=144
  guards.append(dict(seed=seed,kind=meta["question_type"],merges=merges,
     correct=int(METHOD.PACK.solve(memory,q)==q["answer"])))
 return dict(schema="yggdrasil.f65.path-assembly-fit.synthetic-guard.v1",
  stage="UNREGISTERED_SYNTHETIC_ONLY",synthetic_train_cases=len(training),
  guard_cases=len(guards),examples=n,positive_target_merge_events=pos,
  provisional_weights=list(weights),trained_FIT=False,heldout_executed=False,
  independent_F3=False,guard=guards)
def actual_fit(path):
 raw=path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==TRAIN_ROW_SHA256,"F65_TRAIN_EVIDENCE_IDENTITY_DRIFT"
 lines=[json.loads(l) for l in raw.decode("utf-8").splitlines()]
 assert len(lines)==32
 identities={(r["seed"],r["family"]) for r in lines}
 assert identities=={(seed,family) for seed in range(821000,821008)
                    for family in (1580,1581,1582,1583)}
 rows=[]
 for r in lines:
  public=tuple(tuple(e) for e in r["public_events"])
  q=r["postretention_question"]
  rows.append((public,q))
 weights,n,pos=train(rows)
 return dict(schema="yggdrasil.f65.frozen-role-path-assembly-fit.v1",
   source_qualified_head="fb8013361d3b41b0a73c85302a40524ea19b3683",
   first_use_training_run=38888573914,first_use_training_artifact_id=12040777717,
   source_row_sha256=TRAIN_ROW_SHA256,training_cases=len(rows),
   supervised_examples=n,positive_label_merge_examples=pos,
   frozen_weights=list(weights),
   weights_sha256=hashlib.sha256(bytes(w%256 for w in weights)).hexdigest(),
   online_future_question_access=False,offline_train_only_future_labels=True,
   training_corpus_rerun=False,validation_executed=False,
   diagnostic_executed=False,original_executed=False,F3=False,
   scientific_improvement_qualified=False,policy_promotion=False)
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 group=parser.add_mutually_exclusive_group(required=True)
 group.add_argument("--synthetic-only",action="store_true")
 group.add_argument("--archived-fit-rows",type=pathlib.Path)
 args=parser.parse_args()
 print(json.dumps(synthetic_guard() if args.synthetic_only else actual_fit(args.archived_fit_rows),sort_keys=True))
