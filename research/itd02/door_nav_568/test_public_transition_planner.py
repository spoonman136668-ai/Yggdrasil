import unittest
from public_transition_planner import PublicTransitionPlanner

class TransitionTests(unittest.TestCase):
    def test_two_step_planning_and_legal_actions(self):
        p = PublicTransitionPlanner()
        p.observe(b"start", [0, 1])
        p.learn(1, b"middle", 0, False)
        p.observe(b"middle", [0, 2])
        p.learn(2, b"goal", 1, True)
        p.observe(b"start", [0, 1])
        self.assertEqual(p.choose(horizon=1), 0)
        self.assertEqual(p.choose(horizon=2), 1)
        p.observe(b"start", [0])
        self.assertEqual(p.choose(horizon=2), 0)

    def test_checkpoint_and_capacity(self):
        p = PublicTransitionPlanner(capacity=1)
        p.observe(b"a", [0])
        p.learn(0, b"b", 1, True)
        raw = p.checkpoint()
        q = PublicTransitionPlanner.restore(raw)
        self.assertEqual(raw, q.checkpoint())
        q.observe(b"c", [0])
        with self.assertRaises(ValueError):
            q.learn(0, b"d", 0, False)

    def test_action_and_public_frame_validation(self):
        p = PublicTransitionPlanner()
        with self.assertRaises(ValueError):
            p.observe({"private": 1}, [0])
        p.observe(b"frame", [0])
        with self.assertRaises(ValueError):
            p.learn(1, b"next", 1, False)

if __name__ == "__main__":
    unittest.main()
