"""NCI-04D3 development-only native task vs conventional controls.

This is NOT independently sealed scientific first use. Deterministic local
Boolean targets are development fixtures; do not call them unfamiliar laws.
No tuning, optimization loop, network, secret or protected source access.
"""
import json
import math
import os
import random
import sys
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from yggdrasil.task_runtime import LocalTaskRuntime,LocalCountControl

SEEDS=(20260,20261,20262)
LESION=(1,3,5,7)
TRAIN_EVENTS=384
EVAL_EVENTS=128
REPAIR_STEPS=64
def graphs():
    return {
        "ring":tuple(((i-1)%8,(i+1)%8) for i in range(8)),
        "skip":tuple(((i+2)%8,(i+5)%8) for i in range(8)),
        "cross":tuple(((i+1)%8,(i+4)%8) for i in range(8)),
    }

def target(bits,topology):
    result=[]
    for i,(a,b) in enumerate(topology):
        x,y=bits[a],bits[b]
        if i%3==0:result.append(x&y)
        elif i%3==1:result.append(x^y)
        else:result.append(x|y)
    return result

def dataset(seed,n):
    rng=random.Random(seed)
    return [[rng.randrange(2) for _ in range(8)] for _ in range(n)]

def score(pairs,predict):
    s=0.;num=0
    for bits,expect in pairs:
        yhat=predict(bits)
        for y,p in zip(expect,yhat):
            if not math.isfinite(p) or not 0<=p<=1:raise ValueError("invalid probability")
            s+=(p-y)**2;num+=1
    return s/num

def rss_peak_bytes():
    if os.name=="posix":
        import resource
        value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return value if sys.platform=="darwin" else value*1024
    if os.name=="nt":
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_=[("cb",wintypes.DWORD),("PageFaultCount",wintypes.DWORD),
             ("PeakWorkingSetSize",ctypes.c_size_t),("WorkingSetSize",ctypes.c_size_t),
             ("QuotaPeakPagedPoolUsage",ctypes.c_size_t),("QuotaPagedPoolUsage",ctypes.c_size_t),
             ("QuotaPeakNonPagedPoolUsage",ctypes.c_size_t),("QuotaNonPagedPoolUsage",ctypes.c_size_t),
             ("PagefileUsage",ctypes.c_size_t),("PeakPagefileUsage",ctypes.c_size_t)]
        info=Counters()
        info.cb=ctypes.sizeof(info)
        psapi=ctypes.WinDLL("psapi")
        kernel=ctypes.WinDLL("kernel32")
        psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
        if psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(info),info.cb):
            return int(info.PeakWorkingSetSize)
    return None

def run_one(seed,name,graph):
    train=dataset(seed,TRAIN_EVENTS)
    held=dataset(seed+900001,EVAL_EVENTS)
    train_pairs=[(b,target(b,graph)) for b in train]
    test_pairs=[(b,target(b,graph)) for b in held]
    task=LocalTaskRuntime(graph)
    control=LocalCountControl(graph)
    t0=time.process_time()
    for b,y in train_pairs:
        task.observe(b,y)
    train_cpu=time.process_time()-t0
    t1=time.process_time()
    for b,y in train_pairs:
        control.observe(b,y)
    count_train_cpu=time.process_time()-t1
    a=score(test_pairs,task.predict)
    exact=score(test_pairs,control.predict)
    t2=time.process_time()
    task.lesion(LESION)
    drop=score(test_pairs,task.predict)
    no_repair=drop
    damaged_count=LocalCountControl(graph)
    damaged_count.table=[dict(t) for t in control.table]
    for i in LESION:damaged_count.table[i].clear()
    count_lesion=score(test_pairs,damaged_count.predict)
    # Task is not shown true labels after the lesion.
    task.repair_unlabeled(held[0],steps=REPAIR_STEPS)
    repaired=score(test_pairs,task.predict)
    repair_cpu=time.process_time()-t2
    t3=time.process_time()
    for b,y in test_pairs:task.predict(b)
    inference_cpu=time.process_time()-t3
    t4=time.process_time()
    for b,y in test_pairs:control.predict(b)
    count_inference_cpu=time.process_time()-t4
    snapshots=task.snapshot()
    restored=LocalTaskRuntime.restore(snapshots)
    if restored.snapshot()!=snapshots:raise AssertionError("restart snapshot mismatch")
    try:
        task.observe(held[0],target(held[0],graph))
    except ValueError:pass
    else:raise AssertionError("post-damage teaching labels were accepted")
    lost=drop-a
    recovered=drop-repaired
    return {
      "seed":seed,"graph":name,"observations":TRAIN_EVENTS,"heldout":EVAL_EVENTS,
      "learned_pre_damage_brier":a,"control_count_brier":exact,
      "learned_after_lesion_brier":drop,"learned_after_unlabeled_repair_brier":repaired,
      "count_after_matched_cell_erase_brier":count_lesion,
      "learned_no_repair_brier":no_repair,"recovered_fraction":recovered/lost if lost>1e-8 else None,
      "learned_train_cpu_s":train_cpu,"control_train_cpu_s":count_train_cpu,
      "learned_predict_cpu_s":inference_cpu,"control_predict_cpu_s":count_inference_cpu,
      "unlabeled_repair_cpu_s":repair_cpu,
      "learned_snapshot_bytes":len(snapshots.encode("utf-8")),
      "learned_nominal_float_bytes":(3*7+8*3)*8,
      "count_nominal_int_bytes":sum(len(x) for x in control.table)*2*8,
      "count_contexts":sum(len(x) for x in control.table),
      "postdamage_labels_used":0,
    }

def main():
    tracemalloc.start()
    started=time.process_time()
    trials=[run_one(seed,name,g) for name,g in graphs().items() for seed in SEEDS]
    _,heap_peak=tracemalloc.get_traced_memory()
    elapsed=time.process_time()-started
    keys=("learned_pre_damage_brier","control_count_brier",
          "learned_after_lesion_brier","learned_after_unlabeled_repair_brier",
          "count_after_matched_cell_erase_brier")
    summary={k:sum(t[k] for t in trials)/len(trials) for k in keys}
    summary["all_repaired_better_than_damage"]=all(t["learned_after_unlabeled_repair_brier"]<t["learned_after_lesion_brier"] for t in trials)
    summary["all_better_than_conventional"]=all(t["learned_after_unlabeled_repair_brier"]<t["control_count_brier"] for t in trials)
    summary["nominal_model_bytes"]=360
    summary["trial_count"]=len(trials)
    report={"gate":"NCI-04D3","status":"DEVELOPMENT_ONLY_NOT_SCIENTIFIC",
            "configuration":{"seeds":SEEDS,"graphs":list(graphs()),"train_events":TRAIN_EVENTS,
                            "eval_events":EVAL_EVENTS,"repair_steps":REPAIR_STEPS,"lesion":LESION},
            "results":trials,"summary":summary,"resource":{
                "whole_process_cpu_s":elapsed,"whole_process_peak_rss_bytes":rss_peak_bytes(),
                "python_tracemalloc_peak_bytes":heap_peak,
                "note":"Process RSS includes interpreter and all competing implementations; nominal bytes exclude object overhead and code."},
            "admission":{"independent_unfamiliar_task_transfer":False,
                         "equally_trained_neural_control":False,
                         "whole_process_resource_matched":False,
                         "scientific_superiority":"NO_GO"}}
    print("NCI04D3_NATIVE_COMPARISON="+json.dumps(report,sort_keys=True,separators=(",",":")))
    if len(trials)!=9 or not math.isfinite(summary["control_count_brier"]):
        raise SystemExit("NCI04D3_RESULT_INCOMPLETE")
if __name__=="__main__":main()
