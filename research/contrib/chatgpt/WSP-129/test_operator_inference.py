"""WSP129 exact provenance, source-safe negatives and full frozen 128-world comparison."""
from __future__ import annotations
import json
from unittest import TestCase
from unittest.mock import patch

import source as S
import learner as N
import controls as C
import experiment as E

class OperatorInferenceTests(TestCase):
    def test_full_frozen_source_safe_operator_and_negative_experiment(self):
        result=E.run_engineering()
        print("WSP129_FINAL_ENGINEERING_JSON="+S.canon(result))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_admission"])
        self.assertFalse(result["original_first_use"])
        self.assertTrue(result["operator_library_supplied"])
        self.assertTrue(result["cold_restoration"])
        self.assertTrue(result["post_interference_retention"])
        self.assertTrue(result["exact_symbolic_matched_on_all_predictions"])
        self.assertEqual(result["paid_actions_per_arm"],3072)
        self.assertEqual(result["in_grammar_held_per_arm"],22272)
        self.assertEqual(result["off_grammar_held_per_arm"],7424)
        self.assertEqual(result["worlds_by_family"],
                         {"XOR":32,"AND":32,"OR":32,"OFF":32})
        self.assertEqual(result["ridge"]["train_total"],3072)
        self.assertEqual(result["paired_active_fixed_bootstrap"]["seed"],129)
        self.assertEqual(result["paired_active_fixed_bootstrap"]["resamples"],10000)
        for kind in E.KINDS:
            for arm in E.ARMS:
                data=(result["off_family"] if kind=="OFF" else result["fit"][kind])[arm]
                self.assertEqual(data["held"],32*232)
                self.assertEqual(data["source_calls"],32*24)
            data=result["off_family"] if kind=="OFF" else result["fit"][kind]
            self.assertEqual(data["ACTIVE_NUMERIC"],data["ACTIVE_EXACT_SYMBOLIC"])
            self.assertEqual(data["FIXED_NUMERIC"],data["FIXED_EXACT_SYMBOLIC"])
        for arm in E.ARMS:
            self.assertEqual(result["transfer"][arm]["held"],32*256)
            self.assertEqual(result["transfer"][arm]["source_calls"],0)
        self.assertIn(result["status"],
            ("DEVELOPMENT_SUPPORTED_WITHIN_SUPPLIED_GRAMMAR_SYMBOLIC_TIE",
             "DEVELOPMENT_MIXED_ON_GRAMMAR_ONLY","DEVELOPMENT_NO_GO"))

    def test_unauthorized_sources_denied_before_any_rng(self):
        self.assertFalse(S.ALLOWED&S.DENIED)
        with patch.object(S.random,"Random",
                          side_effect=AssertionError("WSP129_PROTECTED_RNG_USED")):
            for seed in (131000,131063,131800,131863,135800,135863,
                         138800,138863,148800,148863,150800,150863,
                         120800,125800,127800,147999,148128,
                         149000,149031,149999,150032,True,-1,"148000"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):
                        S.world(seed)
                    with self.assertRaises(PermissionError):
                        S.open_original(seed)

    def test_exact_source_families_and_hidden_labels(self):
        specs=S._assign()
        self.assertEqual(len(specs),128)
        self.assertEqual(len({lid for lid,_ in specs}),128)
        self.assertEqual({mode:sum(kind==mode for _,kind in specs)
                          for mode in E.KINDS},
                         {"XOR":32,"AND":32,"OR":32,"OFF":32})
        grammar=S._grammar_tables()
        self.assertLessEqual(len(grammar),1350)
        for seed in range(148000,148128):
            view=S.world(seed)
            kind=specs[seed-148000][1]
            truth=S._truth_law(view.law_id)
            self.assertEqual(truth in grammar,kind!="OFF")
            self.assertEqual(view.cohort,"probe")
            self.assertEqual(len(view.legal),256)
            self.assertEqual(len(view.by_pair),256)
            self.assertFalse(hasattr(view,"kind"))
            self.assertFalse(hasattr(view,"mode"))
        self.assertNotIn("source",N.__dict__)
        self.assertNotIn("source",C.__dict__)
        self.assertNotIn("learner",C.__dict__)

    def test_budget_cold_restore_and_forged_hypothesis_bits(self):
        view=S.world(148001)
        model=N.HypothesisWeightBank("active")
        cust=S.Custodian(view)
        remaining=set(view.legal)
        for i in range(24):
            action=model.choose(view,remaining)
            self.assertIn(action,remaining)
            remaining.remove(action)
            model.observe(view,cust.query(action))
        self.assertIsNone(model.choose(view,remaining))
        self.assertEqual(len(tuple(cust.held())),232)
        with self.assertRaises(PermissionError):
            cust.query(next(iter(remaining)))
        with self.assertRaises(ValueError):
            cust.score_once({})
        snapshot=model.snapshot()
        restored=N.HypothesisWeightBank.restore(snapshot,S.world)
        self.assertEqual(restored.snapshot(),snapshot)
        self.assertEqual(
            [model.infer(view,s) for s,_,_ in view.records],
            [restored.infer(view,s) for s,_,_ in view.records])
        bad=json.loads(snapshot)
        state=bad["payload"]["states"][str(view.law_id)]
        state["weight_mask_hex"]="0x0" if state["weight_mask_hex"]!="0x0" else "0x1"
        with self.assertRaisesRegex(ValueError,"WSP129_SNAPSHOT_DIGEST_INVALID"):
            N.HypothesisWeightBank.restore(S.canon(bad),S.world)
        bad["sha256"]=N._digest(bad["payload"])
        with self.assertRaisesRegex(ValueError,"WSP129_FORGED_HYPOTHESIS_WEIGHTS"):
            N.HypothesisWeightBank.restore(S.canon(bad),S.world)

    def test_cold_transfer_and_exact_convex_ridge(self):
        view=S.world(148003)
        model=N.HypothesisWeightBank("active")
        symbolic=C.OptimizedSymbolic()
        ridge=C.FullFitRidge()
        cust=S.Custodian(view)
        available=set(view.legal)
        for _ in range(24):
            chosen=model.choose(view,available)
            available.remove(chosen)
            e=cust.query(chosen)
            model.observe(view,e)
            symbolic.observe(view,e)
            ridge.observe(view,e)
        ridge.fit(view)
        self.assertEqual(len(ridge.states[view.law_id]["weights"]),25)
        for subject,_,_ in view.records:
            self.assertEqual(model.infer(view,subject),
                             symbolic.infer(view,subject))
        self.assertEqual(cust.budget,24)
        zero=S.Custodian(S.world(150000))
        self.assertEqual(zero.budget,0)
        with self.assertRaises(PermissionError):
            zero.query(zero.view.records[0][0])
