"""WSP128 source-safe high-first contradiction, repair and retention checks."""
from __future__ import annotations
import json
from unittest import TestCase
from unittest.mock import patch

import source as S
import repair as R
import controls as C
import experiment as E

class ContradictionRepairTests(TestCase):
    def test_frozen_full_192_world_source_safe_measurement(self):
        result=E.run_engineering()
        print("WSP128_FINAL_ENGINEERING_JSON="+S._canon(result))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["original_first_use"])
        self.assertFalse(result["native_admission"])
        self.assertEqual(result["source_action_calls_per_arm"],163840)
        self.assertEqual(result["all_arm_source_probe_count"],98304)
        self.assertEqual(result["underlying_causal_laws"],64)
        self.assertTrue(result["matched_control_transcripts"])
        self.assertTrue(result["numerical_symbolic_exact_parity"])
        self.assertTrue(result["warm_original_knowledge_preserved"])
        self.assertEqual(result["strong_trained_conventional"],"NOT_RUN_UNQUALIFIED")
        for condition in E.CONDITIONS:
            self.assertEqual(result["detector"][condition]["worlds"],64)
            for arm in E.ARMS:
                cell=result["cohorts"][condition][arm]
                self.assertEqual(cell["held"],229376)
                self.assertEqual(cell["source_calls"],32768)
            self.assertEqual(
                result["cohorts"][condition]["NATIVE_REPAIR"],
                result["cohorts"][condition]["SYMBOLIC_EXACT"])
        self.assertEqual(result["paired_bootstrap"]["seed"],128)
        self.assertEqual(result["paired_bootstrap"]["resamples"],10000)
        self.assertIn(result["status"],(
            "DEVELOPMENT_NO_GO","DEVELOPMENT_MIXED_WITHIN_FAMILY_SYMBOLIC_TIE"))

    def test_no_protected_source_opened_before_generation(self):
        self.assertFalse(S.ALLOWED&S.DENIED)
        with patch.object(S.random,"Random",
                          side_effect=AssertionError("NO_PROTECTED_SOURCE_GENERATION")):
            for seed in (131000,131063,131800,131863,135800,135863,
                         138800,138863,120800,125800,127800,138999,
                         139192,140000,141000,True,-1,"139000"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):
                        S.world(seed)
                    with self.assertRaises(PermissionError):
                        S.open_original(seed)

    def test_source_rank9_rank10_and_scrambled_public_conditions(self):
        assignment=S._assignment()
        self.assertEqual(len(assignment),192)
        self.assertEqual(len(set(assignment)),192)
        for law in (0,1,7,31,63):
            self.assertEqual(S.P.rank(S._patch_rows(law,"unchanged")),8)
            self.assertEqual(S.P.rank(S._patch_rows(law,"rank9")),9)
            self.assertEqual(S.P.rank(S._patch_rows(law,"rank10")),10)
        for seed in (139000,139047,139123,139191):
            view=S.world(seed)
            self.assertEqual(view.cohort,"probe")
            self.assertEqual(len(view.records),4096)
            self.assertEqual(len(view.legal),4096)
            self.assertFalse(hasattr(view,"condition"))
        self.assertNotIn("source",R.__dict__)
        self.assertNotIn("source",C.__dict__)
        self.assertNotIn("repair",C.__dict__)

    def test_one_shot_full_512_paid_source_actions_and_replay(self):
        class ZeroPrior:
            def infer(self,view,subject):
                return 0
        view=S.world(139005)
        cust=S.Custodian(view)
        native=R.DirectResidualRepair(ZeroPrior())
        available=set(view.legal)
        for _ in range(512):
            action=native.choose(view,available)
            self.assertIsNotNone(action)
            self.assertIn(action,available)
            available.remove(action)
            native.observe(view,cust.query(action))
        self.assertIsNone(native.choose(view,available))
        with self.assertRaises(PermissionError):
            cust.query(next(iter(available)))
        self.assertEqual(len(tuple(cust.held())),3584)
        with self.assertRaises(ValueError):
            cust.score_once({})
        snap=native.snapshot()
        restored=R.DirectResidualRepair.restore(ZeroPrior(),snap,lambda seed:view)
        self.assertEqual(snap,restored.snapshot())
        bad=json.loads(snap)
        row=next(iter(bad["payload"]["states"].values()))
        row["contradictions"]+=1
        with self.assertRaisesRegex(ValueError,"WSP128_SNAPSHOT_DIGEST_INVALID"):
            R.DirectResidualRepair.restore(ZeroPrior(),S._canon(bad),lambda seed:view)
        bad["sha256"]=R._hash(bad["payload"])
        with self.assertRaisesRegex(ValueError,"WSP128_SNAPSHOT_FORGED_REPAIR_COEFFICIENT"):
            R.DirectResidualRepair.restore(ZeroPrior(),S._canon(bad),lambda seed:view)
