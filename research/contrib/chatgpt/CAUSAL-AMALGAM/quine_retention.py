"""Research-only Quine retention veto for the existing immutable Amalgam learner.

This module does not run a source, train an additional learner, or authorize
policy influence. It checks each *proposed* shared witness update before its
candidate can replace the currently active research readout.
"""
from fractions import Fraction

from yggdrasil.native_context_basis import canonical, digest

SCHEMA = "yggdrasil.amalgam.quine-retention.v2"
SCALE = 1_000_000
TOLERANCE = Fraction(1, 50)


def _system(value):
    return value.system if hasattr(value, "system") else value


def _ledger(value):
    return _system(value).native._episode_reader()._ledger


def _selector(value):
    return hasattr(value, "system")


def _selector_receipt(value):
    """Canonical active-selector custody; a native checkpoint alone omits routing."""
    if (not callable(getattr(value, "forecast", None))
            or type(getattr(value, "window", None)) is not int
            or type(getattr(value, "minimum_count", None)) is not int
            or not isinstance(getattr(value, "minimum_gain", None), Fraction)
            or type(getattr(value, "enable_reward", None)) is not bool
            or type(getattr(value, "_evidence", None)) is not dict):
        raise ValueError("Quine selector custody unavailable")
    if (not 1 <= value.minimum_count <= value.window
            or not 0 < value.minimum_gain <= 1):
        raise ValueError("Quine selector configuration invalid")
    records = []
    for key, history in sorted(value._evidence.items()):
        if (type(key) is not tuple or len(key) not in (2, 4)
                or any(type(x) is not int or x not in (0, 1) for x in key)
                or type(history) is not tuple or len(history) > value.window):
            raise ValueError("Quine selector evidence shape invalid")
        encoded = []
        for pair in history:
            if (type(pair) is not tuple or len(pair) != 2
                    or any(not isinstance(x, Fraction) for x in pair)):
                raise ValueError("Quine selector evidence value invalid")
            encoded.append([str(pair[0]), str(pair[1])])
        records.append([list(key), encoded])
    return {
        "config": [value.window, value.minimum_count,
                   str(value.minimum_gain), value.enable_reward],
        "evidence": records,
    }


def _checkpoint(value):
    joint = _system(value).checkpoint()
    if not _selector(value):
        return joint
    return canonical({"schema": "yggdrasil.amalgam.active-policy-custody.v1",
                      "joint_sha256": digest(joint),
                      "selector": _selector_receipt(value)})


def _require_policy_modes(*values):
    modes = tuple(_selector(value) for value in values)
    if len(set(modes)) != 1:
        raise ValueError("Quine active-policy/native bypass mismatch")
    if modes[0]:
        configurations = [_selector_receipt(value)["config"] for value in values]
        if any(config != configurations[0] for config in configurations[1:]):
            raise ValueError("Quine active-selector configuration changed")


def verify_selector_replay(expected, restored):
    """Read-only comparison; caller must perform actual authenticated cold restore."""
    _require_policy_modes(expected, restored)
    if not _selector(expected):
        raise ValueError("Quine selector replay requires active selectors")
    if _ledger(expected) != _ledger(restored):
        raise ValueError("Quine restored witness ledger differs")
    if _checkpoint(expected) != _checkpoint(restored):
        raise ValueError("Quine restored active-policy custody differs")
    for event in _ledger(expected):
        if _loss(expected, event) != _loss(restored, event):
            raise ValueError("Quine restored functional readout differs")
    return {"policy_sha256": digest(_checkpoint(restored)),
            "readout_witnesses": len(_ledger(restored)),
            "source_actions": 0, "scientific_pass": False}


def _loss(value, event):
    """Two quantized Brier numerators for one witnessed transition and reward."""
    _, views, first, state, second, reward = event
    if type(state) is not int or state not in (0, 1) or type(reward) is not int or reward not in (0, 1):
        raise ValueError("Quine witness has nonbinary labels")
    if _selector(value):
        forecast = value.forecast
        transition = forecast(views, first)
        terminal = forecast(views, first, state, second)
    else:
        forecast = value.native.experience_context_forecast
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
    _checkpoint(anchor)  # Fail closed when active selector custody cannot be sealed.
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



def _verify_frozen_inputs(anchor, current, quines, quine_sha256, max_brier_drift):
    """Authenticate the frozen guard before any observation, including replay."""
    if type(max_brier_drift) is not Fraction or max_brier_drift != TOLERANCE:
        raise ValueError("Frozen Quine drift gate is exactly 1/50")
    if (type(quines) is not dict
            or digest(canonical(quines)) != quine_sha256
            or quines.get("schema") != SCHEMA):
        raise ValueError("Quine manifest pin mismatch")
    _require_policy_modes(anchor, current)
    old, prior = _ledger(anchor), _ledger(current)
    if (quines.get("anchor_checkpoint_sha256") != digest(_checkpoint(anchor))
            or quines.get("anchor_ledger_sha256") != digest(canonical(old))
            or prior[:len(old)] != old):
        raise ValueError("Quine anchor or exact shared prefix mismatch")
    return old, prior


def assess_update(anchor, current, proposed, quines, quine_sha256, *,
                  max_brier_drift=TOLERANCE):
    """Veto an overwrite if any Quine OR any familiar regime drifts > 0.02.

    The unchanged current state is returned on veto, NOT the original anchor:
    previously admitted continuation remains cumulative. A rejected candidate
    hash is advisory fork provenance only; no rival specialist is activated.
    """
    _require_policy_modes(anchor, current, proposed)
    old, prior = _verify_frozen_inputs(anchor, current, quines,
                                       quine_sha256, max_brier_drift)
    after = _ledger(proposed)
    if after[:len(prior)] != prior:
        raise ValueError("Quine anchor or exact shared prefix mismatch")
    if len(after) != len(prior) + 1:
        raise ValueError("Each Quine gate checks exactly one newly witnessed episode")

    # Historical anchor and candidate forecasts are pure reads. Score each
    # retained charged witness once per policy, then reuse the frozen losses
    # for per-regime, Quine and complete-prefix checks. This preserves every
    # drift threshold without repeatedly rescoring the same native history.
    anchor_losses = tuple(_loss(anchor, event) for event in old)
    proposal_losses = tuple(_loss(proposed, event) for event in old)
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
            for target, value in enumerate(anchor_losses[index]):
                baseline[target] += value
            for target, value in enumerate(proposal_losses[index]):
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
            original = anchor_losses[index]
            if (item["witness_id"] != event[0]
                    or item["witness_sha256"] != digest(canonical(event))
                    or item["signed_reward_proxy"] != (1 if event[5] else -1)
                    or original != (item["transition_brier_numerator"],
                                    item["reward_brier_numerator"])):
                raise ValueError("Quine evidence does not match the pinned anchor")
            updated = proposal_losses[index]
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
    for old_pair, new_pair in zip(anchor_losses, proposal_losses, strict=True):
        for target, value in enumerate(old_pair):
            baseline[target] += value
        for target, value in enumerate(new_pair):
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
                    source_sha256, packet_sha256, max_brier_drift=TOLERANCE,
                    on_veto=None):
    """Guard one charged update, requiring external custody for a rejected witness.

    The active model excludes a vetoed witness. The existing owner must store
    and acknowledge this canonical receipt before the caller can continue.
    Acknowledgement alone is NOT proof of durability; that is the owner's duty.
    """
    _verify_frozen_inputs(anchor, current, quines, quine_sha256,
                          max_brier_drift)
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
    selected, report = assess_update(anchor, current, proposed, quines, quine_sha256,
                                     max_brier_drift=max_brier_drift)
    if report["status"] == "VETO_SHARED_STATE_OVERWRITE":
        receipt = canonical({
            "schema": "yggdrasil.amalgam.charged-veto-receipt.v1",
            "event": _ledger(proposed)[-1],
            "source_sha256": source_sha256,
            "packet_sha256": packet_sha256,
            "active_before_sha256": before,
            "rejected_candidate_sha256": report["rejected_shadow_checkpoint_sha256"],
        })
        receipt_sha256 = digest(receipt)
        if not callable(on_veto):
            raise RuntimeError("VETO_REQUIRES_DURABLE_CHARGED_RECEIPT")
        if on_veto(receipt, receipt_sha256) != receipt_sha256:
            raise RuntimeError("VETO_DURABLE_CHARGED_RECEIPT_NOT_ACKNOWLEDGED")
        report["rejected_witness_receipt_sha256"] = receipt_sha256
        report["external_receipt_acknowledged"] = True
        report["active_model_contains_rejected_witness"] = False
    return selected, report
