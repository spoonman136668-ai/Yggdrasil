"""G26 source-bound, RESEARCH-ONLY cold capsule for G25 blended JEPA heads.

The capsule does not authenticate its own origins. Reopening requires original
independently source-restored anchor/current/proposed checkpoints: the complete
G25 selector and every chosen weight are reconstructed independently.

This does NOT change NativeCausalAmalgam.restore, admit a canonical learner,
or demonstrate autonomous/persistent scientific memory gain.
"""
import json

from yggdrasil.native_context_basis import canonical, digest
from four_head_retention import _inspect, HEAD_NAMES
from headwise_consolidation import _blend_head, assess_bounded_blend

SCHEMA = "yggdrasil.amalgam.dev-headwise-capsule.v1"
MAX_CAPSULE_BYTES = 262144
CAPSULE_KEYS = {
    "schema", "source", "head_order", "alpha_by_head", "selected_head_data",
    "g25_analysis_sha256", "canonical_model_restored", "scientific_pass",
}
SOURCE_KEYS = {
    "anchor_checkpoint_sha256", "current_checkpoint_sha256",
    "proposed_checkpoint_sha256", "old_ledger_sha256",
    "proposed_event_sha256",
}


def _saved(head):
    # Direct/temporal source-validated head architecture, step counts and
    # double-precision values. Do not serialize host wrappers or a new native.
    return head.as_data() if hasattr(head, "as_data") else head.data()


def seal_capsule(anchor, current, proposed):
    """Serialize fixed-size four-head shadow proposal, NEVER a native checkpoint."""
    result = assess_bounded_blend(anchor, current, proposed)
    old_heads, _, anchor_pin = _inspect(anchor)
    _, _, current_pin = _inspect(current)
    new_heads, new_events, proposed_pin = _inspect(proposed)
    if len(new_events) == 0:
        raise ValueError("G26_MISSING_PUBLIC_EVENT")
    alpha = {}
    states = []
    for index, name in enumerate(HEAD_NAMES):
        selected = result["heads"][name]["selected_alpha"]
        if type(selected) is not float:
            raise ValueError("G26_ALPHA_TYPE")
        blended = _blend_head(old_heads[index], new_heads[index], selected)
        alpha[name] = selected
        states.append(_saved(blended))
    source = {
        "anchor_checkpoint_sha256": anchor_pin,
        "current_checkpoint_sha256": current_pin,
        "proposed_checkpoint_sha256": proposed_pin,
        "old_ledger_sha256": result["old_ledger_sha256"],
        "proposed_event_sha256": digest(canonical(new_events[-1])),
    }
    record = {
        "schema": SCHEMA,
        "source": source,
        "head_order": list(HEAD_NAMES),
        "alpha_by_head": alpha,
        "selected_head_data": states,
        "g25_analysis_sha256": digest(canonical(result)),
        "canonical_model_restored": False,
        "scientific_pass": False,
    }
    raw = canonical(record)
    if not (0 < len(raw) <= MAX_CAPSULE_BYTES):
        raise ValueError("G26_CAPSULE_BYTE_BUDGET")
    return raw, digest(raw)


def restore_capsule(raw, expected_sha256, anchor, current, proposed):
    """Source-bound cold rehydration; refuses even rehashed malicious payloads."""
    if (type(raw) is not bytes or not (0 < len(raw) <= MAX_CAPSULE_BYTES)
            or type(expected_sha256) is not str or len(expected_sha256) != 64
            or digest(raw) != expected_sha256):
        raise ValueError("G26_CAPSULE_PIN")
    try:
        record = json.loads(raw.decode("ascii"))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ValueError("G26_CAPSULE_JSON") from exc
    if (type(record) is not dict or set(record) != CAPSULE_KEYS
            or record.get("schema") != SCHEMA
            or type(record.get("source")) is not dict
            or set(record["source"]) != SOURCE_KEYS
            or type(record.get("head_order")) is not list
            or record["head_order"] != list(HEAD_NAMES)
            or type(record.get("alpha_by_head")) is not dict
            or list(record["alpha_by_head"]) != sorted(HEAD_NAMES)
            or type(record.get("selected_head_data")) is not list
            or len(record["selected_head_data"]) != 4
            or record.get("canonical_model_restored") is not False
            or record.get("scientific_pass") is not False
            or canonical(record) != raw):
        raise ValueError("G26_CAPSULE_SCHEMA")
    # A capsule SHA alone is NOT provenance: reconstruct the identical
    # source-authorized original proposal and its frozen G25 selector.
    independently_recomputed, independent_pin = seal_capsule(
        anchor, current, proposed)
    if independently_recomputed != raw or independent_pin != expected_sha256:
        raise ValueError("G26_SOURCE_RECOMPUTE_MISMATCH")
    old_heads, _, _ = _inspect(anchor)
    proposed_heads, _, _ = _inspect(proposed)
    restored = []
    for index, name in enumerate(HEAD_NAMES):
        alpha = record["alpha_by_head"][name]
        if type(alpha) is not float:
            raise ValueError("G26_ALPHA_TYPE")
        head = _blend_head(old_heads[index], proposed_heads[index], alpha)
        if canonical(_saved(head)) != canonical(record["selected_head_data"][index]):
            raise ValueError("G26_HEAD_STATE_MISMATCH")
        restored.append(head)
    return tuple(restored), {
        "schema": "yggdrasil.amalgam.dev-headwise-cold-receipt.v1",
        "capsule_sha256": expected_sha256,
        "capsule_bytes": len(raw),
        "source_checkpoint_pins_verified": True,
        "source_ledger_recomputed": True,
        "selected_head_bytes_recomputed": True,
        "head_count": len(restored),
        "canonical_native_model_restored": False,
        "official_source_equivalent_restore_supported": False,
        "new_training": False,
        "source_actions": 0,
        "scientific_pass": False,
    }
