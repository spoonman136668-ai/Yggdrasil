"""Source-free focused tests for the bounded action memory prototype."""
import unittest
from public_action_memory import PublicActionMemory

class TestPublicActionMemory(unittest.TestCase):
    def test_seven_legal_actions(self):
        m = PublicActionMemory()
        m.observe(b"frame", range(7), 0)
        self.assertIn(m.choose(), range(7))
        with self.assertRaises(ValueError):
            m.learn(9, b"next", 1, False)

    def test_public_feedback_changes_choice(self):
        m = PublicActionMemory()
        m.observe(b"frame", range(7), 0)
        self.assertEqual(m.choose(), 0)
        m.learn(0, b"next", -1, False)
        m.observe(b"frame", range(7), 1)
        self.assertEqual(m.choose(), 1)
        m.learn(1, b"next", 1, True)
        m.observe(b"frame", range(7), 2)
        self.assertEqual(m.choose(), 1)

    def test_checkpoint(self):
        m = PublicActionMemory()
        m.observe(b"frame", [0, 1], 0)
        m.learn(0, b"next", 1, True)
        raw = m.checkpoint()
        self.assertEqual(PublicActionMemory.restore(raw).checkpoint(), raw)

    def test_source_public_only(self):
        m = PublicActionMemory()
        with self.assertRaises(ValueError):
            m.observe({"hidden_map": True}, range(7), 0)
        with self.assertRaises(ValueError):
            m.observe(b"frame", [7], 0)

if __name__ == "__main__":
    unittest.main()
