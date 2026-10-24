"""MR34J0 source-free checks of third public adapter, frozen roles and evaluation."""
import json
from pathlib import Path
import sys
import unittest

import numpy as np

from research.mr34j0 import third_transfer as q
from research.mr34f.prospective_controls import current_vector,original_target

class ThirdTransferTests(unittest.TestCase):
    def test_frozen_dev_source_custody_and_original_author(self):
        self.assertEqual(q.FIRST,"67ceb8db50db5e52fe6387358b0cd6b43947cb9d")
        self.assertEqual(q.PARENT,"06afcc66f26ef02605bdcca45ed89cada3d2ac48")
        self.assertEqual(q.NATIVE_ORIGINAL,"8e1561eb1a542e21307bac669c42435cf48e59bd")
        self.assertEqual(q.UPSTREAM_SHA,"c6d406680d552489c3230dec9714b066c7fd303d")
        self.assertEqual(len(q.TRAIN),20)
        self.assertEqual(len(q.THIRD_DEV),8)
        self.assertFalse(set(q.TRAIN)&set(q.THIRD_DEV))
        self.assertEqual(q.CONTROL_EPOCHS,48)
        self.assertEqual(q.MODEL_INIT,(17,31))
        self.assertEqual(q.DEV_MAX_STEPS,48)
        self.assertEqual(q.STREAMS,(0,1))
        q.frozen_check()

    def test_public_unicode_packed_losslessly_and_target_preaction(self):
        old=np.asarray([[".",".","."],[".","♥","."],[".",".","?"]],dtype="<U1")
        new=np.asarray([[".",".","."],[".","♥","."],[".",".","!"]],dtype="<U1")
        before=q.third_public_bridge(old)
        after=q.third_public_bridge(new)
        self.assertEqual(len(before),36)
        self.assertEqual(len(after),36)
        self.assertNotEqual(before,after)
        original_codepoints=np.frombuffer(before,dtype="<u4").tolist()
        self.assertEqual(original_codepoints,[ord(str(x)) for x in old.flat])
        x=current_vector(before,3)
        self.assertEqual(x.shape,(23,))
        self.assertTrue(np.array_equal(x[16:],np.array([0.,0.,0.,1.,0.,0.,0.])))
        y=original_target(before,after)
        self.assertEqual(y.shape,(8,))
        self.assertGreaterEqual(int(np.count_nonzero(y)),1)
        self.assertEqual(float(np.sum(original_target(before,before))),0.)

    def test_original_source_public_guard_fail_closed(self):
        with self.assertRaises(ValueError):
            q.third_public_bridge(np.zeros((3,3),dtype=np.uint8))
        with self.assertRaises(ValueError):
            q.third_public_bridge(np.array(["bad"],dtype="<U3"))

    def test_postsealed_inference_scores_true_eight_bit_loss(self):
        class DummyNative:
            def forward(self,ep,zero_state=False):
                return np.full((len(ep),8),.25 if zero_state else .75)
        class DummyRecurrent:
            def forward(self,ep):
                return np.full((len(ep),8),.5),[]
        class DummyLogistic:
            def forecast(self,ep):
                return np.full((len(ep),8),.5)
        fake=[(np.zeros(23),np.zeros(69),np.ones(8)) for _ in range(2)]
        prior=np.full(8,.375)
        native=DummyNative()
        self.assertEqual(q.model_prediction("native45",native,prior,fake).shape,(2,8))
        self.assertEqual(q.model_prediction("native45_memory_zeroed",native,prior,fake)[0,0],.25)
        self.assertEqual(q.model_prediction("current_logistic",DummyLogistic(),prior,fake)[0,0],.5)
        self.assertEqual(q.model_prediction("trained_8state_recurrent",DummyRecurrent(),prior,fake)[0,0],.5)
        self.assertEqual(q.model_prediction("familiar_fit_beta_prior",None,prior,fake)[0,0],.375)

    def test_held_source_step_is_only_after_models_sealed(self):
        p=Path(q.__file__).read_text()
        i=p.index("models,prior,fit,seal=fit_familiar")
        j=p.index("unknown,third_custody=acquire_original_third")
        self.assertLess(i,j)
        self.assertIn("source_original_git_readonly",p)
        self.assertIn("env.step(action)",p)
        self.assertIn("BirdEyeWrapper(",p)
        self.assertNotIn("third_source.reward",p)
        self.assertNotIn("env.unwrapped",p)


if __name__=="__main__":
    unittest.main()
