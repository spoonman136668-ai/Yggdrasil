"""Y-F105: offline multi-step teacher and public-only native relational features."""
import importlib.util
import inspect
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf105_credit_tested",HERE/"relational_credit.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.f104,cls.parent,cls.f102,cls.native=m.load()
        cls.pack=cls.native.codec()

    def test_exact_precode_protocol_and_immutable_F104(self):
        self.assertEqual(m.blob(HERE/"prereg.json"),m.FREEZE)
        self.assertEqual(m.blob(HERE.parent/"20261017-y-f104"/"causal_credit.py"),
                         m.F104_BLOB)

    def test_native_source_cohorts_new_and_separate(self):
        tr=m.cohorts(self.f104,self.f102,self.native,m.TRAIN)
        gu=m.cohorts(self.f104,self.f102,self.native,m.GUARD)
        self.assertEqual([len(x) for x in tr],[8,8])
        self.assertEqual([len(x) for x in gu],[8,8,8,8])
        allcases=[x for group in tr+gu for x in group]
        self.assertEqual(len(allcases),48)
        self.assertEqual(len({x[3] for x in allcases}),48)
        self.assertTrue(all(x[0]<0 and len(x[1])==72 for x in allcases))

    def test_forward_backward_signed_record_structure(self):
        record=((10,20,(0,2)),)
        arcs=m.orient(record)
        self.assertEqual(arcs,((0,10,20,(0,2)),(0,20,10,(3,1))))
        self.assertEqual(m.state_eight(record,(10,0,20))[:4],(1.,2.,1.,2.))
        self.assertEqual(m.state_eight(record,(10,0,20))[4:6],(0.,0.))

    def test_online_composition_counts_change_when_middle_join_removed(self):
        b=((10,20,(0,)),(20,30,(2,)),(30,40,(4,)))
        full=m.state_eight(b,(10,0,20))
        damaged=m.state_eight((b[0],b[2]),(10,0,20))
        self.assertGreater(full[4],damaged[4])
        self.assertGreater(full[5],damaged[5])
        self.assertGreater(full[3],damaged[3])

    def test_online_api_never_takes_question_or_future_path(self):
        self.assertEqual(tuple(inspect.signature(m.online).parameters),
                         ("native","parent","pack","stream","weights",
                          "ablated","keep_trace"))
        self.assertEqual(tuple(inspect.signature(m.features).parameters),
                         ("parent","legal","baseline","event"))
        self.assertEqual(tuple(inspect.signature(m.teacher_examples).parameters),
                         ("f104","parent","f102","native","pack","train"))

    def test_native_action_features_bounded_12_plus_eight(self):
        stream=m.cohorts(self.f104,self.f102,self.native,m.TRAIN)[0][0][1]
        actions=self.native.actions((),stream[0],0,self.pack)
        baseline=self.native._f60_step((),stream[0],self.pack)
        vectors=m.features(self.parent,actions,baseline,stream[0])
        self.assertEqual(len(vectors),len(actions))
        self.assertTrue(all(len(v)==20 for v in vectors))
        self.assertTrue(all(v[:12]==tuple(float(x-y) for x,y in zip(
               act[4],next(a[4] for a in actions if a[3]==baseline)))
                    for v,act in zip(vectors,actions)))

    def test_fit_same_train_data_preserves_trainable_parameter_count(self):
        rows=(((1.,)*20,1),((-1.,)*20,-1),((0.,)*20,0))
        for n in (12,20):
            weights,curve=m.fit(rows,n)
            self.assertEqual(len(weights),n)
            self.assertEqual(len(curve),4)
            self.assertTrue(all(t["nonfinite"]==0 for t in curve))
        with self.assertRaises(m.IntegrityError):m.fit(rows,21)

    def test_online_same_source_actions_preserve_real_144byte_native_memory(self):
        stream=m.cohorts(self.f104,self.f102,self.native,m.TRAIN)[0][0][1]
        for width,ablation in ((12,False),(20,False),(20,True)):
            final,trace=m.online(self.native,self.parent,self.pack,stream,
                                 (0.,)*width,ablated=ablation,keep_trace=True)
            self.native._valid_memory(final,self.pack)
            self.assertLessEqual(len(final)*12,144)
            self.assertEqual(len(trace),6)
            self.assertTrue(all(len(c["chosen_feature20"])==20 for c in trace))
            self.assertTrue(all(len(c["native_record_endpoints"])<=12 for c in trace))

    def test_full_result_positives_and_negatives_not_promoted(self):
        z=m.evaluate("a"*40)
        self.assertEqual(z["train_episodes"],16)
        self.assertEqual(z["guard_episodes"],32)
        self.assertEqual(z["training_examples"]["total"],
                         sum(r["pos"]+r["neg"]+r["neutral"]
                             for r in z["training_receipts"]))
        self.assertEqual(len(z["training_receipts"]),96)
        self.assertEqual(len(z["online_feature_names"]),20)
        self.assertEqual(len(z["learned_12_weights"]),12)
        self.assertEqual(len(z["learned_20_weights"]),20)
        self.assertEqual(len(z["blocks"]),4)
        self.assertEqual(len(z["totals"]),6)
        self.assertTrue(z["F102_to_F104_consumed_GUARD_untouched"])
        self.assertFalse(z["protected_firstuse"])
        self.assertFalse(z["independent_science_acceptance"])
        self.assertEqual(z["Codex_calls"],0)
        self.assertEqual(z["accepted_ref_changes"],0)
        for b in z["blocks"]:
            self.assertEqual(len(b["cases"]),8)
            for c in b["cases"]:
                self.assertEqual(len(c["scores"]),6)
                self.assertTrue(all(v in (0,1) for v in c["scores"].values()))
                self.assertTrue(all(v<=144 for v in c["native_final_bytes_by_arm"].values()))
                self.assertTrue(c["question_hidden_during_online_inference"])

if __name__=="__main__":unittest.main()
