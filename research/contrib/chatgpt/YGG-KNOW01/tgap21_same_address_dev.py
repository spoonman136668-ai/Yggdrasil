"""TGAP21: single-address A->B->A and FIT->HELD transfer falsification.

Source-only, noncanonical, tokenless numeric DEV. Frozen protocol committed
before source at 9b4eefddad364bc416511bba2a783401f1413b55. Original
Yggdrasil/Amalgam model, checkpoint, first-use and controller are untouched.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from pathlib import Path

from noisy_regime_memory_dev import (
    StationaryBeta, RollingBeta, ResetBeta, BayesianHMM
)

PREREG = "9b4eefddad364bc416511bba2a783401f1413b55"
SCHEMA = "yggdrasil.tgap21.numeric-two-slot-recurrence.dev.v1"
SOURCE_MODE = "engineering_fixture_only"
CAPACITY = 16384
FIT = (7501, 0, 24, 48, 72)
HELD = ((7601, 0, 16, 40), (7607, 0, 20, 44),
        (7613, 1, 16, 40), (7621, 1, 20, 44))


def require(ok, name):
    if not ok:
        raise ValueError("YGG_TGAP21_" + name)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def beta(pair):
    return (1 + pair[0]) / (2 + pair[1])


def witness(seed, role, step, action, first, second):
    """One actual synthetic reward per action. Private truth never an input."""
    require(type(seed) is int and type(role) is int and role in (0, 1)
            and type(step) is int and 0 <= step < 72
            and type(action) is int and action in (0, 1)
            and type(first) is int and type(second) is int
            and 0 < first < second < 72, "WITNESS_INPUT")
    best = role ^ int(first <= step < second)
    sample = hashlib.sha256(
        f"tgap21:private:witness:v1:{seed}:{role}:{step}".encode("ascii")
    ).digest()
    coin = int.from_bytes(sample[:8], "big") / (1 << 64)
    return int(coin < (0.8 if action == best else 0.2))


class TwoSlotMemory:
    """Preserved two-slot local numeric knowledge at ONE address.

    Counters are learned consequences, not text tokens or supplied law truth.
    Slots are never keyed by public scene or true hidden regime. Fresh held
    worlds reuse both FIT slots; reset only the observable episode cursor and
    recent anomaly control window.
    """

    def __init__(self):
        self.slots = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
        self.active = 0
        self.recent = []
        self.since_switch = 0
        self.next_step = 0
        self.total_witnesses = 0
        self.switches = 0

    def slot_prediction(self, slot, action):
        require(type(slot) is int and slot in (0, 1)
                and type(action) is int and action in (0, 1),
                "PREDICT_INPUT")
        return beta(self.slots[slot][action])

    def predict(self, action):
        return self.slot_prediction(self.active, action)

    def observe(self, step, action, outcome, *, source_mode=SOURCE_MODE):
        require(source_mode == SOURCE_MODE, "SOURCE_AUTHORITY")
        require(type(step) is int and step == self.next_step
                and type(action) is int and action in (0, 1)
                and type(outcome) is int and outcome in (0, 1),
                "REPLAY_OR_TYPE")
        p = self.predict(action)
        anomaly = int((p >= 0.65 and outcome == 0)
                      or (p <= 0.35 and outcome == 1))
        pair = self.slots[self.active][action]
        pair[0] += outcome
        pair[1] += 1
        self.next_step += 1
        self.total_witnesses += 1
        self.since_switch += 1
        self.recent = (self.recent + [anomaly])[-6:]
        if self.since_switch >= 8 and sum(self.recent) >= 3:
            self.active ^= 1
            self.switches += 1
            self.since_switch = 0
            self.recent = []

    def new_public_world(self):
        """No hidden information; carry previously fitted learned counts."""
        other = copy.deepcopy(self)
        other.active = 0
        other.recent = []
        other.since_switch = 0
        other.next_step = 0
        other.switches = 0
        return other

    def checkpoint(self):
        raw = canonical({
            "schema": SCHEMA, "mode": SOURCE_MODE,
            "accepted_native": False, "scientific_gain_verified": False,
            "slots": self.slots, "active": self.active,
            "recent": self.recent, "since_switch": self.since_switch,
            "next_step": self.next_step, "total_witnesses": self.total_witnesses,
            "switches": self.switches,
        })
        require(len(raw) <= CAPACITY, "CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha):
        require(type(raw) is bytes and 0 < len(raw) <= CAPACITY
                and type(expected_sha) is str
                and digest(raw) == expected_sha, "CHECKPOINT_DIGEST")
        def unique(pairs):
            doc = {}
            for k, v in pairs:
                require(k not in doc, "DUPLICATE_CHECKPOINT_KEY")
                doc[k] = v
            return doc
        try:
            obj = json.loads(raw, object_pairs_hook=unique)
            require(type(obj) is dict and set(obj) == {
                "schema", "mode", "accepted_native", "scientific_gain_verified",
                "slots", "active", "recent", "since_switch",
                "next_step", "total_witnesses", "switches"
            } and obj["schema"] == SCHEMA
                    and obj["mode"] == SOURCE_MODE
                    and obj["accepted_native"] is False
                    and obj["scientific_gain_verified"] is False
                    and canonical(obj) == raw, "CHECKPOINT_SCHEMA")
            s = cls()
            s.slots = obj["slots"]
            require(type(s.slots) is list and len(s.slots) == 2
                    and all(type(slot) is list and len(slot) == 2
                            and all(type(pair) is list and len(pair) == 2
                                    and all(type(n) is int and 0 <= n <= 128
                                            for n in pair)
                                    and pair[0] <= pair[1]
                                    for pair in slot)
                            for slot in s.slots), "CHECKPOINT_COUNTS")
            for attr in ("active", "since_switch", "next_step",
                         "total_witnesses", "switches"):
                require(type(obj[attr]) is int and obj[attr] >= 0,
                        "CHECKPOINT_TYPES")
                setattr(s, attr, obj[attr])
            require(s.active in (0, 1)
                    and s.next_step <= 72
                    and s.since_switch <= s.next_step
                    and s.switches <= s.next_step // 8
                    and s.total_witnesses ==
                    sum(pair[1] for slot in s.slots for pair in slot)
                    and s.total_witnesses >= s.next_step
                    and s.total_witnesses <= 256,
                    "CHECKPOINT_STEP_COUNT")
            s.recent = obj["recent"]
            require(type(s.recent) is list
                    and len(s.recent) <= min(6, s.since_switch)
                    and all(type(x) is int and x in (0, 1)
                            for x in s.recent), "CHECKPOINT_RECENT")
            require(s.checkpoint() == raw, "CHECKPOINT_ROUNDTRIP")
            return s
        except (TypeError, ValueError, KeyError, OverflowError) as e:
            raise ValueError("YGG_TGAP21_INVALID_CHECKPOINT") from e


class Uninformed:
    def predict(self, action):
        return 0.5
    def observe(self, action, observed):
        return None


def brier(p, y):
    return (p - y) ** 2


def fit_memory():
    model = TwoSlotMemory()
    conventional = {
        "stationary": StationaryBeta(),
        "rolling_8": RollingBeta(),
        "reset": ResetBeta(),
        "bayes_hmm": BayesianHMM(),
    }
    fit_logs = []
    snapshot = {}
    seed, role, first, second, duration = FIT
    for step in range(duration):
        action = step % 2
        outcome = witness(seed, role, step, action, first, second)
        model.observe(step, action, outcome)
        for ctrl in conventional.values():
            ctrl.observe(action, outcome)
        fit_logs.append((step, action, outcome))
        if step in (23, 47, 71):
            snapshot[step] = copy.deepcopy(model)
    return model, conventional, fit_logs, snapshot


def evaluate_held(fitted, controls, seed, role, first, second):
    states = {
        "two_slot_fit": fitted.new_public_world(),
        "two_slot_no_fit": TwoSlotMemory(),
        "stationary": copy.deepcopy(controls["stationary"]),
        "rolling_8": copy.deepcopy(controls["rolling_8"]),
        "reset": copy.deepcopy(controls["reset"]),
        "bayes_hmm": copy.deepcopy(controls["bayes_hmm"]),
        "source_only": Uninformed(),
    }
    measures = {name: {"all": [], "initial": [], "middle": [],
                       "return": []} for name in states}
    for step in range(64):
        action = step % 2
        outcome = witness(seed, role, step, action, first, second)
        phase = "initial" if step < first else (
            "middle" if step < second else "return")
        for name, state in states.items():
            forecast = state.predict(action)
            require(type(forecast) is float and 0 <= forecast <= 1,
                    "PROBABILITY_RANGE")
            measures[name]["all"].append(brier(forecast, outcome))
            measures[name][phase].append(brier(forecast, outcome))
            if name.startswith("two_slot"):
                state.observe(step, action, outcome)
            else:
                state.observe(action, outcome)
    return {name: {part: sum(vals) / len(vals) for part, vals in part_losses.items()}
            for name, part_losses in measures.items()}


def proof():
    start = time.monotonic()
    frozen = json.loads(
        Path(__file__).with_name("tgap21_protocol.json").read_text("utf-8"))
    require(frozen["schema"] ==
            "yggdrasil.tgap21.same-address-recurrence-transfer-dev.v1"
            and frozen["fit"]["seed"] == FIT[0]
            and len(frozen["held"]["worlds"]) == len(HELD)
            and [(w["seed"], w["role"], *w["switches"])
                 for w in frozen["held"]["worlds"]] == list(HELD),
            "FROZEN_PROTOCOL")
    trained, controls, fit_logs, snapshots = fit_memory()
    trained_ckpt = trained.checkpoint()
    cold = TwoSlotMemory.restore(trained_ckpt, digest(trained_ckpt))
    require(cold.checkpoint() == trained_ckpt, "COLD_RESTORE")
    a_before = [snapshots[23].slot_prediction(0, a) for a in (0, 1)]
    a_after_b = [snapshots[47].slot_prediction(0, a) for a in (0, 1)]
    a_after_return = [cold.slot_prediction(0, a) for a in (0, 1)]
    old_drift = sum(x != y for x, y in zip(a_before, a_after_b))
    held = [evaluate_held(cold, controls, *world) for world in HELD]
    names = tuple(held[0])
    score = {name: {
        phase: round(sum(d[name][phase] for d in held) / len(held), 8)
        for phase in ("all", "return")
    } for name in names}
    by_role = {str(role): {
        name: round(sum(held[i][name]["all"]
                        for i, w in enumerate(HELD) if w[1] == role) /
                    sum(w[1] == role for w in HELD), 8)
        for name in names
    } for role in (0, 1)}
    return {
        "schema": "yggdrasil.tgap21.synthetic-qualifier-result.v1",
        "prereg_sha": PREREG,
        "mode": SOURCE_MODE,
        "fit_witnessed_actions": len(fit_logs),
        "held_worlds": len(held),
        "held_witnesses_per_policy": 64 * len(held),
        "held_brier": score,
        "held_brier_by_hidden_role": by_role,
        "transfer_improvement_over_cold_brier": round(
            score["two_slot_no_fit"]["all"] -
            score["two_slot_fit"]["all"], 8),
        "A_slot_forecast_after_A": a_before,
        "A_slot_forecast_after_B": a_after_b,
        "A_slot_forecast_after_return": a_after_return,
        "A_drift_after_B_readouts": old_drift,
        "fit_checkpoint_bytes": len(trained_ckpt),
        "fit_checkpoint_sha256": digest(trained_ckpt),
        "cold_restore": True,
        "engineering_gate": "PASS",
        "scientific_gate": "DEV_NO_GO_SYNTHETIC_CONTROLS",
        "original_native_modified": False,
        "accepted_learner_modified": False,
        "protected_original_first_use": False,
        "deployment": "NONE",
        "wall_time_seconds_no_checkout": round(time.monotonic() - start, 6)
    }


if __name__ == "__main__":
    print("YGG_TGAP21_RESULT=" + json.dumps(proof(), sort_keys=True))
