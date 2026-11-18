"""Independent audit of CKAD24 frozen shifted-world training and change sensitivity.

Consumes native outputs; never generates episodes or updates a learner.
Every inference receives the original exact CKAD23 model under unchanged
architecture, policy and frozen detector threshold. No post-result tuning.
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
PARENT=HERE.parent/"CKAD-23"
SEEDS=(101,202,303)
SCHEDULES=("middle_swap","double_flip")
SHIFTS=(48,96,144)
CHECKPOINTS=tuple(range(0,193,16))
ARMS=("detector_active","detector_random","no_reset","periodic32",
      "pooled_replay","trailing_mle","exact_mixture","frozen_ckad22")
SOURCE_SHA="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
PARENT_BLOB="e5be78562e8087fd98e1540062de01f15dbc3797"
PARENT_SHA="08fbe556d7ac134d3662f7003af5bc4430013ac1"

def need(condition,reason):
    if not condition:raise ValueError("CKAD24_AUDIT_"+reason)

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def sha(data):
    return sha256(data).hexdigest()

def sha64(s):
    return type(s) is str and len(s)==64 and all(c in "0123456789abcdef" for c in s)

def fraction(value):
    need(type(value) is list and len(value)==2 and
         all(type(v) is int for v in value) and value[1]>0,"RATIO")
    return Fraction(*value)

def source_protocol():
    p=json.loads((HERE/"prereg.json").read_bytes())
    q=json.loads((PARENT/"prereg.json").read_bytes())
    need(p["schema"]=="yggdrasil.ckad24.permuted-causal-changes.prereg.v1"
         and p["base_commit"]==PARENT_SHA
         and p["parent_ckad23_campaign_git_blob"]==PARENT_BLOB
         and p["source_generator_sha256"]==SOURCE_SHA,"FROZEN_SOURCE_PINS")
    need(list(p["schedules"])==list(SCHEDULES) and p["seeds"]==list(SEEDS)
         and p["per_case"]["checkpoints"]==list(CHECKPOINTS)
         and p["per_case"]["true_phase_boundaries"]==list(SHIFTS),
         "FROZEN_PROTOCOL")
    need(q["seeds"]==list(SEEDS) and q["source_sha256"]==SOURCE_SHA,
         "PARENT_PROTOCOL")
    return p,q

def classify(detections):
    """Return independent per-boundary recognition, delay, and false alarms.

    One detection per true change can be credited. Additional detections in
    the same true-change window count as false alarms.
    """
    matched={b:None for b in SHIFTS}
    extra=0
    counts=[]
    for event in detections:
        number=event["evidence_count"]-448
        need(8<=number<=192 and number not in counts,"ALARM_ABSOLUTE_COUNT")
        counts.append(number)
        need(sha64(event["event_id"]) and
             fraction(event["score"])>=16,"ALARM_PUBLIC_EVIDENCE")
        group=next((b for b in SHIFTS if b<number<=b+16),None)
        if group is not None and matched[group] is None:
            matched[group]=number-group
        else:extra+=1
    need(counts==sorted(counts),"ALARM_ORDER")
    return {
        "recognized":{str(k):v is not None for k,v in matched.items()},
        "delays":{str(k):v for k,v in matched.items()},
        "false_alarms":extra,
        "stream_relative_counts":counts,
    }

def validate_case(case,p,q):
    need(case["schema"]=="yggdrasil.ckad24.permuted-causal-changes.case.v1"
         and case["classification"]=="DEVELOPMENT_PROOF_ONLY"
         and case["schedule"] in SCHEDULES and case["seed"] in SEEDS,
         "CASE_IDENTITY")
    spec=p["schedules"][case["schedule"]]
    need(case["phase_worlds"]==spec["phase_worlds"] and
         case["source_seed"]==case["seed"]+spec["source_seed_offset"]
         and case["source_parent_sha"]==PARENT_SHA and
         case["original_generator_sha256"]==SOURCE_SHA and
         case["unchanged_parent_campaign_git_blob"]==PARENT_BLOB,
         "CASE_SOURCE_AND_NAMESPACE")
    need(case["scientific_pass"] is False and
         case["accepted_native"] is False and case["deployment"]=="NONE"
         and case["original_source_actions"]==case["protected_first_use"]==
         case["held_updates"]==0,"NO_PROMOTION_OR_FIRST_USE")
    from campaign import stable_sha256
    need(stable_sha256(case)==case["stable_sha256"],"SEMANTIC_SOURCE_HASH")
    z=case["seed_result"]
    need(z["seed"]==case["seed"] and z["source_seed"]==case["source_seed"],
         "PARENT_CASE_SEED")
    need(z["parent_checkpoint_sha256"]==q["parent_pins"][str(z["seed"])] and
         sha64(z["final_checkpoint_sha256"]) and
         0<z["final_checkpoint_bytes"]<=p["budgets"]["max_final_checkpoint_bytes"],
         "PARENT_CHECKPOINT_PIN")
    need(z["final_checkpoint_name"]==f'seed-{case["seed"]}-stream-native.json',
         "CHECKPOINT_FILENAME")
    need(z["cold"]["sha256"]==z["final_checkpoint_sha256"] and
         z["cold"]["readout_sha256"]==z["final_context_sha256"],
         "COLD_CHECKPOINT_CUSTODY")
    need(z["parity"]["mismatches"]==0 and
         z["parity"]["forecasts"]>0 and z["parity"]["decisions"]>0,
         "EXACT_CONTROL_PARITY")
    need([row["count"] for row in z["stream"]]==list(CHECKPOINTS),
         "HELD_SCHEDULE")
    phases=spec["phase_worlds"]
    for row in z["stream"]:
        count=row["count"]
        need(set(row["evaluation"])==set(ARMS),"HELD_CONTROLS")
        for arm,score in row["evaluation"].items():
            need(score["episodes"]==96 and
                 type(score["reward_sum"]) is int and
                 0<=score["reward_sum"]<=96 and
                 all(Fraction(*score[k])>=0 for k in
                     ("transition_brier","terminal_brier","pooled_brier")),
                 "HELD_SCORE_RANGE")
        need(row["evaluation"]["detector_active"]==
             row["evaluation"]["exact_mixture"],
             "EXACT_MIXTURE_PARITY")
        need(row["checkpoint_sha256"] and sha64(row["checkpoint_sha256"]),
             "INTERMEDIATE_CHECKPOINT")
        need(row["context_start"]<=448+count,"DETECTION_NO_FUTURE")
        need([e for e in row["active_detections"]
              if e["evidence_count"]>448+count]==[],"NO_FUTURE_DETECTIONS")
    need(z["stream"][-1]["checkpoint_sha256"]==
         z["final_checkpoint_sha256"],"FINAL_SOURCE_ROUNDTRIP")
    return classify(z["active_detections"])

def aggregate(cases):
    p,q=source_protocol()
    need(len(cases)==len(SEEDS)*len(SCHEDULES),"EXACT_CASE_COUNT")
    table={}
    for case in cases:
        key=(case["schedule"],case["seed"])
        need(key not in table,"DUPLICATE_CASE")
        diag=validate_case(case,p,q)
        table[key]=(case,diag)
    need(set(table)==set(product(SCHEDULES,SEEDS)),
         "MISSING_INDEPENDENT_CASE")
    schedules={}
    all_gates={}
    for name in SCHEDULES:
        family=[table[name,seed] for seed in SEEDS]
        boundary_counts={str(b):sum(z["recognized"][str(b)] for _,z in family)
                         for b in SHIFTS}
        def avg(counts,arm):
            rows=[x["evaluation"][arm]
                  for c,_ in family for x in c["seed_result"]["stream"]
                  if x["count"] in counts]
            return Fraction(sum(z["reward_sum"] for z in rows),
                            sum(z["episodes"] for z in rows))
        held=(64,112,160)
        active=avg(held,"detector_active")
        no_reset=avg(held,"no_reset")
        periodic=avg(held,"periodic32")
        mle=avg(held,"trailing_mle")
        final=avg((192,),"detector_active")
        gates={
          "all_boundaries_detected_in_2_of_3":all(n>=2 for n in boundary_counts.values()),
          "max_three_false_alarms_each":all(z["false_alarms"]<=3 for _,z in family),
          "held_plus_five_points_vs_no_reset":active-no_reset>=Fraction(1,20),
          "held_at_least_periodic32":active>=periodic,
          "held_at_least_trailing64_mle":active>=mle,
          "return_to_invariant_above_80pct":final>=Fraction(4,5),
        }
        metrics={
          "target_held_reward":[active.numerator,active.denominator],
          "gain_vs_no_reset":[(active-no_reset).numerator,(active-no_reset).denominator],
          "gain_vs_periodic32":[(active-periodic).numerator,(active-periodic).denominator],
          "gain_vs_trailing64_mle":[(active-mle).numerator,(active-mle).denominator],
          "final_return_reward":[final.numerator,final.denominator],
        }
        schedules[name]={
          "true_positive_seeds_by_boundary":boundary_counts,
          "per_seed":{str(c["seed_result"]["seed"]):{
             **diag,
             "checkpoint_sha256":c["seed_result"]["final_checkpoint_sha256"],
             "checkpoint_bytes":c["seed_result"]["final_checkpoint_bytes"]
          } for c,diag in family},
          "metrics":metrics,"gates":gates,
          "classification":"DEVELOPMENT_GO" if all(gates.values())
                           else "DEVELOPMENT_NO_GO",
        }
        all_gates[name]=gates
    result={
      "schema":"yggdrasil.ckad24.permuted-causal-changes.sealed.v1",
      "classification":"DEVELOPMENT_GO" if all(all(x.values()) for x in all_gates.values())
                       else "DEVELOPMENT_NO_GO",
      "source_parent_sha":PARENT_SHA,"source_generator_sha256":SOURCE_SHA,
      "parent_ckad23_development_stable_sha256":
         p["parent_ckad23_development_stable_sha256"],
      "schedules":schedules,"frozen_gates":all_gates,
      "new_synthetic_stream_episodes":192*6,
      "random_stream_episodes":192*6,
      "held_episodes":96*13*6,
      "held_policy_rollouts":96*13*6*len(ARMS),
      "original_source_actions":0,"protected_first_use":0,"held_updates":0,
      "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
      "interpretation":"Known synthetic family phase permutations with new exogenous namespaces; source model and detector unchanged. Additional development stress; not independent scientific superiority or unseen real-world transfer.",
    }
    result["stable_sha256"]=sha(canonical(result))
    return result

def load_os(root,os):
    cases=[]
    for schedule,seed in product(SCHEDULES,SEEDS):
        p=root/f"ckad24-{os}-{schedule}-{seed}-proof"/"case-result.json"
        need(p.is_file(),"ARTIFACT_MISSING")
        cases.append(json.loads(p.read_bytes()))
    return cases

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifact-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    one,two=load_os(args.artifact_root,"ubuntu-latest"),load_os(args.artifact_root,"windows-2022")
    for x,y in zip(one,two):
        need(x["stable_sha256"]==y["stable_sha256"],"CROSS_OS_RESULTS")
    result,rep=aggregate(one),aggregate(two)
    need(result==rep,"CROSS_OS_FROZEN_AGGREGATE")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"classification":result["classification"],"gates":result["frozen_gates"],"stable":result["stable_sha256"]},sort_keys=True))

if __name__=="__main__":main()
