"""ST9 SOURCE-ONLY original eight-intervention budget audit.

Checks genuine public action-consequence evidence from THREE preregistered
actor policies. Models/held/negative mechanisms are never opened. Only
this private evaluator module may inspect actual private source rows.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from research.nci04_st9.private_world import (
    F,original_episode,rotation,source_coefficients,rol,pack,effect
)

FROZEN_COMMIT="5159a65cd403bc3cbd507ab713742ebae330e28a"
FROZEN_BLOB="9ad8bc15e8dd8b0757c8db13772de23c57d2f3cf"
SOURCE_BLOB="d1bdf67503bd797d79386406820679b70403e8bb"
TRAIN_LAWS=(3,5,7,11,13,17,19,23)
TRAIN_SEEDS=tuple(range(100,108))
ACTIVE=(1,2,3,4,6,8,9,12)
PASSIVE_REPEAT=(1,2,4,8,1,2,4,8)
PASSIVE_DISPERSED=(1,3,5,7,9,11,13,15)
ACTORS={"active":ACTIVE,"passive_repeat":PASSIVE_REPEAT,
        "passive_dispersed":PASSIVE_DISPERSED}


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)


def verify_freeze():
    doc=json.loads(Path(__file__).with_name("frozen_protocol.json").read_text(
        encoding="utf-8"
    ))
    s=doc["source"]
    if (doc["schema"]!="yggdrasil.nci04.st9.budgeted-active-native-memory-repair.dev.v1" or
        doc["status"]!="FROZEN_BEFORE_ST9_ORIGINAL_SOURCE_OR_MODEL_OR_OUTCOME" or
        tuple(s["train_laws"])!=TRAIN_LAWS or
        tuple(s["train_seeds"])!=TRAIN_SEEDS or
        tuple(s["frozen_public_active_probes"])!=ACTIVE or
        tuple(s["frozen_blind_passive_repeat"])!=PASSIVE_REPEAT or
        tuple(s["frozen_blind_passive_dispersed"])!=PASSIVE_DISPERSED or
        s["original_train_actions_per_model"]!=16 or
        s["original_informative_interventions_per_model"]!=8 or
        s["held_original_actions_per_model"]!=512 or
        s["protected_scientific_first_use"] is not False or
        doc["authority"]["merge"] is not False):
        raise ValueError("ST9_FROZEN_PROTOCOL_DRIFT")
    def git_blob(p):
        return subprocess.check_output(
            ["git","rev-parse","HEAD:"+p],text=True).strip()
    if (git_blob("research/nci04_st9/frozen_protocol.json")!=FROZEN_BLOB or
        git_blob("research/nci04_st9/private_world.py")!=SOURCE_BLOB):
        raise ValueError("ST9_FROZEN_SOURCE_OR_PROTOCOL_BYTES_CHANGED")
    if subprocess.run(["git","merge-base","--is-ancestor",FROZEN_COMMIT,
                       "HEAD"],check=False).returncode:
        raise ValueError("ST9_FROZEN_PRE_SOURCE_COMMIT_NOT_ANCESTOR")
    return doc


def insert(rows,feat,value,n):
    mask=(1<<n)-1
    row=feat|(value<<n)
    while row&mask:
        pivot=(row&mask).bit_length()-1
        if rows[pivot]:
            row^=rows[pivot]
        else:
            rows[pivot]=row
            return "NEW"
    return "CONTRADICTION" if row>>n else "KNOWN"


def rank(probes,n=8):
    rows=[0]*n
    for B in probes:
        insert(rows,F(B,2) if n==8 else F(B,1),0,n)
    return sum(x!=0 for x in rows)


def greedy_public_actor():
    seen=[]
    basis=[0]*8
    for _ in range(8):
        for B in range(1,16):
            if B in seen:
                continue
            test=list(basis)
            if insert(test,F(B,2),0,8)=="NEW":
                seen.append(B)
                basis=test
                break
        else:
            raise ValueError("ST9_PUBLIC_ACTOR_CANNOT_FIND_NEW_PROBE")
    return tuple(seen)


def source_gate(episodes,steps,cues,active_rank,
                other_ranks,quadratic_coeffs,linear_conflicts,
                full_conflicts,original_violations):
    checks={
        "exactly_eight_original_source_episodes_per_actor":
            episodes=={name:8 for name in ACTORS},
        "exactly_sixteen_original_source_actions_per_actor":
            steps=={name:16 for name in ACTORS},
        "all_neutral_source_public_rotations_recovered":
            cues==24,
        "active_public_action_feature_rank8":active_rank==8,
        "passive_actor_feature_ranks_4_and_6":
            other_ranks==[4,6],
        "private_unknown_source_has_real_quadratic_terms":
            quadratic_coeffs>=8,
        "linear_source_precondition_genuinely_falsified":
            linear_conflicts>=1,
        "full_eight_feature_source_consistent":
            full_conflicts==0,
        "all_original_source_actions_valid":original_violations==0,
    }
    return {"checks":checks,"disposition":
        "SOURCE_BUDGETED_CAUSAL_REPAIR_IDENTIFIABLE_DEV_ONLY"
        if all(checks.values()) else
        "SOURCE_NONIDENTIFIABLE_OR_NO_LINEAR_CONTRADICTION_DEV_NO_GO"
    }


def audit(out):
    verify_freeze()
    if greedy_public_actor()!=ACTIVE:
        raise ValueError("ST9_ACTIVE_POLICY_REPREREG_DRIFT")
    episodes={name:0 for name in ACTORS}
    actions={name:0 for name in ACTORS}
    cues=0;violations=0
    sources={}
    rows1=[0]*4;rows8=[0]*8
    linear_conflicts=0;full_conflicts=0
    for name,probes in ACTORS.items():
        trace=sha256()
        for i,(law,seed,B) in enumerate(zip(TRAIN_LAWS,TRAIN_SEEDS,probes)):
            events=original_episode(law,seed,0,B)
            episodes[name]+=1;actions[name]+=len(events)
            if tuple(ev[1] for ev in events)!=(0,B+1):
                violations+=1
            for before,action,after,delta in events:
                trace.update(bytes((*before,action,*after,*delta)))
                violations+=int(tuple(x^y for x,y in zip(before,after))!=delta)
            before,_,post,_=events[0]
            opts=[r for r in (1,2,3) if rol(pack(before),r)==pack(post)]
            if len(opts)==1 and opts[0]==rotation(law):
                cues+=1
            else:
                violations+=1
            before,_,post,_=events[1]
            y=pack(post)^rol(pack(before),rotation(law))
            if y!=effect(B):
                violations+=1
            if name=="active":
                linear_conflicts+=int(insert(rows1,F(B,1),y,4)=="CONTRADICTION")
                full_conflicts+=int(insert(rows8,F(B,2),y,8)=="CONTRADICTION")
        sources[name]={
            "actual_original_source_action_sha256":trace.hexdigest(),
            "original_source_episodes":episodes[name],
            "original_source_actions":actions[name],
            "probes_public_action_only":list(probes),
            "private_coefficient_or_source_law_passed_to_learner":False
        }
    nonlinear=sum((row>>4).bit_count() for row in source_coefficients())
    gate=source_gate(episodes,actions,cues,rank(ACTIVE),
                     [rank(PASSIVE_REPEAT),rank(PASSIVE_DISPERSED)],
                     nonlinear,linear_conflicts,full_conflicts,violations)
    data={
        "schema":"yggdrasil.nci04.st9.source-only-original-action-audit.v1",
        "frozen_commit":FROZEN_COMMIT,
        "frozen_protocol_blob":FROZEN_BLOB,
        "private_source_blob":SOURCE_BLOB,
        "real_source_actor_receipts":sources,
        "source_private_nonzero_quadratic_coefficients":nonlinear,
        "observed_linear_contradictions_active":linear_conflicts,
        "observed_full_interaction_contradictions":full_conflicts,
        "public_active_feature_rank":rank(ACTIVE),
        "public_passive_repeat_feature_rank":rank(PASSIVE_REPEAT),
        "public_passive_dispersed_feature_rank":rank(PASSIVE_DISPERSED),
        "source_gate":gate,
        "models_not_instantiated":True,
        "held_source_unopened":True,
        "alternative_rule_unopened":True,
        "interference_unopened":True,
        "protected_scientific_first_use_unopened":True,
        "independent_scientific_pass":False
    }
    out.write_text(canonical(data)+"\n",encoding="utf-8")
    print("ST9_SOURCE_ACTIONS_EACH_ARM=16")
    print("ST9_SOURCE_ACTIVE_FEATURE_RANK="+str(rank(ACTIVE)))
    print("ST9_SOURCE_PASSIVE_FEATURE_RANKS="+str([
        rank(PASSIVE_REPEAT),rank(PASSIVE_DISPERSED)]))
    print("ST9_SOURCE_REAL_LINEAR_CONTRADICTIONS="+str(linear_conflicts))
    print("ST9_SOURCE_DISPOSITION="+gate["disposition"])
    print("ST9_NO_HELD_OR_NEGATIVE_OR_FIRST_USE=PASS")
    return data


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();audit(args.out)
