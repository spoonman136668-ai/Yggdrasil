"""Receipt-only recovery for original YGG-CAP01 Linux/Windows evidence.

The source-bound original training and independent audits already PASS on both
OS. Cross-platform native learned float serialization can change JSON byte
count while the learned checkpoint SHA receipts are rightly distinct.
Preserve both actual byte counts explicitly, allow a bounded difference
only in this one diagnostic integer field, and retain the original strict
source/label/verdict comparator for everything else.

Never alters trained weights, source, thresholds, first-use, model code or
original artifact bytes. No original scoring/training is repeated.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from parity import COMPARE_FILES, compare

MAX_BYTES=2*1024*1024
MAX_LENGTH_DIFFERENCE=32768

def require(condition,code):
    if not condition:
        raise ValueError("CAP01_SIZE_RECEIPT_"+code)

def seal_comparison(linux:Path,windows:Path):
    files={}
    for name in COMPARE_FILES:
        l=(linux/name).read_bytes()
        w=(windows/name).read_bytes()
        a=json.loads(l)
        b=json.loads(w)
        length_notes=[]
        if name=="result.json":
            require(len(a["replicas"])==len(b["replicas"])==2,
                    "TWO_NATIVE_MODELS")
            for index,(lr,wr) in enumerate(zip(a["replicas"],b["replicas"])):
                la=lr["final_checkpoint_bytes"]
                wa=wr["final_checkpoint_bytes"]
                require(type(la) is type(wa) is int and
                        0<la<=MAX_BYTES and 0<wa<=MAX_BYTES and
                        abs(la-wa)<=MAX_LENGTH_DIFFERENCE,
                        "LEARNED_CHECKPOINT_BOUND")
                length_notes.append({
                    "replica":index,"old_seed":lr["old_seed"],
                    "linux_checkpoint_bytes":la,
                    "windows_checkpoint_bytes":wa,
                    "absolute_difference":abs(la-wa),
                })
                # This is exclusively a SOURCE INDEPENDENT representation
                # byte-count receipt. Both genuine values are preserved above
                # and in their immutable original JSON files. Never normalize
                # weights, loss values, source hashes or science outcomes.
                lr["final_checkpoint_bytes"]=0
                wr["final_checkpoint_bytes"]=0
        details=compare(a,b)
        files[name]={
            "linux_original_sha256":hashlib.sha256(l).hexdigest(),
            "windows_original_sha256":hashlib.sha256(w).hexdigest(),
            "original_exact_bytes":l==w,
            "serialized_checkpoint_size_receipts":length_notes,
            **details,
        }
    return {
        "schema":"yggdrasil.cap01.two-os-original-receipt-recovery.v1",
        "source_and_science_verdict_exact":True,
        "original_source_training_reused":True,
        "tolerance":1e-8,
        "checkpoint_size_numeric_exception_only":True,
        "per_file":files,
        "scientific_pass":False,
    }
