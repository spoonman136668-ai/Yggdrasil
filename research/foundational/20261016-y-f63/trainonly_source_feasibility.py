"""F63 train-only public-source feasibility check, preserving heldout identities."""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
H=pathlib.Path(__file__).resolve().parent
def sha(p):
 b=p.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert sha(H/"prereg.json")=="ecd9f177c9a47fd42c50e6e2502f938082028513"
assert sha(H/"learn_reliability.py")=="4eef37159bb96e90cf7f89c4dc0ed91b6d9d23c5"
s=importlib.util.spec_from_file_location("f63_l",H/"learn_reliability.py")
l=importlib.util.module_from_spec(s);sys.modules[s.name]=l;s.loader.exec_module(l)
f62=l.f62; packing=l.packing
p=json.loads((H/"prereg.json").read_text())
assert p["frozen_cohorts"]["fit_train_seeds"]==[781000,781008]
assert p["frozen_cohorts"]["fit_validate_seeds"]==[781008,781016]
assert p["frozen_cohorts"]["fit_families"]==[1500,1501,1502,1503]
rows=[]
for seed in range(781000,781008):
 for family in range(1500,1504):
  # New identities have not been admitted to F62's closed source().
  # Its underlying generator is reused as an explicit F63 SOURCE ADAPTER;
  # this does not establish distinct arrival/relationship structure.
  tagged,q,paths,regime=f62._construct(seed,family)
  public=tuple(x[:3] for x in tagged)
  controls=f62.historical_controls_public(public,packing)
  witness=int(packing.solve(controls["offline_full_public_graph_extra_work_noncompetitive"],q)==q["answer"])
  fixed=int(packing.solve(controls["F60_exact_source_fixed_online"],q)==q["answer"])
  rows.append(dict(seed=seed,family=family,regime=regime,witness=witness,fixed=fixed))
assert len(rows)==32
v=dict(schema="yggdrasil.f63.fit-train-source-adapter-feasibility.v1",
 stage="FIT_TRAIN_SOURCE_FEASIBILITY_ONLY",source_adapter="F62_underlying_construct_EXPLICIT_NOT_NEW_STRUCTURE",
 source_novelty_qualified=False,train_cases=32,
 witness_correct=sum(x["witness"] for x in rows),fixed_correct=sum(x["fixed"] for x in rows),
 witness_threshold=p["gates"]["public_extra_work_witness_accuracy_min"],
 fixed_threshold=p["gates"]["source_feasibility_fair_fixed_min"],
 witness_pass=sum(x["witness"] for x in rows)/32>=p["gates"]["public_extra_work_witness_accuracy_min"],
 fixed_pass=sum(x["fixed"] for x in rows)/32>=p["gates"]["source_feasibility_fair_fixed_min"],
 source_feasibility_qualified=False,validation_executed=False,diagnostic_executed=False,
 original_executed=False,independent_F3=False,rows=rows)
print(json.dumps(v,sort_keys=True))
