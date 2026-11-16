"""WSP131 original-source-safe semantic rebinding with adversarial shears."""
from __future__ import annotations
import json
from unittest import TestCase
from unittest.mock import patch

import source as S
import binder as N
import controls as C
import experiment as E

class CausalSemanticBindingTests(TestCase):
    def test_first_use_denied_before_any_source_rng(self):
        self.assertFalse(S.ALLOWED&S.PROTECTED)
        with patch.object(S.random,"Random",
                side_effect=AssertionError("PROTECTED_SOURCE_MUST_NOT_RUN")):
            for seed in (131000,131063,131800,131863,135800,135863,
                         138800,138863,148800,148863,150800,150863,
                         154800,154863,155800,155863,156000,156063,
                         160800,160863,161800,161863,162800,162863,
                         159999,160064,160999,161032,161999,162016,
                         163000,-1,True,"160000"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn("source",N.__dict__)
        self.assertNotIn("source",C.__dict__)
        self.assertNotIn("binder",C.__dict__)

    def test_new_physical_semantic_shift_and_nonpermutation_source(self):
        self.assertEqual(len(S.PERMS),720)
        self.assertEqual(len(S._origins()),64)
        modes=S.P._modes()
        self.assertEqual({mode:sum(modes[i]==mode for i in S._origins())
                          for mode in ("quartic","quintic")},
                         {"quartic":32,"quintic":32})
        for seed in (160000,160009,160017,160063,161000,161012,161031):
            view=S.world(seed)
            self.assertEqual(len(view.records),256)
            self.assertEqual(len(view.legal),256)
            self.assertEqual(view.cohort,"probe")
            self.assertFalse(hasattr(view,"permutation"))
            self.assertFalse(hasattr(view,"shear"))
        for seed in range(161000,161032):
            target=S._physical_law(seed)
            base=S.P._law(target["law"])["truth"]
            signatures={bytes(base[S._permute(x,p)] for x in range(256))
                        for p in S.PERMS}
            self.assertNotIn(bytes(target["truth"]),signatures)
        for seed in range(162000,162016):
            view=S.world(seed)
            self.assertEqual(view.cohort,"transfer")
            self.assertFalse(view.legal)
            cust=S.Custodian(view)
            self.assertEqual(cust.budget,0)
            with self.assertRaises(PermissionError):
                cust.query(view.records[0][0])

    def test_exact_cold_replay_and_forged_rebinding_rejected(self):
        law=S._origins()[0]
        original=S.warm_world(law)
        warm=E.N130.DirectInducer()
        c=S.warm_custodian(original)
        left=set(original.legal)
        for _ in range(128):
            chosen=warm.choose(original,left)
            self.assertIn(chosen,left)
            left.remove(chosen)
            warm.observe(original,c.query(chosen))
        v=S.world(160000)
        m=N.NativeBinder(warm)
        cust=S.Custodian(v)
        remaining=set(v.legal)
        for _ in range(32):
            action=m.choose(v,remaining)
            self.assertIn(action,remaining)
            remaining.remove(action)
            m.observe(v,cust.query(action))
        self.assertIsNone(m.choose(v,remaining))
        self.assertEqual(len(tuple(cust.held())),224)
        with self.assertRaises(PermissionError):
            cust.query(next(iter(remaining)))
        with self.assertRaises(ValueError):
            cust.score_once({})
        frozen=m.snapshot()
        cold=N.NativeBinder.restore(warm,frozen,S.world)
        self.assertEqual(cold.snapshot(),frozen)
        for s,x in v.records:
            self.assertEqual(cold.infer(v,s),m.infer(v,s))
        # LRU re-materialization preserves the same public source evidence
        # even though Python has returned a different View instance.
        for seed in range(160001,160019):
            S.world(seed)
        fresh=S.world(160000)
        self.assertIsNot(fresh,v)
        self.assertEqual(fresh.fingerprint(),v.fingerprint())
        self.assertEqual(m.infer(fresh,fresh.subject(17)),
                         m.infer(v,v.subject(17)))
        forged=S.View(v.seed,v.law_id,v.cohort,
                      tuple(reversed(v.records)),v.legal,
                      v.by_subject,v.by_x)
        with self.assertRaisesRegex(ValueError,"WSP131_CHANGED_PUBLIC_VIEW"):
            m.infer(forged,forged.subject(17))
        bad=json.loads(frozen)
        rec=next(iter(bad["payload"]["states"].values()))
        rec["candidate_weight_hex"]=hex(int(rec["candidate_weight_hex"],16)^1)
        with self.assertRaisesRegex(ValueError,"WSP131_SNAPSHOT_DIGEST_INVALID"):
            N.NativeBinder.restore(warm,S.canon(bad),S.world)
        bad["sha256"]=N.digest(bad["payload"])
        with self.assertRaisesRegex(ValueError,"WSP131_FORGED_PERMUTATION_WEIGHTS"):
            N.NativeBinder.restore(warm,S.canon(bad),S.world)

    def test_frozen_entire_96_world_learning_and_negative_comparison(self):
        z=E.run_engineering()
        print("WSP131_FINAL_ENGINEERING_JSON="+S.canon(z))
        self.assertFalse(z["scientific_pass"])
        self.assertFalse(z["native_admission"])
        self.assertFalse(z["original_first_use"])
        self.assertTrue(z["inherited_source_snapshot_unchanged"])
        self.assertTrue(z["cold_replay_all_target_worlds"])
        self.assertTrue(z["active_exact_symbolic_decision_tie"])
        self.assertTrue(z["fully_fitted_cart_reported"])
        self.assertEqual(z["parent_learning_warm_actions_per_arm"],8192)
        self.assertEqual(z["rebinding_actions_per_arm"],3072)
        self.assertEqual(z["rebinding_worlds"],{"known":64,"shear":32})
        self.assertEqual(z["paired_active_vs_fixed_bootstrap"]["resamples"],10000)
        self.assertEqual(z["paired_active_vs_fixed_bootstrap"]["seed"],131)
        for kind,total in (("known",64),("shear",32)):
            self.assertEqual(z["world_dispositions"][kind]["worlds"],total)
            for arm in E.ARMS:
                for stage in E.STAGES:
                    a=z["scores"][kind][arm][str(stage)]
                    self.assertEqual(a["held"],total*224)
                    self.assertEqual(a["source_calls"],total*stage)
                self.assertEqual(z["scores"][kind]["ACTIVE_NUMERIC_BINDER"][str(stage)],
                                 z["scores"][kind]["ACTIVE_EXACT_SYMBOLIC"][str(stage)])
        for arm in E.ARMS:
            self.assertEqual(z["zero_source_transfer"][arm]["held"],4096)
            self.assertEqual(z["zero_source_transfer"][arm]["source_calls"],0)
        self.assertIn(z["status"],(
           "DEVELOPMENT_SUPPORTED_SEMANTIC_REBINDING_WITHIN_SUPPLIED_PERMUTATION",
           "DEVELOPMENT_NO_GO"))
