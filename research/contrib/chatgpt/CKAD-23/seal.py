"""Persist the exact CKAD23 cross-OS synthetic stream evidence and negatives."""
import json
import os
from pathlib import Path
import shutil
import subprocess

import audit

HERE=Path(__file__).resolve().parent
SOURCE_PREREG="5da91380fdbb7aeb955735ad39225ce8ac5e89c2"
PARENT="f04cfcac2aa07806a6b942d968119de87bfb6aaf"

def need(ok,code):
    if not ok:raise ValueError("CKAD23_SEAL_"+code)

def write(name,data):
    (HERE/name).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")

def main():
    root=Path(os.environ["CKAD23_ARTIFACT_ROOT"])
    source_sha=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    need(subprocess.run(["git","merge-base","--is-ancestor",SOURCE_PREREG,source_sha],
                        check=False).returncode==0,"FROZEN_PROTOCOL")
    need(subprocess.run(["git","merge-base","--is-ancestor",PARENT,source_sha],
                        check=False).returncode==0,"FROZEN_PARENT")
    with (HERE/"prereg.json").open() as f: prereg=json.load(f)
    need(prereg["schema"]=="yggdrasil.ckad23.unsignaled-context-development.prereg.v1" and
         prereg["parent"]==PARENT,"UNMODIFIED_PROTOCOL")
    linux=audit.load_os(root,"ubuntu-latest")
    windows=audit.load_os(root,"windows-2022")
    for a,b in zip(linux,windows):
        need(audit.stable(a)==a["stable_sha256"]==
             audit.stable(b)==b["stable_sha256"],"OS_SEMANTIC_SOURCE")
        seed=a["seeds"][0]["seed"]
        need(seed==b["seeds"][0]["seed"] and
             a["seeds"][0]["final_checkpoint_sha256"]==
             b["seeds"][0]["final_checkpoint_sha256"],
             "CHECKPOINT_CROSS_OS")
        name=f"seed-{seed}-stream-native.json"
        p=root/f"ckad23-ubuntu-latest-{seed}-proof"/name
        q=root/f"ckad23-windows-2022-{seed}-proof"/name
        need(p.is_file() and q.is_file() and p.read_bytes()==q.read_bytes(),
             "EXACT_CHECKPOINT_REPLICATION")
        raw=p.read_bytes()
        need(audit.digest(raw)==a["seeds"][0]["final_checkpoint_sha256"],
             "CHECKPOINT_SOURCE_PIN")
        (HERE/name).write_bytes(raw)
        write(f"seed-{seed}-source-proof.json",a)
        write(f"seed-{seed}-windows-proof.json",b)
    result,replicated=audit.aggregate(linux),audit.aggregate(windows)
    need(result==replicated and result["scientific_pass"] is False,
         "SEALED_OS_AGGREGATE")
    write("result.json",result)
    write("replication-windows.json",replicated)
    write("provenance.json",{
        "schema":"yggdrasil.ckad23.unsignaled-context.provenance.v1",
        "source_sha":source_sha,"frozen_prereg_at":SOURCE_PREREG,
        "parent_sha":PARENT,
        "original_source_sha256":audit.SOURCE_SHA,
        "result_stable_sha256":result["stable_sha256"],
        "linux_windows_exact_checkpoint_parity":True,
        "linux_windows_exact_semantic_parity":True,
        "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    })
    scores=result["held_score_by_checkpoint"]
    counts=(64,112,160,192)
    lines=[
      "# CKAD23 — Unsignaled causal context detection in one cumulative learner",
      "",
      "**"+result["classification"]+"** — frozen synthetic development only.",
      "No native model promotion, no automatic Forge/Yggdrasil loop admission.",
      "",
      "This experiment began with the exact three qualified CKAD22 native",
      "checkpoints at 448 retained public episodes each. The source changed its",
      "causal rule at episode counts 48,96,144; the learner was not told when.",
      "Every chosen first intervention preceded the observed next state; every",
      "second intervention preceded the revealed terminal consequence.",
      "",
      "The detector used S=max(1,S/(4*p)) from exact prequential joint evidence",
      "and triggered a new context at S>=16 after >=8 retained local episodes.",
      "All source receipts remain append-only in one cumulative native model;",
      "only contextual readout/hypothesis selection was reset.",
      "",
      "An independent conventional replay of the same mixture, actions and",
      "context change detector matched native readouts and boundary receipts.",
      "A fully trained trailing64 MLE used the exact same public action receipts.",
      "Random acquisition was equal-budget but chose its own interventions.",
      "",
      "| Held count | Detector /288 | No-reset /288 | Periodic32 /288 | Trailing64 MLE /288 |",
      "|---:|---:|---:|---:|---:|",
    ]
    for count in counts:
        v=scores[str(count)]
        lines.append(f'| {count} | {v["detector_active"]} | {v["no_reset"]} | '
                     f'{v["periodic32"]} | {v["trailing_mle"]} |')
    lines.extend([
      "",
      "## Frozen development gates",
      "",
      *[f'- {name}: {"PASS" if ok else "FAIL"}'
        for name,ok in result["development_gates"].items()],
      "",
      "## Unsignaled detections by seed",
      "",
    ])
    for seed,details in result["seeds"].items():
        indices=[v["count"]-448 for v in details["detected_boundaries"]]
        lines.append(f'- Seed {seed}: stream-relative inferred counts {indices}; '
                     f'false alarms {details["false_alarms"]}; '
                     f'final checkpoint {details["final_checkpoint_sha256"]}.')
    lines.extend([
      "",
      "Limitations: synthetic source family; three model seed groups; change points",
      "and frozen success gates were predefined; matching conventional policy is a",
      "necessary parity test, not proof of superiority over it. No protected",
      "scientific first-use was consumed. Every failed threshold is preserved.",
      "",
      "Final result stable SHA256: "+result["stable_sha256"],
      "",
      "**ENGINEERING:** subject to mandatory full final regression on atlas-sealed SHA.",
      "**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**",
      "",
    ])
    (HERE/"SESSION_REPORT.md").write_text("\n".join(lines))
    print(json.dumps({
      "sealed":True,"classification":result["classification"],
      "development_gates":result["development_gates"],
      "development_metrics":result["development_metrics"],
      "stable_sha256":result["stable_sha256"],
    },sort_keys=True))

if __name__=="__main__":main()
