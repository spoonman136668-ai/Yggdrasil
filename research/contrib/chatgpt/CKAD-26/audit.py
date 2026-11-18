"""CKAD26 independent prospective change-point score and frozen gates.

Recompute every alternative alarm from *public* time-ordered traces. Source
families and true boundaries are used only AFTER all forecasts and alarms
have been committed. No model weights are changed in this script.
"""
from fractions import Fraction
from itertools import product
from hashlib import sha256
import argparse
import json
from pathlib import Path

from causal_evidence import ChangeEvidence,MODES

HERE=Path(__file__).resolve().parent
SEEDS=(101,202,303)
SCHEDULES=("transition_flip","reward_flip","no_change")
COUNTS=(48,96,144)
ARMS=MODES
BASE_SHA="a4c6d82727256306c06c20bf28d65bf888f7e671"
SOURCE_SHA="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"


def need(b,code):
    if not b:raise ValueError("CKAD26_AUDIT_"+code)


def canonical(z):
    return json.dumps(z,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")


def sha(raw):
    return sha256(raw).hexdigest()


def semantic(v):
    def skip(x):
        if isinstance(x,dict):
            return {k:skip(y) for k,y in x.items() if k not in
                    ("stable_sha256","wall_seconds","source_candidate_sha")}
        if isinstance(x,list):return [skip(y) for y in x]
        return x
    return sha(canonical(skip(v)))


def valid_sha(s):
    return type(s) is str and len(s)==64 and all(q in "0123456789abcdef" for q in s)


def protocol():
    p=json.loads((HERE/"prereg.json").read_bytes())
    need(p["schema"]=="yggdrasil.ckad26.causal-change-bayes-prereg.v1" and
         p["parent_commit"]==BASE_SHA and
         p["source_generator_sha256"]==SOURCE_SHA and
         p["seeds"]==list(SEEDS) and
         list(p["schedules"])==list(SCHEDULES) and
         p["exposure"]["public_episodes_per_case"]==192,"FROZEN_PROTOCOL")
    need(p["scientific_pass"] is False if "scientific_pass" in p
         else p["science_pass"] is False,"FROZEN_SCIENCE_FENCE")
    return p


def classify(alarms,changes,random=False):
    matched={str(b):None for b in changes}
    extras=0
    prior=0
    for event in alarms:
        absolute=event["evidence_count"]
        count=absolute-448
        need(type(absolute) is int and 1<=count<=192 and
             count>prior and valid_sha(event["event_id"]),
             "ALARM_EVIDENCE")
        prior=count
        if not random:
            signal=event["score"]
            need(type(signal) is list and len(signal)==2 and
                 all(type(v) is int for v in signal) and signal[1]>0 and
                 Fraction(*signal)>=16,"ALARM_STRENGTH")
        target=next((b for b in changes if b<count<=b+16 and
                     matched[str(b)] is None),None)
        if target is None:extras+=1
        else:matched[str(target)]=count-target
    return {"recognized":{key:value is not None for key,value in matched.items()},
            "detection_lag":matched,
            "true_detections":sum(v is not None for v in matched.values()),
            "false_alarms":extras,
            "alarm_counts":[x["evidence_count"]-448 for x in alarms]}


def validate_case(d,p):
    need(d["schema"]=="yggdrasil.ckad26.causal-change-bayes.case.v1" and
         d["schedule"] in SCHEDULES and d["seed"] in SEEDS,
         "CASE_SELECTOR")
    spec=p["schedules"][d["schedule"]]
    need(d["source_seed"]==d["seed"]+spec["offset"] and
         d["source_cohort"]==p["source_cohort"] and
         d["source_generator_sha256"]==SOURCE_SHA and
         d["parent_commit"]==BASE_SHA,"SOURCE_CUSTODY")
    need(d["source_actions_original"]==d["protected_first_use"]==
         d["held_updates"]==0 and d["scientific_pass"] is False and
         d["accepted_native"] is False and d["deployment"]=="NONE",
         "PROMOTION_FENCE")
    need(d["new_source_episodes"]==192 and d["witnesses_before"]==448 and
         d["witnesses_after"]==640 and d["chosen_intervention_actions"]==384
         and d["parent_immutable"] is True and d["cold_restore_exact"] is True,
         "EPISODE_CUSTODY")
    need(valid_sha(d["parent_checkpoint_sha256"]) and
         valid_sha(d["final_checkpoint_sha256"]) and
         0<d["final_checkpoint_bytes"]<=5*1024*1024 and
         d["final_checkpoint_name"]==f'{d["schedule"]}-{d["seed"]}-native.json',
         "CHECKPOINT_PINS")
    need(semantic(d)==d["stable_sha256"] and
         len(d["trace"])==192 and set(d["alarms"])==set(ARMS),
         "TRACE_PROVENANCE")
    shadow={key:ChangeEvidence(key,f'{d["schedule"]}/{d["seed"]}')
            for key in ARMS}
    for index,event in enumerate(d["trace"]):
        t=448+index+1
        need(set(event)=={
           "event_id","evidence_count","public_views","public_state","first_action",
           "next_state","second_action","reward"
        } and event["evidence_count"]==t and valid_sha(event["event_id"]),
        "PUBLIC_TRACE_FIELDS")
        need(type(event["public_views"]) is list and
             len(event["public_views"])==2 and
             all(type(v) is list and len(v)==2 and
                 all(type(bit) is int and bit in (0,1) for bit in v)
                 for v in event["public_views"]), "TWO_PUBLIC_VIEWS")
        need(event["public_state"]==event["public_views"][0][0],
             "PUBLIC_CONTEXT_COORDINATE")
        row={k:event[k] for k in ("public_state","first_action","next_state",
                                  "second_action","reward")}
        for monitor in shadow.values():
            monitor.observe(event["event_id"],t,row)
    for arm in ("causal_bayes","unconditional_bayes","random_alarm"):
        need(shadow[arm].alarms==d["alarms"][arm],
             "INDEPENDENT_"+arm.upper())
    need([{"event_id":event["event_id"],"evidence_count":event["evidence_count"]}
          for event in d["alarms"]["native_joint"]]==
         [{"event_id":event["event_id"],"evidence_count":event["evidence_count"]}
          for event in d["original_native_joint"]],
          "ORIGINAL_NATIVE_PARITY")
    return {arm:classify(d["alarms"][arm],spec["true_changes"],
                         random=(arm=="random_alarm")) for arm in ARMS}


def aggregate(cases):
    p=protocol()
    need(len(cases)==9,"NINE_SOURCE_CASES_REQUIRED")
    values={}
    for d in cases:
        key=(d["schedule"],d["seed"])
        need(key not in values,"NO_REPEATED_SOURCE")
        values[key]=(d,validate_case(d,p))
    need(set(values)==set(product(SCHEDULES,SEEDS)),"MISSING_GROUPS")
    per_schedule={}
    for name in SCHEDULES:
        changes=p["schedules"][name]["true_changes"]
        arms={}
        for arm in ARMS:
            per_seed={str(seed):values[name,seed][1][arm] for seed in SEEDS}
            recognized={str(change):sum(row["recognized"][str(change)]
                    for row in per_seed.values()) for change in changes}
            arms[arm]={
                "per_seed":per_seed,
                "by_true_boundary":recognized,
                "total_true":sum(row["true_detections"] for row in per_seed.values()),
                "total_false":sum(row["false_alarms"] for row in per_seed.values())
            }
        per_schedule[name]=arms
    changed=SCHEDULES[:2]
    total={arm:sum(per_schedule[s][arm]["total_true"] for s in changed)
           for arm in ARMS}
    gates={
        "recognize_each_boundary_2of3":all(
            all(n>=2 for n in per_schedule[s]["causal_bayes"]["by_true_boundary"].values())
            for s in changed),
        "plus_four_vs_native_joint":total["causal_bayes"]-total["native_joint"]>=4,
        "plus_two_vs_unconditional_bayes":total["causal_bayes"]-
                                         total["unconditional_bayes"]>=2,
        "stationary_null_false_lte1_per_seed":all(
            row["false_alarms"]<=1 for row in
            per_schedule["no_change"]["causal_bayes"]["per_seed"].values()),
        "changed_false_lte2_per_seed":all(
            row["false_alarms"]<=2 for s in changed for row in
            per_schedule[s]["causal_bayes"]["per_seed"].values()),
        "source_and_checkpoint_custody":True
    }
    result={
       "schema":"yggdrasil.ckad26.causal-change-bayes.sealed.v1",
       "classification":"DEVELOPMENT_SIGNAL_GO" if all(gates.values())
                         else "DEVELOPMENT_SIGNAL_NO_GO",
       "parent_sha":BASE_SHA,"generator_sha256":SOURCE_SHA,
       "source_schedules":per_schedule,"total_true_by_arm":total,
       "frozen_gates":gates,
       "independent_parent_groups":3,"new_synthetic_streams":9,
       "new_public_episodes":192*9,"protected_first_use":0,
       "source_actions_original":0,"held_updates":0,
       "shadow_only":True,"policy_reward_claim":False,
       "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    }
    result["stable_sha256"]=sha(canonical(result))
    return result


def load_os(root,os):
    return [json.loads((root/f"ckad26-{os}-{name}-{seed}-proof"/"case-result.json").read_bytes())
            for name,seed in product(SCHEDULES,SEEDS)]


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifact-root",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    linux,win=load_os(args.artifact_root,"ubuntu-latest"),load_os(args.artifact_root,"windows-2022")
    for a,b in zip(linux,win):
        need(a["stable_sha256"]==b["stable_sha256"] and semantic(a)==semantic(b),
             "TWO_OS_SEMANTIC_REPLAY")
    result,other=aggregate(linux),aggregate(win)
    need(result==other,"REPLAY_DRIFT")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"classification":result["classification"],
          "gates":result["frozen_gates"],
          "true":result["total_true_by_arm"],
          "stable":result["stable_sha256"]},sort_keys=True))


if __name__=="__main__":main()
