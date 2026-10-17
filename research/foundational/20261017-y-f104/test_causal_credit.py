"""F104: adversarial structural-credit and source-native online isolation contracts."""
import importlib.util
import inspect
import math
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf104_credit_under_test",HERE/"causal_credit.py")
M=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=M
spec.loader.exec_module(M)

class F104Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.parent,cls.f102,cls.native=M.load()
        cls.packing=cls.native.codec()

    def test_source_freeze_before_code_and_preserves_F103(self):
        self.assertEqual(M.blob(HERE/"prereg.json"),M.PREREG_BLOB)
        self.assertEqual(M.blob(HERE.parent/"20261017-y-f103"/"diagnose.py"),M.F103_BLOB)
        self.assertEqual(M.blob(HERE.parent/"20261017-y-f102"/"delayed_credit.py"),M.F102_BLOB)

    def test_fresh_source_split_uses_no_F102_F103_evidence(self):
        train=M.source_groups(self.f102,self.native,M.TRAIN)
        guard=M.source_groups(self.f102,self.native,M.GUARD)
        self.assertEqual([len(b) for b in train],[8,8])
        self.assertEqual([len(b) for b in guard],[8,8,8])
        allcases=[x for b in train+guard for x in b]
        self.assertEqual(len({p[3] for p in allcases}),40)
        self.assertTrue(all(p[0]<=-15001 for p in allcases))
        for seed,public,q,_ in allcases:
            self.assertEqual(len(public),72)
            with self.assertRaises(ValueError):
                self.native.source(seed,-61)

    def test_offline_source_path_exact_signed_edges_no_shortcuts(self):
        train=M.source_groups(self.f102,self.native,M.TRAIN)
        _,public,q,_=train[0][0]
        nodes,roles=M.source_path(public,q)
        self.assertEqual(len(nodes),len(q["ops"])+1)
        self.assertEqual(len(roles),len(q["ops"]))
        for i,(role,direction) in enumerate(q["ops"]):
            edge=(nodes[i],role,nodes[i+1]) if direction==1 else (
                nodes[i+1],role,nodes[i])
            self.assertIn(edge,public)

    def test_atomic_native_record_source_matches_but_fake_internal_does_not(self):
        nodes=(10,11,12,13)
        spans=M.subpaths(nodes,(0,2,4))
        self.assertIn((10,13,(0,2,4)),spans)
        self.assertNotIn((10,13,(0,)),spans)
        self.assertNotIn((10,13,(0,2)),spans)
        self.assertEqual(M.structural_retained_score(((10,13,(0,2,4)),),spans,self.native),3)
        self.assertEqual(M.structural_retained_score(((13,10,(5,3,1)),),spans,self.native),3)
        self.assertEqual(M.structural_retained_score(((10,12,(0,2,4)),),spans,self.native),0)

    def test_future_answer_does_not_enter_online_model(self):
        self.assertEqual(tuple(inspect.signature(M.online_teacher_and_explorer).parameters),
                         ("native","pack","public","weights","checkpoints"))
        self.assertEqual(tuple(inspect.signature(M.policy_memory).parameters),
                         ("native","pack","public","weights"))
        self.assertEqual(tuple(inspect.signature(M.source_path).parameters),
                         ("public","q"))

    def test_frozen_F102_raw_replay_and_natively_packable_action_choices(self):
        train=M.source_groups(self.f102,self.native,M.TRAIN)
        original=[]
        for fi,family in enumerate((-31,-32)):
            for i in range(8):
                seed=self.f102.TRAIN_START-i
                stream,q,d=self.f102.episode(self.native,seed,family,"raw",fi*8+i)
                original.append((seed,family,stream,q,d))
        labels=self.f102.train_examples(self.native,self.packing,original)
        weights,_=self.f102.train_linear(labels,"raw")
        public=train[0][0][1]
        M.PARENT=self.parent
        _,teacher,explorer=M.online_teacher_and_explorer(
            self.native,self.packing,public,weights)
        old,_=self.f102.learned_online(self.native,public,self.packing,
            lambda x:sum(a*b for a,b in zip(weights,x)))
        self.assertEqual(explorer,old)
        self.native._valid_memory(explorer,self.packing)
        self.assertLessEqual(len(explorer)*12,144)
        self.native._valid_memory(teacher,self.packing)

    def test_frozen_train_label_reports_account_for_both_outcomes(self):
        stats=M.support_report((((0.,)*12,1),((0.,)*12,-1),
                                ((1.,)*12,0),((1.,)*12,0)))
        self.assertEqual((stats["positive"],stats["negative"],stats["zero"]),
                         (1,1,2))
        self.assertEqual(stats["conflicting_feature_vectors"],1)
        self.assertEqual(stats["total"],4)

    def test_source_invalid_head_fails_closed(self):
        with self.assertRaises(M.Rejected):
            M.evaluate("not-a-hash")

    def test_full_report_preserves_negative_science_even_if_train_credit_positive(self):
        report=M.evaluate("a"*40)
        self.assertEqual(report["TRAIN_episodes"],16)
        self.assertEqual(report["GUARD_episodes"],24)
        self.assertEqual(len(report["GUARD_blocks"]),3)
        self.assertTrue(report["original_F102_F103_GUARD_never_loaded"])
        self.assertTrue(report["native_actions_and_144byte_record_cap_unchanged"])
        self.assertTrue(report["all_future_queries_hidden_from_online_policy"])
        self.assertEqual(len(report["TRAIN_causal_credit_receipts"]),192)
        self.assertFalse(report["protected_first_use"])
        self.assertFalse(report["scientific_acceptance"])
        self.assertEqual(report["accepted_ref_mutation"],False)
        self.assertFalse(report["optimizer_promotion"])
        self.assertFalse(report["CKB_connected"])
        self.assertEqual(report["training_support"]["mixed"]["total"],
                         report["training_support"]["teacher"]["total"]+
                         report["training_support"]["onpolicy"]["total"])
        for block in report["GUARD_blocks"]:
            self.assertEqual(len(block["cases"]),8)
            self.assertTrue(all(case["memory_budget_bytes"]==144 for case in block["cases"]))
            self.assertTrue(all(not case["question_visible_to_online_policy"]
                                for case in block["cases"]))
        self.assertEqual(set(report["totals"]),{
            "F60_fixed","F102_original_raw","F104_teacher_credit",
            "F104_mixed_onpolicy_credit","F62_zero"})

if __name__=="__main__": unittest.main()
