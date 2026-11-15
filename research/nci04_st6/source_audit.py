"""ST6 frozen SOURCE-ONLY audit; no model/held/alternative-law first use."""
from collections import Counter
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess

from research.nci04_st6.original_world import (
    source_episode,law_params,rotate,composition,hypothesis_outputs,
    ACTIONS,TRIALS
)

PREREG_COMMIT="5c1c8cebff688eb9042a68d72c96eec1d81e8c5d"
PREREG_BLOB="86b2fa6bfce3333c68cffc44eea67e9904756b65"
TRAIN=(3,5,7,11,13,17,19,23)
SEEDS=tuple(range(100,112))
HELD=(29,31,37,41)
NEG=(43,47)
SCHEMA="yggdrasil.nci04.st6.original-source-eligibility.v1"


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)


def verify_prereg():
    data=json.loads(Path(__file__).with_name(
        "frozen_protocol.json").read_text("utf-8"))
    s=data["source"]
    if (data.get("schema")!=
        "yggdrasil.nci04.st6.compositional-native-causal-transfer.dev.v1" or
        data.get("status")!="PREREG_FROZEN_BEFORE_ST6_SOURCE_CODE_OR_OUTCOMES" or
        tuple(s.get("train_laws",()))!=TRAIN or
        tuple(s.get("train_seeds",()))!=SEEDS or
        tuple(s.get("held_new_combinations",()))!=HELD or
        tuple(s.get("negative_new_mechanism_laws",()))!=NEG or
        s.get("trials_per_law_seed")!=TRIALS or
        s.get("frozen_train_actions")!=7680 or
        s.get("frozen_held_actions")!=2560 or
        data["authority"]["independent_scientific_first_use"] is not False or
        data["authority"]["merge"] is not False):
        raise ValueError("ST6_PREREG_CONTENT_DRIFT")
    get=lambda p:subprocess.check_output(
        ["git","rev-parse","HEAD:"+p],text=True).strip()
    if get("research/nci04_st6/frozen_protocol.json")!=PREREG_BLOB:
        raise ValueError("ST6_FROZEN_PRE_SOURCE_BLOB_CHANGED")
    if subprocess.run(["git","merge-base","--is-ancestor",
                      PREREG_COMMIT,"HEAD"],check=False).returncode:
        raise ValueError("ST6_FROZEN_PROTOCOL_NO_LONGER_ANCESTOR")
    return data


def audit_gate(actions,episodes,correct_cues,signatures,alternate_diff):
    checks={
        "exact_original_training_actions":actions==7680,
        "exact_original_training_episodes":episodes==1536,
        "all_training_public_signatures_recovered":
            correct_cues==episodes,
        "all_eight_training_laws_have_distinct_public_fingerprints":
            len(signatures)==8 and len(set(signatures.values()))==8,
        "true_composition_distinguishable_from_every_alternative":
            type(alternate_diff) is list and len(alternate_diff)==7 and
            all(type(k) is int and k>=16 for k in alternate_diff),
    }
    return {
        "checks":checks,
        "disposition":(
            "SOURCE_COMPOSITION_IDENTIFIABLE_DEV_ONLY"
            if all(checks.values()) else
            "SOURCE_COMPOSITION_IDENTIFIABILITY_NO_GO"
        )
    }


def audit(output):
    verify_prereg()
    actions=0;episodes=0;good=0
    aliases={}
    all_alternates=[0]*7
    receipts=[]
    for law in TRAIN:
        truth=law_params(law)
        trace=sha256()
        for seed in SEEDS:
            for trial in range(TRIALS):
                events,cue=source_episode(law,seed,trial)
                episodes+=1
                actions+=len(events)
                if len(events)!=5 or tuple(e[1] for e in events)!=ACTIONS:
                    raise ValueError("ST6_PUBLIC_ACTOR_DIVERGENCE")
                for before,action,after,target in events:
                    trace.update(bytes((*before,action,*after,*target)))
                    if tuple(x^y for x,y in zip(before,after))!=target:
                        raise ValueError("ST6_ORIGINAL_EVENT_NOT_AUTHENTIC")
                if cue==truth:good+=1
                if law in aliases and aliases[law]!=cue:
                    raise ValueError("ST6_PUBLIC_SOURCE_CUE_NOT_STABLE")
                aliases[law]=cue
                hyp=hypothesis_outputs(cue[1],cue[2])
                source_target=composition(truth[1],truth[2])
                if hyp[0]!=source_target:
                    raise ValueError("ST6_SOURCE_TRUE_RULE_NOT_REGISTERED")
                for j,alt in enumerate(hyp[1:]):
                    all_alternates[j]+=(alt^source_target).bit_count()
        receipts.append({
            "source_law_evaluator_only":law,
            "actual_original_episodes":len(SEEDS)*TRIALS,
            "actual_source_sha256":trace.hexdigest(),
            "public_diagnostic_cue":list(truth),
            "private_law_or_mask_passed_to_model":False,
        })
    result=audit_gate(actions,episodes,good,aliases,all_alternates)
    report={
        "schema":SCHEMA,
        "source_class":"INHOUSE_TRAIN_SOURCE_ONLY",
        "frozen_prereg_commit":PREREG_COMMIT,
        "frozen_prereg_blob":PREREG_BLOB,
        "training_real_action_steps":actions,
        "training_real_episodes":episodes,
        "public_cue_recovered_from_actual_actions":good,
        "distinct_training_public_cues":len(set(aliases.values())),
        "bit_differences_vs_other_seven_frozen_hypotheses":all_alternates,
        "original_source_law_action_receipts":receipts,
        "gate":result,
        "held_dev_laws_unopened":True,
        "unseen_mechanism_negative_laws_unopened":True,
        "trained_models_unopened":True,
        "protected_scientific_first_use_unopened":True,
        "scientific_pass":False
    }
    output.write_text(canonical(report)+"\n",encoding="utf-8")
    print("ST6_SOURCE_REAL_ACTIONS="+str(actions))
    print("ST6_SOURCE_LAW_CUES="+str(report["distinct_training_public_cues"]))
    print("ST6_HYPOTHESIS_NEGATIVE_BIT_MARGINS="+canonical(all_alternates))
    print("ST6_SOURCE_DISPOSITION="+result["disposition"])
    print("ST6_SOURCE_NO_HELD_OR_FIRST_USE=PASS")
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    audit(args.out)
