"""WSP52 independent symbolic comparator developmental-only fixture contract."""
import unittest
from dataclasses import replace
from source import build_world, Observation
from symbolic_baseline import SymbolicCorpusLearner, _split, _hypotheses


class SymbolicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = build_world("SELFTEST", 9001, "identity")

    def test_segmentation_no_word_ids(self):
        self.assertEqual(len(_split("0"*15)), 7)
        self.assertFalse(_split("0"*9))
        for invalid in ("", "0012", "English"):
            with self.assertRaises(ValueError):
                _split(invalid)

    def test_observations_finite_and_missing_labels_unknown(self):
        m = SymbolicCorpusLearner()
        for row in self.world.phase_a:
            m.observe(row)
        self.assertEqual(m.actions, 36)
        with self.assertRaises(ValueError):
            m.observe(self.world.phase_a[0])
        self.assertEqual(m.predict((0,)*8, "0"*15), None)
        m.seal_a()
        with self.assertRaises(ValueError):
            m.seal_a()
        for row in self.world.phase_b:
            m.observe(row)
        with self.assertRaises(ValueError):
            m.observe(self.world.phase_b[0])
        m.finalize_b()
        self.assertEqual(m.actions, 42)
        with self.assertRaises(ValueError):
            m.observe(self.world.phase_b[0])
        with self.assertRaises(ValueError):
            m.use_phase("PRIMARY")

    def test_visible_effect_without_hidden_grammar(self):
        m = SymbolicCorpusLearner()
        for row in self.world.phase_a:
            m.observe(row)
        models = _hypotheses(m.phase_a)
        self.assertTrue(len(models) <= 3)
        for candidate in models:
            self.assertIn(candidate["slot"], (0,1,2))
            self.assertNotIn("_codebook", candidate)
            self.assertNotIn("_orders", candidate)

    def test_cold_restore_and_tamper(self):
        m = SymbolicCorpusLearner()
        for row in self.world.phase_a:
            m.observe(row)
        m.seal_a()
        for row in self.world.phase_b:
            m.observe(row)
        m.finalize_b()
        before = m.snapshot()
        restored = SymbolicCorpusLearner.restore(before)
        self.assertEqual(restored.snapshot(), before)
        for row in self.world.heldout_b[:8]:
            self.assertEqual(m.predict(row.before, row.acoustic_bits),
                             restored.predict(row.before, row.acoustic_bits))
        m.use_phase("A")
        restored.use_phase("A")
        for row in self.world.heldout_a[:8]:
            self.assertEqual(m.predict(row.before, row.acoustic_bits),
                             restored.predict(row.before, row.acoustic_bits))
        with self.assertRaises(ValueError):
            SymbolicCorpusLearner.restore(before + " ")
        with self.assertRaises(ValueError):
            SymbolicCorpusLearner.restore(before[:-1] + "x")

    def test_invisible_entity_cannot_be_oracle_labeled(self):
        m = SymbolicCorpusLearner()
        prior = len(m.phase_a)
        noop = Observation((0,)*8, "00101"*3, (0,)*8)
        m.observe(noop)
        self.assertEqual(m.actions, 1)
        self.assertEqual(len(m.phase_a), prior+1)
        self.assertEqual(_hypotheses(m.phase_a), ())

    def test_all_fixture_scores_recorded_not_promoted(self):
        from fixture_harness import learn_observations, score_observations
        from dataclasses import asdict
        import json
        rows = []
        for seed in (9001, 9002):
            for encoding in ("identity", "permuted", "rotated"):
                world = build_world("SELFTEST", seed, encoding)
                model = SymbolicCorpusLearner()
                learn_observations(model, world.phase_a)
                a = score_observations(model, world.heldout_a)
                model.seal_a()
                learn_observations(model, world.phase_b)
                model.finalize_b()
                b = score_observations(model, world.heldout_b)
                model.use_phase("A")
                retained = score_observations(model, world.heldout_a)
                self.assertEqual(model.actions, 42)
                self.assertEqual(a.total, 60)
                self.assertEqual(b.total, 90)
                self.assertEqual(retained.total, 60)
                self.assertEqual(
                    a.correct + a.abstentions + a.wrong_confident, 60)
                self.assertEqual(
                    b.correct + b.abstentions + b.wrong_confident, 90)
                rows.append({"seed": seed, "encoding": encoding,
                             "A": asdict(a), "B": asdict(b), "retained_A": asdict(retained),
                             "capacity_bits": model.capacity_bits(),
                             "validation_predictions": model.validation_predictions,
                             "parser_candidates": model.replay_parses})
        print("WSP52_SYMBOLIC_PROTOTYPE_SELFTEST "+json.dumps(
            rows, sort_keys=True, separators=(",", ":")), flush=True)
        self.assertEqual(len(rows), 6)

    def test_primary_cannot_enter_selftest_fixture(self):
        from fixture_harness import learn_observations
        # No generator call or protected seed, and no authorization here.
        # A guard around execution must be added before registered cohorts.
        self.assertFalse(hasattr(SymbolicCorpusLearner, "oracle_decode"))


if __name__ == "__main__":
    unittest.main()
