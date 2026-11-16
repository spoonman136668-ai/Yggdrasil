"""NKR-17 exact all-random-schedules robustness/negative qualification."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/"research/contrib/chatgpt/NKR-17/experiment.py"
spec = importlib.util.spec_from_file_location("nkr17_audit", SCRIPT)
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


class ExhaustiveInterventionAuditTests(unittest.TestCase):
    def test_frozen_reused_worlds_exact_uniform_random_distribution(self):
        v = study.run_frozen()
        self.assertTrue(v["engineering_contract_pass"])
        self.assertFalse(v["scientific_pass"])
        self.assertFalse(v["native_accepted"])
        self.assertFalse(v["external_authentic_experience"])
        self.assertEqual(v["worlds"],12)
        self.assertEqual(v["schedules_per_world"],56)
        self.assertEqual(v["total_random_schedule_arms"],672)
        self.assertEqual(v["total_random_schedule_public_actions"],1344)
        self.assertEqual(v["native_active_total_correct"],56)
        self.assertEqual(v["original_seed_random_total_correct"],38)
        self.assertEqual(v["active_vs_one_seed_extra_correct"],18)
        self.assertEqual(v["old_retention_correct"],384)
        self.assertEqual(v["all_672_schedule_confidently_wrong"],0)
        self.assertEqual(v["random_assignment_count"],str(56**12))
        self.assertEqual(sum(v["random_total_score_histogram"].values()),56**12)
        self.assertEqual(len(v["per_world"]),12)
        self.assertEqual(v["random_robustness_threshold_met"],
            v["classification"]=="EXHAUSTIVE_RANDOM_CONTROL_DEV_ROBUST")
        tail = Fraction(v["random_tail_at_or_above_active_exact"])
        self.assertGreaterEqual(tail,0)
        self.assertLessEqual(tail,1)
        self.assertEqual(v["random_tail_assignments"],
                         str(tail.numerator*(56**12)//tail.denominator))
        self.assertTrue(v["original_model_source_unmodified"])

    def test_56_ordered_random_without_replacement_include_all_pairs(self):
        self.assertEqual(len(study.ALL_SCHEDULES),56)
        self.assertEqual(len(set(study.ALL_SCHEDULES)),56)
        self.assertEqual({frozenset(x) for x in study.ALL_SCHEDULES},
                         {frozenset((a,b)) for a in study.COLD
                          for b in study.COLD if a!=b})
        self.assertEqual(len({frozenset(x) for x in study.ALL_SCHEDULES}),28)
        for a,b in study.ALL_SCHEDULES:
            self.assertNotEqual(a,b)
            self.assertIn((b,a),study.ALL_SCHEDULES)

    def test_every_two_action_schedule_only_scores_six_unprobed(self):
        for world in (0,3,7,11):
            for schedule in study.ALL_SCHEDULES:
                r=study.run_ordered_schedule(world,schedule)
                self.assertEqual(r["public_extra_actions"],2)
                self.assertEqual(r["unprobed_cold_queries"],6)
                self.assertEqual(r["correct"]+r["abstentions"],6)
                self.assertEqual(r["correct"],r["covered"])
                self.assertEqual(r["wrong"],0)
                self.assertEqual(len(r["selected_receipts"]),2)
                self.assertNotEqual(r["selected_receipts"][0],
                                    r["selected_receipts"][1])

    def test_independent_entropy_control_matches_original_native_action_choices(self):
        for world in range(12):
            chosen=study.native.run_one_world(world,"structured","active")
            schedule=tuple(chosen["selected"])
            source_safe=study.run_ordered_schedule(
                world,schedule,assert_active=True)
            self.assertEqual(source_safe["correct"],
                             chosen["unprobed_generalization_correct"])
            self.assertEqual(source_safe["covered"],
                             chosen["unprobed_generalization_coverage"])
            self.assertEqual(source_safe["wrong"],0)

    def test_source_visible_only_and_wrong_fixtures_rejected(self):
        env=study.fixture.IndependentActionWorld(4)
        source=study.fixture.observations(env)
        baseline=study.fit_initial_public(source)
        self.assertIn(study.fixture.AND_MASKS[4],baseline[2])
        with self.assertRaisesRegex(ValueError,
                "NKR17_INITIAL_EVIDENCE_ACTION_SEQUENCE_DRIFT"):
            study.fit_initial_public(list(reversed(source)))
        corrupted=[list(row) for row in source]
        for row in corrupted:
            if row[1]==3 and row[2]==0:
                row[3]^=1
        with self.assertRaisesRegex(ValueError,
                "NKR17_INITIAL_VISIBLE_BASELINE_INVALID"):
            study.fit_initial_public(corrupted)
        with self.assertRaisesRegex(ValueError,
                "NKR17_PUBLIC_OBSERVATION_CONTRADICTS_ALL_MASKS"):
            study.filter_observation((3,),3,0)
        self.assertEqual(set(study.COLD)&set(study.TRAIN),set())

    def test_schedule_refusals_and_active_selection_provenance(self):
        for invalid in ((6,6),(6,0),(17,6),(6,),(6,7,9),
                        (True,7)):
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                study.run_ordered_schedule(0,invalid)
        with self.assertRaisesRegex(ValueError,
                "NKR17_ACTIVE_POLICY_NOT_INDEPENDENT_ENTROPY_MAX"):
            study.run_ordered_schedule(0,(15,14),assert_active=True)
        with self.assertRaisesRegex(ValueError,
                "NKR17_SCHEDULE_OUTSIDE_FROZEN_SOURCE_SCOPE"):
            study.run_ordered_schedule(12,(6,7))

    def test_integer_random_distribution_exact_and_quantiles(self):
        h=Counter({1:28,2:28})
        dp=study.exact_distribution([h]*12)
        self.assertEqual(sum(dp.values()),56**12)
        self.assertEqual(dp[12],28**12)
        self.assertEqual(dp[24],28**12)
        self.assertEqual(sum(k*v for k,v in dp.items()),
                         18*(56**12))
        self.assertEqual(study.quantile(dp,50,100),18)
        with self.assertRaisesRegex(ValueError,
                "NKR17_NOT_56_UNIFORM_ORDERED_RANDOM_POLICIES"):
            study.exact_distribution([Counter({0:55})])

if __name__=="__main__":
    unittest.main()
