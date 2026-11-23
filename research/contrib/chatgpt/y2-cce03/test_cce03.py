"""Engineering fixtures ONLY, not preregistered primary seeds or outcomes."""
import hashlib
import json
import unittest

from cce03 import Ecology, Contract, TRAIN, check_event, subsets_for


def fixture(world="positive"):
    # Fixed enumeration, 4 x 64 states x 3 actions = 768 unique-loop events.
    for _ in range(4):
        for state in range(64):
            for action in range(3):
                nxt = state
                if world == "positive" and action == 0:
                    if ((state >> 2) & 1) ^ ((state >> 3) & 1):
                        nxt ^= 1
                yield state, action, nxt


class CCE03Tests(unittest.TestCase):
    def test_parent_space(self):
        for i in range(6):
            sets = subsets_for(i)
            self.assertEqual(16, len(sets))
            self.assertEqual(16, len(set(sets)))
            self.assertTrue(all(i not in p and len(p) <= 2 for p in sets))

    def test_validation_rejects_nonpublic_values(self):
        ec = Ecology()
        for x, a, n in ((True, 0, 0), (64, 0, 0), (0, 3, 0),
                        (0, 0, -1), (1, 1, 1.0)):
            with self.assertRaises(ValueError):
                ec.observe(x, a, n)
        self.assertEqual(0, ec.n)

    def test_no_frozen_prediction_before_complete_training(self):
        ec = Ecology()
        with self.assertRaises(ValueError):
            ec.predict_step(0, 0)
        with self.assertRaises(ValueError):
            ec.freeze()

    def test_known_xor_parent_discovered(self):
        ec = Ecology()
        for event in fixture():
            ec.observe(*event)
        ec.freeze()
        self.assertEqual([2, 3], ec.chosen_parents()["0:0"])
        for x in range(64):
            expected = x ^ (((x >> 2 & 1) ^ (x >> 3 & 1)))
            self.assertEqual(expected, ec.predict_step(x, 0))

    def test_null_world_selects_no_parents(self):
        ec = Ecology()
        for event in fixture(world="null"):
            ec.observe(*event)
        ec.freeze()
        self.assertTrue(all(not p for p in ec.chosen_parents().values()))
        for x in range(64):
            for a in range(3):
                self.assertEqual(x, ec.predict_step(x, a))

    def test_snapshot_exact_recovery_and_no_updates_after_freeze(self):
        ec = Ecology()
        for event in fixture():
            ec.observe(*event)
        ec.freeze()
        cold = Ecology.restore(ec.snapshot())
        self.assertEqual(ec.snapshot(), cold.snapshot())
        self.assertEqual(ec.chosen_parents(), cold.chosen_parents())
        for x in range(64):
            for a in range(3):
                for mode in ("cce", "one", "pooled", "full"):
                    self.assertEqual(ec.predict_step(x, a, mode=mode),
                                     cold.predict_step(x, a, mode=mode))
        with self.assertRaises(ValueError):
            cold.observe(0, 0, 1)

    def test_forged_semantic_checkpoint_rejected(self):
        ec = Ecology()
        ec.observe(0, 0, 1)
        s = json.loads(ec.snapshot().split(b".", 2)[2])
        s["records"][0]["candidates"][0]["counts"][0][2] += 1
        raw = json.dumps(s, sort_keys=True, separators=(",", ":")).encode("ascii")
        forged = b"CCE03." + hashlib.sha256(raw).hexdigest().encode("ascii") + b"." + raw
        with self.assertRaises(ValueError):
            Ecology.restore(forged)

    def test_hash_corruption_fails(self):
        ec = Ecology()
        raw = bytearray(ec.snapshot())
        raw[-1] ^= 1
        with self.assertRaises(ValueError):
            Ecology.restore(bytes(raw))

    def test_hard_training_limit(self):
        ec = Ecology()
        for e in fixture():
            ec.observe(*e)
        self.assertEqual(TRAIN, ec.n)
        with self.assertRaises(ValueError):
            ec.observe(0, 0, 1)


if __name__ == '__main__':
    unittest.main()
