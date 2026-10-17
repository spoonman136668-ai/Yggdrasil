"""F102: exact native resource and label-blind delayed-credit stability contracts."""
import importlib.util
import math
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("y_f102_under_test",HERE/"delayed_credit.py")
M=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=M
spec.loader.exec_module(M)

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.f101,cls.f99,cls.native=M.source_modules()
        cls.pack=cls.native.codec()
        cls.train,cls.guards=M.source_split(cls.native)

    def test_freeze_preceded_all_F102_code_and_parents_unchanged(self):
        self.assertEqual(M.blob(HERE/"prereg.json"),M.PREREG_BLOB)
        self.assertEqual(M.blob(HERE.parent/"20261017-y-f101"/"causal_memory.py"),
                         M.F101_BLOB)

    def test_no_protected_source_seed_names_or_recycled_episodes(self):
        self.assertEqual(len(self.train),16)
        self.assertEqual([len(group) for group in self.guards],[8]*4)
        allrows=self.train+tuple(x for g in self.guards for x in g)
        self.assertEqual(len({x[4] for x in allrows}),48)
        self.assertTrue(all(x[0]<0 and x[1]<0 for x in allrows))
        self.assertTrue(all(len(x[2])==72 and len(set(x[2]))==72
                            for x in allrows))

    def test_guard_transformations_are_structural_and_withhold_question(self):
        self.assertEqual([x["mode"] for x in self.cfg["guard"]],
                         ["raw","swap_roles_and_invert","reverse_order","phase_and_roles"])
        for row in self.train+tuple(g[0] for g in self.guards):
            _seed,_family,public,q,_id=row
            self.assertEqual(len(q["ops"]) in (4,6,8),True)
            self.assertEqual(len(public[0]),3)
            self.assertEqual(len({a for a,_,b in public for a in (a,b)})>30,True)

    def test_source_native_codecs_and_fixed_memory_match_direct_F60(self):
        public=self.guards[0][0][2]
        memory=()
        for event in public:
            memory=self.native._f60_step(memory,event,self.pack)
        direct=self.native.controls()[0].online_fixed(public)
        self.assertEqual(memory,direct)
        self.assertLessEqual(len(memory),12)

    def test_real_counterfactual_training_labels_only_have_public_action_features(self):
        stream,q,_ = M.episode(self.native,-12117,-31,"raw",60)
        examples, counts=self.native.counterfactual_labels(stream,q,self.pack)
        self.assertGreater(len(examples),0)
        self.assertEqual(sum(counts.values()),len(examples))
        self.assertTrue(all(len(features)==12 and label in (-1,0,1)
                            for features,label in examples))
        self.assertTrue(any(label==0 for _,label in examples))

    def test_training_cycles_and_norm_clip_residual_finite(self):
        examples=((tuple(float(j%3-1) for j in range(12)),1),
                  (tuple(float((j+1)%3-1) for j in range(12)),-1),
                  (tuple(float((j+2)%3-1) for j in range(12)),0))
        scale=M.rms_from_train(examples)
        self.assertEqual(len(scale),12)
        for name in ("raw","clip","normalized","residual"):
            weights,logs=M.train_linear(examples,name,scale)
            self.assertEqual(len(weights),12)
            self.assertEqual(len(logs),4)
            self.assertTrue(all(math.isfinite(w) for w in weights))
            self.assertTrue(all(row["nonfinite"]==0 for row in logs))
        self.assertLessEqual(M.train_linear(examples,"residual",scale)[1][-1]["weights_l2"],
                             M.train_linear(examples,"raw",scale)[1][-1]["weights_l2"])

    def test_clip_intervention_caps_each_example_gradient(self):
        data=((tuple([100.] * 12),1),)
        _, logs=M.train_linear(data,"clip")
        self.assertEqual(logs[-1]["cycle"],4)
        self.assertGreater(logs[-1]["clipped_examples"],0)
        self.assertLessEqual(logs[-1]["update_l2_sum"],.081)

    def test_tiny_neural_uses_29_explicit_train_only_scalars(self):
        examples=((tuple(float(i%2) for i in range(12)),1),
                  (tuple(float(i%3==1) for i in range(12)),-1))
        neural=M.TinyNeural().train(examples)
        self.assertEqual(neural.parameters,29)
        self.assertEqual(len(neural.cycles),4)
        self.assertTrue(math.isfinite(neural.score(examples[0][0])))

    def test_policies_use_only_native_source_actions_same_record_budget(self):
        public=self.guards[0][0][2]
        source_features=lambda x:sum(x)
        memory,trace=M.learned_online(self.native,public,self.pack,source_features)
        limited,limited_trace=M.learned_online(self.native,public,self.pack,
                                                 source_features,max_depth=4)
        for output in (memory,limited):
            self.native._valid_memory(output,self.pack)
            self.assertLessEqual(len(output)*12,144)
        self.assertTrue(all(len(rec[2])<=4 for rec in limited))
        self.assertEqual(len(trace),len(limited_trace))
        self.assertEqual(len(trace),6)
        self.assertTrue(all("memory_packed_sha256" in event for event in trace))

    def test_hidden_question_not_in_online_interface(self):
        import inspect
        self.assertEqual(tuple(inspect.signature(M.learned_online).parameters),
                         ("native","public","packing","score_fn","max_depth"))
        self.assertEqual(tuple(inspect.signature(M.episode).parameters),
                         ("native","seed","family","mode","namespace"))

    def test_previously_protected_native_source_API_cannot_admit_F102(self):
        for seed,family in ((-12001,-31),(-13001,-41)):
            with self.assertRaises(ValueError):self.native.source(seed,family)
        with self.assertRaises(M.IntegrityError):
            M.episode(self.native,761000,1460,"raw",0)

    def test_frozen_learner_never_accepts_unbounded_invalid_variant(self):
        with self.assertRaises(M.IntegrityError):
            M.train_linear((((0.,)*12,0),),"retrofit")

if __name__=="__main__":unittest.main()
