"""Gate26: source-free causal-identifiability filter for known JEPA shadow experts.

Gate25 is deliberately preserved as a failed development experiment.
This alternative is a distinct, preregistered hard-disagreement test:
calibration preference on same-class outcomes is NOT causal-law evidence.
Not an accepted learner, controller, or original-source experiment.
"""
from __future__ import annotations

from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location(
    "gate26_preserved_gate25_sources",
    HERE / "public_consequence_retention_gate.py")
PRIOR = module_from_spec(SPEC)
SPEC.loader.exec_module(PRIOR)

SCHEMA = "yggdrasil.amalgam.identifiable-consequence-gate-dev.v1"
VOTES = 2
DISCRIMINATOR = 0.5


class IdentifiablePublicConsequenceGate(PRIOR.PublicConsequenceGate):
    """Read-only trained heads; bounded switch votes from class disagreement."""

    def __init__(self, old_expert, new_expert):
        super().__init__(old_expert, new_expert)
        self.discriminating = 0
        self.abstentions = 0

    def observe(self, identifier, views, y):
        event = PRIOR._source_event(identifier, views, y)
        if identifier in self._known:
            if self._known[identifier] != event:
                raise ValueError("GATE26_CONFLICTING_REPLAY")
            return False
        if len(self._events) >= PRIOR.MAX_EVENTS:
            raise ValueError("GATE26_MAX_EVENTS")

        old_p, new_p = self.pair_probabilities(views)
        old_class, new_class = int(old_p > DISCRIMINATOR), int(new_p > DISCRIMINATOR)
        if old_class == new_class:
            # Identical class forecast => NO causal evidence, regardless
            # of different calibration / relative Brier losses.
            self.abstentions += 1
        else:
            self.discriminating += 1
            challenger_class = new_class if self.active == "old" else old_class
            if y == challenger_class:
                self.votes += 1
            else:
                self.votes = 0
            if self.votes >= VOTES:
                self.active = "new" if self.active == "old" else "old"
                self.switches.append(len(self._events))
                self.votes = 0

        self._events.append(event)
        self._known[identifier] = event
        return True

    def custody(self):
        result = super().custody()
        result["schema"] = SCHEMA
        result["discriminating_events"] = self.discriminating
        result["abstaining_events"] = self.abstentions
        return result


def _fixture(laws=("or", "xor", "or"), corrupted=()):
    if type(corrupted) is not tuple or any(type(i) is not int for i in corrupted):
        raise ValueError("GATE26_CORRUPTION_INDICES")
    if any(i not in (31, 35) for i in corrupted) or len(set(corrupted)) != len(corrupted):
        raise ValueError("GATE26_CORRUPTION_SCOPE")
    events = []
    for i, (phase, identifier, views, y) in enumerate(PRIOR._tape(laws)):
        if i in corrupted:
            if PRIOR.PRIOR._public_pair(views) != (1, 1):
                raise ValueError("GATE26_CORRUPTION_PAIR")
            y = 1 - y
        events.append((phase, identifier, views, y))
    return tuple(events)


def _score_public(laws=("or", "xor", "or"), corrupted=()):
    old, new = PRIOR._fit_expert("or"), PRIOR._fit_expert("xor")
    old_snapshot, new_snapshot = PRIOR._snapshot(old), PRIOR._snapshot(new)
    gate = IdentifiablePublicConsequenceGate(old, new)
    values = {k: [] for k in ("gated", "static_old", "static_new",
                             "symbolic", "last_public_label")}
    phase_values = [{k: [] for k in values} for _ in range(3)]
    truths = []
    phase_truths = [[], [], []]
    score_before_update = True

    symbolic_law = "or"
    prior_label = {pair: int(pair[0] or pair[1]) for pair in PRIOR.PRIOR.PAIRS}
    historical_events = []
    for index, (phase, identifier, views, y) in enumerate(_fixture(laws, corrupted)):
        pair = PRIOR.PRIOR._public_pair(views)
        old_p, new_p = gate.pair_probabilities(views)
        score = {
            "gated": gate.predict(views),
            "static_old": old_p,
            "static_new": new_p,
            "symbolic": float(
                (pair[0] | pair[1]) if symbolic_law == "or"
                else (pair[0] ^ pair[1])),
            "last_public_label": float(prior_label[pair]),
        }
        for key, probability in score.items():
            values[key].append(probability)
            phase_values[phase][key].append(probability)
        truths.append(y)
        phase_truths[phase].append(y)

        # Only after all predictions are recorded, ingest the public
        # witnessed consequence. No fixture phase or ordinal is passed.
        gate.observe(identifier, views, y)
        historical_events.append((identifier, views, y))
        if score["symbolic"] != float(y):
            symbolic_law = "xor" if symbolic_law == "or" else "or"
        prior_label[pair] = y

    final = {
        "schema": SCHEMA,
        "laws_fixture_only": laws,
        "corrupted_indices_fixture_only": corrupted,
        "training_public_events_per_expert": 16,
        "evaluated_public_events": len(truths),
        "predictions_before_outcomes": score_before_update,
        "scores": {key: PRIOR._collect(ps, truths) for key, ps in values.items()},
        "phase_scores": [{
            key: PRIOR._collect(ps, phase_truths[i])
            for key, ps in phase_values[i].items()
        } for i in range(3)],
        "source_free_ledger_sha256": sha256(json.dumps(
            historical_events, separators=(",", ":"), sort_keys=True
        ).encode("ascii")).hexdigest(),
        "custody": gate.custody(),
        "old_model_weights_unchanged": old_snapshot == PRIOR._snapshot(old),
        "new_model_weights_unchanged": new_snapshot == PRIOR._snapshot(new),
        "canonical_checkpoint_mutations": 0,
        "original_source_actions": 0,
        "scientific_pass": False,
        "deployment": "NONE",
    }
    replay = IdentifiablePublicConsequenceGate(
        PRIOR._fit_expert("or"), PRIOR._fit_expert("xor"))
    for identifier, views, y in historical_events:
        replay.observe(identifier, views, y)
    final["cold_replay_exact"] = replay.custody() == gate.custody()
    return final


def audit():
    primary = _score_public()
    no_change = _score_public(("or", "or", "or"))
    one_noise = _score_public(("or", "or", "or"), (31,))
    two_noise = _score_public(("or", "or", "or"), (31, 35))
    return {
        "schema": SCHEMA,
        "primary": primary,
        "no_change_negative": no_change,
        "single_noise_negative": one_noise,
        "double_noise_identifiability_limit": two_noise,
        "gate25_unchanged": True,
        "owner_model_integrated": False,
        "scientific_pass": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2))
