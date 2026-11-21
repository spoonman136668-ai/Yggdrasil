"""G30: finer fixed-step retention/plasticity DEV experiment (no owner admission).

Source-bound historical diagnostic only: compare previous frozen, G28 full,
G29 coarse, and G30 finer fractional post-witness head updates. Selection
queries only old P0 familiar witnesses. The subsequent already-consumed
training-row label is used only for POST-selection fit diagnostics.
"""
from math import isfinite, sqrt

from four_head_retention import _inspect, HEAD_NAMES, MAX_OLD_WITNESSES
from headwise_consolidation import (
    _blend_head, _old_brier, _new_brier, MAX_DRIFT,
    MATRIX_FIELDS, VECTOR_FIELDS,
)
from post_witness_projection import assess_one_more_witness
from yggdrasil.native_context_basis import canonical, digest

# Frozen at GitHub PR #1329 G30 prereg BEFORE source code/trial evaluation.
FINE_ALPHAS = (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0)
FROZEN_ORDINALS = (1, 32, 33, 64)
TRANSITIONS = ("direct_transition", "temporal_transition")


def _blend_fine(current, proposal, alpha):
    """G25 trainable tensors/steps, but only G30's preregistered alphas."""
    if type(alpha) is not float or alpha not in FINE_ALPHAS:
        raise ValueError("G30_ALPHA_NOT_FROZEN")
    candidate = _blend_head(current, proposal, 1.0)
    for key in MATRIX_FIELDS:
        old, new = getattr(current, key), getattr(proposal, key)
        setattr(candidate, key, [
            [float(a * (1.0 - alpha) + b * alpha)
             for a, b in zip(ra, rb, strict=True)]
            for ra, rb in zip(old, new, strict=True)
        ])
    for key in VECTOR_FIELDS:
        old, new = getattr(current, key), getattr(proposal, key)
        setattr(candidate, key, [
            float(a * (1.0 - alpha) + b * alpha)
            for a, b in zip(old, new, strict=True)
        ])
    candidate._validate()
    return candidate


def _weight_delta_norm(a, b):
    accum = 0.0
    for key in MATRIX_FIELDS:
        for x, y in zip(getattr(a, key), getattr(b, key), strict=True):
            accum += sum((p-q) ** 2 for p, q in zip(x, y, strict=True))
    for key in VECTOR_FIELDS:
        accum += sum((p-q) ** 2
                     for p, q in zip(getattr(a, key), getattr(b, key),
                                     strict=True))
    value = sqrt(accum)
    if not isfinite(value):
        raise ValueError("G30_NONFINITE_WEIGHT_CHANGE")
    return value


def evaluate_fine_steps(anchor, before, after):
    """Retrospective source-only: no actual further model/world training."""
    coarse_heads, coarse = assess_one_more_witness(anchor, before, after)
    ah, old, ap = _inspect(anchor)
    bh, prior, bp = _inspect(before)
    ph, new, pp = _inspect(after)
    if len(old) < 1 or len(old) > MAX_OLD_WITNESSES:
        raise ValueError("G30_OLD_SOURCE_LIMIT")
    if (prior[:len(old)] != old or new[:len(prior)] != prior
            or len(new) != len(prior) + 1):
        raise ValueError("G30_SOURCE_PREFIX")
    outcome = new[-1]
    selected = []
    readouts = {}
    for i, name in enumerate(HEAD_NAMES):
        old_anchor = _old_brier(ah[i], i, old)
        old_before = _old_brier(bh[i], i, old)
        if not (isfinite(old_anchor) and isfinite(old_before)
                and old_before - old_anchor <= MAX_DRIFT + 1e-12):
            raise ValueError("G30_UNSAFE_PRESTATE")
        chosen = None
        for alpha in FINE_ALPHAS:
            # Alpha=1 from the source-fit proposal, safe only if it
            # preserves the exact frozen old-memory reference metric.
            h = _blend_fine(bh[i], ph[i], alpha)
            candidate_old = _old_brier(h, i, old)
            if not isfinite(candidate_old):
                raise ValueError("G30_NONFINITE_OLD_BRIER")
            if candidate_old - old_anchor <= MAX_DRIFT + 1e-12:
                chosen = (alpha, h, candidate_old)
                break
        if chosen is None:  # zero update must be safe after checked prestate
            raise ValueError("G30_NO_SAFE_PROJECTION")
        alpha, head, old_loss = chosen
        norm = _weight_delta_norm(head, bh[i])
        new_fit = _new_brier(head, i, outcome, prior)
        coarse_fit = _new_brier(coarse_heads[i], i, outcome, prior)
        frozen_fit = _new_brier(bh[i], i, outcome, prior)
        if any(not isfinite(v) or v < 0 or v > 1
               for v in (new_fit, coarse_fit, frozen_fit)):
            raise ValueError("G30_POSTFIT_NONFINITE")
        if (head.steps != ph[i].steps
                or old_loss - old_anchor > MAX_DRIFT + 1e-12):
            raise ValueError("G30_STEPS_OR_OLD_RETENTION")
        readouts[name] = {
            "fine_alpha": alpha,
            "coarse_alpha": coarse["heads"][name]["alpha"],
            "old_anchor_brier": old_anchor,
            "fine_old_drift": old_loss - old_anchor,
            "coarse_old_drift":
                coarse["heads"][name]["projected_old_drift"],
            "frozen_old_drift": old_before - old_anchor,
            "trainable_weight_l2_change": norm,
            "changed_weights": norm > 0.0,
            "new_witness_frozen_postfit_brier": frozen_fit,
            "new_witness_coarse_postfit_brier": coarse_fit,
            "new_witness_fine_postfit_brier": new_fit,
            "next_row_label_used_to_choose_alpha": False,
        }
        selected.append(head)
    if tuple(_inspect(m)[2] for m in (anchor, before, after)) != (ap, bp, pp):
        raise ValueError("G30_MUTATED_SOURCE_INPUT")
    names = TRANSITIONS
    fine_avg = sum(readouts[n]["new_witness_fine_postfit_brier"]
                   for n in names) / 2
    coarse_avg = sum(readouts[n]["new_witness_coarse_postfit_brier"]
                     for n in names) / 2
    frozen_avg = sum(readouts[n]["new_witness_frozen_postfit_brier"]
                     for n in names) / 2
    report = {
        "gate": "G30_FIXED_FINE_STEP_PLASTICITY_DEV",
        "original_source_before_sha256": bp,
        "original_source_after_sha256": pp,
        "old_ledger_sha256": digest(canonical(old)),
        "old_witnesses": len(old),
        "fixed_fine_alphas": list(FINE_ALPHAS),
        "old_brier_limit": MAX_DRIFT,
        "heads": readouts,
        "all_old_heads_within_original_bound": all(
            v["fine_old_drift"] <= MAX_DRIFT + 1e-12
            for v in readouts.values()),
        "both_transitions_have_real_weight_updates": all(
            readouts[n]["fine_alpha"] > 0.0 and
            readouts[n]["changed_weights"] for n in names),
        "transition_next_postfit_better_than_frozen":
            fine_avg < frozen_avg - 1e-12,
        "transition_next_postfit_better_than_coarse":
            fine_avg < coarse_avg - 1e-12,
        "transition_next_postfit_not_worse_than_coarse":
            fine_avg <= coarse_avg + 1e-12,
        "transition_next_postfit_mean_brier":
            {"frozen": frozen_avg, "coarse": coarse_avg, "fine": fine_avg},
        "next_event_is_already_consumed_training_row": True,
        "new_event_label_used_in_selection": False,
        "new_world_actions": 0,
        "official_native_checkpoint": False,
        "scientific_pass": False,
    }
    return tuple(selected), report


def summarize_fine_samples(samples):
    if (type(samples) is not list or len(samples) != len(FROZEN_ORDINALS)
            or [x.get("ordinal") for x in samples] != list(FROZEN_ORDINALS)):
        raise ValueError("G30_FROZEN_SAMPLE_ORDER")
    reports = [v["analysis"] for v in samples]
    if any(not r["all_old_heads_within_original_bound"] for r in reports):
        raise ValueError("G30_RETENTION_NEGATIVE")
    case1 = reports[0]
    improvement = (
        case1["both_transitions_have_real_weight_updates"]
        and case1["transition_next_postfit_better_than_frozen"]
        and case1["transition_next_postfit_better_than_coarse"]
    )
    parity = all(r["transition_next_postfit_not_worse_than_coarse"]
                 for r in reports)
    return {
        "gate": "G30_SOURCE_CONSUMED_FINE_STEP_QUALIFICATION",
        "frozen_sample_ordinals": list(FROZEN_ORDINALS),
        "cases": samples,
        "old_familiar_limit_pass_count": sum(
            r["all_old_heads_within_original_bound"] for r in reports),
        "both_transition_heads_changed_count": sum(
            r["both_transitions_have_real_weight_updates"] for r in reports),
        "case1_both_transition_heads_changed":
            case1["both_transitions_have_real_weight_updates"],
        "case1_training_row_fit_strictly_better_than_both_controls":
            case1["transition_next_postfit_better_than_frozen"]
            and case1["transition_next_postfit_better_than_coarse"],
        "not_worse_than_g29_coarse_in_all_cases": parity,
        "development_classification": (
            "DEV_FINE_STEP_HELPFUL" if improvement and parity
            else "DEV_FINE_STEP_NO_GO"),
        "new_world_actions": 0,
        "held_worlds": 0,
        "scientific_pass": False,
        "owner_admission": False,
        "deployment": "NONE",
    }
