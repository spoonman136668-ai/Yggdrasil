"""V32D preregistered local private memory with self-detected consequence change.

NEW quarantined Rust module, original V32A/V32C and native Yggdrasil unchanged.
Seven fresh-arm workers/seed, original controls, fresh cold process checkpoint.
"""
from __future__ import annotations
import contextlib
import ctypes
import hashlib
import io
import json
import math
import os
import random
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import research.itd02_v32a_native_microcells_audit as v32a
import research.itd02_v32b_null_margin_audit as v32b
import research.itd02_v32c_world_reversal_audit as v32c
import research.itd02_v32d_context_memory_audit as v32d
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research"/"itd02_v32e_pair_consensus.rs"
SCHEMA="yggdrasil.itd02.v32e.distinct_pair_consensus_context.v1"
ARMS=("new_adapt","old_v32d_adapt","old_adapt","old_fresh","old_conventional",
      "new_frozen","new_sham","new_shuffled_null","new_wrong")
SEEDS=(11,23,37,51,79)
MAGIC=b"V32EMIC1"
SCHEMA_CODE=0x5633324500010001
N=8
TIMEOUT=150


def hex_sha(data):
    return hashlib.sha256(data).hexdigest()


def original_source_guard():
    if (v32c.API.source_sha256 !=
        "d5ecc87a8c42130526c8a62df358a6be43b1fc024c22a63332932fb9af496655"
        or v32c.A!=(0,1,2,1)
        or v32c.B!=(1,2,0,2)
        or v32c.C!=(2,0,1,0)
        or v32b.EPS!=1e-10
        or v32c.SEEDS!=SEEDS):
        raise AssertionError("V32E_ORIGINAL_SOURCE_REWARD_OR_TIE_INVARIANT_DRIFT")
    v32a.source_negative_controls()
    if v32d.API.source_sha256 != hashlib.sha256(
        (ROOT/"research"/"itd02_v32d_context_memory.rs").read_bytes()).hexdigest():
        raise AssertionError("V32E_FROZEN_V32D_RUST_SOURCE_CHANGED")


class NewApi:
    def __init__(self):
        raw=os.environ.get("V32E_NATIVE_LIBRARY")
        if not raw or not Path(raw).is_file() or Path(raw).suffix.lower()!=(
              ".dll" if sys.platform=="win32" else ".so"):
            raise AssertionError("V32E_ORIGINAL_COMPILED_NATIVE_RUST_MODULE_MISSING")
        self.path=str(Path(raw).resolve())
        self.source_sha256=hex_sha(SOURCE.read_bytes())
        self.binary_sha256=hex_sha(Path(raw).read_bytes())
        lib=ctypes.CDLL(self.path)
        ptr=ctypes.c_void_p
        int_=ctypes.c_int
        uint=ctypes.c_uint8
        def bind(sym,args,out):
            fun=getattr(lib,"v32e_"+sym)
            fun.argtypes=args
            fun.restype=out
            return fun
        self.create=bind("new",[],ptr)
        self.free=bind("free",[ptr],None)
        self._schema=bind("schema",[],ctypes.c_uint64)
        self.size=bind("checkpoint_size",[],ctypes.c_size_t)
        self.observe=bind("observe",[ptr,int_],int_)
        self.scores=bind("scores",[ptr,ctypes.POINTER(ctypes.c_double),ctypes.c_size_t],int_)
        self.feedback=bind("feedback",[ptr,int_,ctypes.c_double,int_],int_)
        self.address=bind("cell_address",[ptr,int_],ctypes.c_size_t)
        self.neighbor=bind("neighbor",[ptr,int_,int_],int_)
        self.update=bind("cell_updates",[ptr,int_],ctypes.c_int64)
        self.active=bind("cell_active",[ptr,int_],int_)
        self.switch=bind("cell_switches",[ptr,int_],ctypes.c_int64)
        self.age=bind("cell_bank_age",[ptr,int_,int_],ctypes.c_int64)
        self.save=bind("save",[ptr,ctypes.POINTER(uint),ctypes.c_size_t],int_)
        self.load=bind("load",[ptr,ctypes.POINTER(uint),ctypes.c_size_t],int_)
        if self._schema()!=SCHEMA_CODE or self.size()!=2264:
            raise AssertionError("V32E_BINARY_ABI_CHECKPOINT_SCHEMA_CHANGED")
    def new(self):
        h=self.create()
        if not h:raise AssertionError("V32E_EIGHT_CELL_HEAP_CREATE_FAILED")
        return h
    def layout(self,h):
        a=[self.address(h,i) for i in range(N)]
        if min(a)==0 or len(set(a))!=N:
            raise AssertionError("V32E_PRIVATE_RUST_BOX_CELL_ALIAS")
        for i in range(N):
            for side in (0,1):
                if self.neighbor(h,i,side)!=v32a.RING[i][side]:
                    raise AssertionError("V32E_NONNEIGHBOR_GLOBAL_ROUTE")
            if self.neighbor(h,i,2)!=-1:
                raise AssertionError("V32E_UNAUTHORIZED_NONNEIGHBOR")
        return a
    def observe_one(self,h,cue):
        if self.observe(h,cue):raise AssertionError("V32E_ORIGINAL_VALID_CUE_REJECTED")
    def native_scores(self,h):
        buf=(ctypes.c_double*3)()
        if self.scores(h,buf,3):raise AssertionError("V32E_ORIGINAL_LOCAL_CELL_SCORE_FAILED")
        scores=[float(x) for x in buf]
        if any(not math.isfinite(x) for x in scores):
            raise AssertionError("V32E_NONFINITE_LOCAL_ACTION_SCORE")
        return scores
    def feedback_one(self,h,action,reward,learning):
        if self.feedback(h,action,float(reward),int(learning)):
            raise AssertionError("V32E_INVALID_PRIVATE_CREDIT_OR_REWARD")
    def checkpoint(self,h):
        b=(ctypes.c_uint8*self.size())()
        if self.save(h,b,len(b)):
            raise AssertionError("V32E_TWO_BANK_CHECKPOINT_EXPORT_FAILED")
        o=bytes(b)
        if len(o)!=2264 or o[:8]!=MAGIC:
            raise AssertionError("V32E_WRONG_VERSIONED_DOUBLE_BANK_CHECKPOINT")
        return o
    def restore(self,h,data):
        b=(ctypes.c_uint8*len(data)).from_buffer_copy(data)
        return self.load(h,b,len(data))
    def ledger(self,h):
        return {
            "total_updates":[int(self.update(h,i)) for i in range(N)],
            "active_bank":[int(self.active(h,i)) for i in range(N)],
            "switches":[int(self.switch(h,i)) for i in range(N)],
            "bank0_age":[int(self.age(h,i,0)) for i in range(N)],
            "bank1_age":[int(self.age(h,i,1)) for i in range(N)],
        }

API=NewApi()


def preflight():
    original_source_guard()
    h=API.new()
    try:
        API.layout(h)
        baseline=API.checkpoint(h)
        for malformed in (baseline[:-1], bytes([0])+baseline[1:],
                          baseline[:29]+bytes([baseline[29]^1])+baseline[30:]):
            if API.restore(h,malformed)>=0:
                raise AssertionError("V32E_CORRUPTED_COLD_MODEL_ACCEPTED")
            if API.checkpoint(h)!=baseline:
                raise AssertionError("V32E_REJECTED_BAD_CHECKPOINT_MUTATED_CELL_MEMORY")
        if API.scores(h,(ctypes.c_double*3)(),3)!=-3:
            raise AssertionError("V32E_SCORE_BEFORE_PUBLIC_OBSERVATION_ACCEPTED")
        for bad in (-1,4):
            if API.observe(h,bad)!=-2:
                raise AssertionError("V32E_INVALID_SOURCE_CUE_ACCEPTED")
        if API.feedback(h,0,1,1)!=-3:
            raise AssertionError("V32E_FEEDBACK_BEFORE_OBSERVATION_ACCEPTED")
        API.observe_one(h,0)
        if API.feedback(h,3,1,1)!=-2 or API.feedback(h,0,float("nan"),1)!=-2:
            raise AssertionError("V32E_INVALID_ACTION_OR_REWARD_ACCEPTED")
        if API.scores(h,None,3)!=-1:
            raise AssertionError("V32E_NULL_SCORE_BUFFER_ACCEPTED")
        if API.checkpoint(h)!=baseline:
            raise AssertionError("V32E_INVALID_ABI_MODIFIED_NATIVE_LOCAL_WEIGHTS")
    finally:
        API.free(h)


def frozen_native_stage(h):
    checkpoint=API.checkpoint(h)
    ledger=API.ledger(h)
    rows=[]
    for rep in range(24):
        for cue in range(4):
            API.observe_one(h,cue)
            rows.append(API.native_scores(h))
    if API.checkpoint(h)!=checkpoint or API.ledger(h)!=ledger:
        raise AssertionError("V32E_REWARD_BLIND_EVALUATION_CHANGED_PRIVATE_MEMORY")
    diagA=v32b.diagnostics(rows,v32c.A)
    diagB=v32b.diagnostics(rows,v32c.B)
    diagC=v32b.diagnostics(rows,v32c.C)
    return {
        "policies":{"a":{"raw":diagA["original_raw_accuracy"],"eps":diagA["epsilon_stabilized_accuracy"]},
                    "b":{"raw":diagB["original_raw_accuracy"],"eps":diagB["epsilon_stabilized_accuracy"]},
                    "c":{"raw":diagC["original_raw_accuracy"],"eps":diagC["epsilon_stabilized_accuracy"]}},
        "min_score_margin":diagA["min_top_second_margin"],
        "max_abs_score":diagA["max_abs_score"],
        "first_four_f64_hex":diagA["first_four_score_hex"],
        "scores_sha":v32a.scores_hash(rows),
        "checkpoint_sha":hex_sha(checkpoint),
        "ledger":ledger,
        "checkpoint_bytes":checkpoint,
    }


def cold_worker(path):
    h=API.new()
    try:
        API.layout(h)
        src=Path(path).read_bytes()
        if API.restore(h,src):
            raise AssertionError("V32E_NEW_OS_CONTEXT_MEMORY_RELOAD_FAILED")
        stage=frozen_native_stage(h)
        if API.checkpoint(h)!=src:
            raise AssertionError("V32E_COLD_NATIVE_CHECKPOINT_CHANGED")
        rss,meter=actual_os_peak_resident_bytes()
        print(json.dumps({
            "schema":SCHEMA,"role":"fresh_cold_context_memory",
            "host":sys.platform,"binary_sha256":API.binary_sha256,
            "source_sha256":API.source_sha256,
            "checkpoint_sha":stage["checkpoint_sha"],
            "scores_sha":stage["scores_sha"],
            "first_four_f64_hex":stage["first_four_f64_hex"],
            "ledger":stage["ledger"],"policies":stage["policies"],
            "process_cpu_ns":time.process_time_ns(),
            "os_peak_rss_bytes":rss,"os_meter":meter,
        },sort_keys=True,separators=(",",":"),allow_nan=False))
    finally:
        API.free(h)


def cold_launch(stage):
    with tempfile.TemporaryDirectory(prefix="v32d-cold-",dir=os.environ.get("RUNNER_TEMP") or None) as folder:
        path=Path(folder)/"private-two-bank-full-context-checkpoint.bin"
        path.write_bytes(stage["checkpoint_bytes"])
        start=time.perf_counter_ns()
        p=subprocess.run(
            [sys.executable,"-B",str(Path(__file__).resolve()),"--cold",str(path)],
            cwd=ROOT,capture_output=True,text=True,timeout=TIMEOUT,
            check=False,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        wall=time.perf_counter_ns()-start
        if p.returncode or p.stderr.strip():
            raise AssertionError("V32E_COLD_PROCESS_FAILURE_"+p.stderr[-2000:])
        try:d=json.loads(p.stdout)
        except (ValueError,TypeError) as e:raise AssertionError("V32E_COLD_REPORT_NOT_JSON") from e
        for key,val in (("checkpoint_sha",stage["checkpoint_sha"]),
                        ("scores_sha",stage["scores_sha"]),
                        ("first_four_f64_hex",stage["first_four_f64_hex"]),
                        ("ledger",stage["ledger"]),
                        ("policies",stage["policies"]),
                        ("binary_sha256",API.binary_sha256),
                        ("source_sha256",API.source_sha256)):
            if d.get(key)!=val:
                raise AssertionError("V32E_COLD_RESTART_CONTEXT_WEIGHT_SCORE_MISMATCH_"+key)
        if (d.get("role")!="fresh_cold_context_memory"
            or d.get("host")!=sys.platform
            or not d.get("process_cpu_ns",0)>0
            or not d.get("os_peak_rss_bytes",0)>0):
            raise AssertionError("V32E_COLD_OS_IDENTITY_OR_RESOURCE_UNMETERED")
        d["subprocess_wall_ns"]=wall
        return d


def train_new(h,phase,arm,exposures,learn,seed):
    start=time.process_time_ns()
    rewards=[]
    for cue,action,repeat in exposures:
        if phase in ("a","return_a"):
            reward=1.0 if action==v32c.A[cue] else -1.0
        elif arm=="new_sham":
            reward=1.0 if repeat%2==0 else -1.0
        elif arm=="new_shuffled_null":
            rng=random.Random(seed+47000+cue*101+action*17)
            samples=[1.0]*10+[-1.0]*10
            rng.shuffle(samples)
            reward=samples[repeat]
        elif arm=="new_wrong":
            reward=1.0 if action==v32c.C[cue] else -1.0
        else:
            reward=1.0 if action==v32c.B[cue] else -1.0
        API.observe_one(h,cue)
        API.native_scores(h)
        API.feedback_one(h,action,reward,learn)
        rewards.append(reward)
    c=time.process_time_ns()-start
    return {"events":len(exposures),"positive":rewards.count(1.0),
            "negative":rewards.count(-1.0),
            "input_sha":v32c.checksum(exposures),
            "reward_sha":v32c.checksum(rewards),
            "process_training_cpu_ns":c,"training_cpu_quantized":c==0}


def new_worker(arm,seed):
    h=API.new()
    try:
        API.layout(h)
        src_a=v32c.schedule(seed,"a")
        src_b=v32c.schedule(seed,"b")
        src_r=v32c.schedule(seed,"return_a")
        evidence={}
        stages={"before":frozen_native_stage(h)}
        evidence["a240"]=train_new(h,"a",arm,src_a,True,seed)
        stages["after_a240"]=frozen_native_stage(h)
        evidence["b60"]=train_new(h,"b",arm,src_b[:60],arm!="new_frozen",seed)
        stages["after_b60"]=frozen_native_stage(h)
        evidence["b180"]=train_new(h,"b",arm,src_b[60:],arm!="new_frozen",seed)
        stages["after_b240"]=frozen_native_stage(h)
        if arm=="new_adapt":
            evidence["return_a240"]=train_new(h,"return_a",arm,src_r,True,seed)
            stages["after_return_a240"]=frozen_native_stage(h)
        cold={}
        if arm=="new_adapt":
            for stage in ("after_a240","after_b60","after_b240","after_return_a240"):
                cold[stage]=cold_launch(stages[stage])
        # Only immutable evidence, never expose a future target to Rust.
        result={
            "training":evidence,
            "stages":{k:{x:y for x,y in v.items() if x!="checkpoint_bytes"}
                      for k,v in stages.items()},
            "cold":cold,
            "new_native_heap_owners":8,
            "original_only_two_ring_neighbors":True,
            "actual_new_binary":API.binary_sha256,
            "actual_original_rust_binary":v32a.API.binary_sha256,
        }
        return result
    finally:
        API.free(h)


def old_worker(arm,seed):
    if arm=="old_v32d_adapt":
        buffer=io.StringIO()
        with contextlib.redirect_stdout(buffer):
            v32d.fresh_worker("new_adapt",seed)
        try:d=json.loads(buffer.getvalue())
        except (ValueError,TypeError) as e:
            raise AssertionError("V32E_FROZEN_V32D_ADAPT_RECEIPT_MISSING") from e
        if (d.get("schema")!=v32d.SCHEMA or d.get("arm")!="new_adapt"
            or d.get("new_rust_source_sha256")!=v32d.API.source_sha256):
            raise AssertionError("V32E_ORIGINAL_V32D_NEGATIVE_CONTROL_PROVENANCE_DRIFT")
        return d
    kind={"old_adapt":"native_adapt",
          "old_fresh":"native_fresh_b",
          "old_conventional":"conventional"}[arm]
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):
        v32c.fresh_worker(kind,seed)
    try:
        d=json.loads(capture.getvalue())
    except (ValueError,TypeError) as e:
        raise AssertionError("V32E_FROZEN_V32C_CONTROL_NO_SOURCE_RECEIPT") from e
    if (d.get("schema")!=v32c.SCHEMA or d.get("arm")!=kind
        or d.get("source_sha256")!=v32a.API.source_sha256):
        raise AssertionError("V32E_FROZEN_PREDECESSOR_OLD_CONTROL_TAMPERED")
    return d


def fresh_worker(arm,seed):
    if arm not in ARMS or seed not in SEEDS:
        raise ValueError("V32E_UNDECLARED_FROZEN_ARM_OR_SEED")
    result=new_worker(arm,seed) if arm.startswith("new_") else old_worker(arm,seed)
    rss,meter=actual_os_peak_resident_bytes()
    print(json.dumps({
        "schema":SCHEMA,"host":sys.platform,"role":"fresh_control",
        "arm":arm,"seed":seed,
        "new_rust_source_sha256":API.source_sha256,
        "new_rust_binary_sha256":API.binary_sha256,
        "untouched_v32a_rust_source_sha256":v32a.API.source_sha256,
        "original_old_rust_binary_sha256":v32a.API.binary_sha256,
        "source_schedule_a_sha":v32c.checksum(v32c.schedule(seed,"a")),
        "source_schedule_b_sha":v32c.checksum(v32c.schedule(seed,"b")),
        "source_schedule_return_a_sha":v32c.checksum(v32c.schedule(seed,"return_a")),
        "full_worker_cpu_ns_including_native":time.process_time_ns(),
        "os_peak_resident_bytes":rss,"resident_meter":meter,
        "original_v32c_failure_retained":True,
        "original_native_model_modified":False,
        "scientific_first_use":False,
        "result":result
    },sort_keys=True,separators=(",",":"),allow_nan=False))


def launch(arm,seed):
    start=time.perf_counter_ns()
    p=subprocess.run([sys.executable,"-B",str(Path(__file__).resolve()),
         "--worker",arm,str(seed)],cwd=ROOT,capture_output=True,text=True,
         timeout=TIMEOUT,check=False,
         env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
    wall=time.perf_counter_ns()-start
    if p.returncode or p.stderr.strip():
        raise AssertionError("V32E_FRESH_WORKER_FAILED_{}_{}_{}_{}".format(
            arm,seed,p.returncode,p.stderr[-1800:]))
    try:d=json.loads(p.stdout)
    except (TypeError,ValueError) as e:
        raise AssertionError("V32E_WORKER_SOURCE_REPORT_MISSING") from e
    if (d.get("schema")!=SCHEMA or d.get("role")!="fresh_control"
        or d.get("host")!=sys.platform
        or d.get("arm")!=arm or d.get("seed")!=seed
        or d.get("new_rust_source_sha256")!=API.source_sha256
        or d.get("new_rust_binary_sha256")!=API.binary_sha256
        or d.get("untouched_v32a_rust_source_sha256")!=v32a.API.source_sha256
        or d.get("original_old_rust_binary_sha256")!=v32a.API.binary_sha256
        or d.get("original_v32c_failure_retained") is not True
        or d.get("scientific_first_use") is not False
        or d.get("source_schedule_a_sha")!=v32c.checksum(v32c.schedule(seed,"a"))
        or d.get("source_schedule_b_sha")!=v32c.checksum(v32c.schedule(seed,"b"))
        or d.get("source_schedule_return_a_sha")!=v32c.checksum(v32c.schedule(seed,"return_a"))):
        raise AssertionError("V32E_MODEL_WORLD_OR_WORKER_PROVENANCE_CHANGED")
    method=("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform=="linux"
            else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
            if sys.platform=="win32" else None)
    if (d.get("resident_meter")!=method
        or type(d.get("full_worker_cpu_ns_including_native")) is not int
        or d["full_worker_cpu_ns_including_native"]<=0
        or type(d.get("os_peak_resident_bytes")) is not int
        or d["os_peak_resident_bytes"]<=0):
        raise AssertionError("V32E_UNMETERED_REAL_HOST_PROCESS_CPU_OR_RSS")
    d["full_subprocess_wall_ns"]=wall
    return d


def policy(stage,world):
    return stage["policies"][world]["eps"]


def evaluate_seed(seed,arms):
    d,oldD,o,f,p,z,s,r,w=[arms[x]["result"] for x in ARMS]
    if any(
        arms[arm]["source_schedule_b_sha"]!=arms["new_adapt"]["source_schedule_b_sha"]
        for arm in ARMS):
        raise AssertionError("V32E_SCHEDULED_WORLD_EXPOSURES_MISMATCH")
    ds=d["stages"]; zs=z["stages"];ss=s["stages"];rs=r["stages"];ws=w["stages"]
    oldDs=oldD["result"]["stages"]
    os_=o["evaluation_stages"]
    fs=f["evaluation_stages"]
    ps=p["evaluation_stages"]
    ctrl=lambda stages,key,world:stages[key]["policies"][world]["eps_accuracy"]
    def active(stage):
        return stage["ledger"]["active_bank"]
    def switches(stage):
        return stage["ledger"]["switches"]
    def updates(stage):
        return stage["ledger"]["total_updates"]
    switches_ok=(
        active(ds["after_a240"])==[0]*8
        and switches(ds["after_a240"])==[0]*8
        and active(ds["after_b60"])==[1]*8
        and all(x>=1 for x in switches(ds["after_b60"]))
        and active(ds["after_b240"])==[1]*8
        and active(ds["after_return_a240"])==[0]*8
        and all(x>=2 for x in switches(ds["after_return_a240"]))
        and updates(ds["after_a240"])==[240]*8
        and updates(ds["after_b60"])==[300]*8
        and updates(ds["after_b240"])==[480]*8
        and updates(ds["after_return_a240"])==[720]*8
        and switches(zs["after_b240"])==[0]*8
        and switches(ss["after_b240"])==[0]*8
        and switches(rs["after_b240"])==[0]*8
        and updates(zs["after_b240"])==[240]*8
    )
    controls_ok=(
        ctrl(os_,"after_b60","b")<=.25
        and ctrl(os_,"after_b240","b")<=.25
        and policy(oldDs["after_b60"],"b")>=.75
        and ctrl(fs,"after_b60","b")>=.75
        and ctrl(ps,"after_b60","b")<=.25
        and ctrl(ps,"after_b240","b")<=.25
        and policy(zs["after_b240"],"b")<=.25
        and policy(zs["after_b240"],"a")>=.75
        and policy(ss["after_b240"],"b")<=.25
        and policy(ss["after_b240"],"a")>=.75
        and policy(rs["after_b240"],"b")<=.25
        and policy(rs["after_b240"],"a")>=.75
        and policy(ws["after_b240"],"b")<=.25
        and policy(ws["after_b240"],"c")>=.75
    )
    candidate_ok=(
        policy(ds["after_a240"],"a")>=.75
        and policy(ds["after_a240"],"b")<=.25
        and policy(ds["after_b60"],"b")>=.75
        and policy(ds["after_b240"],"b")>=.75
        and policy(ds["after_b240"],"a")<=.25
        and policy(ds["after_return_a240"],"a")>=.75
        and policy(ds["after_return_a240"],"b")<=.25
        and ds["after_b240"]["min_score_margin"]>=1e-6
        and ds["after_return_a240"]["min_score_margin"]>=1e-6
    )
    transfer=(policy(ds["after_b60"],"b")>=ctrl(fs,"after_b60","b"))
    if len(d["cold"])!=4 or any(
        t not in d["cold"] for t in
        ("after_a240","after_b60","after_b240","after_return_a240")):
        raise AssertionError("V32E_FOUR_INDEPENDENT_COLD_PROCESS_GATES_MISSING")
    return {
        "seed":seed,
        "candidate_learning_criteria_pass":candidate_ok,
        "cell_local_context_switch_criteria_pass":switches_ok,
        "matched_original_and_null_controls_pass":controls_ok,
        "early_partial_new_world_transfer_vs_fresh_pass":transfer,
        "new_native_old_world_after_a240":policy(ds["after_a240"],"a"),
        "new_native_new_world_before_feedback":policy(ds["after_a240"],"b"),
        "new_native_new_world_after_b60":policy(ds["after_b60"],"b"),
        "new_native_new_world_after_b240":policy(ds["after_b240"],"b"),
        "new_native_old_world_after_b240":policy(ds["after_b240"],"a"),
        "new_native_restored_old_world_after_return":policy(ds["after_return_a240"],"a"),
        "new_native_new_world_after_return":policy(ds["after_return_a240"],"b"),
        "old_native_new_world_after_b60":ctrl(os_,"after_b60","b"),
        "old_native_new_world_after_b240":ctrl(os_,"after_b240","b"),
        "fresh_native_new_world_after_b60":ctrl(fs,"after_b60","b"),
        "conventional_new_world_after_b60":ctrl(ps,"after_b60","b"),
        "frozen_new_native_new_world_after_b240":policy(zs["after_b240"],"b"),
        "sham_new_native_new_world_after_b240":policy(ss["after_b240"],"b"),
        "sham_old_world_retention_after_b240":policy(ss["after_b240"],"a"),
        "shuffled_null_b_after_b240":policy(rs["after_b240"],"b"),
        "shuffled_null_a_after_b240":policy(rs["after_b240"],"a"),
        "sham_native_switches":switches(ss["after_b240"]),
        "shuffled_native_switches":switches(rs["after_b240"]),
        "prior_v32d_b60_accuracy":policy(oldDs["after_b60"],"b"),
        "prior_v32d_negative_result_retained":True,
        "wrong_c_new_native_true_b_after_b240":policy(ws["after_b240"],"b"),
        "wrong_c_new_native_own_c_after_b240":policy(ws["after_b240"],"c"),
        "cell_bank_by_stage":{k:{"active":v["ledger"]["active_bank"],
                                  "switches":v["ledger"]["switches"],
                                  "ages0":v["ledger"]["bank0_age"],
                                  "ages1":v["ledger"]["bank1_age"],
                                  "total_updates":v["ledger"]["total_updates"],
                                  "checkpoint_sha":v["checkpoint_sha"]}
                              for k,v in ds.items()},
        "all_raw_per_arm_os_resources":{
            arm:{
                "worker_cpu_ns":rec["full_worker_cpu_ns_including_native"],
                "os_peak_resident_bytes":rec["os_peak_resident_bytes"],
                "subprocess_wall_ns":rec["full_subprocess_wall_ns"],
                "independent_cold_receipts":rec["result"].get("cold",{})}
            for arm,rec in arms.items()},
    }


def audit():
    preflight()
    results=[]
    for seed in SEEDS:
        workers={arm:launch(arm,seed) for arm in ARMS}
        results.append(evaluate_seed(seed,workers))
    positive=all(
        q["candidate_learning_criteria_pass"]
        and q["cell_local_context_switch_criteria_pass"]
        and q["matched_original_and_null_controls_pass"]
        and q["early_partial_new_world_transfer_vs_fresh_pass"]
        for q in results)
    print(json.dumps({
        "schema":SCHEMA,"host":sys.platform,"status":"COMPLETE",
        "classification":("V32E_PAIR_CONSENSUS_FALSE_ALARM_RESISTANT_REVERSAL__NO_SCIENCE"
                          if positive else
                          "V32E_PAIR_CONSENSUS_OR_NULL_NEGATIVE__NO_SCIENCE"),
        "new_native_source_sha256":API.source_sha256,
        "new_native_binary_sha256":API.binary_sha256,
        "old_untouched_v32a_rust_source_sha256":v32a.API.source_sha256,
        "old_native_binary_sha256":v32a.API.binary_sha256,
        "old_v32c_failed_contingency_classification_unchanged":True,
        "original_model_untouched":True,"scientific_first_use":False,
        "new_context_switch_requires_no_phase_oracle":True,
        "independently_os_scheduled_eight_learning_cells":False,
        "original_four_known_cue_ids_only":True,
        "new_weight_capacity":192,"unchanged_original_weight_capacity":96,
        "positive_efficiency_or_energy_claimed":False,
        "matched_worker_processes_each_host":9*len(SEEDS),
        "new_native_fresh_cold_processes_each_host":4*len(SEEDS),
        "original_native_cold_processes_are_additional_and_separately_recorded":True,
        "fixed_seeds":SEEDS,"frozen_input_and_credit_steps_per_world":240,
        "evaluation_without_feedback":96,
        "results":results,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        fresh_worker(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==3 and sys.argv[1]=="--cold":
        cold_worker(sys.argv[2])
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V32E_UNKNOWN_ENTRYPOINT")
