"""WSP218 strict source-only qualification: never constructs FIT/HELD outcomes."""
import json
from pathlib import Path
from collections import Counter
import unittest

from study import (SEEDS,TRUTH_BY_WORLD,STAGES,ROWS_PER_STAGE,HELD_ROWS,
                   PREREG,SCHEMA,SOURCE_SHA,SWEEPS,RIDGE,FULL_FEATURES,
                   MODES,descriptor,rank_unregularized,feature,held_pairs,
                   Observation,LocalCredit,BatchControl,exact_ridge)


class SourceOnlyWSP218(unittest.TestCase):
    def test_frozen_balanced_lag_and_complete_metadata_rank(self):
        prereg=json.loads((Path(__file__).parent/"prereg.json").read_text("utf-8"))
        self.assertEqual(prereg["experiment_id"],"WSP-218")
        self.assertEqual(PREREG,"a37bced024ff959325f42d5259982dbd2197cb8f")
        self.assertEqual(prereg["source_free_protocol"]["cohort"],
                         [{"seed":s,"active_lag":TRUTH_BY_WORLD[s]} for s in SEEDS])
        self.assertEqual(Counter(TRUTH_BY_WORLD.values()),{0:2,1:2})
        self.assertEqual((STAGES,ROWS_PER_STAGE,HELD_ROWS),(4,50,100))
        self.assertEqual((RIDGE,SWEEPS,FULL_FEATURES),(.01,60,16))
        self.assertEqual(SCHEMA,"wsp218.balanced-contextual-credit.v1")
        self.assertEqual(len(SOURCE_SHA),64)
        self.assertEqual(set(MODES),{"local","full_context","first_only",
                         "last_only","lag_blind","context_omitted","shuffled"})
        self.assertFalse(prereg["execution_authority"]["original_GFP_first_use"])
        self.assertFalse(prereg["execution_authority"]["merge"])
        all_ids=set()
        for seed in SEEDS:
            for stage in range(STAGES):
                desc=descriptor(seed,stage)
                self.assertEqual(len(desc),ROWS_PER_STAGE)
                self.assertEqual(Counter(actions for _,actions,_ in desc),
                                 {(a,b):2 for a in range(5) for b in range(5)})
                self.assertEqual(set(ctx for _,_,ctx in desc),set(range(8)))
                self.assertEqual(rank_unregularized(desc),FULL_FEATURES,
                                 msg=f"rank source-invalid {seed} B{stage}")
                self.assertEqual(len({eid for eid,_,_ in desc}),ROWS_PER_STAGE)
                self.assertFalse({eid for eid,_,_ in desc}&all_ids)
                all_ids.update(eid for eid,_,_ in desc)
            with self.assertRaises(ValueError):
                held_pairs(seed)
        for old in (21011,21101,21201,21301,21401,21411,
                    21503,21601,21701,21899):
            with self.assertRaises(ValueError): descriptor(old,0)
            with self.assertRaises(ValueError): held_pairs(old,finished=True)

    def test_unmarked_input_and_bound_cold_checkpoints(self):
        self.assertEqual(tuple(Observation.__dataclass_fields__),
                         ("event_id","actions","context","outcome"))
        self.assertEqual(sum(feature((2,3),4)),3)
        self.assertEqual(feature((2,3),4)[4],1.0)
        self.assertEqual(feature((2,3),4)[9],1.0)
        self.assertEqual(feature((2,3),4)[14],1.0)
        self.assertEqual(sum(feature((2,3),12)),2)
        self.assertEqual(len(feature((2,3),4,"lag_blind")),12)
        self.assertEqual(len(feature((2,3),4,"context_omitted")),9)
        for bad in ((-1,2),(1,5),(1,2,3)):
            with self.assertRaises(ValueError): feature(bad,3)
        with self.assertRaises(ValueError): feature((1,2),16)
        with self.assertRaises(ValueError): feature((1,2),3,"oracle")
        m=LocalCredit(SEEDS[0])
        ck=m.checkpoint()
        self.assertEqual(LocalCredit.restore(ck,SEEDS[0]).checkpoint(),ck)
        with self.assertRaises(ValueError): LocalCredit.restore(ck,SEEDS[1])
        with self.assertRaises(ValueError): LocalCredit.restore(ck[:-1]+b" ",SEEDS[0])
        with self.assertRaises(ValueError): BatchControl.restore(ck,SEEDS[0],"full_context")
        with self.assertRaises(ValueError): m.advance(0,[])
        with self.assertRaises(ValueError): m.advance(1,[])
        for mode in MODES:
            if mode=="local":continue
            b=BatchControl(SEEDS[0],mode)
            snapshot=b.checkpoint()
            self.assertEqual(BatchControl.restore(snapshot,SEEDS[0],mode).checkpoint(),snapshot)
            with self.assertRaises(ValueError): BatchControl.restore(snapshot,SEEDS[1],mode)
            with self.assertRaises(ValueError): BatchControl.restore(snapshot,SEEDS[0],"local")
            with self.assertRaises(ValueError): BatchControl.restore(snapshot[:-1]+b" ",SEEDS[0],mode)

    def test_negative_parity_and_exact_math_on_noncohort_fixture(self):
        from verify_parity import numeric,compare_receipts
        numeric("within tolerance",.1,.1000000002)
        for bad in (float("nan"),float("inf"),"no"):
            with self.assertRaises(ValueError): numeric("nonfinite",0,bad)
        with self.assertRaises(ValueError): numeric("material",.1,.3)
        with self.assertRaises(ValueError): compare_receipts(
            {"classification":"BALANCED_CREDIT_SUPPORTED"},
            {"classification":"BALANCED_CREDIT_SUPPORTED"})
        # Generic deliberately noncohort, non-primary test of exact 2D solve.
        v=exact_ridge([[3.0,0.0],[0.0,4.0]],[[1.0]*3,[2.0]*3])
        self.assertAlmostEqual(v[0][0],1/3.01)
        self.assertAlmostEqual(v[1][0],2/4.01)


if __name__=="__main__":
    unittest.main()
