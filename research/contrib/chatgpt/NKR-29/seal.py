"""Seal actual consumed-feedback repair outcomes after independent OS parity."""
import json
import os
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from audit import stable
linux=json.loads(os.environ["NKR29_LINUX_RESULT"])
windows=json.loads(os.environ["NKR29_WINDOWS_RESULT"])
source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
if stable(linux)!=stable(windows) or any(d["source_candidate_sha"]!=source for d in (linux,windows)):
    raise RuntimeError("NKR29_PARITY_OR_SOURCE_DRIFT")
for name,value in (("result.json",linux),("replication-windows.json",windows)):
    (HERE/name).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
p={"schema":"yggdrasil.nkr29.consumed-feedback-repair.provenance.v1",
   "source_sha":source,"prereg_sha":os.environ["NKR29_PREREG_SHA"],
   "run_id":os.environ["GITHUB_RUN_ID"],"source_artifact":14257634107,
   "source_zip_sha256":linux["source_zip_sha256"],
   "stable_sha256":linux["stable_sha256"],"new_original_source_actions":0,
   "native_runtime_changed":False,"scientific_pass":False,"accepted_native":False,
   "qualification":"full final root/NKR05/G29 both OS pending at evidence commit; terminal PR receipt authoritative"}
(HERE/"provenance.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n")
lines=["# NKR29: bounded feedback repair of actual recorded native forecasts","",
"Result:"+linux["classification"],"",
"The initial native bank learned96 actual public events from four previously",
"consumed external CausalGym worlds. Its164-byte checkpoint is preserved.",
"The remaining28 recorded events were forecast BEFORE being used as feedback.",
"All original labels were historically consumed; this is a retrospective",
"development experiment, not pristine heldout confirmation or new first-use.","",
"## Wide first, then work backward","",
"| Maximum new events | Feedback method | Actually learned events | Pooled Brier (lower better) | Confident misses |",
"|---:|---|---:|---:|---:|"]
for cap in linux["descending_caps"]:
    for name,a in linux["scales"][str(cap)]["arms"].items():
        lines.append(f'| {cap} | {name} | {a["updates_events"]} | {a["scores"]["pooled"]["value"]:.9f} | {a["confident_misses"]} |')
lines+=["","Each matched-random arm updates at EXACTLY the same times/in the same",
"world and uses the same actual number of events as error-only repair.",
"It selects from previously witnessed, as-yet-unassimilated feedback, never",
"future events. Random controls are conditional on error-only's gate, not",
"independent deployed policies. Ordinary all-feedback learning shares the same",
"maximum budget/public stream but may consume more observations; actual costs",
"are disclosed above. A stochastic surprise is not proof of an incorrect law.","",
"Every native forecast matches the independently fitted exact Beta control.",
"The native learned bank retains all192 original observed-counter increments",
"(96 physical events), and newly learned events add2 increments each. Counts",
"agree with independent per-arm event ledgers; other worlds' posterior values",
"remain unchanged after every update. Every final bank cold-restores exactly.",
"Checkpoint hex, hashes and actually learned event IDs are in result.json.","",
"## Interpretation","",
"Error-only support requires at the largest28-event cap BOTH a0.005 Brier",
"gain over frozen memory AND0.005 over matched-random mean. No thresholds or",
"caps are retuned after outcomes. Original NKR19 frozen score is reproduced",
"exactly. Old failures and the original native checkpoint stay frozen; these",
"separate exploratory repaired checkpoints do not rewrite previous evidence.","",
"Learning here means changed native public consequence counts. This does not",
"train the21.3M factual image into understanding, learn a new operator, prove",
"unfamiliar-world transfer, beat an exact equally informed control or authorize",
"accepted-model installation. All source events were previously consumed.","",
"Source SHA:"+source,
"Prereg SHA:"+os.environ["NKR29_PREREG_SHA"],
"Stable SHA256:"+linux["stable_sha256"],
f'Ubuntu audit:{linux["wall_seconds"]:.6f}s. Windows audit:{windows["wall_seconds"]:.6f}s.',
"No source environments imported/reset/intervened; no original source scan,",
"protected seed, runner/controller/scheduler, paid API or deployment.",
"Full final exact-source root/NKR05/independent G29 both OS are qualified after",
"these receipts are committed; final PR records those terminal receipts."]
(HERE/"SESSION_REPORT.md").write_text("\n".join(lines)+"\n")
