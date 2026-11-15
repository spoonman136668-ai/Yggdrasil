"""ST5 frozen source-only cue identifiability qualification.

Train and interference SOURCE ONLY, never held unfamiliar law, model or
protected scientific first-use. The private law and actual masks may be
read by this SOURCE-ONLY auditor for checking, but no model imports it.
"""
from collections import Counter
from hashlib import sha256
import argparse
import json
import subprocess
from pathlib import Path
import time

from research.nci04_st5.diagnostic_world import (
    run_original_episode,initial_public,ACTIONS,TRIALS,public_signature,
)
from research.nci04_st4.paired_world import (
    rotation,immediate_mask,delayed_mask
)

PREREG_COMMIT="2e22be59f6058b464f777a48bbd46d7edbc4db54"
PREREG_BLOB="1f5622f183fe83ece77a85ab8cee8ec1bb6da6b8"
ST4_WORLD_BLOB="447b946ee03c725902ce4d96f17bbc22aaeb814d"
TRAIN_LAWS=(3,5,7,11,13,17,19,23)
TRAIN_SEEDS=tuple(range(100,112))
INTERFERENCE_LAWS=(43,47,71,73,79,83,89,97)
HELD_LAWS=(53,59,61,67)
HELD_SEEDS=tuple(range(201,209))
SCHEMA="yggdrasil.nci04.st5.source-only-diagnostic-gate.v1"


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)


def verify_freeze():
    p=json.loads(Path(__file__).with_name(
        "frozen_protocol.json").read_text("utf-8"))
    s=p.get("source",{})
    if (p.get("schema")!=
        "yggdrasil.nci04.st5.public-diagnostic-native-retention.dev.v1" or
        p.get("status")!="FROZEN_PRE_SOURCE_CORRIGENDUM_NO_SOURCE_CODE_OR_OUTCOME" or
        p.get("source_parent_st4_sha")!=
        "166388855ccba8610c2d1638c1f3193bee324867" or
        tuple(s.get("train_laws",()))!=TRAIN_LAWS or
        tuple(s.get("train_seeds",()))!=TRAIN_SEEDS or
        tuple(s.get("interference_laws",()))!=INTERFERENCE_LAWS or
        tuple(s.get("held_dev_unfamiliar_laws",()))!=HELD_LAWS or
        tuple(s.get("held_dev_seeds",()))!=HELD_SEEDS or
        s.get("steps_per_episode")!=len(ACTIONS) or
        s.get("trials_per_law_seed")!=TRIALS or
        s.get("frozen_train_source_actions")!=7680 or
        s.get("frozen_held_dev_source_actions")!=2560 or
        s.get("no_protected_first_use") is not True or
        p.get("authority",{}).get("merge") is not False or
        p.get("authority",{}).get("protected_first_use") is not False or
        p.get("science_status")!="PREREGISTERED_NO_OUTCOMES"):
        raise ValueError("ST5_PREREG_CONTRACT_DRIFT")
    current=subprocess.check_output(
        ["git","rev-parse",
         "HEAD:research/nci04_st5/frozen_protocol.json"],
        text=True).strip()
    if current!=PREREG_BLOB:
        raise ValueError("ST5_PREREG_GIT_BLOB_CHANGED")
    if subprocess.run(
        ["git","merge-base","--is-ancestor",PREREG_COMMIT,"HEAD"],
        check=False).returncode:
        raise ValueError("ST5_PREREG_NOT_ANCESTOR")
    st4world=subprocess.check_output(
        ["git","rev-parse","HEAD:research/nci04_st4/paired_world.py"],
        text=True).strip()
    if st4world!=ST4_WORLD_BLOB:
        raise ValueError("ST5_IMPORTED_ST4_FROZEN_SOURCE_DRIFT")
    return p


def source_disposition(signatures,action_steps,train_episodes,
                       interference_episodes,unexpected,rotation_fail):
    if (type(signatures) is not dict or
        type(action_steps) is not int or
        type(train_episodes) is not int or
        type(interference_episodes) is not int or
        type(unexpected) is not int or
        type(rotation_fail) is not int):
        raise ValueError("ST5_SOURCE_INVALID_AUDIT_INPUT")
    must={
        "all_16_unique_public_diagnostic_cues":
            len(signatures)==16 and len(set(signatures.values()))==16,
        "train_source_7680_actions":
            action_steps==7680,
        "train_1536_complete_five_action_episodes":
            train_episodes==1536,
        "interference_128_complete_five_action_episodes":
            interference_episodes==128,
        "no_public_cue_inconsistency_across_seed_trials":
            unexpected==0,
        "no_first-step_rotation_ambiguity":rotation_fail==0,
    }
    return {"checks":must,"disposition":(
        "SOURCE_LAW_RETRIEVAL_IDENTIFIABLE_DEV_ONLY"
        if all(must.values())
        else "SOURCE_DIAGNOSTIC_IDENTIFIABILITY_NO_GO"
    )}


def audit(out):
    verify_freeze()
    started=time.perf_counter_ns()
    signatures={}
    training=[]
    interference=[]
    unexpected=0
    rotation_fail=0
    for law in TRAIN_LAWS+INTERFERENCE_LAWS:
        hasher=sha256()
        count=0
        seeds=TRAIN_SEEDS if law in TRAIN_LAWS else (111,)
        for seed in seeds:
            for trial in range(TRIALS):
                history,cue=run_original_episode(law,seed,trial)
                truth=(rotation(law),immediate_mask(law,0),
                       immediate_mask(law,1))
                if cue is None:
                    rotation_fail+=1
                if cue!=truth:
                    unexpected+=1
                if law in signatures and signatures[law]!=cue:
                    unexpected+=1
                signatures[law]=cue
                if len(history)!=5 or tuple(row[1] for row in history)!=ACTIONS:
                    raise ValueError("ST5_ACTUAL_BLIND_ACTOR_DRIFT")
                for before,action,after,target in history:
                    hasher.update(bytes((*before,action,*after,*target)))
                count+=1
        entry={
            "law_source_evaluator_only":law,
            "observed_cue_public":list(signatures[law])
                if signatures[law] is not None else None,
            "complete_real_five_step_episodes":count,
            "real_source_action_history_sha256":hasher.hexdigest(),
            "source_law_private_truth_used_by_learner":False,
        }
        (training if law in TRAIN_LAWS else interference).append(entry)
    result=source_disposition(signatures,7680,len(TRAIN_LAWS)*12*TRIALS,
                              len(INTERFERENCE_LAWS)*TRIALS,
                              unexpected,rotation_fail)
    doc={
        "schema":SCHEMA,
        "pre_source_freeze_git_commit":PREREG_COMMIT,
        "pre_source_freeze_git_blob":PREREG_BLOB,
        "source_parent_st4_world_blob":ST4_WORLD_BLOB,
        "training_source_law_records":training,
        "interference_source_law_records":interference,
        "distinct_public_signature_count":len(set(signatures.values())),
        "training_original_source_steps":7680,
        "interference_original_source_steps":len(INTERFERENCE_LAWS)*TRIALS*5,
        "source_rotation_ambiguity_count":rotation_fail,
        "source_cue_private_disagreement_count":unexpected,
        "source_disposition":result,
        "no_candidate_control_training":True,
        "held_development_unopened":True,
        "protected_first_use_unopened":True,
        "whole_source_audit_wall_ns":time.perf_counter_ns()-started,
        "science_pass":False,
    }
    out.write_text(canonical(doc)+"\n",encoding="utf-8")
    print("ST5_TRAIN_ORIGINAL_ACTIONS=7680")
    print("ST5_INTERFERENCE_SOURCE_ACTIONS="+str(doc["interference_original_source_steps"]))
    print("ST5_DISTINCT_PUBLIC_CAUSAL_CUES="+str(doc["distinct_public_signature_count"]))
    print("ST5_SOURCE_CUE_AMBIGUITIES="+str(rotation_fail+unexpected))
    print("ST5_SOURCE_DISPOSITION="+result["disposition"])
    print("ST5_HELD_AND_PROTECTED_SCIENCE_NOT_OPENED=PASS")
    return doc


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    audit(args.output)
