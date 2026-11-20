"""KNOW31 toy-only source integrity; deliberately NEVER consume frozen HELD seeds."""
import unittest
from know31_paired_interference_dev import (
    SCHEMA, PROTO, protocol, private_witness, cold_copy, slot_digest,
    new_arms, score_at_fork, ARMS, MAPS, SEEDS,
)
from know30_blind_archive_reactivation_dev import Joint, Pair, Single, MODE
from unknown_action_affordance_dev import digest


class TestKNOW31(unittest.TestCase):
    def setUp(self):
        self.prior = [1 / 6.] * 6
        self.a = Joint(self.prior)
        self.b = Joint(self.prior)

    def test_frozen_prereg(self):
        p = protocol()
        self.assertEqual(p["schema"], PROTO)
        self.assertEqual(p["budgets"]["actions_both_forks_per_method"], 2304)
        self.assertEqual(p["source_mode"], MODE)
        self.assertFalse(p["source"]["protected_original_first_use"])

    def test_distinct_fresh_seed_contract(self):
        self.assertEqual(len(SEEDS), len(set(SEEDS)))
        self.assertEqual(len(MAPS) * len(SEEDS), 24)
        self.assertTrue(all(seed >= 16000 for seed in SEEDS))
        self.assertIn("B-specific", protocol()["question"])

    def test_source_mode_and_world_denials_without_frozen_witness(self):
        for kwargs in (
            dict(mid=0, seed=999, t=0, a=0, branch="control_A"),
            dict(mid=9, seed=16001, t=0, a=0, branch="control_A"),
            dict(mid=0, seed=16001, t=48, a=0, branch="control_A"),
            dict(mid=0, seed=16001, t=0, a=5, branch="control_A"),
            dict(mid=0, seed=16001, t=0, a=0, branch="phase_oracle"),
            dict(mid=0, seed=16001, t=0, a=0, branch="control_A",
                 source_mode="original_first_use"),
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    private_witness(**kwargs)

    def test_cold_clone_pair_exact_without_held(self):
        m = Pair(self.a, self.b, quarantine=False)
        m.observe(0, 0, 0, 1)
        before = m.checkpoint()
        copy = cold_copy(m)
        self.assertEqual(copy.checkpoint(), before)
        self.assertEqual(digest(before), digest(copy.checkpoint()))
        self.assertEqual([copy.prob(c,0) for c in range(8)],
                         [m.prob(c,0) for c in range(8)])

    def test_cold_clone_single_exact_without_held(self):
        for rolling in (False, True):
            model = Single(self.a, rolling=rolling)
            for t in range(11):
                model.observe(t, t%4, t%4, t%2)
            copy = cold_copy(model)
            self.assertEqual(copy.rows, model.rows)
            self.assertEqual([copy.prob(c,0) for c in range(8)],
                             [model.prob(c,0) for c in range(8)])

    def test_archived_A_hash_stays_immutable_when_B_only_written(self):
        m = Pair(self.a, self.b, quarantine=True)
        original = slot_digest(m)
        m.slots[1].update(0, 0, 1, 1.0)
        self.assertEqual(slot_digest(m), original)
        self.assertNotEqual(m.slots[1].assimilated, m.slots[0].assimilated)

    def test_same_public_history_deterministic_source_blind(self):
        m = Pair(self.a, self.b, quarantine=False)
        n = cold_copy(m)
        for t in range(8):
            kwargs = (t,t%4,t%4,t%2)
            m.observe(*kwargs)
            n.observe(*kwargs)
        self.assertEqual(m.checkpoint(), n.checkpoint())

    def test_wrong_order_and_forged_witness_fail(self):
        m = Pair(self.a, self.b, quarantine=True)
        with self.assertRaises(ValueError):
            m.observe(1,1,1,1)
        with self.assertRaises(ValueError):
            m.observe(0,0,0,1,source_mode="real")
        m.observe(0,0,0,1)
        with self.assertRaises(ValueError):
            m.observe(0,0,0,1)


if __name__ == "__main__":
    unittest.main()
