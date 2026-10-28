"""V32A isolated native-local plasticity with frozen fair feedback controls.

Native Rust learns from ORIGINAL neighbor-local cue and reward signals.
This is NOT Yggdrasil's original learner; never touches original weight/model.
"""
from __future__ import annotations
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
import tempfile
import time

from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTION_SITES, CELLS, PUBLIC_CUES, RING,
)
from yggdrasil.itd02_local_ring_memory_dev import OBSERVATIONS, OBS_SITES
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_TRACE_SHA, EXPECTED_CHECKPOINT_SHA,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "itd02_v32a_native_microcells.rs"
SCHEMA = "yggdrasil.itd02.v32a.native_microcell_local_plasticity.v1"
SEEDS = (11, 23, 37, 51, 79)
ARMS = ("native", "conventional", "no_learning", "permuted_feedback")
CORRECT = (0, 1, 2, 1)  # PUBLIC harness reward law; never provided to Rust
EXPECTED_FFI = 0x5633324100010001
RATE = 0.20
TRAIN_EXPOSURES = 240
EVAL_EXPOSURES = 96
WORKER_TIMEOUT = 90


class Api:
    def __init__(self):
        raw = os.environ.get("V32A_NATIVE_LIBRARY", "")
        path = Path(raw)
        if (not raw or not path.is_file() or
            path.suffix.lower() != (".dll" if sys.platform=="win32" else ".so")):
            raise AssertionError("V32A_NATIVE_COMPILED_MODULE_NOT_AVAILABLE")
        self.binary_sha256=hashlib.sha256(path.read_bytes()).hexdigest()
        self.source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        lib=ctypes.CDLL(str(path.resolve()))
        void=ctypes.c_void_p
        integer=ctypes.c_int
        up=ctypes.c_uint8
        self.lib=lib
        def attach(name,args,restype):
            fn=getattr(lib,name)
            fn.argtypes=args
            fn.restype=restype
            return fn
        self.create=attach("v32a_new",[],void)
        self.free=attach("v32a_free",[void],None)
        self.schema=attach("v32a_schema",[],ctypes.c_uint64)
        self.size=attach("v32a_checkpoint_size",[],ctypes.c_size_t)
        self.observe=attach("v32a_observe",[void,integer],integer)
        self.scores=attach("v32a_scores",[void,ctypes.POINTER(ctypes.c_double),ctypes.c_size_t],integer)
        self.feedback=attach("v32a_feedback",[void,integer,ctypes.c_double,integer],integer)
        self.address=attach("v32a_cell_address",[void,integer],ctypes.c_size_t)
        self.neighbor=attach("v32a_neighbor",[void,integer,integer],integer)
        self.updates=attach("v32a_cell_updates",[void,integer],ctypes.c_int64)
        self.save=attach("v32a_save",[void,ctypes.POINTER(up),ctypes.c_size_t],integer)
        self.load=attach("v32a_load",[void,ctypes.POINTER(up),ctypes.c_size_t],integer)
        if self.schema()!=EXPECTED_FFI or self.size()!=856:
            raise AssertionError("V32A_NATIVE_FFI_SCHEMA_OR_CHECKPOINT_SIZE_MISMATCH")

    def new(self):
        ptr=self.create()
        if not ptr:
            raise AssertionError("V32A_NATIVE_CELL_ALLOCATION_FAILED")
        return ptr

    def source_layout(self,ptr):
        addresses=[self.address(ptr,i) for i in range(CELLS)]
        if len(set(addresses))!=CELLS or min(addresses)==0:
            raise AssertionError("V32A_NOT_EIGHT_DISTINCT_NATIVE_HEAP_CELLS")
        if ACTION_SITES!=(0,2,5):
            raise AssertionError("V32A_ORIGINAL_ACTION_SITE_CHANGED")
        if [OBS_SITES[OBSERVATIONS.index(c)] for c in PUBLIC_CUES]!=[1,3,7,4]:
            raise AssertionError("V32A_ORIGINAL_PUBLIC_CUE_SITE_CHANGED")
        for i in range(CELLS):
            for side in (0,1):
                if self.neighbor(ptr,i,side)!=RING[i][side]:
                    raise AssertionError("V32A_NONNEIGHBOR_OR_CHANGED_RING")
            if self.neighbor(ptr,i,2)!=-1:
                raise AssertionError("V32A_FORGED_THIRD_RING_EDGE")
        return addresses

    def observe_one(self,ptr,cue):
        if self.observe(ptr,cue)!=0:
            raise AssertionError("V32A_NATIVE_VALID_PUBLIC_CUE_REJECTED")

    def native_scores(self,ptr):
        out=(ctypes.c_double*3)()
        if self.scores(ptr,out,3)!=0:
            raise AssertionError("V32A_NATIVE_SCORE_READOUT_FAILED")
        v=[float(x) for x in out]
        if not all(math.isfinite(x) and abs(x)<=1000 for x in v):
            raise AssertionError("V32A_NONFINITE_NATIVE_ACTION_SCORE")
        return v

    def feedback_one(self,ptr,action,reward,learning):
        if self.feedback(ptr,action,float(reward),int(learning))!=0:
            raise AssertionError("V32A_NATIVE_LOCAL_FEEDBACK_REJECTED")

    def checkpoint(self,ptr):
        count=self.size()
        out=(ctypes.c_uint8*count)()
        if self.save(ptr,out,count)!=0:
            raise AssertionError("V32A_NATIVE_CHECKPOINT_EXPORT_FAILED")
        return bytes(out)

    def restore(self,ptr,data):
        raw=(ctypes.c_uint8*len(data)).from_buffer_copy(data)
        return self.load(ptr,raw,len(data))

    def local_updates(self,ptr):
        return [int(self.updates(ptr,i)) for i in range(CELLS)]


API=Api()
def sha(data):
    return hashlib.sha256(data).hexdigest()

def scores_hash(values):
    return sha(json.dumps(values,separators=(",",":"),allow_nan=False).encode())

def source_negative_controls():
    if sha(SOURCE.read_bytes())!=API.source_sha256:
        raise AssertionError("V32A_IMMUTABLE_RUST_SOURCE_MISMATCH")
    if EXPECTED_TRACE_SHA!="84427bdfa27b0a43e30a699548877a9184413e62e0a6ec6de491fb5ed184b7ff":
        raise AssertionError("V32A_ORIGINAL_SOURCE_TRACE_PROTECTION_DRIFT")
    if EXPECTED_CHECKPOINT_SHA!="0b03b83f999afdab24eb71805a24766fa6b98c069151d14bccfa949602b63c48":
        raise AssertionError("V32A_ORIGINAL_CHECKPOINT_FROZEN_DIGEST_DRIFT")
    p=API.new()
    try:
        API.source_layout(p)
        empty=API.checkpoint(p)
        if len(empty)!=856:
            raise AssertionError("V32A_NATIVE_FROZEN_CHECKPOINT_SIZE_CHANGED")
        if API.scores(p,(ctypes.c_double*3)(),3)!=-3:
            raise AssertionError("V32A_NO_OBSERVATION_SCORE_UNSAFELY_ACCEPTED")
        for invalid in (-1,4,8):
            if API.observe(p,invalid)!=-2:
                raise AssertionError("V32A_INVALID_CUE_ACCEPTED")
        if API.feedback(p,0,1.0,1)!=-3:
            raise AssertionError("V32A_FEEDBACK_WITHOUT_OBSERVATION_ACCEPTED")
        if API.observe(p,0)!=0:
            raise AssertionError("V32A_VALID_SOURCE_OBSERVATION_REJECTED")
        wrong=(ctypes.c_double*2)()
        if API.scores(p,wrong,2)!=-2 or API.scores(p,None,3)!=-1:
            raise AssertionError("V32A_NATIVE_BAD_OUTPUT_BUFFER_ACCEPTED")
        if API.feedback(p,3,1.0,1)!=-2 or API.feedback(p,0,float("nan"),1)!=-2 or API.feedback(p,0,1.0,2)!=-2:
            raise AssertionError("V32A_MALFORMED_LOCAL_REWARD_ACCEPTED")
        if API.local_updates(p)!=[0]*8:
            raise AssertionError("V32A_INVALID_REWARD_UPDATED_PRIVATE_CELL")
        # Source-only readouts must not mutate persistent learned parameters.
        before=API.checkpoint(p)
        API.native_scores(p)
        if API.checkpoint(p)!=before:
            raise AssertionError("V32A_PREDICT_ONLY_MUTATED_NATIVE_WEIGHTS")
        corrupt=bytearray(empty);corrupt[9]^=1
        modified=bytearray(empty);modified[0]=ord("X")
        for candidate in (bytes(corrupt),bytes(modified),empty[:-1]):
            other=API.new()
            try:
                if API.restore(other,candidate)>=0:
                    raise AssertionError("V32A_BAD_NATIVE_CHECKPOINT_ACCEPTED")
                if API.checkpoint(other)!=empty:
                    raise AssertionError("V32A_BAD_CHECKPOINT_MODIFIED_NATIVE_MODEL")
            finally:
                API.free(other)
        API.feedback_one(p,1,1.0,True)
    finally:
        API.free(p)


def training_schedule(seed):
    pairs=[(cue,action,repeat) for repeat in range(20)
           for cue in range(4) for action in range(3)]
    random.Random(seed).shuffle(pairs)
    if len(pairs)!=TRAIN_EXPOSURES or len(set(pairs))!=TRAIN_EXPOSURES:
        raise AssertionError("V32A_PUBLIC_TRAINING_SCHEDULE_NOT_BALANCED")
    return pairs


class Conventional:
    """Richer global-cue control, same 96 weights; no original ring privilege."""
    def __init__(self):
        self.weights=[[[0.0 for _ in range(4)] for _ in range(3)] for _ in range(8)]
    def scores(self,cue):
        return [sum(self.weights[i][a][cue] for i in range(8))/8.0
                for a in range(3)]
    def feedback(self,cue,action,reward):
        for i in range(8):
            x=self.weights[i][action][cue] + RATE*reward
            self.weights[i][action][cue]=max(-8.0,min(8.0,x))
    def checkpoint(self):
        return json.dumps(self.weights,separators=(",",":"),allow_nan=False).encode()


def eval_native(ptr):
    rows=[]
    before=API.checkpoint(ptr)
    for rep in range(24):
        for cue in range(4):
            API.observe_one(ptr,cue)
            rows.append([float(x) for x in API.native_scores(ptr)])
    if API.checkpoint(ptr)!=before:
        raise AssertionError("V32A_FROZEN_REWARD_BLIND_EVAL_MUTATED_NATIVE_WEIGHTS")
    return rows


def eval_conventional(model):
    before=model.checkpoint()
    rows=[model.scores(cue) for _ in range(24) for cue in range(4)]
    if model.checkpoint()!=before:
        raise AssertionError("V32A_CONVENTIONAL_EVAL_MUTATED_WEIGHTS")
    return rows


def accuracy(rows):
    if len(rows)!=EVAL_EXPOSURES:
        raise AssertionError("V32A_INCOMPLETE_FROZEN_PUBLIC_EVALUATION")
    correct=0
    for i,row in enumerate(rows):
        if (type(row) is not list or len(row)!=3 or
                any(not math.isfinite(v) for v in row)):
            raise AssertionError("V32A_BAD_NONFINITE_SCORE_VECTOR")
        action=max(range(3),key=lambda a:row[a])
        if action==CORRECT[i%4]:
            correct+=1
    return correct/EVAL_EXPOSURES


def cold_worker(path):
    p=API.new()
    try:
        API.source_layout(p)
        b=Path(path).read_bytes()
        if API.restore(p,b)!=0:
            raise AssertionError("V32A_FRESH_NATIVE_PROCESS_RESTORE_FAILED")
        restored=API.checkpoint(p)
        if restored!=b:
            raise AssertionError("V32A_NATIVE_RESTART_CHECKPOINT_BYTES_DIFFER")
        rows=eval_native(p)
        cpu=time.process_time_ns()
        resident,method=actual_os_peak_resident_bytes()
        print(json.dumps({
            "schema":SCHEMA,"role":"cold_process","host":sys.platform,
            "score_sha256":scores_hash(rows),
            "checkpoint_sha256":sha(restored),"accuracy":accuracy(rows),
            "local_updates":API.local_updates(p),
            "source_sha256":API.source_sha256,"binary_sha256":API.binary_sha256,
            "process_cpu_ns":cpu,"actual_os_peak_rss_bytes":resident,
            "resident_method":method,"original_model_modified":False,
        },sort_keys=True,separators=(",",":"),allow_nan=False))
    finally:
        API.free(p)


def cold_launch(data):
    with tempfile.TemporaryDirectory(prefix="v32a-native-cold-",dir=os.environ.get("RUNNER_TEMP") or None) as folder:
        path=Path(folder)/"local-native-checkpoint.bin"
        path.write_bytes(data)
        start=time.perf_counter_ns()
        r=subprocess.run(
            [sys.executable,"-B",str(Path(__file__).resolve()),"--cold",str(path)],
            cwd=ROOT,capture_output=True,text=True,timeout=WORKER_TIMEOUT,
            env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},check=False)
        wall=time.perf_counter_ns()-start
        if r.returncode or r.stderr.strip():
            raise AssertionError("V32A_FRESH_COLD_PROCESS_FAILED_"+r.stderr[-1600:])
        try:
            d=json.loads(r.stdout)
        except (TypeError,ValueError) as e:
            raise AssertionError("V32A_COLD_PROCESS_REPORT_MISSING") from e
        if (d.get("role")!="cold_process" or d.get("host")!=sys.platform or
            d.get("source_sha256")!=API.source_sha256 or
            d.get("binary_sha256")!=API.binary_sha256 or
            d.get("checkpoint_sha256")!=sha(data) or
            d.get("original_model_modified") is not False):
            raise AssertionError("V32A_COLD_PROVENANCE_OR_CHECKPOINT_DRIFT")
        if not d.get("process_cpu_ns",0)>0 or not d.get("actual_os_peak_rss_bytes",0)>0:
            raise AssertionError("V32A_UNMETERED_COLD_PROCESS")
        d["subprocess_wall_ns"]=wall
        return d


def fresh_worker(arm,seed):
    if arm not in ARMS or seed not in SEEDS:
        raise ValueError("V32A_UNKNOWN_FROZEN_ARM_OR_SEED")
    begin=time.process_time_ns()
    schedule=training_schedule(seed)
    native=arm!="conventional"
    p=API.new() if native else None
    model=Conventional() if not native else None
    try:
        if native:
            API.source_layout(p)
            before_rows=eval_native(p)
            before_weights=API.checkpoint(p)
        else:
            before_rows=eval_conventional(model)
            before_weights=model.checkpoint()
        for cue,action,repeat in schedule:
            reward=1.0 if action==CORRECT[cue] else -1.0
            if arm=="permuted_feedback":
                reward=1.0 if repeat%2==0 else -1.0
            if native:
                API.observe_one(p,cue)
                API.native_scores(p)  # actual train-time model prediction
                API.feedback_one(p,action,reward,arm!="no_learning")
            else:
                model.scores(cue)
                model.feedback(cue,action,reward)
        trained=time.process_time_ns()
        if native:
            checkpoint=API.checkpoint(p)
            learned=[int(x) for x in API.local_updates(p)]
            rows=eval_native(p)
            final=API.checkpoint(p)
        else:
            checkpoint=model.checkpoint()
            learned=None
            rows=eval_conventional(model)
            final=model.checkpoint()
        if checkpoint!=final:
            raise AssertionError("V32A_FROZEN_PREDICT_ONLY_CHECKPOINT_CHANGED")
        if native and ((arm=="no_learning" and learned!=[0]*8) or
                       (arm!="no_learning" and min(learned)<=0)):
            raise AssertionError("V32A_NATIVE_LOCAL_PLASTICITY_UPDATE_CUSTODY")
        if (arm=="native" and checkpoint==before_weights) or (
                arm=="no_learning" and checkpoint!=before_weights):
            raise AssertionError("V32A_NATIVE_WEIGHTS_DID_NOT_UPDATE_OR_NULL_CHANGED")
        cold=cold_launch(checkpoint) if arm=="native" else None
        if cold is not None and (cold["score_sha256"]!=scores_hash(rows) or
                cold["accuracy"]!=accuracy(rows) or cold["local_updates"]!=learned):
            raise AssertionError("V32A_SEPARATE_PROCESS_COLD_PREDICTION_OR_LOCAL_MEMORY_DRIFT")
        total=time.process_time_ns()
        rss,method=actual_os_peak_resident_bytes()
        print(json.dumps({
            "schema":SCHEMA,"role":"fresh_worker","host":sys.platform,
            "arm":arm,"seed":seed,"train_exposures":TRAIN_EXPOSURES,
            "eval_exposures":EVAL_EXPOSURES,
            "accuracy_before":accuracy(before_rows),"accuracy_after":accuracy(rows),
            "score_sha256":scores_hash(rows),
            "checkpoint_sha256_before":sha(before_weights),
            "checkpoint_sha256_after":sha(checkpoint),
            "frozen_checkpoint_unchanged":True,
            "native_local_update_counts":learned,
            "native_actual_weight_plasticity":arm=="native" and checkpoint!=before_weights,
            "cold_original_process":cold,
            "training_cpu_ns_including_rust":trained-begin,
            "whole_parent_process_cpu_ns_including_rust":total,
            "actual_os_peak_resident_bytes":rss,"os_peak_resident_method":method,
            "source_sha256":API.source_sha256,"binary_sha256":API.binary_sha256,
            "rust_is_original_yggdrasil_learner":False,"scientific_first_use":False,
            "independent_cell_thread_or_process_execution":False,
        },sort_keys=True,separators=(",",":"),allow_nan=False))
    finally:
        if p is not None:
            API.free(p)


def launch(arm,seed):
    start=time.perf_counter_ns()
    r=subprocess.run([sys.executable,"-B",str(Path(__file__).resolve()),
        "--worker",arm,str(seed)],cwd=ROOT,capture_output=True,text=True,
        timeout=WORKER_TIMEOUT,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},check=False)
    wall=time.perf_counter_ns()-start
    if r.returncode or r.stderr.strip():
        raise AssertionError("V32A_WORKER_FAIL_{}_{}_{}".format(arm,seed,r.stderr[-1800:]))
    try:
        d=json.loads(r.stdout)
    except (TypeError,ValueError) as e:
        raise AssertionError("V32A_WORKER_JSON_MISSING") from e
    if (d.get("schema")!=SCHEMA or d.get("role")!="fresh_worker" or
        d.get("host")!=sys.platform or d.get("arm")!=arm or d.get("seed")!=seed or
        d.get("train_exposures")!=TRAIN_EXPOSURES or d.get("eval_exposures")!=EVAL_EXPOSURES or
        d.get("source_sha256")!=API.source_sha256 or d.get("binary_sha256")!=API.binary_sha256 or
        d.get("frozen_checkpoint_unchanged") is not True or
        d.get("scientific_first_use") is not False or
        d.get("rust_is_original_yggdrasil_learner") is not False or
        d.get("independent_cell_thread_or_process_execution") is not False):
        raise AssertionError("V32A_WORKER_REPORTED_UNPINNED_SOURCE_OR_UNAUTHORIZED_MODEL")
    for k in ("whole_parent_process_cpu_ns_including_rust","actual_os_peak_resident_bytes",
              "training_cpu_ns_including_rust"):
        if type(d.get(k)) is not int or d[k]<=0:
            raise AssertionError("V32A_UNMETERED_NATIVE_RESOURCE_"+k)
    meter=("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform=="linux"
           else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES" if sys.platform=="win32" else None)
    if not meter or d.get("os_peak_resident_method")!=meter:
        raise AssertionError("V32A_REAL_OS_RSS_METER_NOT_SUPPORTED")
    d["full_subprocess_wall_ns"]=wall
    return d


def audit():
    source_negative_controls()
    report=[]
    for seed in SEEDS:
        arms={arm:launch(arm,seed) for arm in ARMS}
        a,b,c,d=(arms[x] for x in ARMS)
        positive=(
            a["accuracy_after"]>=.75 and b["accuracy_after"]>=.75 and
            a["accuracy_after"]+0.10>=b["accuracy_after"] and
            c["accuracy_after"]<=.50 and d["accuracy_after"]<=.60 and
            a["accuracy_after"]-a["accuracy_before"]>=.25 and
            a["native_actual_weight_plasticity"] is True and
            len(a["native_local_update_counts"])==8 and
            min(a["native_local_update_counts"])>0 and
            a["cold_original_process"] is not None)
        report.append({
            "seed":seed,
            "learning_gate_passed":positive,
            "native_accuracy":a["accuracy_after"],
            "native_untrained_accuracy":a["accuracy_before"],
            "strong_conventional_accuracy":b["accuracy_after"],
            "no_learning_accuracy":c["accuracy_after"],
            "permuted_feedback_accuracy":d["accuracy_after"],
            "native_private_cell_update_counts":a["native_local_update_counts"],
            "native_checkpoint_sha256":a["checkpoint_sha256_after"],
            "native_score_sha256":a["score_sha256"],
            "fresh_cold_checkpoint_and_96_predictions_exact":True,
            "actual_cpu_and_rss_by_arm":{arm:{
                "training_process_cpu_ns":x["training_cpu_ns_including_rust"],
                "whole_parent_process_cpu_ns":x["whole_parent_process_cpu_ns_including_rust"],
                "actual_os_peak_resident_bytes":x["actual_os_peak_resident_bytes"],
                "subprocess_wall_ns":x["full_subprocess_wall_ns"],
                "separate_cold_process":x["cold_original_process"] if arm=="native" else None,
            } for arm,x in arms.items()}
        })
    positive=all(r["learning_gate_passed"] for r in report)
    print(json.dumps({
        "schema":SCHEMA,"status":"COMPLETE","host":sys.platform,
        "classification":("V32A_NATIVE_LOCAL_PLASTICITY_BOUNDED_POSITIVE__NO_SCIENCE"
                          if positive else
                          "V32A_NATIVE_LOCAL_PLASTICITY_LEARNING_NEGATIVE__NO_SCIENCE"),
        "source_sha256":API.source_sha256,
        "binary_sha256":API.binary_sha256,
        "native_cells_actual_boxed_private_weights":True,
        "native_cells_independent_os_execution":False,
        "original_yggdrasil_learner_modified":False,
        "original_source_digest_contract_unchanged":True,
        "scientific_first_use":False,
        "unfamiliar_world_transfer_proven":False,
        "fixed_seeds":SEEDS,
        "native_training_exposures_per_seed":TRAIN_EXPOSURES,
        "frozen_no_feedback_evaluation_per_seed":EVAL_EXPOSURES,
        "fresh_source_control_processes":len(SEEDS)*len(ARMS),
        "fresh_independent_native_cold_processes":len(SEEDS),
        "baseline_original_model_and_q1_q3_unchanged":True,
        "criteria":{"native_accuracy_at_least":.75,"conventional_at_least":.75,
                    "native_noninferiority_tolerance":.10,
                    "no_learning_at_most":.50,"scrambled_at_most":.60,
                    "native_prepost_accuracy_gain_at_least":.25},
        "results":report,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        fresh_worker(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==3 and sys.argv[1]=="--cold":
        cold_worker(sys.argv[2])
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V32A_NOT_A_DECLARED_COMMAND")
