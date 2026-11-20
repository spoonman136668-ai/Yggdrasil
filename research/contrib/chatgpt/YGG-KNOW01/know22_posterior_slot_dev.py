"""KNOW22: frozen, source-only posterior READOUT ablation over unchanged TGAP21 memory.

Preregistered in commit d3885412f6cc81a366f901b90d33169f399c32c3
before source implementation or any primary held outcome was scored.
NOT a native model, canonical training, source first-use, or owner integration.
"""
from __future__ import annotations

import copy
import json
import math
import time
from pathlib import Path

from tgap21_same_address_dev import (
    TwoSlotMemory, fit_memory, witness, digest,
    StationaryBeta, RollingBeta, ResetBeta, BayesianHMM, Uninformed,
)

SCHEMA = "yggdrasil.know22.posterior-memory-readout-result.v1"
PROTOCOL = "yggdrasil.know22.posterior-memory-readout-isolation-frozen-dev.v1"
PREREG = "d3885412f6cc81a366f901b90d33169f399c32c3"
SOURCE_MODE = "engineering_fixture_only"
HELD = ((8901, 0, 12, 36), (8903, 1, 12, 36),
        (8911, 0, 20, 44), (8917, 1, 20, 44),
        (8923, 0, 9, 33), (8929, 1, 9, 33),
        (8933, 0, 24, 48), (8941, 1, 24, 48))
POLICIES = ("posterior_fit", "gate_fit", "posterior_no_fit",
            "stationary_fit", "rolling_8_fit", "reset_fit",
            "bayes_hmm_fit", "source_only")
HAZARD = 1 / 16


def require(ok, code):
    if not ok:
        raise ValueError("YGG_KNOW22_" + code)


def frozen_protocol():
    p = json.loads(Path(__file__).with_name("know22_protocol.json").read_text("utf-8"))
    require(p["schema"] == PROTOCOL
            and p["data"]["fit"] == {
                "seed": 7501, "role": 0, "switches": [24, 48], "steps": 72
            }
            and p["prior"]["reference_preregister"] ==
            "9b4eefddad364bc416511bba2a783401f1413b55"
            and tuple((w["seed"], w["role"], *w["switches"])
                      for w in p["data"]["held"]) == HELD
            and p["data"]["budget"]["held_actions_per_policy"] == 512
            and p["data"]["budget"]["return_only_actions_per_policy"] == 190
            and p["candidate"]["hazard"].startswith("1/16")
            and p["authority"].find("issue #426") >= 0,
            "FROZEN_PROTOCOL")
    return p


def validate_world(seed, role, first, second):
    require(type(seed) is int and type(role) is int and
            type(first) is int and type(second) is int and
            (seed, role, first, second) in HELD, "FROZEN_WORLD")


class PosteriorReadout:
    """Extra ONE scalar selector: original TGAP21 storage/updates untouched."""

    def __init__(self, memory, hazard=HAZARD):
        require(type(memory) is TwoSlotMemory and
                type(hazard) is float and 0 < hazard < 0.5,
                "SELECTOR_TYPE")
        self.memory = memory
        self.weight_slot1 = 0.5
        self.hazard = hazard

    def forecast(self, action):
        require(type(action) is int and action in (0, 1), "ACTION")
        a = self.memory.slot_prediction(0, action)
        b = self.memory.slot_prediction(1, action)
        return (1 - self.weight_slot1) * a + self.weight_slot1 * b

    def observe(self, step, action, outcome, *, source_mode=SOURCE_MODE):
        require(source_mode == SOURCE_MODE and
                type(outcome) is int and outcome in (0, 1), "SOURCE_OR_OUTCOME")
        # Strictly PRE-update likelihoods: no future observation in prediction.
        q0 = self.memory.slot_prediction(0, action)
        q1 = self.memory.slot_prediction(1, action)
        l0 = q0 if outcome else 1 - q0
        l1 = q1 if outcome else 1 - q1
        w = self.weight_slot1
        denominator = (1 - w) * l0 + w * l1
        require(math.isfinite(denominator) and denominator > 0,
                "POSTERIOR_LIKELIHOOD")
        posterior = w * l1 / denominator
        # Evolve selector only. Storage update remains the exact prior gate.
        self.memory.observe(step, action, outcome, source_mode=source_mode)
        self.weight_slot1 = self.hazard + (1 - 2 * self.hazard) * posterior
        require(math.isfinite(self.weight_slot1) and
                self.hazard <= self.weight_slot1 <= 1 - self.hazard,
                "POSTERIOR_BOUND")


def score_held(fitted, controls, seed, role, first, second):
    validate_world(seed, role, first, second)
    gate = fitted.new_public_world()
    candidate = PosteriorReadout(fitted.new_public_world())
    negative = PosteriorReadout(TwoSlotMemory())
    states = {
        "posterior_fit": candidate,
        "gate_fit": gate,
        "posterior_no_fit": negative,
        "stationary_fit": copy.deepcopy(controls["stationary"]),
        "rolling_8_fit": copy.deepcopy(controls["rolling_8"]),
        "reset_fit": copy.deepcopy(controls["reset"]),
        "bayes_hmm_fit": copy.deepcopy(controls["bayes_hmm"]),
        "source_only": Uninformed(),
    }
    losses = {p: {"all": [], "return": []} for p in POLICIES}
    readout_equal_steps = 0
    for step in range(64):
        action = step % 2
        # Only private evaluator accesses role/shift and exogenous coin.
        observed = witness(seed, role, step, action, first, second)
        for name, model in states.items():
            if name.startswith("posterior_"):
                forecast = model.forecast(action)
            else:
                forecast = model.predict(action)
            require(type(forecast) is float and
                    math.isfinite(forecast) and 0 <= forecast <= 1,
                    "FORECAST")
            loss = (forecast - observed) ** 2
            losses[name]["all"].append(loss)
            if step >= second:
                losses[name]["return"].append(loss)
            if name.startswith("posterior_"):
                model.observe(step, action, observed)
            elif name == "gate_fit":
                model.observe(step, action, observed)
            else:
                model.observe(action, observed)
        # This is the core storage-isolation control: EVERY step exact bytes.
        require(candidate.memory.checkpoint() == gate.checkpoint(),
                "STORAGE_DIVERGED")
        readout_equal_steps += 1
    for m in (candidate.memory, gate, negative.memory):
        raw = m.checkpoint()
        restored = TwoSlotMemory.restore(raw, digest(raw))
        require(restored.checkpoint() == raw, "COLD_RESTORE")
    return {
        "scores": {name: {part: sum(vals) for part, vals in v.items()}
                   for name, v in losses.items()},
        "all_actions": 64, "return_actions": 64 - second,
        "storage_equal_steps": readout_equal_steps,
        "max_memory_bytes": max(len(candidate.memory.checkpoint()),
                                len(gate.checkpoint()),
                                len(negative.memory.checkpoint())),
    }


def proof():
    t0 = time.monotonic()
    frozen_protocol()
    trained, ctrls, fit_logs, snapshots = fit_memory()
    require(len(fit_logs) == 72 and set(snapshots) == {23, 47, 71},
            "FIT_BUDGET")
    raw = trained.checkpoint()
    fitted = TwoSlotMemory.restore(raw, digest(raw))
    require(fitted.checkpoint() == raw, "FIT_COLD")
    before = [snapshots[23].slot_prediction(0, action) for action in (0, 1)]
    after = [snapshots[47].slot_prediction(0, action) for action in (0, 1)]
    held = [score_held(fitted, ctrls, *world) for world in HELD]
    require(sum(x["all_actions"] for x in held) == 512
            and sum(x["return_actions"] for x in held) == 190
            and sum(x["storage_equal_steps"] for x in held) == 512,
            "HELD_BUDGET")
    overall = {name: round(sum(w["scores"][name]["all"] for w in held) / 512, 8)
               for name in POLICIES}
    ret = {name: round(sum(w["scores"][name]["return"] for w in held) / 190, 8)
           for name in POLICIES}
    h1margin = round(overall["gate_fit"] - overall["posterior_fit"], 8)
    h2margin = round(ret["gate_fit"] - ret["posterior_fit"], 8)
    h3margin = round(overall["rolling_8_fit"] - overall["posterior_fit"], 8)
    predicates = {"H1_all_vs_gate": h1margin >= 0.01000,
                  "H2_return_vs_gate": h2margin >= 0.01000,
                  "H3_all_vs_rolling": h3margin >= 0}
    count = sum(predicates.values())
    return {
        "schema": SCHEMA, "prereg_commit": PREREG,
        "source_mode": SOURCE_MODE, "fit_actions": 72,
        "held_worlds": len(HELD), "held_actions_per_policy": 512,
        "return_actions_per_policy": 190,
        "held_brier": overall, "return_brier": ret,
        "margins": {"H1": h1margin, "H2": h2margin, "H3": h3margin},
        "frozen_predicates": predicates,
        "development_verdict": (
            "READOUT_SUPPORTED_DEV" if count == 3 else
            "MIXED_READOUT" if count > 0 else "READOUT_NO_GO"
        ),
        "trained_minus_no_fit_brier": round(
            overall["posterior_fit"] - overall["posterior_no_fit"], 8),
        "old_A_slot_changed_after_B": sum(x != y for x, y in zip(before, after)),
        "fit_checkpoint_sha256": digest(raw),
        "same_original_memory_after_every_update": True,
        "source_only_not_native": True,
        "scientific_gate": "NO_GO_SYNTHETIC_NO_OWNER_FIRST_USE",
        "accepted_main_or_checkpoint_changed": False,
        "deployment": "NONE",
        "max_held_memory_bytes": max(w["max_memory_bytes"] for w in held),
        "isolated_wall_seconds": round(time.monotonic() - t0, 6),
    }


if __name__ == "__main__":
    print(json.dumps(proof(), sort_keys=True, indent=2))
