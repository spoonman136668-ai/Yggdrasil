"""G33 structural tests of an isolated native-shared-rule *candidate* only."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ygg_db01_g33_native", HERE / "native_dg1a.py")
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class NativeCandidateG33(unittest.TestCase):
    def setUp(self):
        self.model = mod.DG1APrototype()
        self.genome = mod.seeded_genome(17)
        self.quiet = tuple(tuple(0.0 for _ in range(4)) for _ in range(4))
        self.spot = tuple(tuple(1.0 if (y, x) == (1, 1) else 0.0
                                for x in range(4)) for y in range(4))
        self.state = self.model.initial_state()

    def test_shared_fixed_capacity_genome_and_seed_replay(self):
        self.assertEqual(mod.CHANNELS, 16)
        self.assertEqual(mod.GENOME_PARAMETER_COUNT, 398)
        self.assertEqual(self.genome.parameter_count, 398)
        self.assertEqual(self.genome, mod.seeded_genome(17))
        self.assertNotEqual(self.genome, mod.seeded_genome(18))
        actual = self.model.step(self.state, self.spot, self.genome)
        self.assertEqual(actual, self.model.step(self.state, self.spot, self.genome))
        self.assertEqual(len(actual), 4)
        self.assertTrue(all(len(row) == 4 and len(cell) == 16
                            for row in actual for cell in row))
        self.assertTrue(all(actual[y][x][:2] == self.state[y][x][:2]
                            for y in range(4) for x in range(4)))

    def test_moore_locality_and_no_global_feedback(self):
        base = self.model.step(self.state, self.quiet, self.genome)
        changed = self.model.step(self.state, self.spot, self.genome)
        self.assertEqual(changed[3][3], base[3][3])
        self.assertNotEqual(changed[1][1], base[1][1])
        perturbed = [list(row) for row in self.state]
        perturbed[0][0] = perturbed[0][0][:2] + (1.0,) + (0.0,) * 13
        other = self.model.step(tuple(map(tuple, perturbed)),
                                self.quiet, self.genome)
        self.assertEqual(base[3][3], other[3][3])
        self.assertNotEqual(base[0][1], other[0][1])

    def test_real_development_parameter_update_is_bounded(self):
        before = self.model.step(self.state, self.spot, self.genome)[1][1][2]
        target = 0.75
        learned = self.model.fit_one_cell(
            self.state, self.spot, self.genome, 1, 1, target)
        after = self.model.step(self.state, self.spot, learned)[1][1][2]
        self.assertLess(abs(after - target), abs(before - target))
        self.assertNotEqual(learned, self.genome)
        self.assertEqual(learned.parameter_count, self.genome.parameter_count)
        self.assertEqual(self.model.step(self.state, self.spot, self.genome)[1][1][2],
                         before)
        self.assertEqual(learned, self.model.fit_one_cell(
            self.state, self.spot, self.genome, 1, 1, target))

    def test_guard_rejects_capacity_and_bad_signals(self):
        for args in ({"width": 17}, {"height": 17}, {"rate": float("nan")},
                     {"rate": 0.3}, {"width": 0}):
            with self.assertRaises(ValueError):
                mod.DG1APrototype(**args)
        for seed in (-1, True, 2**32):
            with self.assertRaises(ValueError):
                mod.seeded_genome(seed)
        with self.assertRaises(ValueError):
            self.model.step(self.state, self.spot, object())
        bad = tuple(tuple(float("nan") if (y, x) == (0, 0) else 0.0
                          for x in range(4)) for y in range(4))
        with self.assertRaises(ValueError):
            self.model.step(self.state, bad, self.genome)
        with self.assertRaises(ValueError):
            self.model.fit_one_cell(self.state, self.spot, self.genome,
                                    1, 1, 0.2, learning_rate=2.0)
        with self.assertRaises(ValueError):
            self.model.fit_one_cell(self.state, self.spot, self.genome,
                                    9, 1, 0.2)

    def test_prereg_draft_is_fail_closed_and_no_primary_execution(self):
        draft = json.loads((HERE / "g33_prereg_draft.json").read_text("utf-8"))
        self.assertEqual(draft["schema"], "yggdrasil.db01.g33-prereg-draft.v1")
        self.assertEqual(draft["status"], "INCOMPLETE_NOT_FROZEN")
        self.assertIs(draft["authority"]["primary_execution_allowed"], False)
        self.assertIs(draft["authority"]["production_authority"], False)
        for key in ("source_sha", "independent_custodian", "task_hash_sha256",
                    "evaluator_sha256", "cohorts_sha256", "primary_thresholds"):
            self.assertIsNone(draft["unfilled_primary_fields"][key])
        self.assertEqual(set(draft["feedback_conditions"]),
                         {"mapped", "reversed", "sham", "no_feedback"})
        self.assertEqual(draft["candidate_class"], "ISOLATED_DEVELOPMENT_PROTOTYPE")
        self.assertNotIn("approved", draft["status"].lower())


if __name__ == "__main__":
    unittest.main()
