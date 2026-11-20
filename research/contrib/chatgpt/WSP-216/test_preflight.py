"""WSP216 guarded metadata-only preflight. Does not generate any new FIT or HELD target."""
import json
from pathlib import Path
import unittest

from study import (WORLDS, STAGE_COUNT, FIT_PER_STAGE, HELD_COUNT, POLICIES,
                   SOURCE_DIGEST, PREREG, LocalMemory, _cell, held, Episode)


class SourceOnlyPreflight(unittest.TestCase):
    def test_frozen_prereg_and_disjoint_scoped_data(self):
        p=json.loads((Path(__file__).parent/"prereg.json").read_text("utf-8"))
        self.assertEqual(p["experiment_id"],"WSP-216")
        self.assertEqual(p["freeze"]["worlds"],list(WORLDS))
        self.assertEqual(PREREG,"3df95400fb43875c4e1856a9f0e1cbbadf44b54c")
        self.assertEqual((STAGE_COUNT,FIT_PER_STAGE,HELD_COUNT),(4,32,64))
        self.assertFalse(p["authority"]["original_gfp_first_use"])
        self.assertFalse(p["authority"]["merge"])
        self.assertFalse(p["authority"]["owner_learner_mutation"])
        self.assertEqual(set(POLICIES),{"credit","full_mle","last_action","no_lag","swap_lag"})
        for seed in WORLDS:
            with self.assertRaises(ValueError):
                held(seed)
        for seed in (21011, 21101, 21201, 21301, 21401, 21411, 21503, 21699):
            with self.assertRaises(ValueError):
                LocalMemory(seed)
            with self.assertRaises(ValueError):
                held(seed,all_stages_finished=True)

    def test_policy_bound_checkpoint_and_negative_inputs(self):
        for policy in POLICIES:
            model=LocalMemory(21601,policy)
            checkpoint=model.checkpoint()
            self.assertEqual(LocalMemory.restore(checkpoint,21601,policy).checkpoint(),checkpoint)
            with self.assertRaises(ValueError):
                LocalMemory.restore(checkpoint,21602,policy)
            other=next(x for x in POLICIES if x!=policy)
            with self.assertRaises(ValueError):
                LocalMemory.restore(checkpoint,21601,other)
            with self.assertRaises(ValueError):
                LocalMemory.restore(checkpoint[:-1]+b" ",21601,policy)
            with self.assertRaises(ValueError):
                model.advance(1,())
            with self.assertRaises(ValueError):
                model.advance(0,())
        self.assertEqual(len(SOURCE_DIGEST),64)

    def test_credit_addressing_without_any_216xx_outcome(self):
        # Only a fabricated static descriptor; never computes any synthetic
        # target or FIT/HELD contrast from the frozen world generators.
        row=Episode("NEGATIVE_ONLY",0,0,3,0,4,3,4,
                    (0.0,)*3,(0.0,)*3)
        self.assertEqual(_cell("credit",row),"0:3")
        self.assertEqual(_cell("swap_lag",row),"1:3")
        self.assertEqual(_cell("no_lag",row),"3")
        self.assertEqual(_cell("last_action",row),"4")
        with self.assertRaises(ValueError):
            _cell("unknown",row)


if __name__=="__main__":
    unittest.main()
