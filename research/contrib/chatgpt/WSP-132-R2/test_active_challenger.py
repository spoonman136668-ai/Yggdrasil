"""WSP132-R2 frozen second repair, source-safe negatives and reproducibility."""
from __future__ import annotations
import json
from unittest import TestCase
from unittest.mock import patch

import source as S
import binder as N
import controls as C
import experiment as E

class ActiveChallengerRepairTests(TestCase):
    def test_source_first_use_fence_precedes_rng(self):
        self.assertFalse(S.NEW&S.PROTECTED)
        with patch.object(S.random,"Random",
                          side_effect=AssertionError("R2_PROTECTED_RNG_USED")):
            for seed in (131000,131063,135800,138800,148800,154800,
                         155800,156000,160800,161800,165800,166800,
                         168999,169064,169999,170032,170999,171016,
                         172800,172863,True,-1,"169000"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn("source",N.__dict__)
        self.assertNotIn("source",C.__dict__)
        self.assertNotIn("binder",C.__dict__)

    def test_all_challenger_maps_are_a_disjoint_complete_partition(self):
        self.assertEqual(len(N.PERMS),720)
        self.assertEqual(len(N.PAIRS),30)
        self.assertEqual(len(N.TRANSFORMS),22320)
        table=N._inverse_mapping()
        self.assertEqual(len(table),64)
        for x in (0,1,7,16,31,63):
            self.assertEqual(sum(v.bit_count() for v in table[x]),22320)
            self.assertEqual(sum(table[x]),N.FULL)
        self.assertEqual(len(S.NEW),112)
        for seed in (169000,169063,170000,170031,171000,171015):
            v=S.world(seed)
            self.assertEqual(len(v.records),256)
            self.assertEqual(v.cohort,"transfer" if seed>=171000 else "probe")
            self.assertFalse(hasattr(v,"true_map"))
            self.assertFalse(hasattr(v,"true_shear"))

    def test_actual_paid_budget_zero_action_transfer_and_cold_forgery(self):
        oldN,oldS,_=E._warm()
        v=S.world(169000)
        n=N.ActiveChallengerRepair(oldN)
        strong=C.ExactChallengerSymbolic(oldS)
        custody=S.Custodian(v)
        available=set(v.legal)
        for _ in range(32):
            s=n.choose(v,available)
            self.assertIn(s,available)
            available.remove(s)
            e=custody.query(s)
            n.observe(v,e)
            strong.observe(v,e)
        self.assertIsNone(n.choose(v,available))
        with self.assertRaises(PermissionError):custody.query(next(iter(available)))
        self.assertEqual(len(tuple(custody.held())),224)
        for subject,x in v.records:
            self.assertEqual(n.infer(v,subject),strong.infer(v,subject))
        frozen=n.snapshot()
        cold=N.ActiveChallengerRepair.restore(oldN,frozen,S.world)
        self.assertEqual(cold.snapshot(),frozen)
        corrupted=json.loads(frozen)
        st=next(iter(corrupted["payload"]["states"].values()))
        st["weights_hex"]=hex(int(st["weights_hex"],16)^1)
        with self.assertRaisesRegex(ValueError,"WSP132R2_SNAPSHOT_CHECKSUM_MISMATCH"):
            N.ActiveChallengerRepair.restore(oldN,S.canon(corrupted),S.world)
        corrupted["sha256"]=N.digest(corrupted["payload"])
        with self.assertRaisesRegex(ValueError,"WSP132R2_FORGED_LEARNED_WEIGHTS"):
            N.ActiveChallengerRepair.restore(oldN,S.canon(corrupted),S.world)
        transfer=S.world(171000)
        zero=S.Custodian(transfer)
        self.assertEqual(zero.budget,0)
        with self.assertRaises(PermissionError):zero.query(transfer.records[0][0])
        self.assertEqual(zero.score_once({s:None for s,x in transfer.records})["source_calls"],0)

    def test_complete_frozen_r2_exposed_and_prospective_repair(self):
        result=E.run_engineering()
        print("WSP132_R2_FINAL_ENGINEERING_JSON="+S.canon(result))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["original_first_use"])
        self.assertFalse(result["native_admission"])
        self.assertTrue(result["old_warm_model_retained"])
        self.assertEqual(result["algorithmic_repair_number"],2)
        self.assertEqual(result["repair_limit"],3)
        self.assertEqual(result["paid_actions_per_target_world_per_arm"],32)
        self.assertEqual(result["each_cohort_target_paid_actions_per_arm"],3072)
        self.assertEqual(result["original_wsp131_frozen_negative"],
                         "DEVELOPMENT_NO_GO_UNCHANGED")
        self.assertEqual(result["r1_frozen_negative"],
                         "DEVELOPMENT_REPAIR_NO_GO_UNCHANGED")
        for cohort in ("exposed_diagnostic","new_prospective_synthetic"):
            z=result[cohort]
            self.assertTrue(z["cold_replay"])
            self.assertTrue(z["same_evidence_exact_symbolic_tie"])
            self.assertEqual(z["worlds"],{"known":64,"shear":32})
            for family,count in (("known",64),("shear",32)):
                for arm in E.ARMS:
                    item=z["scores"][family][arm]
                    self.assertEqual(item["held"],count*224)
                    self.assertEqual(item["source_calls"],count*32)
                self.assertEqual(z["scores"][family]["R2_ACTIVE_NUMERIC"],
                                 z["scores"][family]["R2_SAME_ACTION_SYMBOLIC"])
            if cohort=="new_prospective_synthetic":
                for arm in E.ARMS:
                    t=z["transfer"][arm]
                    self.assertEqual(t["held"],4096)
                    self.assertEqual(t["source_calls"],0)
        self.assertIn(result["status"],(
            "DEVELOPMENT_R2_REPAIR_SUPPORTED_ON_PUBLIC_SYNTHETIC_ONLY",
            "DEVELOPMENT_R2_REPAIR_PARTIAL",
            "DEVELOPMENT_R2_REPAIR_NO_GO"))
