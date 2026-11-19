"""CAP02 original two-OS source, science and numeric receipt parity.

Both OS produce their OWN genuine trained checkpoints. Source / public
intervention IDs, target, regime-tagged EVALUATOR LABELS and scientific
disposition must be exact. Legitimate platform/archived parent SHA identities
are frozen here, not inferred from arbitrary scores. Learned SHA and serialized
weights are retained per-OS, never normalized to conceal a discrepancy.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

TOL=1e-8
LEN_DELTA_LIMIT=32768
PARENT_SHA_PAIRS={
    0:("6babc23f4baf30afde14db5f2ca8eb3e55e321169aa245482478ff9855b68f14",
       "2d08c7e2d6d4d80acfc53727cdd0880d3f632c0f44bdb405b78feffba405938e"),
    1:("c503ccf979f90d6d4954f0e8d42133fc177017d4b47de80ee64c9524b870d827",
       "e09b0cbbe47b95686f3ed3732baf080fe6b47301f0128c360437bf29bf9dfbfb"),
}
NEW_SHA_FIELDS={
    "native_continued_sha256","causal_memory_sha256",
    "new_continued_sha256",
}
BYTE_FIELDS={"native_checkpoint_bytes","memory_checkpoint_bytes"}
ORIGINAL_REF_FIELDS={"old_training_checkpoint_sha256",
                     "original_checkpoint_sha256"}
PLATFORM_FIELDS={"platform","os"}
FILES=("result.json","audit.json",
       "seed-14071-trace.json","seed-14072-trace.json")

def check(ok,code):
    if not ok:
        raise ValueError("CAP02_CROSS_OS_"+code)

def compare(left,right):
    stats={"numeric_count":0,"max_abs_difference":0.0,
           "numeric_examples":[],"trained_sha_receipts":[],
           "original_source_receipts":[],"checkpoint_byte_receipts":[]}
    def walk(a,b,path):
        check(type(a) is type(b),"TYPE:"+path)
        if type(a) is dict:
            check(set(a)==set(b),"FIELDS:"+path)
            for key in sorted(a):
                walk(a[key],b[key],path+"."+key)
        elif type(a) is list:
            check(len(a)==len(b),"COUNT:"+path)
            for i,(x,y) in enumerate(zip(a,b)):
                walk(x,y,path+"["+str(i)+"]")
        elif type(a) is float:
            check(math.isfinite(a) and math.isfinite(b),
                  "NONFINITE:"+path)
            d=abs(a-b)
            check(d<=TOL,"FLOAT_DRIFT:"+path)
            if d:
                stats["numeric_count"]+=1
                stats["max_abs_difference"]=max(stats["max_abs_difference"],d)
                if len(stats["numeric_examples"])<8:
                    stats["numeric_examples"].append({"path":path,"delta":d})
        elif a!=b:
            key=path.rsplit(".",1)[-1]
            if key in PLATFORM_FIELDS:
                check((a,b)==("linux","windows"),
                      "PLATFORM_SOURCE:"+path)
            elif key in ORIGINAL_REF_FIELDS:
                row=0 if "[0]" in path else 1 if "[1]" in path else -1
                check(row in PARENT_SHA_PAIRS and
                      (a,b)==PARENT_SHA_PAIRS[row],
                      "ORIGINAL_PUBLISHED_SOURCE_SHA:"+path)
                stats["original_source_receipts"].append(
                    {"path":path,"linux":a,"windows":b})
            elif key in NEW_SHA_FIELDS:
                check(type(a) is str and len(a)==len(b)==64 and
                      all(c in "0123456789abcdef" for c in a+b),
                      "TRAINED_SHA_FORMAT:"+path)
                stats["trained_sha_receipts"].append(
                    {"path":path,"linux":a,"windows":b})
            elif key in BYTE_FIELDS:
                check(type(a) is int and 0<a<=2*1024*1024 and
                      0<b<=2*1024*1024 and
                      abs(a-b)<=LEN_DELTA_LIMIT,
                      "CHECKPOINT_BYTE_SIZE:"+path)
                stats["checkpoint_byte_receipts"].append(
                    {"path":path,"linux":a,"windows":b,
                     "difference":abs(a-b)})
            else:
                raise ValueError("CAP02_CROSS_OS_EXACT_SOURCE_OR_VERDICT:"+path)
    walk(left,right,"$")
    return stats

def check_originals(linux:Path,windows:Path):
    documents={}
    for filename in FILES:
        x=(linux/filename).read_bytes()
        y=(windows/filename).read_bytes()
        source=compare(json.loads(x),json.loads(y))
        documents[filename]={
            "linux_sha256":hashlib.sha256(x).hexdigest(),
            "windows_sha256":hashlib.sha256(y).hexdigest(),
            "identical_bytes":x==y,
            **source,
        }
    return {
        "schema":"yggdrasil.cap02.original-cross-platform-public-evidence.v1",
        "numeric_tolerance":TOL,
        "source_and_scientific_verdict_exact":True,
        "per_document":documents,
        "scientific_pass":False,
    }
