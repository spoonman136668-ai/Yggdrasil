"""KNOW23 — frozen single-witness quarantine-before-write causal memory DEV.

Research-only numeric learner, not canonical Yggdrasil native intelligence.
Protocol was committed BEFORE implementation at
5d2eb5d552d6fa5c202f422798d1b4e0f7dfcecf.
All unknown roles/switches/noise are private evaluator data, NEVER model inputs.
"""
from __future__ import annotations

import copy
import json
import math
import time
from pathlib import Path

from tgap21_same_address_dev import (
    TwoSlotMemory, witness, beta, canonical, digest,
)
from noisy_regime_memory_dev import (
    StationaryBeta, RollingBeta, ResetBeta, BayesianHMM, PassiveZero,
)

SCHEMA = "yggdrasil.know23.write-quarantine-synthetic-result.v1"
MEM_SCHEMA = "yggdrasil.know23.quarantined-write-two-slot.dev.v1"
READER_SCHEMA = "yggdrasil.know23.posterior-reader.dev.v1"
PROTOCOL_SCHEMA = "yggdrasil.know23.quarantined-write-custody-frozen-dev.v1"
PREREG = "5d2eb5d552d6fa5c202f422798d1b4e0f7dfcecf"
SOURCE_MODE = "engineering_fixture_only"
FIT = (9151, 0, 22, 47, 72)
HELD = (
    (9173, 0, 13, 38), (9199, 1, 13, 38),
    (9221, 0, 19, 41), (9241, 1, 19, 41),
    (9263, 0, 9, 32), (9281, 1, 9, 32),
    (9311, 0, 25, 49), (9337, 1, 25, 49),
)
POLICIES = (
    "quarantine_fit", "original_fit", "quarantine_no_fit",
    "original_no_fit", "rolling_fit", "stationary_fit", "reset_fit",
    "bayes_hmm_fit", "source_only",
)
HAZARD = 1 / 16


def require(ok, tag):
    if not ok:
        raise ValueError("YGG_KNOW23_" + tag)


def protocol():
    data = json.loads(Path(__file__).with_name(
        "know23_protocol.json").read_text(encoding="utf-8"))
    require(data["schema"] == PROTOCOL_SCHEMA and
            data["fit"] == {"seed": FIT[0], "role": FIT[1],
                            "shifts": list(FIT[2:4]), "steps": FIT[4],
                            "action": "t%2", "snapshots":
                            data["fit"]["snapshots"]} and
            [(d["seed"], d["role"], *d["shifts"])
             for d in data["held"]] == list(HELD) and
            data["budget"]["fit_witnesses"] == 72 and
            data["budget"]["held_events_per_policy"] == 512 and
            data["budget"]["return_events_per_policy"] == 192 and
            data["algorithm"]["readout"].startswith("Use identical") and
            data["source"]["mode"] == SOURCE_MODE and
            data["frozen_predicates"]["H1"].endswith("- 0.01000"),
            "PREREG_DRIFT")
    return data


def validate_world(world):
    require(type(world) is tuple and len(world) == 4
            and all(type(x) is int for x in world)
            and world in HELD, "FROZEN_WORLD")


def _valid_pair(pair):
    return (type(pair) is list and len(pair) == 2 and
            all(type(x) is int and 0 <= x <= 136 for x in pair) and
            pair[0] <= pair[1])


class QuarantineWriteMemory:
    """Two persistent action-conditional Beta slots; bounded public event buffer."""

    def __init__(self):
        self.slots = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
        self.active = 0
        self.recent = []
        self.pending = []
        self.since_switch = 0
        self.next_step = 0
        self.total_witnesses = 0
        self.switches = 0
        self.replayed_internal = 0

    def slot_prediction(self, slot, action):
        require(type(slot) is int and slot in (0, 1) and
                type(action) is int and action in (0, 1), "PREDICT")
        return beta(self.slots[slot][action])

    def predict(self, action):
        return self.slot_prediction(self.active, action)

    def _commit(self, action, outcome, slot=None):
        if slot is None:
            slot = self.active
        count = self.slots[slot][action]
        count[0] += outcome
        count[1] += 1

    def observe(self, step, action, outcome, *, source_mode=SOURCE_MODE):
        require(source_mode == SOURCE_MODE, "SOURCE")
        require(type(step) is int and step == self.next_step and
                0 <= step < 72 and type(action) is int and
                action in (0, 1) and type(outcome) is int and
                outcome in (0, 1), "WITNESS_OR_REPLAY")
        p = self.predict(action)
        anomaly = int((p >= .65 and outcome == 0) or
                      (p <= .35 and outcome == 1))
        mature = all(pair[1] >= 4 for pair in self.slots[self.active])
        self.next_step += 1
        self.total_witnesses += 1
        self.since_switch += 1
        self.recent = (self.recent + [anomaly])[-6:]
        if not mature:
            self._commit(action, outcome)
            return
        self.pending.append([action, outcome])
        require(len(self.pending) <= 6, "BUFFER_BOUNDS")
        if self.since_switch >= 8 and sum(self.recent) >= 3:
            self.active ^= 1
            self.switches += 1
            for a, value in self.pending:
                self._commit(a, value)
                self.replayed_internal += 1
            self.pending = []
            self.recent = []
            self.since_switch = 0
        elif len(self.pending) == 6:
            a, value = self.pending.pop(0)
            self._commit(a, value)
        require(self._counted_events() == self.total_witnesses, "ACCOUNTING")

    def _counted_events(self):
        return sum(pair[1] for slot in self.slots for pair in slot) + len(self.pending)

    def finish_episode(self):
        """Commit only ALREADY observed delayed events; no private phase or new data."""
        while self.pending:
            action, outcome = self.pending.pop(0)
            self._commit(action, outcome)
        require(self._counted_events() == self.total_witnesses,
                "END_CUSTODY")

    def new_public_world(self):
        require(not self.pending, "UNFLUSHED_WORLD")
        clone = copy.deepcopy(self)
        clone.active = 0
        clone.recent = []
        clone.since_switch = 0
        clone.next_step = 0
        clone.switches = 0
        return clone

    def checkpoint(self):
        raw = canonical({
            "schema": MEM_SCHEMA, "source_mode": SOURCE_MODE,
            "accepted_native": False, "scientific_gain_verified": False,
            "slots": self.slots, "active": self.active,
            "recent": self.recent, "pending": self.pending,
            "since_switch": self.since_switch,
            "next_step": self.next_step,
            "total_witnesses": self.total_witnesses,
            "switches": self.switches,
            "replayed_internal": self.replayed_internal,
        })
        require(len(raw) <= 16384, "CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw, sha):
        require(type(raw) is bytes and type(sha) is str and
                len(raw) <= 16384 and digest(raw) == sha,
                "CHECKPOINT_DIGEST")
        def reject_duplicates(pairs):
            d = {}
            for key, value in pairs:
                require(key not in d, "DUPLICATE_KEY")
                d[key] = value
            return d
        try:
            obj = json.loads(raw.decode("ascii"),
                             object_pairs_hook=reject_duplicates)
            blank = cls()
            expected = set(json.loads(blank.checkpoint()))
            require(type(obj) is dict and set(obj) == expected and
                    obj["schema"] == MEM_SCHEMA and
                    obj["source_mode"] == SOURCE_MODE and
                    obj["accepted_native"] is False and
                    obj["scientific_gain_verified"] is False and
                    canonical(obj) == raw, "CHECKPOINT_CONTRACT")
            require(type(obj["active"]) is int and obj["active"] in (0, 1) and
                    type(obj["slots"]) is list and len(obj["slots"]) == 2 and
                    all(type(s) is list and len(s) == 2 and
                        all(_valid_pair(pair) for pair in s)
                        for s in obj["slots"]), "SLOT_TYPES")
            require(type(obj["pending"]) is list and
                    len(obj["pending"]) <= 6 and
                    all(type(pair) is list and len(pair) == 2 and
                        all(type(n) is int and n in (0, 1) for n in pair)
                        for pair in obj["pending"]), "PENDING_TYPES")
            require(type(obj["recent"]) is list and
                    len(obj["recent"]) <= 6 and
                    all(type(n) is int and n in (0, 1)
                        for n in obj["recent"]), "ANOMALIES")
            require(all(type(obj[k]) is int and
                        0 <= obj[k] <= 136 for k in (
                            "next_step", "total_witnesses", "since_switch",
                            "switches", "replayed_internal")), "COUNTERS")
            require(obj["next_step"] <= 72 and
                    obj["next_step"] <= obj["total_witnesses"] and
                    obj["since_switch"] <= obj["next_step"] and
                    obj["switches"] <= obj["total_witnesses"] // 8 and
                    sum(p[1] for s in obj["slots"] for p in s) +
                    len(obj["pending"]) == obj["total_witnesses"],
                    "SOURCE_ACCOUNTING")
            for k in ("slots", "active", "recent", "pending",
                      "since_switch", "next_step", "total_witnesses",
                      "switches", "replayed_internal"):
                setattr(blank, k, obj[k])
            require(blank.checkpoint() == raw, "CHECKPOINT_REPLAY")
            return blank
        except (ValueError, TypeError, KeyError, AttributeError,
                UnicodeError) as exc:
            raise ValueError("YGG_KNOW23_CHECKPOINT_REJECTED") from exc


class CommonPosteriorReader:
    """Exactly the KNOW22 pre-update two-slot mixture for both storage designs."""

    def __init__(self, memory):
        require(type(memory) in (TwoSlotMemory, QuarantineWriteMemory),
                "READER_TYPE")
        self.memory = memory
        self.weight_slot1 = .5

    def forecast(self, action):
        require(type(action) is int and action in (0, 1), "ACTION")
        return ((1 - self.weight_slot1) *
                self.memory.slot_prediction(0, action) +
                self.weight_slot1 * self.memory.slot_prediction(1, action))

    def observe(self, step, action, outcome, *, source_mode=SOURCE_MODE):
        require(source_mode == SOURCE_MODE and
                type(outcome) is int and outcome in (0, 1), "READER_SOURCE")
        q0 = self.memory.slot_prediction(0, action)
        q1 = self.memory.slot_prediction(1, action)
        l0 = q0 if outcome else 1 - q0
        l1 = q1 if outcome else 1 - q1
        p = self.weight_slot1
        denom = (1 - p) * l0 + p * l1
        require(math.isfinite(denom) and denom > 0, "LIKELIHOOD")
        posterior = p * l1 / denom
        self.memory.observe(step, action, outcome, source_mode=source_mode)
        self.weight_slot1 = HAZARD + (1 - 2 * HAZARD) * posterior
        require(HAZARD <= self.weight_slot1 <= 1 - HAZARD, "POSTERIOR_BOUNDS")


def fit_all():
    policy = protocol()
    original = TwoSlotMemory()
    quarantine = QuarantineWriteMemory()
    controls = {
        "rolling_fit": RollingBeta(),
        "stationary_fit": StationaryBeta(),
        "reset_fit": ResetBeta(),
        "bayes_hmm_fit": BayesianHMM(),
    }
    a_snapshot = None
    b_snapshot = None
    tape = []
    seed, role, first, second, length = FIT
    for t in range(length):
        action = t % 2
        y = witness(seed, role, t, action, first, second)
        tape.append([t, action, y])
        original.observe(t, action, y)
        quarantine.observe(t, action, y)
        for m in controls.values():
            m.observe(action, y)
        if t in (first - 1, second - 1):
            row = {
                name: [memory.slot_prediction(0, a) for a in (0, 1)]
                for name, memory in (("quarantine", quarantine),
                                     ("original", original))
            }
            if t == first - 1:
                a_snapshot = row
            else:
                b_snapshot = row
    quarantine.finish_episode()
    raw = quarantine.checkpoint()
    restored = QuarantineWriteMemory.restore(raw, digest(raw))
    require(raw == restored.checkpoint() and
            all(restored.slot_prediction(s, a) ==
                quarantine.slot_prediction(s, a)
                for s in (0, 1) for a in (0, 1)),
            "FIT_COLD")
    original_raw = original.checkpoint()
    require(TwoSlotMemory.restore(
        original_raw, digest(original_raw)).checkpoint() == original_raw,
        "ORIGINAL_COLD")
    return {
        "original": original, "quarantine": restored, "controls": controls,
        "A": a_snapshot, "B": b_snapshot, "fit_tape": tape,
        "original_bytes": len(original_raw), "quarantine_bytes": len(raw),
        "replayed": restored.replayed_internal,
    }


def evaluate_one(bundle, world):
    validate_world(world)
    seed, role, first, second = world
    states = {
        "quarantine_fit": CommonPosteriorReader(
            bundle["quarantine"].new_public_world()),
        "original_fit": CommonPosteriorReader(
            bundle["original"].new_public_world()),
        "quarantine_no_fit": CommonPosteriorReader(QuarantineWriteMemory()),
        "original_no_fit": CommonPosteriorReader(TwoSlotMemory()),
        **{name: copy.deepcopy(model)
           for name, model in bundle["controls"].items()},
        "source_only": PassiveZero(),
    }
    require(set(states) == set(POLICIES), "POLICY_IDS")
    losses = {name: {"all": [], "return": []} for name in POLICIES}
    max_candidate_bytes = 0
    for t in range(64):
        action = t % 2
        y = witness(seed, role, t, action, first, second)
        for name, policy in states.items():
            if type(policy) is CommonPosteriorReader:
                q = policy.forecast(action)
            else:
                q = policy.predict(action)
            require(type(q) is float and math.isfinite(q) and 0 <= q <= 1,
                    "PREDICTION")
            loss = (q - y)**2
            losses[name]["all"].append(loss)
            if t >= second:
                losses[name]["return"].append(loss)
            if type(policy) is CommonPosteriorReader:
                policy.observe(t, action, y)
                if type(policy.memory) is QuarantineWriteMemory:
                    max_candidate_bytes = max(
                        max_candidate_bytes, len(policy.memory.checkpoint()))
            else:
                policy.observe(action, y)
    for name in ("quarantine_fit", "quarantine_no_fit"):
        state = states[name].memory
        raw = state.checkpoint()
        require(QuarantineWriteMemory.restore(raw,digest(raw)).checkpoint() ==
                raw, "HELD_COLD")
        state.finish_episode()
    for name in ("original_fit", "original_no_fit"):
        state = states[name].memory
        raw = state.checkpoint()
        require(TwoSlotMemory.restore(raw, digest(raw)).checkpoint() == raw,
                "ORIGINAL_HELD_COLD")
    return {
        "loss_sums": {
            name: {phase: sum(terms) for phase, terms in per.items()}
            for name, per in losses.items()},
        "actions": 64, "return_actions": 64 - second,
        "max_candidate_bytes": max_candidate_bytes,
        "fit_protected_slot": states["quarantine_fit"].memory.slots[0],
        "fit_replayed": states["quarantine_fit"].memory.replayed_internal,
        "original_fit_slot": states["original_fit"].memory.slots[0],
    }


def proof():
    started = time.monotonic()
    bundle = fit_all()
    worlds = [evaluate_one(bundle, world) for world in HELD]
    require(sum(w["actions"] for w in worlds) == 512
            and sum(w["return_actions"] for w in worlds) == 192,
            "FROZEN_ACTION_BUDGET")
    overall = {
        name: round(sum(w["loss_sums"][name]["all"]
                        for w in worlds) / 512, 8)
        for name in POLICIES
    }
    returning = {
        name: round(sum(w["loss_sums"][name]["return"]
                        for w in worlds) / 192, 8)
        for name in POLICIES
    }
    old_drift = {
        name: sum(bundle["A"][name][a] != bundle["B"][name][a]
                  for a in (0,1))
        for name in ("quarantine", "original")
    }
    predicates = {
        "H1_overall_vs_original": overall["original_fit"] -
            overall["quarantine_fit"] >= .01000,
        "H2_return_vs_original": returning["original_fit"] -
            returning["quarantine_fit"] >= .01000,
        "H3_A_drift_reduced": old_drift["quarantine"] < old_drift["original"],
        "H4_vs_rolling": overall["quarantine_fit"] <=
            overall["rolling_fit"],
    }
    successes = sum(predicates.values())
    return {
        "schema": SCHEMA, "prereg_commit": PREREG,
        "source_mode": SOURCE_MODE,
        "fit_actions": len(bundle["fit_tape"]),
        "held_worlds": len(worlds), "held_actions_per_policy": 512,
        "return_actions_per_policy": 192,
        "held_brier": overall, "return_brier": returning,
        "A_slot_readouts_after_A": bundle["A"],
        "A_slot_readouts_after_B": bundle["B"],
        "A_slot_readouts_drifted": old_drift,
        "frozen_predicates": predicates,
        "development_verdict": (
            "PROTECTION_SUPPORTED_DEV" if successes == 4 else
            "MIXED_PROTECTION" if successes else "PROTECTION_NO_GO"
        ),
        "transfer_gain_vs_no_fit": {
            name: round(overall[name+"_no_fit"] -
                        overall[name+"_fit"], 8)
            for name in ("quarantine", "original")
        },
        "replayed_fit_internal_events": bundle["replayed"],
        "fit_quarantine_checkpoint_bytes": bundle["quarantine_bytes"],
        "fit_original_checkpoint_bytes": bundle["original_bytes"],
        "max_held_quarantine_checkpoint_bytes": max(
            w["max_candidate_bytes"] for w in worlds),
        "highest_classic_control": min(
            overall[name] for name in (
                "rolling_fit", "stationary_fit", "reset_fit", "bayes_hmm_fit")),
        "fit_source_tape_sha256": digest(canonical(bundle["fit_tape"])),
        "engineering_gate": "PASS",
        "scientific_gate": "NO_GO_SYNTHETIC_SOURCE_AND_STRONGEST_CONTROL",
        "original_native_modified": False,
        "accepted_model_or_checkpoint_changed": False,
        "protected_original_first_use": False,
        "deployment": "NONE",
        "isolated_wall_seconds_excluding_checkout": round(
            time.monotonic() - started, 6),
    }


if __name__ == "__main__":
    print(json.dumps(proof(), sort_keys=True, indent=2))
