"""Cross-platform seal of CKAD25's source-frozen diagnostic signal evidence."""
import gzip
from itertools import product
import json
import os
from pathlib import Path
import subprocess

import audit

HERE=Path(__file__).resolve().parent
FROZEN="33daba7912a2c0533cdad13968cdeb359cd4e24d"
PARENT=audit.BASE

def need(b,why):
    if not b:raise ValueError("CKAD25_SEAL_"+why)

def write(name,obj):
    (HERE/name).write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")

def save_lossless(name,raw):
    path=HERE/name
    path.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
    need(gzip.decompress(path.read_bytes())==raw,"EXACT_GZIP_ROUNDTRIP")
    return len(path.read_bytes())

def main():
    source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    subprocess.run(["git","merge-base","--is-ancestor",FROZEN,source],check=True)
    subprocess.run(["git","merge-base","--is-ancestor",PARENT,source],check=True)
    root=Path(os.environ["CKAD25_ARTIFACT_ROOT"])
    protocol=audit.protocols()
    cases=[]
    custody=[]
    total_bytes=0
    for scenario,seed in product(audit.SCHEDULES,audit.SEEDS):
        inputs=[]
        for os_name in ("ubuntu-latest","windows-2022"):
            folder=root/f"ckad25-{os_name}-{scenario}-{seed}-proof"
            result=folder/"case-result.json"
            checkpoint=folder/f"{scenario}-{seed}-native.json"
            need(result.is_file() and checkpoint.is_file(),"SOURCE_ARTIFACT")
            record=json.loads(result.read_bytes())
            diagnostic=audit.validate_case(record,protocol)
            raw=checkpoint.read_bytes()
            need(audit.sha(raw)==record["final_checkpoint_sha256"] and
                 len(raw)==record["final_checkpoint_bytes"],
                 "ACTUAL_MODEL_CHECKPOINT_SHA")
            inputs.append((record,raw,result.read_bytes(),diagnostic))
        x,y=inputs
        need(x[0]["stable_sha256"]==y[0]["stable_sha256"] and
             x[0]["trace"]==y[0]["trace"] and x[1]==y[1] and
             x[3]==y[3],"TWO_OS_SOURCE_BYTES_AND_REPLAY")
        stem=f"{scenario}-{seed}"
        total_bytes+=save_lossless(f"{stem}-proof.json.gz",x[2])
        total_bytes+=save_lossless(f"{stem}-native.json.gz",x[1])
        cases.append(x[0])
        custody.append({
            "schedule":scenario,"seed":seed,
            "checkpoint_sha256":audit.sha(x[1]),
            "checkpoint_bytes":len(x[1]),
            "source_trace_sha256":audit.sha(audit.canonical(x[0]["trace"])),
            "semantic_case_sha256":x[0]["stable_sha256"]
        })
    aggregate=audit.aggregate(cases)
    need(aggregate["scientific_pass"] is False and
         aggregate["accepted_native"] is False and
         aggregate["deployment"]=="NONE","PROMOTION_DENIED")
    write("result.json",aggregate)
    write("provenance.json",{
       "schema":"yggdrasil.ckad25.factorized-surprise.provenance.v1",
       "protocol_sha":FROZEN,"source_commit":source,
       "model_parent_sha":PARENT,
       "generator_sha256":audit.SOURCE,
       "aggregate_semantic_sha256":aggregate["stable_sha256"],
       "checkpoint_custody":custody,
       "linux_windows_semantic_reproduction":True,
       "linux_windows_checkpoint_byte_reproduction":True,
       "compressed_proof_and_checkpoint_bytes":total_bytes,
       "trained_native_model_mutation":False,
       "scientific_pass":False,"accepted_native":False,"deployment":"NONE"
    })
    lines=[
       "# CKAD25 — Factorized causal surprise on disjoint synthetic streams",
       "",
       "**"+aggregate["classification"]+"** — frozen development signal test,",
       "not proof of superior policy/learning/retention. The alternative alarms",
       "were shadow monitors, sharing the unchanged native learner's decisions",
       "and public intervention consequences. No split signal changed the model.",
       "",
       "Existing joint alarm uses prequential p(T,Y) with factor4; transition",
       "and reward alarms each use their observed marginal likelihood with",
       "factor2. All use threshold16 and 8 min local observations; factorized",
       "OR fires on either component, resetting both component scores.",
       "",
       "| Schedule | Alarm | Detection 48 /3 | 96 /3 | 144 /3 | Total true detections | False alarms |",
       "|---|---|---:|---:|---:|---:|---:|"
    ]
    for scenario in audit.SCHEDULES:
        for arm in audit.ARMS:
            row=aggregate["source_schedules"][scenario][arm]
            counts=row["seed_recall_per_boundary"]
            lines.append(f'| {scenario} | {arm} | {counts.get("48","—")} | '
                         f'{counts.get("96","—")} | {counts.get("144","—")} | '
                         f'{row["total_true_detections"]} | {row["total_false_alarms"]} |')
    lines.extend(["","## Frozen gates",""])
    for gate,passed in aggregate["frozen_gates"].items():
        lines.append(f'- {gate}: {"PASS" if passed else "FAIL"}')
    lines.extend([
       "",
       "Total true detections: existing joint "+
       str(aggregate["total_joint_true_detections"])+
       " vs factorized OR "+str(aggregate["total_factorized_true_detections"])+
       " (delta "+str(aggregate["factorized_minus_joint_true_detections"])+").",
       "",
       "Every negative result, held null schedule and original checkpoint",
       "witness prefix is preserved. Nine byte-exact Linux and Windows native",
       "checkpoint pairs and event proofs are stored as deterministic gzip",
       "blobs in this GitHub folder. Additional source namespaces are not",
       "independent retrained parent seed groups or novel real-world sources.",
       "",
       "This result measures alarm timing/specificity only, not reward gain,",
       "world-rule discovery, scientific generalization or learning improvement.",
       "",
       "Frozen aggregate SHA256: "+aggregate["stable_sha256"],
       "",
       "**ENGINEERING:** subject to mandatory final cross-platform full regression.",
       "**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**",
       ""
    ])
    (HERE/"SESSION_REPORT.md").write_text("\n".join(lines))
    print(json.dumps({
      "classification":aggregate["classification"],
      "gates":aggregate["frozen_gates"],
      "joint_true":aggregate["total_joint_true_detections"],
      "factorized_true":aggregate["total_factorized_true_detections"],
      "stable_sha256":aggregate["stable_sha256"]
    },sort_keys=True))

if __name__=="__main__":
    main()
