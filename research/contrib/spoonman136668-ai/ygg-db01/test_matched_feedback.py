"""G34 structural negative-control tests; NOT scientific learning evidence."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = obj
    spec.loader.exec_module(obj)
    return obj


matched = module("ygg_db01_g34_matched", "matched_feedback.py")
local = module("ygg_db01_g34_local", "local_development.py")
native = module("ygg_db01_g34_native", "native_dg1a.py")


class G34MatchedControls(unittest.TestCase):
    def test_exact_marginal_energy_and_signed_amplitude_parity(self):
        for length in (16, 32, 64, 128):
            for seed in (0, 1, 2, 17, 123456789, 2**32 - 1):
                for outcome in (0, 1):
                    for condition in ("mapped", "reversed", "sham",
                                      "polarity_flip", "phase_shift"):
                        samples = matched.matched_feedback(
                            outcome, condition, length, seed)
                        self.assertEqual(len(samples), length)
                        self.assertEqual(samples.count(1.0), length // 4)
                        self.assertEqual(samples.count(-1.0), length // 4)
                        self.assertEqual(samples.count(0.0), length // 2)
                        self.assertEqual(sum(samples), 0.0)
                        self.assertEqual(sum(x * x for x in samples),
                                         length // 2)
                        self.assertEqual(sum(abs(x) for x in samples),
                                         length // 2)
                        self.assertLessEqual(max(abs(x) for x in samples), 1.0)
                    self.assertEqual(matched.matched_feedback(
                        outcome, "no_feedback", length, seed), (0.0,) * length)

    def test_temporal_regular_vs_irregular_and_deterministic_replay(self):
        for seed in (0, 1, 2, 17, 123456789, 2**32 - 1):
            regular = matched.matched_feedback(1, length=32, seed=seed)
            irregular = matched.matched_feedback(0, length=32, seed=seed)
            self.assertEqual(regular, matched.PATTERN * 8)
            self.assertNotEqual(regular, irregular)
            self.assertTrue(all(regular[i] == regular[i+4] for i in range(28)))
            self.assertTrue(any(irregular[i] != irregular[i+4] for i in range(28)))
            self.assertEqual(irregular, matched.matched_feedback(
                0, length=32, seed=seed))
            self.assertCountEqual(regular, irregular)

    def test_sham_reversed_polarity_and_phase_as_independent_ablations(self):
        for seed in (0, 1, 2, 17, 18):
            for outcome in (0, 1):
                base = matched.matched_feedback(outcome, "mapped", 16, seed)
                self.assertEqual(matched.matched_feedback(
                    outcome, "reversed", 16, seed),
                    matched.matched_feedback(1-outcome, "mapped", 16, seed))
                self.assertEqual(matched.matched_feedback(
                    outcome, "polarity_flip", 16, seed),
                    tuple(-x for x in base))
                self.assertEqual(matched.matched_feedback(
                    outcome, "phase_shift", 16, seed),
                    base[-1:] + base[:-1])
            self.assertEqual(matched.matched_feedback(
                0, "sham", 16, seed),
                matched.matched_feedback(1, "sham", 16, seed))
            self.assertEqual(matched.matched_feedback(
                0, "sham", 16, seed),
                matched.matched_feedback(seed & 1, "mapped", 16, seed))
        self.assertNotEqual(matched.matched_feedback(1, "polarity_flip"),
                            matched.matched_feedback(1, "phase_shift"))

    def test_rejects_invalid_inputs_before_any_generation(self):
        for bad in (True, False, 0.5, -1, 2, None):
            with self.assertRaises(ValueError):
                matched.matched_feedback(bad)
        for bad in (0, True, None, "unknown", "energy_matched", 7):
            with self.assertRaises(ValueError):
                matched.matched_feedback(1, bad)
        for bad in (4, 15, 17, 1025, 0, True, 16.0):
            with self.assertRaises(ValueError):
                matched.matched_feedback(1, length=bad)
        for bad in (-1, 2**32, True, 17.0, "17"):
            with self.assertRaises(ValueError):
                matched.matched_feedback(1, seed=bad)

    def test_fixed_update_budget_in_both_local_substrates(self):
        for condition in matched.CONDITIONS:
            frames = matched.matched_feedback(1, condition, 16, 17)
            spot = lambda s: tuple(tuple(s if (y, x) == (1, 1) else 0.0
                                         for x in range(4)) for y in range(4))
            fixture = local.LocalDevelopment()
            state = tuple(tuple((0.0, 0.0) for _ in range(4))
                          for _ in range(4))
            candidate = native.DG1APrototype()
            genotype = native.seeded_genome(17)
            phenotype = candidate.initial_state()
            for sample in frames:
                sensor = spot(sample)
                state = fixture.step(state, sensor)
                phenotype = candidate.step(phenotype, sensor, genotype)
            self.assertEqual(len(frames), 16)
            self.assertTrue(all(len(row) == 4 for row in state))
            self.assertTrue(all(len(row) == 4 for row in phenotype))
            self.assertTrue(all(cell[:2] == (0.0, 1.0)
                                for row in phenotype for cell in row))
            self.assertEqual(genotype, native.seeded_genome(17))

    def test_prereg_remains_unfrozen_and_primary_prohibited(self):
        draft = json.loads((HERE / "g33_prereg_draft.json").read_text("utf8"))
        self.assertEqual(draft["status"], "INCOMPLETE_NOT_FROZEN")
        self.assertIs(draft["authority"]["primary_execution_allowed"], False)
        self.assertIs(draft["authority"]["protected_first_use_allowed"], False)
        self.assertEqual(draft["development_diagnostics"]["g34"]["class"],
                         "MATCHED_MARGINAL_STRUCTURE_ONLY")
        self.assertIn("no_feedback_energy_unmatched",
                      draft["development_diagnostics"]["g34"]["limitations"])
        self.assertEqual(draft["unfilled_primary_fields"]["source_sha"], None)
        self.assertEqual(draft["unfilled_primary_fields"]["evaluator_sha256"],
                         None)


if __name__ == "__main__":
    unittest.main()
