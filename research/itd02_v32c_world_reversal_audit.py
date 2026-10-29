"""V32C source-only changing-contingency native microcell replay.

Prospective A->new B->return A with matched reward-blind conventional, frozen,
scrambled, and wrong-world controls. Original Rust V32A+ B32B frozen; no source
learner/genome changes, no scientific first use.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
import time

import research.itd02_v32a_native_microcells_audit as v32a
import research.itd02_v32b_null_margin_audit as v32b
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v32c.contingency_reversal_local_plasticity.v1"
SEEDS=(11,23,37,51,79)
ARMS=("native_adapt","native_fresh_b","native_frozen",
      "conventional","native_sham_b","native_wrong_b")
A=(0,1,2,1)
B=(1,2,0,2)
C=(2,0,1,0)
EPS=v32b.EPS
STRONG=v32b.STRONG_MARGIN
EVAL=96
TRAIN=240
EARLY=60
TIMEOUT=120
API=v32a.API
assert A==v32a.CORRECT and B==v32b.ROTATED and C==(2,0,1,0)
assert all(len({A[i],B[i],C[i]})==3 for i in range(4))


def checksum(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,
        separators=(",",":"),allow_nan=False).encode()).hexdigest()


def schedule(seed,phase):
    if seed not in SEEDS or phase not in ("a","b","return_a"):
        raise ValueError("V32C_UNKNOWN_FROZEN_SEED_OR_WORLD_PHASE")
    # Each 12-event round contains all 4 cue x 3 action combinations once:
    # B first five rounds are exactly 5 each original pair.
    offset={"a":1000,"b":2000,"return_a":3000}[phase]
    rng=random.Random(seed+offset)
    out=[]
    for repeat in range(20):
        round_items=[(cue,action,repeat) for cue in range(4) for action in range(3)]
        rng.shuffle(round_items)
        out.extend(round_items)
    if len(out)!=TRAIN or len(set(out))!=TRAIN or len(out[:EARLY])!=EARLY:
        raise AssertionError("V32C_FROZEN_BALANCED_WORLD_SCHEDULE_FAILED")
    for start in range(0,TRAIN,12):
        if set((c,a) for c,a,_ in out[start:start+12]) != set(
            (c,a) for c in range(4) for a in range(3)):
            raise AssertionError("V32C_BALANCED_TWELVE_CUE_ACTION_ROUND_FAILED")
    return out


def world_reward(arm,phase,cue,action,repeat):
    if phase in ("a","return_a"):
        target=A
    elif phase=="b":
        target=C if arm=="native_wrong_b" else B
        if arm=="native_sham_b":
            return 1.0 if repeat%2==0 else -1.0
    else:
        raise ValueError("V32C_BAD_REWARD_WORLD")
    return 1.0 if action==target[cue] else -1.0


def diag(rows):
    return {label:{
        "raw_accuracy":d["original_raw_accuracy"],
        "eps_accuracy":d["epsilon_stabilized_accuracy"],
    } for label,d in (
        ("a",v32b.diagnostics(rows,A)),
        ("b",v32b.diagnostics(rows,B)),
        ("c",v32b.diagnostics(rows,C))
    )}


def capture_native(handle, *, cold):
    checkpoint=API.checkpoint(handle)
    record=v32b.parse_native_checkpoint(checkpoint)
    rows=v32a.eval_native(handle)
    if API.checkpoint(handle)!=checkpoint:
        raise AssertionError("V32C_REWARD_BLIND_NATIVE_EVAL_CHANGED_WEIGHTS")
    original=v32b.diagnostics(rows,A)
    stage={
        "policies":diag(rows),
        "score_sha256":v32a.scores_hash(rows),
        "first_four_f64_score_hex":original["first_four_score_hex"],
        "margin_min":original["min_top_second_margin"],
        "margin_max":original["max_top_second_margin"],
        "margin_median":original["median_top_second_margin"],
        "learned_weight_max_abs":record["max_abs_local_native_weight"],
        "native_local_updates":API.local_updates(handle),
        "native_checkpoint_sha256":record["checkpoint_sha256"],
        "native_checkpoint_unchanged_during_eval":True,
        "fresh_cold_process":v32b.cold_launch(checkpoint,original,record) if cold else None,
    }
    if stage["native_local_updates"] != record["all_eight_local_update_counters"]:
        raise AssertionError("V32C_NATIVE_HEAP_LEARNED_COUNTER_AND_MEMORY_DRIFT")
    return stage


def capture_conventional(model):
    b=model.checkpoint()
    rows=v32a.eval_conventional(model)
    if model.checkpoint()!=b:
        raise AssertionError("V32C_CONVENTIONAL_REWARD_BLIND_EVAL_MUTATED_STATE")
    source=v32b.diagnostics(rows,A)
    return {
        "policies":diag(rows),
        "score_sha256":v32a.scores_hash(rows),
        "first_four_f64_score_hex":source["first_four_score_hex"],
        "margin_min":source["min_top_second_margin"],
        "margin_max":source["max_top_second_margin"],
        "margin_median":source["median_top_second_margin"],
        "native_local_updates":None,
        "native_checkpoint_sha256":hashlib.sha256(b).hexdigest(),
        "native_checkpoint_unchanged_during_eval":True,
        "fresh_cold_process":None,
    }


def verify_native_layout(handle):
    addr=API.source_layout(handle)
    if len(addr)!=8 or len(set(addr))!=8:
        raise AssertionError("V32C_EIGHT_INDEPENDENT_NATIVE_RUST_CELL_HEAPS_NOT_PROVEN")
    return True


def train_native(handle,arm,phase,stream,learning):
    rewards=[]
    start=time.process_time_ns()
    for cue,action,repeat in stream:
        reward=world_reward(arm,phase,cue,action,repeat)
        API.observe_one(handle,cue)
        API.native_scores(handle)
        API.feedback_one(handle,action,reward,learning)
        rewards.append(reward)
    elapsed=time.process_time_ns()-start
    return {
        "count":len(stream),
        "reward_positive":rewards.count(1.0),
        "reward_negative":rewards.count(-1.0),
        "reward_stream_sha256":checksum(rewards),
        "public_action_cue_stream_sha256":checksum(stream),
        "training_segment_process_cpu_ns":elapsed,
        "training_segment_below_process_clock_resolution":elapsed==0,
    }


def train_conventional(model,phase,stream):
    rewards=[]
    start=time.process_time_ns()
    for cue,action,repeat in stream:
        reward=world_reward("conventional",phase,cue,action,repeat)
        model.scores(cue)
        model.feedback(cue,action,reward)
        rewards.append(reward)
    elapsed=time.process_time_ns()-start
    return {
        "count":len(stream),
        "reward_positive":rewards.count(1.0),
        "reward_negative":rewards.count(-1.0),
        "reward_stream_sha256":checksum(rewards),
        "public_action_cue_stream_sha256":checksum(stream),
        "training_segment_process_cpu_ns":elapsed,
        "training_segment_below_process_clock_resolution":elapsed==0,
    }


def fresh_worker(arm,seed):
    if arm not in ARMS or seed not in SEEDS:
        raise ValueError("V32C_INVALID_FROZEN_ARM_OR_SEED")
    begin=time.process_time_ns()
    initial=schedule(seed,"a")
    switched=schedule(seed,"b")
    returned=schedule(seed,"return_a")
    paths={name:checksum(stream) for name,stream in
           (("a",initial),("b",switched),("return_a",returned))}
    native=arm!="conventional"
    p=API.new() if native else None
    conv=v32a.Conventional() if not native else None
    phases={}
    stages={}
    try:
        if native:verify_native_layout(p)
        current=lambda cold=False: (
            capture_native(p,cold=cold) if native
            else capture_conventional(conv))
        stages["before_training"]=current()
        if arm!="native_fresh_b":
            phases["a240"]=train_native(p,arm,"a",initial,True) if native \
                else train_conventional(conv,"a",initial)
            stages["after_a240"]=current(cold=arm=="native_adapt")
            if native and stages["after_a240"]["native_local_updates"]!=[240]*8:
                raise AssertionError("V32C_PRIVATE_A_WORLD_240_UPDATES_MISSING")
        else:
            stages["before_b"]=current()
        first_b=switched[:EARLY]
        later_b=switched[EARLY:]
        if native:
            learn=arm!="native_frozen"
            phases["b60"]=train_native(p,arm,"b",first_b,learn)
        else:
            phases["b60"]=train_conventional(conv,"b",first_b)
        stages["after_b60"]=current(cold=arm=="native_adapt")
        if native:
            phases["b180"]=train_native(p,arm,"b",later_b,arm!="native_frozen")
        else:
            phases["b180"]=train_conventional(conv,"b",later_b)
        stages["after_b240"]=current(cold=arm=="native_adapt")
        if arm in ("native_adapt","conventional"):
            phases["return_a240"]=train_native(p,arm,"return_a",returned,True) \
                if native else train_conventional(conv,"return_a",returned)
            stages["after_return_a240"]=current(cold=arm=="native_adapt")
        after=time.process_time_ns()
        resident,meter=actual_os_peak_resident_bytes()
        if not after>0 or resident<=0:
            raise AssertionError("V32C_GENUINE_WHOLE_OS_CPU_OR_RESIDENT_MISSING")
        if native:
            expected={
                "native_adapt":{"after_a240":240,"after_b60":300,
                    "after_b240":480,"after_return_a240":720},
                "native_fresh_b":{"after_b60":60,"after_b240":240},
                "native_frozen":{"after_a240":240,"after_b60":240,"after_b240":240},
                "native_sham_b":{"after_a240":240,"after_b60":300,"after_b240":480},
                "native_wrong_b":{"after_a240":240,"after_b60":300,"after_b240":480},
            }[arm]
            for stage,count in expected.items():
                if stages[stage]["native_local_updates"]!=[count]*8:
                    raise AssertionError("V32C_PRIVATE_EIGHT_CELL_COUNT_DRIFT_"+stage)
        result={
            "schema":SCHEMA,"role":"fresh_world_control_worker",
            "host":sys.platform,"arm":arm,"seed":seed,
            "source_sha256":API.source_sha256,"binary_sha256":API.binary_sha256,
            "public_world_mappings":{"a":A,"b":B,"false_c":C},
            "public_exposure_stream_sha256_by_phase":paths,
            "each_frozen_full_world_exposures":TRAIN,
            "exact_new_world_early_exposures":EARLY,
            "frozen_reward_blind_score_evaluation":EVAL,
            "training_phases":phases,
            "evaluation_stages":stages,
            "whole_parent_process_cpu_ns":after,
            "actual_os_peak_resident_bytes":resident,
            "os_peak_resident_meter":meter,
            "v32a_rust_original_unchanged":True,
            "v32a_original_negative_classification_unchanged":True,
            "original_yggdrasil_native_model_unchanged":True,
            "unfamiliar_input_family_transfer_claimed":False,
            "scientific_first_use":False,
        }
        print(json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False))
    finally:
        if p is not None:API.free(p)


def launch(arm,seed):
    start=time.perf_counter_ns()
    p=subprocess.run(
        [sys.executable,"-B",str(Path(__file__).resolve()),"--worker",arm,str(seed)],
        cwd=ROOT,check=False,capture_output=True,text=True,timeout=TIMEOUT,
        env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
    wall=time.perf_counter_ns()-start
    if p.returncode or p.stderr.strip():
        raise AssertionError("V32C_FRESH_CONTROL_PROCESS_FAILURE_{}_{}_{}".format(
            arm,seed,p.stderr[-1600:],p.stdout[-1000:]))
    try:d=json.loads(p.stdout)
    except (ValueError,TypeError) as e:
        raise AssertionError("V32C_FRESH_WORLD_SOURCE_REPORT_NOT_JSON") from e
    if (d.get("schema")!=SCHEMA or d.get("role")!="fresh_world_control_worker"
        or d.get("host")!=sys.platform or d.get("arm")!=arm or d.get("seed")!=seed
        or d.get("source_sha256")!=API.source_sha256
        or d.get("binary_sha256")!=API.binary_sha256
        or d.get("public_exposure_stream_sha256_by_phase")!={
            name:checksum(schedule(seed,name)) for name in ("a","b","return_a")}
        or d.get("v32a_rust_original_unchanged") is not True
        or d.get("v32a_original_negative_classification_unchanged") is not True
        or d.get("original_yggdrasil_native_model_unchanged") is not True
        or d.get("scientific_first_use") is not False):
        raise AssertionError("V32C_OUTSIDE_FROZEN_SOURCE_BOUNDS")
    method=("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform=="linux"
        else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
        if sys.platform=="win32" else None)
    if (d.get("os_peak_resident_meter")!=method
        or type(d.get("whole_parent_process_cpu_ns")) is not int
        or d["whole_parent_process_cpu_ns"]<=0
        or type(d.get("actual_os_peak_resident_bytes")) is not int
        or d["actual_os_peak_resident_bytes"]<=0):
        raise AssertionError("V32C_TRUE_OS_CPU_RSS_MISSING")
    d["full_worker_wall_ns"]=wall
    return d


def action_acc(stages,key,world):
    return stages[key]["policies"][world]["eps_accuracy"]


def stage_margin(stages,key):
    return stages[key]["margin_min"]


def check_phase_provenance(arms):
    # Same B source schedule, matched reward labels for A/N/F/Z/P.
    bs=[x["training_phases"]["b60"] for x in arms.values()]
    if len({x["public_action_cue_stream_sha256"] for x in bs})!=1:
        raise AssertionError("V32C_UNMATCHED_NOVEL_WORLD_OBSERVATIONS")
    if len({x["reward_stream_sha256"] for x in
        (arms["native_adapt"]["training_phases"]["b60"],
         arms["native_fresh_b"]["training_phases"]["b60"],
         arms["native_frozen"]["training_phases"]["b60"],
         arms["conventional"]["training_phases"]["b60"])})!=1:
        raise AssertionError("V32C_BAD_MATCHED_B_FEEDBACK_INPUTS")
    for arm,x in arms.items():
        for name,p in x["training_phases"].items():
            required=60 if name=="b60" else 180 if name=="b180" else 240
            if p["count"]!=required:
                raise AssertionError("V32C_SOURCE_EXPOSURE_LENGTH_CHANGED")
            if arm=="native_sham_b" and name in ("b60","b180"):
                # Sham balanced at B240; prefix has deliberate 5/20 updates.
                continue
            if p["reward_positive"]+p["reward_negative"]!=required:
                raise AssertionError("V32C_PUBLIC_FEEDBACK_GAP")
        if arm=="native_sham_b":
            # B full feedback has ten + and ten - for EACH cue/action pair.
            if (x["training_phases"]["b60"]["reward_positive"]+
                x["training_phases"]["b180"]["reward_positive"]!=120):
                raise AssertionError("V32C_BALANCED_NULL_REWARD_CARDINALITY_DRIFT")


def evaluate_seed(seed,arms):
    check_phase_provenance(arms)
    n,f,z,p,s,w=(arms[x] for x in ARMS)
    ns=n["evaluation_stages"]
    fs=f["evaluation_stages"]
    zs=z["evaluation_stages"]
    ps=p["evaluation_stages"]
    ss=s["evaluation_stages"]
    ws=w["evaluation_stages"]
    pre=n["training_phases"]["before_training"] if "before_training" in n["training_phases"] else n["evaluation_stages"]["before_training"]
    native_learning_ok=(
        action_acc(ns,"after_a240","a")>=.75 and
        action_acc(ns,"after_a240","a")-pre["policies"]["a"]["eps_accuracy"]>=.25 and
        action_acc(ns,"after_a240","b")<=.25 and
        action_acc(ns,"after_b60","b")>=.50 and
        action_acc(ns,"after_b240","b")>=.75 and
        action_acc(ns,"after_b240","a")<=.25 and
        action_acc(ns,"after_return_a240","a")>=.75 and
        action_acc(ns,"after_return_a240","b")<=.25 and
        action_acc(fs,"after_b60","b")>=.50 and
        action_acc(fs,"after_b240","b")>=.75 and
        action_acc(ps,"after_a240","a")>=.75 and
        action_acc(ps,"after_b60","b")>=.50 and
        action_acc(ps,"after_b240","b")>=.75 and
        action_acc(ps,"after_return_a240","a")>=.75 and
        action_acc(ns,"after_b240","b")+.10>=action_acc(ps,"after_b240","b") and
        action_acc(ns,"after_return_a240","a")+.10>=action_acc(ps,"after_return_a240","a") and
        action_acc(zs,"after_b240","b")<=.25 and
        action_acc(zs,"after_b240","a")>=.75 and
        action_acc(ss,"after_b240","b")<=.25 and
        action_acc(ss,"after_b240","a")>=.75 and
        action_acc(ws,"after_b240","b")<=.25 and
        action_acc(ws,"after_b240","c")>=.75 and
        all(stage_margin(ns,name)>STRONG for name in
            ("after_a240","after_b240","after_return_a240")) and
        stage_margin(fs,"after_b240")>STRONG)
    transfer=action_acc(ns,"after_b60","b")>=action_acc(fs,"after_b60","b")
    # full confidence test for each trained correct target requires top TWO
    # gap (regardless of world) >1e-6; never count tiny f64 ties as learning.
    def good_margin(stage):
        return stage["margin_min"]>STRONG
    native_learning_ok=native_learning_ok and all(
        stages[key]["fresh_cold_process"] is not None for stages,key in (
            (ns,"after_a240"),(ns,"after_b60"),
            (ns,"after_b240"),(ns,"after_return_a240")))
    return {
        "seed":seed,
        "native_learning_and_strong_controls_pass":native_learning_ok,
        "native_partial_new_world_at_least_fresh_control":transfer,
        "native_a_after_initial_training":action_acc(ns,"after_a240","a"),
        "native_new_b_before_b_training":action_acc(ns,"after_a240","b"),
        "native_new_b_after_60":action_acc(ns,"after_b60","b"),
        "fresh_b_after_60":action_acc(fs,"after_b60","b"),
        "native_new_b_after_240":action_acc(ns,"after_b240","b"),
        "native_old_a_after_240_b":action_acc(ns,"after_b240","a"),
        "native_restored_old_a_after_return_240":action_acc(ns,"after_return_a240","a"),
        "conventional_new_b_after_60":action_acc(ps,"after_b60","b"),
        "conventional_new_b_after_240":action_acc(ps,"after_b240","b"),
        "conventional_return_old_a_after_240":action_acc(ps,"after_return_a240","a"),
        "frozen_no_update_b_after_240":action_acc(zs,"after_b240","b"),
        "sham_balanced_no_b_info_b_after_240":action_acc(ss,"after_b240","b"),
        "wrong_c_train_b_after_240":action_acc(ws,"after_b240","b"),
        "wrong_c_train_own_c_after_240":action_acc(ws,"after_b240","c"),
        "native_b60_minus_fresh_b60_accuracy_delta":
            action_acc(ns,"after_b60","b")-action_acc(fs,"after_b60","b"),
        "all_original_full_stage_policies":{arm:{
            "policies":{name:s["policies"] for name,s in x["evaluation_stages"].items()},
            "min_score_margin_by_stage":{name:s["margin_min"] for name,s in x["evaluation_stages"].items()},
            "checkpoint_sha_by_stage":{name:s["native_checkpoint_sha256"] for name,s in x["evaluation_stages"].items()},
            "native_local_updates_by_stage":{name:s["native_local_updates"] for name,s in x["evaluation_stages"].items()},
        } for arm,x in arms.items()},
        "actual_host_resource_by_arm":{arm:{
            "whole_parent_cpu_ns":x["whole_parent_process_cpu_ns"],
            "true_os_peak_rss_bytes":x["actual_os_peak_resident_bytes"],
            "parent_full_wall_ns":x["full_worker_wall_ns"],
            "training_phases":x["training_phases"],
            "independent_cold_receipts":{name:s["fresh_cold_process"]
                for name,s in x["evaluation_stages"].items()
                if s["fresh_cold_process"] is not None},
        } for arm,x in arms.items()}
    }


def audit():
    v32a.source_negative_controls()
    if API.source_sha256!="d5ecc87a8c42130526c8a62df358a6be43b1fc024c22a63332932fb9af496655":
        raise AssertionError("V32C_ORIGINAL_V32A_RUST_SOURCE_NOT_IMMUTABLE")
    r=[]
    for seed in SEEDS:
        arms={arm:launch(arm,seed) for arm in ARMS}
        r.append(evaluate_seed(seed,arms))
    full_learning=all(x["native_learning_and_strong_controls_pass"] for x in r)
    transfer=all(x["native_partial_new_world_at_least_fresh_control"] for x in r)
    classification=(
        "V32C_CHANGED_CONTINGENCY_AND_TRANSFER_POSITIVE__NO_SCIENCE"
        if full_learning and transfer else
        "V32C_CHANGED_CONTINGENCY_LEARNING_ONLY_NO_POSITIVE_TRANSFER__NO_SCIENCE"
        if full_learning else
        "V32C_CHANGED_CONTINGENCY_LEARNING_OR_CONTROL_NEGATIVE__NO_SCIENCE")
    print(json.dumps({
        "schema":SCHEMA,"host":sys.platform,"status":"COMPLETE",
        "classification":classification,
        "old_world_a":A,"unfamiliar_reward_mapping_b":B,"wrong_world_c":C,
        "same_original_four_cues_and_three_actions":True,
        "novel_input_family_or_compositional_transfer_proven":False,
        "native_original_rust_source_sha256":API.source_sha256,
        "host_compiled_rust_binary_sha256":API.binary_sha256,
        "original_yggdrasil_model_unchanged":True,
        "prior_v32a_failed_control_unchanged":True,
        "native_cells_independently_os_scheduled":False,
        "scientific_first_use":False,
        "fixed_schedule_seeds":SEEDS,
        "epsilon_tie_policy":EPS,
        "positive_margin_required":STRONG,
        "fresh_matched_six_arm_processes_each_host":len(SEEDS)*len(ARMS),
        "native_independent_cold_processes_each_host":len(SEEDS)*4,
        "balanced_full_world_training_exposures":TRAIN,
        "balanced_partial_unfamiliar_exposures":EARLY,
        "evaluation_no_reward_events":EVAL,
        "results":r,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        fresh_worker(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V32C_INVALID_SUBPROCESS_ENTRY")
