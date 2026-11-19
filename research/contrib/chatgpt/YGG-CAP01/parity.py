"""Exact source/verdict and bounded numeric cross-platform native audit.

Compare independent scored original training reports + event-by-event readouts.
Original trained model bytes must have the same original hash on both OS.
New trained model SHA may differ because of floating-point arithmetic; preserve
its two actual SHA receipts and independently replay both native checkpoints.
Never normalize or silently rewrite genuine evidence to manufacture parity.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

TOLERANCE=1e-8
ALLOW_DIFF_SHA={
    "trained_six_head_sha256",
    "final_segmented_sha256",
    "continued_sha256",
}
COMPARE_FILES=(
    "result.json","audit.json",
    "seed-14071-trace.json","seed-14072-trace.json",
    "seed-14071-future.json","seed-14072-future.json",
)

def compare(left,right):
    counts={"different_numeric_fields":0,"max_abs_numeric_difference":0.0,
            "numeric_samples":[],"learned_checkpoint_sha_differences":[]}
    def visit(a,b,path="$"):
        if type(a) is not type(b):
            raise ValueError("CAP01_CROSS_OS_TYPE:"+path)
        if type(a) is dict:
            if set(a)!=set(b):
                raise ValueError("CAP01_CROSS_OS_KEYS:"+path)
            for k in sorted(a):
                visit(a[k],b[k],path+"."+k)
        elif type(a) is list:
            if len(a)!=len(b):
                raise ValueError("CAP01_CROSS_OS_COUNT:"+path)
            for i,(x,y) in enumerate(zip(a,b)):
                visit(x,y,path+f"[{i}]")
        elif type(a) is float:
            if not math.isfinite(a) or not math.isfinite(b):
                raise ValueError("CAP01_CROSS_OS_NONFINITE:"+path)
            delta=abs(a-b)
            if delta>TOLERANCE:
                raise ValueError("CAP01_CROSS_OS_FLOAT:"+path+":"+repr(delta))
            if delta:
                counts["different_numeric_fields"]+=1
                counts["max_abs_numeric_difference"]=max(
                    counts["max_abs_numeric_difference"],delta)
                if len(counts["numeric_samples"])<6:
                    counts["numeric_samples"].append(
                        {"path":path,"delta":delta})
        elif a!=b:
            name=path.rsplit(".",1)[-1]
            if (name in ALLOW_DIFF_SHA and type(a) is str and
                    len(a)==len(b)==64 and all(
                        z in "0123456789abcdef" for z in a+b)):
                counts["learned_checkpoint_sha_differences"].append(
                    {"path":path,"linux":a,"windows":b})
            else:
                raise ValueError("CAP01_CROSS_OS_SOURCE_OR_VERDICT:"+path)
    visit(left,right)
    return counts

def seal_comparison(linux,windows):
    files={}
    for name in COMPARE_FILES:
        x=(linux/name).read_bytes()
        y=(windows/name).read_bytes()
        record=compare(json.loads(x),json.loads(y))
        files[name]={
            "linux_sha256":hashlib.sha256(x).hexdigest(),
            "windows_sha256":hashlib.sha256(y).hexdigest(),
            "exact_bytes":x==y,
            **record,
        }
    return {
        "schema":"yggdrasil.cap01.cross-platform-source-verdict-parity.v1",
        "source_and_verdict_match_exact":True,
        "numeric_tolerance":TOLERANCE,
        "per_file":files,
        "scientific_pass":False,
    }
