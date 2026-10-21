"""MR17: authentic source-native observation alias audit, DEVELOPMENT ONLY.

Falsifies sufficiency of the frozen MR15 eight-bit public visual-change
interface using the original pinned MiniGrid .step() only. No model is
trained, no source world internals are read, and no outcome reaches a learner.
Observed empirical conditional Brier floors are sample descriptions, NOT
protected scientific performance or population-level impossibility proofs.
"""
from collections import defaultdict
from hashlib import sha256
import json
import pathlib
import subprocess
import sys

from research.mr15.public_view_delta import (
    PublicViewLocalDelta, SOURCE_COMMIT, public_raw_view
)

# Predeclared development-only; no adaptation based on recorded outcomes.
SEEDS = (11, 13, 17, 19)
ACTIONS = (0, 2, 1, 2, 0, 2, 1, 2, 5, 3, 2, 1, 2, 0, 2, 5)


def require_original_source(path):
    root = pathlib.Path(path).resolve()
    head = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    status = subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain"], text=True
    ).strip()
    if head != SOURCE_COMMIT or status:
        raise ValueError("MR17_ORIGINAL_NATIVE_SOURCE_CUSTODY_FAILED")
    return root


def native_rows(env_ctor, source_family, seed):
    env = env_ctor()
    try:
        public_observation, _ = env.reset(seed=seed)
        sensor = PublicViewLocalDelta()
        sensor.prime(public_observation["image"])
        rows = []
        for step, action in enumerate(ACTIONS):
            # Both candidate-facing bits and privileged-free richer public
            # sensor contents are recorded *before* original source action.
            before_bits = tuple(sensor.bits)
            before_raw = public_raw_view(public_observation["image"])
            before_snap = sensor.snapshot()
            if (len(before_bits) != 8 or len(before_raw) != 24 or
                sensor.steps != step):
                raise ValueError("MR17_PUBLIC_SENSOR_STATE_DRIFT")
            next_observation, _reward, _done, _truncated, _info = env.step(action)
            event = sensor.observe_after_native_step(
                action, next_observation["image"]
            )
            outcome = tuple(event["observed_next_local_bits"])
            if (event["prior_local_bits"] != list(before_bits) or
                event["observed_action"] != action or
                len(outcome) != 8 or
                any(bit not in (0, 1) for bit in outcome)):
                raise ValueError("MR17_NATIVE_ACTION_CONSEQUENCE_DRIFT")
            if step == 7:
                snapshot = sensor.snapshot()
                restored = PublicViewLocalDelta.restore(snapshot)
                if snapshot != restored.snapshot():
                    raise ValueError("MR17_SENSOR_RESTART_NOT_IDENTICAL")
                sensor = restored
            rows.append({
                "source_family": source_family, "seed": seed, "step": step,
                "prior_bits": before_bits, "action": action,
                "prior_public_sample": before_raw, "next_bits": outcome,
                "source_commit": SOURCE_COMMIT,
                "prior_sensor_snapshot_sha256": sha256(
                    before_snap.encode("utf-8")
                ).hexdigest()
            })
            public_observation = next_observation
        return rows
    finally:
        env.close()


def conditional_brier_floor(groups):
    count = sum(len(v) for v in groups.values())
    if not count:
        raise ValueError("MR17_EMPTY_NATIVE_OBSERVATIONS")
    numerator = 0.0
    for rows in groups.values():
        for cell in range(8):
            positives = sum(row["next_bits"][cell] for row in rows)
            p = positives / len(rows)
            numerator += len(rows) * p * (1.0 - p)
    return numerator / (8 * count)


def observed_alias_audit(rows):
    coarse = defaultdict(list)
    richer = defaultdict(list)
    for row in rows:
        # The original MR16 learner can see exactly these prior bits/action;
        # the 24-byte raw public sidecar was explicitly NOT a model feature.
        key = (row["prior_bits"], row["action"])
        coarse[key].append(row)
        richer[key + (row["prior_public_sample"],)].append(row)
    source_aliases = []
    same_raw_aliases = 0
    for key, members in coarse.items():
        distinct_outcomes = {r["next_bits"] for r in members}
        if len(distinct_outcomes) < 2:
            continue
        # Two actual original events with same coarse input and action but
        # different native next bits. Try to witness distinct public context.
        pair = next(
            ((a, b) for i, a in enumerate(members)
              for b in members[i+1:]
              if a["next_bits"] != b["next_bits"]), None
        )
        if pair is None:
            raise AssertionError("MR17_NONDETERMINISTIC_ALIAS_INDEX")
        if pair[0]["prior_public_sample"] == pair[1]["prior_public_sample"]:
            same_raw_aliases += 1
        if len(source_aliases) < 8:
            source_aliases.append({
                "identical_model_bits": list(key[0]),
                "identical_original_action": key[1],
                "first": {
                    "source_environment": pair[0]["source_family"],
                    "seed": pair[0]["seed"], "step": pair[0]["step"],
                    "native_next_bits": list(pair[0]["next_bits"]),
                    "prior_public_sample_sha256": sha256(
                        bytes(pair[0]["prior_public_sample"])
                    ).hexdigest(),
                },
                "second": {
                    "source_environment": pair[1]["source_family"],
                    "seed": pair[1]["seed"], "step": pair[1]["step"],
                    "native_next_bits": list(pair[1]["next_bits"]),
                    "prior_public_sample_sha256": sha256(
                        bytes(pair[1]["prior_public_sample"])
                    ).hexdigest(),
                },
                "different_previous_public_tile_bytes":
                    pair[0]["prior_public_sample"] !=
                    pair[1]["prior_public_sample"],
            })
    conflict = sum(len({r["next_bits"] for r in m}) > 1
                   for m in coarse.values())
    coarse_floor = conditional_brier_floor(coarse)
    richer_floor = conditional_brier_floor(richer)
    if richer_floor > coarse_floor + 1e-10:
        raise ValueError("MR17_INFORMATION_MONOTONICITY_VIOLATION")
    return {
        "native_original_events": len(rows),
        "unique_eight_bits_action_contexts": len(coarse),
        "conflicting_coarse_model_contexts": conflict,
        "coarse_aliases_also_same_raw_public_sample":
            same_raw_aliases,
        "observed_coarse_empirical_brier_floor": coarse_floor,
        "observed_24byte_sidecar_empirical_brier_floor": richer_floor,
        "empirical_public_detail_gain":
            max(0.0, coarse_floor-richer_floor),
        "representative_original_native_aliases": source_aliases,
        "no_observed_collision_proves_sufficiency": False,
        "empirical_floors_are_not_generalization_bounds": True,
        "history_or_unobserved_state_can_still_matter": True,
    }


def main(source_root):
    root = require_original_source(source_root)
    sys.path.insert(0, str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    rows = []
    for env_type, family in (
        (lambda: DoorKeyEnv(size=5, render_mode=None), "DoorKeyEnv(5)"),
        (lambda: EmptyEnv(size=8, render_mode=None), "EmptyEnv(8)"),
    ):
        for seed in SEEDS:
            rows.extend(native_rows(env_type, family, seed))
    if len(rows) != 2 * len(SEEDS) * len(ACTIONS):
        raise ValueError("MR17_NATIVE_EVENT_BUDGET_CHANGED")
    by_family = {}
    for family in ("DoorKeyEnv(5)", "EmptyEnv(8)"):
        by_family[family] = observed_alias_audit([
            row for row in rows if row["source_family"] == family
        ])
    print("MR17_ORIGINAL_NATIVE_CAUSAL_ALIAS_AUDIT="+json.dumps({
        "source_commit": SOURCE_COMMIT,
        "frozen_predeclared_development_seeds": list(SEEDS),
        "frozen_action_script": list(ACTIONS),
        "by_environment": by_family,
        "combined": observed_alias_audit(rows),
        "models_trained": False,
        "original_45_coefficients_changed": False,
        "independent_scientific_first_use": False,
        "source_hidden_world_or_oracle_read": False,
        "full_process_cpu_peak_rss": "NOT_QUALIFIED",
        "source_license_discrepancy": "UNRESOLVED",
        "g29_atlas": "NOT_QUALIFIED",
        "scientific_admission": "NO_GO"
    }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m research.mr17.native_alias_audit UPSTREAM")
    main(sys.argv[1])
