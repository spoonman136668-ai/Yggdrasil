"""Source-free WSP124 high-first causal repair; no original science first-use."""
from __future__ import annotations
import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import source as S
import numeric as N
import controls as C
import experiment as E


class CausalRepairTests(TestCase):
    def test_complete_16_domain_high_first_repair_and_transfer(self):
        result=E.run_engineering()
        print("WSP124_ENGINEERING_JSON="+S.canonical(result))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["source_first_use"])
        self.assertFalse(result["native_admission"])
        self.assertEqual(result["fit_source_calls"],368)
        self.assertEqual(result["fit_scores"]["NUMERIC_REPAIR"]["correct"],656)
        self.assertEqual(result["fit_scores"]["SYMBOLIC_STRONG"],
                         result["fit_scores"]["NUMERIC_REPAIR"])
        self.assertEqual(result["transfer"]["worlds"],1024)
        self.assertEqual(result["offfamily"]["worlds"],256)
        self.assertEqual(result["transfer"]["arms"]["NUMERIC_REPAIR"]["correct"],65536)
        self.assertEqual(result["transfer"]["arms"]["NUMERIC_REPAIR"],
                         result["transfer"]["arms"]["SYMBOLIC_STRONG"])
        self.assertEqual(result["offfamily"]["arms"]["NUMERIC_REPAIR"]["wrong_confident"],4096)
        self.assertEqual(result["offfamily"]["arms"]["NUMERIC_REPAIR"],
                         result["offfamily"]["arms"]["SYMBOLIC_STRONG"])
        self.assertEqual(result["native_slot_bytes_only"],1216)
        self.assertTrue(result["cold_retention"])
        self.assertFalse(result["domain_interference"])
        self.assertLess(result["transfer"]["arms"]["SYMBOLIC_PASSIVE"]["correct"],65536)
        self.assertLess(result["transfer"]["arms"]["XOR_ONLY"]["correct"],65536)
        self.assertEqual(result["transfer"]["arms"]["NO_UPDATE"]["abstained"],65536)

    def test_original_protected_and_unregistered_source_denied_early(self):
        self.assertFalse(S.ENGINEERING&(S.ORIGINAL|S.PROTECTED))
        with patch.object(S.random,"Random",side_effect=AssertionError("unsealed source opened")):
            for seed in (127000,127063,127800,127863,123800,122800,
                         121800,120800,128899,128916,130024,130099,
                         130356,-1,True,"128900"):
                with self.subTest(seed=seed),self.assertRaises(PermissionError):
                    S.world(seed)
                with self.subTest(original=seed),self.assertRaises(PermissionError):
                    S.open_original(seed)
        self.assertEqual((len(S.FIT),len(S.TRANSFER),len(S.OFFFAMILY)),
                         (16,1024,256))

    def test_source_first_use_replay_and_zero_transfer_actions_denied(self):
        w=S.world(128900)
        c=S.Custodian(w)
        n=N.NumericRepair()
        with self.assertRaises(PermissionError):
            c.score_once({})
        with self.assertRaises(ValueError):
            n.observe(w,SimpleNamespace())
        available=set(w.legal)
        for step in range(23):
            subject=n.choose(w,available)
            available.remove(subject)
            n.observe(w,c.query(subject))
            if step<22:
                self.assertIsNone(n.infer(w,subject))
        self.assertIsNone(n.choose(w,available))
        with self.assertRaises(PermissionError):
            c.query(w.legal[0])
        with self.assertRaises(PermissionError):
            c.query(next(iter(available)))
        self.assertEqual(c.count,23)
        self.assertEqual(c.score_once({s:n.infer(w,s) for s in c.held})["correct"],41)
        with self.assertRaises(PermissionError):
            c.score_once({})
        for seed in (129000,129063,130023,130100,130355):
            transfer=S.Custodian(S.world(seed))
            self.assertEqual(transfer.budget,0)
            with self.assertRaises(PermissionError):
                transfer.query(transfer.held[0])

    def test_cold_replay_and_digest_repaired_forged_weights_denied(self):
        w=S.world(128901)
        n=N.NumericRepair()
        c=S.Custodian(w)
        available=set(w.legal)
        for _ in range(23):
            s=n.choose(w,available)
            available.remove(s)
            n.observe(w,c.query(s))
        snapshot=n.snapshot()
        restored=N.NumericRepair.restore(snapshot)
        self.assertEqual(restored.snapshot(),snapshot)
        forged=json.loads(snapshot)
        forged["payload"]["weights"]["1"][18]^=1
        with self.assertRaisesRegex(ValueError,"WSP124_COLD_DIGEST_INVALID"):
            N.NumericRepair.restore(S.canonical(forged))
        forged["sha256"]=N.digest(forged["payload"])
        with self.assertRaisesRegex(ValueError,"WSP124_COLD_REPLAY_MISMATCH"):
            N.NumericRepair.restore(S.canonical(forged))
        for subject,_,_ in w.records:
            self.assertEqual(n.infer(w,subject),restored.infer(w,subject))

    def test_independent_symbolic_parity_and_source_receipts(self):
        w=S.world(128902)
        sn,ss=S.Custodian(w),S.Custodian(w)
        n=N.NumericRepair()
        symbolic=C.StrongSymbolic()
        available=set(w.legal)
        for _ in range(23):
            subject=n.choose(w,available)
            available.remove(subject)
            a,b=sn.query(subject),ss.query(subject)
            self.assertEqual(a,b)
            n.observe(w,a)
            symbolic.observe(w,b)
        self.assertEqual(sn.receipt,ss.receipt)
        self.assertEqual(symbolic.candidate_count(w.domain),1)
        self.assertEqual([n.infer(w,s) for s,_,_ in w.records],
                         [symbolic.infer(w,s) for s,_,_ in w.records])
        self.assertNotIn("numeric",C.__dict__)
        self.assertNotIn("source",N.__dict__)

    def test_anchor_indistinguishability_requires_diagnostic_action(self):
        # The baseline and changed world are observationally identical under
        # all 15 source-blind anchors, but disagree at (7,7) by hidden delta.
        for d in range(16):
            for a,b in ([(0,v) for v in range(8)]+
                        [(v,0) for v in range(1,8)]):
                self.assertEqual(S._outcome(d,a,b,repair=True),
                                 S._outcome(d,a,b,repair=False))
            self.assertNotEqual(S._outcome(d,7,7,repair=True),
                                S._outcome(d,7,7,repair=False))

    def test_wrong_sequence_or_untrusted_feedback_cannot_update(self):
        w=S.world(128903)
        c=S.Custodian(w)
        n=N.NumericRepair()
        badsubject=w.subject(7,7)
        genuine=c.query(badsubject)
        with self.assertRaisesRegex(ValueError,"WSP124_INTERVENTION_ORDER_OR_PAIR_MISMATCH"):
            n.observe(w,genuine)
        self.assertEqual(n.counts[w.domain],0)
        first=w.subject(0,0)
        fake=SimpleNamespace(seed=w.seed,domain=w.domain,subject=first,
                             left=0,right=0,effect=3,source_sha256="not-a-hash")
        with self.assertRaisesRegex(ValueError,"WSP124_UNVERIFIED_INTERVENTION_RECORD"):
            n.observe(w,fake)
        self.assertEqual(n.counts[w.domain],0)
