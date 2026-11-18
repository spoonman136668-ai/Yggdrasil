"""Seal cross-platform CKAD24 exact proof and state bytes, fail closed on drift.

Preserve full per-case proofs and native checkpoints compressed losslessly in
GitHub. Scientific PASS and acceptance stay false irrespective of outcomes.
"""
import gzip
from itertools import product
import json
import os
from pathlib import Path
import subprocess

import audit

HERE=Path(__file__).resolve().parent
PREREG_COMMIT="1e531929ce8fc5104d829843e61e8857fbcc1989"
PARENT_COMMIT=audit.PARENT_SHA

def need(cond,reason):
    if not cond:raise ValueError("CKAD24_SEAL_"+reason)

def source_git(*args):
    return subprocess.check_output(["git",*args],text=True).strip()

def persist_json(name,data):
    (HERE/name).write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")

def compression(path,data):
    compressed=gzip.compress(data,compresslevel=9,mtime=0)
    (HERE/path).write_bytes(compressed)
    need(gzip.decompress((HERE/path).read_bytes())==data,"GZIP_LOSSLESS")
    return len(compressed)

def run():
    root=Path(os.environ["CKAD24_ARTIFACT_ROOT"])
    source=source_git("rev-parse","HEAD")
    source_git("merge-base","--is-ancestor",PREREG_COMMIT,source)
    source_git("merge-base","--is-ancestor",PARENT_COMMIT,source)
    prereg,original=audit.source_protocol()
    records={}
    compressed_size=0
    for schedule,seed in product(audit.SCHEDULES,audit.SEEDS):
        expected=f"seed-{seed}-stream-native.json"
        pair=[]
        for os_name in ("ubuntu-latest","windows-2022"):
            folder=root/f"ckad24-{os_name}-{schedule}-{seed}-proof"
            result_path=folder/"case-result.json"
            raw_path=folder/expected
            need(result_path.is_file() and raw_path.is_file(),"MISSING_SOURCE_OUTPUT")
            row=json.loads(result_path.read_bytes())
            raw=raw_path.read_bytes()
            diag=audit.validate_case(row,prereg,original)
            need(audit.sha(raw)==row["seed_result"]["final_checkpoint_sha256"] and
                 len(raw)==row["seed_result"]["final_checkpoint_bytes"],
                 "RAW_CHECKPOINT_PIN")
            pair.append((row,raw,result_path.read_bytes()))
        a,b=pair
        need(a[0]["stable_sha256"]==b[0]["stable_sha256"] and
             a[1]==b[1] and
             a[0]["seed_result"]["final_context_sha256"]==
             b[0]["seed_result"]["final_context_sha256"],
             "TWO_OS_SEMANTIC_AND_BYTE_REPLICATION")
        name=f"{schedule}-{seed}"
        compressed_size+=compression(f"{name}-source-proof.json.gz",a[2])
        compressed_size+=compression(f"{name}-native.json.gz",a[1])
        records[schedule,seed]=a[0]
    ordered=[records[s,seed] for s,seed in product(audit.SCHEDULES,audit.SEEDS)]
    sealed=audit.aggregate(ordered)
    need(sealed["scientific_pass"] is False and
         sealed["accepted_native"] is False and sealed["deployment"]=="NONE",
         "NONPROMOTION")
    persist_json("result.json",sealed)
    persist_json("provenance.json",{
        "schema":"yggdrasil.ckad24.permutations.provenance.v1",
        "protocol_at":PREREG_COMMIT,
        "qualified_parent_at":PARENT_COMMIT,
        "exact_case_source_commit":source,
        "exact_source_generator_sha256":audit.SOURCE_SHA,
        "exact_unchanged_ckad23_campaign_blob":audit.PARENT_BLOB,
        "result_semantic_sha256":sealed["stable_sha256"],
        "preserved_case_proofs":len(ordered),
        "preserved_native_checkpoints":len(ordered),
        "lossless_compressed_bytes":compressed_size,
        "two_os_parity":True,
        "protected_first_use":0,"scientific_pass":False,
        "accepted_native":False,"deployment":"NONE",
    })
    lines=[
       "# CKAD24 — Blind phase-permutation causal change detection",
       "",
       "**"+sealed["classification"]+"** — frozen synthetic development gate.",
       "The learner did not receive source phase names or true change times.",
       "It reused the exact CKAD23 native algorithm and three independently",
       "saved 448-public-episode checkpoints, with two new source permutation",
       "schedules and disjoint exogenous draw namespaces.",
       "",
       "True evaluator-side boundaries: 48, 96, 144. A detection counts only",
       "once per true boundary and only within 16 observed public consequences.",
       "All duplicate alarms count as false positives. This is stricter than",
       "the CKAD23 reward-only development gate.",
       "",
       "| Schedule | Change 48 (seeds/3) | Change 96 | Change 144 | False alarm counts | Development |",
       "|---|---:|---:|---:|---|---|",
    ]
    for name in audit.SCHEDULES:
        row=sealed["schedules"][name]
        recalls=row["true_positive_seeds_by_boundary"]
        alarms=[row["per_seed"][str(seed)]["false_alarms"] for seed in audit.SEEDS]
        lines.append(f'| {name} | {recalls["48"]} | {recalls["96"]} | '
                     f'{recalls["144"]} | {alarms} | {row["classification"]} |')
    lines.extend(["","## Frozen per-schedule metrics and gates",""])
    for name in audit.SCHEDULES:
        entry=sealed["schedules"][name]
        lines.append(f"### {name}")
        for gate,passed in entry["gates"].items():
            lines.append(f'- {gate}: {"PASS" if passed else "FAIL"}')
        for metric,value in entry["metrics"].items():
            lines.append(f'- {metric}: {value[0]}/{value[1]}')
        for seed,detail in entry["per_seed"].items():
            lines.append(f'- Seed {seed}: detections {detail["stream_relative_counts"]}, '
                         f'false alarms {detail["false_alarms"]}; '
                         f'checkpoint {detail["checkpoint_sha256"]}')
    lines.extend([
       "",
       "## Evidence custody and limits",
       "",
       "Six exact native checkpoints and the complete six per-case source",
       "proofs are stored in this folder with deterministic gzip compression;",
       "all were re-executed on Linux and Windows with byte-exact checkpoint",
       "and semantic evidence parity. Every case retains the complete original",
       "448-episode prefix and 192 new public action-consequence witnesses.",
       "",
       "New source namespaces do not imply independently pretrained additional",
       "models: only three original CKAD22 seed groups were independently fitted.",
       "This study uses known synthetic families, and cannot establish scientific",
       "novel-world transfer or autonomous intelligence.",
       "",
       f'Result semantic SHA256: {sealed["stable_sha256"]}',
       "",
       "**ENGINEERING:** pending final exact-candidate Linux/Windows regression and atlas.",
       "**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**",
       "",
    ])
    (HERE/"SESSION_REPORT.md").write_text("\n".join(lines))
    print(json.dumps({
        "classification":sealed["classification"],
        "source_commit":source,
        "frozen_gates":sealed["frozen_gates"],
        "stable_sha256":sealed["stable_sha256"]
    },sort_keys=True))

if __name__=="__main__":run()
