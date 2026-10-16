"""F66B offline-only fit from authenticated source-first-use GitHub artifact.

Uses exactly frozen opportunity-cost teacher. No source generator is invoked.
FIT VALIDATE, DIAG, and ORIGINAL never accessed. No scientific promotion.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
EXPECTED_ROWS_SHA="4bd1b7d87b6f63027daf34dbcf61aa028768b0c3a1cc745df4763b5d09df90bc"
EXPECTED_BLOBS={
 "prereg.json":"fc3283f28ab307b6834c93d530fffce98ad7c0de",
 "prereg-opportunity-cost-amendment.json":"3502d23f503cb0fdc798b2ac7db3f5cdb09c254d",
 "two_head_continuation.py":"fa08d72d79380a82814c86482e98b206b69b4d4a",
 "dense_opportunity_teacher.py":"7b41ebeaf51f879e6426206923e8e0ad1cb9897c"}
def sha(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
for name,expected in EXPECTED_BLOBS.items():
 assert sha(HERE/name)==expected,("F66B_IMMUTABLE_SOURCE_DRIFT",name)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 return module
teacher=load("f66b_frozen_authenticated_teacher",HERE/"dense_opportunity_teacher.py")
prereg=json.loads((HERE/"prereg.json").read_text())
assert prereg["cohorts"]["fit_train_seeds"]==[831000,831008]
assert prereg["cohorts"]["fit_validate_seeds"]==[831008,831016]
assert prereg["cohorts"]["fit_families"]==[1600,1601,1602,1603]
def fit(archived):
 raw=archived.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==EXPECTED_ROWS_SHA,"F66B_FIT_TRAIN_ARCHIVE_DRIFT"
 rows=[json.loads(line) for line in raw.decode("utf-8").splitlines()]
 assert len(rows)==32
 ids={(int(r["seed"]),int(r["family"])) for r in rows}
 expected={(seed,family) for seed in range(831000,831008) for family in range(1600,1604)}
 assert ids==expected,"REGISTERED_TRAIN_IDS_MISMATCH"
 publics=[tuple(tuple(event) for event in row["public_events"]) for row in rows]
 assert all(len(case)==72 and all(len(edge)==3 for edge in case) for case in publics)
 # Only public_events projected; post-retention question/answer is never
 # passed to teacher.fit() or runtime policy.
 weights,counts=teacher.fit(publics)
 assert weights is not None and counts["positive_merge_labels"]>0 and counts["negative_merge_labels"]>0
 assert len(weights)==20
 return dict(schema="yggdrasil.f66b.authentic-frozen-public-opportunity-fit.v1",
   stage="MODEL_FROZEN_TRAIN_ONLY",qualified_synthetic_method_run=38890494602,
   qualified_source_run=38890570573,train_first_use_run=38890771643,
   train_first_use_artifact=12041976206,train_rows_sha256=EXPECTED_ROWS_SHA,
   pinned_git_blobs=EXPECTED_BLOBS,fit_cases=32,fit_counts=counts,
   frozen_int8_weights=list(weights),weights_sha256=hashlib.sha256(bytes(w%256 for w in weights)).hexdigest(),
   training_on_future_public_only=True,training_on_future_question=False,
   online_future_data_used=False,model_params=20,
   train_cohort_rerun=False,fit_validation_executed=False,diagnostic_executed=False,
   original_executed=False,F3=False,accepted_ref_mutation=False,
   scientific_improvement_qualified=False,optimizer_promotion=False)
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--archived-train-rows",type=pathlib.Path,required=True)
 args=parser.parse_args()
 print(json.dumps(fit(args.archived_train_rows),sort_keys=True))
