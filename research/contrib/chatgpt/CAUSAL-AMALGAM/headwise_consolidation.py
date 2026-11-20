"""JEPA-G25: source-free, bounded headwise consolidation proposal (DEV only).

Fixed alpha candidates are screened against OLD witnessed Brier only. Observed
new-witness labels are for POST-SELECTION diagnostics only; they do not control
selection. The owner learner and its source-refitted checkpoint are untouched.

WARNING: interpolated specialists are NOT source-equivalent authentic official
Amalgam checkpoints and must never be passed off as accepted/cold-restorable.
"""
from math import isfinite

from four_head_retention import (
    _head_probability, _inspect, HEAD_NAMES, MAX_OLD_WITNESSES,
)

ALPHAS_DESCENDING = (1.0, 0.75, 0.5, 0.25, 0.0)
MAX_DRIFT = 0.02
MATRIX_FIELDS = ("encoder", "predictor")
VECTOR_FIELDS = ("encoder_bias", "predictor_bias")
TRANSITION_HEADS = ("direct_transition", "temporal_transition")


def _blend_head(anchor, proposal, alpha):
    """Copy proposal head and change ONLY its fixed-footprint trainable floats."""
    if type(alpha) is not float or alpha not in ALPHAS_DESCENDING:
        raise ValueError("G25_ALPHA_NOT_FROZEN")
    if type(anchor) is not type(proposal) or anchor.kind != proposal.kind:
        raise ValueError("G25_HEAD_IDENTITY")
    chosen = proposal.clone()
    for key in MATRIX_FIELDS:
        left, right, target = (
            getattr(anchor, key), getattr(proposal, key), getattr(chosen, key))
        if (len(left) != len(right) or len(target) != len(left)
                or any(len(a) != len(b) or len(c) != len(a)
                       for a, b, c in zip(left, right, target, strict=True))):
            raise ValueError("G25_WEIGHT_SHAPE")
        for i, (a, b) in enumerate(zip(left, right, strict=True)):
            target[i] = [
                float(x * (1.0 - alpha) + y * alpha)
                for x, y in zip(a, b, strict=True)
            ]
    for key in VECTOR_FIELDS:
        a, b = getattr(anchor, key), getattr(proposal, key)
        if len(a) != len(b):
            raise ValueError("G25_BIAS_SHAPE")
        setattr(chosen, key, [
            float(x * (1.0 - alpha) + y * alpha)
            for x, y in zip(a, b, strict=True)
        ])
    chosen._validate()
    return chosen


def _old_brier(head, head_index, original):
    total = 0.0
    for index, event in enumerate(original):
        prefix = original[max(0, index - 8):index]
        observed = event[3] if head_index in (0, 2) else event[5]
        probability = _head_probability(head, head_index, event, prefix)
        total += (probability - observed) ** 2
    return total / len(original)


def _new_brier(head, head_index, event, previous):
    observed = event[3] if head_index in (0, 2) else event[5]
    probability = _head_probability(head, head_index, event, previous[-8:])
    return (probability - observed) ** 2


def assess_bounded_blend(anchor, current, proposed):
    """Read original consumed proposal; do NOT return a restorable/active model.

    This experiment has already seen the original public P0 witness source and
    is strictly exploratory. Its reported one-witness post-fit Brier is in-sample.
    """
    a_heads, old, a_pin = _inspect(anchor)
    c_heads, current_ledger, c_pin = _inspect(current)
    p_heads, proposed_ledger, p_pin = _inspect(proposed)
    if not 0 < len(old) <= MAX_OLD_WITNESSES:
        raise ValueError("G25_OLD_BUDGET")
    if (current_ledger[:len(old)] != old
            or proposed_ledger[:len(current_ledger)] != current_ledger):
        raise ValueError("G25_SOURCE_PREFIX")
    if len(proposed_ledger) != len(current_ledger) + 1:
        raise ValueError("G25_EXACTLY_ONE_PROPOSAL")
    event = proposed_ledger[-1]
    names = {}
    for position, name in enumerate(HEAD_NAMES):
        original = a_heads[position]
        updated = p_heads[position]
        baseline = _old_brier(original, position, old)
        initial_new = _new_brier(original, position, event, current_ledger)
        proposal_new = _new_brier(updated, position, event, current_ledger)
        selected = None
        for alpha in ALPHAS_DESCENDING[:-1]:
            blended = _blend_head(original, updated, alpha)
            old_brier = _old_brier(blended, position, old)
            if not isfinite(old_brier):
                raise ValueError("G25_NONFINITE_OLD_LOSS")
            if old_brier - baseline <= MAX_DRIFT + 1e-12:
                selected = (alpha, blended, old_brier)
                break
        if selected is None:
            # Frozen old head always has zero old-memory drift. Native state
            # and all original proposals continue independently in shadow.
            selected = (0.0, _blend_head(original, updated, 0.0), baseline)
        alpha, head, old_after = selected
        new_loss = _new_brier(head, position, event, current_ledger)
        if not (isfinite(new_loss) and 0.0 <= new_loss <= 1.0):
            raise ValueError("G25_NONFINITE_NEW_LOSS")
        if old_after - baseline > MAX_DRIFT + 1e-12:
            raise ValueError("G25_OLD_RETENTION_BREACH")
        names[name] = {
            "selected_alpha": alpha,
            "old_anchor_brier": baseline,
            "old_selected_brier": old_after,
            "old_drift": old_after - baseline,
            "new_witness_frozen_head_brier": initial_new,
            "new_witness_selected_brier": new_loss,
            "new_witness_full_update_brier": proposal_new,
            "within_frozen_old_comparison": True,
        }
    if tuple(_inspect(m)[2] for m in (anchor, current, proposed)) != (a_pin, c_pin, p_pin):
        raise ValueError("G25_MUTATED_INPUT_CHECKPOINT")
    return {
        "schema": "yggdrasil.amalgam.dev-headwise-blend.v1",
        "old_ledger_count": len(old),
        "old_witness_count": len(old),
        "admitted_original_proposal_count": 0,
        "source_actions": 0,
        "replay_interventions": 0,
        "selected_weight_factors": list(ALPHAS_DESCENDING),
        "max_old_head_brier_drift": MAX_DRIFT,
        "old_ledger_sha256": _inspect(anchor)[2],
        "anchor_checkpoint_sha256": a_pin,
        "current_checkpoint_sha256": c_pin,
        "proposed_checkpoint_sha256": p_pin,
        "heads": names,
        "head_count": len(names),
        "new_event_label_used_in_selection": False,
        "observed_new_event_is_in_sample": True,
        "official_checkpoint_restore_supported": False,
        "repaired_learner_constructed": False,
        "scientific_pass": False,
    }
