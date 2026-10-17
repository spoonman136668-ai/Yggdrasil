"""F106: genuine native feature equivalence collisions, no new learned policy."""
import importlib.util
import inspect
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("yf106_source_test",HERE/"identifiability.py")
m=importlib.util.module_from_spec(s)
sys.modules[s.name]=m
s.loader.exec_module(m)

class F106Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.f105,cls.f104,cls.parent,cls.f102,cls.native=m.load()

    def test_separate_precode_prereg_and_f105_source_unchanged(self):
        self.assertEqual(m.gitblob(HERE/"prereg.json"),m.PREREG_GIT_BLOB)
        self.assertEqual(m.gitblob(HERE.parent/"20261017-y-f105"/"relational_credit.py"),
                         m.F105_GIT_BLOB)
        self.assertEqual(m.gitblob(HERE.parent/"20261017-y-f104"/"causal_credit.py"),
                         m.F104_GIT_BLOB)

    def test_diagnostic_cases_are_new_disjoint_and_not_protected(self):
        new=m.f105_groups if hasattr(m,"f105_groups") else m.NEW
        self.assertEqual([(s,f) for s,f,_,_ in new],[(-19001,-101),(-19101,-102)])
        train=self.f105.cohorts(self.f104,self.f102,self.native,self.f105.TRAIN)
        diag=self.f105.cohorts(self.f104,self.f102,self.native,m.NEW)
        self.assertEqual([len(b) for b in diag],[8,8])
        allcases=[x for b in train+diag for x in b]
        self.assertEqual(len({x[3] for x in allcases}),32)
        self.assertTrue(all(x[0]<0 and len(x[1])==72 for x in allcases))
        for seed,_,_,_ in allcases:
            self.assertNotIn(seed,[-18001,-18101,-18201,-18301,-16001,-16101])

    def test_actor_api_has_no_answer_or_delayed_teacher_input(self):
        self.assertEqual(tuple(inspect.signature(self.f105.online).parameters),
                         ("native","parent","pack","stream","weights","ablated","keep_trace"))
        self.assertEqual(tuple(inspect.signature(m.collect).parameters),
                         ("f105","f104","parent","f102","native","pack","groups"))
        self.assertTrue("future_path_never_online" in
                         (HERE/"identifiability.py").read_text())

    def test_feature_aliasing_exact_classifier_lower_bound(self):
        def row(i,twenty,label,state):
            return dict(record_id=str(i),source_native_12=[0.]*12,
                  online_graph_delta_8=[twenty]+[0.]*7,
                  label_OFFLINE_TRAIN_OR_DIAGNOSTIC_ONLY=label,
                  exact_visible_local_state_sha256=state,
                  current_memory_sha256="x",current_event_sha256="z",
                  source_identity_sha256="g",checkpoint=11)
        rows=[row(1,0,1,"state1"),row(2,0,-1,"state2"),
              row(3,1,1,"state3"),row(4,1,0,"state4")]
        e12=m.equivalences(rows,"12")
        e20=m.equivalences(rows,"20")
        exact=m.equivalences(rows,"exact")
        self.assertEqual(e12["empirical_unavoidable_label_disagreements"],2)
        self.assertEqual(e20["conflicting_classes"],2)
        self.assertEqual(e20["empirical_unavoidable_label_disagreements"],2)
        self.assertEqual(exact["conflicting_classes"],0)
        self.assertEqual(exact["empirical_unavoidable_label_disagreements"],0)
        self.assertEqual(sum(k["class_size"] for k in e20["conflicting_classes_detail"]),4)

    def test_information_loss_from_merging_equivalence_classes_is_monotonic(self):
        rows=[]
        for i in range(6):
            rows.append(dict(record_id=str(i),source_native_12=[float(i%2)]+[0.]*11,
                 online_graph_delta_8=[float(i//2)]+[0.]*7,
                 label_OFFLINE_TRAIN_OR_DIAGNOSTIC_ONLY=(-1,0,1)[i%3],
                 exact_visible_local_state_sha256=str(i),
                 source_identity_sha256="x",current_memory_sha256="y",
                 current_event_sha256="z",checkpoint=11))
        coarse=m.equivalences(rows,"12")
        finer=m.equivalences(rows,"20")
        self.assertGreaterEqual(finer["empirical_majority_correct"],
                                coarse["empirical_majority_correct"])

    def test_missing_input_and_unknown_key_fail_closed(self):
        with self.assertRaisesRegex(m.Invalid,"INVALID_EQUIVALENCE_TYPE"):
            m.equivalences([],"retune")
        with self.assertRaisesRegex(m.Invalid,"EXACT_GIT_HEAD_REQUIRED"):
            m.evaluate("unqualified")

    def test_original_F105_TRAIN_replay_exact_label_data(self):
        train=self.f105.cohorts(self.f104,self.f102,self.native,self.f105.TRAIN)
        pack=self.native.codec()
        actual,_=m.collect(self.f105,self.f104,self.parent,self.f102,
                            self.native,pack,train)
        old,_=self.f105.teacher_examples(self.f104,self.parent,self.f102,
                                         self.native,pack,train)
        self.assertEqual(len(actual),len(old))
        self.assertTrue(all(tuple(a["source_native_12"]+a["online_graph_delta_8"])==x
                            and a["label_OFFLINE_TRAIN_OR_DIAGNOSTIC_ONLY"]==y
                            for a,(x,y) in zip(actual,old)))

    def test_full_source_only_diagnostic_no_model_tuning_or_science_claim(self):
        d=m.evaluate("a"*40)
        self.assertEqual(d["old_F105_TRAIN_actions"],1055)
        self.assertEqual(d["new_public_diagnostic_episodes"],16)
        self.assertEqual(len(d["new_D106_blocks"]),2)
        self.assertTrue(d["frozen_F105_TRAIN_reproduced"])
        self.assertTrue(d["F102_F103_F104_F105_GUARD_not_loaded"])
        self.assertTrue(d["no_F106_retraining_or_model_selection"])
        self.assertEqual(d["accepted_ref_mutations"],0)
        self.assertFalse(d["independent_science_accepted"])
        self.assertFalse(d["protected_firstuse"])
        self.assertFalse(d["CKB_connected"])
        for b in d["new_D106_blocks"]:
            self.assertEqual(b["count"],8)
            self.assertEqual(len(b["online_controls"]),8)
            self.assertEqual(len(b["checkpoint_receipts"]),48)
            self.assertEqual(len(b["per_action_records"]),b["actions"])
            self.assertTrue(all(r["source_native_memory_bytes"]<=144
                                for r in b["per_action_records"]))
            for key in ("12","20","exact","prefix"):
                e=b["equiv"][key]
                self.assertEqual(e["row_count"],b["actions"])
                self.assertEqual(e["empirical_majority_correct"]+
                    e["empirical_unavoidable_label_disagreements"],b["actions"])

if __name__=="__main__":unittest.main()
