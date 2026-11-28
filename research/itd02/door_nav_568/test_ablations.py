"""Source-free falsification controls for ITD-02 #568.

These are conventional planning-reference controls; they do not prove native cognition.
"""
import unittest
from public_transition_planner import PublicTransitionPlanner

def trained():
    p = PublicTransitionPlanner()
    p.observe(b"start", [0, 1])
    p.learn(1, b"middle", 0, False)
    p.observe(b"middle", [0, 2])
    p.learn(2, b"goal", 1, True)
    return p

class AblationTests(unittest.TestCase):
    def test_no_planning_erases_two_step_preference(self):
        p = trained()
        p.observe(b"start", [0, 1])
        self.assertEqual(p.choose(horizon=2), 1)
        self.assertEqual(p.choose(horizon=1), 0)

    def test_no_retained_memory_erases_two_step_preference(self):
        p = PublicTransitionPlanner()
        p.observe(b"start", [0, 1])
        self.assertEqual(p.choose(horizon=2), 0)

    def test_wrong_action_consequence_changes_decision(self):
        p = PublicTransitionPlanner()
        p.observe(b"start", [0, 1])
        p.learn(0, b"middle", 0, False)
        p.observe(b"middle", [0, 2])
        p.learn(2, b"goal", 1, True)
        p.observe(b"start", [0, 1])
        self.assertEqual(p.choose(horizon=2), 0)

if __name__ == "__main__":
    unittest.main()
