"""Source-free deterministic shadow tests. No original MiniGrid environment calls."""
import unittest
from fractions import Fraction
from research.mass_r7c38.deterministic_shadow import shadow_fit,solve,compare_models,sha

class ExactShadowTests(unittest.TestCase):
    def test_known_rational_solution(self):
        x=solve([[Fraction(2),Fraction(1)],[Fraction(1),Fraction(3)]],
                [Fraction(1),Fraction(2)])
        self.assertEqual(x,[Fraction(1,5),Fraction(3,5)])
    def test_frozen_linear_fit_semantics(self):
        r=shadow_fit([[1.,0.],[1.,1.],[1.,2.]],[0.,1.,2.],1.)
        self.assertAlmostEqual(r["shadow_coefficients"][0],1/3)
        self.assertAlmostEqual(r["shadow_coefficients"][1],2/3)
        self.assertEqual(r["fit_rows"],3)
        self.assertEqual(r["real_original_world_steps_in_shadow"],0)
        self.assertFalse(r["scientific_go"])
    def test_ridge_numerical_result_invariant_to_source_fit_row_order(self):
        x=[[1.,i/20.,(i%3)/8.] for i in range(19)]
        y=[float(i%7-3) for i in range(19)]
        a=shadow_fit(x,y,10.)
        b=shadow_fit(list(reversed(x)),list(reversed(y)),10.)
        self.assertEqual(a["shadow_coefficients_sha256"],b["shadow_coefficients_sha256"])
    def test_reject_invalid_unobserved_or_nonnumeric_input(self):
        invalid=[([[1.,float("nan")]],[1.],1.),([[1.,float("inf")]],[1.],1.),
          ([[1.]],[],1.),([[1.]],[1.],0.),([[1.]],[1.],-1.),
          ([[1.,0.],[1.]],[1.,2.],1.),([[1.]],[True],1.)]
        for xx,yy,reg in invalid:
            with self.subTest(xx=xx,yy=yy,reg=reg):
                with self.assertRaises(ValueError):shadow_fit(xx,yy,reg)
    def test_untrained_or_underdetermined_fit_not_promoted(self):
        with self.assertRaises(ValueError):
            shadow_fit([[1.,0.]], [0.],0.)
        with self.assertRaises(ValueError):
            solve([[Fraction(0)]],[Fraction(1)])
    def test_comparison_must_use_complete_original_c36_three_choice_group(self):
        fit=shadow_fit([[1.,0.],[1.,1.]],[0.,1.],1.)
        with self.assertRaises(ValueError):
            compare_models([0.,0.],fit,[[1.,0.]]*8)
    def test_shadow_calculations_do_not_modify_original_native(self):
        fit=shadow_fit([[1.,0.],[1.,1.]],[0.,1.],1.)
        self.assertFalse(fit["original_C36_model_modified"])
        self.assertEqual(fit["real_original_world_steps_in_shadow"],0)
    def test_hash_stable_for_same_numeric_values(self):
        self.assertEqual(sha([0.5,1.25]),sha([0.5,1.25]))
if __name__=="__main__":unittest.main()
