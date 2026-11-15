"""FKP-12 source-safe fixtures: no DEV/transfer/protected world source usage."""
from pathlib import Path
import hashlib
import sys
import unittest

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import source
import model
import baselines


class FKP12Fixtures(unittest.TestCase):
    def test_frozen_source_seeds_and_public_actions(self):
        self.assertEqual(source.SOURCE_SHA,
                         "a94f2b60d1769ea44df3226561488768e1dff9f4")
        self.assertEqual(len(source.TRAIN),16)
        self.assertEqual(len(source.VALIDATION),4)
        self.assertEqual(len(source.DEV),8)
        self.assertEqual(len(source.RESERVED_TRANSFER),8)
        self.assertFalse(set(source.TRAIN)&set(source.VALIDATION))
        self.assertFalse(set(source.DEV)&set(source.TRAIN))
        self.assertFalse(set(source.DEV)&set(source.VALIDATION))
        self.assertEqual(source.FEATURE_DIM,204)
        self.assertEqual(source.CAP_STEPS,256)
        for s in (971100,971600,1900,972100,True):
            with self.assertRaises((PermissionError,ValueError)):
                source.permitted(s)
        with self.assertRaises(PermissionError):
            source.permitted(source.DEV[0])
        self.assertEqual(source.permitted(source.DEV[0],True),"DEV")
        for p in source.POLICIES:
            seq=[source.action(source.TRAIN[0],p,t) for t in range(17)]
            self.assertEqual(seq,[source.action(source.TRAIN[0],p,t) for t in range(17)])
            self.assertTrue(all(len(x)==2 and all(0<=a<3 for a in x) for x in seq))
            if p=="macro8":
                self.assertEqual(len(set(seq[0:8])),1)
                self.assertEqual(len(set(seq[8:16])),1)
        with self.assertRaises(PermissionError):
            source.action(1900,"uniform",0)

    def test_public_images_causal_action_and_prev_feedback(self):
        im=np.zeros((32,48,3),dtype=np.uint8)
        im[0:16,:,0]=255
        feature=source.input_feature(im,(1,2),0)
        self.assertEqual(feature.shape,(204,))
        self.assertEqual(feature.dtype,np.float32)
        self.assertEqual(feature[192+5],1)
        self.assertEqual(feature[201],1)
        self.assertTrue(np.all(feature[:192]>=0))
        alt=source.input_feature(im,(0,0),2)
        self.assertFalse(np.array_equal(feature,alt))
        self.assertEqual(source.label(-0.05),0)
        self.assertEqual(source.label(0.),1)
        self.assertEqual(source.label(0.1),2)
        with self.assertRaises(ValueError):
            source.input_feature(im,(3,0),1)
        with self.assertRaises(ValueError):
            source.pooled_public_rgb(np.zeros((4,8,3),dtype=np.uint8))

    @staticmethod
    def fabricated_episode(n,offset):
        rows=[];labels=[]
        for t in range(n):
            im=np.full((16,16,3),((t+offset)*37)%255,dtype=np.uint8)
            rows.append(source.input_feature(im,((t+offset)%3,(t+1)%3),t%3))
            labels.append((t+offset)%3)
        return {"x":np.stack(rows),"y":np.asarray(labels,dtype=np.int64)}

    def test_direct_nongradient_weights_stable_cold_and_tamper(self):
        train=[self.fabricated_episode(33,0),self.fabricated_episode(27,4)]
        direct=model.DirectMemory().fit(train)
        self.assertEqual(direct.weights.shape,(4096,3))
        self.assertEqual(direct.weights.dtype,np.int32)
        self.assertEqual(direct.weights.nbytes,49152)
        self.assertEqual(int(direct.weights.sum()),120)
        x=train[0]["x"]
        p=direct.predict(x)
        self.assertEqual(p.shape,(33,3))
        self.assertTrue(np.isfinite(p).all())
        self.assertTrue(np.allclose(p.sum(axis=1),1))
        blob=direct.snapshot()
        restored=model.DirectMemory.restore(blob)
        self.assertEqual(blob,restored.snapshot())
        self.assertTrue(np.array_equal(p,restored.predict(x)))
        tampered=bytearray(blob);tampered[99]^=1
        with self.assertRaises(ValueError):
            model.DirectMemory.restore(bytes(tampered))
        no_action=model.DirectMemory(ignore_action=True).fit(train)
        one_key=model.DirectMemory(two_hash=False).fit(train)
        shuffled=model.DirectMemory().fit(train,shuffle_labels=True)
        self.assertTrue(np.isfinite(no_action.predict(x)).all())
        self.assertTrue(np.isfinite(one_key.predict(x)).all())
        self.assertTrue(np.isfinite(shuffled.predict(x)).all())
        self.assertGreaterEqual(model.brier(p,train[0]["y"]),0)
        self.assertGreaterEqual(model.logloss(p,train[0]["y"]),0)

    def test_no_held_or_private_sources_in_models(self):
        text=(HERE/"source.py").read_text()
        self.assertNotIn("env.unwrapped",text)
        self.assertNotIn("debug_rgb_array",text)
        self.assertNotIn("env.render(",text)
        self.assertIn("env.step(",text)
        self.assertEqual(baselines.SEEDS,(1212,3434))
        self.assertEqual(baselines.EPOCHS,24)
        self.assertEqual(baselines.HIDDEN,64)

    def test_all_public_feature_controls_refuse_invalid_input(self):
        with self.assertRaises(ValueError):
            model.indices(np.zeros((2,195),dtype=np.float32))
        with self.assertRaises(ValueError):
            source.input_feature(np.zeros((16,16,3),dtype=np.uint8),(1,1),5)
        with self.assertRaises(ValueError):
            source.collect(tuple(source.RESERVED_TRANSFER))
        with self.assertRaises(PermissionError):
            source.collect(tuple(source.DEV))


if __name__=="__main__":
    unittest.main()
