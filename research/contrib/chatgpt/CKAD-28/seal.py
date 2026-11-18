"""Seal CKAD28 authentic cross-platform actions, scores and native memories.

The identical frozen source actions are independently executed on Linux and
Windows; seal only if original witness prefixes, matched source outcomes,
rational held metrics, and saved native checkpoint bytes match across OS.
Negative research results are retained without threshold changes.
"""
from itertools import product
from pathlib import Path
import gzip
import json
import os
import subprocess

import audit

HERE=Path(__file__).resolve().parent
FROZEN="6f6a50fbf53cbc1e6dd317d896c25caa081b24d6"
PARENT="43a468dea22b19498329e386aa0af0abecc3100b"


def need(ok,why):
    if not ok:raise ValueError("CKAD28_SEAL_"+why)


def save(name,raw):
    compressed=gzip.compress(raw,compresslevel=9,mtime=0)
    (HERE/name).write_bytes(compressed)
    need(gzip.decompress((HERE/name).read_bytes())==raw,"LOSSLESS_GZIP")
    return len(compressed)


def write(name,obj):
    (HERE/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")


def seal():
    source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    for ancestor in (FROZEN,PARENT):
        subprocess.run(["git","merge-base","--is-ancestor",ancestor,source],
                       check=True)
    p=audit.campaign.source_protocol()
    root=Path(os.environ["CKAD28_ARTIFACT_ROOT"])
    collected=[]
    source_bytes=0
    custody=[]
    for scenario,seed in product(audit.SCENARIOS,audit.SEEDS):
        pair=[]
        for osname in ("ubuntu-latest","windows-2022"):
            folder=root/f"ckad28-{osname}-{scenario}-{seed}-proof"
            receipt_file=folder/"case-result.json"
            need(receipt_file.is_file(),"MISSING_SOURCE_RECEIPT")
            d=json.loads(receipt_file.read_bytes())
            audit.verify_case(d,p)
            native={}
            for arm in audit.ARMS:
                path=folder/f"{scenario}-{seed}-{arm}-native.json"
                need(path.is_file(),"MISSING_NATIVE_CHECKPOINT")
                raw=path.read_bytes()
                pin=d["custody"][arm]
                need(audit.digest(raw)==pin["checkpoint_sha256"]
                     and len(raw)==pin["checkpoint_bytes"],
                     "SOURCE_CHECKPOINT_CUSTODY")
                native[arm]=raw
            pair.append((d,native,receipt_file.read_bytes()))
        linux,win=pair
        need(linux[0]["stable_sha256"]==win[0]["stable_sha256"]
             and audit.campaign.stable(linux[0])==
                 audit.campaign.stable(win[0])
             and linux[1]==win[1],
             "CROSS_OS_EXACT_SOURCE_AND_MODEL")
        collected.append(linux[0])
        prefix=f"{scenario}-{seed}"
        source_bytes+=save(prefix+"-source-proof.json.gz",linux[2])
        for arm,raw in linux[1].items():
            source_bytes+=save(f"{prefix}-{arm}-native.json.gz",raw)
            custody.append({
               "scenario":scenario,"seed":seed,"arm":arm,
               "checkpoint_sha256":audit.digest(raw),
               "checkpoint_bytes":len(raw)
            })
    report=audit.metrics(collected)
    need(report["scientific_pass"] is False and
         report["accepted_native"] is False and
         report["deployment"]=="NONE",
         "NO_SCIENCE_PROMOTION")
    write("result.json",report)
    write("provenance.json",{
       "schema":"yggdrasil.ckad28.decision-relevance.provenance.v1",
       "frozen_prereg_commit":FROZEN,
       "qualified_ckad27_parent_commit":PARENT,
       "exact_candidate_source":source,
       "original_generator_sha256":p["original_source_sha256"],
       "result_stable_sha256":report["stable_sha256"],
       "independent_parent_seeds":list(audit.SEEDS),
       "cold_model_checkpoints":custody,
       "source_proofs":len(collected),
       "exact_cross_os_model_and_result_parity":True,
       "total_lossless_gzip_bytes":source_bytes,
       "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    })
    lines=[
       "# CKAD28 — Reward-hypothesis-decision causal interventions",
       "",
       "**"+report["classification"]+"** — frozen synthetic development experiment.",
       "",
       "All arms started from the exact CKAD22 448-public-witness native",
       "checkpoint, used the unchanged original Yggdrasil native model and",
       "unsignaled stream detector, and observed 128 new sequential",
       "action-consequence episodes per arm. The 'decision' policy selects",
       "decision-relevant value of information across the retained context",
       "models. Existing native exploration and deterministic random policies",
       "received identical underlying exogenous draw keys and action budgets.",
       "",
       "An independent fully fitted trailing-64 conventional MLE predictor",
       "was fitted on each arm's same receipts and scored on identical held",
       "episodes. Held world outcomes were never used to update any model.",
       "",
       "## Frozen outcomes",
       "",
       "| Metric | Exact fraction |",
       "|---|---:|",
    ]
    for key,value in report["metrics"].items():
        if key=="per_seed_gain_vs_native":
            continue
        value_text=(f"{value[0]}/{value[1]}" if type(value) is list else str(value))
        lines.append(f"| {key} | {value_text} |")
    lines.extend(["","## Frozen gates",""])
    for gate,pas in report["frozen_gates"].items():
        lines.append(f'- {gate}: {"PASS" if pas else "FAIL"}')
    lines.extend([
       "",
       "Per-seed native reward gains: "+
       str(report["metrics"]["per_seed_gain_vs_native"]),
       "",
       "## Evidence and limitations",
       "",
       "Every one of six source cases was independently repeated on Ubuntu and",
       "Windows. Eighteen full model checkpoints were compared byte-for-byte,",
       "then retained on this GitHub branch alongside all complete 128-event",
       "source receipts. Actual source outcomes are recomputed independently",
       "from recorded actions; all original 448 witnesses are preserved.",
       "",
       "The test uses two schedules of one known synthetic generator with",
       "three pretrained parent groups. The decision policy directly inspects",
       "the existing native candidate posterior; this is a read-only",
       "policy candidate, not proof of novel-world causal intelligence.",
       "Metric advantages do not imply scientific PASS, generalization,",
       "weight learning, retention outside this source, or deployment.",
       "",
       "Stable result SHA-256: "+report["stable_sha256"],
       "",
       "**ENGINEERING**: subject to mandatory full exact-candidate two-OS",
       "regression and independent G29 evidence verification.",
       "**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**",
       ""
    ])
    (HERE/"SESSION_REPORT.md").write_text("\n".join(lines))
    print(json.dumps({
        "classification":report["classification"],
        "gates":report["frozen_gates"],
        "metrics":report["metrics"],
        "stable":report["stable_sha256"]
    },sort_keys=True))


if __name__=="__main__":
    seal()
