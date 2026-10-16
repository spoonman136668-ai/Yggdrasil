"""F62 pre-validation audit. Synthetic ONLY; never calls registered FIT source."""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,struct,sys

HERE=pathlib.Path(__file__).resolve().parent
receipt=json.loads((HERE/"frozen_train_receipt.json").read_text())
prereg=json.loads((HERE/"prereg.json").read_text())
def gitblob(p):
 b=p.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(HERE/"frozen_train_receipt.json")=="3ebca86bb230c9e6f4885f9c636d76f5d06e115f"
assert gitblob(HERE/"source_pilot.py")==receipt["source_blob"]=="7ed72deca5584d7c0b6562d74456fa7d4bee6712"
assert gitblob(HERE/"prereg.json")==receipt["prereg_blob"]=="f0fffb43fc1f344261c4802d917696aaf4035ce0"
weights=tuple(receipt["frozen_int8_weights"])
assert len(weights)==prereg["learned_policy"]["parameters_max"]==12
assert all(isinstance(w,int) and -127<=w<=127 for w in weights)
assert hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()==receipt["frozen_weights_sha256"]
assert receipt["train_cases"]==32 and receipt["counterfactual_examples"]==2085
assert receipt["heldout_validation_seeds"]==prereg["fit"]["within_fit_validation"]==[761008,761016]
assert receipt["validation_performed"] is False and receipt["retraining_permitted"] is False
assert receipt["scientific_improvement_qualified"] is False
spec=importlib.util.spec_from_file_location("y_f62_custody_source",HERE/"source_pilot.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
au=importlib.util.spec_from_file_location("y_f62_custody_audit",HERE/"audit_public.py")
a=importlib.util.module_from_spec(au);sys.modules[au.name]=a;au.loader.exec_module(a)
packing=m.codec()
summary=[]
for seed,family in ((-71,-2),(-72,-1)):
 tagged,q,_paths,regime=m._construct(seed,family)
 public=tuple(e[:3] for e in tagged)
 assert len(public)==72 and all(len(e)==3 for e in public)
 assert m.assert_F60_step_parity(public,packing)
 comparison=m.historical_controls_public(public,packing)
 for label,memory in comparison.items():
  m._valid_memory(memory,packing)
  assert len(memory)<=12,(label,len(memory))
 complete,acts,trace=m.learned_online(public,weights,packing,trace=True)
 without,acts_abl,trace_abl=m.learned_online(public,weights,packing,trace=True,allow_composition=False)
 assert a.verify(public,q,trace)["prefixes"]==72
 assert a.verify(public,q,trace_abl)["prefixes"]==72
 assert all(action!="merge" for action,_old,_drop in acts_abl)
 assert len(complete)<=12 and len(without)<=12
 summary.append(dict(regime=regime,case="UNREGISTERED_SYNTHETIC_ONLY",
   learned_correct=bool(packing.solve(complete,q)==q["answer"]),
   no_composition_correct=bool(packing.solve(without,q)==q["answer"]),
   retained_bytes=12*len(complete),ablation_retained_bytes=12*len(without),
   historical_controls=list(comparison)))
print(json.dumps(dict(schema="yggdrasil.f62.prevalidation-custody-audit.v1",
 status="SYNTHETIC_CUSTODY_ONLY",train_result_sha256=receipt["result_sha256"],
 frozen_weights_sha256=receipt["frozen_weights_sha256"],
 validation_consumed=False,fit_training_rerun=False,independent_F3=False,
 synthetic_cases=summary),sort_keys=True))
