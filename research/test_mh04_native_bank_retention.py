"""MH04 source/prereg controls: no primary cohort actions or rewards executed."""
import unittest

from research import mh04_native_bank_retention as m
from research import mh03_checkpoint_bank_readback as mh03


class MH04FrozenProtocolTests(unittest.TestCase):
    def test_pinned_source_and_genuinely_disjoint_synthetic_cohort(self):
        m.source_guard()
        self.assertEqual(m.SEEDS, (401, 409, 419, 421, 431))
        self.assertEqual(m.MAPS, {"F": (2, 1, 0, 2), "G": (1, 0, 1, 2)})
        self.assertEqual(m.A, (0, 1, 2, 1))
        self.assertEqual(m.STOPS, (1, 2, 4, 8, 24, 48))
        self.assertEqual(m.bank.SIZE, 2264)

    def test_source_schedule_and_disjoint_phase_names(self):
        # Schedule structure only. NO outcomes or learning generated in tests.
        for seed in m.SEEDS:
            for phase in ("A", "X", "return"):
                rows = m.events(seed, phase)
                self.assertEqual(len(rows), 240)
                self.assertEqual(len(set(rows)), 240)
                self.assertEqual(rows, m.events(seed, phase))
                for block in range(20):
                    sample = rows[block*12:(block+1)*12]
                    self.assertEqual({(cue, action) for cue, action, _ in sample},
                                     {(cue, action) for cue in range(4)
                                      for action in range(3)})
        for seed, phase in ((101, "A"), (401, "bad"), (True, "X"), (431, "a")):
            with self.assertRaises(ValueError):
                m.events(seed, phase)

    def test_source_only_conventional_baseline_does_not_use_phase_label(self):
        model = m.FullHistory()
        b = model.checkpoint()
        with self.assertRaises(ValueError):
            model.learn(4, 0, 1.0)
        self.assertEqual(model.checkpoint(), b)
        model.learn(0, 2, 1.0)
        model.learn(0, 2, -1.0)
        self.assertEqual(model.scores(0), [0.0, 0.0, 0.0])
        self.assertEqual(model.updates, 2)
        self.assertEqual(m.arm_readout(model, m.A)["bytes"],
                         len(model.checkpoint()))

    def test_policy_score_uses_existing_tolerant_source_tie_break(self):
        scores = [[1.0, 0.0, -1.0], [0.0, 1.0, 0.0],
                  [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]
        self.assertEqual(m.score4(scores, m.A), 1.0)
        self.assertEqual(m.score4(scores, m.MAPS["G"]), 0.0)
        with self.assertRaises(ValueError):
            m.score4(scores[:3], m.A)

    def test_stored_bank_readout_is_offline_only(self):
        # This does not execute a reward schedule or the primary cohort.
        source = mh03.SOURCE
        self.assertTrue(source.is_file())
        self.assertTrue(m.PREREG_SHA)
        self.assertTrue(m.TRIAL.startswith("MH04-SYNTH-"))
        self.assertTrue(m.bank.inspect_snapshot)
        self.assertEqual(m.bank.N, 8)


if __name__ == "__main__":
    unittest.main()
