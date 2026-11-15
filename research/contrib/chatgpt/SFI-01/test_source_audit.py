"""Source contract checks only. Never open original FKP-17 held cohorts."""
import unittest

import source_audit as src


class SourceContractTests(unittest.TestCase):
    def test_fixed_world_grid_and_forbidden_seeds(self):
        self.assertEqual(len(src.WORLD_SEEDS), 32)
        self.assertEqual(len(src.FAMILIES), 4)
        self.assertEqual({(s // 8, s % 8) for s in src.WORLD_SEEDS},
                         {(f, shift) for f in range(4) for shift in range(8)})
        for bad in (978500, 978531, 978600, 978663, -1, 32, True):
            with self.assertRaises(PermissionError):
                src.collect_public(bad, (0,))

    def test_same_public_actions_and_source_replay_are_deterministic(self):
        seed = src.WORLD_SEEDS[0]
        tape = src.exploration(seed)
        self.assertEqual(len(tape), 24)
        self.assertEqual(tape, src.exploration(seed))
        self.assertEqual(src.collect_public(seed, tape), src.collect_public(seed, tape))

    def test_public_only_fields_and_continuous_observations(self):
        rows = src.collect_public(4, src.exploration(4))
        self.assertEqual(len(rows), 24)
        for i, row in enumerate(rows):
            self.assertEqual(row._fields, src.PUBLIC_FIELDS)
            self.assertEqual(len(row.before), 8)
            self.assertEqual(len(row.after), 8)
            self.assertLessEqual(len(row.history), 16)
            self.assertFalse(hasattr(row, '_family'))
            self.assertFalse(hasattr(row, '_shift'))
            self.assertFalse(hasattr(row, 'alternatives'))
            if i:
                self.assertEqual(rows[i - 1].after, row.before)
            if row.history:
                self.assertEqual(row.history[-1].after, row.before)
            self.assertTrue(all(old._fields == src.PublicPrior._fields
                                for old in row.history))

    def test_delayed_reward_is_earned_from_real_prior_action(self):
        w = src._SourceWorld(0)
        rows = [w.step(a) for a in (0, 1, 2, 3)]
        self.assertEqual([r.reward for r in rows[:3]], [0.0] * 3)
        prior = rows[0].action
        eligible = rows[1]
        first = src._target(w._family, w._shift, prior, 0, eligible.before[0] & 1)
        self.assertEqual(rows[3].reward > 0, eligible.action == first)

    def test_invalid_action_and_capacity_do_not_mutate_source(self):
        env = src._SourceWorld(2)
        before = (env.state, env.public_history(), env._steps)
        with self.assertRaises(ValueError):
            env.step(True)
        with self.assertRaises(ValueError):
            env.step(8)
        self.assertEqual(before, (env.state, env.public_history(), env._steps))
        for i in range(src.EXPLORATION + src.SCORING):
            env.step(i % 8)
        with self.assertRaises(ValueError):
            env.step(0)

    def test_source_hypothesis_signature_is_public(self):
        tape = src.exploration(1)
        self.assertGreaterEqual(src._audited_matches(1, tape, 8), 1)
        self.assertGreaterEqual(src._audited_matches(1, tape, 24), 1)

    def test_actual_goal_events_have_done_and_episode_reset(self):
        env = src._SourceWorld(7)
        for action in src.exploration(7):
            row = env.step(action)
            if row.done:
                self.assertEqual(row.reward, 1.0)
                self.assertEqual(env.public_history(), ())
        for _ in range(src.SCORING):
            row = env.step(src._choose_oracle(env))
            if row.done:
                self.assertEqual(row.reward, 1.0)
                self.assertEqual(env.public_history(), ())

    def test_prefix_diagnostic_does_not_change_true_source(self):
        seed = 5
        tape = src.exploration(seed)
        ref = src.collect_public(seed, tape)
        src._audited_matches(seed, tape, 8)
        src._audited_matches(seed, tape, 24)
        self.assertEqual(ref, src.collect_public(seed, tape))


if __name__ == '__main__':
    unittest.main()
