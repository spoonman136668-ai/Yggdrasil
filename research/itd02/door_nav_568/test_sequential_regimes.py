"""Sequential retention and adaptation controls for learned feature cells."""
import unittest
from sequential_regimes import run

class SequentialRegimeTests(unittest.TestCase):
    def test_adapts_to_three_regimes_with_bounded_memory(self):
        result = run()
        phases = result["phases"]
        self.assertEqual([p["regime"] for p in phases], ["A", "B", "A"])
        self.assertEqual([p["selected_position"] for p in phases], [1, 0, 1])
        self.assertEqual([p["own_regime_correct"] for p in phases], [4, 4, 4])
        self.assertEqual([p["history_size"] for p in phases], [8, 8, 8])

    def test_reversals_expose_retention_loss(self):
        phases = run()["phases"]
        # Memory budget deliberately excludes previous regimes, so restoring
        # performance requires eight new source-free feedback observations.
        self.assertEqual(phases[1]["former_A_correct"], 2)
        self.assertEqual(phases[2]["former_B_correct"], 2)

    def test_repeatability(self):
        self.assertEqual(run(), run())

if __name__ == "__main__":
    unittest.main()
