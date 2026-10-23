"""Public, source-free finite rational guard tests. No original episodes."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from screen_original_mdp_public import law,decision_certificate,original_equations,STEPS,SEEDS,F

class SourceFreeMechanismMath(unittest.TestCase):
    def test_reward_and_transition_fractions(self):
        r,t=law()
        self.assertEqual(r[0,0],F(41,50))
        self.assertEqual(r[1,1],F(41,50))
        self.assertEqual(r[1,0],F(9,50))
        self.assertEqual(t[0,0],F(41,50))
        self.assertEqual(t[1,1],F(9,50))
    def test_source_truth_function_xor(self):
        self.assertEqual(original_equations(0,0,1,0,1),(1,0))
    def test_context_dependency_and_optimal_values(self):
        d=decision_certificate()
        self.assertEqual(d["unique_optimal_action_by_public_state"],{"0":0,"1":1})
        vals=d["thirty_decision_expected_reward"]
        self.assertEqual(vals["public_state_feedback"]["numerator"],123)
        self.assertEqual(vals["public_state_feedback"]["denominator"],5)
        self.assertEqual(vals["constant_0"]["decimal"],15.)
        self.assertEqual(vals["constant_1"]["decimal"],9.0608)
        self.assertTrue(d["unique_state_feedback_at_all_horizons_1_to_30"])
    def test_budget(self):
        self.assertEqual(STEPS,30)
        self.assertEqual(SEEDS,(930301,930302))
if __name__=="__main__":
    unittest.main()
