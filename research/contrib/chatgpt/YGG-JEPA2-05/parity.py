"""Numeric cross-OS source and scored-evidence parity with explicit ULP disclosure.

Only per-OS trained-weight SHA fields may differ; original checkpoint hashes,
source IDs, episode order, counts, controls and verdict must agree exactly.
No new training is performed by this verifier.
"""
import hashlib
import json
import math
from pathlib import Path

TOLERANCE = 1e-8
ALLOW_DIFFERENT_SHA = frozenset({
    "updated_model_sha256", "final_future_heads_sha256",
    "updated_native_sha256",
})
FILES = ("result.json", "audit.json",
         "seed-14071-trace.json", "seed-14072-trace.json",
         "seed-14071-replay.json", "seed-14072-replay.json")

def compare(a, b):
    state = {"number_differences":0,"max_abs_diff":0.,
             "sha_difference_fields":[],"numeric_example_diffs":[]}
    def descend(x,y,path="$"):
        if type(x) is not type(y):
            raise ValueError("JEPA205_PARITY_TYPE:"+path)
        if type(x) is dict:
            if set(x) != set(y):
                raise ValueError("JEPA205_PARITY_KEYS:"+path)
            for k in sorted(x):
                descend(x[k],y[k],path+"."+k)
        elif type(x) is list:
            if len(x)!=len(y):
                raise ValueError("JEPA205_PARITY_COUNT:"+path)
            for i,(u,v) in enumerate(zip(x,y)):
                descend(u,v,path+"["+str(i)+"]")
        elif type(x) is float:
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("JEPA205_PARITY_NONFINITE:"+path)
            delta=abs(x-y)
            if delta > TOLERANCE:
                raise ValueError("JEPA205_PARITY_FLOAT:"+path+"="+repr(delta))
            if delta:
                state["number_differences"]+=1
                state["max_abs_diff"]=max(state["max_abs_diff"],delta)
                if len(state["numeric_example_diffs"])<8:
                    state["numeric_example_diffs"].append(
                        {"path":path,"delta":delta})
        elif x!=y:
            name=path.split(".")[-1]
            if name in ALLOW_DIFFERENT_SHA and type(x) is str and \
               len(x)==len(y)==64 and all(
                   z in "0123456789abcdef" for z in x+y):
                state["sha_difference_fields"].append({
                    "path":path,"linux_sha256":x,"windows_sha256":y})
            else:
                raise ValueError("JEPA205_PARITY_EXACT:"+path)
    descend(a,b)
    return state

def verify(linux,windows):
    files={}
    for name in FILES:
        p=linux/name
        q=windows/name
        source=p.read_bytes()
        other=q.read_bytes()
        info=compare(json.loads(source),json.loads(other))
        files[name]={
            "linux_sha256":hashlib.sha256(source).hexdigest(),
            "windows_sha256":hashlib.sha256(other).hexdigest(),
            "exact_binary_parity":source==other,
            **info,
        }
    return {"schema":"yggdrasil.jepa2-05.cross-os-original-parity.v1",
            "numeric_tolerance":TOLERANCE,"per_file":files,
            "all_original_input_source_and_verdict_exact":True,
            "science_pass":False}
