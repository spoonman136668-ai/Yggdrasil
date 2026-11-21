"""Process-separated fixture evaluator, no registered source admission."""
from __future__ import annotations
import ctypes
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

from num05 import canonical, digest, error, target
from numerical_source import FIXTURES, fixture_world
from numerical_scoring import (ARM_NAMES, _new, _predict, head_squared_errors,
                               head_window_report)


def _peak_rss():
    if sys.platform == "win32":
        from ctypes import wintypes
        class Counter(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (k, ctypes.c_size_t) for k in (
                "PeakWorkingSetSize","WorkingSetSize","QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage","QuotaNonPagedPoolUsage",
                "PagefileUsage","PeakPagefileUsage")]
        counter=Counter()
        counter.cb=ctypes.sizeof(counter)
        kernel=ctypes.WinDLL("kernel32",use_last_error=True)
        kernel.GetCurrentProcess.restype=wintypes.HANDLE
        fn=ctypes.WinDLL("psapi",use_last_error=True).GetProcessMemoryInfo
        fn.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counter),wintypes.DWORD]
        fn.restype=wintypes.BOOL
        if not fn(kernel.GetCurrentProcess(),ctypes.byref(counter),counter.cb):
            raise OSError(ctypes.get_last_error(),"GetProcessMemoryInfo")
        return int(counter.PeakWorkingSetSize)
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    raise RuntimeError("NUM06_RSS_PLATFORM_UNQUALIFIED")


def _state(model):
    return model.checkpoint() if hasattr(model,"checkpoint") else canonical(vars(model))


def _restore(name,params,raw,expected_hash):
    if digest(raw)!=expected_hash or len(raw)>300000:
        raise ValueError("NUM06_COLD_HASH")
    model=_new(name,params)
    if hasattr(model,"checkpoint"):
        model=type(model).restore(raw,expected_hash)
    else:
        state=json.loads(raw)
        if type(state) is not dict or canonical(state)!=raw:
            raise ValueError("NUM06_CONTROL_STATE_FORMAT")
        for row in state.get("rows",[]):
            model.observe(row)
    if _state(model)!=raw:
        raise ValueError("NUM06_COLD_STATE_MISMATCH")
    return model


def _cpu_status(ns):
    """Zero delta is unresolved, not evidence of zero computational cost."""
    if type(ns) is not int or ns < 0:
        raise ValueError("NUM06_CPU_COUNTER_INVALID")
    return "BELOW_TIMER_DETECTION" if ns == 0 else "OBSERVED_NONZERO"


def _check_head_accounting(losses,heads):
    if len(losses)!=len(heads) or not losses:
        raise ValueError("NUM06_HEAD_ACCOUNTING")
    for loss,head in zip(losses,heads,strict=True):
        if (type(loss) not in (int,float) or not math.isfinite(loss) or
                type(head) not in (list,tuple) or len(head)!=3 or
                any(type(v) not in (int,float) or not math.isfinite(v) or v<0
                    for v in head) or
                abs(loss-sum(head)/3)>1e-12):
            raise ValueError("NUM06_HEAD_ACCOUNTING")


def _worker(request):
    start_wall=time.perf_counter_ns()
    start_cpu=time.process_time_ns()
    seed=request["seed"]
    if type(seed) is not int or seed not in FIXTURES:
        raise ValueError("NUM06_PROCESS_RESERVED_DENIED")
    name=request["arm"]
    if name not in ARM_NAMES:
        raise ValueError("NUM06_PROCESS_ARM")
    params=tuple(request["params"])
    phase=request["segment"]
    if type(phase) is not int or phase not in (0,1):
        raise ValueError("NUM06_PROCESS_SEGMENT")
    rows,meta=fixture_world(seed)
    boundary=meta["t2"]
    model=_new(name,params)
    start,stop=(0,boundary) if phase==0 else (boundary,len(rows))
    restored=None
    restore_ns=0
    if phase==1:
        raw=request["state"].encode("ascii")
        begin=time.process_time_ns()
        model=_restore(name,params,raw,request["state_sha256"])
        restore_ns=time.process_time_ns()-begin
        restored=digest(_state(model))
    elif set(request)!= {"seed","arm","params","segment"}:
        raise ValueError("NUM06_PROCESS_PREFIX_INPUT")
    pre_forecast=_predict(model,rows[start])
    preds=[]
    losses=[]
    head_losses=[]
    predict_ns=observe_ns=0
    for i in range(start,stop):
        row=rows[i]
        tick=time.process_time_ns()
        prediction=_predict(model,row)
        predict_ns+=time.process_time_ns()-tick
        preds.append(prediction)
        actual=target(row)
        losses.append(error(prediction,actual))
        head_losses.append(head_squared_errors(prediction,actual))
        tick=time.process_time_ns()
        model.observe(row)
        observe_ns+=time.process_time_ns()-tick
    raw=_state(model)
    next_forecast=_predict(model,rows[stop]) if stop<len(rows) else None
    return {"pid":os.getpid(),"segment":phase,"start":start,"stop":stop,
            "source_sha256":digest(canonical(rows)),"rows_sha256":digest(canonical(rows[start:stop])),
            "restored_sha256":restored,"state":raw.decode("ascii"),"state_sha256":digest(raw),
            "first_forecast":pre_forecast,"next_forecast":next_forecast,
            "prediction_sha256":digest(canonical(preds)),"losses":losses,
            "head_losses":head_losses,
            "predict_cpu_ns":predict_ns,"observe_cpu_ns":observe_ns,"restore_cpu_ns":restore_ns,
            "worker_cpu_ns":time.process_time_ns()-start_cpu,
            "worker_wall_ns":time.perf_counter_ns()-start_wall,
            "cpu_reported_resolution_ns":max(1,round(time.get_clock_info("process_time").resolution*1e9)),
            "peak_rss_bytes":_peak_rss()}


def _launch(request):
    result=subprocess.run([sys.executable,"-B",str(Path(__file__).resolve()),"--worker"],
                          input=canonical(request),capture_output=True,check=True,timeout=120)
    return json.loads(result.stdout)


def score_process_fixture(seed,name,params=(.02,.04,.5)):
    if type(seed) is not int or seed not in FIXTURES:
        raise ValueError("NUM06_PROCESS_RESERVED_DENIED")
    if name not in ARM_NAMES:
        raise ValueError("NUM06_PROCESS_ARM")
    rows,meta=fixture_world(seed)
    request={"seed":seed,"arm":name,"params":list(params),"segment":0}
    start_wall=time.perf_counter_ns()
    first=_launch(request)
    # subprocess.run has returned; the original learner process has exited.
    second=_launch(dict(request,segment=1,state=first["state"],state_sha256=first["state_sha256"]))
    source=digest(canonical(rows))
    t1,t2=meta["t1"],meta["t2"]
    if not (first["pid"]!=second["pid"] and first["start"]==0 and
            first["stop"]==second["start"]==t2 and second["stop"]==len(rows) and
            first["source_sha256"]==second["source_sha256"]==source and
            first["rows_sha256"]==digest(canonical(rows[:t2])) and
            second["rows_sha256"]==digest(canonical(rows[t2:])) and
            second["restored_sha256"]==first["state_sha256"] and
            first["next_forecast"]==second["first_forecast"]):
        raise ValueError("NUM06_PROCESS_COLD_PARITY")
    elapsed_wall=time.perf_counter_ns()-start_wall
    cpu=sum(q["worker_cpu_ns"] for q in (first,second))
    components={k:sum(q[k] for q in (first,second)) for k in
                ("predict_cpu_ns","observe_cpu_ns","restore_cpu_ns")}
    component_status={k:_cpu_status(v) for k,v in components.items()}
    losses=first["losses"]+second["losses"]
    heads=first["head_losses"]+second["head_losses"]
    _check_head_accounting(losses,heads)
    if len(losses)!=len(rows):
        raise ValueError("NUM06_PROCESS_WITNESS_COUNT")
    avg=lambda seq:sum(seq)/len(seq)
    late,back=avg(losses[t1+80:t2]),avg(losses[t2+32:])
    return {"arm":name,"classification":"FIXTURE_ONLY","source_sha256":source,
            "witness_count":len(losses),"full_mse":avg(losses),"late_mse":late,
            "return_mse":back,"pooled_mse":(late+back)/2,
            **head_window_report(heads,t1,t2),
            "cold_exact":True,"cold_process_ids":[first["pid"],second["pid"]],
            "cold_state_sha256":first["state_sha256"],
            "final_state_sha256":second["state_sha256"],
            "cold_state_bytes":len(first["state"].encode("ascii")),
            "final_state_bytes":len(second["state"].encode("ascii")),
            **components,"cpu_component_status":component_status,
            "worker_cpu_ns":cpu,"worker_cpu_status":_cpu_status(cpu),
            "cpu_reported_resolution_ns":max(q["cpu_reported_resolution_ns"] for q in (first,second)),
            "worker_wall_ns":sum(q["worker_wall_ns"] for q in (first,second)),
            "elapsed_wall_ns":elapsed_wall,
            "peak_rss_bytes":max(first["peak_rss_bytes"],second["peak_rss_bytes"]),
            "rss_scope":"max isolated worker process peak, includes interpreter/source/evaluator",
            "registered_cohorts_consumed":0,"resource_qualification":False,
            "source_owner_authenticated":False,"scientific_gain_verified":False}


if __name__=="__main__":
    if sys.argv[1:]!=["--worker"]:
        raise SystemExit("NUM06_FIXTURE_WORKER_ONLY")
    sys.stdout.buffer.write(canonical(_worker(json.load(sys.stdin))))
