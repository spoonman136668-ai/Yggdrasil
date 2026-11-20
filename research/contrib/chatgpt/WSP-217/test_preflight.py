"""WSP217 source-only negative controls — no FIT or held outcomes generated."""
import json
from pathlib import Path
from collections import Counter
import unittest

from study import (SEEDS,STAGES,ROWS_PER_STAGE,HELD_ROWS,PREREG,SCHEMA,
                   SOURCE_SHA,MODES,feature,fit_descriptor,held_pairs,
                   LocalCredit,BatchRidge,Observation,_solve_exact)


def unregularized_rank(g):
    matrix=[list(map(float,row)) for row in g]
    n=len(matrix)
    pivot_count=0
    for col in range(n):
        pivot=max(range(pivot_count,n),key=lambda k:abs(matrix[k][col]))
        if abs(matrix[pivot][col])<=1e-8:
            continue
        matrix[pivot_count],matrix[pivot]=matrix[pivot],matrix[pivot_count]
        v=matrix[pivot_count][col]
        for j in range(col,n):
            matrix[pivot_count][j]/=v
        for i in range(pivot_count+1,n):
            fac=matrix[i][col]
            for j in range(col,n):
                matrix[i][j]-=fac*matrix[pivot_count][j]
        pivot_count+=1
    return pivot_count


class WSP217SourceOnly(unittest.TestCase):
    def test_freeze_and_full_identifiable_action_grid(self):
        p=json.loads((Path(__file__).parent/"prereg.json").read_text("utf-8"))
        self.assertEqual(p["experiment_id"],"WSP-217")
        self.assertEqual(PREREG,"273f0c4671bb4a27dcbe29f24bb0ab16339361cc")
        self.assertEqual(p["worlds"]["seeds"],list(SEEDS))
        self.assertEqual((STAGES,ROWS_PER_STAGE,HELD_ROWS),(4,50,100))
        self.assertFalse(p["execution"]["bounds"].startswith("ALLOW OWNER"))
        self.assertFalse(p["execution"]["scope"].startswith("local runner"))
        self.assertFalse(p["prereg_integrity"].startswith("tune"))
        self.assertEqual(SCHEMA,"wsp217.unmarked-delayed-credit.v1")
        self.assertEqual(len(SOURCE_SHA),64)
        self.assertEqual(set(MODES),{"local","full_regression","last_action",
                                      "pooled_action","shuffled_consequence"})
        all_ids=set()
        for seed in SEEDS:
            for stage in range(STAGES):
                desc=fit_descriptor(seed,stage)
                self.assertEqual(len(desc),ROWS_PER_STAGE)
                self.assertEqual(Counter(actions for _,actions,_ in desc),
                                 {(a,b):2 for a in range(5) for b in range(5)})
                self.assertTrue(all(0<=context<=7 for _,_,context in desc))
                ids=[event_id for event_id,_,_ in desc]
                self.assertFalse(set(ids)&all_ids)
                all_ids.update(ids)
                gram=[[0.0]*9 for _ in range(9)]
                for _,actions,_ in desc:
                    x=feature(actions)
                    for i in range(9):
                        for j in range(9):
                            gram[i][j]+=x[i]*x[j]
                self.assertEqual(unregularized_rank(gram),9)
            with self.assertRaises(ValueError):
                held_pairs(seed)
        for old in (21011,21101,21201,21301,21401,21411,21503,
                    21601,21602,21603,21604,21799):
            with self.assertRaises(ValueError):
                fit_descriptor(old,0)
        with self.assertRaises(ValueError):
            fit_descriptor(SEEDS[0],4)

    def test_marker_is_absent_and_wrong_custody_fails(self):
        self.assertEqual(tuple(Observation.__dataclass_fields__),
                         ("event_id","context","actions","outcome"))
        with self.assertRaises(ValueError):
            feature((1,2,3))
        with self.assertRaises(ValueError):
            feature((-1,2))
        with self.assertRaises(ValueError):
            feature((1,2),"oracle")
        self.assertEqual(feature((0,2))[:5],(1.0,0.0,0.0,0.0,0.0))
        self.assertEqual(feature((1,2))[1],1.0)
        self.assertEqual(feature((1,2))[6],1.0)
        a=LocalCredit(SEEDS[0])
        checkpoint=a.checkpoint()
        self.assertEqual(LocalCredit.restore(checkpoint,SEEDS[0]).checkpoint(),checkpoint)
        with self.assertRaises(ValueError):
            LocalCredit.restore(checkpoint,SEEDS[1])
        with self.assertRaises(ValueError):
            LocalCredit.restore(checkpoint[:-1]+b" ",SEEDS[0])
        with self.assertRaises(ValueError):
            BatchRidge.restore(checkpoint,SEEDS[0],"full_regression")
        with self.assertRaises(ValueError):
            a.advance(1,())
        with self.assertRaises(ValueError):
            a.advance(0,())
        for mode in MODES:
            if mode=="local":continue
            b=BatchRidge(SEEDS[0],mode)
            blob=b.checkpoint()
            self.assertEqual(BatchRidge.restore(blob,SEEDS[0],mode).checkpoint(),blob)
            with self.assertRaises(ValueError):
                BatchRidge.restore(blob,SEEDS[1],mode)
            with self.assertRaises(ValueError):
                BatchRidge.restore(blob,SEEDS[0],"local")
            with self.assertRaises(ValueError):
                BatchRidge.restore(blob[:-1]+b" ",SEEDS[0],mode)

    def test_numeric_parity_negative(self):
        from verify_parity import numeric,compare_receipts
        numeric("near",0.1,0.1000000001)
        for bad in (float("nan"),float("inf"),"bad"):
            with self.assertRaises(ValueError):
                numeric("nonfinite",0,bad)
        with self.assertRaises(ValueError):
            numeric("drift",0,0.1)
        with self.assertRaises(ValueError):
            compare_receipts({"status":"UNMARKED_CREDIT_SUPPORTED"},
                             {"status":"UNMARKED_CREDIT_SUPPORTED"})


if __name__=="__main__":
    unittest.main()
