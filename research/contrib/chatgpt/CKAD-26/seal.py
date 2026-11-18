"""Seal CKAD26 exact cross-platform public traces and cold native checkpoints."""
import gzip
from itertools import product
import json
import os
from pathlib import Path
import subprocess

import audit

HERE=Path(__file__).resolve().parent
PARENT=audit.BASE_SHA
PREREG="a2d91989773a062d581a8290bf4f6da2ace75746"


def need(b,code):
    if not b:raise ValueError("CKAD26_SEAL_"+code)


def persist(name,obj):
    (HERE/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")


def compressed(path,raw):
    (HERE/path).write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
    need(gzip.decompress((HERE/path).read_bytes())==raw,
         "LOSSLESS_SOURCE")
    return (HERE/path).stat().st_size


def seal():
    sha=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    for ancestor in (PARENT,PREREG):
        subprocess.run(["git","merge-base","--is-ancestor",ancestor,sha],check=True)
    p=audit.protocol()
    root=Path(os.environ["CKAD26_ARTIFACT_ROOT"])
    cases=[]
    compressed_bytes=0
    checkpoint_custody=[]
    for name,seed in product(audit.SCHEDULES,audit.SEEDS):
        both=[]
        for osname in ("ubuntu-latest","windows-2022"):
            folder=root/f"ckad26-{osname}-{name}-{seed}-proof"
            trace=folder/"case-result.json"
            model=folder/f"{name}-{seed}-native.json"
            need(trace.is_file() and model.is_file(),
                 "SOURCE_MISSING")
            proof=json.loads(trace.read_bytes())
            score=audit.validate_case(proof,p)
            raw=model.read_bytes()
            need(audit.sha(raw)==proof["final_checkpoint_sha256"] and
                 len(raw)==proof["final_checkpoint_bytes"],
                 "CHECKPOINT_BYTES")
            both.append((proof,score,raw,trace.read_bytes()))
        linux,windows=both
        need(linux[0]["stable_sha256"]==windows[0]["stable_sha256"] and
             linux[1]==windows[1] and linux[2]==windows[2],
             "CROSS_PLATFORM_PARITY")
        stem=f"{name}-{seed}"
        compressed_bytes+=compressed(stem+"-proof.json.gz",linux[3])
        compressed_bytes+=compressed(stem+"-native.json.gz",linux[2])
        cases.append(linux[0])
        checkpoint_custody.append({
          "schedule":name,"seed":seed,"sha256":linux[0]["final_checkpoint_sha256"],
          "bytes":len(linux[2]),"public_trace_sha256":
          audit.sha(audit.canonical(linux[0]["trace"]))
        })
    report=audit.aggregate(cases)
    need(report["scientific_pass"] is False and
         report["accepted_native"] is False and
         report["deployment"]=="NONE","NONPROMOTION")
    persist("result.json",report)
    persist("provenance.json",{
       "schema":"yggdrasil.ckad26.causal-bayes.provenance.v1",
       "frozen_prereg_commit":PREREG,
       "parent_model_commit":PARENT,"exact_source_commit":sha,
       "generator_sha256":audit.SOURCE_SHA,
       "stable_result_sha256":report["stable_sha256"],
       "platforms":["ubuntu-latest","windows-2022"],
       "source_case_count":9,"checkpoint_custody":checkpoint_custody,
       "compressed_evidence_bytes":compressed_bytes,
       "exact_cross_os_semantic_and_checkpoint_parity":True,
       "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    })
    lines=[
      "# CKAD26 — Conditional causal evidence versus raw surprise",
      "",
      "**"+report["classification"]+"** — frozen, prospective synthetic development.",
      "Nine native 192-episode public-action streams start from exactly three",
      "previously qualified 448-episode Yggdrasil checkpoints, using new",
      "synthetic source namespaces. Every shadow detector received exactly",
      "the same public action-consequence evidence. Neither shadow hypothesis",
      "could alter the native learner, exploration actions or learned weights.",
      "",
      "Candidate tests a Beta(1,1) split-versus-shared conditional transition",
      "or reward distribution over the previous 32 observations (16+16).",
      "Exact rational Bayes factor threshold=16, persistence=2, spacing=8.",
      "The unconditional conventional detector has identical windows,",
      "threshold and persistence but ignores intervention state/action keys.",
      "Native joint surprise is the preserved CKAD23 comparator.",
      "Random alarm is a label-free hash-rate control, not a learner.",
      "",
      "| Schedule | Arm | Correct boundary 48 /3 | 96 /3 | 144 /3 | True detections | False alarms |",
      "|---|---|---:|---:|---:|---:|---:|",
    ]
    for name in audit.SCHEDULES:
        for arm in audit.ARMS:
            row=report["source_schedules"][name][arm]
            counts=row["by_true_boundary"]
            lines.append(f'| {name} | {arm} | {counts.get("48","—")} | '
                        f'{counts.get("96","—")} | {counts.get("144","—")} | '
                        f'{row["total_true"]} | {row["total_false"]} |')
    lines += [
       "",
       "## Frozen gates",
       "",
       *[f'- {key}: {"PASS" if val else "FAIL"}'
         for key,val in report["frozen_gates"].items()],
       "",
       "## Limitations",
       "",
       "This is causal-*conditional* evidence in a known synthetic world",
       "family, not independently verified causal discovery. All candidate",
       "change alarms are shadow-only; an alarm cannot establish improved",
       "learning, retained knowledge, transfer, planning or reward.",
       "",
       "The nine native source checkpoints and full timestamp-ordered action",
       "receipts were independently reproduced byte-for-byte on Linux and",
       "Windows, preserved with deterministic lossless gzip in this folder.",
       "Three independent pretrained parent groups; nine source draw namespaces",
       "are not nine independent pretrained models. No protected first use.",
       "",
       "Stable result SHA256: "+report["stable_sha256"],
       "",
       "**ENGINEERING:** subject to mandatory full exact-candidate cross-OS regression.",
       "**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**",
       ""
    ]
    (HERE/"SESSION_REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"classification":report["classification"],
         "gates":report["frozen_gates"],
         "true_by_arm":report["total_true_by_arm"],
         "stable":report["stable_sha256"]},sort_keys=True))

if __name__=="__main__":seal()
