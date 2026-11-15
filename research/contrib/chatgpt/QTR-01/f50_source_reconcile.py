#!/usr/bin/env python3
"""F50 source-only checkpoint reconciliation after bounded RESOURCE_STOP.

Reuse is by verified, exact role-dependent model semantics and source-data
identity, NOT by falsely relabeling a checkpoint's original commit SHA. No
F50 DEV target law, real target outcome, main promotion or accepted-weight
mutation is permitted. Copies retain their authentic original metadata.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
from time import process_time

import numpy as np

import f50_conventional_controls as controls
import f50_source_fit as sourcefit
import f50_target_public_controls as target
import f50_worlds as world

SCHEMA="yggdrasil.qtr01.f50.role-key-reuse-source-only.v1"
OLD_SOURCE="0f62f98e1a8778e9d7afd8f229d8f5635ec7d3ee"
NEW_SOURCE="def7e7a88517b9afadc6854bd7847d7e4a5d42e6"
OLD_RUN=43767024842
NEW_RUN=43769382063
OLD_ARTIFACT=14182614963
NEW_ARTIFACT=14184063472
OLD_RECEIPT_SHA256="975fd99afdc46cd8b4c64f5fb197eadec85f454b0e89105e158ca20fd1527c92"
NEW_RECEIPT_SHA256="f89d3163a7ac8af781387355f93135566a4b887711924e0fcac9e2cf86d2749d"
SOURCE_DATA_SHA256="5ffae27d69f20188f9fe987b2139cf6a8ca17be74875da269e4caaea8c9ce369"
MLP_SHA256="33e57b5fe4eea03f3b1778589776a9219dd1f9f51291577e54af0ad971e952e8"
GRU_SHA256="334c562ba6c3b48f1ea8233e9a7efcb787b37fcaf38dd3d06c3d1bf4f5395ecf"
MAX_LOGISTIC_CPU_SECONDS=600
SOURCE_DIR="research/contrib/chatgpt/QTR-01"


class ReconcileRejected(sourcefit.SourceFitRejected):
    pass


def git_bytes(commit,path):
    if not re.fullmatch(r"[0-9a-f]{40}",commit):
        raise ReconcileRejected("F50_REUSE_INVALID_COMMIT")
    return subprocess.check_output(["git","show",f"{commit}:{path}"])


def verify_role_semantics():
    """Mathematics and all source inputs byte-identical; only logistic changed."""
    checked={}
    for name in ("f50_worlds.py","f50_public_corpus.py",
                 "f50_source_fit.py","f50_prereg.json"):
        path=f"{SOURCE_DIR}/{name}"
        legacy=git_bytes(OLD_SOURCE,path)
        now=Path(path).read_bytes()
        if legacy!=now:
            raise ReconcileRejected("F50_SOURCE_SEMANTIC_INPUT_DRIFT:"+name)
        checked[name]=sha256(now).hexdigest()
    name=f"{SOURCE_DIR}/f50_conventional_controls.py"
    legacy=git_bytes(OLD_SOURCE,name)
    now=Path(name).read_bytes()
    boundary=b"def logistic_source_rows"
    tail=b"def pretraining_dataset"
    if (legacy.count(boundary)!=1 or now.count(boundary)!=1
        or legacy.count(tail)!=1 or now.count(tail)!=1):
        raise ReconcileRejected("F50_ROLE_EQUIVALENCE_BOUNDARY_MISSING")
    neural_old=legacy.split(boundary,1)[0]
    neural_new=now.split(boundary,1)[0]
    tail_old=tail+legacy.split(tail,1)[1]
    tail_new=tail+now.split(tail,1)[1]
    if neural_old!=neural_new or tail_old!=tail_new:
        raise ReconcileRejected("F50_NEURAL_TRAIN_ROLE_CACHE_INVALID")
    checked["neural_source_math_sha256"]=sha256(neural_new+tail_new).hexdigest()
    checked["current_logistic_source_sha256"]=sha256(
        now.split(boundary,1)[1].split(tail,1)[0]).hexdigest()
    checked["source_program_changed_for_logistic"]=True
    return checked


def verify_prior_receipt(path,sha,expected_source,expected_status,expected_kinds):
    file=Path(path)/"f50-source-fit-receipt.json"
    raw=file.read_bytes()
    if sha256(raw).hexdigest()!=sha:
        raise ReconcileRejected("F50_SOURCE_RECEIPT_BYTES_TAMPERED")
    j=json.loads(raw)
    if (j.get("schema")!=sourcefit.SCHEMA
        or j.get("source_commit")!=expected_source
        or j.get("frozen_prereg_blob")!=world.PREREG_BLOB
        or j.get("status")!=expected_status
        or j.get("target_outcomes")!=0
        or j.get("scientific_pass") is not False
        or j.get("size")!=4096
        or j.get("source",{}).get("source_data_sha256")!=SOURCE_DATA_SHA256
        or j["source"].get("fit_laws")!=3276
        or j["source"].get("validation_laws")!=820
        or [x["kind"] for x in j["models"]]!=expected_kinds):
        raise ReconcileRejected("F50_PRIOR_SOURCE_RECEIPT_SCOPE_REJECTED")
    for m in j["models"]:
        f=Path(path)/m["checkpoint"]
        if (not f.is_file() or f.stat().st_size!=m["bytes"]
            or sha256(f.read_bytes()).hexdigest()!=m["sha256"]
            or m["cold_restored"] is not True
            or m["fit"]["source_training_complete"] is not True):
            raise ReconcileRejected("F50_PRIOR_MODEL_BYTES_OR_FIT_INVALID")
    return j


def selected_model(path,receipt,kind,sha,source_sha):
    entries=[x for x in receipt["models"] if x["kind"]==kind]
    if len(entries)!=1 or entries[0]["sha256"]!=sha:
        raise ReconcileRejected("F50_SOURCE_ROLE_CHECKPOINT_NOT_FOUND")
    entry=entries[0]
    model,meta=sourcefit.load_checkpoint(
        Path(path)/entry["checkpoint"],sha,source_sha,
        expected_kind=kind,expected_size=4096)
    if (meta["source_data_sha256"]!=SOURCE_DATA_SHA256
        or meta["model_training"]["source_training_complete"] is not True):
        raise ReconcileRejected("F50_SOURCE_CHECKPOINT_ROLE_MISMATCH")
    return model,meta,entry


def synthetic_public_cold_test(model,meta,kind,digest):
    """A fixture outcome, NOT a generated target-law/DEV observation."""
    arm=target.TargetPublicArm(4096,4013,kind,model,meta,digest)
    episode=arm.pool[0]
    before=arm.probability(episode)
    if len(before)!=3 or not all(np.isfinite(x) and 0<=x<=1 for x in before):
        raise ReconcileRejected("F50_SOURCE_TARGET_UNKNOWN_PREDICTION_INVALID")
    index,public_trajectory=arm.select()
    if public_trajectory!=arm.pool[index]:
        raise ReconcileRejected("F50_PUBLIC_ACTION_CUSTODY")
    arm.observe(index,(1,0,1))  # hard-coded synthetic feedback, no target law
    packet=arm.cold_checkpoint()
    restored=target.TargetPublicArm.restore(packet,model,meta,digest)
    if (restored.cold_checkpoint()!=packet
        or restored.probability(episode)!=arm.probability(episode)
        or arm.observed_bits!=3 or arm.target_graph_available):
        raise ReconcileRejected("F50_ACTUAL_CHECKPOINT_COLD_PARITY_FAILED")
    corrupted=packet[:-1]+bytes((packet[-1]^1,))
    try:
        target.TargetPublicArm.restore(corrupted,model,meta,digest)
    except target.TargetParityRejected:
        pass
    else:
        raise ReconcileRejected("F50_ACTUAL_CHECKPOINT_TAMPER_ACCEPTED")
    return {"source_model_sha256":digest,"public_synthetic_bits":3,
            "cold_bit_exact":True,"corruption_rejected":True,
            "target_ast_seen":False,"dev_target_outcomes":0,
            "model_weights_updated":False}


def reconcile(old_dir,new_dir,output,source_sha,*,max_logistic_cpu=600):
    world.freeze()
    if (not re.fullmatch(r"[0-9a-f]{40}",source_sha)
        or type(max_logistic_cpu) is not int
        or not 1<=max_logistic_cpu<=MAX_LOGISTIC_CPU_SECONDS):
        raise ReconcileRejected("F50_REUSE_UNQUALIFIED_PARAMS")
    out=Path(output)
    if out.exists() and any(out.iterdir()):
        raise ReconcileRejected("F50_REUSE_REFUSE_OVERWRITE")
    out.mkdir(parents=True,exist_ok=True)
    keys=verify_role_semantics()
    legacy=verify_prior_receipt(old_dir,OLD_RECEIPT_SHA256,OLD_SOURCE,
            "ALL_THREE_SOURCE_ONLY_TRAINED",list(controls.KINDS))
    partial=verify_prior_receipt(new_dir,NEW_RECEIPT_SHA256,NEW_SOURCE,
            "RESOURCE_STOP",[controls.KINDS[0]])
    if (partial.get("stopped_at")!="law_conditioned_set_mlp"
        or partial.get("resource_receipt",{}).get("status")!="RESOURCE_STOP"
        or partial["resource_receipt"].get("source_training_complete") is not False):
        raise ReconcileRejected("F50_RESOURCE_STOP_HISTORY_MISMATCH")
    start=process_time()
    model_map={}
    manifest={"schema":SCHEMA,"candidate_source_sha":source_sha,
      "frozen_prereg_blob":world.PREREG_BLOB,"source_data_sha256":SOURCE_DATA_SHA256,
      "semantic_role_keys":keys,"v1_artifact_id":OLD_ARTIFACT,"v1_run_id":OLD_RUN,
      "v2_artifact_id":NEW_ARTIFACT,"v2_run_id":NEW_RUN,
      "v1_status":legacy["status"],"v2_status":partial["status"],
      "v2_discarded_incomplete_mlp_cpu":partial["resource_receipt"]["cpu_seconds"],
      "models":[],"target_outcomes":0,"scientific_pass":False,
      "protected_first_use":False,"status":"INCOMPLETE"}

    def append_prior(kind,folder,j,expected_sha,expected_source):
        model,meta,entry=selected_model(folder,j,kind,expected_sha,expected_source)
        dst=out/entry["checkpoint"]
        if dst.exists():
            raise ReconcileRejected("F50_DUPLICATE_MODEL_NAME")
        shutil.copyfile(Path(folder)/entry["checkpoint"],dst)
        if sha256(dst.read_bytes()).hexdigest()!=expected_sha:
            raise ReconcileRejected("F50_REUSED_COLD_BYTES_CHANGED")
        cold=synthetic_public_cold_test(model,meta,kind,expected_sha)
        manifest["models"].append({"kind":kind,"checkpoint":dst.name,
            "sha256":expected_sha,"original_source_sha":expected_source,
            "source_fit":entry["fit"],"synthetic_cold":cold,
            "cache_role":"byte-identical-neural-model-source-math-and-FIT-data"})
        model_map[kind]=(model,meta)
    append_prior(controls.KINDS[0],new_dir,partial,GRU_SHA256,NEW_SOURCE)
    append_prior(controls.KINDS[1],old_dir,legacy,MLP_SHA256,OLD_SOURCE)

    fit=controls.pretraining_dataset(4096)
    validation=controls.pretraining_dataset(4096,validation=True)
    source_receipt=controls.dataset_receipt(4096,fit,validation)
    if source_receipt["source_data_sha256"]!=SOURCE_DATA_SHA256:
        raise ReconcileRejected("F50_SOURCE_DATA_DIGEST_CHANGED")
    fit_ids=tuple(sorted(fit))
    val_ids=tuple(sorted(validation))
    m,trained=controls.logistic_fit_source(fit,fit_ids,validation,val_ids,
                      budget_seconds=max_logistic_cpu)
    if m is None or trained.get("status")!="TRAINED_SOURCE_ONLY":
        manifest.update(status="RESOURCE_STOP",stopped_at=controls.KINDS[2],
                        resource_receipt=trained,
                        total_reconciliation_cpu_seconds=process_time()-start)
    else:
        if (trained.get("target_graph_unknown_compatible") is not True
            or trained.get("validation_target_graph_hidden") is not True):
            raise ReconcileRejected("F50_LOGISTIC_TARGET_UNKNOWN_MISMATCH")
        name=f"f50-source-4096-{controls.KINDS[2]}.npz"
        digest,bytes_count=sourcefit.write_checkpoint(
            out/name,controls.KINDS[2],4096,m,source_sha,source_receipt,trained)
        fitted,meta=sourcefit.load_checkpoint(out/name,digest,source_sha,
                  expected_kind=controls.KINDS[2],expected_size=4096)
        cold=synthetic_public_cold_test(fitted,meta,controls.KINDS[2],digest)
        manifest["models"].append({"kind":controls.KINDS[2],
            "checkpoint":name,"sha256":digest,"bytes":bytes_count,
            "original_source_sha":source_sha,"source_fit":trained,
            "synthetic_cold":cold,"cache_role":"fresh-corrected-unknown-target-graph-fit"})
        manifest["status"]="ALL_THREE_SOURCE_CONTROLS_ROLE_KEY_VERIFIED"
        manifest["total_reconciliation_cpu_seconds"]=process_time()-start
    # This is the COMPLETE cumulative cost including aborted source fits.
    manifest["historical_v1_total_cpu_seconds"]=legacy["total_cpu_seconds"]
    manifest["historical_v2_spent_cpu_seconds_estimate"]=(
      partial["preprocessing_cpu_seconds"]+
      partial["models"][0]["fit"]["cpu_seconds"]+
      partial["resource_receipt"]["cpu_seconds"])
    manifest["cumulative_program_cpu_seconds_lower_bound"]=(
      manifest["historical_v1_total_cpu_seconds"]+
      manifest["historical_v2_spent_cpu_seconds_estimate"]+
      manifest["total_reconciliation_cpu_seconds"])
    (out/"f50-source-reconciliation-receipt.json").write_text(
      json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-only",action="store_true")
    p.add_argument("--legacy",type=Path,required=True)
    p.add_argument("--corrected-partial",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--candidate-sha",required=True)
    p.add_argument("--logistic-cpu-budget",type=int,default=600)
    a=p.parse_args()
    if not a.source_only:
        p.error("F50_TARGET_DEVELOPMENT_NOT_PERMITTED")
    result=reconcile(a.legacy,a.corrected_partial,a.output,a.candidate_sha,
                     max_logistic_cpu=a.logistic_cpu_budget)
    print("F50_ROLE_KEY_REUSE_STATUS="+result["status"],flush=True)
    print("F50_ROLE_KEY_SOURCE_CONTROL_COUNT="+str(len(result["models"])),flush=True)
    print("F50_DEV_TARGET_OUTCOMES=0",flush=True)


if __name__=="__main__":
    main()
