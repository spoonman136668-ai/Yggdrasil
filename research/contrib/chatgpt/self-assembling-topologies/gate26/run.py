"""Gate26: true cross-process native counter checkpoint readout, source interference, controls.

The 24 new seeds are consumed by the first completed primary execution.
Separate fresh Python subprocesses must save, reload, and read functional decisions.
Research only; no accepted checkpoint, owner runner, or native Amalgam integration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import stage
from yggdrasil.public_causal_cells import PublicCausalCells

ROOT = Path(__file__).resolve().parents[5]
STAGE = Path(__file__).with_name("stage.py")
PINNED_NATIVE_GIT_BLOB = "5c9a9904e31688bebc2e53723569e1fb988a981f"


def git_blob(content: bytes) -> str:
    header = ("blob " + str(len(content)) + "\0").encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def call_stage(phase: str, seed: int, checkpoint_in: Path | None = None,
               checkpoint_out: Path | None = None, expect_failure: bool = False):
    cmd = [sys.executable, "-B", str(STAGE), "--phase", phase, "--seed", str(seed)]
    if checkpoint_in is not None:
        cmd.extend(["--input", str(checkpoint_in)])
    if checkpoint_out is not None:
        cmd.extend(["--output", str(checkpoint_out)])
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True,
                          text=True, timeout=30, check=False)
    if expect_failure:
        return proc.returncode != 0
    if proc.returncode != 0:
        raise RuntimeError("GATE26_CHILD_STAGE_FAILED " + phase +
                           " stderr=" + proc.stderr[-500:])
    record = json.loads(proc.stdout)
    if record["stage"] != phase or record["size"] != 164 or record["pid"] == os.getpid():
        raise AssertionError("GATE26_COLD_STAGE_IDENTITY_MISMATCH")
    return record


def independent_beta_choose(seed: int, retained: bool, address: int):
    """Independent Beta(1,1) evidence control, never reading native counters."""
    observed = []
    for action in (0, 1):
        samples = [
            stage.observation(seed, "A", retained, address, action, visit)
            for visit in range(24)
        ]
        if not retained:
            samples.extend(
                stage.observation(seed, "B", retained, address, action, visit)
                for visit in range(64)
            )
        observed.append((sum(samples) + 1) / (len(samples) + 2))
    if observed[0] == observed[1]:
        return None
    return 0 if observed[0] > observed[1] else 1


def rounded(x: float) -> float:
    return round(x, 10)


def execute():
    native = (ROOT / "yggdrasil" / "public_causal_cells.py").read_bytes()
    native_blob_valid = git_blob(native) == PINNED_NATIVE_GIT_BLOB
    if not native_blob_valid:
        raise AssertionError("GATE26_NATIVE_SOURCE_BLOB_DRIFT")
    totals = {
        "process_identity_correct": 0, "source_A_cold_exact": 0,
        "B_and_C_cold_exact": 0, "functional_readout_cold_exact": 0,
        "retained_raw_source_unchanged": 0, "retained_correct": 0,
        "retained_wilson_decisions": 0, "retained_denominator": 0,
        "B_active_correct": 0, "B_active_denominator": 0,
        "historical_A_active_correct_after_B": 0, "historical_A_active_denominator": 0,
        "beta_correct": 0, "native_correct_in_known_contexts": 0,
        "known_context_denominator": 0, "unseen_native_abstained": 0,
        "unseen_total": 0, "held_rewards": 0, "held_reward_trials": 0,
        "held_null_expected_rewards": 0, "retained_A_readout_exact": 0,
        "unfamiliar_native_correct": 0, "unfamiliar_scratch_correct": 0,
        "worlds": 0, "tamper_rejections": 0, "tamper_attempts": 0,
    }
    for seed in range(301000, 301024):
        with tempfile.TemporaryDirectory(prefix="ygg-g26-") as root:
            root_path = Path(root)
            A_file = root_path / "source.A.checkpoint"
            B_file = root_path / "interference.B.checkpoint"
            first = call_stage("train_a", seed, checkpoint_out=A_file)
            second = call_stage("train_b", seed, checkpoint_in=A_file,
                                checkpoint_out=B_file)
            third = call_stage("read_b", seed, checkpoint_in=B_file)
            snap_A = A_file.read_bytes()
            snap_B = B_file.read_bytes()
            warm = PublicCausalCells()
            stage.apply_events(warm, seed, "A")
            warm_A = warm.snapshot()
            original_A_readout = stage.readout(warm)
            stage.apply_events(warm, seed, "B")
            warm_B = warm.snapshot()

            pids = (first["pid"], second["pid"], third["pid"])
            totals["process_identity_correct"] += int(len(set(pids)) == 3)
            totals["source_A_cold_exact"] += int(
                snap_A == warm_A and first["digest"] == hashlib.sha256(snap_A).hexdigest()
                and first["readout"] == original_A_readout
            )
            totals["B_and_C_cold_exact"] += int(
                snap_B == warm_B
                and second["digest"] == hashlib.sha256(snap_B).hexdigest()
                and third["digest"] == second["digest"]
                and PublicCausalCells.restore(snap_B).snapshot() == snap_B
            )
            totals["functional_readout_cold_exact"] += int(
                second["readout"] == third["readout"] == stage.readout(warm)
            )
            # 7 active cells (56 bytes), then 9 retained cells (72 bytes).
            totals["retained_raw_source_unchanged"] += int(
                snap_A[60:132] == snap_B[60:132]
            )
            old = {(r["retained"], r["address"]): r for r in original_A_readout}
            now = {(r["retained"], r["address"]): r for r in third["readout"]}
            scratch = PublicCausalCells()
            for retained, capacity in ((False, 7), (True, 9)):
                for address in range(capacity):
                    key = (retained, address)
                    current = now[key]
                    if address >= 5:
                        totals["unseen_total"] += 1
                        if (current["choice"] is None and current["wilson"] is None
                                and current["contrast"] is None
                                and scratch.choose(address, retained=retained) is None):
                            totals["unseen_native_abstained"] += 1
                        # No generalization mechanism: an unsupported choice is
                        # scored as chance, identical to an untrained scratch cell.
                        totals["unfamiliar_native_correct"] += 0
                        totals["unfamiliar_scratch_correct"] += 0
                        continue
                    preference_B = stage.preference(seed, retained, address)
                    if not retained:
                        preference_B ^= 1
                        totals["B_active_denominator"] += 1
                        totals["B_active_correct"] += int(current["choice"] == preference_B)
                        totals["historical_A_active_denominator"] += 1
                        totals["historical_A_active_correct_after_B"] += int(
                            current["choice"] == stage.preference(seed, retained, address)
                        )
                    else:
                        totals["retained_denominator"] += 1
                        totals["retained_correct"] += int(current["choice"] == preference_B)
                        totals["retained_wilson_decisions"] += int(current["wilson"] is not None)
                        totals["retained_A_readout_exact"] += int(current == old[key])
                    independent_choice = independent_beta_choose(seed, retained, address)
                    totals["known_context_denominator"] += 1
                    totals["beta_correct"] += int(independent_choice == preference_B)
                    totals["native_correct_in_known_contexts"] += int(
                        current["choice"] == preference_B
                    )
                    for held_visit in range(16):
                        # Independent phase-domain samples: not previously observed.
                        result = stage.observation(
                            seed, "A" if retained else "B", retained,
                            address, current["choice"] if current["choice"] is not None else 0,
                            held_visit, held=True
                        )
                        totals["held_rewards"] += result
                        totals["held_reward_trials"] += 1
                        totals["held_null_expected_rewards"] += .5

            if seed == 301000:
                broken = {
                    "corrupt_digest": bytes(
                        snap_B[:18] + bytes([snap_B[18] ^ 1]) + snap_B[19:]
                    ),
                    "truncated": snap_B[:-1],
                    "wrong_magic": b"BAD!" + snap_B[4:],
                }
                for label, payload in broken.items():
                    invalid = root_path / (label + ".checkpoint")
                    invalid.write_bytes(payload)
                    totals["tamper_attempts"] += 1
                    totals["tamper_rejections"] += int(
                        call_stage("read_b", seed, checkpoint_in=invalid,
                                   expect_failure=True)
                    )
                totals["tamper_attempts"] += 1
                try:
                    PublicCausalCells.restore(bytearray(snap_B))
                except ValueError:
                    totals["tamper_rejections"] += 1
            totals["worlds"] += 1

    def fraction(numerator, denominator):
        return rounded(totals[numerator] / totals[denominator])
    retained = fraction("retained_correct", "retained_denominator")
    beta = fraction("beta_correct", "known_context_denominator")
    native = fraction("native_correct_in_known_contexts", "known_context_denominator")
    held_gain = rounded(
        (totals["held_rewards"] - totals["held_null_expected_rewards"]) /
        totals["held_reward_trials"]
    )
    unseen_gain = rounded(
        (totals["unfamiliar_native_correct"] - totals["unfamiliar_scratch_correct"]) /
        totals["unseen_total"]
    )
    metrics = {
        "worlds": totals["worlds"], "process_exit_restarts": totals["worlds"] * 3,
        "cross_process_functional_readout_exact_fraction":
            rounded(totals["functional_readout_cold_exact"] / 24),
        "cross_process_checkpoint_bytes_exact_fraction":
            rounded(min(totals["source_A_cold_exact"], totals["B_and_C_cold_exact"]) / 24),
        "distinct_parent_child_pids_all": totals["process_identity_correct"] == 24,
        "retained_source_choose_accuracy": retained,
        "retained_source_wilson_coverage":
            fraction("retained_wilson_decisions", "retained_denominator"),
        "retained_historical_bytes_preserved_all":
            totals["retained_raw_source_unchanged"] == 24
            and totals["retained_A_readout_exact"] == totals["retained_denominator"],
        "previously_unseen_address_abstention_fraction":
            fraction("unseen_native_abstained", "unseen_total"),
        "held_reward_gain_vs_untrained_chance": held_gain,
        "corruption_and_truncation_rejected_all":
            totals["tamper_rejections"] == totals["tamper_attempts"] == 4,
        "independent_equal_evidence_beta_advantage": rounded(native - beta),
        "historical_active_source_return_accuracy":
            fraction("historical_A_active_correct_after_B",
                     "historical_A_active_denominator"),
        "unseen_context_transfer_gain_vs_scratch": unseen_gain,
        "all_original_native_source_unmodified": native_blob_valid,
        "B_active_current_world_accuracy":
            fraction("B_active_correct", "B_active_denominator"),
        "independent_beta_accuracy": beta,
        "native_known_context_accuracy": native,
    }
    limits = {
        "cross_process_functional_readout_exact_fraction_min":
            metrics["cross_process_functional_readout_exact_fraction"] >= 1,
        "cross_process_checkpoint_bytes_exact_fraction_min":
            metrics["cross_process_checkpoint_bytes_exact_fraction"] >= 1,
        "distinct_parent_child_pids_all": metrics["distinct_parent_child_pids_all"],
        "retained_source_choose_accuracy_min": retained >= .85,
        "retained_source_wilson_coverage_min":
            metrics["retained_source_wilson_coverage"] >= .6,
        "retained_historical_bytes_preserved_all":
            metrics["retained_historical_bytes_preserved_all"],
        "previously_unseen_address_abstention_fraction_min":
            metrics["previously_unseen_address_abstention_fraction"] >= 1,
        "held_reward_gain_vs_untrained_chance_min": held_gain >= .10,
        "corruption_and_truncation_rejected_all":
            metrics["corruption_and_truncation_rejected_all"],
        "independent_equal_evidence_beta_advantage_min":
            metrics["independent_equal_evidence_beta_advantage"] >= .02,
        "historical_active_source_return_accuracy_min":
            metrics["historical_active_source_return_accuracy"] >= .80,
        "unseen_context_transfer_gain_vs_scratch_min": unseen_gain >= .10,
        "all_original_native_source_unmodified": native_blob_valid,
    }
    functional_pass = all(list(limits.values())[:9])
    science_pass = all(limits.values())
    return {
        "schema": "yggdrasil.gate26.native-cold-functional.v1",
        "prereg_commit": "5840ca52435204b4351c46ce528dcaf98cd35263",
        "parent_commit": "df8464eac118e29386495de61567b3c8cae0f722",
        "native_git_blob": PINNED_NATIVE_GIT_BLOB,
        "cohorts": {"first_seed": 301000, "last_seed": 301023, "n": 24,
                    "trained_active_contexts": 5, "trained_retained_contexts": 5,
                    "untrained_contexts": 6, "snapshot_bytes": 164,
                    "source_experiences_per_seed": 480,
                    "interference_experiences_per_seed": 640},
        "totals": totals,
        "metrics": metrics,
        "conditions": limits,
        "functional_retention_classification": (
            "CROSS_PROCESS_FUNCTIONAL_COUNTER_RETENTION_PASS" if functional_pass
            else "CROSS_PROCESS_FUNCTIONAL_COUNTER_RETENTION_FAIL"),
        "scientific_classification": (
            "SYNTHETIC_CUMULATIVE_GENERALIZATION_SIGNAL_ONLY" if science_pass
            else "SCIENTIFIC_NO_GO_GENERALIZATION_AND_INTERFERENCE"),
        "exclusions": {
            "dynamic_graph_spawning": False, "native_amalgam_checkpoint": False,
            "native_owner_first_use": False, "independent_novelty": False,
            "cross_context_transfer": False, "open_world_cognition": False,
            "deployment": False, "equal_compute": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = execute()
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise AssertionError("GATE26_EXACT_RESULT_MISMATCH")
        print("GATE26_EXACT_REPLAY_PASS " + result["scientific_classification"])
    else:
        print("GATE26_PRIMARY_JSON " + json.dumps(result, sort_keys=True,
                                                  separators=(",", ":")))
