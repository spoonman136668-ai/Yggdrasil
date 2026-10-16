"""Y-F62 first-use FIT TRAIN only. NEVER evaluates heldout FIT/DIAG/original.

Frozen method inherited from source-qualification SHA 002c7ae6.
"""
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
Q=P/"source_pilot.py"
b=Q.read_bytes()
blob=hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
assert blob=="7ed72deca5584d7c0b6562d74456fa7d4bee6712"
spec=importlib.util.spec_from_file_location("y_f62_once_train",Q)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
assert (m.TRAIN.start,m.TRAIN.stop)==(761000,761008)
assert (m.VALIDATE.start,m.VALIDATE.stop)==(761008,761016)
assert m.FAMILIES==(1460,1461,1462,1463)
weights,n=m.train_action_advantage(m.codec())
assert len(weights)==12 and all(isinstance(w,int) and -127<=w<=127 for w in weights)
result=dict(schema="yggdrasil.f62.once-fit-train-only.v1",source_blob=blob,
  qualified_source_head="002c7ae6ebd5c8d8fc6f6fcee6df3a97ff1de398",
  fit_train_seeds=[761000,761008],fit_train_families=list(m.FAMILIES),
  train_cases=32,counterfactual_examples=n,quantized_int8_weights=list(weights),
  weights_sha256=hashlib.sha256(bytes(w%256 for w in weights)).hexdigest(),
  heldout_fit_validation_executed=False,diagnostic_executed=False,
  original_executed=False,independent_F3=False,policy_promotion=False,
  qualified_scientific_improvement=False)
assert n>0
print(json.dumps(result,sort_keys=True))
