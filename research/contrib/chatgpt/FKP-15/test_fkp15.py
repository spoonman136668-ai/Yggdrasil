"""FKP-15 source-safe fixtures. Absolutely NO original first-use env.reset."""
from __future__ import annotations
from pathlib import Path
import hashlib
import sys
import unittest
from unittest import mock
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import source
import learners
import baselines
import run_dev


def public_fixture(seed,anchor):
    seq=[]
    im=np.full((16,24,3),(seed+anchor)%255,dtype=np.uint8)
    seq.append(source.public_feature(im,None,1))
    for t in range(anchor):
        im=np.full((16,24,3),(seed+anchor+t*3)%255,dtype=np.uint8)
        seq.append(source.public_feature(im,(t%3,(t//3)%3),t%3))
    array=np.stack(seq).astype(np.float32)
    context=array[-min(8,len(array)):].mean(axis=0,dtype=np.float64).astype(np.float32)
    ret=np.asarray([round(.1*((i+seed+anchor)%4)-.05*((seed+i)%2),3)
                    for i in range(9)],dtype=np.float64)
    digest=hashlib.sha256(array.tobytes()).hexdigest()
    return {"valid":True,"seed":seed,"anchor":anchor,
            "sequence":array,"context":context,"returns":ret,
            "prefix_sha256":digest,
            "branches_sha256":[hashlib.sha256(bytes((i,))+array.tobytes()).hexdigest()
                               for i in range(9)],
            "physical_steps":(anchor+16)*9+anchor,
            "physical_resets":10,
            "goal_by_action":[0]*9}


class TestFKP15(unittest.TestCase):
    def test_disjoint_new_cohorts_and_protected_fence(self):
        self.assertEqual(source.SOURCE_SHA,"a94f2b60d1769ea44df3226561488768e1dff9f4")
        self.assertEqual((len(source.TRAIN),len(source.VAL),len(source.DEV)),(64,16,32))
        self.assertEqual(source.ANCHORS,(0,16,32,64))
        self.assertEqual(source.HORIZON,16)
        self.assertEqual(len(source.ACTIONS),9)
        self.assertTrue(set(source.TRAIN).isdisjoint(source.VAL))
        self.assertTrue(set(source.DEV).isdisjoint(source.TRAIN))
        self.assertTrue(set(source.DEV).isdisjoint(source.VAL))
        self.assertTrue(set(source.DEV).isdisjoint(source.TRANSFER))
        self.assertEqual(source.OPTIONS,{"reward_fall_off":-0.05,"max_steps":512})
        for seed in (970100,971500,973500,974000,974500,975600,1900,True):
            with self.assertRaises((PermissionError,ValueError)):
                source.gate(seed)
        with self.assertRaises(PermissionError):source.gate(source.DEV[0])
        with self.assertRaises(PermissionError):source.real_prefix(source.DEV[0],0)
        self.assertEqual(source.gate(source.DEV[0],allow_dev=True),"DEVELOPMENT")
        with self.assertRaises(PermissionError):
            source.collect(source.DEV)
        with self.assertRaises(PermissionError):
            source.collect(source.TRANSFER)
        with self.assertRaises(PermissionError):
            source.collect((source.DEV[0],),allow_dev=True)

    def test_original_source_public_history_featurization(self):
        rgb=np.full((32,40,3),128,dtype=np.uint8)
        x=source.public_feature(rgb,None,1)
        self.assertEqual(x.shape,(204,))
        self.assertEqual(x.dtype,np.float32)
        self.assertTrue(np.array_equal(x[192:201],np.zeros(9)))
        self.assertEqual(x[202],1)
        y=source.public_feature(rgb,(2,1),0)
        self.assertEqual(y[192+7],1)
        self.assertEqual(y[201],1)
        with self.assertRaises(ValueError):
            source.public_feature(rgb,(9,9),1)
        with self.assertRaises(ValueError):
            source.public_feature(np.zeros((4,16,3),dtype=np.uint8),None,1)
        for seed in (source.TRAIN[0],source.VAL[-1],source.DEV[0]):
            a=source.prefix(seed,64)
            self.assertEqual(a,source.prefix(seed,64))
            self.assertEqual(len(a),64)
            self.assertTrue(all(a[i:i+8].count(a[i])==8 for i in range(0,64,8)))

    def test_direct_count_weight_programming_cold_and_negative_controls(self):
        data=[public_fixture(source.TRAIN[i],a)
              for i in range(4) for a in source.ANCHORS]
        direct=learners.DirectValues().fit(data)
        count=learners.DirectValues(two_keys=False).fit(data)
        shuffled=learners.DirectValues(shuffled=True).fit(data)
        self.assertEqual(direct.count.nbytes+direct.sum_milli.nbytes,294912)
        self.assertEqual(direct.count.shape,(4096,9))
        self.assertEqual(int(direct.count.sum()),2*9*len(data))
        x=np.stack([d["context"] for d in data])
        y=direct.predict(x)
        self.assertEqual(y.shape,(len(data),9))
        self.assertTrue(np.isfinite(y).all())
        cold=direct.snapshot()
        self.assertEqual(cold,learners.DirectValues.restore(cold).snapshot())
        self.assertTrue(np.array_equal(y,learners.DirectValues.restore(cold).predict(x)))
        corrupt=bytearray(cold);corrupt[100]^=1
        with self.assertRaises(ValueError):
            learners.DirectValues.restore(bytes(corrupt))
        self.assertTrue(np.isfinite(count.predict(x)).all())
        self.assertTrue(np.isfinite(shuffled.predict(x)).all())
        self.assertGreaterEqual(learners.mse(y,np.stack([d["returns"] for d in data])),0)

    def test_strong_trained_controllers_all_epochs_and_dev_unopened(self):
        train=[public_fixture(source.TRAIN[i],a) for i in range(3)
               for a in source.ANCHORS]
        val=[public_fixture(source.VAL[i],a) for i in range(2)
             for a in source.ANCHORS]
        models=run_dev.value_predictors(train,val)
        self.assertEqual(set(models["fit_info"]),{"GRU","MLP"})
        for kind in ("GRU","MLP"):
            info=models["fit_info"][kind]
            self.assertEqual(info["epochs_per_seed"],24)
            self.assertEqual(info["seeds_trained"],[1515,2626])
            self.assertGreater(info["parameters"],0)
            prediction=baselines.prediction(models[kind],kind,val,models["torch"])
            self.assertEqual(prediction.shape,(8,9))
            self.assertTrue(np.isfinite(prediction).all())
        self.assertEqual(models["KNN_receipt"]["hyperparameter"] in (1,5,15),True)
        self.assertEqual(models["RIDGE_receipt"]["hyperparameter"] in (.01,1.,100.),True)
        # A real held-world prefix has NO unchosen action rewards.
        blind=[{k:v for k,v in r.items() if k not in
                ("returns","goal_by_action","branches_sha256")} for r in val]
        for kind in ("GRU","MLP"):
            scores=baselines.prediction(models[kind],kind,blind,models["torch"])
            self.assertEqual(scores.shape,(len(val),9))
            self.assertTrue(np.isfinite(scores).all())
        sealed=run_dev.prior_seal(train,val,models)
        self.assertEqual(len(sealed),64)
        self.assertEqual(sealed,run_dev.prior_seal(train,val,models))

    def test_mocked_development_branch_selection_is_blind(self):
        train=[public_fixture(source.TRAIN[i],a) for i in range(3)
               for a in source.ANCHORS]
        val=[public_fixture(source.VAL[i],a) for i in range(2)
             for a in source.ANCHORS]
        models=run_dev.value_predictors(train,val)
        class FakeEnv:
            def close(self):pass
        calls=[]
        def mocked_prefix(seed,anchor,allow_dev=False):
            self.assertTrue(allow_dev)
            row=public_fixture(seed,anchor)
            for forbidden in ("returns","goal_by_action","branches_sha256"):
                row.pop(forbidden,None)
            row["source_steps"]=anchor
            row["env"]=FakeEnv()
            return row
        def mocked_branch(seed,anchor,allow_dev=False):
            self.assertTrue(allow_dev)
            calls.append((seed,anchor))
            return public_fixture(seed,anchor)
        with mock.patch.object(source,"real_prefix",side_effect=mocked_prefix),mock.patch.object(
            source,"collect_one",side_effect=mocked_branch):
            result,cost,dev_sha=run_dev.dev_once(models)
        self.assertEqual(len(result),len(source.DEV)*len(source.ANCHORS))
        self.assertEqual(len(calls),len(result))
        self.assertTrue(all(r["valid"] for r in result))
        self.assertTrue(all(len(r["chosen_actions"])==9 for r in result))
        self.assertTrue(all(all(0<=x<9 for x in r["chosen_actions"].values()) for r in result))
        self.assertGreater(cost,0)
        self.assertEqual(len(dev_sha),64)
        best,means,ci,n=run_dev.paired_bootstrap(result)
        self.assertIn(best,run_dev.STRONG)
        self.assertEqual(len(ci),2)
        self.assertEqual(n,32)
        self.assertTrue(np.isfinite(list(means.values())).all())

    def test_no_private_source_features_or_learned_dev_updates(self):
        import ast
        s=(HERE/"source.py").read_text(encoding="utf-8")
        t=(HERE/"run_dev.py").read_text(encoding="utf-8")
        nodes=(n for program in (s,t) for n in ast.walk(ast.parse(program)))
        self.assertFalse(any(isinstance(node,ast.Attribute) and node.attr in
                             ("unwrapped","_env","position")
                             for node in nodes))
        self.assertNotIn("debug_rgb_array",s+t)
        self.assertIn("env.step(",s)
        self.assertEqual(baselines.EPOCHS,24)
        self.assertEqual(baselines.SEEDS,(1515,2626))

if __name__=="__main__":unittest.main()
