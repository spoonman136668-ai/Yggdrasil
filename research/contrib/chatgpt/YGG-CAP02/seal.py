"""Seal original completed CAP02 Linux/Windows training evidence without rerun."""
from __future__ import annotations
import hashlib,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
from parity import compare_paths
from yggdrasil.native_context_basis import canonical

FILES=("result.json","audit.json","timings.json",
       "seed-14071-state.json","seed-14072-state.json",
       "seed-14071-trace.json","seed-14072-trace.json")
PREREG="99ec70e48d09df724a32fa0384c3aa5ef18c0b2e"
PARENT="3770e660bc8b908218e6fe82e176bd4bf91158d9"
def check(ok,code):
    if not ok:raise ValueError("CAP02_SEAL_"+code)

def main():
    run=os.environ.get("CAP02_RUN","")
    source=os.environ.get("CAP02_SOURCE_SHA","")
    check(run.isdigit() and len(source)==40,"RUN_CUSTODY")
    linux=Path(os.environ["CAP02_LINUX"])
    windows=Path(os.environ["CAP02_WINDOWS"])
    check(all((path/name).is_file() for name in FILES
              for path in (linux,windows)),"ALL_ORIGINAL_MEMBERS")
    prior=subprocess.check_output([
        "git","rev-parse",
        PREREG+":research/contrib/chatgpt/YGG-CAP02/prereg.json"],
        cwd=ROOT,text=True).strip()
    now=subprocess.check_output([
        "git","rev-parse","HEAD:research/contrib/chatgpt/YGG-CAP02/prereg.json"],
        cwd=ROOT,text=True).strip()
    check(prior==now,"ORIGINAL_PREREG_NOT_CHANGED")
    parity=compare_paths(linux,windows)
    originals=[]
    for name,path in (("linux",linux),("windows",windows)):
        result=json.loads((path/"result.json").read_bytes())
        audit=json.loads((path/"audit.json").read_bytes())
        check(result["scientific_pass"] is False and
              result["development_go"]==audit["development_go"] and
              audit["engineering_audit_pass"] is True and
              audit["scientific_pass"] is False and
              [x["total"] for x in result["replicas"]]==[1086,1061],
              "ACTUAL_SOURCE_OUTCOMES_AND_SCIENCE")
        dest=HERE/"original"/name
        dest.mkdir(parents=True,exist_ok=True)
        for f in FILES:
            raw=(path/f).read_bytes()
            target=dest/f
            target.write_bytes(raw)
            check(target.read_bytes()==raw,"ORIGINAL_BYTE_COPY")
            originals.append({
                "path":target.relative_to(ROOT).as_posix(),
                "sha256":hashlib.sha256(raw).hexdigest(),
                "bytes":len(raw)
            })
    (HERE/"result.json").write_bytes(canonical(
        json.loads((linux/"result.json").read_bytes())))
    (HERE/"parity.json").write_bytes(canonical(parity))
    (HERE/"provenance.json").write_bytes(canonical({
        "schema":"yggdrasil.cap02.sealed-original-two-os-development.v1",
        "original_training_run":run,"original_source_sha":source,
        "frozen_prereg_commit":PREREG,"parent_sha":PARENT,
        "original_members":originals,"science_pass":False,
        "development_go":json.loads((linux/"result.json").read_bytes())
            ["development_go"],"accepted_model":False,
        "source_retrained_in_seal":False,"deployment":"NONE"
    }))
    print("CAP02_ORIGINAL_TWO_OS_EVIDENCE_SEALED",
          len(originals),"development_go",
          json.loads((linux/"result.json").read_bytes())["development_go"],
          "SCIENCE_NOT_PASS",flush=True)

if __name__=="__main__":
    main()
