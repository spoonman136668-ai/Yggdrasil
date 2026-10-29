"""V32B frozen numerical-tie/independent-wrong-feedback diagnostics.

Uses V32A's EXACT native Rust model/FFI/source. No reward/weight/learning
implementation changes. This audit CANNOT repair or promote failed V32A.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import struct
import subprocess
import sys
import tempfile
import time

import research.itd02_v32a_native_microcells_audit as v32a
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v32b.null_margin_diagnostic.v1"
SEEDS = (11, 23, 37, 51, 79)
ARMS = ("native_true", "conventional_true", "native_no_learning",
        "balanced_null", "rotated_action", "shifted_cue")
EPS = 1e-10
STRONG_MARGIN = 1e-6
TRAIN = 240
EVAL = 96
EXPECTED_RAW_BALANCED = {
    11: .25, 23: .75, 37: .25, 51: 0.0, 79: .25,
}
MAX_WORKER_SECONDS = 100
CORRECT = (0, 1, 2, 1)
ROTATED = tuple((a+1)%3 for a in CORRECT)
SHIFTED = tuple(CORRECT[(i+1)%4] for i in range(4))
API = v32a.API
assert CORRECT == v32a.CORRECT
assert ROTATED == (1, 2, 0, 2)
assert SHIFTED == (1, 2, 1, 0)
assert all(a != b and a != c for a,b,c in zip(CORRECT,ROTATED,SHIFTED))


def digest(obj):
    return hashlib.sha256(json.dumps(
        obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()


def tolerant_action(row):
    if (len(row) != 3 or any(type(v) is not float or not math.isfinite(v) for v in row)):
        raise AssertionError("V32B_INVALID_FULL_PRECISION_NATIVE_SCORE")
    winner = 0
    for i in (1, 2):
        if row[i] > row[winner] + EPS:
            winner = i
    return winner


def diagnostics(rows, mapping):
    if len(rows) != EVAL or len(mapping) != 4:
        raise AssertionError("V32B_WRONG_REWARD_BLIND_EVALUATION_LENGTH")
    raw = []
    stable = []
    margins = []
    hex_examples = []
    bits_examples = []
    max_abs = 0.0
    for i,row in enumerate(rows):
        if len(row)!=3 or any(not math.isfinite(v) for v in row):
            raise AssertionError("V32B_MALFORMED_NONFINITE_ACTION_READOUT")
        ranked = sorted(row,reverse=True)
        margin = ranked[0] - ranked[1]
        margins.append(margin)
        if margin < 0 or not math.isfinite(margin):
            raise AssertionError("V32B_INVALID_NATIVE_SCORE_MARGIN")
        raw.append(max(range(3),key=lambda a:row[a]))
        stable.append(tolerant_action(row))
        max_abs = max(max_abs,*(abs(v) for v in row))
        if i < 4:
            hex_examples.append([float(v).hex() for v in row])
            bits_examples.append([struct.pack(">d",v).hex() for v in row])
    return {
        "original_raw_accuracy": sum(a == mapping[i%4] for i,a in enumerate(raw))/EVAL,
        "epsilon_stabilized_accuracy": sum(a == mapping[i%4] for i,a in enumerate(stable))/EVAL,
        "raw_actions_first_four": raw[:4],
        "epsilon_actions_first_four": stable[:4],
        "first_four_score_hex":hex_examples,
        "first_four_f64_bits_be":bits_examples,
        "all_raw_score_sha256":v32a.scores_hash(rows),
        "max_abs_score":max_abs,
        "max_top_second_margin":max(margins),
        "min_top_second_margin":min(margins),
        "median_top_second_margin":statistics.median(margins),
        "near_tie_decisions_1e_minus_10":sum(x<=EPS for x in margins),
        "tie_cutoff_abs":EPS,
    }


def parse_native_checkpoint(payload):
    if type(payload) is not bytes or len(payload)!=856 or payload[:8]!=b"V32AMIC1":
        raise AssertionError("V32B_NATIVE_856_BYTE_ORIGINAL_CHECKPOINT_DRIFT")
    at=16
    updates=[]
    weights=[]
    all_bits=[]
    for i in range(8):
        updates.append(struct.unpack_from("<Q",payload,at)[0])
        at+=8
        row=[]
        for j in range(12):
            val=struct.unpack_from("<d",payload,at)[0]
            if not math.isfinite(val) or abs(val)>8:
                raise AssertionError("V32B_NONFINITE_PRIVATE_LOCAL_LEARNING_WEIGHT")
            row.append(val)
            all_bits.append(payload[at:at+8].hex())
            at+=8
        weights.append(row)
    if at!=848 or len(all_bits)!=96:
        raise AssertionError("V32B_SOURCE_NATIVE_CELL_PARAMETER_NUMBER_CHANGED")
    return {
        "all_eight_local_update_counters":updates,
        "all_96_native_weight_f64_hex_little_endian":all_bits,
        "max_abs_local_native_weight":max(abs(x) for row in weights for x in row),
        "num_weights_gt_epsilon":sum(abs(x)>EPS for row in weights for x in row),
        "checkpoint_sha256":hashlib.sha256(payload).hexdigest(),
        "total_rust_learning_feedback_calls":struct.unpack_from("<Q",payload,8)[0],
    }


def reward_for(arm,cue,action,repeat):
    if arm in ("native_true","conventional_true","native_no_learning"):
        target=CORRECT[cue]
        return 1.0 if action == target else -1.0
    if arm=="balanced_null":
        return 1.0 if repeat%2==0 else -1.0
    if arm=="rotated_action":
        return 1.0 if action==ROTATED[cue] else -1.0
    if arm=="shifted_cue":
        return 1.0 if action==SHIFTED[cue] else -1.0
    raise AssertionError("V32B_UNDECLARED_CONTROL_REWARD")


def record_null_balance(schedule,arm,rewards):
    if len(rewards)!=TRAIN or len(schedule)!=TRAIN:
        raise AssertionError("V32B_INCOMPLETE_MATCHED_FEEDBACK_SEQUENCE")
    if arm=="balanced_null":
        for cue in range(4):
            for action in range(3):
                outcomes=[rewards[i] for i,(c,a,_rep) in enumerate(schedule)
                          if c==cue and a==action]
                if len(outcomes)!=20 or outcomes.count(1.0)!=10 or outcomes.count(-1.0)!=10:
                    raise AssertionError("V32B_FROZEN_ZERO_MEAN_PER_ACTION_NULL_LOST")
    elif arm in ("rotated_action","shifted_cue"):
        if rewards.count(1.0)!=80 or rewards.count(-1.0)!=160:
            raise AssertionError("V32B_WRONG_TARGET_REWARD_LABEL_HISTOGRAM_CHANGED")
    else:
        if rewards.count(1.0)!=80 or rewards.count(-1.0)!=160:
            raise AssertionError("V32B_MATCHED_PUBLIC_TRUE_FEEDBACK_HISTOGRAM_DRIFT")


def cold_evaluate(path):
    p=API.new()
    try:
        API.source_layout(p)
        data=Path(path).read_bytes()
        if API.restore(p,data)!=0:
            raise AssertionError("V32B_NEW_PROCESS_COLD_NATIVE_RESTORE_REJECTED")
        actual=API.checkpoint(p)
        if actual!=data:
            raise AssertionError("V32B_NATIVE_SNAPSHOT_COLD_BYTES_CHANGED")
        rows=v32a.eval_native(p)
        if API.checkpoint(p)!=actual:
            raise AssertionError("V32B_NEW_PROCESS_REWARD_BLIND_EVAL_WROTE_WEIGHTS")
        record=diagnostics(rows,CORRECT)
        weights=parse_native_checkpoint(actual)
        cpu=time.process_time_ns()
        resident,meter=actual_os_peak_resident_bytes()
        print(json.dumps({
            "schema":SCHEMA,"role":"cold_fresh_process","host":sys.platform,
            "binary_sha256":API.binary_sha256,
            "source_sha256":API.source_sha256,
            "score_sha256":record["all_raw_score_sha256"],
            "checkpoint_sha256":weights["checkpoint_sha256"],
            "raw_accuracy":record["original_raw_accuracy"],
            "epsilon_accuracy":record["epsilon_stabilized_accuracy"],
            "all_eight_local_update_counters":weights["all_eight_local_update_counters"],
            "first_four_score_hex":record["first_four_score_hex"],
            "cpu_ns":cpu,"os_peak_resident_bytes":resident,"os_resident_method":meter,
        },sort_keys=True,separators=(",",":"),allow_nan=False))
    finally:
        API.free(p)


def cold_launch(checkpoint,diag,weight_record):
    with tempfile.TemporaryDirectory(prefix="v32b-cold-",dir=os.environ.get("RUNNER_TEMP") or None) as folder:
        path=Path(folder)/"native-original-856-byte-checkpoint.bin"
        path.write_bytes(checkpoint)
        start=time.perf_counter_ns()
        p=subprocess.run(
            [sys.executable,"-B",str(Path(__file__).resolve()),"--cold",str(path)],
            cwd=ROOT,check=False,capture_output=True,text=True,
            env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},timeout=MAX_WORKER_SECONDS)
        wall=time.perf_counter_ns()-start
        if p.returncode or p.stderr.strip():
            raise AssertionError("V32B_FRESH_COLD_RUST_PROCESS_FAILED_"+p.stderr[-1500:])
        try: data=json.loads(p.stdout)
        except (ValueError,TypeError) as e:
            raise AssertionError("V32B_FRESH_COLD_JSON_UNAVAILABLE") from e
        if (data.get("schema")!=SCHEMA or data.get("role")!="cold_fresh_process" or
            data.get("host")!=sys.platform or
            data.get("binary_sha256")!=API.binary_sha256 or
            data.get("source_sha256")!=API.source_sha256 or
            data.get("checkpoint_sha256")!=weight_record["checkpoint_sha256"] or
            data.get("score_sha256")!=diag["all_raw_score_sha256"] or
            data.get("raw_accuracy")!=diag["original_raw_accuracy"] or
            data.get("epsilon_accuracy")!=diag["epsilon_stabilized_accuracy"] or
            data.get("first_four_score_hex")!=diag["first_four_score_hex"] or
            data.get("all_eight_local_update_counters")!=
            weight_record["all_eight_local_update_counters"] or
            type(data.get("cpu_ns")) is not int or data["cpu_ns"]<=0 or
            type(data.get("os_peak_resident_bytes")) is not int or
            data["os_peak_resident_bytes"]<=0):
            raise AssertionError("V32B_CROSS_OS_PROCESS_MEMORIZED_F64_OR_NATIVE_WEIGHT_DRIFT")
        data["parent_subprocess_wall_ns"]=wall
        return data


def fresh_worker(arm,seed):
    if arm not in ARMS or seed not in SEEDS:
        raise ValueError("V32B_INVALID_FROZEN_ARM_OR_SEED")
    start=time.process_time_ns()
    schedule=v32a.training_schedule(seed)
    schedule_sha=digest(schedule)
    native=arm!="conventional_true"
    p=API.new() if native else None
    conventional=v32a.Conventional() if not native else None
    try:
        if native:
            API.source_layout(p)
            initial_checkpoint=API.checkpoint(p)
            initial_rows=v32a.eval_native(p)
        else:
            initial_checkpoint=conventional.checkpoint()
            initial_rows=v32a.eval_conventional(conventional)
        initial=diagnostics(initial_rows,CORRECT)
        rewards=[]
        for cue,action,repeat in schedule:
            reward=reward_for(arm,cue,action,repeat)
            rewards.append(reward)
            if native:
                API.observe_one(p,cue)
                API.native_scores(p)  # Same V32A training-time native forward
                API.feedback_one(p,action,reward,arm!="native_no_learning")
            else:
                conventional.scores(cue)
                conventional.feedback(cue,action,reward)
        record_null_balance(schedule,arm,rewards)
        training_cpu_ns=time.process_time_ns()-start
        if native:
            checkpoint=API.checkpoint(p)
            weight_record=parse_native_checkpoint(checkpoint)
            rows=v32a.eval_native(p)
            counters=API.local_updates(p)
            if counters!=weight_record["all_eight_local_update_counters"]:
                raise AssertionError("V32B_LOCAL_NATIVE_HEAP_AND_COLD_WEIGHT_COUNTER_DRIFT")
            if arm!="native_no_learning" and (counters!=[TRAIN]*8 or
                                                 checkpoint==initial_checkpoint):
                raise AssertionError("V32B_PER_CELL_NATIVE_LOCAL_PLASTICITY_NOT_PROVEN")
            if arm=="native_no_learning" and (counters!=[0]*8 or
                                                   checkpoint!=initial_checkpoint):
                raise AssertionError("V32B_FROZEN_NO_UPDATE_NEGATIVE_CONTROL_MUTATED")
        else:
            checkpoint=conventional.checkpoint()
            weight_record=None
            rows=v32a.eval_conventional(conventional)
        after=diagnostics(rows,CORRECT)
        if native and API.checkpoint(p)!=checkpoint:
            raise AssertionError("V32B_NUMERIC_SCORE_INSPECTION_CHANGED_NATIVE_CHECKPOINT")
        if not native and conventional.checkpoint()!=checkpoint:
            raise AssertionError("V32B_NUMERIC_SCORE_INSPECTION_CHANGED_CONVENTIONAL_WEIGHTS")
        wrong_map=(ROTATED if arm=="rotated_action" else SHIFTED if arm=="shifted_cue" else CORRECT)
        target=diagnostics(rows,wrong_map)
        cold=(cold_launch(checkpoint,after,weight_record)
              if arm in ("native_true","balanced_null") else None)
        cpu=time.process_time_ns()
        resident,meter=actual_os_peak_resident_bytes()
        print(json.dumps({
            "schema":SCHEMA,"role":"matched_original_source_worker","host":sys.platform,
            "arm":arm,"seed":seed,"source_sha256":API.source_sha256,
            "binary_sha256":API.binary_sha256,
            "fixed_240_public_cue_action_train_exposures":TRAIN,
            "frozen_96_reward_blind_evaluation":EVAL,
            "exact_training_schedule_sha256":schedule_sha,
            "actual_feedback_stream_sha256":digest(rewards),
            "correct_public_feedback_histogram":{"+1":rewards.count(1.0),"-1":rewards.count(-1.0)},
            "before_original_score":initial,
            "after_original_score":after,
            "after_wrong_target_score":target,
            "original_native_checkpoint_sha256":hashlib.sha256(checkpoint).hexdigest(),
            "native_private_weight_record":weight_record,
            "new_os_cold_process_receipt":cold,
            "whole_process_cpu_ns":cpu,
            "training_process_cpu_ns":training_cpu_ns,
            "training_below_os_clock_resolution":training_cpu_ns==0,
            "actual_os_peak_rss_bytes":resident,
            "actual_os_rss_method":meter,
            "original_v32a_native_rust_source_unmodified":True,
            "original_yggdrasil_model_unchanged":True,
            "previous_v32a_failed_classification_unchanged":True,
            "scientific_first_use":False,
        },sort_keys=True,separators=(",",":"),allow_nan=False))
    finally:
        if p is not None:
            API.free(p)


def launch(arm,seed):
    before=time.perf_counter_ns()
    p=subprocess.run(
        [sys.executable,"-B",str(Path(__file__).resolve()),"--worker",arm,str(seed)],
        cwd=ROOT,check=False,capture_output=True,text=True,
        env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},timeout=MAX_WORKER_SECONDS)
    wall=time.perf_counter_ns()-before
    if p.returncode or p.stderr.strip():
        raise AssertionError("V32B_FRESH_MATCHED_ARM_FAILURE_{}_{}_{}".format(
            arm,seed,p.returncode,p.stderr[-1800:]))
    try: data=json.loads(p.stdout)
    except (ValueError,TypeError) as e:
        raise AssertionError("V32B_UNREADABLE_FRESH_WORKER_SOURCE_OUTPUT") from e
    if (data.get("schema")!=SCHEMA or
        data.get("role")!="matched_original_source_worker" or
        data.get("arm")!=arm or data.get("seed")!=seed or
        data.get("host")!=sys.platform or
        data.get("source_sha256")!=API.source_sha256 or
        data.get("binary_sha256")!=API.binary_sha256 or
        data.get("fixed_240_public_cue_action_train_exposures")!=TRAIN or
        data.get("frozen_96_reward_blind_evaluation")!=EVAL or
        data.get("exact_training_schedule_sha256")!=digest(v32a.training_schedule(seed)) or
        data.get("original_v32a_native_rust_source_unmodified") is not True or
        data.get("previous_v32a_failed_classification_unchanged") is not True or
        data.get("scientific_first_use") is not False):
        raise AssertionError("V32B_WORKER_SOURCE_ORIGINAL_LEARNING_LINEAGE_DRIFT")
    meter=("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform=="linux"
           else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES" if sys.platform=="win32"
           else None)
    if (not meter or data.get("actual_os_rss_method")!=meter or
        type(data.get("whole_process_cpu_ns")) is not int or
        data["whole_process_cpu_ns"]<=0 or
        type(data.get("actual_os_peak_rss_bytes")) is not int or
        data["actual_os_peak_rss_bytes"]<=0 or
        type(data.get("training_process_cpu_ns")) is not int or
        data["training_process_cpu_ns"]<0 or
        data.get("training_below_os_clock_resolution") is not
        (data["training_process_cpu_ns"]==0)):
        raise AssertionError("V32B_REAL_OS_CPU_RSS_OR_CLOCK_RESOLUTION_MISSING")
    data["parent_full_worker_wall_ns"]=wall
    return data


def audit():
    v32a.source_negative_controls()  # unchanged previous version and ABI
    all_reports=[]
    for seed in SEEDS:
        arms={arm:launch(arm,seed) for arm in ARMS}
        a,b,c,d,e,f=(arms[name] for name in ARMS)
        if (len({x["exact_training_schedule_sha256"] for x in arms.values()})!=1 or
            len({x["actual_feedback_stream_sha256"] for x in (a,b,c)})!=1 or
            len({x["actual_feedback_stream_sha256"] for x in (a,d,e,f)})!=4):
            raise AssertionError("V32B_UNFAIR_OR_IDENTICAL_EXPERIMENTAL_REWARD_STREAM")
        if any(x["correct_public_feedback_histogram"]!={"+1":80,"-1":160}
               for x in (a,b,c,e,f)) or d["correct_public_feedback_histogram"]!={"+1":120,"-1":120}:
            raise AssertionError("V32B_FROZEN_REWARD_BALANCE_NOT_VERIFIED")
        aa=a["after_original_score"]
        bb=b["after_original_score"]
        cc=c["after_original_score"]
        dd=d["after_original_score"]
        ee=e["after_original_score"]
        ff=f["after_original_score"]
        dw=d["native_private_weight_record"]
        source_eps=(dd["max_abs_score"]<=EPS and
                    dd["max_top_second_margin"]<=EPS and
                    dd["near_tie_decisions_1e_minus_10"]==EVAL and
                    dw["max_abs_local_native_weight"]<=EPS and
                    dw["num_weights_gt_epsilon"]==0)
        expectedD=EXPECTED_RAW_BALANCED[seed]
        h1=(aa["original_raw_accuracy"]==1.0 and
            aa["epsilon_stabilized_accuracy"]==1.0 and
            aa["min_top_second_margin"]>STRONG_MARGIN and
            bb["original_raw_accuracy"]==1.0 and
            bb["epsilon_stabilized_accuracy"]==1.0 and
            cc["original_raw_accuracy"]==.25 and
            cc["epsilon_stabilized_accuracy"]==.25 and
            dd["original_raw_accuracy"]==expectedD and
            dd["epsilon_stabilized_accuracy"]==.25 and
            source_eps)
        h2=(all(x["original_raw_accuracy"]<=.25 and
                x["epsilon_stabilized_accuracy"]<=.25
                for x in (ee,ff)) and
            all(x["epsilon_stabilized_accuracy"]>=.75
                for x in (e["after_wrong_target_score"],
                          f["after_wrong_target_score"])) and
            ee["min_top_second_margin"]>STRONG_MARGIN and
            ff["min_top_second_margin"]>STRONG_MARGIN)
        if any(x["new_os_cold_process_receipt"] is None
               for x in (a,d)):
            raise AssertionError("V32B_MISSING_TWO_INDEPENDENT_COLD_PROCESS_TESTS")
        all_reports.append({
            "seed":seed,
            "h1_numerical_tie_diagnosis_pass":h1,
            "h2_wrong_consequence_reward_dependence_pass":h2,
            "frozen_v32a_original_scrambled_null_raw_accuracy":dd["original_raw_accuracy"],
            "balanced_null_epsilon_accuracy":dd["epsilon_stabilized_accuracy"],
            "balanced_null_max_abs_native_weight":dw["max_abs_local_native_weight"],
            "balanced_null_max_abs_score":dd["max_abs_score"],
            "balanced_null_max_top_two_score_margin":dd["max_top_second_margin"],
            "native_true_raw_accuracy":aa["original_raw_accuracy"],
            "native_true_stable_accuracy":aa["epsilon_stabilized_accuracy"],
            "native_true_min_score_margin":aa["min_top_second_margin"],
            "conventional_true_accuracy":bb["epsilon_stabilized_accuracy"],
            "no_learning_accuracy":cc["epsilon_stabilized_accuracy"],
            "rotated_wrong_map_true_accuracy":ee["epsilon_stabilized_accuracy"],
            "rotated_wrong_map_own_accuracy":e["after_wrong_target_score"]["epsilon_stabilized_accuracy"],
            "shifted_wrong_map_true_accuracy":ff["epsilon_stabilized_accuracy"],
            "shifted_wrong_map_own_accuracy":f["after_wrong_target_score"]["epsilon_stabilized_accuracy"],
            "cold_native_true_checkpoint_exact":True,
            "cold_balanced_null_checkpoint_exact":True,
            "full_f64_native_weight_and_score_hex_by_arm":{
                arm: {
                    "native_weight_f64_bits":
                        x["native_private_weight_record"]["all_96_native_weight_f64_hex_little_endian"]
                        if x["native_private_weight_record"] is not None else None,
                    "first_four_score_hex":
                        x["after_original_score"]["first_four_score_hex"],
                    "first_four_f64_bits":
                        x["after_original_score"]["first_four_f64_bits_be"],
                    "score_sha256":
                        x["after_original_score"]["all_raw_score_sha256"],
                } for arm,x in arms.items()
            },
            "full_original_os_resources_by_arm":{
                arm:{
                    "whole_process_cpu_ns":x["whole_process_cpu_ns"],
                    "training_process_cpu_ns":x["training_process_cpu_ns"],
                    "training_below_os_clock_resolution":x["training_below_os_clock_resolution"],
                    "actual_os_peak_rss_bytes":x["actual_os_peak_rss_bytes"],
                    "parent_full_worker_wall_ns":x["parent_full_worker_wall_ns"],
                    "independent_cold_process_resources":x["new_os_cold_process_receipt"],
                } for arm,x in arms.items()
            }
        })
    positive=all(r["h1_numerical_tie_diagnosis_pass"] and
                 r["h2_wrong_consequence_reward_dependence_pass"]
                 for r in all_reports)
    print(json.dumps({
        "schema":SCHEMA,"status":"COMPLETE","host":sys.platform,
        "classification":(
            "V32B_NUMERICAL_TIE_AND_REWARD_DEPENDENCE_SUPPORTED__NO_SCIENCE"
            if positive else
            "V32B_NUMERIC_OR_WRONG_LABEL_DIAGNOSIS_NEGATIVE__NO_SCIENCE"),
        "original_v32a_scrambled_control_still_FAILED":True,
        "frozen_original_v32a_negative_classification":
            "V32A_NATIVE_LOCAL_PLASTICITY_LEARNING_NEGATIVE__NO_SCIENCE",
        "native_source_sha256_unchanged":API.source_sha256,
        "native_compiled_sha256":API.binary_sha256,
        "in_process_eight_box_cell_local_weights":True,
        "original_yggdrasil_model_modified":False,
        "scientific_first_use":False,
        "new_science_or_native_model_promotion":False,
        "independent_native_os_cell_execution_proven":False,
        "fixed_seeds":SEEDS,
        "fixed_tie_epsilon":EPS,
        "strong_positive_score_margin_required":STRONG_MARGIN,
        "fresh_matched_control_workers_per_host":len(SEEDS)*len(ARMS),
        "fresh_independent_native_cold_processes_per_host":len(SEEDS)*2,
        "native_learning_train_exposures":TRAIN,
        "reward_blind_eval_exposures":EVAL,
        "results":all_reports,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        fresh_worker(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==3 and sys.argv[1]=="--cold":
        cold_evaluate(sys.argv[2])
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V32B_UNAUTHORIZED_COMMAND")
