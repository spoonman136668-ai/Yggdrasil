"""Preserve the source-conditioned diagnostic without rewriting prior nulls."""
import json
import os
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from decision_audit import stable,sha

linux=json.loads(os.environ["NKR23_LINUX_RESULT"])
windows=json.loads(os.environ["NKR23_WINDOWS_RESULT"])
if stable(linux)!=stable(windows):
    raise RuntimeError("NKR23_SOURCE_DIAGNOSTIC_REPLICATION_DRIFT")
source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
if linux["source_candidate_sha"]!=source or windows["source_candidate_sha"]!=source:
    raise RuntimeError("NKR23_PRIMARY_SOURCE_CHANGED")
(HERE/"campaign-result.json").write_text(json.dumps(linux,indent=2,sort_keys=True)+"\n")
(HERE/"replication-windows.json").write_text(json.dumps(windows,indent=2,sort_keys=True)+"\n")
for report in linux["experiments"]:
    folder=HERE.parent/report["experiment"];folder.mkdir(exist_ok=True)
    (folder/"result.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
prov={"schema":"yggdrasil.nkr23-24.provenance.v1","prereg_sha":os.environ["NKR23_PREREG_SHA"],
      "source_sha":source,"github_run_id":os.environ["GITHUB_RUN_ID"],
      "upstream_sha":"c94e9a4cd3641588b6b8507e71ccee5c27032bdf",
      "original_source_blob":"6264ec5450754c009e98c3e85f6d5927ece0a9ab",
      "oracle_is_evaluator_only":True,"native_checkpoint_identity_required":"sealed NKR19",
      "stable_result_sha256":linux["stable_sha256"],
      "new_original_source_actions":0,"scientific_pass":False,"accepted_native":False,
      "qualification":"pending final derived child; terminal PR receipt supplies result"}
(HERE/"provenance.json").write_text(json.dumps(prov,indent=2,sort_keys=True)+"\n")
mechanism,decisions=linux["experiments"]
lines=["# NKR-23 and NKR-24 — source-conditioned decision diagnostics","",
"These two studies continued after NKR20/21 negative learning results and",
"NKR22's missing-action-support result. They do not rerun those primaries.",
"Source equations were publicly inspected before this preregistration;",
"this is explicitly exploratory/source-conditioned, not blind source science.","",
"## Why extra history failed in this fixed source model","",
"The original public MDPSCM reward/transition source was verified at exact",
"Git blob6264ec5450754c009e98c3e85f6d5927ece0a9ab. A restricted Boolean AST",
"interpreter and independent direct equations agree on all32 state/action/",
"latent assignments. No original code, RNG, environment constructor, reset",
"or do action was executed.","",
"| Public state | Action | Nominal reward-one probability | Next-state-one probability |",
"|---:|---:|---:|---:|"]
for row in mechanism["kernel"]:
    lines.append(f'| {row["state"]} | {row["action"]} | {row["reward_probability"]["value"]:.2f} | {row["next_state_one_probability"]["value"]:.2f} |')
lines+=["","Under the source's nominal iid latent model, current state/action are",
"sufficient for these conditional probabilities. Prior public reward adds",
"no population conditional information. That explains why increasing the",
"history bins can add sparse-sample error rather than better understanding.",
"This is evaluator-derived knowledge of the published source, not a relation",
"newly discovered by the native model.","",
"## Do already-learned native counts imply useful decisions?","",
"Every reconstructed native checkpoint MUST equal its previously sealed NKR19",
"checkpoint. Thus source-derived oracle equations cannot change native training.",
"An independent same-information Beta fit makes identical action choices.",
"Seven-step reward expectations below are calculated from the source model,",
"not measured by executing new policies. Common initial state is uniform.","",
"| Public observations/world | Native optimal choices /8 | Native expected reward/step | Mechanical policy | Source oracle ceiling |",
"|---|---:|---:|---:|---:|"]
for row in decisions["scales"]:
    p=row["common_uniform_start_expected_reward_per_step"]
    lines.append(f'| {row["observations_per_world"]} | {row["source_oracle_optimal_choices"]} | {p["native"]["value"]:.9f} | {p["mechanical"]["value"]:.9f} | {p["source_oracle"]["value"]:.9f} |')
lines+=["",decisions["classification"],"",
"All always0/always1 values, actual historical prefix-start-state expectations,",
"full action maps and exact fractions are preserved in NKR24/result.json.",
"The source oracle is an unfair knowledge upper bound, not an equally informed",
"learner. Strongest equally informed conventional gain is ZERO.","",
"NKR22 data-only bounds are unchanged: they deliberately omit these added",
"source-equation assumptions and concern realized missing rewards. A known",
"model can calculate expectations without providing empirical validation of",
"new policy execution, real-world source truth or unfamiliar mechanisms.","",
"## Qualification and boundaries","",
"Public source Git SHA:c94e9a4cd3641588b6b8507e71ccee5c27032bdf.",
"Original source license:Apache-2.0. Original source snapshot is included only",
"as nonexecuted attributed reference text. The actual nominal probability",
"model is a mathematical interpretation of source decimal probabilities,",
"not a test of NumPy's PRNG implementation or new physical observations.","",
"Native modules/weights/acceptance were not changed; new source actions0.",
"scientific_pass=false; no owner runtime, merge, controller, schedule or paid API.",
f'Ubuntu audit:{linux["wall_seconds"]:.6f}s; Windows:{windows["wall_seconds"]:.6f}s.',
"Source SHA:"+source,
"Stable receipt:"+linux["stable_sha256"],
"Final whole-root/NKR05 and independent G29 both-OS qualification is pending",
"at evidence commit time; terminal PR receipt supplies the final source status."]
(HERE/"SESSION_REPORT.md").write_text("\n".join(lines)+"\n")
