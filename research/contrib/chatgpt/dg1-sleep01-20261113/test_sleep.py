"""Physical custody, no-oracle, deterministic sleep and negative controls."""
import hashlib
import random
import unittest
from sleep_model import (SleepMemory, BayesianRunLength, FULL,
                         surviving, rule_effect, replay, canonical)
from eval_dev import ARMS, SEEDS, World, cold_clone, one_world


class SleepTests(unittest.TestCase):
    def test_frozen_rule_grammar_matches_hc09(self):
        from eval_dev import base
        for state in range(16):
            for rule in range(40):
                self.assertEqual(rule_effect(state, rule, "native"),
                                 base.effect(state, rule))
                self.assertEqual(rule_effect(state, rule, "conventional"),
                                 base.effect(state, rule))

    def test_new_seed_physics_deterministic_and_evaluator_only(self):
        self.assertEqual([len(x) for x in SEEDS.values()], [8, 8, 8])
        self.assertEqual(len(set().union(*(set(x) for x in SEEDS.values()))), 24)
        w = World(93001, "ABA")
        for state in range(16):
            for action in range(4):
                self.assertEqual(w.true_next_for_evaluator(state, action, 0),
                                 World(93001, "ABA").true_next_for_evaluator(state, action, 0))
        self.assertEqual((w.causal, w.flips), (0, 0))
        for params in ((-1, 0, 0), (0, 4, 0), (16, 0, 0), (0, 0, 3)):
            with self.assertRaises(ValueError):
                w.true_next_for_evaluator(*params)
        with self.assertRaises(ValueError):
            World(91001, "ABA")

    def test_physical_locality_and_no_pseudo_observations(self):
        m = SleepMemory()
        with self.assertRaises(ValueError):
            m.sleep()
        with self.assertRaises(ValueError):
            m.observe(0, 0, 2)
        with self.assertRaises(TypeError):
            m.observe(0, 0, 0, hidden_regime=0)
        m.observe(0, 0, 0)
        m.sleep()
        initial = m.snapshot()
        self.assertIsNone(m.predict(0, 0))
        self.assertEqual(len(m.history), 1)
        m.sleep()
        self.assertEqual(len(m.history), 1)
        self.assertNotEqual(m.snapshot(), initial)
        self.assertEqual(len(m.history), 1)

    def test_exact_proofs_require_pre_update_predictions(self):
        m = SleepMemory()
        m.observe(0, 0, 0)
        m.observe(1, 0, 1)
        m.sleep()
        # No two distinct valid holdout predictions emerged ex nihilo.
        self.assertIsNone(m.predict(2, 0))
        self.assertLess(len(m.proofs[m.active][0]), 2)

    def test_offline_two_bank_replay_never_uses_context_label(self):
        source = [(0, 0, 0)] * 4 + [(0, 0, 1)] * 4 + [(0, 0, 0)] * 4
        h = replay(source, "native", 2)
        self.assertEqual(len(h.path), 12)
        self.assertLessEqual(len(h.banks), 2)
        self.assertEqual(h.unexplained, 0)
        self.assertLessEqual(len(set(i for i in h.path if i >= 0)), 2)
        assert all(i in (-1, 0, 1) for i in h.path)

    def test_absence_of_dream_learning(self):
        a, b = SleepMemory(dreams=True), SleepMemory(dreams=False)
        for i in range(20):
            s = i % 16
            action = i % 4
            nxt = s ^ ((i % 3 == 0) << action)
            a.observe(s, action, nxt)
            b.observe(s, action, nxt)
        a.sleep(); b.sleep()
        self.assertEqual(a.history, b.history)
        self.assertEqual(a.banks, b.banks)
        for s in range(16):
            for action in range(4):
                self.assertEqual(a.predict(s, action), b.predict(s, action))
        self.assertTrue(all((s, action) not in {(p, q) for p, q, _ in a.history}
                            for s, action, _ in a.dream_proposals))

    def test_cold_restore_and_tampering(self):
        for fam in ("native", "conventional"):
            m = SleepMemory(fam)
            for i in range(16):
                m.observe(i, i % 4, i)
            m.sleep()
            raw = m.snapshot()
            self.assertLessEqual(len(raw), 8192)
            self.assertEqual(SleepMemory.restore(raw).snapshot(), raw)
            damaged = bytearray(raw)
            damaged[len(raw)//2] ^= 1
            for broken in (bytes(damaged), raw[:-1], raw + b' ', bytearray(raw)):
                with self.assertRaises(ValueError):
                    SleepMemory.restore(broken)
        b = BayesianRunLength()
        b.observe(0, 0, 0)
        self.assertEqual(BayesianRunLength.restore(b.snapshot()).snapshot(), b.snapshot())

    def test_charged_shared_actions_across_arms(self):
        for seed, group in ((93001, "ABA"), (93009, "stationary_majority"),
                            (93017, "OOD_cubic")):
            result = one_world(seed, group)
            self.assertEqual(set(result["final"]), set(ARMS))
            self.assertEqual(result["charged_real_actions"], 40 if group == "ABA" else 48)
            self.assertLessEqual(result["charged_exogenous_flips"], 8)
            self.assertEqual(result["final"]["sleep_native"],
                             result["final"]["sleep_no_dream"])
            for arm in ARMS:
                self.assertEqual(sum(result["final"][arm][x] for x in
                                     ("correct", "wrong_confident", "abstained")), 64)
                self.assertLessEqual(result["snapshot_bytes"][arm], 8192)
                self.assertEqual(len(result["checkpoint_sha256"][arm]), 64)


if __name__ == "__main__":
    unittest.main()
