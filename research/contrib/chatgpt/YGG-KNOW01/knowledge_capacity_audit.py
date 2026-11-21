"""Read-only audit of existing experimental Amalgam knowledge capacity.

No model imports, writes, owner-state inspection, new observations or training.
The historical archive is caller-supplied and must match an independently
established SHA-256; self-hashed bytes are not source authentication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import zipfile

ARCHIVE_MEMBER = "amalgam-joint-state.json"
JOINT_SCHEMA = "yggdrasil.ckad.native-causal-amalgam.v1"
NATIVE_SCHEMA = "yggdrasil.ckad.native-cumulative-learner.v5"
PROPERTY_SCHEMA = "yggdrasil.ckad.native-property-knowledge.v1"
EPISODE_SCHEMAS = frozenset({
    "yggdrasil.ckad.native-episode-experience.v6",
    "yggdrasil.ckad.native-episode-experience.v5",
})
MAX_ARCHIVE_BYTES = 16 * 1024 * 1024
MAX_JOINT_BYTES = 32 * 1024 * 1024
HEX = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, reason):
    if not condition:
        raise ValueError("YGG_KNOW01_" + reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    value = {}
    for key, val in pairs:
        require(key not in value, "DUPLICATE_JSON_KEY")
        value[key] = val
    return value


def parse(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_JOINT_BYTES,
            "JSON_SIZE")
    try:
        data = json.loads(raw.decode("ascii"), object_pairs_hook=unique,
                          parse_constant=lambda _: require(False, "NONFINITE"))
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False).encode("ascii")
    except (UnicodeError, ValueError, TypeError, OverflowError) as exc:
        raise ValueError("YGG_KNOW01_BAD_JSON") from exc
    require(canonical == raw, "NONCANONICAL_JSON")
    return data


def pin(value):
    return type(value) is str and HEX.fullmatch(value) is not None


def inventory(joint_raw, expected_joint_sha256):
    require(pin(expected_joint_sha256) and
            digest(joint_raw) == expected_joint_sha256, "JOINT_PIN")
    joint = parse(joint_raw)
    require(type(joint) is dict and set(joint) == {
        "schema", "native_ascii", "native_parent_sha256",
        "specialist_parent_sha256", "action_heads", "temporal_heads",
    } and joint["schema"] == JOINT_SCHEMA, "JOINT_SCHEMA")
    require(pin(joint["native_parent_sha256"]) and
            pin(joint["specialist_parent_sha256"]), "PARENT_PINS")
    native_raw = joint["native_ascii"].encode("ascii")
    native = parse(native_raw)
    require(type(native) is dict and native.get("schema") == NATIVE_SCHEMA
            and native.get("accepted_native") is False
            and native.get("scientific_pass") is False,
            "NATIVE_NOT_RESEARCH_V5")
    prop_raw = native["properties_ascii"].encode("ascii")
    prop = parse(prop_raw)
    require(type(prop) is dict and prop.get("schema") == PROPERTY_SCHEMA
            and prop.get("source_mode") == "engineering_fixture_only"
            and prop.get("accepted_native") is False
            and prop.get("scientific_pass") is False,
            "PROPERTY_NOT_SYNTHETIC_RESEARCH")
    entities = prop["entities"]
    bits = prop["context_bits"]
    require(type(entities) is int and 1 <= entities <= 10000 and
            type(bits) is int and 1 <= bits <= 10,
            "PROPERTY_SHAPE")
    try:
        planes = bytes.fromhex(prop["known_value_planes_uint16le"])
    except (TypeError, ValueError) as exc:
        raise ValueError("YGG_KNOW01_PLANES_HEX") from exc
    require(len(planes) == 4 * entities, "PLANES_LENGTH")
    mask_limit = (1 << bits) - 1
    known_bits = 0
    fully_known = 0
    nonzero_entities = 0
    for known, value in struct.iter_unpack("<HH", planes):
        require(known <= mask_limit and value & ~known == 0,
                "UNKNOWN_OR_INVALID_PROPERTY")
        known_bits += known.bit_count()
        fully_known += known == mask_limit
        nonzero_entities += known != 0
    sources = prop["property_sources"]
    require(type(sources) is list and len(sources) <= 16 and
            len(set(sources)) == len(sources) and
            all(pin(src) for src in sources) and
            (known_bits == 0 or bool(sources)),
            "PROPERTY_SOURCE_PINS")
    relations = prop["relation_sources"]
    require(type(relations) is list and len(relations) == 16 and
            all(pin(src) for src in relations), "RELATION_SOURCE_PINS")
    episodes = parse(native["experience_ascii"].encode("ascii"))
    require(type(episodes) is dict and
            episodes.get("schema") in EPISODE_SCHEMAS and
            type(episodes.get("episodes")) is list, "EPISODE_LEDGER")
    heads = joint["action_heads"] + joint["temporal_heads"]
    require(type(joint["action_heads"]) is list and
            type(joint["temporal_heads"]) is list and
            len(joint["action_heads"]) == 2 and
            len(joint["temporal_heads"]) == 2 and
            all(type(x) is dict and type(x.get("steps")) is int
                and x["steps"] >= 0 for x in heads), "HEAD_SHAPE")
    capacity = bits * entities
    require(known_bits <= capacity, "CAPACITY")
    return {
        "schema": "yggdrasil.know01.archived-native-property-inventory.v1",
        "joint_checkpoint_sha256": digest(joint_raw),
        "native_checkpoint_sha256": digest(native_raw),
        "property_checkpoint_sha256": digest(prop_raw),
        "native_properties": known_bits,
        "total_binary_property_positions": capacity,
        "unoccupied_binary_property_positions": capacity - known_bits,
        "fully_known_entities": fully_known,
        "nonempty_entities": nonzero_entities,
        "entity_capacity": entities,
        "property_bits_per_entity": bits,
        "property_source_namespace": prop["source_namespace"],
        "property_source_count": len(sources),
        "nondefault_relation_source_slots": sum(
            source != "0" * 64 for source in relations),
        "retained_native_public_witnesses": len(episodes["episodes"]),
        "trained_specialist_count": len(heads),
        "trained_specialist_steps": [x["steps"] for x in heads],
        "source_mode": "engineering_fixture_only",
        "historical_real_knowledge_graph_joint_verified": False,
        "real_world_causal_grounding": "UNVERIFIED",
        "new_knowledge_ingested": 0,
        "actual_cumulative_owner_checkpoint": "UNVERIFIED",
        "new_training_executed": False,
        "scientific_pass": False,
        "checkpoint_mutated": False,
        "accepted_model_mutated": False,
    }


def archive_inventory(path, archive_sha256, joint_sha256):
    require(pin(archive_sha256) and pin(joint_sha256), "EXPECTED_SHA_FORMAT")
    path = Path(path)
    require(path.is_file() and path.stat().st_size <= MAX_ARCHIVE_BYTES,
            "ARCHIVE_MISSING_OR_OVERSIZE")
    raw = path.read_bytes()
    require(digest(raw) == archive_sha256, "ARCHIVE_PIN")
    with zipfile.ZipFile(path) as bundle:
        items = bundle.infolist()
        require(len(items) <= 8 and len({x.filename for x in items}) == len(items)
                and ARCHIVE_MEMBER in {x.filename for x in items},
                "ARCHIVE_ROSTER")
        member = bundle.getinfo(ARCHIVE_MEMBER)
        require(0 < member.file_size <= MAX_JOINT_BYTES, "JOINT_MEMBER_SIZE")
        with bundle.open(member) as handle:
            joint_raw = handle.read(MAX_JOINT_BYTES + 1)
    report = inventory(joint_raw, joint_sha256)
    return {"artifact_zip_sha256": archive_sha256, **report}


def compare(linux, windows):
    stable_keys = (
        "native_checkpoint_sha256", "property_checkpoint_sha256",
        "native_properties", "total_binary_property_positions",
        "unoccupied_binary_property_positions", "fully_known_entities",
        "nonempty_entities", "entity_capacity", "property_bits_per_entity",
        "property_source_namespace", "property_source_count",
        "nondefault_relation_source_slots", "retained_native_public_witnesses",
        "trained_specialist_count", "trained_specialist_steps",
    )
    require(all(linux[k] == windows[k] for k in stable_keys),
            "PLATFORM_NATIVE_KNOWLEDGE_DIVERGENCE")
    return {
        "schema": "yggdrasil.know01.cross-platform-knowledge-capacity.v1",
        "linux": linux, "windows": windows,
        "native_property_state_identical": True,
        "native_checkpoint_identical": True,
        "joint_checkpoint_byte_identical": (
            linux["joint_checkpoint_sha256"] == windows["joint_checkpoint_sha256"]),
        "new_source_actions": 0, "training_executed": False,
        "science_executed": False, "accepted_state_changed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--linux", type=Path, required=True)
    p.add_argument("--linux-archive-sha256", required=True)
    p.add_argument("--linux-joint-sha256", required=True)
    p.add_argument("--windows", type=Path, required=True)
    p.add_argument("--windows-archive-sha256", required=True)
    p.add_argument("--windows-joint-sha256", required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = compare(
        archive_inventory(args.linux, args.linux_archive_sha256, args.linux_joint_sha256),
        archive_inventory(args.windows, args.windows_archive_sha256, args.windows_joint_sha256),
    )
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()