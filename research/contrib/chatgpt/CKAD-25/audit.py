"""Independent CKAD25 evidence scorer and prospective no-change falsification.

This auditor only replays public event probabilities already committed by
the real-action native learner. It does not regenerate source outcomes or
fit any alternate model. Every alarm event is recomputed independently.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
SCHEDULES=("transition_only","reward_only","stationary_null")
SEEDS=(101,202,303)
ARMS=("joint","transition","reward","factorized_or")
ORIGIN=448
BOUNDARIES=(48,96,144)
BASE="4ecc1144b1c2a3af388734fbd11a619c2cd50498"
SOURCE="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"

def need(b,reason):
    if not b:raise ValueError("CKAD25_AUDIT_"+reason)

def canonical(d):
    return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def sha(raw):
    return sha256(raw).hexdigest()

def semantic(d):
    def normalize(v):
        if isinstance(v,dict):
            return {k:normalize(x) for k,x in v.items()
                    if k not in ("stable_sha256","wall_seconds","runtime_host",
                                 "source_candidate_sha")}
        if isinstance(v,list):return [normalize(x) for x in v]
        return v
    return sha(canonical(normalize(d)))

def ratio(f):
    return [f.numerator,f.denominator]

def unratio(z):
    need(type(z) is list and len(z)==2 and
         all(type(x) is int for x in z) and z[1]>0,"RATIO")
    return Fraction(*z)

def sha64(s):
    return type(s) is str and len(s)==64 and all(z in "0123456789abcdef" for z in s)

def alarms(trace,kind):
    need(kind in ARMS,"ALARM_KIND")
    joint=transition=reward=Fraction(1)
    last=ORIGIN
    output=[]
    for index,event in enumerate(trace):
        count=ORIGIN+index+1
        need(event["evidence_count"]==count and sha64(event["event_id"]),
             "TRACE_SOURCE_ORDER")
        p=unratio(event["p_transition_observed"])
        q=unratio(event["p_reward_observed"])
        need(0<p<=1 and 0<q<=1,"TRACE_PROBABILITY")
        joint=max(Fraction(1),joint/(4*p*q))
        transition=max(Fraction(1),transition/(2*p))
        reward=max(Fraction(1),reward/(2*q))
        if count-last<8:continue
        if kind=="joint":
            flag=joint>=16
            score=joint
            causes=["joint"] if flag else []
        elif kind=="transition":
            flag=transition>=16
            score=transition
            causes=["transition"] if flag else []
        elif kind=="reward":
            flag=reward>=16
            score=reward
            causes=["reward"] if flag else []
        else:
            flag=transition>=16 or reward>=16
            score=max(transition,reward)
            causes=[name for name,b in (("transition",transition>=16),
                                       ("reward",reward>=16)) if b] if flag else []
        if flag:
            output.append({"event_id":event["event_id"],"evidence_count":count,
                           "score":ratio(score),"causes":causes})
            joint=transition=reward=Fraction(1)
            last=count
    return output

def classify(items,changes):
    need(all(type(b) is int for b in changes),"BOUNDARY_TYPES")
    detected={str(b):None for b in changes}
    false=0
    counts=[]
    for event in items:
        n=event["evidence_count"]-ORIGIN
        need(8<=n<=192 and n not in counts and sha64(event["event_id"]),
             "ALARM_SOURCE")
        counts.append(n)
        need(unratio(event["score"])>=16,"ALARM_STRENGTH")
        match=next((b for b in changes if b<n<=b+16 and detected[str(b)] is None),None)
        if match is None:false+=1
        else:detected[str(match)]=n-match
    need(counts==sorted(counts),"ALARM_ORDER")
    return {"recognized":{k:v is not None for k,v in detected.items()},
            "detection_delays":detected,"false_alarms":false,
            "stream_counts":counts}

def protocols():
    p=json.loads((HERE/"prereg.json").read_bytes())
    need(p["schema"]=="yggdrasil.ckad25.factorized-surprise-development.prereg.v1" and
         p["parent_commit"]==BASE and p["generator_sha256"]==SOURCE and
         p["checkpoint_parent_group_seeds"]==list(SEEDS) and
         p["budgets"]["source_case_count"]==9,"FROZEN_PROTOCOL")
    need(list(p["source_schedules"])==list(SCHEDULES) and
         set(p["true_change_counts"])==set(SCHEDULES),"SCENARIO_KEYS")
    need(p["true_change_counts"]=={
       "transition_only":[48,96,144],"reward_only":[48,96,144],"stationary_null":[]
    },"FROZEN_BOUNDARIES")
    return p

def validate_case(d,protocol):
    need(d["schema"]=="yggdrasil.ckad25.factorized-surprise.case.v1" and
         d["schedule"] in SCHEDULES and d["seed"] in SEEDS,"SOURCE_ID")
    need(d["source_seed"]==d["seed"]+protocol["source_seed_offsets"][d["schedule"]] and
         d["source_cohort"]==protocol["source_namespace"] and
         d["source_generator_sha256"]==SOURCE and
         d["unchanged_native_parent_commit"]==BASE,"SOURCE_PIN")
    need(d["scientific_pass"] is False and d["accepted_native"] is False and
         d["deployment"]=="NONE" and d["original_source_actions"]==
         d["protected_first_use"]==d["held_updates"]==0,"SOURCE_CUSTODY")
    need(d["new_public_episodes"]==d["case_episodes"]==192 and
         d["old_public_episodes"]==448 and d["source_actions"]==384,
         "EPISODE_BUDGET")
    need(sha64(d["parent_checkpoint_sha256"]) and
         sha64(d["final_checkpoint_sha256"]) and d["final_checkpoint_bytes"]>0 and
         d["final_checkpoint_name"]==
         f'{d["schedule"]}-{d["seed"]}-native.json',"CHECKPOINT_FENCE")
    need(len(d["trace"])==192 and set(d["alarms"])==set(ARMS),"TRACE_LENGTH")
    need(semantic(d)==d["stable_sha256"],"SEMANTIC_SHA256")
    for item in d["trace"]:
        need(set(item)=={
          "event_id","evidence_count","public_view","first_action","next_state",
          "second_action","reward","p_transition_observed","p_reward_observed"
        },"SOURCE_PUBLIC_ONLY")
        need(type(item["public_view"]) is list and len(item["public_view"])==2 and
             all(type(z) is int and z in (0,1) for z in
                 item["public_view"]+
                 [item["first_action"],item["next_state"],
                  item["second_action"],item["reward"]]),
             "BINARY_OBSERVATION")
    result={}
    for arm in ARMS:
        shadow=alarms(d["trace"],arm)
        need(shadow==d["alarms"][arm],"SHADOW_DETECTOR_REPLAY")
        result[arm]=classify(shadow,protocol["true_change_counts"][d["schedule"]])
    need([{k:v for k,v in z.items() if k in ("event_id","evidence_count")}
          for z in d["alarms"]["joint"]]==
         [{k:v for k,v in z.items() if k in ("event_id","evidence_count")}
          for z in d["native_joint_detections"]],"NATIVE_JOINT_REPLAY")
    return result

def aggregate(cases):
    p=protocols()
    need(len(cases)==9,"NINE_CASES")
    matrix={}
    for d in cases:
        key=(d["schedule"],d["seed"])
        need(key not in matrix,"DUPLICATE_CASE")
        matrix[key]=(d,validate_case(d,p))
    need(set(matrix)==set(product(SCHEDULES,SEEDS)),"ALL_CASES")
    schedule_results={}
    for name in SCHEDULES:
        source=[matrix[name,s] for s in SEEDS]
        changes=p["true_change_counts"][name]
        per_arm={}
        for arm in ARMS:
            per_seed={str(d["seed"]):diag[arm] for d,diag in source}
            recall={str(b):sum(row["recognized"][str(b)] for row in per_seed.values())
                    for b in changes}
            per_arm[arm]={
                "per_seed":per_seed,
                "seed_recall_per_boundary":recall,
                "total_true_detections":sum(recall.values()),
                "total_false_alarms":sum(row["false_alarms"] for row in per_seed.values())
            }
        schedule_results[name]=per_arm
    joint=sum(schedule_results[n]["joint"]["total_true_detections"] for n in SCHEDULES[:2])
    fact=sum(schedule_results[n]["factorized_or"]["total_true_detections"] for n in SCHEDULES[:2])
    gates={
       "recognition_per_boundary_each_schedule":all(
           all(v>=2 for v in schedule_results[n]["factorized_or"]["seed_recall_per_boundary"].values())
           for n in SCHEDULES[:2]),
       "gain_at_least_four_true_detections":fact-joint>=4,
       "changed_world_false_alarms_lte3_each":all(
           row["false_alarms"]<=3
           for n in SCHEDULES[:2]
           for row in schedule_results[n]["factorized_or"]["per_seed"].values()),
       "stationary_null_false_alarms_lte1_each":all(
           row["false_alarms"]<=1
           for row in schedule_results["stationary_null"]["factorized_or"]["per_seed"].values()),
       "exact_source_and_replay_custody":True
    }
    report={
       "schema":"yggdrasil.ckad25.factorized-surprise.sealed.v1",
       "classification":"DEVELOPMENT_SIGNAL_GO" if all(gates.values())
                        else "DEVELOPMENT_SIGNAL_NO_GO",
       "parent_sha":BASE,"original_generator_sha256":SOURCE,
       "source_schedules":schedule_results,
       "frozen_gates":gates,
       "total_joint_true_detections":joint,
       "total_factorized_true_detections":fact,
       "factorized_minus_joint_true_detections":fact-joint,
       "independently_restored_parent_seed_groups":3,
       "synthetic_new_exogenous_streams":9,
       "total_public_episodes":192*9,
       "original_source_actions":0,"protected_first_use":0,
       "held_learning_updates":0,
       "shadow_only":True,
       "policy_reward_claim":False,
       "scientific_pass":False,"accepted_native":False,"deployment":"NONE"
    }
    report["stable_sha256"]=sha(canonical(report))
    return report

def files(root,os):
    return [json.loads((root/f"ckad25-{os}-{schedule}-{seed}-proof"/"case-result.json").read_bytes())
            for schedule,seed in product(SCHEDULES,SEEDS)]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--artifact-root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    linux,windows=files(args.artifact_root,"ubuntu-latest"),files(args.artifact_root,"windows-2022")
    for a,b in zip(linux,windows):
        need(a["stable_sha256"]==b["stable_sha256"],"CROSS_OS_SOURCE_SEMANTIC")
        need(semantic(a)==semantic(b),"CROSS_OS_MISMATCH")
    one,two=aggregate(linux),aggregate(windows)
    need(one==two,"CROSS_OS_RESULT")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(one,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "classification":one["classification"],
        "gain":one["factorized_minus_joint_true_detections"],
        "frozen_gates":one["frozen_gates"],
        "stable_sha256":one["stable_sha256"]
    },sort_keys=True))

if __name__=="__main__":main()
