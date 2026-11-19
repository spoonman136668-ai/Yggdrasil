"""Pure fixture-only tests; never read real owner storage or load a model."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("custody_probe", HERE / "custody_probe.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def synthetic_amalgam(episodes=None):
    episodes = episodes if episodes is not None else [
        ["1" * 64, [[0, 1], [0, 1]], 1, 0, 1, 1],
    ]
    xp = canonical({"schema": "fixture", "episodes": episodes,
                    "state_sha256": "a" * 64})
    native = canonical({
        "schema": "yggdrasil.ckad.native-cumulative-learner.v5",
        "experience_ascii": xp.decode("ascii"),
    })
    return canonical({
        "schema": mod.AMALGAM,
        "native_ascii": native.decode("ascii"),
        "native_parent_sha256": "b" * 64,
        "specialist_parent_sha256": "c" * 64,
        "action_heads": [
            {"kind": "transition", "steps": 3},
            {"kind": "reward", "steps": 3},
        ],
        "temporal_heads": [
            {"kind": "transition", "steps": 3},
            {"kind": "reward", "steps": 3},
        ],
    })


class CustodyProbeTests(unittest.TestCase):
    def test_pyc1_counter_integrity_but_not_owner_custody(self):
        payload = b"YPC1" + struct.pack(">64H", *([1] + [0] * 63))
        raw = payload + hashlib.sha256(payload).digest()
        report = mod.inspect(raw, hashlib.sha256(raw).hexdigest())
        self.assertEqual(report["total_observed_counter_increments"], 1)
        self.assertEqual(report["owner_authentication"], "UNVERIFIED")
        self.assertFalse(report["continuation_authorized"])

    def test_pyc1_tamper_rejected(self):
        payload = b"YPC1" + b"\\x00" * 128
        raw = payload + hashlib.sha256(payload).digest()
        with self.assertRaisesRegex(ValueError, "PYC1_INTEGRITY"):
            mod.inspect(raw[:-1] + bytes([raw[-1] ^ 1]))

    def test_amalgam_extracts_only_bounded_summary(self):
        raw = synthetic_amalgam()
        result = mod.inspect(raw)
        self.assertEqual(result["witnessed_episodes"], 1)
        self.assertEqual(result["shadow_specialist_steps"], [3] * 4)
        self.assertEqual(result["source_equivalence_replay"], "NOT_EXECUTED")
        self.assertFalse(result["canonical_cumulative_model_identified"])
        self.assertNotIn("raw", json.dumps(result))

    def test_duplicate_witness_rejected(self):
        event = ["1" * 64, [[0, 1], [0, 1]], 1, 0, 1, 1]
        with self.assertRaisesRegex(ValueError, "DUPLICATE_EPISODE"):
            mod.inspect(synthetic_amalgam([event, event]))

    def test_non_public_outcome_rejected(self):
        bad = [["1" * 64, [[0, 1], [0, 1]], 1, 0, 1, 2]]
        with self.assertRaisesRegex(ValueError, "EPISODE_PUBLIC_BITS"):
            mod.inspect(synthetic_amalgam(bad))

    def test_wrong_supplied_sha_rejected(self):
        with self.assertRaisesRegex(ValueError, "EXPECTED_DIGEST_MISMATCH"):
            mod.inspect(synthetic_amalgam(), "0" * 64)

    def test_noncanonical_and_duplicate_keys_rejected(self):
        raw = synthetic_amalgam()
        with self.assertRaisesRegex(ValueError, "NONCANONICAL_JSON"):
            mod.inspect(b" " + raw)
        with self.assertRaisesRegex(ValueError, "DUPLICATE_KEY"):
            mod.inspect(b'{"schema":1,"schema":2}')

    def test_wrong_schema_is_not_silently_accepted(self):
        data = json.loads(synthetic_amalgam())
        data["schema"] = "unknown"
        with self.assertRaisesRegex(ValueError, "AMALGAM_SCHEMA"):
            mod.inspect(canonical(data))

    def test_no_scientific_or_owner_acceptance_from_self_hash(self):
        raw = synthetic_amalgam()
        report = mod.inspect(raw, mod.sha(raw))
        for field in ("owner_authentication", "source_lease",
                      "functional_retention", "scientific_improvement"):
            self.assertEqual(report[field], "UNVERIFIED")
        self.assertFalse(report["continuation_authorized"])
        self.assertFalse(report["training_executed"])


if __name__ == "__main__":
    unittest.main()
