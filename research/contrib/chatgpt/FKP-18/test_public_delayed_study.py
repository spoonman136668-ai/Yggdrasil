"""Public diagnostic invariants, no FKP-17 DEV/TRANSFER access."""
import unittest

import public_delayed_study as m


class PublicDelayedTests(unittest.TestCase):
    def test_public_world_determinism_and_protected_seeds(self):
        with self.assertRaises(PermissionError):
            m.PublicWorld(978500)
        with self.assertRaises(PermissionError):
            m.PublicWorld(978600)
        a, b = m.PublicWorld(m.PUBLIC_WORLDS[0]), m.PublicWorld(m.PUBLIC_WORLDS[0])
        for action in m.exploration(m.PUBLIC_WORLDS[0]):
            self.assertEqual(a.step(action), b.step(action))

    def test_two_step_credit_is_really_delayed(self):
        world = m.PublicWorld(m.PUBLIC_WORLDS[0])
        tape = [0, 1, 2, 3]
        rows = [world.step(a) for a in tape]
        self.assertTrue(all(x.reward == 0 for x in rows[:3]))
        self.assertEqual(m._earned(rows[3])[4], 1)
        self.assertEqual(m._earned(rows[3])[2], 0)
        self.assertIsNotNone(m._earned(rows[3]))

    def test_equal_observations_and_matched_actions(self):
        native, symbolic = m.NativeCompositionalTrace(), m.ConventionalSymbolic()
        world = m.PublicWorld(m.PUBLIC_WORLDS[3])
        for action in m.exploration(m.PUBLIC_WORLDS[3]):
            row = world.step(action)
            native.observe_public(row)
            symbolic.observe_public(row)
            self.assertEqual(native.choose(world.state, world.public_history()),
                             symbolic.choose(world.state, world.public_history()))

    def test_private_fields_refused_without_mutation(self):
        model = m.NativeCompositionalTrace()
        row = m.PublicWorld(m.PUBLIC_WORLDS[1]).step(0)
        old = (model.mask, model.observed)
        with self.assertRaises(ValueError):
            model.observe_public(row._asdict())
        with self.assertRaises(ValueError):
            model.observe_public(row._replace(action=True))
        self.assertEqual(old, (model.mask, model.observed))

    def test_credit_contradiction_fails_without_mutation(self):
        world = m.PublicWorld(m.PUBLIC_WORLDS[2])
        model = m.NativeCompositionalTrace()
        for action in m.exploration(m.PUBLIC_WORLDS[2]):
            model.observe_public(world.step(action))
        self.assertEqual(model.mask.bit_count(), 1)
        row = world.step(0)
        observed = m._earned(row)
        wrong_reward = -0.25 if observed[1] else 1.0
        before = (model.mask, model.observed)
        with self.assertRaises(ValueError):
            model.observe_public(row._replace(reward=wrong_reward))
        self.assertEqual(before, (model.mask, model.observed))

    def test_equal_strong_control_tie_no_novelty(self):
        report = m.study()
        self.assertEqual(report["source_simulated_actions"], 7680)
        self.assertEqual(report["native_minus_equal_symbolic_mean"], 0.0)
        self.assertEqual(report["native_minus_equal_symbolic_bootstrap_95"], [0.0, 0.0])
        self.assertGreater(report["means"]["native"], report["means"]["tabular"])
        self.assertLess(report["means"]["native"], report["means"]["oracle"])
        self.assertFalse(report["scientific_pass"])
        self.assertFalse(report["strong_control_advantage_gate"])
        self.assertFalse(report["protected_fkp17_first_use"])

    def test_step_budget(self):
        world = m.PublicWorld(m.PUBLIC_WORLDS[0])
        for action in range(m.EXPLORE + m.SCORE):
            world.step(action % m.ACTIONS)
        with self.assertRaises(ValueError):
            world.step(0)

    def test_no_previous_action_abstention_and_guards(self):
        model = m.NativeCompositionalTrace()
        self.assertEqual(model.choose((0,) + (8,) * 7, ()), 0)
        with self.assertRaises(ValueError):
            model.choose((0,) * 7, ())
        with self.assertRaises(ValueError):
            m._action(True)


if __name__ == "__main__":
    unittest.main()
