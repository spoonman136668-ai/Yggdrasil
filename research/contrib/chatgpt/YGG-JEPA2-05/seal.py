"""Seal two independent original JEPA2-05 training artifacts without retraining."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0,str(HERE))
from parity import verify
from yggdrasil.native_context_basis import canonical

FILENAMES = (
    "result.json","audit.json","timings.json",
    "seed-14071-state.json","seed-14072-state.json",
    "seed-14071-trace.json","seed-14072-trace.json",
    "seed-14071-replay.json","seed-14072-replay.json",
)

def require(cond,label):
    if not cond:
        raise ValueError("YGG_JEPA205_SEAL_"+label)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    source=os.environ.get("YGG_205_SOURCE")
    run=os.environ.get("YGG_205_RUN")
    require(source is not None and len(source)==40
            and run is not None and run.isdigit(), "ENV")
    linux=Path(os.environ["YGG_205_LINUX"])
    windows=Path(os.environ["YGG_205_WINDOWS"])
    require(all((root/name).is_file() for root in (linux,windows)
                for name in FILENAMES), "COMPLETE_SOURCE_ARTIFACTS")
    prereg=subprocess.check_output([
        "git","rev-parse",
        "d0fa25aad2c6dc270eb0f863b6e93cbb89092f23:"
        "research/contrib/chatgpt/YGG-JEPA2-05/prereg.json"],
        cwd=ROOT,text=True).strip()
    frozen=subprocess.check_output([
        "git","rev-parse",
        "HEAD:research/contrib/chatgpt/YGG-JEPA2-05/prereg.json"],
        cwd=ROOT,text=True).strip()
    require(frozen==prereg, "PREREG_FROZEN")

    result_a=json.loads((linux/"result.json").read_bytes())
    result_b=json.loads((windows/"result.json").read_bytes())
    audit_a=json.loads((linux/"audit.json").read_bytes())
    audit_b=json.loads((windows/"audit.json").read_bytes())
    for scored,audited in ((result_a,audit_a),(result_b,audit_b)):
        require(scored["science_pass"] is False and
                scored["accepted_native"] is False and
                audited["engineering_audit"] is True and
                audited["science_pass"] is False and
                scored["development_go"]==audited["development_go"]
                and scored["prereg_first_sha"] ==
                    "d0fa25aad2c6dc270eb0f863b6e93cbb89092f23",
                "EVIDENCE_DISPOSITION_MATCH")
        require(len(scored["replicas"])==2 and
                [x["seed"] for x in scored["replicas"]]==[99231,99247],
                "SOURCE_SEED_CUSTODY")

    parity=verify(linux,windows)
    manifest=[]
    for platform,root in (("linux",linux),("windows",windows)):
        target=HERE/"original"/platform
        target.mkdir(parents=True,exist_ok=True)
        for filename in FILENAMES:
            source_bytes=(root/filename).read_bytes()
            dest=target/filename
            dest.write_bytes(source_bytes)
            require(dest.read_bytes()==source_bytes, "EXACT_ORIGINAL_COPY")
            manifest.append({
                "path":dest.relative_to(ROOT).as_posix(),
                "bytes":len(source_bytes),
                "sha256":digest(source_bytes),
            })

    (HERE/"result.json").write_bytes(canonical(result_a))
    (HERE/"parity.json").write_bytes(canonical(parity))
    provenance={
        "schema":"yggdrasil.jepa2-05.original-development-provenance.v1",
        "source_commit":source,
        "original_training_run":run,
        "prereg_first_sha":"d0fa25aad2c6dc270eb0f863b6e93cbb89092f23",
        "parent_exact_sha":"84bb01dc6b8cfe0a729db30f8637265aa38fd97e",
        "original_sha256_receipts":manifest,
        "independent_two_os_audit":True,
        "matched_controls":True,
        "development_go":result_a["development_go"],
        "science_pass":False,
        "accepted_model":False,
        "deployment":"NONE",
        "scored_original_rerun":False,
    }
    (HERE/"provenance.json").write_bytes(canonical(provenance))
    print("YGG_JEPA2_05_TWO_PLATFORM_EVIDENCE_SEALED",
          "original_members",len(manifest),
          "development_go",result_a["development_go"],
          "science_pass",False,flush=True)

if __name__=="__main__":
    main()
