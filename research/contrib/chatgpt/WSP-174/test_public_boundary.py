"""Source-free WSP174 test suite. No CausalMBRL/Gym/Torch source execution."""
import ast
import dataclasses
import hashlib
import json
from pathlib import Path
import unittest

from public_boundary import (PublicEvidence, decode_public_state, PUBLIC_FIELDS,
                             SCHEMA, ACTION_COUNT)

POSITIONS = ((0, 0), (0, 4), (4, 0), (4, 4), (2, 2))


def state(colors, positions=POSITIONS):
    t = [[[0 for _ in range(5)] for _ in range(5)] for _ in range(25)]
    for i, (color, (x, y)) in enumerate(zip(colors, positions)):
        t[5 * i + color][x][y] = 1
    return t


def valid():
    return dict(current_state=state((0, 1, 2, 3, 4)),
                goal_state=state((0, 1, 0, 3, 4)),
                action=2 * 5, next_state=state((0, 1, 0, 3, 4)),
                reward=1.0, done=False)


class ChemistryPublicEvidenceTests(unittest.TestCase):
    def test_public_exact_and_decoding(self):
        e = PublicEvidence.from_public(**valid())
        self.assertEqual(e.action, 10)
        self.assertEqual(e.current[2], (4, 0, 2))
        self.assertEqual(e.next[2], (4, 0, 0))
        self.assertEqual(e.reward, 1)
        self.assertEqual(len(e.current), 5)
        self.assertEqual(ACTION_COUNT, 25)
        self.assertEqual(PUBLIC_FIELDS, set(valid()))
        self.assertEqual(e.policy_input().keys(), {"current", "goal"})
        for field in ("next", "reward", "action", "done", "adjacency_matrix", "mlps"):
            self.assertNotIn(field, e.policy_input())
        self.assertLess(len(e.canonical()), 4096)
        self.assertEqual(e, PublicEvidence.restore(e.canonical(), e.sha256()))
        self.assertEqual(e.sha256(), hashlib.sha256(e.canonical()).hexdigest())
        tree = ast.parse(Path(__file__).with_name("public_boundary.py").read_text(encoding="utf-8"))
        imports = {a.name.partition(".")[0] for n in ast.walk(tree)
                   for a in (n.names if isinstance(n, ast.Import) else ())}
        imports |= {n.module.partition(".")[0] for n in ast.walk(tree)
                    if isinstance(n, ast.ImportFrom) and n.module}
        self.assertFalse(imports & {"gym", "torch", "numpy", "causal_gym"})

    def test_detached_and_immutable(self):
        v = valid()
        e = PublicEvidence.from_public(**v)
        raw = e.canonical()
        v["current_state"][0][0][0] = 0
        v["goal_state"][0][0][0] = 0
        v["next_state"][0][0][0] = 0
        self.assertEqual(raw, e.canonical())
        a = e.policy_input()
        a["current"][0][0] = 999
        self.assertEqual(raw, e.canonical())
        with self.assertRaises(dataclasses.FrozenInstanceError):
            e.reward = 0

    def test_privileged_metadata_does_not_cross(self):
        for name in ("info", "mlps", "mask", "adjacency_matrix", "source_graph",
                     "actions_to_target", "source_seed", "cohort", "rng", "hidden",
                     "natural_action", "future_reward", "evaluator_labels", "env"):
            with self.subTest(extra=name), self.assertRaisesRegex(ValueError, "FIELD_SET"):
                PublicEvidence.from_public(**{**valid(), name: "privileged"})
        for name in PUBLIC_FIELDS:
            v = valid()
            v.pop(name)
            with self.subTest(missing=name), self.assertRaisesRegex(ValueError, "FIELD_SET"):
                PublicEvidence.from_public(**v)

    def test_state_shapes_and_value_validation(self):
        tensors = (None, "tensor", [0] * 25, state((0, 0, 0, 0, 0))[:-1])
        for tensor in tensors:
            with self.subTest(tensor=type(tensor)), self.assertRaises(ValueError):
                decode_public_state(tensor)
        t = state((0, 0, 0, 0, 0))
        t[0][0][0] = True
        with self.assertRaisesRegex(ValueError, "BINARY"):
            decode_public_state(t)
        t = state((0, 0, 0, 0, 0))
        t[0][0][0] = 0
        with self.assertRaisesRegex(ValueError, "NOT_ONEHOT"):
            decode_public_state(t)
        t = state((0, 0, 0, 0, 0))
        t[0][0][1] = 1
        with self.assertRaisesRegex(ValueError, "NOT_ONEHOT"):
            decode_public_state(t)
        t = state((0, 0, 0, 0, 0))
        t[0][0] = [0]
        with self.assertRaisesRegex(ValueError, "GRID_SHAPE"):
            decode_public_state(t)
        t = state((0, 0, 0, 0, 0))
        t[5][0][0] = 1
        with self.assertRaisesRegex(ValueError, "NOT_ONEHOT"):
            decode_public_state(t)
        t = state((0, 0, 0, 0, 0), positions=((0, 0), (0, 0), *POSITIONS[2:]))
        with self.assertRaisesRegex(ValueError, "COLLISION"):
            decode_public_state(t)

    def test_action_reward_goal_and_terminal_negatives(self):
        for action in (-1, 25, True, 0.0, "10"):
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, "ACTION"):
                PublicEvidence.from_public(**{**valid(), "action": action})
        for reward in (float("nan"), float("inf"), -1, 1.25, True, "1", 0.4):
            with self.subTest(reward=reward), self.assertRaises(ValueError):
                PublicEvidence.from_public(**{**valid(), "reward": reward})
        for done in (True, 0, 1, None, "False"):
            with self.subTest(done=done), self.assertRaisesRegex(ValueError, "SOURCE_DONE"):
                PublicEvidence.from_public(**{**valid(), "done": done})
        with self.assertRaisesRegex(ValueError, "ACTION_EFFECT"):
            PublicEvidence.from_public(**{**valid(), "action": 11})
        with self.assertRaisesRegex(ValueError, "MOVED_OBJECT"):
            PublicEvidence.from_public(**{**valid(), "next_state":
                state((0, 1, 0, 3, 4), positions=((0, 1), *POSITIONS[1:]))})
        with self.assertRaisesRegex(ValueError, "CHANGED_TARGET_POSITIONS"):
            PublicEvidence.from_public(**{**valid(), "goal_state":
                state((0, 1, 0, 3, 4), positions=((0, 1), *POSITIONS[1:]))})

    def test_reward_source_consistency_not_target_oracle_leak(self):
        v = valid()
        v["goal_state"] = state((0, 1, 2, 3, 4))
        with self.assertRaisesRegex(ValueError, "REWARD_MISMATCH"):
            PublicEvidence.from_public(**v)
        v["reward"] = 0.8
        e = PublicEvidence.from_public(**v)
        self.assertEqual(e.reward, 0.8)
        self.assertEqual(e.next[2][2], 0)

    def test_wire_attack_and_canonical_negative(self):
        e = PublicEvidence.from_public(**valid())
        raw = e.canonical()
        with self.assertRaisesRegex(ValueError, "WIRE_HASH"):
            PublicEvidence.restore(raw, "0" * 64)
        for raw2 in (raw+b" ", raw.replace(b'"reward":1.0', b'"reward":0.8')):
            with self.assertRaises(ValueError):
                PublicEvidence.restore(raw2, e.sha256())
        swapped = json.dumps(json.loads(raw)).encode()
        with self.assertRaisesRegex(ValueError, "WIRE_NONCANONICAL"):
            PublicEvidence.restore(swapped, hashlib.sha256(swapped).hexdigest())
        payload = json.loads(raw)
        payload["adjacency_matrix"] = "spoof"
        injected = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        with self.assertRaisesRegex(ValueError, "WIRE_SCHEMA"):
            PublicEvidence.restore(injected, hashlib.sha256(injected).hexdigest())
        duplicate = raw.replace(b'"schema":', b'"schema":"evil","schema":')
        with self.assertRaisesRegex(ValueError, "WIRE_PARSE"):
            PublicEvidence.restore(duplicate, hashlib.sha256(duplicate).hexdigest())
        for data in ("not bytes", b"", b"x" * 5000):
            with self.assertRaisesRegex(ValueError, "WIRE_SIZE"):
                PublicEvidence.restore(data, "0"*64)

    def test_no_source_execution_or_lease_path(self):
        e = PublicEvidence.from_public(**valid())
        dumped = e.canonical().decode("ascii")
        for protected in ("mlps", "mask", "adjacency_matrix", "actions_to_target",
                          "source_seed", "owner_lease", "first_use_execution_allowed",
                          "source_graph", "rng", "hidden"):
            self.assertNotIn(protected, dumped)
        self.assertFalse(hasattr(e, "lease"))
        self.assertFalse(hasattr(e, "run"))


if __name__ == "__main__":
    unittest.main()
