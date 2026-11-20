"""KNOW21: frozen new *shift schedules* for original KNOW20 sparse memory.

NOT a new model, checkpoint owner, or real-source experiment. Reuses
NOISY original public controller, and separate hidden simulator. Source IDs
are intentionally reused, while private noise seeds and switch timings are new.
Prereg SHA: 371727480dc70686b25340a3653ebf6b826a1961.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from noisy_regime_memory_dev import (
    NativeSparseRegimeMemory, StationaryBeta, RollingBeta, ResetBeta,
    BayesianHMM, DeterministicRandom, PassiveZero,
    HELD as PUBLIC_SCENES, SOURCE_MODE, canonical, digest, require,
)

PREREG_COMMIT = "371727480dc70686b25340a3653ebf6b826a1961"
SCHEMA = "yggdrasil.know21.unfamiliar-regime-schedules-result.v1"
STEP_COUNT = 48
PROTOCOL = "yggdrasil.know21.unfamiliar-regime-schedules-frozen-dev.v1"

# The names and signatures are frozen in the prior, separately committed JSON.
FAMILIES = (
    ("early_return", (11, 29), (7207, 7309)),
    ("late_return", (19, 37), (7411, 7523)),
    ("early_odd_shifts", (8, 24, 37), (7639, 7753)),
    ("short_four_switches", (6, 18, 30, 40), (7867, 7979)),
    ("late_fast_return", (27, 36), (8093, 8209)),
    ("middle_return", (10, 24), (8317, 8431)),
)
POLICIES = (
    "native", "stationary_beta", "rolling_8", "gated_reset",
    "bayes_hmm", "seeded_random", "passive_zero", "truth_oracle",
)
STRONG_CONTROLS = ("stationary_beta", "rolling_8", "gated_reset", "bayes_hmm")


def ensure_protocol():
    p = json.loads(Path(__file__).with_name("know21_protocol.json").read_text(
        encoding="utf-8"))
    require(p.get("schema") == PROTOCOL and
            p.get("source", {}).get("source_mode") == SOURCE_MODE and
            p.get("source", {}).get("original_model_untouched") is True and
            p.get("budgets", {}).get("per_policy_actions") == 1152 and
            p.get("budgets", {}).get("steps_per_world") == STEP_COUNT and
            p.get("prior_know20_held_scenes") == list(PUBLIC_SCENES),
            "FROZEN_PROTOCOL")
    source_rows = p.get("frozen_cases")
    require(isinstance(source_rows, list) and len(source_rows) == 6 and all(
        src == {"family": name, "switches": list(switches),
                "replicates": list(seeds)}
        for src, (name, switches, seeds) in zip(source_rows, FAMILIES)),
        "FROZEN_FAMILIES")
    require(p.get("roles") == [0, 1], "FROZEN_ROLES")
    return p


def validate_world(seed, role, shifts):
    require(type(seed) is int and any(seed in seeds for _, _, seeds in FAMILIES),
            "PRIVATE_SEED")
    require(type(role) is int and role in (0, 1), "PRIVATE_ROLE")
    require(type(shifts) is tuple and shifts in tuple(s for _, s, _ in FAMILIES),
            "FROZEN_SCHEDULE")


def optimal_action(role, t, shifts):
    require(type(role) is int and role in (0, 1)
            and type(t) is int and 0 <= t < STEP_COUNT
            and type(shifts) is tuple and shifts in tuple(s for _, s, _ in FAMILIES),
            "PRIVATE_LAW")
    return role ^ (sum(t >= s for s in shifts) & 1)


def private_noise(seed, role, t):
    require(type(seed) is int and type(role) is int and role in (0, 1)
            and type(t) is int and 0 <= t < STEP_COUNT
            and any(seed in seeds for _, _, seeds in FAMILIES), "PRIVATE_NOISE")
    raw = f"know21:private:noise:v1:{seed}:{role}:{t}".encode("ascii")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") / (1 << 64)


def consequence(seed, role, t, action, shifts):
    validate_world(seed, role, shifts)
    require(type(action) is int and action in (0, 1), "ACTION")
    correct = optimal_action(role, t, shifts)
    p = 0.8 if action == correct else 0.2
    return int(private_noise(seed, role, t) < p)


def new_control(name, scene):
    if name == "stationary_beta":
        return StationaryBeta()
    if name == "rolling_8":
        return RollingBeta()
    if name == "gated_reset":
        return ResetBeta()
    if name == "bayes_hmm":
        return BayesianHMM()
    if name == "seeded_random":
        return DeterministicRandom(scene)
    if name == "passive_zero":
        return PassiveZero()
    raise ValueError("YGG_KNOW21_UNKNOWN_CONTROL")


def evaluate_world(name, scene, seed, role, shifts):
    validate_world(seed, role, shifts)
    require(type(scene) is int and scene in PUBLIC_SCENES
            and name in POLICIES, "WORLD")
    # Every public policy starts empty for each new private world. Never
    # share the previous role/world's learned state.
    state = NativeSparseRegimeMemory() if name == "native" else (
        None if name == "truth_oracle" else new_control(name, scene))
    action_trace = []
    brier_total = 0.0
    rewards = 0
    wrong = 0
    return_wrong = 0
    end_segment = shifts[-1] if len(shifts) % 2 == 0 else None
    return_steps = 0
    for t in range(STEP_COUNT):
        best = optimal_action(role, t, shifts)  # private evaluator only
        if name == "native":
            action = state.choose(scene)
            predicted = state.predict(scene, action)
        elif name == "truth_oracle":
            action, predicted = best, 0.8
        else:
            action = state.choose()
            predicted = state.predict(action)
        require(type(action) is int and action in (0, 1)
                and type(predicted) in (int, float)
                and 0 <= predicted <= 1, "POLICY_OUTPUT")
        reward = consequence(seed, role, t, action, shifts)
        rewards += reward
        brier_total += (predicted - reward) ** 2
        error = int(action != best)
        wrong += error
        if end_segment is not None and t >= end_segment:
            return_steps += 1
            return_wrong += error
        action_trace.append((action, reward))
        if name == "native":
            state = state.stage(scene, t, action, reward,
                                source_mode=SOURCE_MODE)
        elif name != "truth_oracle":
            state.observe(action, reward)
    switches = state.switches(scene) if name == "native" else (
        state.switch_count if name == "gated_reset" else None)
    checkpoint_bytes = len(state.checkpoint()) if name == "native" else None
    if name == "native":
        raw = state.checkpoint()
        cold = NativeSparseRegimeMemory.restore(raw, digest(raw))
        require(cold.checkpoint() == raw
                and all(cold.predict(scene, a) == state.predict(scene, a)
                        for a in (0, 1)), "COLD_CHECKPOINT")
    return {"wrong": wrong, "return_wrong": return_wrong,
            "return_steps": return_steps, "rewards": rewards,
            "brier": brier_total, "switches": switches,
            "checkpoint_bytes": checkpoint_bytes, "witnessed": STEP_COUNT,
            "trace_sha256": digest(canonical(action_trace))}


def summarize(rows):
    n = sum(x["witnessed"] for x in rows)
    ret = sum(x["return_steps"] for x in rows)
    require(n == 1152 and ret == 372, "EXPECTED_BUDGET")
    wrong = sum(x["wrong"] for x in rows)
    ret_wrong = sum(x["return_wrong"] for x in rows)
    return {
        "worlds": len(rows), "witnessed_actions": n,
        "expected_regret": round(0.6 * wrong / n, 8),
        "correct_action_rate": round(1 - wrong / n, 8),
        "return_expected_regret": round(0.6 * ret_wrong / ret, 8),
        "return_actions": ret,
        "realized_reward_rate": round(sum(x["rewards"] for x in rows) / n, 8),
        "prequential_brier": round(sum(x["brier"] for x in rows) / n, 8),
        "switches_total": (sum(x["switches"] for x in rows)
                           if rows[0]["switches"] is not None else None),
        "max_checkpoint_bytes": max(
            (x["checkpoint_bytes"] or 0) for x in rows),
        "world_traces_sha256": digest(canonical(
            [x["trace_sha256"] for x in rows]))
    }


def study():
    ensure_protocol()
    started = time.monotonic()
    by_policy = {}
    by_family = {}
    for name in POLICIES:
        rows = []
        family_data = {}
        for (family, shifts, seeds), scene in zip(FAMILIES, PUBLIC_SCENES):
            current = [
                evaluate_world(name, scene, seed, role, shifts)
                for seed in seeds for role in (0, 1)]
            rows.extend(current)
            family_data[family] = {
                "worlds": len(current),
                "actions": sum(x["witnessed"] for x in current),
                "expected_regret": round(
                    0.6 * sum(x["wrong"] for x in current) / 192, 8),
                "return_expected_regret": round(
                    0.6 * sum(x["return_wrong"] for x in current)
                    / sum(x["return_steps"] for x in current), 8)
                if sum(x["return_steps"] for x in current) else None,
                "switches": (sum(x["switches"] for x in current)
                             if current[0]["switches"] is not None else None)
            }
        by_policy[name] = summarize(rows)
        by_family[name] = family_data
    n = by_policy["native"]
    station = by_policy["stationary_beta"]
    rolling = by_policy["rolling_8"]
    reset = by_policy["gated_reset"]
    survival_reset = round(
        reset["return_expected_regret"] - n["return_expected_regret"], 8)
    survival_rolling = round(
        rolling["return_expected_regret"] - n["return_expected_regret"], 8)
    overall_stationary = round(
        station["expected_regret"] - n["expected_regret"], 8)
    return_supported = survival_reset >= 0.02 and survival_rolling >= 0.01
    overall_supported = overall_stationary >= 0.03
    dev = ("RETURN_MEMORY_DEVELOPMENT_SUPPORTED"
           if return_supported and overall_supported
           else "MIXED_RETURN_MEMORY"
           if return_supported or overall_supported
           else "RETURN_MEMORY_NO_GO")
    return {
        "schema": SCHEMA, "prereg_commit": PREREG_COMMIT,
        "source_mode": SOURCE_MODE,
        "original_know20_source_unchanged": True,
        "unfamiliar_operator_grammar": False,
        "new_private_shift_schedules": True,
        "new_private_noise_seeds": True,
        "same_public_source_scene_ids_as_know20": True,
        "held_worlds": 24, "per_policy_actions": 1152,
        "held_policy_results": by_policy,
        "family_results": by_family,
        "frozen_claim_tests": {
            "return_vs_reset_margin": survival_reset,
            "return_vs_rolling_margin": survival_rolling,
            "overall_vs_stationary_margin": overall_stationary,
            "return_supported": return_supported,
            "overall_supported": overall_supported
        },
        "development_verdict": dev,
        "strongest_control_regret": min(
            by_policy[key]["expected_regret"] for key in STRONG_CONTROLS),
        "engineering_gate": "PASS",
        "scientific_gate": "DEV_ONLY_STRONGEST_CONTROL_AND_REAL_FIRST_USE_NOT_QUALIFIED",
        "accepted_model_changed": False,
        "protected_original_first_use": False,
        "deployment": "NONE",
        "isolated_wall_seconds": round(time.monotonic() - started, 6)
    }


if __name__ == "__main__":
    print(json.dumps(study(), indent=2, sort_keys=True))
