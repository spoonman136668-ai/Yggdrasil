"""CS12 source-free causal assignment and source-prior tests."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs12_original_portable_causal_rule import (
    ALL_PERMUTATIONS,H_GRID,ARMS,public_inventory,
    infer_assignment,source_seed,OLD_MAP_KEYS,NEW_MAP_KEYS,
    original_law_probability,make_models,SOURCE_N,BUDGETS
)
def records(n,shift=0):
    mapping=[(i*4+shift)%20 for i in range(5)]
    x=[]
    for e in range(n):
        signs=[1 if (e>>i)&1 else -1 for i in range(5)]
        rewards=[0]*20
        for i,p in enumerate(mapping):rewards[p]=signs[i]
        x.append({"checks":signs,"reward10":rewards,"position":(e%5,0)})
    return x
class Focused(unittest.TestCase):
    def test_exact_120_permutations_and_original_source_probability(self):
        self.assertEqual(len(ALL_PERMUTATIONS),120)
        self.assertEqual(len(set(ALL_PERMUTATIONS)),120)
        self.assertAlmostEqual(original_law_probability((2,2),(2,2),1,20.),1.)
        self.assertAlmostEqual(original_law_probability((2,2),(2,2),0,20.),0.)
    def test_sensor_assignment_cannot_use_hidden_indices(self):
        data=records(8)
        inferred,state=infer_assignment(data,20.)
        self.assertEqual(len(inferred),5)
        self.assertEqual(len(set(inferred)),5)
        self.assertEqual(state["candidate_permutations_evaluated"],120)
        self.assertEqual(len(public_inventory(data)),5)
    def test_target_controls_are_equal_fit(self):
        source=[records(SOURCE_N,0),records(SOURCE_N,1)]
        target=records(4,2)
        m=make_models(source,target,20.,{})
        self.assertEqual(m[ARMS[2]].mapping(),m[ARMS[3]].mapping())
        self.assertEqual(len(m[ARMS[0]].mapping()),5)
        self.assertEqual(len(set(m[ARMS[0]].mapping())),5)
        self.assertEqual(m[ARMS[6]].mapping(),())
    def test_roles_disjoint_and_frozen(self):
        values={source_seed("source",m,i) for m in range(2) for i in range(24)}
        values|={source_seed("target",m,i) for m in range(3) for i in range(4)}
        values|={source_seed("dev",m,i) for m in range(3) for i in range(48)}
        self.assertEqual(len(values),48+12+144)
        self.assertEqual(len(set(OLD_MAP_KEYS+NEW_MAP_KEYS)),5)
        self.assertEqual(BUDGETS,(1,2,4))
        self.assertEqual(H_GRID,(5.,10.,20.,40.,80.))
if __name__=="__main__":
    unittest.main()
