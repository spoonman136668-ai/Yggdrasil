"""Persist only compact derived receipts after both cached-audit platforms pass."""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from audit import stable,sha,canon

linux=json.loads(os.environ["NKR19_LINUX_RESULT"])
windows=json.loads(os.environ["NKR19_WINDOWS_RESULT"])
if stable(linux)!=stable(windows):
    raise RuntimeError("NKR19_DO_NOT_SEAL_INCONSISTENT_REPLICATION")
source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
if linux["source_candidate_sha"]!=source or windows["source_candidate_sha"]!=source:
    raise RuntimeError("NKR19_PRIMARY_SOURCE_CHANGED")
(HERE/"result.json").write_text(json.dumps(linux,indent=2,sort_keys=True)+"\n")
(HERE/"replication-windows.json").write_text(json.dumps(windows,indent=2,sort_keys=True)+"\n")
prov={"schema":"yggdrasil.nkr19.cached-source.provenance.v1",
      "source_sha":source,"parent_pr":1157,
      "prereg_sha":os.environ["NKR19_PREREG_SHA"],
      "github_run_id":os.environ["GITHUB_RUN_ID"],
      "original_receipt_run":43930489602,"original_receipt_artifact":14257634107,
      "source_archive_sha256":linux["source_zip_sha256"],
      "original_source_actions":0,"cached_original_source_actions":124,
      "result_stable_sha256":linux["stable_result_sha256"],
      "cross_platform_all_stable_metrics_equal":True,
      "scientific_pass":False,"accepted_native":False,
      "final_regression":"pending on generated child; terminal PR receipt authoritative",
      "source_files":{str(p.relative_to(HERE.parents[3])):sha(p.read_bytes())
                      for p in (HERE/"audit.py",HERE/"seal.py",HERE/"prereg.json",
                                HERE.parents[3]/"yggdrasil/public_causal_cells.py")}}
(HERE/"provenance.json").write_text(json.dumps(prov,indent=2,sort_keys=True)+"\n")
lines=["# NKR-19 — cached genuine external knowledge audit","",
"Retrospective development only. No new external actions, protected source use,",
"learned policy-value claim, merge or accepted native model change.","",
"## Frozen source and primary result","",
"Primary source SHA: "+source,
"Stable result SHA256: "+linux["stable_result_sha256"],
"Classification: **"+linux["classification"]+"**; scientific_pass=false.","",
"Four consumed FKP26 mechanical episodes supply 124 original public actions.",
"Their raw transcripts remain in original Actions artifact 14257634107;",
"this report publishes derived measures only. No source environment was imported.","",
"## Does more distinct observed knowledge help?","",
"All scales use 96 presentations total. Replayed original event IDs are ignored;",
"each genuinely independent physical observation counts once.",
"Test: same last seven events per world, 56 public output predictions total.","",
"| Unique events/world | Native Brier | Exact Beta | MLE | Last-key | Persistence | Chance |",
"|---|---:|---:|---:|---:|---:|---:|"]
for k,row in linux["scales"].items():
    lines.append("| "+k+" | "+" | ".join(
        f'{row["scores"][a]["pooled"]["value"]:.9f}' for a in
        ("native_beta","exact_beta","empirical_mle","last_key","persistence","chance"))+" |")
lines+=["","Lower Brier is better. Both public targets (reward/next-state) are",
"reported separately as exact fractions in result.json. Same-capacity exact",
"Bayesian fitting matches every native probability, so strongest-equivalent",
"control gain is zero. MLE is a fully fitted conventional discrete model;",
"no neural baseline or matched compute advantage is claimed.","",
"## What the deterministic model cannot represent","",
json.dumps(linux["deterministic_audit"],sort_keys=True),"",
"Mixed outcomes for identical supplied inputs can reflect stochasticity, hidden",
"confounding or nonstationarity; these explanations are not distinguished.",
"Rejecting a legitimate public measurement does not make that measurement false.","",
"## Retention and understanding limits","",
"All old probability readouts remained identical after later, separate-address",
"learning and cold restoration. The original 164-byte native format is unchanged.",
"This is counter-based statistical knowledge, not unrestricted relation discovery,",
"shared-weight interference resistance, changed-rule adaptation or general intelligence.",
"The prequential screen supplies 184 predict-before-update output scores.","",
"## Qualification and runtime","",
"Ubuntu and Windows stable metrics, trace/source hashes and checkpoints match.",
f'Primary audit wall: {linux["wall_seconds"]:.6f}s; Windows: {windows["wall_seconds"]:.6f}s.',
"Download/setup time is additional and recorded by the workflow steps.",
"Full final regression and independent G29 are pending when these receipts",
"are committed; terminal qualification is recorded in the draft PR.","",
"Remaining scientific boundary: fresh owner-authorized unfamiliar-world",
"cohort, matched trained neural/policy controls, independent qualification,",
"prospective interventions and realistic whole-process costs."]
(HERE/"SESSION_REPORT.md").write_text("\n".join(lines)+"\n")
