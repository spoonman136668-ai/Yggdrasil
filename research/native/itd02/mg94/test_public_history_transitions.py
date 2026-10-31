"""Synthetic development tests; no original Farama environment or native success claim."""
import unittest
from research.native.itd02.mg94.public_history_transitions import PublicHistoryTransitions


class PublicHistoryTests(unittest.TestCase):
    def test_history_alias_discrimination_and_cold_restore(self):
        model = PublicHistoryTransitions()
        # Identical current public bit (0), identical action (1), different
        # publicly observed immediate history (prior 0 versus prior 1).
        for prior, expected in ((0, 0), (1, 1)):
            for _ in range(5):
                model.begin(prior)
                model.select(0)
                model.feedback(0)
                model.select(1)
                model.feedback(expected)
        model.begin(0)
        model.select(0)
        model.feedback(0)
        self.assertEqual(model.predict(1), (0, 5))
        model.begin(1)
        model.select(0)
        model.feedback(0)
        self.assertEqual(model.predict(1), (5, 5))
        saved = model.snapshot()
        restored = PublicHistoryTransitions.restore(saved)
        self.assertEqual(restored.snapshot(), saved)
        self.assertEqual(restored.predict(1), (5, 5))

    def test_selected_only_and_pending_snapshot_rejected(self):
        m = PublicHistoryTransitions()
        m.begin(0)
        self.assertIsNone(m.predict(1))
        with self.assertRaises(ValueError):
            m.feedback(1)
        m.select(0)
        with self.assertRaises(ValueError):
            m.snapshot()
        with self.assertRaises(ValueError):
            m.select(1)
        m.feedback(1)
        self.assertIsNone(m.predict(0))

    def test_integrity_and_input_rejection(self):
        m = PublicHistoryTransitions()
        with self.assertRaises(ValueError):
            m.begin(True)
        m.begin(0)
        m.select(0)
        m.feedback(1)
        saved = m.snapshot()
        with self.assertRaises(ValueError):
            PublicHistoryTransitions.restore(saved[:-1] + b"x")


if __name__ == "__main__":
    unittest.main()
