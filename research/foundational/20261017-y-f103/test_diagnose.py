"""Y-F103: frozen parent TRAIN labels and genuine on-policy state audit."""
import importlib.util
import inspect
import math
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
p=importlib.util.spec_from_file_location("y_f103_diagnostic_under_test",HERE/"diagnose.py")
M=importlib.util.module_from_spec(p)
sys.modules[p.name]=M
p.loader.exec_module(M)

class F103SourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.parent,cls.native=M.load()
        cls.pack=cls.native.codec()

    def test_f103_prereg_first_and_f102_source_immutable(self):
        self.assertEqual(M.gitblob(HERE/"prereg.json"),M.PREREG_BLOB)
        self.assertEqual(M.gitblob(HERE.parent/"20261017-y-f102"/"delayed_credit.py"),M.F102_BLOB)
        self.assertEqual(M.gitblob(HERE.parent/"20261017-y-f102"/"prereg.json"),
                         M.F102_PREREG_BLOB)

    def test_source_is_fresh_negative_seed_and_not_original(self):
        for first,family,mode,nspace in M.DIAGS:
            self.assertLess(first,0)
            self.assertLess(family,0)
            public,q,proof=self.parent.episode(
                self.native,first,family,mode,nspace)
            self.assertEqual(len(public),72)
            self.assertEqual(len(q["ops"]) in (4,6,8),True)
            self.assertEqual(len(proof),64)
            with self.assertRaises(ValueError):
                self.native.source(first,family)

    def test_offline_label_summary_does_not_drop_negative(self):
        labels=(((0.,)*12,0),((0.,)*12,1),
                ((1.,)*12,-1),((1.,)*12,1))
        stats=M.summarize_labels(labels)
        self.assertEqual((stats["neg"],stats["zero"],stats["pos"]),(1,1,2))
        self.assertEqual(stats["conflicting_same_features"],2)
        self.assertEqual(stats["zero_feature_reward_counts"]["1"],1)

    def test_learner_api_has_no_future_answer_argument(self):
        self.assertEqual(tuple(inspect.signature(M.public_rollout).parameters),
                         ("native","pack","stream","weights"))
        self.assertEqual(tuple(inspect.signature(M.offline_counterfactual).parameters),
                         ("native","pack","stream","question","point"))

    def test_frozen_parent_train_only_weight_replay_exact(self):
        train=[]
        for i,family in enumerate((-31,-32)):
            for offset in range(8):
                seed=self.parent.TRAIN_START-offset
                stream,q,identity=self.parent.episode(
                    self.native,seed,family,"raw",i*8+offset)
                train.append((seed,family,stream,q,identity))
        rows=self.parent.train_examples(self.native,self.pack,train)
        weights,curve=self.parent.train_linear(rows,"raw")
        self.assertEqual(len(rows)>0,True)
        self.assertEqual(len(weights),12)
        self.assertEqual(len(curve),4)
        stream=train[0][2]
        from_new, fixed, checkpoints,_=M.public_rollout(
            self.native,self.pack,stream,weights)
        from_F102,_=self.parent.learned_online(self.native,stream,self.pack,
             lambda d:M.dot(weights,d))
        self.assertEqual(from_new,from_F102)
        self.assertEqual(len(checkpoints),6)
        self.assertEqual(all(v["online_future_question_visible"] is False
                             for _,v in checkpoints),True)

    def test_frozen_F60_teacher_control_replays_exactly(self):
        stream,q,_=self.parent.episode(self.native,-14001,-51,"raw",48)
        first,second,rows,_=M.public_rollout(
             self.native,self.pack,stream,(0.,)*12)
        mem=()
        for edge in stream: mem=self.native._f60_step(mem,edge,self.pack)
        self.assertEqual(second,mem)
        self.assertTrue(all(0<=p.chosen_index<len(p.native_states) for p,_ in rows))

    def test_offline_counterfactual_outcomes_are_valid_and_source_only(self):
        stream,q,_=self.parent.episode(self.native,-14001,-51,"raw",48)
        _,_,trace,_=M.public_rollout(self.native,self.pack,stream,(0.,)*12)
        for record,public in trace:
            local=M.offline_counterfactual(
                self.native,self.pack,stream,q,record)
            self.assertEqual(len(local["native_action_rewards"]),
                             public["learner_native_actions"])
            self.assertTrue(all(x in (0,1) for x in local["native_action_rewards"]))
            self.assertTrue(local["offline_future_answer_exclusively_here"])

    def test_malformed_stream_or_invalid_head_fails_closed(self):
        with self.assertRaises(M.Invalid):
            M.public_rollout(self.native,self.pack,((1,0,2),),(0.,)*12)
        with self.assertRaises(M.Invalid):
            M.evaluate("foo")

    def test_complete_report_is_diagnostic_not_new_scientific_success(self):
        out=M.evaluate("a"*40)
        self.assertEqual(out["training_examples"],out["label_support"]["total"])
        self.assertEqual(out["train_source_count"],16)
        self.assertEqual(out["fresh_F103_diagnostic_episodes"],16)
        self.assertEqual(out["checkpoint_count"],96)
        self.assertEqual(len(out["blocks"]),2)
        self.assertTrue(out["F102_GUARD_not_read_for_training_or_selection"])
        self.assertTrue(out["reserved_F62_source_sets_untouched"])
        self.assertEqual(out["native_memory_limit_bytes"],144)
        self.assertTrue(out["causation_of_F102_failure_not_established"])
        self.assertFalse(out["independent_scientific_firstuse"])
        self.assertFalse(out["protected_science_accepted"])
        self.assertFalse(out["optimizer_promoted"])
        self.assertEqual(out["accepted_ref_mutations"],0)
        for block in out["blocks"]:
            self.assertEqual(len(block["episodes"]),8)
            for ep in block["episodes"]:
                self.assertEqual(ep["events"],72)
                self.assertEqual(len(ep["checkpoints"]),6)
                self.assertTrue(all(a["source_native_memory_bytes"]<=144
                                    for a in ep["checkpoints"]))

if __name__=="__main__": unittest.main()
