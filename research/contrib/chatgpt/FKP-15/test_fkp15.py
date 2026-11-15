"""FKP15 fixture-only source guards and fully fitted conventional controls.

Fixture tests never call original FKP15 public DEV seeds or protected source.
"""
import hashlib
import unittest
import numpy as np

import source
import models
from models import DirectReturnMemory
import run_dev


class FixtureTests(unittest.TestCase):
    def _row(self,action:int,pattern:int=0):
        older=np.full((192,),np.float32((pattern%8)/8),dtype=np.float32)
        current=np.full((192,),np.float32(((pattern+1)%8)/8),dtype=np.float32)
        return source.feature_pair(older,current,action)

    def test_source_first_use_and_held_fences(self):
        self.assertEqual(source.TRAIN[0],975100)
        self.assertEqual(source.VALIDATION[-1],975215)
        self.assertEqual(source.DEV[0],975500)
        with self.assertRaises(PermissionError):
            source.source_branch(975600,0,0,upstream=None,allow_dev=True)
        with self.assertRaises(PermissionError):
            source.source_branch(975500,0,0,upstream=None)
        with self.assertRaises(PermissionError):
            source.source_branch(974000,0,0,upstream=None,allow_dev=True)
        with self.assertRaises(ValueError):
            source.cohort(True,allow_dev=True)
        self.assertEqual(len(source.prefix_actions(975100)),64)
        self.assertEqual(source.prefix_actions(975100),source.prefix_actions(975100))
        with self.assertRaises(ValueError):
            source.source_branch(975100,0,9,upstream=None)

    def test_public_rgb_feature_without_privileged_state(self):
        old=np.zeros((192,),dtype=np.float32)
        now=np.ones((192,),dtype=np.float32)
        row=source.feature_pair(old,now,2)
        self.assertEqual(row.shape,(393,))
        self.assertEqual(row.dtype,np.float32)
        self.assertEqual(float(row.sum()),193.)
        with self.assertRaises(ValueError):
            source.feature_pair(old,now,9)
        with self.assertRaises(ValueError):
            source.feature_pair(old[:20],now,2)

    def test_direct_numerical_learning_capacity_and_cold(self):
        memory=DirectReturnMemory(streams=2)
        before=self._row(3)
        other=self._row(8,3)
        memory.update(before,0.125)
        memory.update(other,-0.05)
        predictions=memory.predict(np.stack((before,other)))
        self.assertTrue(np.isfinite(predictions).all())
        self.assertEqual(memory.events,2)
        self.assertEqual(memory.raw_weights_bytes,131072)
        blob=memory.snapshot()
        cold=DirectReturnMemory.restore(blob)
        self.assertEqual(blob,cold.snapshot())
        self.assertTrue(np.array_equal(predictions,cold.predict(np.stack((before,other)))))
        corrupted=bytearray(blob)
        corrupted[30]^=1
        with self.assertRaises(ValueError):DirectReturnMemory.restore(bytes(corrupted))
        with self.assertRaises(ValueError):DirectReturnMemory.restore(blob[:-1])
        with self.assertRaises(ValueError):memory.update(before,float("nan"))
        with self.assertRaises(ValueError):memory.predict(np.zeros((4,392),dtype=np.float32))
        convention=DirectReturnMemory(streams=1).fit([{"x":before,"real_return":0.125}])
        self.assertEqual(convention.raw_weights_bytes,65536)
        self.assertEqual(convention.snapshot(),DirectReturnMemory.restore(convention.snapshot()).snapshot())

    def test_frozen_policy_choices_are_legal_and_reproducible(self):
        for arm in run_dev.ARMS:
            if arm=="FIXED_MACRO":scores=2
            elif arm=="RANDOM":scores=None
            else:scores=np.asarray([i/100 for i in range(9)],dtype=np.float64)
            a=run_dev.choose(arm,975500,16,scores)
            self.assertEqual(a,run_dev.choose(arm,975500,16,scores))
            self.assertIn(a,range(9))
        with self.assertRaises(PermissionError):
            run_dev.choose("DIRECT_ONLINE",975600,16,np.zeros(9))
        with self.assertRaises(ValueError):
            run_dev.choose("GRU_FROZEN",975500,16,np.zeros(8))

    def test_two_fully_trained_neural_models_and_ridge_use_same_fixture_evidence(self):
        synthetic=[]
        for index in range(18):
            action=index%9
            row=self._row(action,index%8)
            synthetic.append({"x":row,"real_return":float(action-4)/20.0})
        val=synthetic[:9]
        torch,trained,receipts=models.fit_controls(synthetic,val)
        self.assertEqual(set(trained),{"MLP_FROZEN","GRU_FROZEN","RIDGE_FROZEN"})
        for name in ("MLP_FROZEN","GRU_FROZEN"):
            self.assertEqual(receipts[name]["trained_epochs_each"],24)
            self.assertEqual(receipts[name]["trained_seeds"],[1212,3434])
        query=np.stack([r["x"] for r in val])
        for m in trained.values():
            z=models.predict_control(torch,m,query)
            self.assertEqual(z.shape,(9,))
            self.assertTrue(np.isfinite(z).all())

    def test_world_cluster_bootstrap_does_not_count_four_anchors_as_independent(self):
        rows=[]
        for seed in source.DEV:
            for anchor in source.ANCHORS:
                for arm in run_dev.ARMS:
                    rows.append({"seed":seed,"anchor":anchor,"arm":arm,
                                 "return":1.0 if arm=="DIRECT_ONLINE" else 0.5})
        means,best,gain,ci=run_dev.paired_bootstrap(rows)
        self.assertAlmostEqual(gain,0.5)
        self.assertAlmostEqual(ci[0],0.5)
        self.assertAlmostEqual(ci[1],0.5)

if __name__=="__main__":
    unittest.main()
