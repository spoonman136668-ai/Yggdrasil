"""MG93 frozen source checkpoint and prospective cohort engineering only.

These source-only assertions are not authentic MiniGrid task results.
"""
import hashlib
import unittest
from research.native.itd02.mg93 import paired_original_dev as mg93
from research.native.itd02.mg92.feedback_cells import PublicFeedbackGate
from research.native.itd02.mg91.native_prototypes import PublicRewardPrototypes
from research.native.itd02.mg91.independent_linear import IndependentLinearControl
from research.native.itd02.mg91.test_teacher_values import shaped

class FrozenMG93(unittest.TestCase):
    def test_frozen_9_checkpoint_digest_manifest_and_new_cohorts(self):
        self.assertEqual(len(mg93.CHECKPOINT_SHA),9)
        self.assertEqual(len(mg93.FAMILIAR),3)
        self.assertEqual(sum(len(v) for v in mg93.FAMILIAR.values()),9)
        self.assertEqual(len(mg93.TRANSFER_SEEDS),3)
        self.assertEqual(mg93.TRANSFER_FAMILY,"MiniGrid-DoorKey-6x6-v0")
        self.assertEqual(mg93.TRANSFER_SOURCE,"MiniGrid-KeyCorridorS3R2-v0")
        self.assertEqual(len(set(x for v in mg93.FAMILIAR.values()
                                 for x in v)|set(mg93.TRANSFER_SEEDS)),12)
        self.assertTrue(all(len(v)==64 and all(c in "0123456789abcdef" for c in v)
                            for v in mg93.CHECKPOINT_SHA.values()))

    def test_models_trained_on_equal_positive_original_public_fixture(self):
        demo=shaped()
        models=[PublicFeedbackGate(),PublicRewardPrototypes(),
                IndependentLinearControl()]
        for m in models:
            m.fit(demo)
        self.assertEqual(len({m.data_sha for m in models}),1)
        for m in models:
            raw=m.checkpoint()
            self.assertEqual(type(m).restore(raw).checkpoint(),raw)
            with self.assertRaises(ValueError):
                type(m).restore(raw+b"unexpected")

    def test_separate_codepaths_preserve_reference_models(self):
        self.assertIsNot(PublicFeedbackGate,PublicRewardPrototypes)
        self.assertIsNot(IndependentLinearControl,PublicRewardPrototypes)
        self.assertEqual([role for role,_ in mg93.NATIVE],
                         list(mg93.frozen.ROLES[:3]))
        self.assertEqual(mg93.frozen.CAP,384)
        self.assertEqual(mg93.UPSTREAM,mg93.frozen.UPSTREAM)
        self.assertEqual(len(mg93.SOURCE),5)

if __name__=="__main__":
    unittest.main()
