"""Source-safe WSP125 regression: new slots, exact controls, negatives."""
from __future__ import annotations
import json
from unittest import TestCase
from unittest.mock import patch

import source as S
import numeric as N
import controls as C
import experiment as E


class DynamicFeatureGrowthTests(TestCase):
    def test_high_first_128_laws_256_unfamiliar_ids_64_new_law_negatives(self):
        result=E.run_engineering()
        print("WSP125_ENGINEERING_JSON="+S.canonical(result))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["source_first_use"])
        self.assertFalse(result["native_admission"])
        self.assertEqual(result["fit_source_calls"],4096)
        self.assertEqual(result["fit"]["NUMERIC_GROW"]["held"],4096)
        self.assertEqual(result["transfer"]["worlds"],256)
        self.assertEqual(result["transfer"]["arms"]["NUMERIC_GROW"]["held"],16384)
        self.assertEqual(result["offfamily"]["worlds"],64)
        self.assertEqual(result["offfamily"]["arms"]["NUMERIC_GROW"]["held"],4096)
        self.assertEqual(result["transfer"]["arms"]["NUMERIC_GROW"]["source_calls"],0)
        self.assertGreater(result["learned_relation_features"],0)
        self.assertEqual(result["coefficient_bytes_only"],
                         result["coefficient_int32_slots"]*4)
        self.assertTrue(result["cold_retention"])
        self.assertFalse(result["multi_law_interference"])
        self.assertEqual(result["fit"]["NUMERIC_GROW"]["wrong_confident"],0)
        self.assertEqual(result["transfer"]["arms"]["NUMERIC_GROW"]["wrong_confident"],0)
        self.assertGreater(result["offfamily"]["arms"]["NUMERIC_GROW"]["wrong_confident"],0)
        self.assertEqual(result["transfer"]["arms"]["NO_UPDATE"]["abstained"],16384)

    def test_protected_original_unlisted_first_use_denied_before_rng(self):
        self.assertFalse(S.ALLOWED&(S.ORIGINAL|S.PROTECTED))
        with patch.object(S.random,"Random",
                          side_effect=AssertionError("unauthorized generated")):
            for seed in (125000,125063,125800,125863,127800,123800,
                         122800,121800,120800,125899,126028,126199,
                         126456,126499,126564,True,-1,"125900"):
                with self.subTest(seed=seed),self.assertRaises(PermissionError):
                    S.world(seed)
                with self.assertRaises(PermissionError):
                    S.open_original(seed)

    def test_strict_source_budget_held_replay_and_transfer_action_denial(self):
        view=S.world(125900)
        owner=S.Custodian(view)
        numeric=N.DirectFeatureGrowth()
        with self.assertRaises(PermissionError):
            owner.score_once({})
        remaining=set(view.legal)
        for _ in range(32):
            subject=numeric.choose(view,remaining)
            remaining.remove(subject)
            numeric.observe(view,owner.query(subject))
        self.assertIsNone(numeric.choose(view,remaining))
        with self.assertRaises(PermissionError):
            owner.query(view.legal[0])
        with self.assertRaises(PermissionError):
            owner.query(next(iter(remaining)))
        self.assertEqual(owner.score_once({
            s:numeric.infer(view,s) for s in owner.held
        })["held"],32)
        with self.assertRaises(PermissionError):
            owner.score_once({})
        for seed in (126200,126455,126500,126563):
            other=S.Custodian(S.world(seed))
            self.assertEqual(other.budget,0)
            with self.assertRaises(PermissionError):
                other.query(other.held[0])

    def test_new_features_only_after_measured_contradiction(self):
        view=S.world(125901)
        owner=S.Custodian(view)
        numeric=N.DirectFeatureGrowth()
        self.assertEqual(numeric.feature_slots,0)
        available=set(view.legal)
        first=None
        for _ in range(32):
            subject=numeric.choose(view,available)
            available.remove(subject)
            observation=owner.query(subject)
            numeric.observe(view,observation)
            if numeric.feature_slots and first is None:
                first=(observation.left,observation.right,observation.effect)
        self.assertIsNotNone(first,"No witness in predeclared source budget")
        self.assertEqual(numeric.feature_slots,17)
        self.assertEqual(numeric.learned_laws,1)
        for subject in view.legal:
            result=numeric.infer(view,subject)
            if result is not None:
                self.assertIn(result,range(8))

    def test_exact_symbolic_is_independent_and_no_confident_unsoundness(self):
        self.assertNotIn("numeric",C.__dict__)
        self.assertNotIn("source",N.__dict__)
        self.assertEqual(len(C.MASKS),210)
        self.assertEqual(C.COUNT,210*210*7)
        for seed in (125900,125907,126027):
            view=S.world(seed)
            a,b=S.Custodian(view),S.Custodian(view)
            numeric=N.DirectFeatureGrowth()
            strong=C.ExactSymbolicSupports()
            avail=set(view.legal)
            for _ in range(32):
                subject=numeric.choose(view,avail)
                avail.remove(subject)
                ev1=a.query(subject)
                ev2=b.query(subject)
                self.assertEqual(ev1,ev2)
                numeric.observe(view,ev1)
                strong.observe(view,ev2)
            self.assertEqual(a.receipt,b.receipt)
            self.assertGreater(strong.remaining(view.law_id),0)
            for subject in a.held:
                prediction=numeric.infer(view,subject)
                if prediction is not None:
                    self.assertEqual(prediction,strong.infer(view,subject))

    def test_cold_feature_forgery_rejected_even_with_repaired_digest(self):
        view=S.world(125902)
        owner=S.Custodian(view)
        numeric=N.DirectFeatureGrowth()
        avail=set(view.legal)
        for _ in range(32):
            subject=numeric.choose(view,avail)
            avail.remove(subject)
            numeric.observe(view,owner.query(subject))
        snap=numeric.snapshot()
        self.assertEqual(N.DirectFeatureGrowth.restore(snap).snapshot(),snap)
        tampered=json.loads(snap)
        state=tampered["payload"]["states"]["2"]
        self.assertIsNotNone(state["left"])
        state["left"][0]=1-state["left"][0] if state["left"][0]>=0 else 0
        with self.assertRaisesRegex(ValueError,"WSP125_COLD_DIGEST_INVALID"):
            N.DirectFeatureGrowth.restore(S.canonical(tampered))
        tampered["sha256"]=N.digest(tampered["payload"])
        with self.assertRaisesRegex(ValueError,"WSP125_COLD_FORGED_RELATION_WEIGHTS"):
            N.DirectFeatureGrowth.restore(S.canonical(tampered))

    def test_new_opaque_entities_do_not_replay_fit_action_identity(self):
        w=S.world(125903)
        transfer_a=S.world(126200+2*3)
        transfer_b=S.world(126200+2*3+1)
        negative=S.world(126500+3)
        self.assertEqual((w.law_id,transfer_a.law_id,transfer_b.law_id,
                          negative.law_id),(3,3,3,3))
        ids=[{identity for identity,_,_ in view.records}
             for view in (w,transfer_a,transfer_b,negative)]
        for i in range(len(ids)):
            for j in range(i+1,len(ids)):
                self.assertFalse(ids[i]&ids[j])
