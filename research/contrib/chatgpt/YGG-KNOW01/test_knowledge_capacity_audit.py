"""Fixture-only negative controls for the archived-property knowledge audit."""
import importlib.util
import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("know01_audit", HERE / "knowledge_capacity_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def canon(doc):
    return json.dumps(doc, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def assembled(*, pairs=((3, 1), (0, 0)), mode="engineering_fixture_only",
              joint_suffix=None):
    prop = {
        "schema": audit.PROPERTY_SCHEMA,
        "source_mode": mode, "accepted_native": False,
        "scientific_pass": False, "entities": 2,
        "context_bits": 2,
        "source_namespace": "synthetic-fixture",
        "property_sources": ["1" * 64],
        "relation_sources": ["0" * 64] * 16,
        "known_value_planes_uint16le": b"".join(struct.pack("<HH", *x)
                                                for x in pairs).hex(),
    }
    native = {
        "schema": audit.NATIVE_SCHEMA, "source_mode": "engineering_fixture_only",
        "accepted_native": False, "scientific_pass": False,
        "properties_ascii": canon(prop).decode("ascii"),
        "experience_ascii": canon({"schema":
            "yggdrasil.ckad.native-episode-experience.v6", "episodes": []}).decode("ascii"),
    }
    joint = {
        "schema": audit.JOINT_SCHEMA,
        "native_ascii": canon(native).decode("ascii"),
        "native_parent_sha256": "2" * 64, "specialist_parent_sha256": "3" * 64,
        "action_heads": [{"kind": k, "steps": 12} for k in ("transition", "reward")],
        "temporal_heads": [{"kind": k, "steps": 12} for k in ("transition", "reward")],
    }
    if joint_suffix:
        joint.update(joint_suffix)
    return canon(joint)


class KnowledgeCapacityAuditTests(unittest.TestCase):
    def test_counts_and_rejects_false_native_promotion(self):
        raw = assembled()
        v = audit.inventory(raw, audit.digest(raw))
        self.assertEqual((v["native_properties"],
                          v["unoccupied_binary_property_positions"]), (2, 2))
        self.assertEqual(v["property_source_namespace"], "synthetic-fixture")
        self.assertEqual(v["real_world_causal_grounding"], "UNVERIFIED")
        self.assertEqual(v["new_knowledge_ingested"], 0)
        self.assertFalse(v["accepted_model_mutated"])

    def test_no_unobserved_property_values(self):
        raw = assembled(pairs=((1, 2), (0, 0)))
        with self.assertRaisesRegex(ValueError, "UNKNOWN_OR_INVALID_PROPERTY"):
            audit.inventory(raw, audit.digest(raw))

    def test_external_claim_must_not_be_laundered(self):
        raw = assembled(mode="owner_authenticated_real_world")
        with self.assertRaisesRegex(ValueError, "PROPERTY_NOT_SYNTHETIC_RESEARCH"):
            audit.inventory(raw, audit.digest(raw))

    def test_modified_joint_requires_exact_trusted_pin(self):
        raw = assembled()
        with self.assertRaisesRegex(ValueError, "JOINT_PIN"):
            audit.inventory(raw + b" ", audit.digest(raw))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "BAD_JSON"):
            audit.parse(b'{"x":1,"x":2}')

    def test_absent_specialist_or_field_rejected(self):
        raw = assembled(joint_suffix={"temporal_heads": []})
        with self.assertRaisesRegex(ValueError, "HEAD_SHAPE"):
            audit.inventory(raw, audit.digest(raw))
        raw = assembled(joint_suffix={"unauthorized_model_update": True})
        with self.assertRaisesRegex(ValueError, "JOINT_SCHEMA"):
            audit.inventory(raw, audit.digest(raw))

    def test_native_matching_but_float_head_difference_disclosed(self):
        raw = assembled()
        other = assembled(joint_suffix={"action_heads": [
            {"kind": "transition", "steps": 12, "weight": 0.000000000001},
            {"kind": "reward", "steps": 12}]})
        x = audit.inventory(raw, audit.digest(raw))
        y = audit.inventory(other, audit.digest(other))
        pair = audit.compare(x, y)
        self.assertTrue(pair["native_checkpoint_identical"])
        self.assertFalse(pair["joint_checkpoint_byte_identical"])

    def test_cross_platform_native_change_refused(self):
        one = assembled()
        two = assembled(pairs=((3, 1), (1, 1)))
        with self.assertRaisesRegex(ValueError, "PLATFORM_NATIVE_KNOWLEDGE_DIVERGENCE"):
            audit.compare(audit.inventory(one, audit.digest(one)),
                          audit.inventory(two, audit.digest(two)))

    def test_archive_pin_and_bounded_member_read(self):
        raw = assembled()
        with tempfile.TemporaryDirectory() as td:
            name = Path(td) / "evidence.zip"
            with zipfile.ZipFile(name, "w") as archive:
                archive.writestr(audit.ARCHIVE_MEMBER, raw)
            expected = audit.digest(name.read_bytes())
            out = audit.archive_inventory(name, expected, audit.digest(raw))
            self.assertEqual(out["native_properties"], 2)
            with self.assertRaisesRegex(ValueError, "ARCHIVE_PIN"):
                audit.archive_inventory(name, "0" * 64, audit.digest(raw))


if __name__ == "__main__":
    unittest.main()