"""Read-only local checkpoint inventory for the existing Yggdrasil lineage.

Does not execute a model, import a learner, read hidden source state, modify
checkpoints, attest an owner, accept science, or authorize continuation.
Prints only bounded metadata. Owner must separately authenticate provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

AMALGAM = "yggdrasil.ckad.native-causal-amalgam.v1"
PYC1 = b"YPC1"
MAX_BYTES = 32 * 1024 * 1024


def require(ok, code):
    if not ok:
        raise ValueError("YGG_LINEAGE01_CUSTODY_" + code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(value):
    return type(value) is str and len(value) == 64 and all(
        c in "0123456789abcdef" for c in value
    )


def unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "DUPLICATE_KEY")
        out[key] = value
    return out


def parse_canonical(raw):
    try:
        obj = json.loads(raw.decode("ascii"), object_pairs_hook=unique,
                         parse_constant=lambda _: require(False, "NONFINITE"))
        reproduced = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=True, allow_nan=False).encode("ascii")
    except (UnicodeError, json.JSONDecodeError, TypeError, OverflowError) as exc:
        raise ValueError("YGG_LINEAGE01_CUSTODY_INVALID_JSON") from exc
    require(reproduced == raw, "NONCANONICAL_JSON")
    return obj


def inspect(raw, expected_sha256=None):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES, "SIZE_OR_TYPE")
    actual = sha(raw)
    require(expected_sha256 is None or pin(expected_sha256),
            "EXPECTED_DIGEST_FORMAT")
    require(expected_sha256 is None or actual == expected_sha256,
            "EXPECTED_DIGEST_MISMATCH")
    common = {
        "schema": "yggdrasil.lineage01.local-custody-inventory.v1",
        "checkpoint_sha256": actual,
        "checkpoint_bytes": len(raw),
        "checkpoint_digest_matches_supplied_pin": (
            True if expected_sha256 is not None else "NOT_SUPPLIED"),
        "owner_authentication": "UNVERIFIED",
        "source_lease": "UNVERIFIED",
        "functional_retention": "UNVERIFIED",
        "scientific_improvement": "UNVERIFIED",
        "continuation_authorized": False,
        "training_executed": False,
    }
    if raw.startswith(PYC1):
        require(len(raw) == 164 and sha(raw[:-32]).encode("ascii") ==
                raw[-32:].hex().encode("ascii"), "PYC1_INTEGRITY")
        counts = struct.unpack(">64H", raw[4:-32])
        return {
            **common,
            "format": "PYC1_EXPLICIT_MEMORY",
            "witnessed_episode_ledger": "NOT_PRESENT_IN_FORMAT",
            "total_observed_counter_increments": sum(counts),
            "nonzero_counter_cells": sum(value > 0 for value in counts),
            "canonical_cumulative_model_identified": False,
        }
    data = parse_canonical(raw)
    require(type(data) is dict and set(data) == {
        "schema", "native_ascii", "native_parent_sha256",
        "specialist_parent_sha256", "action_heads", "temporal_heads",
    } and data["schema"] == AMALGAM, "AMALGAM_SCHEMA")
    require(pin(data["native_parent_sha256"]) and
            pin(data["specialist_parent_sha256"]), "PARENT_PINS")
    heads = data["action_heads"]
    temporal = data["temporal_heads"]
    require(type(heads) is list and type(temporal) is list and
            len(heads) == 2 and len(temporal) == 2, "SPECIALIST_SHAPE")
    for i, head in enumerate(heads + temporal):
        require(type(head) is dict and head.get("kind") ==
                ("transition" if i % 2 == 0 else "reward") and
                type(head.get("steps")) is int and
                0 <= head["steps"] <= 100000, "SPECIALIST_STEPS")
    native_ascii = data["native_ascii"]
    require(type(native_ascii) is str, "NATIVE_ASCII_TYPE")
    native_raw = native_ascii.encode("ascii")
    native = parse_canonical(native_raw)
    require(type(native) is dict and
            native.get("schema") == "yggdrasil.ckad.native-cumulative-learner.v5",
            "NATIVE_SCHEMA")
    # This probe checks only the native witnessed-episode subledger, not all
    # numeric weights or their source-equivalence. A full restore is separate.
    experience_ascii = native.get("experience_ascii")
    require(type(experience_ascii) is str, "EXPERIENCE_MISSING")
    experience = parse_canonical(experience_ascii.encode("ascii"))
    require(type(experience) is dict and type(experience.get("episodes")) is list
            and type(experience.get("state_sha256")) is str and
            pin(experience["state_sha256"]), "EPISODE_SCHEMA")
    seen = set()
    episodes = experience["episodes"]
    require(len(episodes) <= 1152, "EPISODE_CAPACITY")
    for event in episodes:
        require(type(event) is list and len(event) == 6 and pin(event[0]),
                "EPISODE_ROW")
        require(event[0] not in seen, "DUPLICATE_EPISODE")
        seen.add(event[0])
        views = event[1]
        require(type(views) is list and len(views) == 2 and all(
            type(view) is list and len(view) == 2 and all(
                type(bit) is int and bit in (0, 1) for bit in view
            ) for view in views), "EPISODE_PUBLIC_VIEWS")
        require(all(type(bit) is int and bit in (0, 1)
                    for bit in event[2:]), "EPISODE_PUBLIC_BITS")
    require(all(head["steps"] % 3 == 0 for head in heads + temporal),
            "SPECIALIST_STEP_MULTIPLE")
    return {
        **common,
        "format": "EXPERIMENTAL_AMALGAM_V1",
        "native_sha256": sha(native_raw),
        "native_parent_sha256": data["native_parent_sha256"],
        "specialist_parent_sha256": data["specialist_parent_sha256"],
        "witnessed_episodes": len(episodes),
        "witnessed_ledger_sha256": sha(json.dumps(
            episodes, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True).encode("ascii")),
        "shadow_specialist_steps": [head["steps"] for head in heads + temporal],
        "source_equivalence_replay": "NOT_EXECUTED",
        "canonical_cumulative_model_identified": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--expected-sha256", default=None)
    args = parser.parse_args(argv)
    try:
        # No writes. No checkpoint bytes/paths are emitted to stdout.
        require(args.checkpoint.is_file(), "NO_FILE")
        require(args.checkpoint.stat().st_size <= MAX_BYTES, "SIZE")
        report = inspect(args.checkpoint.read_bytes(), args.expected_sha256)
    except (ValueError, OSError, UnicodeError) as exc:
        print("YGG_LINEAGE01_CUSTODY_UNVERIFIED " +
              type(exc).__name__ + ": " + str(exc).splitlines()[0],
              file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
