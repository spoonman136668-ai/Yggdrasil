"""Seal original two-OS CAP03 paired intervention evidence, without retraining.

Input artifacts are from the already finished scored qualification. Save their
exact original bytes, independently verify original source provenance, numeric
score parity and model SHA receipts, then G29 and full regression at final SHA.
"""
from __future__ import annotations
import hashlib,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
from parity import compare
from yggdrasil.native_context_basis import canonical

FILES=("result.json","audit.json","timings.json",
       "seed-14071-state.json","seed-14072-state.json",
       "seed-14071-trace.json","seed-14072-trace.json")
PREREG="f9c5e6d69827e76df27239c421aed01d4229d51b"
PARENT="23429ef8145e88ce3005d5c5df6e87443a3c7dec"

def check(value,label):
    if not value:
        raise ValueError("CAP03_EVIDENCE_SEAL_"+label)

def main():
    run=os.environ.get("CAP03_RUN","")
    sha=os.environ.get("CAP03_SOURCE_SHA","")
    check(run.isdigit() and len(sha)==40 and
          all(c in "0123456789abcdef" for c in sha),
          "ORIGINAL_SOURCE_RUN")
    paths={
        "linux":Path(os.environ["CAP03_LINUX"]),
        "windows":Path(os.environ["CAP03_WINDOWS"]),
    }
    check(all((path/f).is_file() for f in FILES
              for path in paths.values()),"ALL_ORIGINAL_MEMBERS")
    first=subprocess.check_output([
        "git","rev-parse",
        PREREG+":research/contrib/chatgpt/YGG-CAP03/prereg.json"],
        cwd=ROOT,text=True,timeout=20).strip()
    final=subprocess.check_output([
        "git","rev-parse","HEAD:research/contrib/chatgpt/YGG-CAP03/prereg.json"],
        cwd=ROOT,text=True,timeout=20).strip()
    check(first==final,"FROZEN_PREREG")
    parity=compare(paths["linux"],paths["windows"])
    receipts=[]
    for osname,folder in paths.items():
        result=json.loads((folder/"result.json").read_bytes())
        audit=json.loads((folder/"audit.json").read_bytes())
        check(result["scientific_pass"] is False and
              audit["scientific_pass"] is False and
              audit["audit_pass"] is True and
              result["development_go"]==audit["development_go"] and
              [r["total"] for r in result["replicas"]]==[1118,1093] and
              [r["new_matched_fork_outcomes"]
                 for r in result["replicas"]]==[128,128],
              "NATIVE_AND_CAUSAL_SOURCE_DISPOSITION")
        destination=HERE/"original"/osname
        destination.mkdir(parents=True,exist_ok=True)
        for name in FILES:
            data=(folder/name).read_bytes()
            file=destination/name
            file.write_bytes(data)
            check(file.read_bytes()==data,"IMMUTABLE_BYTES")
            receipts.append({
                "path":file.relative_to(ROOT).as_posix(),
                "bytes":len(data),
                "sha256":hashlib.sha256(data).hexdigest(),
            })
    (HERE/"result.json").write_bytes(canonical(
        json.loads((paths["linux"]/"result.json").read_bytes())))
    (HERE/"parity.json").write_bytes(canonical(parity))
    (HERE/"provenance.json").write_bytes(canonical({
        "schema":"yggdrasil.cap03.original-paired-native-evidence.v1",
        "source_sha":sha,"original_qualification_run":run,
        "parent":PARENT,"prereg_commit":PREREG,
        "original_os_artifacts":receipts,
        "development_go":json.loads(
            (paths["linux"]/"result.json").read_bytes()
        )["development_go"],
        "science_pass":False,
        "accepted_model":False,
        "deployment":"NONE",
        "scored_training_replayed":False,
    }))
    print("CAP03_ORIGINAL_TWO_OS_EVIDENCE_SEALED",
          len(receipts),"development_go",
          json.loads((paths["linux"]/"result.json").read_bytes())
          ["development_go"],"scientific_pass",False,flush=True)

if __name__=="__main__":
    main()
