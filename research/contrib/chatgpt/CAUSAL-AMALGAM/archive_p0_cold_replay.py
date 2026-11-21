"""Restore original archived experimental P0 and check source-free Quine replay.

This is not owner-controlled restore, learned selector qualification or science.
The joint file and its two trained parents are pinned to original CI artifacts.
No world, source, first-use, weight update or live model is executed.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from specialist_selection import SpecialistSelection
import quine_retention as guard
from four_head_retention import (HEAD_NAMES, audit_old_heads,
                                 assess_one_witness_head_update)
from headwise_consolidation import assess_bounded_blend, _new_brier
from headwise_capsule import seal_capsule, restore_capsule
from headwise_shadow_readout import materialize_research_readout
from two_witness_retention import (
    assess_two_witness_source, summarize_frozen_two_witnesses,
    protect_immediate_memory, summarize_g32,
)
from fine_step_plasticity import (
    evaluate_fine_steps, summarize_fine_samples,
)
from post_witness_projection import (
    assess_one_more_witness, summarize_four_frozen_samples,
)
from headwise_source_continuation import (
    SAMPLE_ORDINALS, seal_consumed_continuation,
    recover_consumed_continuation, historical_retention,
)
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_context_basis import digest

PROTOCOL = HERE / "selection_protocol_dev.json"
EXPECTED_NATIVE = "5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d"
EXPECTED_LEDGER = "55697acbbe953b5cf6878cecfd3286b068f665fc3c6f78334d241466c4beb274"
EXPECTED_JOINT = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
EXPECTED_EPISODES = 1025
EXPECTED_VIEWS = 8
MODES = {"native": 0, "direct": 1, "temporal": 2}
# Frozen before G24 diagnostics; original A→B→A 32/32/32 consumed phases.
SHADOW_ORDINALS = (1, 8, 32, 33, 64, 65, 96)
# Frozen G25 five original previously-consumed witness locations.
CONSOLIDATION_ORDINALS = (1, 32, 33, 64, 96)


def checked(directory, name, pin):
    """Read pinned original artifact members; refuse substitutions."""
    content = (directory / name).read_bytes()
    if sha256(content).hexdigest() != pin:
        raise ValueError("P0_ARCHIVE_MEMBER_PIN_MISMATCH:" + name)
    return content


def route_evidence(mode):
    """Artificial routing *fixture*; never presented as learned selector state."""
    if mode == "native":
        return {}
    if mode not in ("direct", "temporal"):
        raise ValueError("Unknown bounded routing fixture")
    sign = 1 if mode == "direct" else -1
    value = (Fraction(sign, 8), Fraction(-sign, 8))
    # Existing public two-stage policy addresses: 4 first-stage, 16 terminal.
    keys = (
        [(context, first) for context, first in product((0, 1), repeat=2)]
        + list(product((0, 1), repeat=4))
    )
    return {key: (value,) * 4 for key in keys}


def restore_core(directory, protocol):
    native = checked(directory, protocol["native_name"], protocol["native_sha256"])
    donor_raw = checked(directory, protocol["donor_name"], protocol["donor_sha256"])
    donor = json.loads(donor_raw)
    joint = checked(directory, protocol["joint_name"], protocol["joint_sha256"])
    system = NativeCausalAmalgam.restore(
        joint, protocol["joint_sha256"],
        native_parent=native, native_pin=protocol["native_sha256"],
        donor_parent=donor["state_ascii"].encode("ascii"),
        donor_pin=donor["state_sha256"],
    )
    if system.checkpoint() != joint:
        raise ValueError("P0_ARCHIVE_JOINT_RESTORE_DRIFT")
    if digest(system.native.checkpoint()) != EXPECTED_NATIVE:
        raise ValueError("P0_ARCHIVE_NATIVE_DRIFT")
    ledger = system.native._episode_reader()._ledger
    from yggdrasil.native_context_basis import canonical
    if len(ledger) != EXPECTED_EPISODES or digest(canonical(ledger)) != EXPECTED_LEDGER:
        raise ValueError("P0_ARCHIVE_LEDGER_DRIFT")
    return system


def make_policy(system, mode):
    policy = SpecialistSelection(
        system, window=16, minimum_count=4,
        minimum_gain=Fraction(1, 100), enable_reward=True,
        evidence=route_evidence(mode),
    )
    if mode != "native":
        for key in policy._evidence:
            if policy.selection(((key[0], 0), (key[0], 1)), key[1], *key[2:]) != MODES[mode]:
                raise ValueError("P0_ARCHIVE_ROUTING_FIXTURE_DRIFT")
    return policy



def summarize_shadow(samples):
    """Reject malformed samples; this is NOT acceptance of a repaired learner."""
    if type(samples) is not list or len(samples) != len(SHADOW_ORDINALS):
        raise ValueError("P0_HEAD_SHADOW_SAMPLE_COUNT")
    failures = 0
    for ordinal, sample in zip(SHADOW_ORDINALS, samples, strict=True):
        if (type(sample) is not dict
                or set(sample) != {"ordinal", "phase", "witness_sha256", "head_guard"}
                or sample["ordinal"] != ordinal
                or sample["phase"] != (ordinal - 1) // 32
                or type(sample["witness_sha256"]) is not str
                or len(sample["witness_sha256"]) != 64):
            raise ValueError("P0_HEAD_SHADOW_ORDINAL_OR_SOURCE")
        advice = sample["head_guard"]
        if (type(advice) is not dict
                or advice.get("schema") != "yggdrasil.amalgam.four-head-one-witness-advice.v1"
                or type(advice.get("passed")) is not bool
                or advice.get("old_ledger_sha256") != EXPECTED_LEDGER
                or advice.get("old_witness_count") != EXPECTED_EPISODES
                or advice.get("anchor_checkpoint_sha256")
                != EXPECTED_JOINT
                or type(advice.get("heads")) is not dict
                or tuple(advice["heads"]) != HEAD_NAMES):
            raise ValueError("P0_HEAD_SHADOW_CUSTODY")
        checks = []
        for name in HEAD_NAMES:
            part = advice["heads"][name]
            if (type(part) is not dict
                    or type(part.get("within_existing_quine_comparison")) is not bool
                    or type(part.get("old_brier_drift")) not in (int, float)):
                raise ValueError("P0_HEAD_SHADOW_HEAD_FIELDS")
            checks.append(part["old_brier_drift"] <= 0.02)
            if part["within_existing_quine_comparison"] != checks[-1]:
                raise ValueError("P0_HEAD_SHADOW_HEAD_CLASSIFICATION")
        if advice["passed"] != all(checks):
            raise ValueError("P0_HEAD_SHADOW_PASS_MISMATCH")
        failures += not advice["passed"]
    return {
        "gate": "P0_CONSUMED_G24_SHADOW_GUARD_SENSITIVITY",
        "fixed_sample_ordinals": list(SHADOW_ORDINALS),
        "shadow_proposals": samples,
        "sample_count": len(samples),
        "shadow_head_only_would_veto_count": failures,
        "shadow_head_only_within_comparison_count": len(samples) - failures,
        "old_witnesses": EXPECTED_EPISODES,
        "replayed_consumed_suffix_witnesses": 96,
        "source_actions": 0,
        "real_vetoes_enforced": 0,
        "new_training": False,
        "counterfactual_new_policy_or_gain_verified": False,
        "owner_approval_verified": False,
        "scientific_pass": False,
    }



def summarize_bounded_consolidation(samples):
    """Exploratory gate only; original source decisions are never counterfactual."""
    if (type(samples) is not list
            or [x.get("ordinal") for x in samples] != list(CONSOLIDATION_ORDINALS)):
        raise ValueError("G25_FROZEN_ORDINALS")
    positive_transition_samples = 0
    observed_transition_fit_improvement = 0
    for sample in samples:
        if (sample.get("phase") != (sample["ordinal"] - 1) // 32
                or type(sample.get("witness_sha256")) is not str
                or len(sample["witness_sha256"]) != 64):
            raise ValueError("G25_SOURCE_SAMPLE_CUSTODY")
        result = sample["blend"]
        if (result.get("schema") != "yggdrasil.amalgam.dev-headwise-blend.v1"
                or result.get("old_witness_count") != EXPECTED_EPISODES
                or result.get("old_ledger_sha256") != EXPECTED_LEDGER
                or result.get("anchor_checkpoint_sha256") != EXPECTED_JOINT
                or result.get("head_count") != 4
                or tuple(result.get("heads", {})) != HEAD_NAMES
                or result.get("official_checkpoint_restore_supported") is not False):
            raise ValueError("G25_BLEND_CUSTODY")
        receipt = sample.get("g26_cold_receipt")
        if (type(receipt) is not dict
                or receipt.get("schema") != "yggdrasil.amalgam.dev-headwise-cold-receipt.v1"
                or receipt.get("source_checkpoint_pins_verified") is not True
                or receipt.get("selected_head_bytes_recomputed") is not True
                or receipt.get("head_count") != 4
                or receipt.get("canonical_native_model_restored") is not False
                or type(receipt.get("capsule_bytes")) is not int
                or not 0 < receipt["capsule_bytes"] <= 262144
                or receipt.get("scientific_pass") is not False):
            raise ValueError("G26_RESEARCH_COLD_RECEIPT_CUSTODY")
        heads = result["heads"]
        if any(
            item.get("selected_alpha") not in (1.0, 0.75, 0.5, 0.25, 0.0)
            or item.get("old_drift", float("inf")) > 0.02 + 1e-12
            for item in heads.values()
        ):
            raise ValueError("G25_OLD_HEAD_BOUND_OR_GRID")
        transitions = (heads["direct_transition"], heads["temporal_transition"])
        if any(item["selected_alpha"] > 0 for item in transitions):
            positive_transition_samples += 1
        if sum(item["new_witness_selected_brier"] for item in transitions) < (
                sum(item["new_witness_frozen_head_brier"] for item in transitions)
                - 1e-12):
            observed_transition_fit_improvement += 1
    promised = (positive_transition_samples >= 3
                and observed_transition_fit_improvement >= 2)
    return {
        "gate": "JEPA_G25_CONSUMED_DEV_BLEND_COMPARISON",
        "sample_ordinals": list(CONSOLIDATION_ORDINALS),
        "samples": samples,
        "sample_count": len(samples),
        "g26_rehydration_count": sum(
            sample["g26_cold_receipt"]["selected_head_bytes_recomputed"]
            for sample in samples),
        "g26_rehydration_bytes_total": sum(
            sample["g26_cold_receipt"]["capsule_bytes"] for sample in samples),
        "positive_transition_alpha_samples": positive_transition_samples,
        "in_sample_transition_fit_better_than_frozen_count": observed_transition_fit_improvement,
        "development_classification": ("DEV_MECHANISM_PROMISING" if promised
                                       else "DEV_MIXED_NO_GO"),
        "source_first_use": False,
        "new_world_actions": 0,
        "real_vetoes_enforced": 0,
        "new_learner_constructed": False,
        "canonical_checkpoint_admitted": False,
        "scientific_pass": False,
    }


def replay_consumed_selector(start, source_directory):
    """Reconstruct selector evidence from an already-consumed 96-event trace.

    This is a source-free historical replay, not new knowledge acquisition.
    The original P0 archive contains no independently authenticated trained
    selector checkpoint; the evidence is derived here from public trace rows.
    """
    from collections import Counter
    from specialist_selection import SpecialistSelection
    # The existing selection_trial module imports Unix-only resource; this
    # portable archive readback needs just its original frozen configuration.
    from yggdrasil.native_context_basis import canonical
    from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

    protocol = json.loads(PROTOCOL.read_bytes())
    evidence = HERE / "selection-dev-01"
    producer = json.loads((evidence / "producer.json").read_bytes())
    report = json.loads((evidence / "audit.json").read_bytes())
    raw_trace = (evidence / "trace.json").read_bytes()
    if digest(raw_trace) != producer["trace_sha256"]:
        raise ValueError("P0_CONSUMED_SELECTOR_TRACE_PIN")
    records = json.loads(raw_trace)
    if (len(records) != 96 or producer["episodes"] != 96
            or producer["parent_sha256"] != protocol["joint_sha256"]
            or report["development"] != "DEV_NO_GO"):
        raise ValueError("P0_CONSUMED_SELECTOR_PROTOCOL")
    original_ledger = start.native._episode_reader()._ledger
    known = {event[0] for event in original_ledger}
    if len(known) != len(original_ledger):
        raise ValueError("P0_CONSUMED_SELECTOR_DUPLICATE_PARENT")

    config = dict(window=protocol["window"],
                  minimum_count=protocol["minimum_count"],
                  minimum_gain=Fraction(protocol["selection_gain"]))
    gate = SpecialistSelection(start, **config)
    counts = Counter()
    shadow = []
    consolidation = []
    g28_retention = []
    g29_projection_samples = []
    g30_fine_samples = []
    g31_two_step_samples = []
    g32_rehearsal_samples = []
    g28_native_by_next = {}
    g31_native_by_second = {}
    original_native_parent = checked(source_directory, protocol["native_name"],
                                     protocol["native_sha256"])
    original_donor = json.loads(checked(
        source_directory, protocol["donor_name"], protocol["donor_sha256"]))
    original_parents = {
        "native_parent": original_native_parent,
        "native_pin": protocol["native_sha256"],
        "donor_parent": original_donor["state_ascii"].encode("ascii"),
        "donor_pin": original_donor["state_sha256"],
    }
    for index, event in enumerate(records):
        identifier, row = event["id"], event["row"]
        views = tuple(tuple(view) for view in event["views"])
        if (identifier in known or len(views) != 2
                or views[0][0] != views[1][0]
                or set(row) != {"s1", "x1", "s2", "x2", "y"}
                or row["s1"] != views[0][0]
                or event["phase"] != index // 32):
            raise ValueError("P0_CONSUMED_SELECTOR_EVENT")
        known.add(identifier)
        actions = (row["x1"],)
        before = gate._forecasts(views, actions)
        origin = gate.selection(views, *actions)
        prediction = event["prediction"]
        if origin != event["origin"] or prediction["selector"] != prediction[
                ("native", "direct", "temporal")[origin]]:
            raise ValueError("P0_CONSUMED_SELECTOR_ROUTING_DRIFT")
        for value, key in zip(before, ("native", "direct", "temporal"), strict=True):
            if abs(round(value * 1_000_000) - prediction[key]) > 1:
                raise ValueError("P0_CONSUMED_SELECTOR_PREDICTION_DRIFT")
        counts[origin] += 1
        previous = gate
        packet = digest(canonical([identifier, views, row]))
        gate = gate.observe_experience(
            identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
            packet_sha256=packet)
        if index + 1 in g28_native_by_next:
            expected = g28_native_by_next.pop(index + 1)
            if digest(gate.system.native.checkpoint()) != expected:
                raise ValueError("G28_ARCHIVE_NATIVE_NEXT_MISMATCH")
        if index + 1 in g31_native_by_second:
            expected = g31_native_by_second.pop(index + 1)
            if digest(gate.system.native.checkpoint()) != expected:
                raise ValueError("G31_ARCHIVE_NATIVE_SECOND_MISMATCH")
        if index + 1 in SHADOW_ORDINALS:
            # Read-only on the SAME authentic consumed trajectory; do not
            # enforce this advisory veto, branch policy or create new trials.
            advice = assess_one_witness_head_update(
                start, previous.system, gate.system)
            shadow.append({
                "ordinal": index + 1,
                "phase": event["phase"],
                "witness_sha256": packet,
                "head_guard": advice,
            })
        if index + 1 in CONSOLIDATION_ORDINALS:
            # G25 source-consumed shadow only. The newly witnessed label is
            # excluded from the frozen old-Brier weight interpolation selector.
            capsule_raw, capsule_pin = seal_capsule(
                start, previous.system, gate.system)
            reconstructed_heads, cold_receipt = restore_capsule(
                capsule_raw, capsule_pin,
                start, previous.system, gate.system)
            if (len(reconstructed_heads) != 4
                    or cold_receipt["canonical_native_model_restored"] is not False
                    or cold_receipt["capsule_bytes"] != len(capsule_raw)):
                raise ValueError("G26_SIDECARE_RECONSTRUCT_FAILED")
            # G27: genuine original native cold restore + G26 heads as
            # *read-only* shadow, preserving the canonical v1 restore fence.
            original_checkpoints = tuple(
                m.checkpoint() for m in (start, previous.system, gate.system))
            readout, g27_receipt = materialize_research_readout(
                capsule_raw, capsule_pin, start, previous.system,
                gate.system, **original_parents)
            seen_views = tuple(dict.fromkeys(
                item[1] for item in start.native._episode_reader()._ledger))
            if len(seen_views) != EXPECTED_VIEWS:
                raise ValueError("G27_PUBLIC_VIEW_COVERAGE")
            policy_queries = 0
            for public in seen_views:
                if readout.plan(public[0]) != gate.system.plan(public[0]):
                    raise ValueError("G27_NATIVE_PLAN_CHANGED")
                for first in (0, 1):
                    values = readout.specialist_forecasts(public, first)
                    if len(values) != 2:
                        raise ValueError("G27_TRANSITION_FORECASTS")
                    policy_queries += 1
                    for state, second in product((0, 1), repeat=2):
                        values = readout.specialist_forecasts(
                            public, first, state, second)
                        if len(values) != 2:
                            raise ValueError("G27_REWARD_FORECASTS")
                        policy_queries += 1
            if (policy_queries != 80
                    or tuple(m.checkpoint() for m in (
                        start, previous.system, gate.system)) != original_checkpoints):
                raise ValueError("G27_COLD_READOUT_INTEGRITY")
            try:
                readout.checkpoint()
            except ValueError as exc:
                if "G27_NOT_AN_OFFICIAL_NATIVE_CHECKPOINT" not in str(exc):
                    raise
            else:
                raise ValueError("G27_UNAUTHORIZED_CHECKPOINT")
            try:
                readout.observe_experience("prohibited", (), {})
            except ValueError as exc:
                if "G27_READ_ONLY_NO_TRAINING" not in str(exc):
                    raise
            else:
                raise ValueError("G27_UNAUTHORIZED_UPDATE")
            if index + 1 in SAMPLE_ORDINALS:
                # G28 never calls the world: this next source-public event
                # is read from the PINNED ALREADY-CONSUMED original trace.
                g28_raw, g28_pin, advanced = seal_consumed_continuation(
                    capsule_raw, capsule_pin, start, previous.system,
                    gate.system, raw_trace, index + 1, **original_parents)
                cold_advanced, g28_receipt = recover_consumed_continuation(
                    g28_raw, g28_pin, capsule_raw, capsule_pin,
                    start, previous.system, gate.system,
                    raw_trace, index + 1, **original_parents)
                if advanced.checkpoint() != cold_advanced.checkpoint():
                    raise ValueError("G28_COLD_CONTINUATION_MISMATCH")
                # A learned witness may legitimately change the native plan.
                # Compare against the SAME source-fitted native continuation,
                # never the PRE-update planner (first CI's harness mistake).
                following = records[index + 1]
                following_views = tuple(tuple(v) for v in following["views"])
                following_packet = digest(canonical([
                    following["id"], following_views, following["row"]]))
                reference_next = gate.system.observe_experience(
                    following["id"], following_views, following["row"],
                    source_sha256=EXPERIENCE_SOURCE,
                    packet_sha256=following_packet)
                if (reference_next is gate.system
                        or reference_next.native.checkpoint()
                           != advanced.native.checkpoint()):
                    raise ValueError("G28_NATIVE_SOURCE_CONTINUATION_DRIFT")
                for public in seen_views:
                    if (advanced.plan(public[0]) != cold_advanced.plan(public[0])
                            or advanced.plan(public[0]) != reference_next.plan(public[0])):
                        raise ValueError("G28_NATIVE_PLAN_DRIFT")
                    for first in (0, 1):
                        if (advanced.specialist_forecasts(public, first)
                                != cold_advanced.specialist_forecasts(public, first)):
                            raise ValueError("G28_FIRST_ACTION_PROBE_DRIFT")
                        for state, second in product((0, 1), repeat=2):
                            if (advanced.specialist_forecasts(
                                    public, first, state, second)
                                    != cold_advanced.specialist_forecasts(
                                    public, first, state, second)):
                                raise ValueError("G28_SECOND_ACTION_PROBE_DRIFT")
                old_report = historical_retention(
                    start, advanced, cold_advanced)
                g28_retention.append({
                    **g28_receipt, "old_historical_retention": old_report,
                    "historically_seen_public_forecast_addresses": 80})
                # G29: same archived historical witness, pure research-only
                # plasticity comparison of FULL vs NO HEAD UPDATE vs bounded.
                # Construct the G25 pre-witness selected state only; no actor.
                before_selected = NativeCausalAmalgam(
                    readout._source.native,
                    tuple(h.clone() for h in readout._heads),
                    readout._source._native_parent,
                    readout._source._specialist_parent)
                frozen_before = before_selected.checkpoint()
                chosen, analysis = assess_one_more_witness(
                    start, before_selected, advanced)
                cold_chosen, cold_analysis = assess_one_more_witness(
                    start, before_selected, cold_advanced)
                from headwise_capsule import _saved as g29_head_bytes
                from yggdrasil.native_context_basis import canonical as g29_canonical
                if (analysis != cold_analysis
                        or g29_canonical([g29_head_bytes(h) for h in chosen])
                        != g29_canonical([g29_head_bytes(h) for h in cold_chosen])
                        or before_selected.checkpoint() != frozen_before):
                    raise ValueError("G29_COLD_PROJECTED_HEADS_DRIFT")
                projected = NativeCausalAmalgam(
                    advanced.native, chosen,
                    advanced._native_parent, advanced._specialist_parent)
                cold_projected = NativeCausalAmalgam(
                    cold_advanced.native, cold_chosen,
                    cold_advanced._native_parent, cold_advanced._specialist_parent)
                if (projected.native.checkpoint() != advanced.native.checkpoint()
                        or projected.checkpoint() != cold_projected.checkpoint()):
                    raise ValueError("G29_NATIVE_OR_COLD_DRIFT")
                post_project_queries = 0
                for public in seen_views:
                    if projected.plan(public[0]) != reference_next.plan(public[0]):
                        raise ValueError("G29_NATIVE_PLAN_CHANGED")
                    for first in (0, 1):
                        if (projected.specialist_forecasts(public, first)
                                != cold_projected.specialist_forecasts(public, first)):
                            raise ValueError("G29_FIRST_FORECAST_MISMATCH")
                        post_project_queries += 1
                        for state, second in product((0, 1), repeat=2):
                            if (projected.specialist_forecasts(
                                    public, first, state, second)
                                    != cold_projected.specialist_forecasts(
                                    public, first, state, second)):
                                raise ValueError("G29_SECOND_FORECAST_MISMATCH")
                            post_project_queries += 1
                if post_project_queries != 80:
                    raise ValueError("G29_FORECAST_COVERAGE")
                g29_projection_samples.append({
                    "ordinal": index + 1,
                    "analysis": analysis,
                    "cold_forecast_queries": post_project_queries,
                    "source_checks": {
                        "parent_capsule_sha256": capsule_pin,
                        "native_next_sha256": g28_receipt["after_native_sha256"],
                        "source_exact_v1_native_replay": True,
                        "new_world_actions": 0,
                    },
                })
                # G30 opt-in: same original source-cold G28 successor,
                # finer fixed alpha grid; selection sees ONLY old witnesses.
                fine_heads, fine_analysis = evaluate_fine_steps(
                    start, before_selected, advanced)
                fine_cold, fine_cold_analysis = evaluate_fine_steps(
                    start, before_selected, cold_advanced)
                if (fine_analysis != fine_cold_analysis
                        or g29_canonical([g29_head_bytes(h) for h in fine_heads])
                        != g29_canonical([g29_head_bytes(h) for h in fine_cold])):
                    raise ValueError("G30_SOURCE_COLD_STEP_DRIFT")
                fine = NativeCausalAmalgam(
                    advanced.native, fine_heads,
                    advanced._native_parent, advanced._specialist_parent)
                fine_reopen = NativeCausalAmalgam(
                    cold_advanced.native, fine_cold,
                    cold_advanced._native_parent, cold_advanced._specialist_parent)
                if (fine.native.checkpoint() != advanced.native.checkpoint()
                        or fine.checkpoint() != fine_reopen.checkpoint()):
                    raise ValueError("G30_NATIVE_OR_COLD_DRIFT")
                seen = 0
                for public in seen_views:
                    if fine.plan(public[0]) != reference_next.plan(public[0]):
                        raise ValueError("G30_NATIVE_PLAN_CHANGED")
                    for first in (0, 1):
                        if (fine.specialist_forecasts(public, first)
                                != fine_reopen.specialist_forecasts(public, first)):
                            raise ValueError("G30_TRANSITION_FORECAST_COLD")
                        seen += 1
                        for state, second in product((0, 1), repeat=2):
                            if (fine.specialist_forecasts(
                                    public, first, state, second)
                                    != fine_reopen.specialist_forecasts(
                                    public, first, state, second)):
                                raise ValueError("G30_REWARD_FORECAST_COLD")
                            seen += 1
                if seen != 80:
                    raise ValueError("G30_FROZEN_PUBLIC_COVERAGE")
                g30_fine_samples.append({
                    "ordinal": index + 1,
                    "analysis": fine_analysis,
                    "cold_forecast_queries": seen,
                    "source_checks": {
                        "native_next_sha256": g28_receipt["after_native_sha256"],
                        "capsule_sha256": capsule_pin,
                        "new_world_actions": 0,
                    },
                })
                # G31 two consecutive source-consumed events. First event
                # is exactly G28/G29/G30; second comes from original PINNED
                # old 96-trace without additional world/actor interaction.
                compared, g31_analysis = assess_two_witness_source(
                    start, before_selected, advanced, projected, fine,
                    analysis, fine_analysis, raw_trace, index + 1)
                cold_compared, g31_cold = assess_two_witness_source(
                    start, before_selected, cold_advanced, cold_projected,
                    fine_reopen, cold_analysis, fine_cold_analysis,
                    raw_trace, index + 1)
                if (g31_analysis != g31_cold
                        or any(compared[arm].checkpoint()
                               != cold_compared[arm].checkpoint()
                               for arm in ("full", "coarse", "fine"))
                        or len(compared) != 4):
                    raise ValueError("G31_SOURCE_COLD_CONTINUATION_DRIFT")
                second_native_sha = g31_analysis["native_second_sha256"]
                # G32: same authentic second already-consumed witness; a new
                # OLD + previous-new-row rehearsal constraint (NO new grid).
                second_from_original = records[index + 2]
                second_views = tuple(tuple(v) for v in second_from_original["views"])
                second_packet = digest(canonical([
                    second_from_original["id"], second_views,
                    second_from_original["row"]]))
                fresh_full = fine.observe_experience(
                    second_from_original["id"], second_views,
                    second_from_original["row"],
                    source_sha256=EXPERIENCE_SOURCE,
                    packet_sha256=second_packet)
                fresh_cold = fine_reopen.observe_experience(
                    second_from_original["id"], second_views,
                    second_from_original["row"],
                    source_sha256=EXPERIENCE_SOURCE,
                    packet_sha256=second_packet)
                if (fresh_full is fine or fresh_cold is fine_reopen
                        or digest(fresh_full.native.checkpoint()) != second_native_sha
                        or fresh_full.checkpoint() != fresh_cold.checkpoint()):
                    raise ValueError("G32_SECOND_SOURCE_PROPOSAL_DRIFT")
                recent_heads, recent_report = protect_immediate_memory(
                    start, before_selected, fine, fresh_full)
                cold_recent_heads, cold_recent_report = protect_immediate_memory(
                    start, before_selected, fine_reopen, fresh_cold)
                from headwise_capsule import _saved as g32_saved_head
                if (recent_report != cold_recent_report
                        or canonical([g32_saved_head(h) for h in recent_heads])
                        != canonical([g32_saved_head(h) for h in cold_recent_heads])):
                    raise ValueError("G32_COLD_SELECTED_HEAD_DRIFT")
                recent = NativeCausalAmalgam(
                    fresh_full.native, recent_heads,
                    fresh_full._native_parent, fresh_full._specialist_parent)
                cold_recent = NativeCausalAmalgam(
                    fresh_cold.native, cold_recent_heads,
                    fresh_cold._native_parent, fresh_cold._specialist_parent)
                if (recent.checkpoint() != cold_recent.checkpoint()
                        or recent.native.checkpoint() != compared["full"].native.checkpoint()):
                    raise ValueError("G32_COLD_OR_NATIVE_PLAN_DRIFT")
                first_fit = sum(
                    fine_analysis["heads"][name]["new_witness_fine_postfit_brier"]
                    for name in ("direct_transition", "temporal_transition"))
                second_fit = sum(
                    recent_report["second_witness_postfit_brier"][name]
                    for name in ("direct_transition", "temporal_transition"))
                two_fit = (first_fit + second_fit) / 4
                two_arm = dict(g31_analysis[
                    "two_row_postfit_mean_transition_brier_by_arm"])
                two_arm["rehearsal"] = two_fit
                # Historical *pseudo*-prequential second-row readout, using
                # pre-second heads. Already-consumed source, NOT held science.
                second_event = fresh_full.native._episode_reader()._ledger[-1]
                first_ledger = fine.native._episode_reader()._ledger
                pre_second = {}
                for arm, first_model in (
                        ("full", advanced), ("coarse", projected),
                        ("fine", fine), ("rehearsal", fine),
                        ("frozen", before_selected)):
                    pre_second[arm] = sum(
                        _new_brier(first_model._heads[pos], pos,
                                   second_event, first_ledger)
                        for pos in (0, 2)) / 2
                g32_rehearsal_samples.append({
                    "ordinal": index + 1,
                    "both_transition_heads_changed_first_fine":
                        all(fine_analysis["heads"][n]["changed_weights"]
                            for n in ("direct_transition", "temporal_transition")),
                    "rehearsal": recent_report,
                    "two_row_postfit_mean_transition_brier": two_arm,
                    "pseudo_prequential_second_witness_brier_by_arm": pre_second,
                    "cold_historical_public_forecast_addresses": 80,
                    "same_native_source_after_two_events": True,
                })
                seen_second = 0
                for public in seen_views:
                    reference_plan = compared["full"].plan(public[0])
                    for arm in ("full", "coarse", "fine", "rehearsal"):
                        model = recent if arm == "rehearsal" else compared[arm]
                        cold_model = (cold_recent if arm == "rehearsal"
                                      else cold_compared[arm])
                        if (model.plan(public[0]) != reference_plan
                                or cold_model.plan(public[0]) != reference_plan):
                            raise ValueError("G31_NATIVE_SECOND_PLAN_DRIFT")
                        for first in (0, 1):
                            if (model.specialist_forecasts(public, first)
                                    != cold_model.specialist_forecasts(public, first)):
                                raise ValueError("G31_TRANSITION_COLD_DRIFT")
                            for state, second in product((0, 1), repeat=2):
                                if (model.specialist_forecasts(
                                        public, first, state, second)
                                        != cold_model.specialist_forecasts(
                                        public, first, state, second)):
                                    raise ValueError("G31_REWARD_COLD_DRIFT")
                    seen_second += 10
                if seen_second != 80:
                    raise ValueError("G31_FROZEN_PUBLIC_PROBE_COVERAGE")
                g31_two_step_samples.append({
                    "ordinal": index + 1,
                    "analysis": g31_analysis,
                    "native_source_verified_after_both_steps": True,
                    "historical_public_cold_address_count_per_arm": seen_second,
                    "original_g26_capsule_sha256": capsule_pin,
                    "new_world_actions": 0,
                })
                g31_native_by_second[index + 3] = second_native_sha
                g28_native_by_next[index + 2] = g28_receipt["after_native_sha256"]
            consolidation.append({
                "ordinal": index + 1,
                "phase": event["phase"],
                "witness_sha256": packet,
                "blend": assess_bounded_blend(
                    start, previous.system, gate.system),
                "g26_cold_receipt": cold_receipt,
                "g27_readonly_receipt": {
                    **g27_receipt, "historical_public_forecast_queries": policy_queries},
            })

    if len(g28_retention) != len(SAMPLE_ORDINALS) or g28_native_by_next:
        raise ValueError("G28_FROZEN_SAMPLES_NOT_COMPLETED")
    if len(g31_two_step_samples) != 4 or g31_native_by_second:
        raise ValueError("G31_FROZEN_TWO_WITNESS_SOURCE_NOT_COMPLETED")
    g29_report = summarize_four_frozen_samples(g29_projection_samples)
    g30_report = summarize_fine_samples(g30_fine_samples)
    g31_report = summarize_frozen_two_witnesses(g31_two_step_samples)
    g32_report = summarize_g32(g32_rehearsal_samples)
    shadow_report = summarize_shadow(shadow)
    consolidation_report = summarize_bounded_consolidation(consolidation)
    checkpoint = gate.system.checkpoint()
    native = gate.system.native.checkpoint()
    if (len(gate.system.native._episode_reader()._ledger) != 1121
            or digest(native) != producer["native_sha256"]
            or [new.steps - old.steps
                for new, old in zip(gate.system._heads, start._heads, strict=True)]
            != producer["head_gradient_steps"]):
        raise ValueError("P0_CONSUMED_SELECTOR_RECONSTRUCTION_DRIFT")

    # Re-open the reconstructed core through the original, existing source-
    # authenticated native+JEPA cold restore. Rebuild the non-persisted selector
    # evidence only from the exact same already-consumed accepted suffix.
    original_native = checked(source_directory, protocol["native_name"],
                              protocol["native_sha256"])
    donor = json.loads(checked(source_directory, protocol["donor_name"],
                               protocol["donor_sha256"]))
    reopened_core = NativeCausalAmalgam.restore(
        checkpoint, digest(checkpoint), native_parent=original_native,
        native_pin=protocol["native_sha256"],
        donor_parent=donor["state_ascii"].encode("ascii"),
        donor_pin=donor["state_sha256"])
    reopened = SpecialistSelection.replay(start, reopened_core, **config)
    if (guard._checkpoint(gate) != guard._checkpoint(reopened)
            or gate.system.checkpoint() != reopened.system.checkpoint()):
        raise ValueError("P0_CONSUMED_SELECTOR_COLD_POLICY_DRIFT")
    policy_check = guard.verify_selector_replay(gate, reopened)
    # Archived 1,025-witness old-task head-only functional retention: compare
    # original P0 to the already-consumed 96-event descendant and its cold clone.
    four_head_retention = audit_old_heads(start, gate.system, reopened_core)
    # Contrast the *original* P0 against its already-consumed negative
    # development descendant: differences are action-policy diagnostics,
    # never a claim that either action's unobserved consequence is correct.
    native_action_drift = guard.diagnose_historical_action_divergence(
        start, gate.system)
    selector_action_drift = guard.diagnose_historical_action_divergence(
        SpecialistSelection(start, **config), gate)
    if (native_action_drift["view_count"] != EXPECTED_VIEWS
            or selector_action_drift["view_count"] != EXPECTED_VIEWS):
        raise ValueError("P0_CONSUMED_SELECTOR_POLICY_VIEW_COVERAGE")
    if (policy_check["readout_witnesses"] != 1121
            or policy_check["policy_queries"] != 80
            or dict(counts) != {0: 96}
            or report["specialist_origin_counts"] != {"0": 64}):
        raise ValueError("P0_CONSUMED_SELECTOR_ORIGINAL_NEGATIVE_DRIFT")
    return {
        "gate": "P0_CONSUMED_SELECTOR_POLICY_REPLAY_PASS",
        "selection_original_development": "DEV_NO_GO",
        "replayed_consumed_events": len(records),
        "prequential_selection_counts": dict(sorted(counts.items())),
        "historical_checkpoint_linux_pin": producer["checkpoint_sha256"],
        "reconstructed_core_sha256": digest(checkpoint),
        "reconstructed_native_sha256": digest(native),
        "linux_exact_core_bytes_required_on_windows": False,
        "policy_check": policy_check,
        "four_head_retention": four_head_retention,
        "shadow_guard_sensitivity": shadow_report,
        "bounded_headwise_consolidation": consolidation_report,
        "g29_post_witness_projection": g29_report,
        "g30_fine_step_plasticity": g30_report,
        "g31_two_witness_memory": g31_report,
        "g32_recent_rehearsal": g32_report,
        "g28_consumed_source_continuation": {
            "gate": "G28_RESEARCH_ONLY_ONE_WITNESS_COLD_CONTINUATION",
            "frozen_sample_ordinals": list(SAMPLE_ORDINALS),
            "source_action_count": 0,
            "new_training_worlds": 0,
            "official_checkpoint_admitted": False,
            "scientific_pass": False,
            "samples": g28_retention,
        },
        "native_action_drift": native_action_drift,
        "selector_action_drift": selector_action_drift,
        "selector_evidence_from_original_public_trace": True,
        "independently_saved_trained_selector_authenticated": False,
        "new_world_actions": 0,
        "fresh_training": False,
        "scientific_pass": False,
        "owner_cold_restore_verified": False,
    }


def run(directory):
    """Archive-only cold replay, no scientific source actions or owner custody."""
    protocol = json.loads(PROTOCOL.read_bytes())
    if protocol["joint_sha256"] != EXPECTED_JOINT:
        raise ValueError("P0_ARCHIVE_PROTOCOL_PIN_MISMATCH")
    original = restore_core(directory, protocol)
    reopened = restore_core(directory, protocol)
    before = original.checkpoint()
    views = tuple(dict.fromkeys(row[1] for row in original.native._episode_reader()._ledger))
    if len(views) != EXPECTED_VIEWS:
        raise ValueError("P0_ARCHIVE_PUBLIC_VIEW_COVERAGE")
    checks = {}
    for mode in MODES:
        first, second = make_policy(original, mode), make_policy(reopened, mode)
        result = guard.verify_selector_replay(first, second)
        if result["readout_witnesses"] != EXPECTED_EPISODES or result["policy_queries"] != 80:
            raise ValueError("P0_ARCHIVE_POLICY_READBACK_COVERAGE")
        checks[mode] = result
    if original.checkpoint() != before or reopened.checkpoint() != before:
        raise ValueError("P0_ARCHIVE_SOURCE_FREE_MUTATION")
    consumed_selector = replay_consumed_selector(original, directory)
    return {
        "consumed_selector": consumed_selector,
        "gate": "P0_ARCHIVED_RESEARCH_COLD_POLICY_READBACK_PASS",
        "experimental_joint_sha256": protocol["joint_sha256"],
        "native_sha256": EXPECTED_NATIVE,
        "ledger_sha256": EXPECTED_LEDGER,
        "witnesses": EXPECTED_EPISODES,
        "seen_public_view_pairs": len(views),
        "modes": checks,
        "selector_routing_fixture_is_trained": False,
        "owner_cold_restore_verified": False,
        "science_first_use": False,
        "source_actions": 0,
        "scientific_pass": False,
        "deployment": "NONE",
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: archive_p0_cold_replay.py EXTRACTED_ARCHIVE_DIR")
    print(json.dumps(run(Path(sys.argv[1])), indent=2, sort_keys=True))
