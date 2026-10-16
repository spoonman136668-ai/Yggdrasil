"""F76 two-regime arrival-shift source: ADAPTIVE source engineering ONLY.

The F75 synthetic outcome prompted this NEW prereg with disjoint seeds.
No old F75 cases are used or relabeled. All positive registered scientific
seeds are rejected by source() and may be used only after separate custody.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 raw=path.read_bytes();return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert blob(P/"prereg.json")=="8f4179dd8116dfb8ef9e56d68b858d1484abca47"
def load(name,path,sha):
 assert blob(path)==sha,(name,"SCIENCE_FROZEN_SOURCE_IDENTITY_DRIFT")
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
BASE=load("f76_unchanged_original_public_generator",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
ACTION=load("f76_frozen_source_F60_controls",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDITOR=load("f76_independent_exact_public_prefix_audit",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=ACTION.codec()
def shift(public,family):
 assert len(public)==72
 if family%2==0:return tuple(public),"original"
 return tuple(x for i in range(0,72,4)
              for x in (public[i+1],public[i+2],public[i+3],public[i])),"local_rotate4"
def _create(seed,family,attempt):
 public,q,meta=BASE._create(seed,family,attempt)
 shifted,regime=shift(public,family)
 assert collections.Counter(public)==collections.Counter(shifted)
 # Source retries any nonunique public answer before first registered use.
 merged=dict(meta,source_id="F76_ADAPTIVE_SOURCE",
             arrival_regime=regime,original_F63C_regime=meta["regime"])
 return shifted,q,merged
def source(seed,family):
 if seed>=0 or family not in (-2,-1):
  raise ValueError("F76_REGISTERED_COHORT_SOURCE_DENIED")
 for attempt in range(8):
  public,q,meta=_create(seed,family,attempt)
  if BASE.public_witness(public,q)=={q["answer"]}:return public,q,meta
 raise AssertionError("F76_INDEPENDENT_PUBLIC_WITNESS_NOT_UNIQUE")
def audit_frozen_F60(public,q):
 memory=()
 trace=[]
 for event in public:
  memory=ACTION._f60_step(memory,event,PACK)
  ACTION._valid_memory(memory,PACK)
  trace.append(tuple(PACK.pack(*r).hex() for r in memory))
 proof=AUDITOR.verify(public,q,trace)
 assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
 return int(PACK.solve(memory,q)==q["answer"])
def synthetic_source_qualification():
 rows=[]
 for k in range(32):
  seed=-4201-k;family=(-2,-1)[k%2]
  public,q,meta=source(seed,family)
  assert len(public)==72 and len(set(public))==72
  assert BASE.public_witness(public,q)=={q["answer"]}
  good=audit_frozen_F60(public,q)
  rows.append(dict(seed=seed,family=family,
    arrival_regime=meta["arrival_regime"],
    question_type=meta["question_type"],
    F60_correct=good,public_answer_unique=True,
    independent_full_prefix_causality=True,
    F63C_original_regime=meta["original_F63C_regime"]))
 summary={}
 for regime in ("original","local_rotate4"):
  sub=[r for r in rows if r["arrival_regime"]==regime]
  correct=sum(r["F60_correct"] for r in sub)
  kinds={r["question_type"] for r in sub}
  summary[regime]=dict(cases=len(sub),frozen_F60_correct=correct,
    accuracy=correct/len(sub),meets_minimum_25_percent=(correct/len(sub)>=.25),
    both_question_types_present=(len(kinds)==2),
    per_type={kind:dict(cases=sum(r["question_type"]==kind for r in sub),
      F60_correct=sum(r["F60_correct"] for r in sub if r["question_type"]==kind))
      for kind in sorted(kinds)})
 assert sum(r["F60_correct"] for r in rows)<=32
 source_pass=all(x["meets_minimum_25_percent"] and x["both_question_types_present"]
                 for x in summary.values())
 result=dict(schema="yggdrasil.f76.adaptive-two-order-source.synthetic-qualification.v1",
  stage="PRE_REGISTERED_ADAPTIVE_SYNTHETIC_ONLY",
  source_selection_was_informed_by_F75_exposed_synthetic_result=True,
  cases=32,by_arrival_regime=summary,
  frozen_source_feasibility_gate_pass=source_pass,
  independent_public_witness_all_cases_pass=True,
  independent_72_prefix_causality_pass=True,
  registered_FIT_train_used=False,registered_FIT_validate_used=False,
  diagnostic_used=False,original_used=False,F3=False,
  optimizer_promotion=False,scientific_improvement_claim=False,rows=rows)
 print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 synthetic_source_qualification()
