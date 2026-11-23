"""Read original native causal repair receipts as immutable typed cell versions.

Research-only historical recall. Does not route live predictions, select a
regime, change native counters, train, or promote learned structure.
"""
from __future__ import annotations

from fractions import Fraction


def _binary_count(pair, field):
    if (type(pair) not in (list, tuple) or len(pair) != 2 or
            any(type(v) is not int or v < 0 or v > 65535 for v in pair)):
        raise ValueError(f"VERSION_{field}_COUNT")
    return tuple(pair)


def _outcome_probability(pair):
    failures, successes = _binary_count(pair, "SOURCE")
    return Fraction(successes + 1, failures + successes + 2)


def _source_event(model, identifier):
    event = model._ids.get(identifier)
    if event is None or len(event) != 6 or event[0] != identifier:
        raise ValueError("VERSION_EVIDENCE_NOT_IN_NATIVE_LEDGER")
    return event


def read_repair_version(native, *, last_evidence_id, target, slot, action, version):
    """Return a source-validated historical native cell probability.

    The caller must possess the exact third witness ID of a native repair.
    It is an audit capability, NOT a regime oracle or online routing policy.
    """
    if (type(last_evidence_id) is not str or len(last_evidence_id) != 64 or
            any(ch not in "0123456789abcdef" for ch in last_evidence_id)):
        raise ValueError("VERSION_WITNESS_ID")
    # Only the observed, experimentally qualified native transition reset is
    # exposed here. Terminal overwrite support needs its own separate proof.
    if type(target) is not str or target != "transition":
        raise ValueError("VERSION_TARGET")
    if type(slot) is not int or not 0 <= slot < 2:
        raise ValueError("VERSION_SLOT")
    if type(action) is not int or action not in (0, 1):
        raise ValueError("VERSION_ACTION")
    if version not in ("before", "reset", "live") or type(version) is not str:
        raise ValueError("VERSION_KIND")

    # Exact native source's immutable checkpoint ledger is custody. Its public
    # repair journal is reconstructed from that ledger by native.restore().
    receipts = [r for r in native.info()["repairs"]
                if r["target"] == target and r["slot"] == slot
                and r["action"] == action
                and len(r["evidence"]) == 3
                and r["evidence"][-1] == last_evidence_id]
    if len(receipts) != 1:
        raise ValueError("VERSION_RECEIPT_NOT_UNIQUE")
    receipt = receipts[0]
    old = _binary_count(receipt["old_counts"], "OLD")
    reset = _binary_count(receipt["new_counts"], "RESET")
    if (len(set(receipt["evidence"])) != 3 or sum(old) < 12
            or sum(reset) != 3 or min(reset) != 0
            or receipt["prior_majority"] not in (0, 1)
            or old[receipt["prior_majority"]] * 5 < 4 * sum(old)
            or reset[1 - receipt["prior_majority"]] != 3):
        raise ValueError("VERSION_RECEIPT_STRUCTURE")

    # Verify each repair witness is a real, correctly addressed native event,
    # not just a forged public metadata claim. Outcomes are not generated.
    indices = []
    locations = {event[0]: i for i, event in enumerate(native._ledger)}
    for identifier in receipt["evidence"]:
        event = _source_event(native, identifier)
        _, views, first, state, second, reward = event
        context = native._context(views)
        address, arm, outcome = context, first, state
        if (address != slot or arm != action or
                outcome != 1 - receipt["prior_majority"]):
            raise ValueError("VERSION_WITNESS_CELL_MISMATCH")
        indices.append(locations.get(identifier))
    if any(index is None for index in indices) or indices != sorted(indices):
        raise ValueError("VERSION_WITNESS_ORDER")

    if version == "before":
        counts = old
    elif version == "reset":
        counts = reset
    else:
        counts = _binary_count(native._transition._counts[slot][action], "LIVE")
    return {
        "target": target, "slot": slot, "action": action,
        "last_evidence_id": last_evidence_id,
        "version": version,
        "counts": list(counts),
        "probability": _outcome_probability(counts),
        "derived_state_sha256": native.info()["state_sha256"],
        "evidence_count": len(receipt["evidence"]),
    }
