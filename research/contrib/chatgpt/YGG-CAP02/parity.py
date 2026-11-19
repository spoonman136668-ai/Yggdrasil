"""Strict cross-OS original source, decision, numeric and real SHA comparison.

The generic original CAP01 verifier is reused for exact nonnumeric source
fields and frozen verdict. New native/selector checkpoint hashes may differ
slightly because of floating-point learned updates; their actual bytes and
SHA256 are kept. No science threshold is relaxed.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
COMMON=HERE.parent/"YGG-CAP01"/"parity.py"
spec=importlib.util.spec_from_file_location("cap02_pinned_generic_parity",COMMON)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ALLOWED=(
    "continued_checkpoint_sha256","model_sha256",
    "gate_sha256","sham_sha256","source_checkpoint_sha256"
)
mod.ALLOW_DIFF_SHA.update(ALLOWED)
COMPARE_FILES=(
    "result.json","audit.json",
    "seed-14071-trace.json","seed-14072-trace.json"
)
MAX_ORIGINAL=2*1024*1024

def require(cond,name):
    if not cond:
        raise ValueError("CAP02_PARITY_"+name)

def compare_paths(linux,windows):
    receipts={}
    for name in COMPARE_FILES:
        lb=(linux/name).read_bytes()
        wb=(windows/name).read_bytes()
        details=mod.compare(json.loads(lb),json.loads(wb))
        receipts[name]={
            "original_linux_sha256":hashlib.sha256(lb).hexdigest(),
            "original_windows_sha256":hashlib.sha256(wb).hexdigest(),
            "byte_identical":lb==wb,
            **details
        }
    weights=[]
    for seed in (14071,14072):
        name=f"seed-{seed}-state.json"
        x=(linux/name).read_bytes()
        y=(windows/name).read_bytes()
        a=json.loads(x);b=json.loads(y)
        require(set(a)==set(b) and
                a["old_sha256"]==b["old_sha256"] and
                a["seed"]==b["seed"] and
                a["old_seed"]==b["old_seed"],
                "ORIGINAL_TRAINED_MODEL_CUSTODY")
        models=[]
        for item,raw in ((a,x),(b,y)):
            require(len(raw)<=MAX_ORIGINAL and
                    hashlib.sha256(item["model_ascii"].encode("ascii"))
                    .hexdigest()==item["model_sha256"] and
                    hashlib.sha256(item["gate_ascii"].encode("ascii"))
                    .hexdigest()==item["gate_sha256"] and
                    hashlib.sha256(item["sham_ascii"].encode("ascii"))
                    .hexdigest()==item["sham_sha256"],
                    "ORIGINAL_COLD_MODEL_EVIDENCE")
            models.append({
                "sha256":hashlib.sha256(raw).hexdigest(),
                "model_sha256":item["model_sha256"],
                "gate_sha256":item["gate_sha256"],
                "sham_sha256":item["sham_sha256"],
                "model_bytes":len(item["model_ascii"].encode("ascii")),
            })
        weights.append({
            "seed":seed,"linux":models[0],"windows":models[1],
            "original_exact":x==y
        })
    return {
        "schema":"yggdrasil.cap02.original-cross-os-evidence-parity.v1",
        "source_verdict_exact":True,
        "numeric_tolerance":mod.TOLERANCE,
        "files":receipts,"original_trained_checkpoints":weights,
        "scientific_pass":False
    }
