"""WSP101 wide synthetic DEV learning and custody checks; no original worlds."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from wide_truth import source, heldout, answer
from wide_models import DirectWeightMemory, infer_symbolic, predict_symbolic
from wide_stress import TIERS, execute

class WideDevelopmentTests(unittest.TestCase):
    def test_frozen_largest_first(self):
        self.assertEqual(TIERS,((64,64,12),(32,32,11),(8,8,10)))
        self.assertEqual(64*64*(1<<12),16777216)

    def test_unknown_operator_source_fit_and_unseen_prediction(self):
        m=DirectWeightMemory(4,10)
        for idx in range(4):
            pairs=source(idx,idx+1,10)
            symbolic=infer_symbolic(pairs,10)
            m.write(idx,pairs)
            for x in heldout(idx,idx+1,10,32):
                target=answer(idx,idx+1,10,x)
                self.assertEqual(m.predict(idx,x),target)
                self.assertEqual(predict_symbolic(symbolic,x,10),target)

    def test_cold_restoration_and_later_nonoverlapping_learning(self):
        model=DirectWeightMemory(4,10)
        model.write(0,source(1,1,10))
        image=model.cold_image()
        copy=DirectWeightMemory.restore(4,10,image)
        self.assertEqual(copy.cold_image(),image)
        for i in range(1,4):
            copy.write(i,source(i+1,i,10))
        for x in heldout(1,1,10,64):
            self.assertEqual(copy.predict(0,x),answer(1,1,10,x))
        with self.assertRaises(ValueError):
            copy.write(0,source(1,1,10))

    def test_no_fabricated_memory_oracle(self):
        model=DirectWeightMemory(1,10)
        self.assertIsNone(model.predict(0,13))
        with self.assertRaises(ValueError):
            model.write(0,source(0,0,10)[:3])
        with self.assertRaises(ValueError):
            DirectWeightMemory.restore(1,10,(b"short",b"\x01"))

    def test_little_tier_source_blind_original_free_stress(self):
        result=execute(2,2,10)
        self.assertEqual(result["training_observed_links"],32)
        self.assertEqual(result["unseen_one_hop_queries"],512)
        self.assertFalse(result["original_worlds_used"])
        self.assertFalse(result["scientific_superiority"])
        self.assertEqual(result["methods"]["direct_numeric"]["one_hop_correct"],512)
        self.assertEqual(result["methods"]["independent_symbolic"]["one_hop_correct"],512)
        self.assertEqual(result["methods"]["direct_numeric"]["two_hop_correct"],8192)

if __name__=="__main__":
    unittest.main()
