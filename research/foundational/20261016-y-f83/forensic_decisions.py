"""F83 immutable guard-only decision forensics — no model refitting.

Frozen F83 model is replayed identically on its EXPOSED 32 synthetic guard
cases. Task-aware labels are retrospective, never accessed by selection.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="2c47c4116bcad183ef2e3f327b9760b8ea95b3c1"
assert blob(P/"forensic_prereg.json")=="9d4333afe6baf45025decf19e9cfad3319981a22"
parent=P/"pairwise_learner.py"
assert blob(parent)=="68138887c8bc42a17f8866df96cbede8e2594325"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 return module
F=load("f83_immutable_retrospective",parent)
pr=json.loads((P/"forensic_prereg.json").read_text())
w=tuple(pr["parents"]["frozen_weights"])
assert len(w)==24
assert hashlib.sha256(bytes(x%256 for x in w)).hexdigest()==pr["parents"]["weights_sha256"]
rows=[]
counters=collections.defaultdict(collections.Counter)
for seed in range(-5121,-5137,-1):
 for family in (-2,-1):
  public,q,meta=F.M.SOURCE.source(seed,family)
  memory=()
  trace=[]
  local=collections.Counter()
  for index,event in enumerate(public):
   baseline,opts=F.M.F79.unique_alternatives(memory,event,index)
   ranked=[]
   for j,(action,drop,after,_ignored) in enumerate(opts):
    features=F.M.features(memory,baseline,after,event,action,drop)
    value=F.score(tuple(z/64 for z in w),features)
    ranked.append((value,-j,after))
   ranked.sort(reverse=True)
   chosen=False
   if ranked:
    top=ranked[0][0]
    second=ranked[1][0] if len(ranked)>1 else 0.0
    chosen=bool(top>0.0 and top-second>=0.05)
   if chosen:
    candidate=ranked[0][2]
    # Task answers are used ONLY here as retrospective offline labels.
    control=F.M.F62._finish_fixed(baseline,public[index+1:],F.M.PACK)
    alternate=F.M.F62._finish_fixed(candidate,public[index+1:],F.M.PACK)
    control_good=F.M.PACK.solve(control,q)==q["answer"]
    alt_good=F.M.PACK.solve(alternate,q)==q["answer"]
    label="beneficial" if alt_good and not control_good else (
      "harmful" if control_good and not alt_good else "neutral")
    local[label]+=1
    local["interventions"]+=1
    local["early_interventions" if index<24 else "late_interventions"]+=1
    memory=candidate
   else:
    memory=baseline
   F.M.F62._valid_memory(memory,F.M.PACK)
   trace.append(tuple(F.M.PACK.pack(*r).hex() for r in memory))
  original_memory,original_trace,original_count=F.online(public,w,True,True)
  assert memory==original_memory and tuple(trace)==original_trace
  assert local["interventions"]==original_count
  proof=F.M.AUDITOR.verify(public,q,tuple(trace))
  assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
  frozen=F.M.F62.controls()[0].online_fixed(public)
  record=dict(seed=seed,family=family,
    arrival_regime=meta["arrival_regime"],question_type=meta["question_type"],
    learned_correct=int(F.M.PACK.solve(memory,q)==q["answer"]),
    frozen_F60_correct=int(F.M.PACK.solve(frozen,q)==q["answer"]),
    chosen_interventions=local["interventions"],
    early_interventions=local["early_interventions"],
    retrospective_beneficial=local["beneficial"],
    retrospective_harmful=local["harmful"],
    retrospective_neutral=local["neutral"])
  rows.append(record)
  counters[(meta["arrival_regime"],meta["question_type"])].update(local)
by_regime={}
for regime in ("original","local_rotate4"):
 selected=[r for r in rows if r["arrival_regime"]==regime]
 by_regime[regime]=dict(cases=len(selected),
   frozen_F60_correct=sum(r["frozen_F60_correct"] for r in selected),
   frozen_pairwise_correct=sum(r["learned_correct"] for r in selected),
   selected_interventions=sum(r["chosen_interventions"] for r in selected),
   early_interventions=sum(r["early_interventions"] for r in selected),
   beneficial=sum(r["retrospective_beneficial"] for r in selected),
   harmful=sum(r["retrospective_harmful"] for r in selected),
   neutral=sum(r["retrospective_neutral"] for r in selected))
by_kind={}
for kind in sorted(set(r["question_type"] for r in rows)):
 selected=[r for r in rows if r["question_type"]==kind]
 by_kind[kind]=dict(cases=len(selected),
    F60_correct=sum(r["frozen_F60_correct"] for r in selected),
    learned_correct=sum(r["learned_correct"] for r in selected),
    beneficial=sum(r["retrospective_beneficial"] for r in selected),
    harmful=sum(r["retrospective_harmful"] for r in selected),
    neutral=sum(r["retrospective_neutral"] for r in selected))
result=dict(schema="yggdrasil.f83.immutable-guard-decision-forensics.v1",
  status="READ_ONLY_ALREADY_EXPOSED_SYNTHETIC",
  cases=len(rows),model_weights_sha256=pr["parents"]["weights_sha256"],
  by_arrival_regime=by_regime,by_question_type=by_kind,
  original_F83_online_trace_exact=True,all_72_public_prefixes_audited=True,
  weights_modified=False,source_modified=False,
  new_source_cases_accessed=False,registered_FIT_train_used=False,
  registered_FIT_validation_used=False,DIAG_used=False,
  original_used=False,F3=False,optimizer_promotion=False,rows=rows)
assert len(rows)==32
assert sum(r["chosen_interventions"] for r in rows)==737
assert sum(r["frozen_F60_correct"] for r in rows)==19
assert sum(r["learned_correct"] for r in rows)==10
print(json.dumps(result,sort_keys=True))
