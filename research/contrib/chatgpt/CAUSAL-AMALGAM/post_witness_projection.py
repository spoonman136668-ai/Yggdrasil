"""G29 source-consumed post-witness retention projection. Research-only.

A source-cold G26-selected JEPA head state is advanced by the exact G28 native
one-witness training. We assess a second bounded step AFTER that witness, with
frozen old-ledger loss only. This is a development diagnostic: old bound is
guaranteed by alpha=0 if prestate was safe. New-row scores are POST-FIT only.
No source actions, official native checkpoint, new learner or owner acceptance.
"""
from math import isfinite

from four_head_retention import (
    _inspect, HEAD_NAMES, MAX_OLD_WITNESSES,
)
from headwise_consolidation import (
    ALPHAS_DESCENDING, MAX_DRIFT, MATRIX_FIELDS, VECTOR_FIELDS,
    _blend_head, _new_brier, _old_brier,
)
from headwise_capsule import _saved
from yggdrasil.native_context_basis import canonical, digest


def _weights(head):
    return canonical({
        "matrix": [getattr(head, x) for x in MATRIX_FIELDS],
        "bias": [getattr(head, x) for x in VECTOR_FIELDS],
    })


def assess_one_more_witness(anchor, before, after):
    """Select among G25's same five alphas, predeclared OLD-memory loss only.

    Return four standalone research heads + data. The returned heads are not
    source-equivalent and cannot be admitted through official native restore.
    """
    ah, old, ap = _inspect(anchor)
    bh, prior, bp = _inspect(before)
    ph, new, pp = _inspect(after)
    if not 0 < len(old) <= MAX_OLD_WITNESSES:
        raise ValueError("G29_OLD_WITNESS_LIMIT")
    if (prior[:len(old)] != old or new[:len(prior)] != prior
            or len(new) != len(prior) + 1):
        raise ValueError("G29_ONE_WITNESS_PREFIX")
    if any(p.steps - b.steps != 3 for p, b in zip(ph, bh, strict=True)):
        raise ValueError("G29_HEAD_UPDATE_STEPS")

    outcome = new[-1]  # scoring only, never used to select alpha
    selected_heads = []
    records = {}
    for index, name in enumerate(HEAD_NAMES):
        baseline = _old_brier(ah[index], index, old)
        old_before = _old_brier(bh[index], index, old)
        if not (isfinite(baseline) and isfinite(old_before)
                and old_before - baseline <= MAX_DRIFT + 1e-12):
            raise ValueError("G29_PRESTATE_RETENTION_BREACH")
        full_loss = _old_brier(ph[index], index, old)
        choice = None
        for alpha in ALPHAS_DESCENDING:
            h = _blend_head(bh[index], ph[index], alpha)
            loss = _old_brier(h, index, old)
            if not isfinite(loss):
                raise ValueError("G29_NONFINITE_OLD_LOSS")
            if loss - baseline <= MAX_DRIFT + 1e-12:
                choice = alpha, h, loss
                break
        if choice is None:  # alpha=0 MUST be eligible after valid prestate
            raise ValueError("G29_NO_SAFE_ALPHA")
        alpha, head, retained = choice
        if (retained - baseline > MAX_DRIFT + 1e-12
                or head.steps != ph[index].steps):
            raise ValueError("G29_RETENTION_OR_STEPS")
        # The newly observed training row is consulted ONLY AFTER alpha choice.
        frozen_new = _new_brier(bh[index], index, outcome, prior)
        projected_new = _new_brier(head, index, outcome, prior)
        full_new = _new_brier(ph[index], index, outcome, prior)
        if any(not isfinite(x) or x < 0 or x > 1
               for x in (frozen_new, projected_new, full_new)):
            raise ValueError("G29_POSTFIT_PROBE")
        records[name] = {
            "alpha": alpha,
            "anchor_old_brier": baseline,
            "frozen_old_drift": old_before - baseline,
            "full_old_drift": full_loss - baseline,
            "projected_old_drift": retained - baseline,
            "new_witness_frozen_postfit_brier": frozen_new,
            "new_witness_projected_postfit_brier": projected_new,
            "new_witness_full_postfit_brier": full_new,
            "changed_trainable_parameters": _weights(head) != _weights(bh[index]),
            "steps_from_prestate": head.steps - bh[index].steps,
        }
        selected_heads.append(head)

    if tuple(_inspect(m)[2] for m in (anchor, before, after)) != (ap, bp, pp):
        raise ValueError("G29_MUTATED_SOURCE")
    tnames = ("direct_transition", "temporal_transition")
    positive_both = all(records[name]["alpha"] > 0
                        and records[name]["changed_trainable_parameters"]
                        for name in tnames)
    projected_new = sum(records[n]["new_witness_projected_postfit_brier"]
                        for n in tnames) / 2
    frozen_new = sum(records[n]["new_witness_frozen_postfit_brier"]
                     for n in tnames) / 2
    report = {
        "gate": "G29_POST_WITNESS_BOUNDED_PLASTICITY_DEV",
        "source_pre_sha256": bp,
        "source_after_sha256": pp,
        "old_ledger_sha256": digest(canonical(old)),
        "old_witnesses": len(old),
        "native_continuation_unchanged": True,
        "frozen_alphas": list(ALPHAS_DESCENDING),
        "old_comparison_limit": MAX_DRIFT,
        "heads": records,
        "all_old_heads_within_comparison": all(
            r["projected_old_drift"] <= MAX_DRIFT + 1e-12
            for r in records.values()),
        "both_transition_heads_nonzero": positive_both,
        "transition_mean_next_postfit_brier_better_than_frozen":
            projected_new < frozen_new - 1e-12,
        "next_event_label_used_to_select_alpha": False,
        "new_event_is_previously_consumed_training_row": True,
        "source_world_actions": 0,
        "official_checkpoint": False,
        "scientific_pass": False,
    }
    return tuple(selected_heads), report


def summarize_four_frozen_samples(samples):
    """Frozen >=3/4 viability rule; report NO_GO without changing evidence."""
    fixed = (1, 32, 33, 64)
    if type(samples) is not list or len(samples) != 4 or [
            s.get("ordinal") for s in samples] != list(fixed):
        raise ValueError("G29_SAMPLE_ORDINALS")
    if any(not s["analysis"]["all_old_heads_within_comparison"]
           for s in samples):
        raise ValueError("G29_RETENTION_BREACH")
    both = sum(s["analysis"]["both_transition_heads_nonzero"] for s in samples)
    fit = sum(s["analysis"][
        "transition_mean_next_postfit_brier_better_than_frozen"] for s in samples)
    return {
        "gate": "G29_SOURCE_CONSUMED_BOUNDED_PLASTICITY_COMPARISON",
        "sample_ordinals": list(fixed),
        "candidate_arm": "full_native_and_four_head_then_retention_projection",
        "controls": ["same_native_with_full_four_head_update",
                     "same_native_with_preupdate_four_head_weights"],
        "samples": samples,
        "old_memory_retention_pass_count": 4,
        "two_transition_heads_positive_update_count": both,
        "projected_postfit_better_than_frozen_transition_count": fit,
        "development_classification": (
            "DEV_MECHANISM_PROMISING"
            if both >= 3 and fit >= 3 else "DEV_MIXED_OR_NO_GO"),
        "held_test_count": 0,
        "new_world_actions": 0,
        "scientific_pass": False,
        "owner_admission": False,
        "deployment": "NONE",
    }
