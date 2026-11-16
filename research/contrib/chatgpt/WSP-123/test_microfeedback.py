"""WSP-123 bounded causal-factor microfeedback and negative controls."""
from __future__ import annotations
import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import experiment as E
import source as S
import symbolic as Y
import weights as W


class CausalFactorTests(TestCase):
    def test_high_first_full_engineering_transfer_and_offfamily(self):
        with patch.object(S,"open_original",
                          side_effect=AssertionError("original opened")):
            result=E.run_engineering()
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["source_first_use"])
        self.assertFalse(result["native_admission"])
        self.assertEqual(result["fit_source_calls"],60)
        self.assertEqual(result["fit_held"],64)
        self.assertEqual(result["transfer"]["worlds"],256)
        self.assertEqual(result["offfamily"]["worlds"],64)
        self.assertEqual(result["native_slot_bytes_only"],256)
        self.assertTrue(result["cold_retention"])
        self.assertTrue(result["strong_control_parity"])
        n=result["transfer"]["arms"]["NUMERIC_FACTOR_GROW"]
        sym=result["transfer"]["arms"]["SYMBOLIC_FACTOR_STRONG"]
        self.assertEqual(n,sym)
        self.assertEqual((n["held"],n["correct"],n["wrong_confident"],n["abstained"]),
                         (16384,16384,0,0))
        negative=result["offfamily"]["arms"]["NUMERIC_FACTOR_GROW"]
        self.assertEqual((negative["correct"],negative["wrong_confident"]),
                         (3072,1024))
        self.assertLess(result["transfer"]["arms"]["SYMBOLIC_PASSIVE"]["correct"],16384)
        self.assertEqual(result["transfer"]["arms"]["MEMO_ONLY"]["abstained"],16384)
        self.assertEqual(result["transfer"]["arms"]["NO_UPDATE"]["abstained"],16384)

    def test_original_protected_and_unlisted_world_denied(self):
        self.assertFalse(S.ALLOWED & (S.ORIGINAL|S.PROTECTED))
        for seed in (123000,123063,123800,123863,122800,121800,120800,
                     125000,-1,True,"123900"):
            with self.subTest(seed=seed),self.assertRaises(PermissionError):
                S.world(seed)
            with self.subTest(original=seed),self.assertRaises(PermissionError):
                S.open_original(seed)

    def test_public_source_is_paired_and_held_query_fenced(self):
        view=S.world(123900)
        self.assertEqual((len(view.records),len(view.legal),len(view.held)),
                         (64,48,16))
        c=S.Custodian(view)
        with self.assertRaises(PermissionError):
            c.query(view.held[0])
        with self.assertRaises(PermissionError):
            c.score_once({s:None for s in view.held})
        for s in view.legal[:15]:
            event=c.query(s)
            self.assertEqual((event.left,event.right),view.pair(s))
            self.assertEqual(len(event.source_sha256),64)
        with self.assertRaises(PermissionError):
            c.query(view.legal[0])
        with self.assertRaises(PermissionError):
            c.query(view.legal[15])
        self.assertEqual(c.score_once({s:None for s in view.held})["abstained"],16)
        with self.assertRaises(PermissionError):
            c.score_once({s:None for s in view.held})
        for seed in (124000,124063,124255,124400,124463):
            unseen=S.Custodian(S.world(seed))
            self.assertEqual(unseen.budget,0)
            with self.assertRaises(PermissionError):
                unseen.query(unseen.public.held[0])

    def test_direct_incremental_weights_snapshot_replay_and_weight_forgery(self):
        w=S.world(123900)
        source=S.Custodian(w)
        n=W.NumericCausalBank()
        remaining=set(w.legal)
        for _ in range(15):
            choice=n.choose(w,remaining)
            self.assertIsNotNone(choice)
            remaining.remove(choice)
            n.observe(w,source.query(choice))
        s=n.snapshot()
        self.assertEqual(W.NumericCausalBank.restore(s).snapshot(),s)
        snap=json.loads(s)
        snap["payload"]["weights"]["0"][0]=7
        with self.assertRaisesRegex(ValueError,"WSP123_COLD_DIGEST_INVALID"):
            W.NumericCausalBank.restore(S.canonical(snap))
        snap["sha256"]=W._sha(snap["payload"])
        with self.assertRaisesRegex(ValueError,"WSP123_COLD_WEIGHT_PROVENANCE"):
            W.NumericCausalBank.restore(S.canonical(snap))
        for subject in w.held:
            self.assertEqual(n.infer(w,subject),W.NumericCausalBank.restore(s).infer(w,subject))

    def test_untrusted_or_contradictory_observations_fail_closed(self):
        w=S.world(123900)
        source=S.Custodian(w)
        numeric=W.NumericCausalBank()
        ev=source.query(w.legal[0])
        numeric.observe(w,ev)
        with self.assertRaisesRegex(ValueError,"WSP123_DUPLICATE_OBSERVATION"):
            numeric.observe(w,ev)
        # Mutated but source-looking record from a different subject with the
        # same causal pair is rejected because each world has unique pairs.
        another=w.legal[1]
        bad=SimpleNamespace(seed=ev.seed,domain=ev.domain,subject=another,
                            left=ev.left,right=ev.right,effect=ev.effect,
                            source_sha256=ev.source_sha256)
        with self.assertRaisesRegex(ValueError,"WSP123_UNVERIFIED_OR_UNAUTHORIZED"):
            numeric.observe(w,bad)
        self.assertEqual(len(numeric.events),1)

    def test_new_opaque_entities_and_domain_memory_not_action_ids(self):
        original=S.world(123900)
        transfer=S.world(124000)
        self.assertEqual(original.domain,transfer.domain)
        self.assertFalse({row[0] for row in original.records} &
                         {row[0] for row in transfer.records})
        same=S.world(123900)
        self.assertEqual(original,same)
        self.assertNotEqual(S.world(123900).records,S.world(123901).records)

    def test_independent_strong_symbolic_solver_matches_numeric_at_each_fit(self):
        public=S.world(123901)
        sn,ss=S.Custodian(public),S.Custodian(public)
        n,y=W.NumericCausalBank(),Y.StrongSymbolicFactors()
        remaining=set(public.legal)
        for _ in range(15):
            subject=n.choose(public,remaining)
            self.assertEqual(subject,y.choose(public,remaining))
            remaining.remove(subject)
            en,ey=sn.query(subject),ss.query(subject)
            self.assertEqual(en.effect,ey.effect)
            n.observe(public,en)
            y.observe(public,ey)
            for s in public.held:
                self.assertEqual(n.infer(public,s),y.infer(public,s))
        self.assertEqual(sn.receipt,ss.receipt)
        self.assertEqual(sum(n.infer(public,s) is not None for s in public.held),16)
