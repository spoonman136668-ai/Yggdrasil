"""HC11 conservative confidence, physical-rights and cold-storage qualification."""
import unittest

from gate import EvidenceGate, base, control
from eval_dev import World, SEEDS, ARMS, one_world


class WitnessGateTests(unittest.TestCase):
    def test_requires_two_real_consistent_causal_observations(self):
        m = EvidenceGate("native", 2)
        self.assertIsNone(m.predict(0, 0))
        m.observe(0, 0, 0)
        self.assertIsNone(m.predict(0, 0))
        m.observe(0, 0, 0)
        self.assertEqual(m.predict(0, 0), 0)
        self.assertIsNone(m.predict(1, 0))
        self.assertEqual(m.witness[(0, 0)], (0, 2))

    def test_one_witness_ablation_and_independent_conventional_model(self):
        naive = EvidenceGate("native", 1)
        conventional = EvidenceGate("conventional", 2)
        self.assertIsInstance(conventional.model, control.ConventionalContextModel)
        for model in (naive, conventional):
            model.observe(0, 0, 0)
        self.assertEqual(naive.predict(0, 0), 0)
        self.assertIsNone(conventional.predict(0, 0))
        conventional.observe(0, 0, 0)
        self.assertEqual(conventional.predict(0, 0), 0)
        self.assertEqual(naive.model.capacity_bits, 320)
        self.assertEqual(conventional.model.capacity_bits, 320)

    def test_direct_contradiction_clears_prior_witnesses(self):
        m = EvidenceGate("native", 2)
        m.observe(0, 0, 0)
        m.observe(0, 0, 0)
        self.assertEqual(m.predict(0, 0), 0)
        m.observe(0, 0, 1)
        self.assertIsNone(m.predict(0, 0))
        self.assertGreater(m.epoch, 0)
        self.assertEqual(m.witness[(0, 0)], (1, 1))

    def test_does_not_output_confident_model_prediction_against_witness(self):
        m = EvidenceGate("native", 2)
        m.observe(0, 0, 0)
        m.observe(0, 0, 0)
        m.model.banks[m.model.active][0] = (1 << 1)  # predicts effect 1
        self.assertIsNone(m.predict(0, 0))

    def test_rejects_invalid_inputs_and_oracle_parameters(self):
        m = EvidenceGate()
        for params in ((-1, 0, 0), (16, 0, 0), (0, 4, 0), (0, 0, 16), (True, 0, 0)):
            with self.subTest(params=params):
                with self.assertRaises(ValueError):
                    m.observe(*params)
        with self.assertRaises(TypeError):
            m.observe(0, 0, 0, hidden_phase=1)
        for args in (("neural", 2), ("native", 0), ("native", 3), ("native", True)):
            with self.assertRaises(ValueError):
                EvidenceGate(*args)

    def test_snapshot_cold_restore_and_tampering(self):
        for family in ("native", "conventional"):
            m = EvidenceGate(family, 2)
            m.observe(0, 0, 0)
            m.observe(0, 0, 0)
            raw = m.snapshot()
            self.assertLessEqual(len(raw), 4096)
            cold = EvidenceGate.restore(raw)
            self.assertEqual(cold.snapshot(), raw)
            self.assertEqual(cold.predict(0, 0), m.predict(0, 0))
            damaged = bytearray(raw)
            damaged[len(raw) // 2] ^= 1
            for invalid in (bytes(damaged), raw[:-1], raw + b"x", bytearray(raw)):
                with self.subTest(family=family, length=len(invalid)):
                    with self.assertRaises(ValueError):
                        EvidenceGate.restore(invalid)

    def test_seed_freeze_and_audit_queries_not_physical_actions(self):
        self.assertEqual([len(v) for v in SEEDS.values()], [8, 8, 8])
        self.assertEqual(len(set().union(*(set(s) for s in SEEDS.values()))), 24)
        with self.assertRaises(ValueError):
            World(81001, "ABA")
        world = World(91001, "ABA")
        for state in range(16):
            for action in range(4):
                world.true_next_for_evaluator(state, action, 0)
        self.assertEqual((world.causal, world.flips), (0, 0))
        for value in (-1, 2, True):
            with self.assertRaises(ValueError):
                world.true_next_for_evaluator(0, 0, value)
        self.assertEqual((world.causal, world.flips), (0, 0))

    def test_uncharged_perturbations_do_not_fit_rules(self):
        world = World(91001, "ABA")
        gate = EvidenceGate()
        raw = gate.snapshot()
        state = 91001 % 16
        moved = world.charge_flip(state, 0)
        self.assertEqual(moved, state ^ 1)
        self.assertEqual(gate.snapshot(), raw)
        self.assertEqual(world.flips, 1)
        after = world.charge_causal(moved, 1, 0)
        gate.observe(moved, 1, after)
        self.assertEqual(gate.model.observations, 1)
        self.assertEqual(world.causal, 1)

    def test_one_world_all_arms_charged_cold_and_no_evaluator_training(self):
        for seed, group in ((91001, "ABA"), (91009, "stationary_majority"),
                            (91017, "OOD_cubic")):
            w = one_world(seed, group)
            self.assertEqual(set(w["arms"]), set(ARMS))
            for arm, r in w["arms"].items():
                expected = 40 if group == "ABA" else 48
                self.assertEqual(r["charged_real_actions"], expected, arm)
                self.assertEqual(r["charged_exogenous_flips"] +
                                 r["charged_mechanism_actions"], expected, arm)
                self.assertLessEqual(r["charged_exogenous_flips"], 8, arm)
                self.assertTrue(r["cold_restore_identical"], arm)
                self.assertLessEqual(r["snapshot_bytes"], 4096, arm)
                self.assertEqual(sum(r["final"][k] for k in
                                 ("correct", "wrong_confident", "abstained")), 64)
                if group == "ABA":
                    self.assertEqual(r["final"], r["intermediate_evaluator_only"]["40"])
                if arm.endswith("gate2") or arm.endswith("gate1"):
                    self.assertLessEqual(r["final"]["correct"] +
                                         r["final"]["wrong_confident"],
                                         r["distinct_fitted_pairs"], arm)


if __name__ == "__main__":
    unittest.main()
