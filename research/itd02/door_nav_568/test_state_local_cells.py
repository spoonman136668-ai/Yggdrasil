"""State-conditioned local R7 cells: public-only source-free discrimination."""
import unittest
from state_local_cells import StateLocalActionCells

class StateLocalTests(unittest.TestCase):
    def test_opposite_actions_in_distinct_public_states(self):
        p = StateLocalActionCells()
        for _ in range(3):
            for frame, action in ((b"left", 0), (b"right", 1)):
                p.observe(frame, [0, 1])
                p.learn(action, b"next", 1, True)
        p.observe(b"left", [0, 1])
        self.assertEqual(p.choose(), 0)
        p.observe(b"right", [0, 1])
        self.assertEqual(p.choose(), 1)

    def test_capacity_and_owned_action(self):
        p = StateLocalActionCells(max_states=1)
        p.observe(b"a", [0])
        with self.assertRaises(ValueError):
            p.learn(1, b"b", 1, False)
        p.learn(0, b"b", 1, False)
        p.observe(b"c", [0])
        with self.assertRaises(ValueError):
            p.learn(0, b"d", 1, True)

    def test_no_delayed_credit_without_local_reward(self):
        p = StateLocalActionCells()
        p.observe(b"start", [0, 1])
        p.learn(1, b"middle", 0, False)
        p.observe(b"middle", [2])
        p.learn(2, b"goal", 1, True)
        p.observe(b"start", [0, 1])
        self.assertEqual(p.choose(), 0)

if __name__ == "__main__":
    unittest.main()
