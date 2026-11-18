"""CKAD23: independently reconstruct frozen qualification from executed shards.

The audit makes no source interventions and has no access to private episode
states or future outcomes. Independently checks matched held outcomes,
change-count accounting, source/checkpoint pins, negative controls and seeds.
"""
import argparse
from fractions import Fraction
from itertools import product
from hashlib import sha256
import json
from pathlib import Path
import sys

if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"CKAD-22"
SOURCE_SHA="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
PARENT_SHA="f04cfcac2aa07806a6b942d968119de87bfb6aaf"
PREVIOUS_SHA="4b20ef3b9229eddfd509e5897e6aa8f8d5226288ab331c4a98f8a7bc46fbccc2"
SEEDS=(101,202,303)
COUNTS=tuple(range(0,193,16))
CHANGE=(48,96,144)
PHASES=(("invariant",0),("terminal_switch",1),
        ("invariant",1),("invariant",0))
ARMS=("detector_active","detector_random","no_reset","periodic32",
      "pooled_replay","trailing_mle","frozen_ckad22","exact_monitor")

def canonical(d):
    return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")

def digest(raw):
    return sha256(raw).hexdigest()

def need(b,reason):
    if not b:raise ValueError("CKAD23_AUDIT_"+reason)

def valid_sha(s):
    return type(s) is str and len(s)==64 and all(q in "0123456789abcdef" for q in s)

def ratio(f):
    return [f.numerator,f.denominator]

def stable(d):
    def normalized(v):
        if isinstance(v,dict):
            return {k:normalized(z) for k,z in v.items()
                    if k not in ("source_candidate_sha","stable_sha256",
                                 "whole_wall_seconds","wall_seconds",
                                 "cpu_seconds","peak_rss_bytes")}
        if isinstance(v,list):return [normalized(z) for z in v]
        return v
    return digest(canonical(normalized(d)))

def parent_pins():
    d=json.loads((PARENT/"result.json").read_bytes())
    need(d["stable_sha256"]==PREVIOUS_SHA and
         d["source_candidate_sha"]=="de1c3daac160c0ef24f352ce238558b1356c06dd",
         "PARENT_REPORT_PIN")
    return {z["seed"]:z["sha256"] for z in d["final_checkpoints"]}

def phase(count):
    return PHASES[0 if count==0 else (count-1)//48]

def false_alarms(rows):
    return sum(not any(b+1<=event["count"]-448<=b+16 for b in CHANGE)
               for event in rows)

def validate_seed(item,pins):
    seed=item["seed"]
    need(seed in SEEDS and item["source_seed"]==seed+14000,"SEED_ID")
    need(item["original_checkpoint_sha256"]==pins[seed],"PARENT_CHECKPOINT")
    need(valid_sha(item["final_checkpoint_sha256"]) and
         item["final_checkpoint_bytes"]>0 and
         item["final_checkpoint_name"]==f"seed-{seed}-stream-native.json",
         "FINAL_CHECKPOINT")
    need(item["legacy_checkpoint_retained"] is True and
         item["held_updates"]==0 and
         item["first_public_actions"]==item["second_public_actions"]==
         item["random_first_public_actions"]==item["random_second_public_actions"]==192,
         "STREAM_ACTION_CUSTODY")
    need(type(item["checkpoints"]) is list and
         [c["count"] for c in item["checkpoints"]]==list(COUNTS),
         "HELD_CHECKPOINTS")
    prior=[]
    for row in item["detected_boundaries"]:
        need(valid_sha(row["identifier"]) and type(row["count"]) is int and
             456<=row["count"]<=640 and row["count"] not in prior,
             "DETECTION_ID_OR_BOUNDS")
        prior.append(row["count"])
        v=row["score"]
        need(type(v) is list and len(v)==2 and
             all(type(n) is int and n>0 for n in v) and
             Fraction(*v)>=16,"DETECTION_SCORE")
    need(prior==sorted(prior) and
         item["false_alarms"]==false_alarms(item["detected_boundaries"]),
         "FALSE_ALARM_ACCOUNTING")
    for count,record in zip(COUNTS,item["checkpoints"]):
        need(record["held_cohort"]==f"ckad23-held-{count}" and
             record["source_phase_evaluator_only"]==list(phase(count)),
             "HELD_SOURCE_PROVENANCE")
        need(valid_sha(record["checkpoint_sha256"]) and
             0<record["checkpoint_bytes"]<5*1024*1024 and
             record["context_candidates"]>=1,"HELD_SAVED_MODEL")
        need(record["active_stream"]["stream_start"]==448 and
             type(record["active_stream"]["detections"]) is list,
             "STORED_STREAM_SCOPE")
        stream_dets=record["active_stream"]["detections"]
        need(all(x["count"]<=448+count for x in stream_dets) and
             item["detected_boundaries"][:len(stream_dets)]==stream_dets,
             "DETECTION_IS_CAUSAL")
        scores=record["evaluation"]
        need(type(scores) is dict and set(scores)==set(ARMS),"HELD_ARM_SCOPE")
        for arm in ARMS:
            result=scores[arm]
            need(result["episodes"]==96 and
                 type(result["reward_sum"]) is int and
                 0<=result["reward_sum"]<=96 and
                 valid_sha(result["trace_sha256"]),"HELD_OUTCOME")
            for name in ("transition_brier","terminal_brier","pooled_brier"):
                q=Fraction(*result[name])
                need(0<=q<=1,"HELD_BRIER")
        need(scores["detector_active"]==scores["exact_monitor"],
             "HELD_CONVENTIONAL_PARITY")
    need(item["checkpoints"][-1]["checkpoint_sha256"]==
         item["final_checkpoint_sha256"] and
         item["checkpoints"][-1]["checkpoint_bytes"]==
         item["final_checkpoint_bytes"],"FINAL_SOURCE_MATCH")
    p=item["parity"]
    need(p["source_outcomes"]==p["detector_boundaries_checked"]==192
         and p["readout_checks"]==13 and p["forecast_queries"]>=13*40,
         "ONLINE_PARITY_COUNTER")
    return item

def aggregate(shards):
    need(type(shards) is list and len(shards)==3,"SEED_COUNT")
    pins=parent_pins()
    ordered=sorted(shards,key=lambda d:d["seeds"][0]["seed"])
    seen=[]
    receipts=[]
    source_shas=set()
    for shard in ordered:
        need(shard["schema"]=="yggdrasil.ckad23.unsignaled-context-development.result.v1"
             and shard["classification"]=="PARTIAL_SOURCE_PROOF" and
             shard["scientific_pass"] is False and
             shard["accepted_native"] is False and shard["deployment"]=="NONE",
             "SHARD_NO_PROMOTION")
        need(shard["source_parent"]==PARENT_SHA and
             shard["source_sha256"]==SOURCE_SHA and
             shard["scope"]=={
                 "original_source_actions":0,"protected_first_use":0,
                 "held_updates":0,"stream_episodes":192,
                 "held_episodes":96*13,"held_policy_rollouts":96*13*len(ARMS),
             },"SOURCE_BUDGET")
        need(stable(shard)==shard["stable_sha256"],"SOURCE_REPLAY_HASH")
        need(len(shard["seeds"])==1,"ONE_SEED_PER_SHARD")
        source_shas.add(shard["source_candidate_sha"])
        item=validate_seed(shard["seeds"][0],pins)
        receipts.append(item)
        seen.append(item["seed"])
    need(seen==list(SEEDS) and len(source_shas)==1,"EXACT_SEED_AND_CODE_IDENTITY")

    def mean(checkpoints,arm):
        rows=[x["evaluation"][arm] for seed in receipts for x in seed["checkpoints"]
              if x["count"] in checkpoints]
        return Fraction(sum(r["reward_sum"] for r in rows),
                        sum(r["episodes"] for r in rows))
    comparison=(64,112,160)
    active=mean(comparison,"detector_active")
    no_reset=mean(comparison,"no_reset")
    periodic=mean(comparison,"periodic32")
    mle=mean(comparison,"trailing_mle")
    final=mean((192,),"detector_active")
    gates={
       "gain_vs_no_reset":active-no_reset>=Fraction(1,20),
       "at_least_periodic32":active>=periodic,
       "at_least_trailing64_mle":active>=mle,
       "returning_invariant_reward":final>=Fraction(4,5),
       "per_seed_false_alarms":all(s["false_alarms"]<=3 for s in receipts),
    }
    metrics={
       "target_held_reward":ratio(active),
       "target_gain_vs_no_reset":ratio(active-no_reset),
       "target_gain_vs_periodic32":ratio(active-periodic),
       "target_gain_vs_trailing64_mle":ratio(active-mle),
       "final_invariant_reward":ratio(final),
    }
    per_seed={
       str(s["seed"]):{
           "detected_boundaries":s["detected_boundaries"],
           "false_alarms":s["false_alarms"],
           "acquired_reward":s["acquired_reward"],
           "final_checkpoint_sha256":s["final_checkpoint_sha256"],
       } for s in receipts
    }
    result={
      "schema":"yggdrasil.ckad23.unsignaled-context-development.sealed.v1",
      "classification":"DEVELOPMENT_GO" if all(gates.values()) else "DEVELOPMENT_NO_GO",
      "source_parent":PARENT_SHA,
      "source_sha256":SOURCE_SHA,
      "source_candidate_sha":next(iter(source_shas)),
      "parent_ckad22_stable_sha256":PREVIOUS_SHA,
      "parent_checkpoint_sha256":{str(k):v for k,v in pins.items()},
      "development_gates":gates,"development_metrics":metrics,
      "seeds":per_seed,
      "held_score_by_checkpoint":{
          str(count):{arm:sum(s["checkpoints"][count//16]["evaluation"][arm]["reward_sum"]
                              for s in receipts) for arm in ARMS}
          for count in COUNTS
      },
      "matched_held_episodes":96*13*3,
      "held_policy_rollouts":96*13*3*len(ARMS),
      "stream_public_episodes":192*3,
      "random_probe_public_episodes":192*3,
      "max_stream_episodes_after_parent":640,
      "original_source_actions":0,"protected_first_use":0,"held_updates":0,
      "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    }
    result["stable_sha256"]=digest(canonical(result))
    return result

def load_os(root,os_name):
    records=[]
    for seed in SEEDS:
        directory=root/f"ckad23-{os_name}-{seed}-proof"
        p=directory/"result.json"
        need(p.is_file(),"OS_ARTIFACT_MISSING")
        records.append(json.loads(p.read_text()))
    return records

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--artifact-root",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    linux=load_os(args.artifact_root,"ubuntu-latest")
    windows=load_os(args.artifact_root,"windows-2022")
    for a,b in zip(linux,windows):
        need(a["stable_sha256"]==b["stable_sha256"],"CROSS_OS_SHA_MISMATCH")
        need(stable(a)==stable(b),"CROSS_OS_SOURCE_MISMATCH")
        need(a["seeds"][0]["final_checkpoint_sha256"]==
             b["seeds"][0]["final_checkpoint_sha256"],"CROSS_OS_CHECKPOINT_MISMATCH")
    one,two=aggregate(linux),aggregate(windows)
    need(one==two,"CROSS_OS_AGGREGATE")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(one,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"classification":one["classification"],
                      "development_gates":one["development_gates"],
                      "development_metrics":one["development_metrics"],
                      "stable_sha256":one["stable_sha256"]},sort_keys=True))

if __name__=="__main__":main()
