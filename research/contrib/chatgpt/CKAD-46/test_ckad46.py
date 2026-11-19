"""CKAD46 engineering-only fixtures: no original CKAD46 DEV/held run."""
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

from yggdrasil.native_context_basis import canonical,digest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad46_unit_fixture",HERE/"campaign.py")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


class CKAD46Fixtures(unittest.TestCase):
    def test_prereg_cohorts_binary_native_gate_and_exact_prior(self):
        self.assertEqual(D.PREREG,"1fcd7e165e87561cc4f47ef7a0f71ebc3e1873ba")
        self.assertEqual(D.DEV,(46111,46112))
        self.assertEqual((D.SOURCE,D.TRANSFER_END,D.TOTAL),(96,240,288))
        self.assertEqual(len(D.BALANCED),6)
        self.assertEqual(len(D.HYPOTHESES),36)
        self.assertTrue(set(D.DEV).isdisjoint(D.PILOT+D.PRIMARY+D.EXCLUDED))
        for seed in (*D.PILOT,*D.PRIMARY,*D.EXCLUDED):
            with self.assertRaisesRegex(ValueError,"CKAD46_ONLY_REGISTERED_DEV"):
                D.run(seed)
        with self.assertRaises(ValueError):
            D.private_world(D.PRIMARY[0],0)
        from yggdrasil.public_causal_cells import PublicCausalCells
        with self.assertRaises(ValueError):
            PublicCausalCells._bit(10,"ACTION")

    def test_new_symbols_and_hidden_mappings_are_unavailable_to_adapter(self):
        events,private=D.private_world(999,0)
        self.assertEqual(len(events),288)
        self.assertEqual(sorted(private["stage1"]),[0,0,1,1])
        self.assertEqual(sorted(private["stage2"]),[0,0,1,1])
        self.assertTrue(all(row["x1"] in (0,1) and row["x2"] in (0,1)
                            for _,_,row,_ in events[:96]))
        self.assertTrue(all(row["x1"] in D.TOKENS and row["x2"] in D.TOKENS
                            for _,_,row,_ in events[96:240]))
        self.assertTrue(all(row["x1"] in (0,1) and row["x2"] in (0,1)
                            for _,_,row,_ in events[240:]))
        self.assertEqual(D.private_world(999,0),D.private_world(999,0))
        self.assertNotEqual(D.private_world(999,0),D.private_world(999,1))
        self.assertEqual(set(events[96][2]),{"s1","x1","s2","x2","y"})

    def test_prequential_known_source_exact_cold_and_raw_id_preserved(self):
        events,_=D.private_world(999,0)
        for mode in ("native_likelihood_grounding","exact_balanced_mapping","native_hash"):
            m=D.GroundingBase(mode)
            for t,(ident,views,row,_) in enumerate(events[:128]):
                if t==D.WARM:m.begin_stream()
                before=m.checkpoint()
                p=m.forecast(views[0],row["x1"])
                q=m.forecast(views[0],row["x1"],row["s2"],row["x2"])
                self.assertTrue(0<p<1 and 0<q<1)
                self.assertEqual(before,m.checkpoint())
                m.observe(ident,views,row)
                if t==D.SOURCE-1:
                    frozen=m.frozen.checkpoint()
                if t>=D.SOURCE:
                    self.assertEqual(m.frozen.checkpoint(),frozen)
            self.assertEqual(m.n,128)
            self.assertEqual(m.causal.n,m.native.info()["episodes"] if
                             isinstance(m.native.info().get("episodes"),int)
                             else len(m.native._ledger))
            self.assertEqual(len(m.raw_receipts),128)
            self.assertEqual(m.frozen.n,96)
            raw=m.checkpoint()
            restored=D.GroundingBase.restore(raw,digest(raw))
            self.assertEqual(raw,restored.checkpoint())
            self.assertEqual(m.forecast((1,0),10,1,11),
                             restored.forecast((1,0),10,1,11))
            self.assertIn('"x1":10',next(x for x in m.raw_receipts.values() if '"x1":10' in x)
                          if any('"x1":10' in x for x in m.raw_receipts.values())
                          else '"x1":10')
            self.assertTrue(any('"x1":10' in x or '"x2":10' in x for x in m.raw_receipts.values()))

    def test_fitted_exact_posterior_is_normalized_and_uses_witnessed_only(self):
        events,_=D.private_world(999,1)
        exact=D.GroundingBase("exact_balanced_mapping")
        approximate=D.GroundingBase("native_likelihood_grounding")
        for t,(ident,views,row,_) in enumerate(events[:140]):
            if t==D.WARM:
                exact.begin_stream()
                approximate.begin_stream()
            old=exact.checkpoint()
            _=exact.forecast(views[0],row["x1"])
            _=exact.forecast(views[0],row["x1"],row["s2"],row["x2"])
            self.assertEqual(old,exact.checkpoint())
            exact.observe(ident,views,row)
            approximate.observe(ident,views,row)
        self.assertAlmostEqual(sum(exact.weights),1.0,delta=1e-13)
        self.assertGreater(max(exact.weights),1/36)
        self.assertTrue(any(abs(v)>1e-8 for v in approximate.logodds[0].values()))
        self.assertEqual(set(approximate.logodds[0]).issubset(set(D.TOKENS)),True)
        self.assertTrue(all(math.isfinite(v) for bank in approximate.logodds
                            for v in bank.values()))
        self.assertEqual(exact.frozen.checkpoint(),
                         approximate.frozen.checkpoint())

    def test_duplicates_and_conflicts_do_not_retrain_native_or_causal(self):
        events,_=D.private_world(999,0)
        obj=D.GroundingBase("native_likelihood_grounding")
        for t,(ident,views,row,_) in enumerate(events[:108]):
            if t==D.WARM:obj.begin_stream()
            obj.observe(ident,views,row)
        ident,views,row,_=events[107]
        raw=obj.checkpoint()
        self.assertIs(obj.observe(ident,views,row),obj)
        self.assertEqual(raw,obj.checkpoint())
        corrupt=dict(row);corrupt["y"]^=1
        with self.assertRaisesRegex(ValueError,"CKAD46_CONFLICTING_RAW_SOURCE_ID"):
            obj.observe(ident,views,corrupt)
        self.assertEqual(obj.checkpoint(),raw)
        with self.assertRaisesRegex(ValueError,"CKAD46_COLD_DIGEST"):
            D.GroundingBase.restore(raw,"0"*64)

    def test_frozen_scientific_go_requires_strongest_control(self):
        def fake(seed,good=.10,exact=.122,raw=.128,naive=.129,early=.115,ret=.11):
            def group(v):
                return {"brier":{"native_likelihood_grounding":v,
                    "exact_balanced_mapping":exact,"independent_raw_beta":raw,
                    "native_hash":naive,"frozen_uniform":.14,
                    "oracle_known_mapping":.09}}
            return {"seed":seed,"worlds":[{"arm":"native_likelihood_grounding",
                "source_prefix48_preserved":True,"frozen_source96_exact":True,
                "cold_exact":True,"duplicate_idempotent":True,"conflict_atomic":True,
                "distinct_stage1_novel_symbols_witnessed":4,
                "distinct_stage2_novel_symbols_witnessed":4}],
                "groups":{"unseen_late_plus_return":group(good),
                          "unseen_early":group(early),
                          "cold_return":group(ret)}}
        a,b=[fake(seed) for seed in D.DEV]
        self.assertEqual(D.classify([a,b]),"DEV_FEASIBLE_NOT_SCIENTIFIC")
        self.assertEqual(D.classify([a,fake(D.DEV[1],good=.112)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,fake(D.DEV[1],early=.155)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,fake(D.DEV[1],ret=.14)]),"DEV_NO_GO")
        with self.assertRaises(AssertionError):
            D.classify([b,a])


if __name__=="__main__":
    unittest.main()
