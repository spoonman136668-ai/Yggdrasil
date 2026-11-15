"""ST7 source-only original action identifiability audit; NO held first-use.

The ONLY file in ST7 source-only path that may access true privately
sampled quadratic coefficients. Models cannot import this file.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from research.nci04_st7.private_world import (
    original_episode,private_params,private_coefficient_rows,quadratic,
    public_byte,rol,ACTIONS,TRIALS,features
)

PREREG_COMMIT="b03c8a7978359077ab62d746bb8142c42925bdf1"
PREREG_BLOB="75366ef5b1acf5668433fb3a363a610ff7104111"
SOURCE_BLOB="ac39c7a5a7a0c3119e5d91872017deee84ecfef4"
TRAIN=(3,5,7,11,13,17,19,23)
SEEDS=tuple(range(100,112))
HELD=(29,31,37,41)
SCHEMA="yggdrasil.nci04.st7.private-source-only-stage0.v1"


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)


def verify_prereg():
    d=json.loads(Path(__file__).with_name(
        "frozen_protocol.json").read_text("utf-8"))
    s=d["source"]
    if (d.get("schema")!="yggdrasil.nci04.st7.unknown-quadratic-boolean-causal-law.dev.v1" or
        d.get("status")!="PREREGISTERED_BEFORE_SOURCE_CODE_OR_ANY_ST7_OUTCOME" or
        tuple(s["train_laws"])!=TRAIN or tuple(s["train_seeds"])!=SEEDS or
        tuple(s["held_new_laws"])!=HELD or
        s["train_original_source_actions"]!=7680 or
        s["held_original_source_actions"]!=2560 or
        s["trials_per_law_seed"]!=16 or
        s["protected_first_use"] is not False or
        d["authority"]["merge"] is not False or
        d["authority"]["protected_scientific_first_use"] is not False):
        raise ValueError("ST7_PREREG_PROTOCOL_DRIFT")
    def blob(path):
        return subprocess.check_output(
            ["git","rev-parse","HEAD:"+path],text=True).strip()
    if (blob("research/nci04_st7/frozen_protocol.json")!=PREREG_BLOB or
        blob("research/nci04_st7/private_world.py")!=SOURCE_BLOB):
        raise ValueError("ST7_ORIGINAL_GIT_BLOB_MISMATCH")
    if subprocess.run(["git","merge-base","--is-ancestor",PREREG_COMMIT,
                       "HEAD"],check=False).returncode:
        raise ValueError("ST7_PRE_SOURCE_FREEZE_NOT_ANCESTOR")
    return d


def source_rank_insert(basis,vector):
    if type(vector) is not int or not 0<=vector<(1<<36):
        raise ValueError("ST7_AUDIT_BAD_ACTUATOR_FEATURE_VECTOR")
    x=vector
    while x:
        pivot=x.bit_length()-1
        if basis[pivot]:
            x^=basis[pivot]
        else:
            basis[pivot]=x
            return True
    return False


def disposition(actions,episodes,cues,rank,quadratic_terms,distinct,violations):
    checks={
        "7680_actual_source_training_actions":actions==7680,
        "1536_full_original_source_episodes":episodes==1536,
        "all_public_actuator_cues_match_true_private_actuators":cues==episodes,
        "36_quadratic_monomials_identifiable_from_actual_B":rank==36,
        "nontrivial_hidden_quadratic_structure":quadratic_terms>=32,
        "eight_distinct_public_fingerprints":distinct==8,
        "no_false_source_outcomes_or_stale_actor":violations==0,
    }
    return {
        "checks":checks,
        "decision":"SOURCE_UNKNOWN_QUADRATIC_IDENTIFIABLE_DEV_ONLY"
        if all(checks.values()) else "SOURCE_UNIDENTIFIABLE_DEV_NO_GO"
    }


def audit(path):
    verify_prereg()
    rows=private_coefficient_rows(False)
    nonlinear=sum((row>>8).bit_count() for row in rows)
    actions=0;episodes=0;verified=0;violations=0
    rank_basis=[0]*36
    unique=set()
    per_law=[]
    for law in TRAIN:
        digest=sha256()
        for seed in SEEDS:
            for trial in range(TRIALS):
                trace,cue=original_episode(law,seed,trial)
                truth=private_params(law,seed,trial)
                episodes+=1
                actions+=len(trace)
                if cue==truth:
                    verified+=1
                else:
                    violations+=1
                if len(trace)!=5 or [step[1] for step in trace]!=list(ACTIONS):
                    violations+=1
                for before,action,after,delta in trace:
                    digest.update(bytes((*before,action,*after,*delta)))
                    if tuple(a^b for a,b in zip(before,after))!=delta:
                        violations+=1
                x,_,last,_=trace[4]
                truth_g=truth[1]^quadratic(truth[2],False)
                residual=public_byte(last)^rol(public_byte(x),truth[0])
                if residual!=truth_g:
                    violations+=1
                source_rank_insert(rank_basis,features(truth[2]))
                if seed==100 and trial==0:
                    unique.add(cue)
        per_law.append({
            "evaluator_only_law":law,
            "source_original_steps":len(SEEDS)*TRIALS*len(ACTIONS),
            "actual_action_history_sha256":digest.hexdigest(),
            "source_hidden_rule_not_exported_to_models":True,
        })
    rank=sum(int(v!=0) for v in rank_basis)
    gate=disposition(actions,episodes,verified,rank,nonlinear,
                     len(unique),violations)
    record={
        "schema":SCHEMA,
        "frozen_prereg_commit":PREREG_COMMIT,
        "frozen_prereg_git_blob":PREREG_BLOB,
        "private_source_git_blob":SOURCE_BLOB,
        "train_original_real_actions":actions,
        "train_original_real_episodes":episodes,
        "genuine_public_cues_recovered":verified,
        "public_feature_GF2_rank":rank,
        "nonzero_private_quadratic_terms_source_only":nonlinear,
        "distinct_train_world_fingerprints":len(unique),
        "violations":violations,
        "per_law_actual_original_source_receipts":per_law,
        "source_gate":gate,
        "held_new_combinations_unopened":True,
        "negative_new_rule_unopened":True,
        "interference_laws_unopened":True,
        "models_not_trained":True,
        "protected_first_use_unopened":True,
        "scientific_pass":False
    }
    path.write_text(canonical(record)+"\n",encoding="utf-8")
    print("ST7_ORIGINAL_TRAIN_ACTIONS="+str(actions))
    print("ST7_SOURCE_GF2_FEATURE_RANK="+str(rank))
    print("ST7_PRIVATE_NONZERO_QUADRATIC_COEFFICIENT_COUNT="+str(nonlinear))
    print("ST7_SOURCE_DISPOSITION="+gate["decision"])
    print("ST7_NO_HELD_NEGATIVE_INTERFERENCE_OR_FIRST_USE=PASS")
    return record


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    audit(args.out)
