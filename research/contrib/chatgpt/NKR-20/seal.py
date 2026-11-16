"""Seal all three frozen study outcomes, including nulls, after reproduction."""
import json
import os
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from campaign import stable,sha,canon

linux=json.loads(os.environ["NKR20_LINUX_RESULT"])
windows=json.loads(os.environ["NKR20_WINDOWS_RESULT"])
if stable(linux)!=stable(windows):
    raise RuntimeError("NKR20_CAMPAIGN_REPLICATION_DRIFT")
source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
if linux["source_candidate_sha"]!=source or windows["source_candidate_sha"]!=source:
    raise RuntimeError("NKR20_SOURCE_CHANGED")
for name,data in (("campaign-result.json",linux),("replication-windows.json",windows)):
    (HERE/name).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
for report in linux["experiments"]:
    folder=HERE.parent/report["experiment"]
    folder.mkdir(exist_ok=True)
    (folder/"result.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
provenance={
 "schema":"yggdrasil.nkr20-22.campaign.provenance.v1","source_sha":source,
 "prereg_sha":os.environ["NKR20_PREREG_SHA"],
 "github_run_id":os.environ["GITHUB_RUN_ID"],
 "canonical_original_public_fixture_source":"5836c5dcdb74a8a1a7c5c32097d02ee955a4b2c3",
 "canonical_original_public_fixture_path":"research/contrib/chatgpt/CVH-04/consumed_public_fixture.json",
 "fixture_sha256":sha((HERE/"source_fixture.json").read_bytes()),
 "ordered_transition_sha256":linux["source_transition_sha256"],
 "stable_result_sha256":linux["stable_sha256"],
 "all_three_studies_executed_without_outcome_based_tuning":True,
 "linux_windows_stable_parity":True,"original_source_actions":0,
 "scientific_pass":False,"accepted_native":False,
 "final_qualification":"pending on generated final child; terminal PR receipt supplies result"}
(HERE/"provenance.json").write_text(json.dumps(provenance,indent=2,sort_keys=True)+"\n")
lines=["# Continuous knowledge campaign: NKR-20, NKR-21, NKR-22","",
"All three studies were frozen together and executed consecutively without",
"waiting for another operator gate. Earlier negative hypotheses did not stop",
"the later frozen tests. No model/feature/threshold selection followed scores.","",
"## Source and authority","",
"Source SHA: "+source,
"Stable campaign SHA256: "+linux["stable_sha256"],
"Original public observations:124; new external environment actions:0.",
"Four previously consumed external mechanical episodes only; not pristine",
"independent science. Original public transition hashes verified. Parent NKR19",
"knowledge/retention result and other research tracks remain unchanged.","",
"## NKR-20: does previous public reward help?","",
linux["experiments"][0]["classification"],"",
"| Frozen representation | Reward Brier | Next-state Brier | Pooled Brier |",
"|---|---:|---:|---:|"]
for arm,v in linux["experiments"][0]["scores"].items():
    lines.append("| "+arm+" | "+" | ".join(
        f'{v[k]["value"]:.9f}' for k in ("reward","after","pooled"))+" |")
lines+=["","Lower is better. Native Bayesian probabilities match an independent",
"same-information batch fit exactly. MLE controls are fitted in closed form.",
"All representations receive the same23 training rows/world and328-byte",
"two-bank native capacity. Current inputs include before/action; history uses",
"only previous public reward, including earlier already-observed test rows.",
"Test observations never update model weights/counters.","",
"## NKR-21: fixed hierarchical pooling","",
linux["experiments"][1]["classification"],"",
"| Frozen representation | Reward Brier | Next-state Brier | Pooled Brier |",
"|---|---:|---:|---:|"]
for arm,v in linux["experiments"][1]["scores"].items():
    lines.append("| "+arm+" | "+" | ".join(
        f'{v[k]["value"]:.9f}' for k in ("reward","after","pooled"))+" |")
lines+=["","Parent estimate is pooled from the same child-bank counters; no extra",
"parent bank/capacity. Fixed strength4 was chosen before all campaign outcomes.",
"Independent conventional hierarchical estimation ties every prediction.","",
"## NKR-22: different action rules remain unidentified","",
linux["experiments"][2]["classification"],"",
"These are bounds on one-step binary reward switching at the recorded",
"public histories. They are NOT bounds on total return after a different",
"policy would change later states/histories. That question also remains open.","",
"| Decision rule | Later rows | Unobserved chosen consequences | Lower bound | Upper bound |",
"|---|---:|---:|---:|---:|"]
for arm,v in linux["experiments"][2]["later_held_rows"].items():
    lines.append(f'| {arm} | {v["rows"]} | {v["unknown_rewards"]} | {v["lower_bound"]["value"]:.9f} | {v["upper_bound"]["value"]:.9f} |')
lines+=["","Full124-row support/bounds and the later28-row support audit are preserved",
"in NKR-22/result.json. Original deterministic behavior has observed-action",
"propensity1 and alternative-action propensity0 conditional on the complete",
"public decision history. Predictions do not manufacture unobserved rewards.","",
"## Retention, qualification and limits","",
"Old native probability readouts survived separate-address additions and",
"cold restoration with exact equality. This does not test overlapping",
"shared-weight interference or successful same-address changed-rule learning.",
"Strongest equivalent control superiority is ZERO; scientific_pass=false.",
"Native architecture, accepted main and owner runtime were not modified.","",
f'Ubuntu campaign audit:{linux["wall_seconds"]:.6f}s; Windows:{windows["wall_seconds"]:.6f}s.',
"Original datasets were not scanned and original environments were not rerun.",
"Only the small source-hash-checked public fixture is replayed for this frozen",
"retrospective campaign; Windows independently reproduces stable results.",
"Final entire root regression, NKR05 and independent G29 on both platforms",
"are pending when this receipt is committed; terminal status is in draft PR.","",
"Next genuinely decisive action-value science requires owner-approved new",
"interventions on an unconsumed source cohort with trained conventional",
"policy controls and independent qualification. No scheduled/background",
"controller, accepted-model deployment or paid API was added."]
(HERE/"SESSION_REPORT.md").write_text("\n".join(lines)+"\n")
