"""F67B frozen signed-int8 learning from authentic archived FIT TRAIN only.

Never re-invokes protected source or reads postretention question/answer.
All future-public teacher signals are confined to this offline TRAIN step.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
TRAIN_SHA256="5c01043f1691842b795cde77ce008b5d1bc46750dae4f2224c4e601cab6a7bb9"
PINNED={
 "prereg-positive-admission.json":"e923b32001eb22236c9d55e9d6ab00abe5cc7214",
 "fit_admission_synthetic.py":"a6b4251354e8e79b744449ad6e08b7179bb9e6ab",
 "durable_policy.py":"21f2f3fc90a3d00d09029f39e4958e09a33908cc"}
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
for name,sha in PINNED.items():
 assert blob(HERE/name)==sha,(name,"F67B_SOURCE_IDENTITY_DRIFT")
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(s);sys.modules[name]=mod;s.loader.exec_module(mod);return mod
FIT=load("f67b_frozen_positive_admission_mentor",HERE/"fit_admission_synthetic.py")
prereg=json.loads((HERE/"prereg-positive-admission.json").read_text())
c=prereg["prospective"]
assert c["fit_train"]==[861000,861008] and c["fit_validate"]==[861008,861016]
assert c["families"]==[1660,1661,1662,1663]
def run(path):
 raw=path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==TRAIN_SHA256,"ARCHIVED_FIT_ROWS_IDENTITY_DRIFT"
 rows=[json.loads(line) for line in raw.decode("utf-8").splitlines()]
 assert len(rows)==32
 assert {(r["seed"],r["family"]) for r in rows}=={(seed,family) for seed in range(861000,861008) for family in range(1660,1664)}
 publics=[tuple(tuple(e) for e in row["public_events"]) for row in rows]
 assert all(len(x)==72 and all(len(e)==3 for e in x) for x in publics)
 # Never pass future question, answer, hidden tag or frozen control scores.
 weights,counts=FIT.fit(publics)
 assert len(weights)==16 and counts["teacher_merges"]>0 and counts["examples"]>0
 return dict(schema="yggdrasil.f67b.authentic-frozen-positive-admission-fit.v1",
    stage="FIT_TRAIN_MODEL_FROZEN",source_qualified_head="51c3edb30668810d031c61277132f46fddf61528",
    prereg_blob=PINNED["prereg-positive-admission.json"],frozen_source_blob=PINNED["durable_policy.py"],
    frozen_method_blob=PINNED["fit_admission_synthetic.py"],
    synthetic_method_qualified_run=38893778756,source_first_use_run=38894210922,
    source_first_use_artifact=12043815121,source_train_rows_sha256=TRAIN_SHA256,
    training_cases=len(rows),teacher_examples=counts["examples"],
    teacher_merges=counts["teacher_merges"],frozen_weights=list(weights),
    weights_sha256=hashlib.sha256(bytes(w%256 for w in weights)).hexdigest(),
    offline_future_public_training_only=True,online_future_question=False,
    train_rows_rerun=False,heldout_executed=False,diagnostics_executed=False,
    originals_executed=False,F3=False,policy_promotion=False,scientific_positive=False)
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--fit-evidence",type=pathlib.Path,required=True)
 args=parser.parse_args()
 print(json.dumps(run(args.fit_evidence),sort_keys=True))
