"""F75 preregistered local public-order source feasibility, synthetic ONLY.

No task/model training. The same frozen graph and future question are used
under three deterministic event arrival permutations. Retention remains
the unchanged F60 controller with 12 lossless 12-byte records.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert blob(P/"prereg.json")=="0abfd46d50b333ab854ab2c2f846740b532cf7e2"
def load(name,path,sha):
 assert blob(path)==sha,(name,"FROZEN_SCIENTIFIC_SOURCE_DRIFT")
 spec=importlib.util.spec_from_file_location(name,path)
 obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj
SOURCE=load("f75_immutable_public_source",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
ACTION=load("f75_frozen_F60_memory_controls",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDITOR=load("f75_frozen_independent_public_prefix_audit",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=ACTION.codec()
def orders(events):
 events=tuple(events)
 assert len(events)==72
 adjacent=tuple(edge for i in range(0,72,2) for edge in (events[i+1],events[i]))
 rotate=tuple(edge for i in range(0,72,4) for edge in
              (events[i+1],events[i+2],events[i+3],events[i]))
 return dict(original=events,adjacent_swap=adjacent,local_rotate4=rotate)
def frozen_F60(public,q):
 memory=()
 trace=[]
 for event in public:
  memory=ACTION._f60_step(memory,event,PACK)
  ACTION._valid_memory(memory,PACK)
  trace.append(tuple(PACK.pack(*r).hex() for r in memory))
 claim=AUDITOR.verify(public,q,trace)
 assert claim["prefixes"]==72 and claim["max_payload_bytes"]<=144
 return int(PACK.solve(memory,q)==q["answer"])
def main():
 rows=[]
 for k in range(24):
  seed=-4001-k;family=(-2,-1)[k%2]
  public,q,meta=SOURCE.source(seed,family)
  assert len(public)==72 and len(set(public))==72
  for name,reordered in orders(public).items():
   assert collections.Counter(reordered)==collections.Counter(public)
   assert SOURCE.public_witness(reordered,q)=={q["answer"]}
   correct=frozen_F60(reordered,q)
   rows.append(dict(seed=seed,family=family,
       question_type=meta["question_type"],
       order=name,F60_correct=correct,
       frozen_public_witness_unique=True,
       independent_F60_prefix_causality=True))
 groups={}
 for name in ("original","adjacent_swap","local_rotate4"):
  group=[x for x in rows if x["order"]==name]
  correct=sum(x["F60_correct"] for x in group)
  kind={label:dict(cases=sum(x["question_type"]==label for x in group),
    F60_correct=sum(x["F60_correct"] for x in group if x["question_type"]==label))
    for label in sorted({x["question_type"] for x in group})}
  groups[name]=dict(cases=len(group),F60_correct=correct,
    F60_accuracy=correct/len(group),source_F60_min25_pass=correct>=6,
    per_question_type=kind,
    both_question_types_present=len(kind)==2)
 qualified=all(g["source_F60_min25_pass"] and g["both_question_types_present"]
               for g in groups.values())
 outcome=dict(schema="yggdrasil.f75.mild-arrival-jitter.source-feasibility.v1",
    stage="UNREGISTERED_SYNTHETIC_SOURCE_ONLY",
    synthetic_base_cases=24,public_order_families=3,total_cases=len(rows),
    by_order=groups,all_public_multisets_identical=True,
    all_independent_72_prefix_audits_pass=True,
    source_family_qualifies_all_frozen_gates=qualified,
    scientific_improvement_claim=False,
    registered_FIT_train_used=False,registered_FIT_validation_used=False,
    diagnostic_used=False,original_used=False,F3=False,
    optimizer_promotion=False,rows=rows)
 print(json.dumps(outcome,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 main()
