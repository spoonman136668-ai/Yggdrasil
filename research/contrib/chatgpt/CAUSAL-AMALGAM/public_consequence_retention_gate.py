"""Gate25: isolated public-consequence, evidence-gated old/new readout replay.

This module neither changes nor runs Yggdrasil's canonical learner, source actor,
trainer, accepted checkpoint, or native planner. The two candidates are separately
fitted on *exposed synthetic* Gate24 data. Retention is scored on an A/B/A tape.
"""
from __future__ import annotations

from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist

HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("gate25_existing_gate24_module",
                               HERE / "symmetric_pair_residual.py")
PRIOR = module_from_spec(SPEC)
SPEC.loader.exec_module(PRIOR)

MARGIN = 0.05
VOTES = 2
MAX_EVENTS = 64
EXTRAS = (0, 0, 0)
SCHEMA = "yggdrasil.amalgam.public-consequence-retention-gate-dev.v1"


def _event_id(ordinal):
    return sha256(f"gate25-event/{ordinal}".encode("ascii")).hexdigest()


def _source_event(identifier, views, y):
    if (type(identifier) is not str or len(identifier) != 64
            or any(c not in "0123456789abcdef" for c in identifier)):
        raise ValueError("GATE25_EVENT_ID")
    PRIOR._public_pair(views)
    if type(y) is not int or y not in (0, 1):
        raise ValueError("GATE25_PUBLIC_OUTCOME")
    return (identifier, views, y)


def _fit_expert(law):
    head = ActionLatentSpecialist("reward")
    observed = PRIOR.rows(law, 0)
    for _, views, y in observed:
        head.observe(views, EXTRAS, y)
    adapter = PRIOR.SymmetricPairResidual().fit(observed)
    return head, adapter


def _expert_forecast(expert, views):
    head, adapter = expert
    return adapter.probability(head.probability(views, *EXTRAS),
                               views, enabled=True)


def _snapshot(expert):
    head, adapter = expert
    return json.dumps({"head": head.as_data(), "adapter": adapter.weights},
                      sort_keys=True, separators=(",", ":"))


class PublicConsequenceGate:
    """Source-blind, deterministic, bounded gate with two stored experts."""

    def __init__(self, old_expert, new_expert):
        self.old_expert = old_expert
        self.new_expert = new_expert
        self.active = "old"
        self.votes = 0
        self.switches = []
        self._events = []
        self._known = {}

    def pair_probabilities(self, views):
        PRIOR._public_pair(views)
        return (_expert_forecast(self.old_expert, views),
                _expert_forecast(self.new_expert, views))

    def predict(self, views):
        old_p, new_p = self.pair_probabilities(views)
        return old_p if self.active == "old" else new_p

    def observe(self, identifier, views, y):
        event = _source_event(identifier, views, y)
        if identifier in self._known:
            if self._known[identifier] != event:
                raise ValueError("GATE25_CONFLICTING_REPLAY")
            return False
        if len(self._events) >= MAX_EVENTS:
            raise ValueError("GATE25_MAX_EVENTS")
        # Prediction must happen before this method in the evaluator;
        # only public just-witnessed outcome y enters the update.
        old_p, new_p = self.pair_probabilities(views)
        incumbent = old_p if self.active == "old" else new_p
        challenger = new_p if self.active == "old" else old_p
        delta = (incumbent - y)**2 - (challenger - y)**2
        if delta > MARGIN:
            self.votes += 1
        elif delta < -MARGIN:
            self.votes = 0
        if self.votes >= VOTES:
            self.active = "new" if self.active == "old" else "old"
            self.switches.append(len(self._events))
            self.votes = 0
        self._events.append(event)
        self._known[identifier] = event
        return True

    def ledger(self):
        return tuple(self._events)

    def custody(self):
        return {
            "schema": SCHEMA,
            "active": self.active,
            "pending_votes": self.votes,
            "switch_after_zero_based_event_indices": tuple(self.switches),
            "observed_event_count": len(self._events),
            "public_ledger_sha256": sha256(json.dumps(
                self._events, sort_keys=True, separators=(",", ":")
            ).encode("ascii")).hexdigest(),
        }


def _tape(laws=("or", "xor", "or"), *, lone_bad_at=None):
    if type(laws) is not tuple or len(laws) != 3 or any(
            law not in ("or", "xor") for law in laws):
        raise ValueError("GATE25_LAWS")
    items, ordinal = [], 0
    for phase, (law, cycles) in enumerate(zip(laws, (4, 8, 4), strict=True)):
        for _ in range(cycles):
            for a, b in PRIOR.PAIRS:
                y = (a ^ b) if law == "xor" else (a | b)
                if ordinal == lone_bad_at:
                    if (a, b) != (1, 1):
                        raise ValueError("GATE25_BAD_OUTCOME_POSITION")
                    y ^= 1
                items.append((phase, _event_id(ordinal),
                              ((1, a), (1, b)), y))
                ordinal += 1
    return tuple(items)


def _collect(probs, truths):
    return {
        "correct": sum(int(p > 0.5) == y for p, y in zip(probs, truths)),
        "brier": sum((p - y)**2 for p, y in zip(probs, truths)) / len(truths)
    }


def _test_run(laws=("or", "xor", "or"), *, lone_bad_at=None):
    old, new = _fit_expert("or"), _fit_expert("xor")
    old_weights_before, new_weights_before = _snapshot(old), _snapshot(new)
    gate = PublicConsequenceGate(old, new)
    tape = _tape(laws, lone_bad_at=lone_bad_at)
    counts = {pair: int(pair[0] or pair[1]) for pair in PRIOR.PAIRS}
    symbolic = "or"
    preds = {k: [] for k in ("gated", "static_old", "static_new",
                              "symbolic", "last_public_label")}
    truths = []
    phase_preds = {phase: {k: [] for k in preds} for phase in range(3)}
    phase_truths = {0: [], 1: [], 2: []}
    phase_snapshots = []
    for index, (phase, identifier, views, y) in enumerate(tape):
        a, b = PRIOR._public_pair(views)
        old_p, new_p = gate.pair_probabilities(views)
        values = {
            "gated": gate.predict(views),
            "static_old": old_p,
            "static_new": new_p,
            "symbolic": float((a | b) if symbolic == "or" else (a ^ b)),
            "last_public_label": float(counts[(a, b)]),
        }
        # Strict PRE-OUTCOME score, then current y becomes public.
        for key, p in values.items():
            preds[key].append(p)
            phase_preds[phase][key].append(p)
        truths.append(y)
        phase_truths[phase].append(y)
        gate.observe(identifier, views, y)
        if values["symbolic"] != float(y):
            symbolic = "xor" if symbolic == "or" else "or"
        counts[(a, b)] = y
        if index in (15, 47, 63):
            phase_snapshots.append(gate.custody())
    all_scores = {k: _collect(v, truths) for k, v in preds.items()}
    phase_scores = [
        {k: _collect(v, phase_truths[p]) for k, v in phase_preds[p].items()}
        for p in range(3)
    ]
    replay = PublicConsequenceGate(_fit_expert("or"), _fit_expert("xor"))
    for _, identifier, views, y in tape:
        replay.observe(identifier, views, y)
    return {
        "schema": SCHEMA,
        "laws_fixture_only": laws,
        "predictions_before_outcomes": True,
        "train_rows_per_expert": 16,
        "test_events": len(tape),
        "scores": all_scores,
        "phase_scores": phase_scores,
        "old_weights_unchanged": _snapshot(old) == old_weights_before,
        "new_weights_unchanged": _snapshot(new) == new_weights_before,
        "replay_equal": replay.custody() == gate.custody(),
        "custody": gate.custody(),
        "phase_custody": phase_snapshots,
        "original_world_source_actions": 0,
        "canonical_checkpoint_updates": 0,
        "scientific_pass": False,
        "deployment": "NONE",
    }


def audit():
    primary = _test_run()
    negative = _test_run(("or", "or", "or"))
    one_outlier = _test_run(("or", "or", "or"), lone_bad_at=31)
    return {
        "schema": SCHEMA,
        "primary": primary,
        "no_change_negative": negative,
        "single_contradiction_negative": one_outlier,
        "owner_model_integrated": False,
        "scientific_pass": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
