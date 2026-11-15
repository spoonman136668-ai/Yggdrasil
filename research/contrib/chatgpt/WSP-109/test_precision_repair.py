"""Pure synthetic binary-label exhaustive precision qualification for WSP109.

All 2^3 arbitrary feedback patterns are tested on fabricated action kinds.
No original FIT or TRANSFER law, labels, oracle, query or historical data are
consulted. This catches the loss-roundoff stall in the aborted original run.
"""
from __future__ import annotations

from itertools import product
import math
from pathlib import Path
import sys
import unittest

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from learners import ConventionalLogistic, NEWTON_TOL, L2, MAX_NEWTON_STEPS


class TestAllEightSyntheticFeedbackPatterns(unittest.TestCase):
    def test_convex_stationarity_on_all_eight_possible_three_bit_labels(self):
        for kinds in ((0,1,2),(0,3,8)):
            for pattern in product((False,True),repeat=3):
                with self.subTest(kinds=kinds,pattern=pattern):
                    m=ConventionalLogistic()
                    observations=list(zip(kinds,pattern))
                    m.fit("fixture",observations)
                    self.assertLessEqual(m.gradients["fixture"],NEWTON_TOL)
                    self.assertLessEqual(m.steps["fixture"],MAX_NEWTON_STEPS)
                    self.assertTrue(np.all(np.isfinite(m.theta["fixture"])))
                    self.assertEqual(m.theta["fixture"].shape,(10,))

    def test_mathematical_objective_preserved_by_higher_precision(self):
        for pattern in product((False,True),repeat=3):
            model=ConventionalLogistic()
            model.fit("fixture",list(zip((0,1,2),pattern)))
            X=np.zeros((3,10),dtype=np.float64)
            X[np.arange(3),np.arange(3)]=1.
            X[:,-1]=1.
            y=np.asarray(pattern,dtype=np.float64)
            theta=model.theta["fixture"]
            decimal_result=model._precise_objective(theta,X,y)
            binary64_result=model._objective(theta,X,y)
            self.assertLess(abs(float(decimal_result)-binary64_result),1e-12)
            self.assertTrue(math.isfinite(binary64_result))

    def test_convex_solver_does_not_silently_relax_frozen_objective(self):
        self.assertEqual(L2,0.03)
        self.assertEqual(NEWTON_TOL,1e-9)
        self.assertEqual(MAX_NEWTON_STEPS,100)
        model=ConventionalLogistic()
        model.fit("fixture",[(0,True),(1,False),(2,True)])
        self.assertLessEqual(model.gradients["fixture"],1e-9)


if __name__=="__main__":
    unittest.main()
