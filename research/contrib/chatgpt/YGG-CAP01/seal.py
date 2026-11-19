"""Seal both original native capacity continuation receipts in GitHub.

No second intervention campaign is dispatched. Retain the genuine OS-native
weight bytes and exact prior model SHA, then rebuild G29 at exact evidence SHA.
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
from parity import seal_comparison
from yggdrasil.native_context_basis import canonical

FILES=(
    "result.json","audit.json","timings.json",
    "seed-14071-state.json","seed-14072-state.json",
    "seed-14071-trace.json","seed-14072-trace.json",
    "seed-14071-future.json","seed-14072-future.json",
)

def require(ok,tag):
    if not ok:
        raise ValueError("CAP01_ORIGINAL_SEAL_"+tag)

def main():
    run=os.environ.get("CAP01_RUN","")
    start=os.environ.get("CAP01_SOURCE_SHA","")
    require(run.isdigit() and len(start)==40 and
            all(c in "0123456789abcdef" for c in start),
            "RUN_AND_SOURCE_PROVENANCE")
    dirs={
        "linux":Path(os.environ["CAP01_LINUX_ARTIFACT"]),
        "windows":Path(os.environ["CAP01_WINDOWS_ARTIFACT"]),
    }
    for path in dirs.values():
        require(all((path/name).is_file() for name in FILES),
                "ORIGINAL_ARTIFACT_COMPLETE")
    before=subprocess.check_output([
        "git","rev-parse",
        "d7107c0f63260684ed47fbf1e6baf32c34922fb4:"
        "research/contrib/chatgpt/YGG-CAP01/prereg.json"],
        cwd=ROOT,text=True).strip()
    after=subprocess.check_output([
        "git","rev-parse",
        "HEAD:research/contrib/chatgpt/YGG-CAP01/prereg.json"],
        cwd=ROOT,text=True).strip()
    require(before==after,"PREREG_UNCHANGED")
    receipt=seal_comparison(dirs["linux"],dirs["windows"])
    manifest=[]
    for osname,path in dirs.items():
        report=json.loads((path/"result.json").read_bytes())
        audit=json.loads((path/"audit.json").read_bytes())
        require(report["engineering_development_go"] is True and
                report["scientific_pass"] is False and
                audit["engineering_audit_pass"] is True and
                audit["scientific_pass"] is False and
                [replica["total_count"] for replica in
                 report["replicas"]]==[1054,1029],
                "FROZEN_SCIENCE_AND_CAPACITY_DISPOSITION")
        destination=HERE/"original"/osname
        destination.mkdir(parents=True,exist_ok=True)
        for name in FILES:
            raw=(path/name).read_bytes()
            saved=destination/name
            saved.write_bytes(raw)
            require(saved.read_bytes()==raw,"BYTE_EXACT_ORIGINAL_COPY")
            manifest.append({
                "path":saved.relative_to(ROOT).as_posix(),
                "bytes":len(raw),
                "sha256":hashlib.sha256(raw).hexdigest(),
            })
    (HERE/"result.json").write_bytes(canonical(
        json.loads((dirs["linux"]/"result.json").read_bytes())))
    (HERE/"parity.json").write_bytes(canonical(receipt))
    provenance={
        "schema":"yggdrasil.cap01.original-cumulative-capacity-provenance.v1",
        "first_prereg_sha":"d7107c0f63260684ed47fbf1e6baf32c34922fb4",
        "original_parent_sha":"7b0d9fd8c16b8e0433a632666cec88d8d008c19f",
        "actual_source_execution_sha":start,
        "original_training_run":run,
        "exact_os_original_artifact_members":manifest,
        "engineering_capacity_qualified":True,
        "scientific_pass":False,
        "accepted_native":False,
        "deployment":"NONE",
        "source_scoring_rerun":False,
    }
    (HERE/"provenance.json").write_bytes(canonical(provenance))
    print("YGG_CAP01_ORIGINAL_TWO_PLATFORM_TRAINED_EVIDENCE_SEALED",
          len(manifest),"source",start,"scientific_pass",False,flush=True)

if __name__=="__main__":
    main()
