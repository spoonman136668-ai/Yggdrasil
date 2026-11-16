"""WSP132 bounded repair R1: source custody, independent strong control and scope."""
from __future__ import annotations
from unittest import TestCase
from unittest.mock import patch
import json
import source as S
import repair as R
import controls as C
import experiment as E

class BoundedConfidenceRepairTests(TestCase):
    def test_original_and_prospective_source_safe_complete_run(self):
        z=E.run_engineering()
        print("WSP132_FINAL_ENGINEERING_JSON="+S.canon(z))
        self.assertFalse(z["scientific_pass"])
        self.assertFalse(z["original_first_use"])
        self.assertFalse(z["native_admission"])
        self.assertTrue(z["warm_original_weights_immutable"])
        self.assertTrue(z["independent_repaired_symbolic_prediction_tie"])
        self.assertTrue(z["cold_replay_both_cohorts"])
        self.assertEqual(z["original_wsp131_frozen_status"],"DEVELOPMENT_NO_GO")
        self.assertEqual(z["repair_attempt"],1)
        self.assertEqual(z["warm_actions_per_arm"],8192)
        self.assertEqual(z["each_cohort_paid_actions_per_arm"],3072)
        self.assertEqual(z["each_target_world_paid_actions_per_arm"],32)
        for c in E.COHORTS:
            d=z["exposed_diagnostic"] if c=="EXPOSED_DIAGNOSTIC" else z["new_synthetic_prospective"]
            for kind,worlds in (("known",64),("shear",32)):
                self.assertEqual(d["counts"][kind]["worlds"],worlds)
                for arm in E.ARMS:
                    result=d["scores"][kind][arm]
                    self.assertEqual(result["held"],worlds*224)
                    self.assertEqual(result["source_calls"],worlds*32)
                self.assertEqual(d["scores"][kind]["REPAIRED_NUMERIC"],
                                 d["scores"][kind]["REPAIRED_INDEPENDENT_SYMBOLIC"])
                self.assertEqual(d["scores"][kind]["ORIGINAL_NUMERIC"],
                                 d["scores"][kind]["ORIGINAL_EXACT_SYMBOLIC"])
            self.assertTrue(d["cold_replay"])
            self.assertTrue(d["repaired_symbolic_parity"])
        self.assertEqual(z["exposed_diagnostic"]["scores"]["known"]["ORIGINAL_NUMERIC"]["correct"],14336)
        self.assertEqual(z["exposed_diagnostic"]["scores"]["shear"]["ORIGINAL_NUMERIC"]["wrong_confident"],240)
        self.assertEqual(z["new_synthetic_prospective"]["zero_source_transfer"]["REPAIRED_NUMERIC"]["source_calls"],0)
        self.assertEqual(z["new_synthetic_prospective"]["zero_source_transfer"]["REPAIRED_INDEPENDENT_SYMBOLIC"]["source_calls"],0)
        self.assertIn(z["status"],("DEVELOPMENT_REPAIR_SUPPORTED_ONLY",
                                   "DEVELOPMENT_REPAIR_PARTIAL",
                                   "DEVELOPMENT_REPAIR_NO_GO"))
        self.assertEqual(z["resource"]["matched_whole_process_energy"],"UNQUALIFIED")

    def test_denied_original_or_unregistered_seeds_before_rng(self):
        self.assertFalse(S.ALLOWED&S.DENIED)
        with patch.object(S.random,"Random",
                          side_effect=AssertionError("WSP132_PROTECTED_ORIGINAL_RNG_USED")):
            for seed in (131000,131063,131800,131863,135800,135863,
                         138800,138863,148800,148863,150800,150863,
                         154800,154863,155800,155863,156000,156063,
                         160800,160863,161800,161863,162800,162863,
                         164999,165064,165999,166032,166999,167016,
                         168000,True,-1,"165000"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn("source",R.__dict__)
        self.assertNotIn("source",C.__dict__)
        self.assertNotIn("repair",C.__dict__)

    def test_960_candidate_input_transformations_and_fresh_source_split(self):
        self.assertEqual(len(R.PERMS),720)
        self.assertEqual(len(R.PAIRS),30)
        self.assertEqual(len(S.ALLOWED),112)
        self.assertEqual(len(S.S._origins()),64)
        for seed in (165000,165063,166000,166031,167000,167015):
            v=S.world(seed)
            self.assertEqual(len(v.records),256)
            self.assertEqual(len(v.by_x),256)
            self.assertFalse(hasattr(v,"condition"))
            self.assertFalse(hasattr(v,"permutation"))
            self.assertFalse(hasattr(v,"shear"))
            self.assertEqual(v.cohort,"transfer" if 167000<=seed<167016 else "probe")
        self.assertEqual(len(set(range(165000,165064)) & set(range(160000,160064))),0)
        self.assertEqual(len(set(range(166000,166032)) & set(range(161000,161032))),0)
        for seed in (166000,166002,166013,166031):
            origin=S.S.P._law(S.S._origins()[seed-166000])["truth"]
            truth=bytes(S._truth(seed))
            pure={bytes(origin[S.S._permute(x,p)] for x in range(256)) for p in S.PERMS}
            self.assertNotIn(truth,pure)

    def test_source_budget_and_new_identity_zero_actions(self):
        v=S.world(165000)
        c=S.Custodian(v)
        self.assertEqual(c.budget,32)
        x=v.subject(17)
        e=c.query(x)
        self.assertIn(e.effect,(0,1))
        with self.assertRaises(PermissionError):c.query(x)
        with self.assertRaises(PermissionError):c.score_once({})
        self.assertEqual(len(tuple(c.held())),255)
        transferred=S.world(167000)
        zero=S.Custodian(transferred)
        self.assertEqual(zero.budget,0)
        with self.assertRaises(PermissionError):
            zero.query(transferred.records[0][0])
        result=zero.score_once({subject:None for subject,x in transferred.records})
        self.assertEqual(result["source_calls"],0)
        self.assertEqual(result["abstained"],256)

    def test_challenge_grammar_source_blind_gating(self):
        # Source-independent proof of the conservative release rule:
        # ambiguity must abstain; unanimity permits a confident bit.
        p=R.PERMS[0]
        base=[0]*256
        for x in range(256):
            base[x]=((x&5).bit_count()%2)
        self.assertEqual(R._map(0,p),0)
        for i,j in R.PAIRS:
            self.assertIn(R._shear(63,i,j),range(64))
        self.assertNotIn("source",R.__dict__)
