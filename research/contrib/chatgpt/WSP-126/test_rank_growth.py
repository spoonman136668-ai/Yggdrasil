"""WSP126 source-safe exhaustive high-first factor-rank development regression."""
from __future__ import annotations

import json
from unittest import TestCase
from unittest.mock import patch

import source as S
import numeric as N
import controls as C
import experiment as E


class LatentRankTests(TestCase):
    def test_high_first_frozen_128_laws_and_320_zero_source_worlds(self):
        result=E.run_engineering()
        print("WSP126_ENGINEERING_JSON="+S.canonical(result))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["source_first_use"])
        self.assertFalse(result["native_admission"])
        self.assertEqual(result["fit"]["calls_per_arm"],20480)
        self.assertEqual(result["fit"]["arms"]["NUMERIC_RANK_GROW"]["held"],12288)
        self.assertEqual(result["transfer"]["worlds"],256)
        self.assertEqual(result["transfer"]["scores"]["NUMERIC_RANK_GROW"]["held"],65536)
        self.assertEqual(result["offfamily"]["worlds"],64)
        self.assertEqual(result["offfamily"]["scores"]["NUMERIC_RANK_GROW"]["held"],16384)
        self.assertEqual(result["transfer"]["scores"]["NUMERIC_RANK_GROW"]["source_calls"],0)
        self.assertGreater(result["feature_slots"],0)
        self.assertTrue(result["cold_retention"])
        self.assertFalse(result["interference_detected"])
        self.assertFalse(result["unique_numerical_gain"])
        self.assertEqual(result["fit"]["arms"]["NUMERIC_RANK_GROW"],
                         result["fit"]["arms"]["SYMBOLIC_MATCHED"])
        self.assertEqual(result["transfer"]["scores"]["NUMERIC_RANK_GROW"],
                         result["transfer"]["scores"]["SYMBOLIC_MATCHED"])
        self.assertEqual(result["fit"]["arms"]["NUMERIC_RANK_GROW"]["wrong_confident"],0)
        self.assertGreater(result["offfamily"]["scores"]["NUMERIC_RANK_GROW"]["wrong_confident"],0)

    def test_protected_unregistered_original_denied_before_rng(self):
        self.assertFalse(S.ALLOWED & (S.ORIGINAL|S.PROTECTED))
        with patch.object(S.random,"Random",
                          side_effect=AssertionError("NO_SOURCE_GENERATION")):
            for seed in (131000,131063,131800,131863,125800,
                         127800,123800,122800,121800,120800,
                         131999,132128,132999,133256,133999,
                         134064,True,-1,"132000"):
                with self.subTest(seed=seed),self.assertRaises(PermissionError):
                    S.world(seed)
                with self.assertRaises(PermissionError):
                    S.open_original(seed)

    def test_exhaustive_unique_opaque_ids_448_worlds(self):
        ids=set()
        for seed in list(range(132000,132128))+list(range(133000,133256))+list(range(134000,134064)):
            view=S.world(seed)
            self.assertEqual(len(view.records),256)
            for identity,_,_ in view.records:
                self.assertNotIn(identity,ids)
                ids.add(identity)
        self.assertEqual(len(ids),448*256)

    def test_exact_rank4_positive_and_rank5_source_negative(self):
        for law in (0,1,2,7,31,63):
            rows=S._hidden_rows(law)
            self.assertEqual(S._rank(rows),4)
            if law<64:
                changed=S._negative_extra(law)
                self.assertEqual(S._rank(changed),5)
                self.assertTrue(any(a!=b for a,b in zip(rows,changed)))

    def test_first_source_growth_cold_restore_and_budget_denial(self):
        view=S.world(132003)
        c=S.Custodian(view)
        n=N.DirectRankGrowth()
        self.assertEqual(n.factor_slots,0)
        with self.assertRaises(PermissionError):
            c.score_once({})
        pool=set(view.legal)
        for step in range(160):
            action=n.choose(view,pool)
            pool.remove(action)
            n.observe(view,c.query(action))
            if step<16:
                self.assertLessEqual(n.factor_slots,1)
        self.assertIsNone(n.choose(view,pool))
        self.assertTrue(n.factor_slots in (3,4))
        before=n.snapshot()
        self.assertEqual(before,N.DirectRankGrowth.restore(before).snapshot())
        self.assertEqual(c.calls,160)
        with self.assertRaises(PermissionError):
            c.query(next(iter(pool)))
        self.assertEqual(c.score_once({s:n.infer(view,s) for s in c.held})["held"],96)
        with self.assertRaises(PermissionError):
            c.score_once({})
        for seed in (133000,133255,134000,134063):
            v=S.Custodian(S.world(seed))
            self.assertEqual(v.budget,0)
            with self.assertRaises(PermissionError):
                v.query(v.held[0])

    def test_snapshot_forged_rank_factor_rejected_even_with_fixed_digest(self):
        view=S.world(132006)
        c=S.Custodian(view)
        n=N.DirectRankGrowth()
        available=set(view.legal)
        for _ in range(160):
            s=n.choose(view,available)
            available.remove(s)
            n.observe(view,c.query(s))
        snap=n.snapshot()
        restored=N.DirectRankGrowth.restore(snap)
        self.assertEqual(restored.snapshot(),snap)
        bad=json.loads(snap)
        factors=bad["payload"]["states"]["6"]["factors"]
        k=next(iter(factors))
        factors[k]^=1
        with self.assertRaisesRegex(ValueError,"WSP126_COLD_DIGEST_INVALID"):
            N.DirectRankGrowth.restore(S.canonical(bad))
        bad["sha256"]=N._digest(bad["payload"])
        with self.assertRaisesRegex(ValueError,"WSP126_COLD_FABRICATED_LATENT_FACTOR"):
            N.DirectRankGrowth.restore(S.canonical(bad))

    def test_independent_symbolic_parity_same_actions(self):
        self.assertNotIn("source",N.__dict__)
        self.assertNotIn("numeric",C.__dict__)
        for law in (0,1,7,31):
            view=S.world(132000+law)
            source_a,source_b=S.Custodian(view),S.Custodian(view)
            native,strong=N.DirectRankGrowth(),C.OptimizedSymbolic()
            allowed=set(view.legal)
            for _ in range(160):
                action=native.choose(view,allowed)
                allowed.remove(action)
                e1,e2=source_a.query(action),source_b.query(action)
                self.assertEqual(e1,e2)
                native.observe(view,e1)
                strong.observe(view,e2)
            self.assertEqual(source_a.receipt,source_b.receipt)
            for action in source_a.held:
                self.assertEqual(native.infer(view,action),
                                 strong.infer(view,action))

    def test_independently_new_opaque_entities_transfer_without_action_id_reuse(self):
        fit=S.world(132013)
        t1,t2=S.world(133026),S.world(133027)
        n=S.world(134013)
        self.assertEqual([v.law_id for v in (fit,t1,t2,n)],[13]*4)
        idsets=[{s for s,_,_ in v.records} for v in (fit,t1,t2,n)]
        for i in range(4):
            for j in range(i+1,4):
                self.assertFalse(idsets[i]&idsets[j])
