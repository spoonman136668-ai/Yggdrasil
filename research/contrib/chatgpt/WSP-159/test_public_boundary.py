"""Fabricated WSP159 public-boundary tests; never import or run causal_gym."""
import dataclasses
import hashlib
import json
import sys
import unittest

from public_boundary import PublicTransition, PUBLIC_FIELDS, SCHEMA


def valid():
    return dict(observation=[-0.0, .5, 1, -2], action=1,
                next_observation=[.01, -.2, 0.1, .8], reward=1,
                terminated=False, truncated=False)


class PublicBoundaryTests(unittest.TestCase):
    def test_public_roundtrip_and_no_source_import(self):
        self.assertNotIn("causal_gym", sys.modules)
        raw = valid()
        record = PublicTransition.from_public(**raw)
        self.assertEqual(len(record.observation), 4)
        self.assertEqual(record.observation[0], 0.0)
        self.assertEqual(record.model_input().keys(), PUBLIC_FIELDS)
        self.assertTrue(record.canonical().isascii())
        self.assertLess(len(record.canonical()), 2048)
        restored = PublicTransition.restore(record.canonical(), record.sha256())
        self.assertEqual(restored, record)
        self.assertEqual(restored.sha256(), hashlib.sha256(record.canonical()).hexdigest())
        self.assertNotIn("causal_gym", sys.modules)

    def test_detached_public_values_and_immutable_record(self):
        values = valid()
        record = PublicTransition.from_public(**values)
        snapshot = record.canonical()
        values["observation"][0] = 999
        values["next_observation"][0] = 999
        self.assertEqual(snapshot, record.canonical())
        with self.assertRaises(dataclasses.FrozenInstanceError):
            record.reward = 23
        exported = record.model_input()
        exported["observation"][0] = 999
        self.assertEqual(snapshot, record.canonical())

    def test_privileged_payloads_rejected(self):
        for key in ("info", "u_wind", "get_graph", "ctf_do", "env", "unwrapped",
                    "source_family", "source_seed", "hidden_label", "natural_action"):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "FIELD_SET"):
                PublicTransition.from_public(**{**valid(), key: "private"})
        for key in PUBLIC_FIELDS:
            reduced = valid()
            del reduced[key]
            with self.subTest(missing=key), self.assertRaisesRegex(ValueError, "FIELD_SET"):
                PublicTransition.from_public(**reduced)

    def test_invalid_actions_flags_and_nonfinite(self):
        for action in (-1, 2, True, 0.0, "1"):
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, "ACTION"):
                PublicTransition.from_public(**{**valid(), "action": action})
        for flags in ((1, False), (False, 0), ("False", True)):
            with self.subTest(flags=flags), self.assertRaisesRegex(ValueError, "FLAG"):
                PublicTransition.from_public(**{**valid(), "terminated": flags[0],
                                                "truncated": flags[1]})
        for value in (float("nan"), float("inf"), -float("inf"), "0.1", True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                PublicTransition.from_public(**{**valid(), "reward": value})
            for key in ("observation", "next_observation"):
                with self.subTest(value=value, key=key), self.assertRaises(ValueError):
                    v = valid()
                    v[key] = [0, 0, value, 0]
                    PublicTransition.from_public(**v)

    def test_bad_shape_and_protected_metadata_in_state(self):
        for malformed in ((0, 0, 0), [0, 0, 0, 0, 0], "0000", None,
                          {"x": 0, "y": 0, "theta": 0, "wind": 0}):
            for key in ("observation", "next_observation"):
                with self.subTest(shape=malformed, key=key), self.assertRaises(ValueError):
                    PublicTransition.from_public(**{**valid(), key: malformed})
        with self.assertRaises(ValueError):
            PublicTransition.from_public(**{**valid(), "reward": 10**1000})

    def test_tampering_duplicate_fields_and_noncanonical_rejected(self):
        r = PublicTransition.from_public(**valid())
        raw = r.canonical()
        for changed in (raw + b" ", raw.replace(b'"reward":1.0', b'"reward":2.0'),
                        b"\x00" + raw):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                PublicTransition.restore(changed, r.sha256())
        expanded = json.loads(raw)
        expanded["u_wind"] = 0.12
        injected = json.dumps(expanded, sort_keys=True, separators=(",", ":")).encode()
        with self.assertRaisesRegex(ValueError, "SCHEMA"):
            PublicTransition.restore(injected, hashlib.sha256(injected).hexdigest())
        duplicate = raw.replace(b'"schema":', b'"schema":"x","schema":')
        with self.assertRaisesRegex(ValueError, "PARSE"):
            PublicTransition.restore(duplicate, hashlib.sha256(duplicate).hexdigest())
        spaced = json.dumps(json.loads(raw)).encode()
        with self.assertRaisesRegex(ValueError, "NONCANONICAL"):
            PublicTransition.restore(spaced, hashlib.sha256(spaced).hexdigest())
        with self.assertRaisesRegex(ValueError, "WIRE_HASH"):
            PublicTransition.restore(raw, "0"*64)

    def test_wire_rejects_bad_size_types_and_scalar_schema(self):
        for value in ("x", b"", b"x"*3000, bytearray(b"x")):
            with self.subTest(value=type(value)), self.assertRaises(ValueError):
                PublicTransition.restore(value, "0"*64)
        data = {"schema": SCHEMA, **valid()}
        data["schema"] = "evil"
        raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        with self.assertRaisesRegex(ValueError, "SCHEMA"):
            PublicTransition.restore(raw, hashlib.sha256(raw).hexdigest())
        data["schema"] = SCHEMA
        data["reward"] = None
        raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        with self.assertRaises(ValueError):
            PublicTransition.restore(raw, hashlib.sha256(raw).hexdigest())

    def test_upstream_dual_terminal_flags_preserved(self):
        v = valid()
        v["terminated"] = True
        v["truncated"] = True
        original = PublicTransition.from_public(**v)
        restored = PublicTransition.restore(original.canonical(), original.sha256())
        self.assertTrue(restored.terminated and restored.truncated)


if __name__ == "__main__":
    unittest.main()
