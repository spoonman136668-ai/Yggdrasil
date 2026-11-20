"""Retrospective four-head functional-retention audit on existing witnessed history.

Read-only development diagnosis. Does not train, select policy, obtain source
world actions, approve continuation, or establish held/scientific benefit.
"""
from math import isfinite

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist

HEAD_NAMES = ("direct_transition", "direct_reward",
              "temporal_transition", "temporal_reward")
HEAD_TYPES = (ActionLatentSpecialist, ActionLatentSpecialist,
              TemporalLatentSpecialist, TemporalLatentSpecialist)
KINDS = ("transition", "reward", "transition", "reward")
MAX_OLD_WITNESSES = 4096
MAX_COMPARISON_DRIFT = 0.02  # Existing Quine P0 advisory limit; NOT an owner GO.


def _inspect(model):
    """Check genuine JEPA head interfaces and immutable native witness access."""
    heads = model._heads
    if (type(heads) is not tuple or len(heads) != 4
            or any(type(h) is not t or h.kind != k
                   for h, t, k in zip(heads, HEAD_TYPES, KINDS, strict=True))):
        raise ValueError("HEAD4_HEAD_IDENTITY")
    ledger = model.native._episode_reader()._ledger
    if type(ledger) not in (tuple, list):
        raise ValueError("HEAD4_LEDGER_TYPE")
    ledger = tuple(ledger)
    for event in ledger:
        if (type(event) not in (tuple, list) or len(event) != 6
                or any(type(value) is not int or value not in (0, 1)
                       for value in event[2:])):
            raise ValueError("HEAD4_PUBLIC_EVENT")
    raw = model.checkpoint()
    if type(raw) is not bytes or not raw:
        raise ValueError("HEAD4_CHECKPOINT_BYTES")
    return heads, ledger, digest(raw)


def _head_probability(head, position, event, history):
    _, views, first, state, second, _ = event
    extras = (first,) if position in (0, 2) else (first, state, second)
    if position < 2:
        value = head.probability(views, *extras)
    else:
        value = head.probability(views, extras, history)
    if not isinstance(value, (float, int)) or not isfinite(value) or not 0 <= value <= 1:
        raise ValueError("HEAD4_PROBABILITY")
    return float(value)


def audit_old_heads(anchor, descendant, restored):
    """Score four trained heads on the exact same historical OLD public events.

    Brier is calculated using *retrospective* readouts from complete trained
    checkpoints, NOT prequential or independently held evaluation. The
    96-event suffix may already have been consumed; no source action occurs.
    """
    a_heads, original, a_pin = _inspect(anchor)
    b_heads, continued, b_pin = _inspect(descendant)
    c_heads, cold, c_pin = _inspect(restored)
    if not 0 < len(original) <= MAX_OLD_WITNESSES:
        raise ValueError("HEAD4_OLD_WITNESS_LIMIT")
    if continued[:len(original)] != original or len(continued) <= len(original):
        raise ValueError("HEAD4_HISTORICAL_PREFIX")
    if cold != continued or c_pin != b_pin:
        raise ValueError("HEAD4_COLD_CHECKPOINT_MISMATCH")

    total = len(original)
    report = {}
    for head_index, name in enumerate(HEAD_NAMES):
        old_loss = new_loss = max_change = max_cold_difference = 0.0
        for index, event in enumerate(original):
            # Historical source before each old row only. The same past is
            # supplied to old, descendant and cold-restored temporal heads.
            past = original[max(0, index - 8):index]
            expected = event[3] if head_index in (0, 2) else event[5]
            before = _head_probability(a_heads[head_index], head_index, event, past)
            after = _head_probability(b_heads[head_index], head_index, event, past)
            replay = _head_probability(c_heads[head_index], head_index, event, past)
            old_loss += (before - expected) ** 2
            new_loss += (after - expected) ** 2
            max_change = max(max_change, abs(after - before))
            max_cold_difference = max(max_cold_difference, abs(after - replay))
        if max_cold_difference > 1e-9:
            raise ValueError("HEAD4_COLD_READOUT_MISMATCH")
        before_score = old_loss / total
        after_score = new_loss / total
        drift = after_score - before_score
        report[name] = {
            "old_brier": before_score,
            "continued_brier": after_score,
            "old_brier_drift": drift,
            "maximum_probability_change": max_change,
            "cold_replay_max_difference": max_cold_difference,
            "within_existing_quine_comparison": drift <= MAX_COMPARISON_DRIFT,
        }

    if (_inspect(anchor)[2] != a_pin or _inspect(descendant)[2] != b_pin
            or _inspect(restored)[2] != c_pin):
        raise ValueError("HEAD4_MUTATED_DURING_READOUT")
    within = all(item["within_existing_quine_comparison"]
                 for item in report.values())
    return {
        "gate": "ARCHIVED_FOUR_HEAD_RETENTION_READOUT",
        "disposition": ("HISTORICAL_HEAD_RETENTION_WITHIN_COMPARISON"
                        if within else "HISTORICAL_HEAD_RETENTION_EXCEEDS_COMPARISON"),
        "old_witness_count": total,
        "continuation_witness_count": len(continued) - total,
        "old_ledger_sha256": digest(canonical(original)),
        "anchor_checkpoint_sha256": a_pin,
        "descendant_checkpoint_sha256": b_pin,
        "restored_checkpoint_sha256": c_pin,
        "heads": report,
        "threshold_is_advisory_not_owner_science_acceptance": True,
        "evaluation": "retrospective_original_witnesses_not_heldout",
        "original_world_actions": 0,
        "new_training": False,
        "scientific_pass": False,
        "deployment": "NONE",
    }
