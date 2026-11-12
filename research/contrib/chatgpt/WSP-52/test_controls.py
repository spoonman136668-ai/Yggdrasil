"""WSP52 source/controls boundary tests: SELFTEST-only, not scientific outcomes."""
import json
import unittest
from dataclasses import dataclass

from source import Observation, build_world
from controls import WholeStreamTable, ErasedControl
from fixture_harness import run_selftest_controls, learn_observations, score_observations


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.world = build_world("SELFTEST", 9001, "identity")

    def test_no_compositional_credit_to_whole_stream(self):
        receipts = run_selftest_controls(self.world)
        for name in ("whole_stream", "erased"):
            arm = receipts["arms"][name]
            self.assertEqual(arm["exposed_actions"], 42)
            for k, n in (("phase_a", 60), ("phase_b", 90), ("a_retention_after_b", 60)):
                self.assertEqual(arm[k]["total"], n)
                self.assertEqual(arm[k]["correct"], 0)
                self.assertEqual(arm[k]["abstentions"], n)
                self.assertEqual(arm[k]["wrong_confident"], 0)
        self.assertTrue(receipts["arms"]["whole_stream"]["cold_restore_parity"])
        self.assertEqual(receipts["arms"]["erased"]["persistent_capacity_bits_upper_bound"], 0)

    def test_full_stream_recall_only_observed_state(self):
        source = self.world.phase_a[0]
        table = WholeStreamTable()
        table.observe(source)
        self.assertEqual(table.predict(source.before, source.acoustic_bits), source.after)
        changed_before = tuple((v + 1) % 4 for v in source.before)
        self.assertIsNone(table.predict(changed_before, source.acoustic_bits))
        self.assertIsNone(table.predict(source.before, source.acoustic_bits + "0"))

    def test_contradictory_observation_abstains_even_after_more_writes(self):
        row = Observation((0,) * 8, "010101010101", (1,) + (0,) * 7)
        opposite = Observation(row.before, row.acoustic_bits, (2,) + (0,) * 7)
        table = WholeStreamTable()
        table.observe(row)
        table.observe(opposite)
        table.observe(row)
        self.assertIsNone(table.predict(row.before, row.acoustic_bits))
        self.assertIsNone(WholeStreamTable.restore(table.snapshot()).predict(row.before, row.acoustic_bits))

    def test_restore_tamper_and_noncanonical_rejection(self):
        table = WholeStreamTable()
        table.observe(self.world.phase_a[0])
        raw = table.snapshot()
        self.assertEqual(WholeStreamTable.restore(raw).snapshot(), raw)
        with self.assertRaises(ValueError):
            WholeStreamTable.restore(raw + " ")
        with self.assertRaises(ValueError):
            WholeStreamTable.restore(raw[:-1] + "x")
        parsed = json.loads(raw)
        parsed["payload"]["experiences"] += 100
        with self.assertRaises(ValueError):
            WholeStreamTable.restore(json.dumps(parsed))

    def test_evaluation_api_does_not_pass_hidden_labels_or_answer(self):
        class Recording:
            def __init__(self):
                self.observed = []
                self.evaluated = []
            def observe(self, row):
                self.observed.append(row)
            def predict(self, before, acoustic_bits):
                self.evaluated.append((before, acoustic_bits))
                return None
        learner = Recording()
        learn_observations(learner, self.world.phase_a)
        score = score_observations(learner, self.world.heldout_a)
        self.assertEqual(score.abstentions, 60)
        self.assertEqual(len(learner.observed), 36)
        self.assertEqual(len(learner.evaluated), 60)
        self.assertTrue(all(type(row) is Observation for row in learner.observed))
        self.assertEqual(set(vars(learner.observed[0])),
                         {"before", "acoustic_bits", "after", "action_cost", "reset_cost"})
        self.assertTrue(all(isinstance(v, tuple) and isinstance(bits, str)
                            for v, bits in learner.evaluated))

    def test_fixture_rejects_registered_cohorts_before_scoring(self):
        from dataclasses import replace
        with self.assertRaises(PermissionError):
            run_selftest_controls(replace(self.world, cohort="PRIMARY"))

    def test_invalid_acoustic_and_state_rejected(self):
        table = WholeStreamTable()
        for bits in ("", "01012", "nonsense"):
            with self.assertRaises(ValueError):
                table.predict((0,) * 8, bits)
        with self.assertRaises(ValueError):
            table.predict((0,) * 7, "0101")


if __name__ == "__main__":
    unittest.main()
