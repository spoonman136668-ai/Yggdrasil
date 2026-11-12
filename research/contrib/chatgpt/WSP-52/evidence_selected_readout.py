"""WSP52 SELFTEST-only: learn whether to use a supplied order-invariant readout.

This is a bounded *model-selection* diagnostic, NOT grammar invention or a
registered WSP52 arm. It never inspects heldout source records or hidden codes.
Six leave-one-out validation folds use only the already observed six phase-B
consequences. The 246 additional model-writes are charged as replay compute,
not as new environment actions.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json

from source import Observation
from direct_writer import DirectWeightWriter, _canonical, _validate_state
from order_invariant_ablation import OrderInvariantReadout

A_COUNT = 36
B_COUNT = 6
REPLAY_WRITES = B_COUNT * (A_COUNT + B_COUNT - 1)
INVARIANT_MIN_ADVANTAGE = 2


def select_readout(validation):
    """Fail closed unless invariance wins >=2 validated disagreements and is error-free."""
    if len(validation) != B_COUNT:
        raise ValueError("incomplete six-example selection evidence")
    for pair in validation:
        if set(pair) != {"slot", "unordered"}:
            raise ValueError("unknown candidate outcome")
        if any(v not in ("correct", "wrong", "abstain") for v in pair.values()):
            raise ValueError("invalid validation status")
    evidence = {"slot": {"correct": 0, "wrong": 0, "abstain": 0},
                "unordered": {"correct": 0, "wrong": 0, "abstain": 0}}
    for pair in validation:
        for mode, outcome in pair.items():
            evidence[mode][outcome] += 1
    gain = sum(pair["unordered"] == "correct" and pair["slot"] != "correct"
               for pair in validation)
    loss = sum(pair["slot"] == "correct" and pair["unordered"] != "correct"
               for pair in validation)
    safe = evidence["unordered"]["wrong"] == 0
    choice = ("unordered" if safe and gain >= INVARIANT_MIN_ADVANTAGE and
              gain > loss else "slot")
    return choice, {"gain": gain, "loss": loss, "counts": evidence,
                    "validation_examples": len(validation)}


def _record(row):
    if type(row) is not Observation:
        raise ValueError("unexpected observation object")
    return {"before": list(row.before), "acoustic_bits": row.acoustic_bits,
            "after": list(row.after), "action_cost": row.action_cost,
            "reset_cost": row.reset_cost}


def _unrecord(entry):
    if type(entry) is not dict or set(entry) != {"before", "acoustic_bits", "after",
                                                 "action_cost", "reset_cost"}:
        raise ValueError("bad observation record")
    if type(entry["before"]) is not list or type(entry["after"]) is not list:
        raise ValueError("invalid physical state payload")
    return Observation(tuple(entry["before"]), entry["acoustic_bits"],
                       tuple(entry["after"]), entry["action_cost"], entry["reset_cost"])


class EvidenceSelectedReadout:
    """Single-source training; optional pre-registered-by-code readout selection.

    Only the already observed phase-A/phase-B records may influence selection.
    This deliberately retains source examples for fold replay: count the total
    serialized capacity, don't compare against memory-limited models as equal.
    """

    def __init__(self):
        self.writer = DirectWeightWriter()
        self.phase_a = []
        self.phase_b = []
        self.sealed = False
        self.finalized = False
        self.mode = "slot"
        self.selection = None
        self.replay_writes = 0
        self.selector_predictions = 0

    def observe(self, row):
        if self.finalized:
            raise ValueError("cannot update a finalized diagnostic")
        _record(row)  # strict learner-facing source shape
        if self.sealed:
            if len(self.phase_b) >= B_COUNT:
                raise ValueError("phase-B experience cap exceeded")
            self.phase_b.append(row)
        else:
            if len(self.phase_a) >= A_COUNT:
                raise ValueError("phase-A experience cap exceeded")
            self.phase_a.append(row)
        self.writer.observe(row)

    def seal_a(self):
        if self.sealed or len(self.phase_a) != A_COUNT:
            raise ValueError("requires exactly 36 phase-A source observations")
        self.sealed = True

    def finalize_b(self):
        if not self.sealed or self.finalized or len(self.phase_b) != B_COUNT:
            raise ValueError("requires exactly six phase-B observations")
        validation = []
        for holdout_idx, row in enumerate(self.phase_b):
            fold = DirectWeightWriter()
            for source in self.phase_a:
                fold.observe(source)
            for idx, source in enumerate(self.phase_b):
                if idx != holdout_idx:
                    fold.observe(source)
            slot = fold.predict(row.before, row.acoustic_bits)
            unordered = OrderInvariantReadout.predict(fold, row.before, row.acoustic_bits)
            def verdict(prediction):
                if prediction is None:
                    return "abstain"
                return "correct" if prediction == row.after else "wrong"
            validation.append({"slot": verdict(slot), "unordered": verdict(unordered)})
        self.mode, self.selection = select_readout(tuple(validation))
        self.replay_writes = REPLAY_WRITES
        self.selector_predictions = 2 * B_COUNT
        self.finalized = True

    def predict(self, before, acoustic_bits):
        _validate_state(before)
        if self.finalized and self.mode == "unordered":
            return OrderInvariantReadout.predict(self.writer, before, acoustic_bits)
        return self.writer.predict(before, acoustic_bits)

    @property
    def actions(self):
        return self.writer.actions

    def snapshot(self):
        payload = {"schema": "wsp52.evidence-selected-readout.selftest.v1",
                   "phase_a": [_record(x) for x in self.phase_a],
                   "phase_b": [_record(x) for x in self.phase_b],
                   "sealed": self.sealed, "finalized": self.finalized,
                   "mode": self.mode, "selection": self.selection,
                   "writer": self.writer.snapshot(),
                   "replay_writes": self.replay_writes,
                   "selector_predictions": self.selector_predictions}
        return _canonical({"payload": payload,
                           "sha256": sha256(_canonical(payload).encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls, blob):
        if type(blob) is not str:
            raise ValueError("invalid snapshot data")
        try:
            data = json.loads(blob)
            if type(data) is not dict or set(data) != {"payload", "sha256"}:
                raise ValueError("bad envelope")
            payload = data["payload"]
            if type(payload) is not dict or set(payload) != {
                "schema", "phase_a", "phase_b", "sealed", "finalized", "mode",
                "selection", "writer", "replay_writes", "selector_predictions"}:
                raise ValueError("unknown schema fields")
            if payload["schema"] != "wsp52.evidence-selected-readout.selftest.v1":
                raise ValueError("unknown model schema")
            if sha256(_canonical(payload).encode("ascii")).hexdigest() != data["sha256"]:
                raise ValueError("tampered payload")
            if type(payload["sealed"]) is not bool or type(payload["finalized"]) is not bool:
                raise ValueError("invalid phase flags")
            obj = cls()
            for item in payload["phase_a"]:
                obj.observe(_unrecord(item))
            if payload["sealed"]:
                obj.seal_a()
            if payload["phase_b"] and not obj.sealed:
                raise ValueError("phase-B observations before seal")
            for item in payload["phase_b"]:
                obj.observe(_unrecord(item))
            if payload["finalized"]:
                obj.finalize_b()
            if obj.snapshot() != blob:
                raise ValueError("noncanonical or inconsistent model state")
            return obj
        except (TypeError, KeyError, ValueError, IndexError,
                UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid or tampered model snapshot") from exc

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii")) * 8


def run_selftest_selection(world):
    """Constrained fixture results, never registered DEV/PRIMARY science."""
    from fixture_harness import learn_observations, score_observations
    if world.cohort != "SELFTEST":
        raise PermissionError("registered science cohorts are not fixture evidence")
    obj = EvidenceSelectedReadout()
    learn_observations(obj, world.phase_a)
    phase_a = asdict(score_observations(obj, world.heldout_a))
    obj.seal_a()
    learn_observations(obj, world.phase_b)
    obj.finalize_b()
    phase_b = asdict(score_observations(obj, world.heldout_b))
    retained = asdict(score_observations(obj, world.heldout_a))
    restored = EvidenceSelectedReadout.restore(obj.snapshot())
    if score_observations(restored, world.heldout_a) != score_observations(obj, world.heldout_a):
        raise AssertionError("cold-retention mismatch")
    if score_observations(restored, world.heldout_b) != score_observations(obj, world.heldout_b):
        raise AssertionError("cold-transfer mismatch")
    return {"arm": "post-hoc-fixture-evidence-selected-readout",
            "phase_a": phase_a, "phase_b": phase_b, "retained_a": retained,
            "selected": obj.mode, "selector": obj.selection,
            "unique_environment_actions": obj.actions, "replay_writes": obj.replay_writes,
            "selector_predictions": obj.selector_predictions, "gradient_steps": 0,
            "total_persistent_bits": obj.capacity_bits(),
            "cold_restore_parity": True}
