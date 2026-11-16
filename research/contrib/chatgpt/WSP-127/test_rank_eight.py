"""WSP127 high-first source-safe engineering and negative-control regression."""
import json
from unittest import TestCase
from unittest.mock import patch

import source as S
import numeric as N
import controls as C
import experiment as E

class RankEightEvidenceTests(TestCase):
    def test_frozen_full_128_law_equal_budget_protocol(self):
        result = E.run_engineering()
        print("WSP127_FINAL_ENGINEERING_JSON=" + S.canon(result))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["original_first_use"])
        self.assertFalse(result["native_admission"])
        self.assertTrue(result["cold_retention"])
        self.assertTrue(result["post_interference"])
        self.assertTrue(result["symbolic_matched"])
        self.assertEqual(result["strong_trained_conventional"], "UNQUALIFIED_NOT_RUN")
        fit = result["fit"]
        self.assertEqual(sum(fit["rank_histogram"].values()), 128)
        for arm in E.ARMS:
            self.assertEqual(fit["scores"][arm]["held"], 393216)
            self.assertEqual(fit["scores"][arm]["source_calls"], 131072)
            self.assertEqual(result["transfer"]["scores"][arm]["held"], 1048576)
            self.assertEqual(result["transfer"]["scores"][arm]["source_calls"], 0)
            self.assertEqual(result["out_family"]["scores"][arm]["held"], 262144)
            self.assertEqual(result["out_family"]["scores"][arm]["source_calls"], 0)
        for cohort in ("fit", "transfer", "out_family"):
            scores = (result["fit"]["scores"] if cohort == "fit"
                      else result[cohort]["scores"])
            self.assertEqual(scores["ADAPTIVE_NUMERIC"],
                             scores["ADAPTIVE_OPTIMIZED_GF2"])
            self.assertEqual(scores["FIXED_NUMERIC"],
                             scores["FIXED_OPTIMIZED_GF2"])
        self.assertEqual(result["transfer"]["worlds"], 256)
        self.assertEqual(result["out_family"]["worlds"], 64)
        self.assertEqual(fit["paired_bootstrap"]["resamples"], 10000)
        self.assertEqual(fit["paired_bootstrap"]["seed"], 127)
        self.assertEqual(result["fit"]["scores"]["ADAPTIVE_NUMERIC"]["wrong_confident"], 0)
        self.assertIn(result["status"],
            ("DEVELOPMENT_NO_GO", "DEVELOPMENT_MIXED_POLICY_ONLY",
             "DEVELOPMENT_POLICY_SUPPORTED_NOT_UNIQUE_NUMERIC"))

    def test_protected_source_denied_before_random_or_factors(self):
        self.assertFalse(S.ALLOWED & S.DENIED)
        with patch.object(S.random, "Random",
                          side_effect=AssertionError("SOURCE_MUST_NOT_CREATE")):
            for seed in (131000,131063,131800,131863,135800,135863,
                         138800,138863,120800,125800,127800,134999,135128,
                         136256,137064,True,-1,"135000"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):
                        S.world(seed)
                    with self.assertRaises(PermissionError):
                        S.open_original(seed)

    def test_inspectable_source_rank_and_unseen_law_negative(self):
        for law in (0, 1, 13, 63, 127):
            self.assertEqual(S.rank(S._rows(law)), 8)
            if law < 64:
                self.assertEqual(S.rank(S._negative_rows(law)), 9)
        self.assertNotIn("source", N.__dict__)
        self.assertNotIn("source", C.__dict__)
        self.assertNotIn("numeric", C.__dict__)

    def test_action_budget_feedback_and_zero_action_holdouts(self):
        view = S.world(135001)
        source = S.Custodian(view)
        model = N.DirectRankEight("adaptive")
        available = set(view.legal)
        seen = set()
        for step in range(1024):
            subject = model.choose(view, available)
            self.assertIn(subject, available)
            self.assertNotIn(subject, seen)
            seen.add(subject)
            available.remove(subject)
            model.observe(view, source.query(subject))
        self.assertIsNone(model.choose(view, available))
        self.assertEqual(len(source.events), 1024)
        self.assertEqual(len(tuple(source.held())), 3072)
        with self.assertRaises(PermissionError):
            source.query(next(iter(available)))
        with self.assertRaises(PermissionError):
            source.score_once({})
        for seed in (136000, 136255, 137000, 137063):
            cust = S.Custodian(S.world(seed))
            self.assertEqual(cust.budget, 0)
            self.assertEqual(len(tuple(cust.held())), 4096)
            with self.assertRaises(PermissionError):
                cust.query(cust.view.records[0][0])

    def test_cold_replay_rejects_forged_weights_even_with_fixed_digest(self):
        view = S.world(135002)
        model = N.DirectRankEight("adaptive")
        c = S.Custodian(view)
        available = set(view.legal)
        for step in range(1024):
            subject = model.choose(view, available)
            available.remove(subject)
            model.observe(view, c.query(subject))
        snapshot = model.snapshot()
        self.assertEqual(N.DirectRankEight.restore(snapshot).snapshot(), snapshot)
        bad = json.loads(snapshot)
        factors = bad["payload"]["states"]["2"]["factors"]
        self.assertTrue(factors)
        first_key = next(iter(factors))
        factors[first_key] ^= 1
        with self.assertRaisesRegex(ValueError, "WSP127_SNAPSHOT_DIGEST_INVALID"):
            N.DirectRankEight.restore(S.canon(bad))
        bad["sha256"] = N._hash(bad["payload"])
        with self.assertRaisesRegex(ValueError, "WSP127_SNAPSHOT_FABRICATED_WEIGHTS"):
            N.DirectRankEight.restore(S.canon(bad))

    def test_fixed_and_adaptive_source_actions_differ_but_same_budget(self):
        view = S.world(135004)
        adaptive = N.DirectRankEight("adaptive")
        fixed = N.DirectRankEight("fixed")
        receipts = []
        for model in (adaptive, fixed):
            cust = S.Custodian(view)
            available = set(view.legal)
            for _ in range(1024):
                chosen = model.choose(view, available)
                available.remove(chosen)
                model.observe(view, cust.query(chosen))
            receipts.append(cust.receipt)
        self.assertEqual(len(adaptive._state(4).events), 1024)
        self.assertEqual(len(fixed._state(4).events), 1024)
        self.assertEqual(len(receipts), 2)
