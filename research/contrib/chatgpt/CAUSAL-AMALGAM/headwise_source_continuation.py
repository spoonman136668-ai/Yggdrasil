"""G28: source-pinned, research-only one-witness JEPA continuation receipt.

This is NOT an official native v2 checkpoint or independent learner. It uses
the existing native+four-head update method and only the previously consumed,
SHA-pinned selection-dev-01 witness trace. Every cold readback independently
reconstructs the source-fitted v1 proposal and its G26 selected head capsule.
No new world/source calls, owner admission or scientific first use.
"""
import json
from math import isfinite

from four_head_retention import audit_old_heads
from headwise_capsule import restore_capsule, _saved
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

SCHEMA = "yggdrasil.amalgam.dev-source-replay-continuation.v1"
ORIGINAL_TRACE_SHA256 = "36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114"
SAMPLE_ORDINALS = (1, 32, 33, 64)
MAX_BYTES = 32 * 1024 * 1024
FIELDS = {
    "schema", "sample_ordinal", "next_ordinal", "trace_sha256",
    "anchor_sha256", "current_sha256", "proposal_sha256",
    "capsule_sha256", "next_packet_sha256", "native_after_sha256",
    "heads_after_sha256", "core_after_sha256", "core_after_ascii",
    "owner_authorized", "official_native_checkpoint", "scientific_pass"
}


def _read_trace(raw):
    if type(raw) is not bytes or digest(raw) != ORIGINAL_TRACE_SHA256:
        raise ValueError("G28_FROZEN_TRACE_PIN")
    records = json.loads(raw)
    if type(records) is not list or len(records) != 96:
        raise ValueError("G28_TRACE_LENGTH")
    return records


def _next_event(records, sample_ordinal):
    if type(sample_ordinal) is not int or sample_ordinal not in SAMPLE_ORDINALS:
        raise ValueError("G28_FROZEN_ORDINAL")
    event = records[sample_ordinal]  # original sample is one-based
    if (type(event) is not dict or type(event.get("id")) is not str
            or type(event.get("views")) is not list or len(event["views"]) != 2
            or type(event.get("row")) is not dict
            or set(event["row"]) != {"s1", "x1", "s2", "x2", "y"}
            or event.get("phase") != sample_ordinal // 32):
        raise ValueError("G28_PUBLIC_EVENT")
    views = tuple(tuple(v) for v in event["views"])
    if (any(type(v) is not tuple or len(v) != 2 or
            any(type(bit) is not int or bit not in (0, 1) for bit in v)
            for v in views)
            or views[0][0] != views[1][0]
            or event["row"]["s1"] != views[0][0]
            or any(type(x) is not int or x not in (0, 1)
                   for x in event["row"].values())):
        raise ValueError("G28_EVENT_BITS")
    packet = digest(canonical([event["id"], views, event["row"]]))
    return event["id"], views, event["row"], packet


def _derive(capsule_raw, capsule_pin, anchor, current, proposal,
            source_trace_raw, sample_ordinal, parents):
    if any(type(m) is not NativeCausalAmalgam for m in (anchor, current, proposal)):
        raise ValueError("G28_NATIVE_SOURCE_REQUIRED")
    prior_bytes = tuple(m.checkpoint() for m in (anchor, current, proposal))
    records = _read_trace(source_trace_raw)
    identifier, views, row, packet = _next_event(records, sample_ordinal)
    if (len(proposal.native._episode_reader()._ledger) -
            len(anchor.native._episode_reader()._ledger) != sample_ordinal):
        raise ValueError("G28_ORIGINAL_SOURCE_ORDINAL")
    source = NativeCausalAmalgam.restore(
        prior_bytes[2], digest(prior_bytes[2]), **parents)
    heads, proof = restore_capsule(
        capsule_raw, capsule_pin, anchor, current, source)
    if not proof["selected_head_bytes_recomputed"]:
        raise ValueError("G28_G26_SOURCE_RECOMPUTE")
    # Research-only reconstitution of the same existing NativeCausalAmalgam.
    # Not promoted or passed to its official source-equivalent v1 restorer.
    selected = NativeCausalAmalgam(
        source.native, tuple(h.clone() for h in heads),
        source._native_parent, source._specialist_parent)
    original = selected.checkpoint()
    before_steps = tuple(h.steps for h in selected._heads)
    after = selected.observe_experience(
        identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=packet)
    if (after is selected or len(after.native._episode_reader()._ledger)
            != len(selected.native._episode_reader()._ledger) + 1
            or after.native._episode_reader()._ledger[:-1]
            != selected.native._episode_reader()._ledger
            or tuple(h.steps - before for h, before in
                     zip(after._heads, before_steps, strict=True)) != (3, 3, 3, 3)):
        raise ValueError("G28_REAL_NATIVE_ONE_WITNESS_UPDATE")
    if after.observe_experience(
            identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
            packet_sha256=packet) is not after:
        raise ValueError("G28_DUPLICATE_NOT_IDEMPOTENT")
    # The native subsystem must match a regular source-fitted v1 continuation.
    reference = source.observe_experience(
        identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=packet)
    if reference.native.checkpoint() != after.native.checkpoint():
        raise ValueError("G28_NATIVE_CONTINUATION_DIVERGED")
    if selected.checkpoint() != original:
        raise ValueError("G28_SELECTED_PARENT_MUTATED")
    if tuple(m.checkpoint() for m in (anchor, current, proposal)) != prior_bytes:
        raise ValueError("G28_SOURCE_INPUT_MUTATED")
    raw_after = after.checkpoint()
    record = {
        "schema": SCHEMA, "sample_ordinal": sample_ordinal,
        "next_ordinal": sample_ordinal + 1,
        "trace_sha256": ORIGINAL_TRACE_SHA256,
        "anchor_sha256": digest(prior_bytes[0]),
        "current_sha256": digest(prior_bytes[1]),
        "proposal_sha256": digest(prior_bytes[2]),
        "capsule_sha256": capsule_pin,
        "next_packet_sha256": packet,
        "native_after_sha256": digest(after.native.checkpoint()),
        "heads_after_sha256": digest(canonical([_saved(h) for h in after._heads])),
        "core_after_sha256": digest(raw_after),
        "core_after_ascii": raw_after.decode("ascii"),
        "owner_authorized": False,
        "official_native_checkpoint": False,
        "scientific_pass": False,
    }
    return record, after


def seal_consumed_continuation(capsule_raw, capsule_pin, anchor, current,
                               proposal, source_trace_raw, sample_ordinal, *,
                               native_parent, native_pin, donor_parent, donor_pin):
    record, after = _derive(
        capsule_raw, capsule_pin, anchor, current, proposal,
        source_trace_raw, sample_ordinal,
        dict(native_parent=native_parent, native_pin=native_pin,
             donor_parent=donor_parent, donor_pin=donor_pin))
    raw = canonical(record)
    if not 0 < len(raw) <= MAX_BYTES:
        raise ValueError("G28_RESEARCH_BYTES")
    return raw, digest(raw), after


def recover_consumed_continuation(raw, expected_pin, capsule_raw, capsule_pin,
                                  anchor, current, proposal, source_trace_raw,
                                  sample_ordinal, *,
                                  native_parent, native_pin, donor_parent, donor_pin):
    if (type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES
            or type(expected_pin) is not str or digest(raw) != expected_pin):
        raise ValueError("G28_ENVELOPE_PIN")
    try:
        item = json.loads(raw.decode("ascii"))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ValueError("G28_ENVELOPE_JSON") from exc
    if (type(item) is not dict or set(item) != FIELDS
            or item.get("schema") != SCHEMA
            or item.get("sample_ordinal") != sample_ordinal
            or item.get("next_ordinal") != sample_ordinal + 1
            or item.get("trace_sha256") != ORIGINAL_TRACE_SHA256
            or item.get("owner_authorized") is not False
            or item.get("official_native_checkpoint") is not False
            or item.get("scientific_pass") is not False
            or canonical(item) != raw):
        raise ValueError("G28_ENVELOPE_SCHEMA")
    rebuilt, restored = _derive(
        capsule_raw, capsule_pin, anchor, current, proposal,
        source_trace_raw, sample_ordinal,
        dict(native_parent=native_parent, native_pin=native_pin,
             donor_parent=donor_parent, donor_pin=donor_pin))
    if rebuilt != item or canonical(rebuilt) != raw:
        raise ValueError("G28_SOURCE_RECOMPUTE_MISMATCH")
    if restored.checkpoint() != item["core_after_ascii"].encode("ascii"):
        raise ValueError("G28_COLD_CORE_MISMATCH")
    return restored, {
        "schema": "yggdrasil.amalgam.dev-one-witness-recovery.v1",
        "sample_ordinal": sample_ordinal,
        "next_ordinal": sample_ordinal + 1,
        "archive_source_verified": True,
        "source_recomputed": True,
        "original_native_update_reused": True,
        "after_core_sha256": item["core_after_sha256"],
        "after_native_sha256": item["native_after_sha256"],
        "after_head_sha256": item["heads_after_sha256"],
        "research_bytes": len(raw),
        "official_native_checkpoint": False,
        "new_world_actions": 0,
        "scientific_pass": False,
        "deployment": "NONE",
    }


def historical_retention(anchor, continued, cold):
    """Never a held score: exposes OLD trained head drift as diagnosed, not gated."""
    report = audit_old_heads(anchor, continued, cold)
    return {
        "classification": report["disposition"],
        "old_witnesses": report["old_witness_count"],
        "old_brier_drift": {
            name: values["old_brier_drift"]
            for name, values in report["heads"].items()
        },
        "all_within_existing_0p02_bound": all(
            x["within_existing_quine_comparison"]
            for x in report["heads"].values()),
        "already_consumed_not_held": True,
        "scientific_pass": False,
    }
