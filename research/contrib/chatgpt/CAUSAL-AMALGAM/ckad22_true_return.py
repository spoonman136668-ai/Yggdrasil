"""Retrospective original CKAD22 same-law return; read-only archived receipt audit.

Never imports the learner/simulator, regenerates held cohorts, or updates checkpoints.
Original four-session synthetic held evidence was already consumed in CKAD22.
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from fractions import Fraction
from pathlib import Path

ZIP_SHA256 = "90362c075154ab936fc2e0a82716fbe5bd875585cd89aeed0b08b32831560fc4"
SOURCE_SHA256 = "20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
SCHEMA = "yggdrasil.ckad22.adaptive-context-development.result.v1"
SEEDS = (101, 202, 303)
WORLDS = (("terminal_switch", 0), ("invariant", 1),
          ("terminal_switch", 0), ("invariant", 0))
ARMS = ("beta", "exact_mixture", "frozen_ckad21", "novel_active",
        "novel_random", "pooled_replay", "retrieval_only", "trailing_mle")
BASELINES = tuple(a for a in ARMS if a not in ("novel_active", "exact_mixture"))
LOSSES = ("transition_brier", "terminal_brier", "pooled_brier")
METRICS = ("reward_sum",) + LOSSES


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_original(path: str | Path) -> dict:
    raw = Path(path).read_bytes()
    if sha256(raw) != ZIP_SHA256:
        raise ValueError("ORIGINAL_ZIP_SHA256_MISMATCH")
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    with zipfile.ZipFile(path) as z:
        expected = {"campaign-result.json"} | {
            f"seed-{s}-expanded-native.json" for s in SEEDS
        }
        if set(z.namelist()) != expected:
            raise ValueError("ORIGINAL_ARCHIVE_MEMBER_SET")
        d = json.loads(z.read("campaign-result.json"))
        cps = d.get("final_checkpoints")
        if type(cps) is not list or len(cps) != 3:
            raise ValueError("ORIGINAL_CHECKPOINT_MANIFEST")
        for cp in cps:
            if (cp.get("seed") not in SEEDS or
                cp.get("name") != f"seed-{cp.get('seed')}-expanded-native.json" or
                sha256(z.read(cp["name"])) != cp.get("sha256") or
                len(z.read(cp["name"])) != cp.get("bytes")):
                raise ValueError("ORIGINAL_CHECKPOINT_BYTES")
    return d


def validate(d: dict) -> None:
    if (d.get("schema") != SCHEMA or d.get("source_sha256") != SOURCE_SHA256
        or d.get("scientific_pass") is not False
        or d.get("accepted_native") is not False
        or d.get("deployment") != "NONE"
        or d.get("classification") != "DEVELOPMENT_GO"
        or d.get("scope", {}).get("original_source_actions") != 0
        or d.get("scope", {}).get("protected_first_use") != 0
        or d.get("scope", {}).get("held_updates") != 0):
        raise ValueError("FROZEN_SOURCE_SCIENCE_BOUNDARY")
    ss = d.get("seeds")
    if type(ss) is not list or [s.get("seed") for s in ss] != list(SEEDS):
        raise ValueError("EXACT_SEEDS_AND_ORDER")
    for s in ss:
        if s.get("source_seed") != s["seed"] + 7000:
            raise ValueError("FROZEN_SOURCE_SEED")
        sessions = s.get("sessions")
        if type(sessions) is not list or len(sessions) != 4:
            raise ValueError("FROZEN_SESSION_COUNT")
        for j, r in enumerate(sessions):
            if (r.get("session") != j or
                (r.get("family"), r.get("regime")) != WORLDS[j] or
                r.get("probe_cohort") != f"ckad22-probe-{j}" or
                r.get("held_cohort") != f"ckad22-held-{j}" or
                r.get("training_episodes") != 320 + 32 * (j + 1)):
                raise ValueError("FROZEN_SOURCE_WORLD_CLOCK")
            e = r.get("evaluation")
            if type(e) is not dict or set(e) != set(ARMS):
                raise ValueError("FROZEN_CONTROL_SET")
            for arm, v in e.items():
                if (v.get("episodes") != 96 or
                    type(v.get("reward_sum")) is not int or
                    not 0 <= v["reward_sum"] <= 96):
                    raise ValueError("HELD_EPISODE_BUDGET")
                for name in LOSSES:
                    fraction = v.get(name)
                    if (type(fraction) is not list or len(fraction) != 2 or
                        any(type(a) is not int for a in fraction) or
                        fraction[0] < 0 or fraction[1] <= 0):
                        raise ValueError("SCORED_BRIER_FRACTION")


def audit(d: dict) -> dict:
    validate(d)
    rows = []
    parity = {k: 0 for k in METRICS}
    for j, (family, regime) in enumerate(WORLDS):
        evaluations = [s["sessions"][j]["evaluation"] for s in d["seeds"]]
        score = {arm: sum(e[arm]["reward_sum"] for e in evaluations)
                 for arm in ARMS}
        brier = {arm: {metric: sum(
            float(Fraction(*e[arm][metric])) for e in evaluations) / 3
            for metric in LOSSES} for arm in ARMS}
        seed_scores = []
        for seed, e in zip(SEEDS, evaluations):
            old = e["novel_active"]["reward_sum"]
            strongest = max(e[arm]["reward_sum"] for arm in BASELINES)
            seed_scores.append({"seed": seed, "native": old,
                                "strongest_other": strongest,
                                "native_minus_strongest": old - strongest})
            for metric in METRICS:
                parity[metric] += (e["novel_active"][metric] ==
                                   e["exact_mixture"][metric])
        max_baseline = max(score[arm] for arm in BASELINES)
        rows.append({"session": j, "world": f"{family}/{regime}",
                     "n_scored_per_arm": 288,
                     "rewards_by_arm": score,
                     "brier_means_by_arm": brier,
                     "best_non_equivalent_control_reward": max_baseline,
                     "native_minus_best_control": score["novel_active"] - max_baseline,
                     "per_seed": seed_scores})
    if any(p != 12 for p in parity.values()):
        raise ValueError("ORIGINAL_INDEPENDENT_EXACT_MIXTURE_PARITY")
    return_row = rows[2]
    screen = (return_row["rewards_by_arm"]["novel_active"] * 5 >= 288 * 4
              and return_row["native_minus_best_control"] >= 15
              and all(x["native_minus_strongest"] >= 0 for x in return_row["per_seed"]))
    return {"schema": "yggdrasil.ckad22.true-full-world-return-audit.v1",
            "data_status": "historically_consumed_synthetic_held_development",
            "identical_complete_source_law_sessions": [0, 2],
            "return_is_after_probes": 32,
            "original_source_actions": 0,
            "new_learner_or_source_calls": 0,
            "independent_mixture_parity_over_12_seed_sessions": parity,
            "sessions": rows,
            "frozen_historical_return_advantage_screen":
                "RETURN_SCREEN_PASS" if screen else "RETURN_SCREEN_NO_GO",
            "scientific_gain_verified": False,
            "full_original_world_retention_proven": False,
            "deployment": "NONE"}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: ckad22_true_return.py HISTORICAL_ORIGINAL_ZIP")
    print(json.dumps(audit(read_original(sys.argv[1])), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
