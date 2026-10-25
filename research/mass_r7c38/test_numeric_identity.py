"""C38 source-free numeric identity contract tests, entirely SYNTHETIC fixtures.

Fixtures are not original MiniGrid returns and never substitute for archived FIT.
"""
import hashlib
import unittest
import numpy as np
from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c36.run import CausalOptions,PAIRS,feature,P as ORIGINAL
from research.mass_r7c38.numeric_identity import P


def invented_fixtures():
    keys={f"{a}{b}":{"completed_two_original_actions":True,
         "actual_selected_source_actions":[{"action":a},{"action":b}],
         "real_two_step_goal_distance_improvement":(2 if a==2 else a)-b
        } for a in range(3) for b in range(3)}
    return [
      {"family":"MiniGrid-FourRooms-v0",
       "public_initial":{"x":3+i,"y":5,"goal_x":8,"goal_y":10,
          "direction":i%4,"front_blocked":bool(i%2)},
       "all_nine_original_physical_pairs":keys} for i in range(4)
    ]


def motors():
    return {str(d):{f"{dx},{dy}":10} for d,(dx,dy) in
        enumerate(((1,0),(0,1),(-1,0),(0,-1)))}


class OriginalNumericCustodySourceFree(unittest.TestCase):
    def test_existing_prior_C37_provenance_not_rewritten(self):
        self.assertNotEqual(P["original_C37_A_model_sha"],P["original_C37_B_model_sha"])
        self.assertEqual(P["original_C35_artifact_id"],12603145885)
        self.assertEqual(P["original_C37_A_run"],40207853631)
        self.assertEqual(P["original_C37_B_run"],40208146358)

    def test_frozen_model_constructor_and_sha_are_deterministic_on_public_fixtures(self):
        fit=invented_fixtures()
        a=CausalOptions(fit,motors())
        b=CausalOptions(fit,motors())
        self.assertEqual(a.model_sha,b.model_sha)
        self.assertEqual(canonical(a.snapshot()),canonical(b.snapshot()))
        self.assertEqual(a.fitted,len(fit)*len(PAIRS))

    def test_normal_equations_are_actual_original_numpy_math(self):
        fit=invented_fixtures()
        x=np.asarray([feature(r,p) for r in fit for p in PAIRS],dtype=np.float64)
        y=np.asarray([r["all_nine_original_physical_pairs"][f"{p[0]}{p[1]}"]["real_two_step_goal_distance_improvement"]
                    for r in fit for p in PAIRS],dtype=np.float64)
        a=x.T@x
        reg=np.eye(x.shape[1])*ORIGINAL["mechanism"]["frozenRidgePenalty"]
        reg[0,0]=0.
        rhs=x.T@y
        model=CausalOptions(fit,motors())
        self.assertLess(float(np.max(np.abs((a+reg)@np.array(model.ridge)-rhs))),1e-6)

    def test_invalid_source_original_pair_cannot_train_as_counterfactual(self):
        fit=invented_fixtures()
        fit[0]["all_nine_original_physical_pairs"]["02"]["completed_two_original_actions"]=False
        with self.assertRaisesRegex(ValueError,"IMPUTED"):
            CausalOptions(fit,motors())

    def test_tampering_original_selected_source_actions_rejected(self):
        fit=invented_fixtures()
        fit[0]["all_nine_original_physical_pairs"]["12"]["actual_selected_source_actions"][0]["action"]=0
        with self.assertRaisesRegex(ValueError,"IMPUTED"):
            CausalOptions(fit,motors())


if __name__=="__main__":
    unittest.main()
