"""FKP-17 frozen 64-TRAIN-world paired diagnostic, NOT original science.

Uses an existing, fully trained, public-foundation GRU checkpoint. All other
arms are fitted ONCE from the same public 32,768-record source corpus. Every
world physically executes an identical 24-action public exploratory tape and
16 individually chosen actions per arm, via the source-independent blind
harness. All seeds are known TRAIN, never original held DEV or TRANSFER.

No model/policy/hyperparameter adjustments based on measured return. Outputs
both positive and negative world results with full provenance/cost receipts.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import random
import time

import blind_public_harness as blind
import portable_recurrent as portable
import public_policies as direct
import recurrent_control as recurrent
import source_fixture as fixture
import strong_controls as independent

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "train_matrix_lock.json"
MODEL_LIMIT = 1048576
TRIALS = tuple(range(978100, 978164))
ARMS = blind.ARMS
EXPECTED_PRIOR_SHA256 = "c8400f67e8d26147de702c0c9bdba1f05581ee6f70635b3e9c90d73d6af81ecf"


def _model_bytes(policy):
    size = getattr(policy, "learned_bytes", None)
    if size is None:
        size = getattr(policy, "memory_bytes", None)
    if type(size) is not int or not 0 < size <= MODEL_LIMIT:
        raise ValueError("FKP17_MATRIX_MODEL_CAPACITY")
    return size


def _seconds(value):
    if not math.isfinite(value) or value < 0:
        raise ValueError("FKP17_MATRIX_INVALID_COST")
    return value


class TimedPublicArm:
    """Transparent measurement wrapper; never supplies a future label."""
    def __init__(self, impl):
        self.impl = impl
        self.inference_calls = 0
        self.update_calls = 0
        self.inference_wall = 0.0
        self.update_wall = 0.0
        self.inference_cpu = 0.0
        self.update_cpu = 0.0

    def begin_world(self):
        self.impl.begin_world()
        self.inference_calls = self.update_calls = 0
        self.inference_wall = self.update_wall = 0.0
        self.inference_cpu = self.update_cpu = 0.0

    def choose_public(self, public_state):
        t0, c0 = time.perf_counter(), time.process_time()
        chosen = self.impl.choose_public(public_state)
        self.inference_wall += time.perf_counter() - t0
        self.inference_cpu += time.process_time() - c0
        self.inference_calls += 1
        if type(chosen) is not int or not 0 <= chosen < 8:
            raise ValueError("FKP17_MATRIX_INVALID_CHOSEN_ACTION")
        return chosen

    def observe_public(self, public_row):
        t0, c0 = time.perf_counter(), time.process_time()
        self.impl.observe_public(public_row)
        self.update_wall += time.perf_counter() - t0
        self.update_cpu += time.process_time() - c0
        self.update_calls += 1

    def state_receipt(self):
        return self.impl.state_receipt()

    def timings(self):
        if self.inference_calls != 16 or self.update_calls != 40:
            raise ValueError("FKP17_MATRIX_PHYSICAL_ACTION_COUNT")
        return {
            "inference_calls": self.inference_calls,
            "public_observations": self.update_calls,
            "inference_wall_seconds": _seconds(self.inference_wall),
            "update_wall_seconds": _seconds(self.update_wall),
            "inference_cpu_seconds": _seconds(self.inference_cpu),
            "update_cpu_seconds": _seconds(self.update_cpu),
        }


def _mean(values):
    if not values:
        raise ValueError("FKP17_MATRIX_EMPTY_SAMPLE")
    if not all(type(x) in (int, float) and math.isfinite(x) for x in values):
        raise ValueError("FKP17_MATRIX_NONFINITE_RETURN")
    return sum(values) / len(values)


def paired_bootstrap(rewards, *, draws=10000, seed=1515,
                     candidate="STRUCTURED", control_names=()):
    """Per-replicate reselect strongest comparator; no oracle information.

    The interval describes known-family TRAIN data only; it cannot satisfy
    the frozen DEV/TRANSFER scientific thresholds.
    """
    if type(draws) is not int or draws != 10000 or seed != 1515:
        raise ValueError("FKP17_MATRIX_FROZEN_BOOTSTRAP")
    if tuple(rewards) != TRIALS:
        raise ValueError("FKP17_MATRIX_MISSING_OR_REORDERED_TRAIN_WORLDS")
    control_names = tuple(control_names)
    if not control_names or candidate in control_names or len(set(control_names)) != len(control_names):
        raise ValueError("FKP17_MATRIX_CONTROL_SELECTION_INVALID")
    if any(set(row) != set(ARMS) for row in rewards.values()):
        raise ValueError("FKP17_MATRIX_INCOMPLETE_ARM_SCORES")
    n = len(TRIALS)
    rows = tuple(rewards[s] for s in TRIALS)
    means = {name: _mean([row[name] for row in rows]) for name in ARMS}
    strongest_name = max(control_names, key=lambda k: means[k])
    paired = means[candidate] - means[strongest_name]
    rng = random.Random(seed)
    sample = []
    for _ in range(draws):
        chosen = [rows[rng.randrange(n)] for _ in range(n)]
        c = _mean([row[candidate] for row in chosen])
        # Choosing the best control INSIDE each replicate correctly accounts
        # for the winning comparator being selected from multiple controls.
        strongest = max(_mean([row[name] for row in chosen])
                        for name in control_names)
        sample.append(c - strongest)
    sample.sort()
    return {
        "means": means,
        "strongest_matched_control": strongest_name,
        "paired_gain_vs_strongest_control": paired,
        "paired_gain_vs_minimal_prior_ablation": means[candidate] - means["MINIMAL"],
        "reselected_control_world_bootstrap_95_ci": [sample[249], sample[9749]],
        "bootstrap_seed": seed,
        "bootstrap_replicates": draws,
        "worlds": n,
        "known_family_only": True,
        "scientific_pass": False,
    }


def _load_lock():
    p = json.loads(LOCK.read_text(encoding="utf-8"))
    if p["schema"] != "fkp17.public-train-matrix-lock.v1":
        raise ValueError("FKP17_MATRIX_WRONG_FROZEN_PROTOCOL")
    if (p["seed_schedule"]["start"], p["seed_schedule"]["end"],
            p["seed_schedule"]["count"]) != (978100, 978163, 64):
        raise ValueError("FKP17_MATRIX_SEED_LOCK_DRIFT")
    if tuple(p["arms"]) != ARMS or p["prior_public_sha256"] != EXPECTED_PRIOR_SHA256:
        raise ValueError("FKP17_MATRIX_ARM_OR_PRIOR_DRIFT")
    if p["checkpoint_file_sha256"] != (
            "4cb2ad52ffe9cf5e89c61fadc6751260e5ce8f1d89772d9ffbd17a76cae6e2c3"):
        raise ValueError("FKP17_MATRIX_CHECKPOINT_LOCK_DRIFT")
    if p["held_source_rules"] != {
            "no_dev": True, "no_reserved_transfer": True,
            "no_owner_first_use": True, "original_dev_start": 978500,
            "original_transfer_start": 978600}:
        raise ValueError("FKP17_MATRIX_HELD_SOURCE_AUTHORITY_DRIFT")
    if (p["primary_known_family_diagnostic"]["bootstrap_seed"] != 1515 or
            p["primary_known_family_diagnostic"]["bootstrap_draws"] != 10000):
        raise ValueError("FKP17_MATRIX_BOOTSTRAP_DRIFT")
    return p


def evaluate_known_train_matrix(checkpoint):
    lock = _load_lock()
    path = Path(checkpoint)
    if not path.is_file() or sha256(path.read_bytes()).hexdigest() != (
            lock["checkpoint_file_sha256"]):
        raise ValueError("FKP17_MATRIX_CHECKPOINT_SHA_MISMATCH")
    started = time.perf_counter()
    facts = tuple(row for _, _, row in fixture.foundation_facts())
    if len(facts) != 32768:
        raise ValueError("FKP17_MATRIX_PUBLIC_FOUNDATION_SHORT")
    setup = {}
    arms = {}
    for name in direct.ARMS:
        begin = time.perf_counter()
        arms[name] = direct.PublicRelationArm(name).fit_public_foundation(facts)
        setup[name] = _seconds(time.perf_counter() - begin)
    common = direct.assert_equal_public_foundation(arms.values())
    for name, constructor in (
            ("BAYES_SYMBOLIC", independent.SymbolicBayes),
            ("COUNT_RETRIEVAL", independent.CountRetrieval)):
        begin = time.perf_counter()
        arms[name] = constructor().fit_public_foundation(facts)
        setup[name] = _seconds(time.perf_counter() - begin)
    independent.assert_strong_public_information(
        (arms["BAYES_SYMBOLIC"], arms["COUNT_RETRIEVAL"]), common)
    if common != lock["prior_public_sha256"]:
        raise ValueError("FKP17_MATRIX_FOUNDATION_DIGEST_MISMATCH")
    begin = time.perf_counter()
    arms["RECURRENT"] = portable.restore_public_gru(path, common)
    setup["RECURRENT"] = _seconds(time.perf_counter() - begin)
    recurrent.assert_science_ready(arms["RECURRENT"], common)
    if tuple(arms) != ARMS:
        raise ValueError("FKP17_MATRIX_ARM_ORDER_OR_MISSING_CONTROL")
    sizes = {name: _model_bytes(arm) for name, arm in arms.items()}
    timed = {name: TimedPublicArm(arm) for name, arm in arms.items()}
    rewards = {}
    per_world = []
    cost = {name: {"inference_calls": 0, "public_observations": 0,
                   "inference_wall_seconds": 0.0, "update_wall_seconds": 0.0,
                   "inference_cpu_seconds": 0.0, "update_cpu_seconds": 0.0}
            for name in ARMS}
    for seed in TRIALS:
        if fixture.cohort(seed) != "TRAIN":
            raise PermissionError("FKP17_MATRIX_NOT_TRAIN_COHORT")
        tape = fixture.public_actions(seed, 24)
        wall = time.perf_counter()
        observed = blind.evaluate_training_fixture(
            lambda s=seed: fixture.PublicSession(s), tape, timed, seed)
        elapsed = _seconds(time.perf_counter() - wall)
        row = {name: observed["arms"][name]["actual_public_reward"] for name in ARMS}
        if set(row) != set(ARMS) or any(
                observed["arms"][name]["scored_steps"] != 16 for name in ARMS):
            raise ValueError("FKP17_MATRIX_INCOMPLETE_REAL_ACTIONS")
        rewards[seed] = row
        for name in ARMS:
            receipt = timed[name].timings()
            for key, val in receipt.items():
                cost[name][key] += val
        per_world.append({
            "seed": seed,
            "actual_rewards": row,
            "shared_exploration_sha256": observed["identical_exploration_sha256"],
            "chosen_action_hash_by_arm": {
                name: sha256(json.dumps(observed["arms"][name]["selected_actions"],
                                        separators=(",", ":")).encode("ascii")).hexdigest()
                for name in ARMS
            },
            "actual_scored_steps_per_arm": {name: 16 for name in ARMS},
            "world_wall_seconds": elapsed,
        })
    comparison = paired_bootstrap(
        rewards, draws=lock["primary_known_family_diagnostic"]["bootstrap_draws"],
        seed=lock["primary_known_family_diagnostic"]["bootstrap_seed"],
        candidate=lock["primary_known_family_diagnostic"]["candidate"],
        control_names=tuple(lock["primary_known_family_diagnostic"]["matched_information_controls"]))
    if any(cost[n]["inference_calls"] != 64 * 16 or
           cost[n]["public_observations"] != 64 * 40 for n in ARMS):
        raise ValueError("FKP17_MATRIX_CUMULATIVE_ACTION_COUNT")
    return {
        "schema": "fkp17.known-train-64-world-diagnostic.v1",
        "classification": "KNOWN_TRAIN_ONLY_NOT_UNFAMILIAR_LAW_SCIENCE",
        "source_commit_original": None,  # workflow binds actual git SHA
        "checkpoint_sha256": lock["checkpoint_file_sha256"],
        "source_public_sha256": common,
        "seed_start": TRIALS[0],
        "seed_end": TRIALS[-1],
        "worlds": len(TRIALS),
        "exploration_actions_per_arm_per_world": 24,
        "scored_actual_actions_per_arm_per_world": 16,
        "foundation_records": len(facts),
        "bootstrap": comparison,
        "fit_or_restore_wall_seconds": setup,
        "model_parameter_bytes": sizes,
        "per_arm_whole_64_world_cost": cost,
        "per_world": per_world,
        "whole_process_wall_seconds": _seconds(time.perf_counter() - started),
        "fresh_dev_opened": False,
        "reserved_transfer_opened": False,
        "independent_scientific_pass": False,
        "native_yggdrasil_changed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint_file", help="Previously trained, original public FOUNDATION artifact")
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()
    report = evaluate_known_train_matrix(args.checkpoint_file)
    target = Path(args.output_json)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n",
                      encoding="utf-8")
    # Keep action receipts in artifact, summary in CI log only.
    concise = {k: report[k] for k in (
        "schema", "classification", "checkpoint_sha256", "worlds",
        "source_public_sha256", "bootstrap", "whole_process_wall_seconds",
        "fresh_dev_opened", "reserved_transfer_opened",
        "independent_scientific_pass", "native_yggdrasil_changed")}
    print("FKP17_KNOWN_TRAIN_64_WORLD_RESULT=" +
          json.dumps(concise, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
