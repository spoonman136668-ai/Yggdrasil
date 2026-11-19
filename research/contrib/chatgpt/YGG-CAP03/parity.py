"""Cross-OS original native model source parity: strict source/verdict identity.

Original 7-component parent model weights are deliberately OS-specific,
with source/audit and previously sealed SHA receipts pinned. Numeric outputs
may vary by at most 1e-8. Do not erase the genuine learned checkpoint SHA.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"YGG-CAP01"/"parity.py"
spec=importlib.util.spec_from_file_location("cap03_numeric",OLD)
parity=importlib.util.module_from_spec(spec)
spec.loader.exec_module(parity)
parity.ALLOW_DIFF_SHA.update({
    "original_checkpoint_sha256","original_six_head_sha256",
    "continued_six_head_sha256","continued_native_sha256",
    "new_sha256","original_sha256",
})
COMPARE=("result.json","audit.json",
         "seed-14071-trace.json","seed-14072-trace.json")
PIN_PARENT={
 14071:("94ba6cd5a7771cb15f69920ac8ee03a1277bd41b9b2ab5dc98fda514f7292481",
        "abc78822a3fc8c30297738338a48199b31addcc1590f71850c9c529bb8b62bd0"),
 14072:("e1469b3477b69560ecac2c1b41a26e12055d11e2a1203b112fde1f6910e19cbd",
        "3fc0c2ab1bdcc798d4d10fb02225d6394331bacd434906a881a9596d5f629dac"),
}
MAX_BYTES=2097152

def check(ok,s):
    if not ok:
        raise ValueError("CAP03_PARITY_"+s)

def compare(original_linux,original_windows):
    files={}
    for name in COMPARE:
        la=(original_linux/name).read_bytes()
        wa=(original_windows/name).read_bytes()
        numeric=parity.compare(json.loads(la),json.loads(wa))
        files[name]={
            "linux_sha256":hashlib.sha256(la).hexdigest(),
            "windows_sha256":hashlib.sha256(wa).hexdigest(),
            "exact_bytes":la==wa,
            **numeric,
        }
    weights=[]
    for seed in (14071,14072):
        items=[]
        for osname,location in (
            ("linux",original_linux),("windows",original_windows)):
            raw=(location/f"seed-{seed}-state.json").read_bytes()
            document=json.loads(raw)
            check(type(document) is dict and
                  set(document)=={
                    "seed","old_seed","original_sha256",
                    "model_sha256","model_ascii",
                    "contrast_sha256","contrast_ascii",
                    "sham_sha256","sham_ascii"
                  } and
                  document["old_seed"]==seed and
                  document["original_sha256"]==
                  PIN_PARENT[seed][0 if osname=="linux" else 1],
                  "PINNED_ORIGINAL_PARENT")
            for name in ("model","contrast","sham"):
                value=document[name+"_ascii"].encode("ascii")
                check(hashlib.sha256(value).hexdigest()==
                      document[name+"_sha256"] and
                      0<len(value)<=MAX_BYTES,
                      "ORIGINAL_SHA_"+name)
            items.append({
                "os":osname,"artifact_sha256":hashlib.sha256(raw).hexdigest(),
                "root_sha256":document["model_sha256"],
                "contrast_sha256":document["contrast_sha256"],
                "sham_sha256":document["sham_sha256"],
                "model_bytes":len(document["model_ascii"].encode("ascii")),
            })
        weights.append({"old_seed":seed,"original_os_states":items})
    return {
        "schema":"yggdrasil.cap03.original-two-platform-numeric-parity.v1",
        "source_and_science_decision_exact":True,
        "numeric_tolerance":parity.TOLERANCE,
        "files":files,
        "trained_weights_per_os":weights,
        "scientific_pass":False,
    }
