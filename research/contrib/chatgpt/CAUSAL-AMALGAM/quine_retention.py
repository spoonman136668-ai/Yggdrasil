"""Research-only Quine retention veto for the existing immutable Amalgam learner.

This module does not run a source, train an additional learner, or authorize
policy influence. It checks each *proposed* shared witness update before its
candidate can replace the currently active research readout.
"""
from fractions import Fraction

from yggdrasil.native_context_basis import canonical, digest

SCHEMA = "yggdrasil.amalgam.quine-retention.v1"
SCALE = 1_000_000
TOLERANCE = Fraction(1, 50)


def _system(value):
    return value.system if hasattr(value, "system") else value


def _ledger(value):
    return _system(value).native._episode_reader()._ledger


def _checkpoint(value):
    return _system(value).checkpoint()


def _loss(value, event):
    """Two quantized Brier numerators for one witnessed transition and reward."""
    _, views, first, state, second, reward = event
    if type(state) is not int or state not in (0, 1) or type(reward) is not int or reward not in (0, 1):
        raise ValueError("Quine witness has nonbinary labels")
    forecast = _system(value).native.experience_context_forecast
    transition = forecast(views[0], first)
    terminal = forecast(views[0], first, state, second)
    if not (0 <= transition <= 1 and 0 <= terminal <= 1):
        raise ValueError("Quine prediction outside unit interval")
    return ((round(SCALE * transition) - SCALE * state) ** 2,
            (round(SCALE * terminal) - SCALE * reward) ** 2)


def select_quines(anchor, regime_windows, *, count=8):
    """Select 5-10 high-loss charged witnesses per externally qualified regime.

    Scores are computed from the pinned, already-trained anchor. They are
    retrospective anchor-surprise, NOT prequential loss or independent mastery
    evidence. Regime windows must be provenance-certified by the experiment.
    A binary terminal reward is a signed proxy (+1/-1), NOT a measured cost.
    """
    events = _ledger(anchor)
    if type(regime_windows) is not dict or not regime_windows:
        raise ValueError("Explicit qualified regime windows required")
    if type(count) is not int or not 5 <= count <= 10:
        raise ValueError("Quine count must be between five and ten")
    occupied = set()
    groups = {}
    for regime, bounds in sorted(regime_windows.items()):
        if type(regime) is not str or not regime or type(bounds) not in (tuple, list) or len(bounds) != 2:
            raise ValueError("Invalid qualified regime address")
        start, stop = bounds
        if not (type(start) is int and type(stop) is int and
                0 <= start < stop <= len(events) and stop - start >= count):
            raise ValueError("Qualified regime window cannot supply the Quines")
        indices = set(range(start, stop))
        if occupied & indices:
            raise ValueError("Overlapping mastered regime windows")
        occupied.update(indices)
        ranked = []
        for index in range(start, stop):
            event = events[index]
            transition, terminal = _loss(anchor, event)
            ranked.append((-transition, -terminal, index, event))
        ranked.sort(key=lambda item: (item[0], item[1], item[2]))
        quines = []
        for _, _, index, event in ranked[:count]:
            transition, terminal = _loss(anchor, event)
            quines.append({
                "index": index,
                "witness_id": event[0],
                "witness_sha256": digest(canonical(event)),
                "signed_reward_proxy": 1 if event[5] else -1,
                "transition_brier_numerator": transition,
                "reward_brier_numerator": terminal,
            })
        groups[regime] = {"window": [start, stop], "quines": quines}
    return {
        "schema": SCHEMA,
        "anchor_checkpoint_sha256": digest(_checkpoint(anchor)),
        "anchor_ledger_sha256": digest(canonical(events)),
        "ranking": "retrospective_anchor_transition_brier_not_prequential",
        "charge": "binary_terminal_reward_plus1_minus1_no_cost_claim",
        "quines_per_regime": count,
        "regimes": groups,
    }


def assess_update(anchor, current, proposed, quines, quine_sha256, *,
                  max_brier_drift=TOLERANCE):
    """Veto an overwrite if any Quine OR any familiar regime drifts > 0.02.

    The unchanged current state is returned on veto, NOT the original anchor:
    previously admitted continuation remains cumulative. A rejected candidate
    hash is advisory fork provenance only; no rival specialist is activated.
    """
    if not isinstance(max_brier_drift, Fraction) or not 0 <= max_brier_drift <= 1:
        raise ValueError("Invalid frozen retention tolerance")
    if digest(canonical(quines)) != quine_sha256 or quines.get("schema") != SCHEMA:
        raise ValueError("Quine manifest pin mismatch")
    old, prior, after = _ledger(anchor), _ledger(current), _ledger(proposed)
    if (quines.get("anchor_checkpoint_sha256") != digest(_checkpoint(anchor))
            or quines.get("anchor_ledger_sha256") != digest(canonical(old))
            or prior[:len(old)] != old or after[:len(prior)] != prior):
        raise ValueError("Quine anchor or exact shared prefix mismatch")
    if len(after) != len(prior) + 1:
        raise ValueError("Each Quine gate checks exactly one newly witnessed episode")

    allowed = max_brier_drift * SCALE * SCALE
    largest = Fraction(0)
    items = 0
    groups = {}
    indices_seen = set()
    for name, group in sorted(quines["regimes"].items()):
        start, stop = group["window"]
        if (type(name) is not str or not name or type(start) is not int
                or type(stop) is not int or not 0 <= start < stop <= len(old)
                or len(group["quines"]) != quines["quines_per_regime"]
                or not 5 <= len(group["quines"]) <= 10):
            raise ValueError("Invalid frozen Quine regime")
        baseline = [0, 0]
        candidate = [0, 0]
        for index in range(start, stop):
            for target, value in enumerate(_loss(anchor, old[index])):
                baseline[target] += value
            for target, value in enumerate(_loss(proposed, old[index])):
                candidate[target] += value
        denominator = (stop - start) * SCALE * SCALE
        group_drift = [Fraction(new - before, denominator)
                       for before, new in zip(baseline, candidate, strict=True)]
        passed = all(delta <= max_brier_drift for delta in group_drift)
        groups[name] = {"familiar_transition_drift": float(group_drift[0]),
                        "familiar_reward_drift": float(group_drift[1]),
                        "pass": passed}
        for item in group["quines"]:
            index = item["index"]
            if (type(index) is not int or not start <= index < stop
                    or index in indices_seen):
                raise ValueError("Quine index missing, duplicated, or outside regime")
            indices_seen.add(index)
            event = old[index]
            original = _loss(anchor, event)
            if (item["witness_id"] != event[0]
                    or item["witness_sha256"] != digest(canonical(event))
                    or item["signed_reward_proxy"] != (1 if event[5] else -1)
                    or original != (item["transition_brier_numerator"],
                                    item["reward_brier_numerator"])):
                raise ValueError("Quine evidence does not match the pinned anchor")
            updated = _loss(proposed, event)
            delta = [Fraction(new - before, SCALE * SCALE)
                     for before, new in zip(original, updated, strict=True)]
            largest = max(largest, *delta)
            if any(value > max_brier_drift for value in delta):
                passed = False
            items += 1
        groups[name]["pass"] = passed

    if not groups:
        raise ValueError("No Quines selected")
    baseline, candidate = [0, 0], [0, 0]
    for event in old:
        for target, value in enumerate(_loss(anchor, event)):
            baseline[target] += value
        for target, value in enumerate(_loss(proposed, event)):
            candidate[target] += value
    overall = [Fraction(new - before, len(old) * SCALE * SCALE)
               for before, new in zip(baseline, candidate, strict=True)]
    passed = all(group["pass"] for group in groups.values())
    passed &= all(value <= max_brier_drift for value in overall)
    candidate_pin = digest(_checkpoint(proposed))
    return (proposed if passed else current), {
        "status": "ADMIT_RESEARCH_CANDIDATE" if passed else "VETO_SHARED_STATE_OVERWRITE",
        "scientific_pass": False,
        "quines_checked": items,
        "largest_single_quine_delta": float(largest),
        "max_brier_drift": str(max_brier_drift),
        "full_anchor_transition_drift": float(overall[0]),
        "full_anchor_reward_drift": float(overall[1]),
        "regimes": groups,
        "active_checkpoint_sha256": digest(_checkpoint(proposed if passed else current)),
        "rejected_shadow_checkpoint_sha256": None if passed else candidate_pin,
        "speciation": "proposal_only_not_activated" if not passed else "not_needed",
    }


def guarded_observe(anchor, current, quines, quine_sha256, identifier, views, row, *,
                    source_sha256, packet_sha256, max_brier_drift=TOLERANCE):
    """Wrap the existing single shared-witness transaction, no second learner."""
    before = digest(_checkpoint(current))
    anchor_before = digest(_checkpoint(anchor))
    proposed = current.observe_experience(
        identifier, views, row, source_sha256=source_sha256,
        packet_sha256=packet_sha256,
    )
    if digest(_checkpoint(current)) != before or digest(_checkpoint(anchor)) != anchor_before:
        raise ValueError("Quine update mutated a retained input checkpoint")
    if proposed is current:
        return current, {"status": "IDEMPOTENT_WITNESS", "scientific_pass": False,
                         "active_checkpoint_sha256": before}
    return assess_update(anchor, current, proposed, quines, quine_sha256,
                         max_brier_drift=max_brier_drift)
