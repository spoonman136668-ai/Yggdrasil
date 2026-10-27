"""Bounded training-history and feature drift tests."""
import unittest
from learned_byte_cells import LearnedByteCells

class LearnedHistoryTests(unittest.TestCase):
    def test_bounded_replay_history_under_repeated_feedback(self):
        agent = LearnedByteCells(feature_positions=2, max_examples=8)
        for step in range(64):
            frame = (b"x" if step % 2 else b"y") + (b"A" if (step // 2) % 2 else b"B") + b"-train"
            correct = 1 if frame[1:2] == b"A" else 0
            agent.observe(frame, [0, 1])
            agent.learn(step % 2, b"terminal", int((step % 2) == correct), True)
            self.assertLessEqual(len(agent.examples), 8)
            self.assertLessEqual(len(agent.cells), agent.max_groups)

    def test_recent_feedback_can_change_selected_feature(self):
        agent = LearnedByteCells(feature_positions=2, max_examples=8)
        # Balanced nuisance, predictive feature at position 1.
        for nuisance in (b"x", b"y"):
            for signal, correct in ((b"A", 1), (b"B", 0)):
                for action in (0, 1):
                    agent.observe(nuisance+signal+b"-train", [0, 1])
                    agent.learn(action, b"terminal", int(action == correct), True)
        self.assertEqual(agent.feature_position, 1)
        # Replacement feedback changes the predictive position to zero.
        for nuisance in (b"x", b"y"):
            for signal in (b"A", b"B"):
                for action in (0, 1):
                    agent.observe(nuisance+signal+b"-shift", [0, 1])
                    agent.learn(action, b"terminal", int(action == (1 if nuisance == b"x" else 0)), True)
        self.assertEqual(len(agent.examples), 8)
        self.assertEqual(agent.feature_position, 0)

    def test_reject_unbounded_history_configuration(self):
        for count in (0, 7, 4097, 12.5, True):
            with self.assertRaises(ValueError):
                LearnedByteCells(max_examples=count)

if __name__ == "__main__":
    unittest.main()
