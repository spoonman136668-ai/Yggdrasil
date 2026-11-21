"""Gate26 independent numerical/custody receipt audit; not independent learner replication."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
pre = json.loads((here / "prereg.json").read_text(encoding="utf-8"))
result = json.loads((here / "result.json").read_text(encoding="utf-8"))
runner = (here / "run.py").read_text(encoding="utf-8")
stage = (here / "stage.py").read_text(encoding="utf-8")
native_file = here.parents[4] / "yggdrasil" / "public_causal_cells.py"
native = native_file.read_bytes()
git_blob = hashlib.sha1(("blob " + str(len(native.replace(b"\r\n", b"\n"))) + "\0").encode()
                        + native.replace(b"\r\n", b"\n")).hexdigest()

assert pre["experiment_id"] == "GATE26-NATIVE-PUBLIC-CAUSAL-CROSS-PROCESS-FUNCTIONAL-RETENTION-20261120"
assert result["prereg_commit"] == "5840ca52435204b4351c46ce528dcaf98cd35263"
assert result["parent_commit"] == "df8464eac118e29386495de61567b3c8cae0f722"
assert result["native_git_blob"] == git_blob == "5c9a9904e31688bebc2e53723569e1fb988a981f"
assert result["cohorts"]["n"] == 24
assert result["cohorts"]["source_experiences_per_seed"] == 480
assert result["cohorts"]["interference_experiences_per_seed"] == 640
assert result["cohorts"]["snapshot_bytes"] == 164
assert result["metrics"]["process_exit_restarts"] == 72
assert result["functional_retention_classification"] == "CROSS_PROCESS_FUNCTIONAL_COUNTER_RETENTION_PASS"
assert result["scientific_classification"] == "SCIENTIFIC_NO_GO_GENERALIZATION_AND_INTERFERENCE"
assert len(result["conditions"]) == 13
assert set(result["conditions"]) == set(pre["frozen_thresholds"])
assert [key for key, value in result["conditions"].items() if not value] == [
    "historical_active_source_return_accuracy_min",
    "independent_equal_evidence_beta_advantage_min",
    "unseen_context_transfer_gain_vs_scratch_min",
]
t = result["totals"]
assert t["worlds"] == 24
assert t["source_A_cold_exact"] == t["B_and_C_cold_exact"] == t["functional_readout_cold_exact"] == 24
assert t["process_identity_correct"] == 24
assert t["retained_denominator"] == t["retained_correct"] == t["retained_wilson_decisions"] == 120
assert t["retained_A_readout_exact"] == 120
assert t["historical_A_active_correct_after_B"] == 0
assert t["historical_A_active_denominator"] == 120
assert t["unseen_total"] == t["unseen_native_abstained"] == 144
assert t["native_correct_in_known_contexts"] == t["beta_correct"] == t["known_context_denominator"] == 240
assert t["tamper_attempts"] == t["tamper_rejections"] == 4
assert t["held_reward_trials"] == 3840
assert t["held_rewards"] == 3439
assert abs(result["metrics"]["held_reward_gain_vs_untrained_chance"] -
           ((t["held_rewards"] / t["held_reward_trials"]) - 0.5)) < 1e-9
assert result["metrics"]["unseen_context_transfer_gain_vs_scratch"] == 0
assert result["metrics"]["independent_equal_evidence_beta_advantage"] == 0
assert result["metrics"]["historical_active_source_return_accuracy"] == 0
assert 'subprocess.run(cmd' in runner and 'expect_failure=True' in runner
assert 'native.replace(b"\\r\\n", b"\\n")' in runner
assert 'PublicCausalCells.restore(raw)' in stage
assert 'args.output_checkpoint.write_bytes(output)' in stage
print("GATE26_RECEIPT_AUDIT_PASS FUNCTIONAL_COLD_RETENTION_PASS SCIENTIFIC_GENERALIZATION_NO_GO")
