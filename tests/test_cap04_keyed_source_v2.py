"""CAP04 v2 source protocol safety and non-enumerable-ID engineering fixtures."""
import importlib.util
from pathlib import Path
from collections import defaultdict
import hashlib
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/YGG-CAP04/prospective_source_v2.py")
spec = importlib.util.spec_from_file_location("cap04_v2_engineering_only", SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# These are deliberately PUBLIC low-entropy illustrative fixture values.
# They must NEVER be used as private source keys for a scientific cohort.
TEST_A = bytes(range(32))
TEST_B = bytes(range(32, 64))


class V2ProtectedSourceTests(unittest.TestCase):
    def test_registered_first_use_unconditionally_locked(self):
        self.assertEqual(m.REGISTERED_DEV, (99917, 99931))
        for seed in m.REGISTERED:
            for entropy in (None, TEST_A, TEST_B):
                with self.subTest(seed=seed), self.assertRaisesRegex(
                        ValueError, "REGISTERED_FIRST_USE_FORBIDDEN"):
                    m.generate_registered(seed, entropy)
        for unknown in (False, "99917", 1, 99811):
            with self.assertRaises(ValueError):
                m.generate_registered(unknown, TEST_A)
        for invalid in (None, 99917, 1, "cap04-v2-engineering-unknown"):
            with self.assertRaisesRegex(ValueError,
                                        "REGISTERED_FIRST_USE_FORBIDDEN"):
                m.engineering_fixture(invalid, TEST_A)

    def test_bad_key_type_length_and_domain_rejected(self):
        for bad in (None, b"", b"a", b"0"*31, b"0"*33,
                    "0"*32, False, 1, bytearray(32)):
            with self.subTest(bad=type(bad).__name__), self.assertRaisesRegex(
                    ValueError, "PRIVATE_256BIT_ENTROPY_REQUIRED"):
                m.engineering_fixture(m.ENGINEERING_FIXTURES[0], bad)
        with self.assertRaisesRegex(ValueError, "PRIVATE_KEY_ROLE"):
            m._key(TEST_A, b"bad-role")
        for bad in (-1, 96, True, 1.5, "1"):
            with self.assertRaisesRegex(ValueError, "ACTION_INDEX"):
                m.action_at(TEST_A, bad)

    def test_public_rows_are_keyed_opaque_and_strictly_sequential(self):
        a, b = [(identity, m.engineering_fixture(identity, key))
                for identity, key in zip(m.ENGINEERING_FIXTURES,
                                         (TEST_A, TEST_B))]
        rows_a, rows_b = a[1], b[1]
        self.assertEqual(rows_a, m.engineering_fixture(a[0], TEST_A))
        self.assertEqual(rows_b, m.engineering_fixture(b[0], TEST_B))
        self.assertEqual(m.SCHEMA, "yggdrasil.cap04.prospective-source-keyed.v2")
        self.assertNotEqual(
            m.commitment(TEST_A, a[0], "a"*40, "b"*40),
            m.commitment(TEST_B, b[0], "a"*40, "b"*40))
        self.assertEqual(len(rows_a), len(rows_b), 96)
        self.assertFalse(set(r["id"] for r in rows_a) &
                         set(r["id"] for r in rows_b))
        for identity, key, rows in ((a[0], TEST_A, rows_a),
                                    (b[0], TEST_B, rows_b)):
            for t, row in enumerate(rows):
                self.assertEqual(set(row),
                                 {"id", "views", "action", "s2", "y", "post"})
                self.assertEqual(row["id"], m.witness_id(identity, key, t))
                self.assertEqual(len(row["id"]), 64)
                self.assertEqual(row["action"], m.action_at(identity, key, t))
                # Public witness IDs have no unkeyed, enumeratable source tag.
                old = hashlib.sha256(
                    f"YGG-CAP04/public-witness-v1/{identity}/{t}/observed"
                    .encode("ascii")).hexdigest()
                self.assertNotEqual(row["id"], old)
            for prev, following in zip(rows, rows[1:]):
                self.assertEqual(prev["post"],
                                 (following["views"][0][0],
                                  following["views"][0][1],
                                  following["views"][1][1]))
            for lo, hi in ((0, 32), (32, 72), (72, 96)):
                self.assertEqual({action: sum(row["action"] == action
                                              for row in rows[lo:hi])
                                  for action in m.ACTIONS},
                                 {action: (hi-lo)//4 for action in m.ACTIONS})

    def test_exogenous_schedule_varies_predecessor_and_clock(self):
        left = m.engineering_fixture(m.ENGINEERING_FIXTURES[0], TEST_A)
        right = m.engineering_fixture(m.ENGINEERING_FIXTURES[1], TEST_B)
        for rows in (left, right):
            predecessors = defaultdict(set)
            for t in range(32, 72):
                predecessors[rows[t]["action"]].add(rows[t-1]["action"])
            self.assertGreaterEqual(min(map(len, predecessors.values())), 2)
        ambiguities = [t for t in range(32,72)
                       if left[t]["action"] == right[t]["action"] and
                       left[t-1]["action"] != right[t-1]["action"]]
        self.assertGreaterEqual(len(ambiguities), 1)
        # Source-specific entropy is not part of the learner's public views.
        self.assertTrue(all("entropy" not in row and "identity" not in row
                            and "seed" not in row and "phase" not in row
                            for row in left + right))

    def test_same_entropy_is_source_bound_and_reuse_detectable(self):
        # Reproduce the original bug: two different source identities
        # receiving identical entropy MUST NOT yield identical histories.
        left, right = [m.engineering_fixture(label, TEST_A)
                       for label in m.ENGINEERING_FIXTURES]
        self.assertNotEqual(left, right)
        self.assertTrue(set(r["id"] for r in left).isdisjoint(
                        r["id"] for r in right))
        self.assertTrue(any(a["action"] != b["action"]
                            for a, b in zip(left, right)))
        for role in (b"action", b"witness", b"world"):
            self.assertNotEqual(m._key(TEST_A, role, m.ENGINEERING_FIXTURES[0]),
                                m._key(TEST_A, role, m.ENGINEERING_FIXTURES[1]))
        first = m.commitment(TEST_A, m.ENGINEERING_FIXTURES[0],
                             "a"*40, "b"*40)
        self.assertEqual(first, m.commitment(
            TEST_A, m.ENGINEERING_FIXTURES[0], "a"*40, "b"*40))
        self.assertNotEqual(first, m.commitment(
            TEST_A, m.ENGINEERING_FIXTURES[1], "a"*40, "b"*40))
        self.assertNotEqual(first, m.commitment(
            TEST_A, m.ENGINEERING_FIXTURES[0], "c"*40, "b"*40))
        self.assertNotEqual(first, m.commitment(
            TEST_A, m.ENGINEERING_FIXTURES[0], "a"*40, "c"*40))
        for invalid in (None, "nope", "A"*40, "0"*39, "x"*40):
            with self.assertRaisesRegex(ValueError, "PINNED_GIT_SHA_REQUIRED"):
                m.commitment(TEST_A, m.ENGINEERING_FIXTURES[0],
                             invalid, "b"*40)
        with self.assertRaisesRegex(ValueError, "REGISTERED_FIRST_USE_FORBIDDEN"):
            m.commitment(TEST_A, "99917", "a"*40, "b"*40)


if __name__ == "__main__":
    unittest.main()
