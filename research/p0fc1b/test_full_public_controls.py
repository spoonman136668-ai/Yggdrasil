"""P0F-C1B strict source-free learning and custody tests: NOT source evidence."""
import copy
import math
import unittest

import numpy as np

from research.p0fc1b.full_public_controls import (
    FullFrameCategorical, TRAIN, SELECT, DEV, arrays, check_config,
    cluster_compare, frame_features
)


class FrozenConventionalSourceFree(unittest.TestCase):
    def test_exact_source_public_dev_only(self):
        z=check_config()
        self.assertEqual(len(TRAIN),24)
        self.assertEqual(len(SELECT),6)
        self.assertEqual(len(DEV),12)
        self.assertEqual(len(set(TRAIN+SELECT+DEV)),42)
        self.assertFalse(z["promotion"])
        self.assertIn("categorical",z["evaluation"].lower())

    def test_original_action_checked_and_history_source_fields_only(self):
        a=bytes([3,7,0])
        with self.assertRaisesRegex(ValueError, "ACTION_INVALID"):
            frame_features(a,8,7)
        sample=(17,a,1,(bytes([9,7,0]),0),None,bytes([3,9,0]))
        x,y,s=arrays([sample],3,True)
        self.assertEqual(x.shape,(1,18))
        self.assertEqual(tuple(y[0]),(3,9,0))
        self.assertEqual(int(s[0]),17)
        self.assertTrue(np.all(x[0,-6:]==0))

    def test_normalized_unseen_byte_and_full_outcome_entropy(self):
        xx=np.zeros((4,5),dtype=np.float64)
        yt=np.array([[0,2],[0,2],[1,2],[1,3]],dtype=np.uint8)
        model=FullFrameCategorical(5,yt,8,17)
        known=model.score(xx,yt)
        hold=model.score(xx,np.array([[242,239],[0,2],[1,3],[0,3]],dtype=np.uint8))
        self.assertTrue(np.all(np.isfinite(known)))
        self.assertTrue(np.all(np.isfinite(hold)))
        self.assertGreater(hold[0],known[0])
        self.assertGreater(float(hold[0]),float(hold[1]))

    def test_actual_gradient_updates_and_training_only_metrics(self):
        x=np.array([[0.,1.,0.],[1.,0.,1.],[0.,1.,1.],[1.,1.,0.]]*6)
        y=np.array([[1,0],[0,1],[1,1],[0,0]]*6,dtype=np.uint8)
        m=FullFrameCategorical(3,y,12,31)
        before=m.score(x,y).mean()
        identity=m.checkpoint_sha()
        m.train(x,y,.02,24,31)
        self.assertNotEqual(identity,m.checkpoint_sha())
        self.assertTrue(np.isfinite(m.score(x,y)).all())
        self.assertLess(m.score(x,y).mean(),before)
        self.assertGreater(m.checkpoint_bytes(),0)

    def test_held_dev_never_updates_trained_model(self):
        x=np.zeros((2,4));y=np.array([[2,4],[2,4]],dtype=np.uint8)
        m=FullFrameCategorical(4,y,6,17)
        identity=m.checkpoint_sha()
        v=m.score(x,np.array([[2,4],[12,13]],dtype=np.uint8))
        self.assertTrue(np.isfinite(v).all())
        self.assertEqual(m.checkpoint_sha(),identity)

    def test_one_independent_cluster_per_reset_not_per_step(self):
        seeds=np.repeat(np.array(DEV,dtype=np.int64),2)
        curr=np.ones((24,))*3.0
        hist=np.ones((24,))*2.0
        result=cluster_compare(seeds,curr,hist)
        self.assertEqual(result["independent_original_source_reset_clusters"],12)
        self.assertEqual(result["original_held_events"],24)
        self.assertAlmostEqual(result["paired_reset_seed_mean_full_frame_history_gain_nats"],1.0)
        self.assertGreater(result["paired_seed_cluster_95_percentile_interval"][0],0)


if __name__=="__main__":
    unittest.main()
