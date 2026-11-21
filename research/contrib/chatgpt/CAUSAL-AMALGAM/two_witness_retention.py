"""G31: source-bound TWO consecutive historical JEPA continuation comparison.

Already-consumed source events ONLY. Four original start ordinals [1,32,33,64]
and their exact next-two witnesses are immutable; this is an in-sample
development stress test, not new scientific first-use or a native checkpoint.
"""
from math import isfinite

from four_head_retention import HEAD_NAMES, _inspect
from headwise_consolidation import _new_brier, _old_brier, MAX_DRIFT
from post_witness_projection import assess_one_more_witness
from fine_step_plasticity import evaluate_fine_steps, _weight_delta_norm
from headwise_source_continuation import _read_trace
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

STARTS = (1, 32, 33, 64)
TRANSITION_POSITIONS = (0, 2)
ARMS = ("full", "frozen", "coarse", "fine")


def _next_consumed(raw_trace, ordinal, before_ledger):
    """Refuse unknown, skipped, replayed or nonbinary events before updating."""
    if type(ordinal) is not int or ordinal not in STARTS:
        raise ValueError("G31_UNFROZEN_START")
    records = _read_trace(raw_trace)
    # First continuation at original ordinal=start+1 already occurred;
    # second continuation is ordinal=start+2 at zero-based index start+1.
    event = records[ordinal + 1]
    if (type(event) is not dict or set(event) != {
            "id", "views", "row", "phase", "origin", "prediction"}):
        raise ValueError("G31_SOURCE_EVENT_FIELDS")
    identifier = event["id"]
    views = event["views"]
    row = event["row"]
    if (type(identifier) is not str or not identifier
            or type(views) is not list or len(views) != 2
            or type(row) is not dict
            or set(row) != {"s1", "x1", "s2", "x2", "y"}
            or event["phase"] != (ordinal + 1) // 32
            or any(type(v) is not list or len(v) != 2 or
                   any(type(bit) is not int or bit not in (0, 1) for bit in v)
                   for v in views)
            or views[0][0] != views[1][0]
            or type(row["s1"]) is not int or row["s1"] != views[0][0]
            or any(type(v) is not int or v not in (0, 1)
                   for v in row.values())):
        raise ValueError("G31_SOURCE_EVENT_SHAPE")
    if (any(old[0] == identifier for old in before_ledger)
            or len(before_ledger) < 1025 + ordinal + 1):
        raise ValueError("G31_SOURCE_DUPLICATE_OR_GAP")
    views = tuple(tuple(v) for v in views)
    return identifier, views, row, digest(canonical([identifier, views, row]))


def _as_model(updated, heads):
    return NativeCausalAmalgam(
        updated.native, tuple(h.clone() for h in heads),
        updated._native_parent, updated._specialist_parent)


def _score_new(heads, event, before):
    result = {}
    for position, name in enumerate(HEAD_NAMES):
        val = _new_brier(heads[position], position, event, before)
        if not isfinite(val) or val < 0 or val > 1:
            raise ValueError("G31_SECOND_WITNESS_POSTFIT")
        result[name] = val
    return result


def assess_two_witness_source(anchor, original_selected,
                              first_full, first_coarse, first_fine,
                              first_coarse_receipt, first_fine_receipt,
                              raw_trace, ordinal):
    """Continue all matched head arms ONE more exact already-consumed row.

    Models' native ledger advances through its existing observe_experience;
    no actor/world action, no official new checkpoint. Native must be bitwise
    equal for every arm. Head source before/after checks enforce provenance.
    """
    if type(ordinal) is not int or ordinal not in STARTS:
        raise ValueError("G31_FROZEN_ORDINAL")
    models = (anchor, original_selected, first_full, first_coarse, first_fine)
    if any(type(m) is not NativeCausalAmalgam for m in models):
        raise ValueError("G31_SOURCE_NATIVE_REQUIRED")
    originals = tuple(m.checkpoint() for m in models)
    h_anchor, old, _ = _inspect(anchor)
    h_start, base_ledger, _ = _inspect(original_selected)
    _, first_ledger, _ = _inspect(first_full)
    if (len(old) != 1025 or len(base_ledger) != len(old) + ordinal
            or len(first_ledger) != len(base_ledger) + 1
            or base_ledger[:len(old)] != old
            or first_ledger[:len(base_ledger)] != base_ledger):
        raise ValueError("G31_SOURCE_PREFIX_ORDINAL")
    native_first = first_full.native.checkpoint()
    for model in (first_coarse, first_fine):
        h, led, _ = _inspect(model)
        if (led != first_ledger
                or model.native.checkpoint() != native_first):
            raise ValueError("G31_FIRST_NATIVE_DIVERGED")
    identifier, views, row, packet = _next_consumed(
        raw_trace, ordinal, first_ledger)
    full2 = first_full.observe_experience(
        identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=packet)
    coarse_full = first_coarse.observe_experience(
        identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=packet)
    fine_full = first_fine.observe_experience(
        identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=packet)
    if any(updated is parent for updated, parent in (
            (full2, first_full), (coarse_full, first_coarse),
            (fine_full, first_fine))):
        raise ValueError("G31_DUPLICATE_UPDATE")
    native2 = full2.native.checkpoint()
    ledger2 = full2.native._episode_reader()._ledger
    if (len(ledger2) != len(first_ledger) + 1
            or ledger2[:-1] != first_ledger
            or any(m.native.checkpoint() != native2 or
                   m.native._episode_reader()._ledger != ledger2
                   for m in (coarse_full, fine_full))):
        raise ValueError("G31_NEXT_NATIVE_SOURCE_DIVERGED")
    coarse_heads, coarse_receipt2 = assess_one_more_witness(
        anchor, first_coarse, coarse_full)
    fine_heads, fine_receipt2 = evaluate_fine_steps(
        anchor, first_fine, fine_full)
    models2 = {
        "full": full2,
        "coarse": _as_model(coarse_full, coarse_heads),
        "fine": _as_model(fine_full, fine_heads),
        "frozen": _as_model(full2, h_start),
    }
    if (any(m.native.checkpoint() != native2 for m in models2.values())
            or tuple(m.checkpoint() for m in models) != originals):
        raise ValueError("G31_NATIVE_OR_SOURCE_MUTATION")
    if full2.observe_experience(
            identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
            packet_sha256=packet) is not full2:
        raise ValueError("G31_DUPLICATE_NOT_IDEMPOTENT")
    # All four arms: same original next event and previous native context.
    second_scores = {
        name: _score_new(m._heads, ledger2[-1], first_ledger)
        for name, m in models2.items()
    }
    first_scores = {name: {} for name in ARMS}
    for pos in TRANSITION_POSITIONS:
        name = HEAD_NAMES[pos]
        coarse_first = first_coarse_receipt["heads"][name]
        fine_first = first_fine_receipt["heads"][name]
        first_scores["full"][name] = coarse_first[
            "new_witness_full_postfit_brier"]
        first_scores["coarse"][name] = coarse_first[
            "new_witness_projected_postfit_brier"]
        first_scores["fine"][name] = fine_first[
            "new_witness_fine_postfit_brier"]
        first_scores["frozen"][name] = coarse_first[
            "new_witness_frozen_postfit_brier"]
        if abs(first_scores["coarse"][name] -
               fine_first["new_witness_coarse_postfit_brier"]) > 1e-12:
            raise ValueError("G31_PRIOR_COARSE_CONTROL_DRIFT")
    cumulative = {}
    for arm in ARMS:
        two_row = sum(
            first_scores[arm][HEAD_NAMES[p]] +
            second_scores[arm][HEAD_NAMES[p]]
            for p in TRANSITION_POSITIONS) / 4
        if not isfinite(two_row) or two_row < 0 or two_row > 1:
            raise ValueError("G31_NONFINITE_TWO_ROW_FIT")
        cumulative[arm] = two_row
    original_losses = [
        _old_brier(h_anchor[i], i, old) for i in range(4)
    ]
    old_drift = {}
    for arm, model in models2.items():
        old_drift[arm] = {
            name: _old_brier(model._heads[i], i, old) - original_losses[i]
            for i, name in enumerate(HEAD_NAMES)
        }
        if any(not isfinite(v) for v in old_drift[arm].values()):
            raise ValueError("G31_NONFINITE_OLD_RETENTION")
    step2 = {}
    for name in HEAD_NAMES:
        i = HEAD_NAMES.index(name)
        step2[name] = {
            "coarse_alpha": coarse_receipt2["heads"][name]["alpha"],
            "fine_alpha": fine_receipt2["heads"][name]["fine_alpha"],
            "first_fine_alpha": first_fine_receipt["heads"][name]["fine_alpha"],
            "fine_second_weight_l2": _weight_delta_norm(
                models2["fine"]._heads[i], first_fine._heads[i]),
            "fine_first_weight_l2": first_fine_receipt["heads"][name][
                "trainable_weight_l2_change"],
            "fine_final_vs_g26_l2": _weight_delta_norm(
                models2["fine"]._heads[i], h_start[i]),
            "fine_old_brier_drift": old_drift["fine"][name],
            "coarse_old_brier_drift": old_drift["coarse"][name],
            "full_old_brier_drift": old_drift["full"][name],
            "frozen_old_brier_drift": old_drift["frozen"][name],
            "fine_second_postfit_brier": second_scores["fine"][name],
            "coarse_second_postfit_brier": second_scores["coarse"][name],
            "full_second_postfit_brier": second_scores["full"][name],
            "frozen_second_postfit_brier": second_scores["frozen"][name],
        }
    real_both_each = all(
        step2[name]["fine_first_weight_l2"] > 0.0
        and step2[name]["fine_second_weight_l2"] > 0.0
        for name in ("direct_transition", "temporal_transition")
    )
    valid_old = all(v <= MAX_DRIFT + 1e-12
                    for v in old_drift["fine"].values())
    report = {
        "gate": "G31_SOURCE_CONSUMED_TWO_WITNESS_RETENTION_DEV",
        "start_ordinal": ordinal,
        "frozen_pair_ordinals": [ordinal + 1, ordinal + 2],
        "second_original_packet_sha256": packet,
        "selected_g26_before_sha256": digest(originals[1]),
        "full_first_sha256": digest(originals[2]),
        "full_second_sha256": digest(full2.checkpoint()),
        "native_second_sha256": digest(native2),
        "head_results": step2,
        "two_row_postfit_mean_transition_brier_by_arm": cumulative,
        "all_fine_old_heads_within_frozen_bound": valid_old,
        "both_transition_heads_changed_on_both_steps": real_both_each,
        "fine_two_row_better_than_coarse": (
            cumulative["fine"] < cumulative["coarse"] - 1e-12),
        "fine_two_row_better_than_frozen": (
            cumulative["fine"] < cumulative["frozen"] - 1e-12),
        "fine_two_row_not_worse_than_coarse": (
            cumulative["fine"] <= cumulative["coarse"] + 1e-12),
        "source_actions": 0,
        "original_world_replay": "already_consumed_read_only",
        "held_evidence": False,
        "official_native_checkpoint": False,
        "scientific_pass": False,
    }
    return models2, report


def summarize_frozen_two_witnesses(samples):
    if (type(samples) is not list or len(samples) != len(STARTS)
            or [s.get("ordinal") for s in samples] != list(STARTS)):
        raise ValueError("G31_FROZEN_SAMPLE_SET")
    r=[s["analysis"] for s in samples]
    case1=r[0]
    old_all=all(x["all_fine_old_heads_within_frozen_bound"] for x in r)
    case1_real=case1["both_transition_heads_changed_on_both_steps"]
    case1_fit=case1["fine_two_row_better_than_coarse"] and case1[
        "fine_two_row_better_than_frozen"]
    no_worse=all(x["fine_two_row_not_worse_than_coarse"] for x in r)
    return {
        "gate": "G31_ORIGINAL_CONSUMED_TWO_WITNESS_COMPARISON",
        "sample_ordinals": list(STARTS),
        "second_consecutive_source_witnesses": [[n + 1, n + 2]
                                               for n in STARTS],
        "all_fine_old_bounds_met": old_all,
        "case1_both_transition_heads_changed_each_step": case1_real,
        "case1_two_row_better_than_coarse_and_frozen": case1_fit,
        "all_four_fine_two_row_not_worse_than_coarse": no_worse,
        "samples": samples,
        "development_classification": (
            "DEV_TWO_STEP_CONTINUATION_HELPFUL"
            if old_all and case1_real and case1_fit and no_worse
            else "DEV_TWO_STEP_STALL_OR_NO_GO"
        ),
        "protected_new_world_actions": 0,
        "held_source_worlds": 0,
        "official_native_checkpoint_admitted": False,
        "scientific_pass": False,
        "deployment": "NONE",
    }
