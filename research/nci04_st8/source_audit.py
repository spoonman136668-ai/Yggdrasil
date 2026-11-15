"""ST8 frozen SOURCE ONLY: does real cubic rule falsify quadratic prior?

No ST8 candidate is instantiated; no held/new-rule/interference outcomes
are touched. Original private source truth may be inspected by THIS
evaluator-only audit, never by the learner API.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from research.nci04_st8.private_world import (
    ACTIONS,source_episode,private_params,effect,
    coefficient_rows,monomials,pack,rol,TRIALS
)

PREREG_COMMIT="2e9cdb5a84306f54f670fd17d9f063809604d236"
PREREG_BLOB="1bf9f460c8a38d271ed1299c8d86cb777b0b0a0e"
SOURCE_BLOB="39502f081e85ff0d3f7a5c22101a7bf3c1f3629a"
TRAIN=(3,5,7,11,13,17,19,23)
SEEDS=tuple(range(100,112))
HELD=(29,31,37,41)
SCHEMA="yggdrasil.nci04.st8.cubic-identifiability-source-only.v1"


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)


def verify():
    d=json.loads(Path(__file__).with_name(
        "frozen_protocol.json").read_text("utf-8"))
    s=d["source"]
    if (d["schema"]!=
        "yggdrasil.nci04.st8.contradiction-driven-structural-growth.dev.v1" or
        d["status"]!="FROZEN_BEFORE_ST8_SOURCE_CODE_MODEL_IMPLEMENTATION_OR_OUTCOME" or
        tuple(s["train_laws"])!=TRAIN or tuple(s["train_seeds"])!=SEEDS or
        tuple(s["held_new_laws"])!=HELD or
        s["trial_count_per_law_seed"]!=TRIALS or
        s["actual_training_actions"]!=7680 or
        s["actual_held_actions"]!=2560 or
        s["protected_scientific_first_use"] is not False or
        d["authority"]["merge"] is not False):
        raise ValueError("ST8_FROZEN_PREREG_CHANGED")
    def blob(p):
        return subprocess.check_output(
            ["git","rev-parse","HEAD:"+p],text=True).strip()
    if (blob("research/nci04_st8/frozen_protocol.json")!=PREREG_BLOB or
        blob("research/nci04_st8/private_world.py")!=SOURCE_BLOB):
        raise ValueError("ST8_ORIGINAL_PREREG_SOURCE_BLOB_DRIFT")
    if subprocess.run(["git","merge-base","--is-ancestor",PREREG_COMMIT,
                       "HEAD"],check=False).returncode:
        raise ValueError("ST8_PREREG_NO_LONGER_ANCESTOR")
    return d


def put_constraint(basis,vec,output,rank):
    if (type(vec) is not int or not 0<=vec<(1<<rank) or
        type(output) is not int or output not in range(256) or
        type(basis) is not list or len(basis)!=rank):
        raise ValueError("ST8_SOURCE_GF2_BAD_CONSTRAINT")
    row=vec|(output<<rank)
    while row&((1<<rank)-1):
        pivot=(row&((1<<rank)-1)).bit_length()-1
        if basis[pivot]:
            row^=basis[pivot]
        else:
            basis[pivot]=row
            return "INDEPENDENT"
    return "CONTRADICTS" if row>>rank else "REDUNDANT"


def source_gate(episodes,actions,cues,rank92,nonlinear_terms,
                contradictory_quadratic,conflict_cubic,unique_cues,violations):
    checks={
        "original_source_1536_complete_episodes":episodes==1536,
        "original_source_7680_real_actions":actions==7680,
        "every_original_public_diagnostic_recovers_true_A_B_rotation":cues==episodes,
        "92_cubic_features_independent_on_original_training_B":rank92==92,
        "true_private_third_order_causal_terms_present":nonlinear_terms>=120,
        "quadratic_36_feature_prior_falsified_on_genuine_consequences":
            contradictory_quadratic>=16,
        "full_cubic_source_is_consistent":conflict_cubic==0,
        "eight_distinct_original_public_law_signatures":unique_cues==8,
        "no_original_event_or_actor_violations":violations==0,
    }
    return {
        "checks":checks,
        "disposition":"SOURCE_CUBIC_FALSIFIES_QUADRATIC_DEV_ONLY"
        if all(checks.values()) else "SOURCE_NONCUBIC_OR_UNIDENTIFIABLE_DEV_NO_GO"
    }


def audit(out):
    verify()
    terms=sum((row>>36).bit_count() for row in coefficient_rows())
    original_count=0;episodes=0;cues=0;violations=0
    quadratic=[0]*36;cubic=[0]*92
    rank92=0;bad36=0;bad92=0
    first_cues=set()
    law_records=[]
    for law in TRAIN:
        history=sha256()
        for seed in SEEDS:
            for trial in range(TRIALS):
                events,cue=source_episode(law,seed,trial)
                truth=private_params(law,seed,trial)
                episodes+=1;original_count+=len(events)
                cues+=int(cue==truth)
                violations+=int(cue!=truth)
                if (len(events)!=5 or
                    tuple(z[1] for z in events)!=ACTIONS):
                    violations+=1
                for before,action,after,delta in events:
                    history.update(bytes((*before,action,*after,*delta)))
                    violations+=int(
                        tuple(a^b for a,b in zip(before,after))!=delta
                    )
                before,act,after,_=events[4]
                f_truth=effect(truth[2])
                derived=pack(after)^rol(pack(before),truth[0])^truth[1]
                violations+=int(derived!=f_truth)
                q=put_constraint(quadratic,monomials(truth[2],2),
                                 derived,36)
                c=put_constraint(cubic,monomials(truth[2],3),
                                 derived,92)
                bad36+=int(q=="CONTRADICTS")
                bad92+=int(c=="CONTRADICTS")
                rank92+=int(c=="INDEPENDENT")
                if seed==100 and trial==0:
                    first_cues.add(cue)
        law_records.append({
            "evaluator_law_only":law,
            "source_real_original_actions":len(SEEDS)*TRIALS*5,
            "source_real_public_action_sha256":history.hexdigest(),
            "coefficient_row_or_law_id_passed_to_learner":False
        })
    gate=source_gate(episodes,original_count,cues,rank92,terms,
                     bad36,bad92,len(first_cues),violations)
    d={
        "schema":SCHEMA,
        "pre_source_frozen_protocol_commit":PREREG_COMMIT,
        "pre_source_frozen_protocol_blob":PREREG_BLOB,
        "original_private_source_blob":SOURCE_BLOB,
        "real_original_training_episodes":episodes,
        "real_original_training_actions":original_count,
        "correct_public_diagnostic_actions":cues,
        "cubic_source_true_third_order_nonzero_terms":terms,
        "observed_cubic_GF2_rank":rank92,
        "observed_quadratic_contradictions":bad36,
        "observed_cubic_contradictions":bad92,
        "eight_distinct_world_first_cues":len(first_cues),
        "private_source_or_public_action_violations":violations,
        "real_source_law_action_history_records":law_records,
        "source_gate":gate,
        "no_native_model_trained":True,
        "held_worlds_unopened":True,
        "different_rule_negative_unopened":True,
        "interference_source_unopened":True,
        "protected_scientific_first_use_unopened":True,
        "independent_scientific_pass":False
    }
    out.write_text(canonical(d)+"\n",encoding="utf-8")
    print("ST8_SOURCE_ORIGINAL_ACTIONS="+str(original_count))
    print("ST8_SOURCE_CUBIC_RANK="+str(rank92))
    print("ST8_SOURCE_QUADRATIC_CONTRADICTIONS="+str(bad36))
    print("ST8_SOURCE_CUBIC_CONTRADICTIONS="+str(bad92))
    print("ST8_SOURCE_DISPOSITION="+gate["disposition"])
    print("ST8_SOURCE_NO_UNFAMILIAR_OR_PROTECTED_FIRST_USE=PASS")
    return d


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    audit(args.out)
