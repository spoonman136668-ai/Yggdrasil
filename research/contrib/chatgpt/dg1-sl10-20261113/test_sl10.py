"""DG1-SL10 frozen physical interventions, oracle exclusion and custody."""
import json
import unittest
from pathlib import Path

from sl10 import (
    ARMS, AUDITS, COHORTS, FLIPS, FREEZE, PAIRS,
    ExactBayes, World, candidate_choose, candidate_score,
    model_for, one_world, sl09, trial,
)


class SL10Tests(unittest.TestCase):
    def test_frozen_prereg_and_paid_budget(self):
        p = json.loads((Path(__file__).parent / "prereg.json").read_text())
        self.assertEqual(FREEZE, "43d7307c3bcaf2862c4312583c6b220766feb04e")
        self.assertEqual(p["status"],
                         "FROZEN_BEFORE_IMPLEMENTATION_AND_PRIMARY_OUTCOMES")
        self.assertEqual(p["budgets"]["charged_physical_steps"], 23040)
        self.assertEqual(p["budgets"]["paid_causal_observations"], 20160)
        self.assertEqual(len(ARMS), 9)
        self.assertEqual(sum(map(len, COHORTS.values())), 32)
        self.assertEqual(len(FLIPS), 10)
        self.assertEqual(AUDITS, (60, 64, 72, 80))

    def test_world_pays_for_each_choice_and_forbids_oracle_as_training(self):
        for cohort, seeds in COHORTS.items():
            w = World(seeds[0], cohort)
            state = seeds[0] % 16
            count = {"causal": 0, "flip": 0}
            for step in range(80):
                chosen = 0 if step >= 60 and step not in FLIPS else None
                kind, action, next_state = w.step(state, step, chosen)
                count[kind] += 1
                self.assertIn(next_state, (state, state ^ (1 << action)))
                state = next_state
            self.assertEqual(count, {"causal": 70, "flip": 10})
            self.assertEqual(w.paid, 80)
            with self.assertRaises(ValueError):
                w.step(state, 79, 0)
            with self.assertRaises(ValueError):
                w.audit_truth(0, 0, 79)
        with self.assertRaises(ValueError):
            World(102001, "RETURN_A")
        w = World(103001, "RETURN_A")
        with self.assertRaises(ValueError):
            w.step(0, 0, 2)
        with self.assertRaises(ValueError):
            w.step(0, 60)
        with self.assertRaises(TypeError):
            ExactBayes().observe(0, 0, 1, hidden_program=(1, 2, 3))

    def test_true_independent_conventional_grammar_and_paid_learning(self):
        x = ExactBayes()
        self.assertEqual(len(sl09.MASKS), 4)
        self.assertTrue(all(len(s) == 216 for s in sl09.MASKS.values()))
        predictions = [x.predict(s, a) for s in range(16) for a in range(4)]
        self.assertEqual(len(predictions), 64)
        for s in range(16):
            for a in range(4):
                self.assertGreaterEqual(x.uncertainty(s, a), 0)
        x.observe(0, 0, 1)
        self.assertEqual(x.causal_events, 1)
        with self.assertRaises(ValueError):
            x.observe(0, 0, 2)
        with self.assertRaises(ValueError):
            x.choose(0, 59)
        with self.assertRaises(ValueError):
            x.choose(0, 62)

    def test_frozen_native_candidate_disagreement_uses_only_paid_memory(self):
        c = model_for("candidate_active")
        self.assertEqual(c.arm, "candidate_compositional_episodic")
        for action in range(4):
            self.assertIsInstance(candidate_score(c, 1, action), int)
        self.assertIn(candidate_choose(c, 0, 60), range(4))
        self.assertIn(candidate_choose(c, 0, 60, sham=True), range(4))
        c.observe(0, 0, 0)
        self.assertIn(candidate_choose(c, 0, 60), range(4))
        with self.assertRaises(TypeError):
            c.observe(0, 0, 1, hidden_phase="B")
        with self.assertRaises(ValueError):
            candidate_choose(c, 0, 62)
        with self.assertRaises(ValueError):
            candidate_choose(model_for(
                "candidate_no_episodic_on_candidate"), 0, 60)

    def test_bayesian_checkpoint_round_trip_and_tamper_negative(self):
        x = ExactBayes()
        for i in range(12):
            state = i % 16
            action = i % 4
            x.observe(state, action, state)
        original = x.snapshot()
        self.assertLessEqual(len(original), 8192)
        y = ExactBayes.restore(original)
        self.assertEqual(y.snapshot(), original)
        self.assertEqual(
            [x.predict(s, a) for s in range(16) for a in range(4)],
            [y.predict(s, a) for s in range(16) for a in range(4)],
        )
        for bad in (original[:-1], original + b" ",
                    bytes([original[0] ^ 1]) + original[1:]):
            with self.assertRaises(ValueError):
                ExactBayes.restore(bad)
        for _ in range(58):
            x.observe(0, 0, 0)
        with self.assertRaises(ValueError):
            x.observe(0, 0, 0)

    def test_physical_paired_replay_and_cold_restore_all_nine_arms(self):
        result = one_world(103001, "RETURN_A")
        self.assertEqual(set(result["arms"]), set(ARMS))
        r = result["arms"]
        self.assertEqual(len({z["pre_cold_trace_sha256"]
                              for z in r.values()}), 1)
        for group in PAIRS:
            self.assertEqual(len({r[a]["trace_sha256"] for a in group}), 1)
        for arm, z in r.items():
            self.assertEqual(z["paid_steps"], 80, arm)
            self.assertEqual(z["charged_flips"], 10, arm)
            self.assertEqual(z["causal_observations"], 70, arm)
            self.assertLessEqual(z["cold_checkpoint_bytes"], 8192, arm)
            self.assertLessEqual(z["final_checkpoint_bytes"], 8192, arm)
            self.assertEqual(len(z["paid_trace"]), 80)
            self.assertEqual(sum(z["prequential"].values()), 70)
            for point in AUDITS:
                values = z["stage_audits"][str(point)]
                self.assertEqual(sum(values[k] for k in
                                 ("correct", "wrong_confident", "abstained")),
                                 64, arm)

    def test_replay_plan_invalid_and_no_free_choices(self):
        with self.assertRaises(ValueError):
            trial(103001, "RETURN_A", "candidate_active",
                  "replay", replay_plan=[None])
        with self.assertRaises(ValueError):
            trial(103001, "RETURN_A", "nonsense", "candidate")
        with self.assertRaises(ValueError):
            ExactBayes().choose(0, 78)


if __name__ == "__main__":
    unittest.main()
