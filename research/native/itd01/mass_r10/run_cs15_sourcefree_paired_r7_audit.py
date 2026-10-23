#!/usr/bin/env python3
"""CS15 independent, source-free R7 paired retention audit.

Historical R7 study/gates are invoked unmodified and their FAILURE preserved.
The same original R7 A examples are evaluated before and after B-only
training. A separate adversarial A update is a sensitivity control.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
try:
    import resource  # POSIX-only; Windows runs exactly same science without RSS
except ImportError:
    resource=None
import subprocess
import sys
import time

NATIVE_DIR=Path(__file__).resolve().parents[1]/"r7"
sys.path.insert(0,str(NATIVE_DIR))
from native_cells import (
    Colony,LocalCell,PublicDevGenerator,_examples,_score,study,gates
)

FIRST="e743767fd31d3cc30437c41df73f595c5132c9b4"
ORIGINAL_NATIVE_GIT_BLOB="4c492a494ac5b25d5e9c49b98185be6a2c966b2f"
ORIGINAL_TEST_GIT_BLOB="5565929be0e91c679bfd3c6741d171b69d9a013f"
HISTORICAL=(17,31,47)
PROSPECTIVE_EXTRA=(59,83,107)
SEEDS=HISTORICAL+PROSPECTIVE_EXTRA
TRAIN_N=320
A_COHORT_N=160
SENSITIVITY_INVERTED_PASSES=3
def need(b,msg):
    if not b:raise RuntimeError(msg)
def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()
def hash_file(path):
    p=subprocess.run(["git","hash-object","--",str(path)],capture_output=True,
                     text=True,cwd=Path(__file__).resolve().parents[4],timeout=25)
    need(p.returncode==0,"ORIGINAL_R7_GIT_SOURCE_UNAVAILABLE")
    return p.stdout.strip()
def verify_source():
    target=NATIVE_DIR/"native_cells.py"
    original_test=NATIVE_DIR/"test_native_cells.py"
    need(hash_file(target)==ORIGINAL_NATIVE_GIT_BLOB,
         "FROZEN_R7_NATIVE_BLOB_ALTERED")
    need(hash_file(original_test)==ORIGINAL_TEST_GIT_BLOB,
         "FROZEN_R7_TEST_BLOB_ALTERED")
    need(Path(sys.modules[Colony.__module__].__file__).resolve()==target.resolve(),
         "R7_ACTUAL_COLONY_CLASS_WRONG_SOURCE")
    return {"original_native_Git_blob":ORIGINAL_NATIVE_GIT_BLOB,
            "original_frozen_R7_test_Git_blob":ORIGINAL_TEST_GIT_BLOB,
            "historical_R7_source_and_tests_not_modified":True}
def exact_cohorts(seed):
    g=PublicDevGenerator(seed+71)
    train_a=_examples(g,"A",TRAIN_N)
    valid_a=_examples(g,"A",A_COHORT_N)
    train_b=_examples(g,"B",TRAIN_N)
    retained_a=_examples(g,"A",A_COHORT_N)
    held_b=_examples(g,"B",A_COHORT_N)
    for name,rows,context,n in (
        ("train_A",train_a,"A",TRAIN_N),
        ("valid_A",valid_a,"A",A_COHORT_N),
        ("train_B",train_b,"B",TRAIN_N),
        ("retained_A",retained_a,"A",A_COHORT_N),
        ("held_B",held_b,"B",A_COHORT_N)):
        need(len(rows)==n and all(z[0]==context for z in rows),
             "R7_SOURCE_FREE_EXACT_PUBLIC_GENERATOR_GROUP_DRIFT:"+name)
    return train_a,valid_a,train_b,retained_a,held_b
def examples_digest(xs):
    return sha([{"context":ctx,"sensory_bits":list(sensors),"public_label":label}
                for ctx,sensors,label in xs])
def raw_pred_bits(colony,rows):
    return [bool(colony.predict(ctx,senses)) for ctx,senses,label in rows]
def model_context_state(model,context):
    return [asdict(c) for c in model.cells[context]]
def case_audit(seed):
    train_a,valid_a,train_b,retained_a,held_b=exact_cohorts(seed)
    model=Colony()
    for ctx,senses,outcome in train_a:
        model.predict(ctx,senses)
        model.learn_completed_public_feedback(ctx,senses,outcome,2)
    need(model.feedback_updates==TRAIN_N and
         all(x.updates==TRAIN_N for x in model.cells["A"]) and
         all(x.updates==0 for x in model.cells["B"]),
         "ORIGINAL_A_TRAINING_SOURCE_COUNTS_INVALID")
    prior_raw=model.checkpoint()
    prior_A_state=model_context_state(model,"A")
    prior_B_state=model_context_state(model,"B")
    before=Colony.restore(prior_raw)
    need(before.checkpoint()==prior_raw,
         "ORIGINAL_BEFORE_COLD_CHECKPOINT_NOT_BYTE_IDENTICAL")
    pre_valid_bits=raw_pred_bits(before,valid_a)
    pre_retained_bits=raw_pred_bits(before,retained_a)
    pre_valid=_score(before,valid_a)
    pre_retained=_score(before,retained_a)
    for ctx,senses,outcome in train_b:
        model.predict(ctx,senses)
        model.learn_completed_public_feedback(ctx,senses,outcome,2)
    need(model.feedback_updates==2*TRAIN_N and
         all(c.updates==TRAIN_N for c in model.cells["A"]) and
         all(c.updates==TRAIN_N for c in model.cells["B"]) and
         model.neighbor_messages==8*2*TRAIN_N,
         "ORIGINAL_B_TRAINING_FEEDBACK_COUNTS_INVALID")
    after_raw=model.checkpoint()
    after=Colony.restore(after_raw)
    need(after.checkpoint()==after_raw and prior_raw!=after_raw,
         "ORIGINAL_AFTER_COLD_CHECKPOINT_NOT_NEW_OR_IDENTICAL")
    post_valid_bits=raw_pred_bits(after,valid_a)
    post_retained_bits=raw_pred_bits(after,retained_a)
    post_valid=_score(after,valid_a)
    post_retained=_score(after,retained_a)
    post_B=_score(after,held_b)
    need(prior_A_state==model_context_state(after,"A"),
         "ACTUAL_ORIGINAL_A_STATE_CHANGED_DURING_B_ONLY_UPDATES")
    need(prior_B_state!=model_context_state(after,"B"),
         "NEGATIVE_CONTROL_B_CELLS_NOT_TRAINED")
    need(pre_valid_bits==post_valid_bits and
         pre_retained_bits==post_retained_bits,
         "PAIRED_EXACT_SAME_A_EXAMPLE_PREDICTIONS_CHANGED")
    need(pre_valid==post_valid and pre_retained==post_retained,
         "PAIRED_SAME_EXAMPLES_CHANGED_SCORE")
    unpaired=pre_valid-post_retained
    within_valid=pre_valid-post_valid
    within_retained=pre_retained-post_retained
    cross_post=post_valid-post_retained
    need(abs(unpaired-(within_valid+cross_post))<1e-14,
         "UNPAIRED_ACCURACY_LOSS_DECOMPOSITION_INVALID")
    historical=study(seed)
    need(pre_valid==historical["a_before_b"] and
         post_retained==historical["a_after_b"] and
         post_B==historical["b_after_training"] and
         after_raw.hex() and hashlib.sha256(after_raw).hexdigest()==
         historical["checkpoint_sha256"],
         "ORIGINAL_HISTORICAL_STUDY_SCORE_OR_CHECKPOINT_MISMATCH")
    need(model_context_state(before,"A")==prior_A_state,
         "FROZEN_ORIGINAL_MODEL_BEFORE_A_STATE_UNEXPECTED")
    # Positive-sensitivity adversarial ablation on a SEPARATE restored copy.
    # Never changes original prior/after, original R7, source histories or DEV.
    corruption=Colony.restore(prior_raw)
    for _ in range(SENSITIVITY_INVERTED_PASSES):
        for ctx,senses,label in train_a:
            corruption.learn_completed_public_feedback(ctx,senses,not label,2)
    changed_valid=sum(a!=b for a,b in zip(
        pre_valid_bits,raw_pred_bits(corruption,valid_a)))
    changed_retained=sum(a!=b for a,b in zip(
        pre_retained_bits,raw_pred_bits(corruption,retained_a)))
    need(corruption.checkpoint()!=prior_raw and
         model_context_state(corruption,"A")!=prior_A_state,
         "ADVERSARIAL_A_NEGATIVE_LABEL_SENSITIVITY_STATE_UNCHANGED")
    return {
        "frozen_public_R7_seed":seed,
        "original_generator": "unmodified_PublicDevGenerator(seed+71)",
        "frozen_original_public_cohort_SHA256":{
            "train_A_320":examples_digest(train_a),
            "valid_A_160":examples_digest(valid_a),
            "train_B_320":examples_digest(train_b),
            "retained_A_160":examples_digest(retained_a),
            "held_B_160":examples_digest(held_b)},
        "original_source_free_train_A_updates":TRAIN_N,
        "original_source_free_train_B_updates":TRAIN_N,
        "original_A_before_B_checkpoint_SHA256":hashlib.sha256(prior_raw).hexdigest(),
        "original_A_after_B_checkpoint_SHA256":hashlib.sha256(after_raw).hexdigest(),
        "original_full_checkpoint_changed_after_B_training":True,
        "original_A_four_local_cells_byte_exact_after_B":True,
        "original_B_four_local_cells_unchanged_after_B":False,
        "original_public_A_valid_160_accuracy_before_B":pre_valid,
        "original_public_A_valid_160_accuracy_after_B":post_valid,
        "original_public_A_retained_160_accuracy_before_B":pre_retained,
        "original_public_A_retained_160_accuracy_after_B":post_retained,
        "original_public_B_held_160_accuracy_after_B":post_B,
        "PAIRED_same_valid_A_loss":within_valid,
        "PAIRED_same_retained_A_loss":within_retained,
        "ORIGINAL_UNPAIRED_different_valid_A_to_retained_A_loss":unpaired,
        "UNPAIRED_ONLY_held_sample_accuracy_gap_post_B":cross_post,
        "original_unpaired_loss_decomposition_exact":True,
        "identical_A_prediction_counts":{
            "valid_A_160":sum(a==b for a,b in zip(pre_valid_bits,post_valid_bits)),
            "retained_A_160":sum(a==b for a,b in zip(pre_retained_bits,post_retained_bits))},
        "adversarial_inverted_actual_A_feedback_PASSES":SENSITIVITY_INVERTED_PASSES,
        "adversarial_inverted_A_valid_pred_changes":changed_valid,
        "adversarial_inverted_A_retained_pred_changes":changed_retained,
        "original_R7_study_exact_reproduced":True,
        "original_unchanged_study_report":historical,
    }
def audit():
    verification=verify_source()
    history=[study(seed) for seed in HISTORICAL]
    original_pass=gates(history)
    need(original_pass is False,"HISTORICAL_FROZEN_R7_NEGATIVE_NOT_PRESERVED")
    need(history[1]["a_before_b"]==.93125 and
         history[1]["a_after_b"]==.86875 and
         abs((history[1]["a_before_b"]-history[1]["a_after_b"])-.0625)<1e-14,
         "HISTORICAL_ORIGINAL_SEED31_FROZEN_NEGATIVE_CHANGED")
    cases=[case_audit(seed) for seed in SEEDS]
    need(len(cases)==6 and
         all(x["PAIRED_same_valid_A_loss"]==0 and
             x["PAIRED_same_retained_A_loss"]==0 and
             x["identical_A_prediction_counts"]["valid_A_160"]==160 and
             x["identical_A_prediction_counts"]["retained_A_160"]==160
             for x in cases),
         "PAIRED_SOURCE_FREE_RETENTION_MEASUREMENT_DIVERGED")
    need(sum(x["adversarial_inverted_A_valid_pred_changes"]+
             x["adversarial_inverted_A_retained_pred_changes"] for x in cases)>0,
         "ADVERSARIAL_A_SENSITIVITY_CONTROL_DID_NOT_CHANGE_ANY_PREDICTION")
    return {
        "schema":"mass.cs15.frozen_R7_paired_retention_audit.v1",
        "frozen_FIRST_only_prereg_SHA":FIRST,
        "original_native_git_identity":verification,
        "this_is_source_free_original_PUBLIC_dev_only":True,
        "original_R7_study_gates_unchanged":True,
        "frozen_original_R7_historical_gates_pass":original_pass,
        "original_R7_full_integration_promotion_gate":"FAIL_UNCHANGED",
        "historical_original_seed_31_unpaired_loss":.0625,
        "paired_same_examples_all_6_seeds_exact_score_loss":0,
        "paired_same_examples_all_6_seeds_exact_prediction_changes":0,
        "original_public_DEV_seeds_list":list(SEEDS),
        "historical_original_three_R7_study_reports":history,
        "all_original_source_free_public_paired_case_results":cases,
        "adversarial_A_label_inversion_any_prediction_change":True,
        "independent_sealed_original_source_first_use":False,
        "native_new_architecture_or_source_research_advancement":False,
        "frozen_R7_acceptance_threshold_waived":False,
        "CS14_production_or_G29_promoted":False,
        "ELG01_language_experiment_executed":False,
        "disposition":"PUBLIC_CS15_PAIRED_R7_MEASUREMENT_CONFOUND_CONFIRMED"
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    rec={"schema":"mass.cs15.frozen_R7_paired_retention_audit.v1",
         "frozen_FIRST_only_prereg_SHA":FIRST,
         "disposition":"PUBLIC_CS15_INVALID"}
    begin=time.process_time_ns()
    try:
        rec=audit()
    except Exception as e:
        rec["first_failure"]=type(e).__name__+":"+str(e)[:850]
    finally:
        (out/"cs15-sourcefree-frozen-R7-paired-audit.json").write_text(
            json.dumps(rec,sort_keys=True,indent=2,allow_nan=False)+"\n")
        metadata={
            "sourcefree_audit_logical_receipt_SHA256":sha(rec),
            "elapsed_process_CPU_ns":time.process_time_ns()-begin,
            "original_native_source_files_mutated":False,
            "frozen_historical_R7_test_still_a_promotion_blocker":True,
        }
        if resource is not None:
            metadata["peak_process_RSS_KiB_linux_only"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        else:
            metadata["peak_process_RSS_KiB_linux_only"]="NOT_MEASURED_ON_WINDOWS"
        (out/"cs15-process-resource-metadata.json").write_text(json.dumps(metadata,sort_keys=True,indent=2)+"\n")
    print("CS15_DISPOSITION="+rec["disposition"],flush=True)
    print("CS15_LOGICAL_RECEIPT_SHA256="+sha(rec),flush=True)
    return 0 if rec["disposition"]=="PUBLIC_CS15_PAIRED_R7_MEASUREMENT_CONFOUND_CONFIRMED" else 2
if __name__=="__main__":
    raise SystemExit(main())
