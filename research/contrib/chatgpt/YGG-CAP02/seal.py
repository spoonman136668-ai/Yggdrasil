"""Seal ORIGINAL scored CAP02 Linux/Windows native/causal source artifacts.

Does not run campaign.py, derive new source actions, tune a condition, or
replace raw checkpoint bytes. Original two-OS prequential evidence and saved
parameters are copied byte-for-byte and named in a reproducible SHA manifest.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
from parity import check_originals
from yggdrasil.native_context_basis import canonical

FILES=(
    "result.json","audit.json","timings.json",
    "seed-14071-state.json","seed-14072-state.json",
    "seed-14071-trace.json","seed-14072-trace.json",
)
PREREG_SHA="d07b9ac4448b4c23288f4f9a76aec7f2c69faa55"
SOURCE_BLOB="bcae839c6f43ecf14fc1a1a2f3ce7ac813f501bf"

def check(ok,code):
    if not ok:
        raise ValueError("CAP02_ORIGINAL_EVIDENCE_SEAL_"+code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    identity=os.environ.get("CAP02_SOURCE_SHA","")
    source_run=os.environ.get("CAP02_RUN","")
    check(len(identity)==40 and all(c in "0123456789abcdef"
          for c in identity) and source_run.isdigit(),
          "SOURCE_RUN_PROVENANCE")
    linux=Path(os.environ["CAP02_LINUX_ARTIFACT"])
    windows=Path(os.environ["CAP02_WINDOWS_ARTIFACT"])
    for d in (linux,windows):
        check(all((d/f).is_file() for f in FILES),
              "COMPLETE_ORIGINAL_MEMBER_SET")
    prereg=subprocess.check_output([
        "git","rev-parse",PREREG_SHA+
        ":research/contrib/chatgpt/YGG-CAP02/prereg.json"],
        cwd=ROOT,text=True,timeout=30).strip()
    frozen=subprocess.check_output([
        "git","rev-parse",
        "HEAD:research/contrib/chatgpt/YGG-CAP02/prereg.json"],
        cwd=ROOT,text=True,timeout=30).strip()
    source=subprocess.check_output([
        "git","rev-parse",
        "HEAD:research/contrib/chatgpt/YGG-CAP02/source.py"],
        cwd=ROOT,text=True,timeout=30).strip()
    check(prereg==frozen and source==SOURCE_BLOB,
          "FROZEN_BEFORE_EVIDENCE")

    parity=check_originals(linux,windows)
    committed=[]
    for osname,location in (("linux",linux),("windows",windows)):
        result=json.loads((location/"result.json").read_bytes())
        audit=json.loads((location/"audit.json").read_bytes())
        check(result["development_go"]==audit["development_go"] and
              result["scientific_pass"] is False and
              audit["scientific_pass"] is False and
              audit["engineering_audit"] is True and
              [r["new_seed"] for r in result["replicas"]]==[99811,99829] and
              [r["new_interventions"] for r in result["replicas"]]==[48,48] and
              [r["continued_total"] for r in result["replicas"]]==[1102,1077] and
              [r["platform"] for r in result["replicas"]]==[osname,osname],
              "CORRECT_SCIENCE_DECISION_AND_ACTUAL_CUSTODY")
        target=HERE/"original"/osname
        target.mkdir(parents=True,exist_ok=True)
        for file in FILES:
            contents=(location/file).read_bytes()
            dest=target/file
            dest.write_bytes(contents)
            check(dest.read_bytes()==contents,"ORIGINAL_EXACT_COPY")
            committed.append({
                "path":dest.relative_to(ROOT).as_posix(),
                "bytes":len(contents),
                "sha256":sha(contents),
            })
    result=json.loads((linux/"result.json").read_bytes())
    (HERE/"result.json").write_bytes(canonical(result))
    (HERE/"parity.json").write_bytes(canonical(parity))
    proven={
        "schema":"yggdrasil.cap02.original-two-platform-causal-provenance.v1",
        "source_run":source_run,
        "source_sha":identity,
        "original_parent_sha":"3770e660bc8b908218e6fe82e176bd4bf91158d9",
        "preregistered_first_sha":PREREG_SHA,
        "source_blob":SOURCE_BLOB,
        "original_training_artifact_members":committed,
        "both_independent_audits":True,
        "training_rerun":False,
        "development_go":result["development_go"],
        "scientific_pass":False,
        "accepted_native":False,
        "deployment":"NONE",
    }
    (HERE/"provenance.json").write_bytes(canonical(proven))
    print("YGG_CAP02_ORIGINAL_EVIDENCE_SEALED",len(committed),
          "source_run",source_run,
          "development_go",result["development_go"],
          "scientific_pass",False,flush=True)

if __name__=="__main__":
    main()
