"""No-source-use DTR2/CS2 training guards; synthetic rows are unit tests only."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs02_public_mdp_learning import (
    FittedLogistic,TabularRewards,TabularTD,BlindRewards,MaskedLogistic,
    FixedZero,bit,seed,REPS,ARMS,HORIZON,sha
)
def rows():
    return [(s,a,int(s==a),1-s,int(i%30==29))
            for i,(s,a) in enumerate((i//2%2,i%2) for i in range(120))]
class Focused(unittest.TestCase):
    def test_all_trained_models_change_from_fit(self):
        data=rows()
        for cls in (FittedLogistic,TabularRewards,TabularTD,BlindRewards):
            m=cls();a=sha(m.state());m.fit(data)
            self.assertNotEqual(sha(m.state()),a)
            self.assertIn(m.choose(0),(0,1))
            self.assertIn(m.choose(1),(0,1))
    def test_only_mask_observed_state_not_weights(self):
        f=FittedLogistic();f.fit(rows())
        masked=MaskedLogistic(f)
        self.assertEqual(masked.w,f.w)
        self.assertEqual(masked.choose(0),masked.choose(1))
    def test_exact_public_split_identifiers(self):
        ids={seed(t,r,i) for t,n in (("FIT",256),("VALID",64),("DEV",128))
             for r in REPS for i in range(n)}
        self.assertEqual(len(ids),3*(256+64+128))
        self.assertNotIn(930301,ids)
        self.assertEqual(HORIZON,30)
        self.assertEqual(len(ARMS),6)
    def test_binary_validation(self):
        self.assertEqual(bit(0),0)
        self.assertEqual(bit(True),1)
        with self.assertRaises(RuntimeError):bit(2)
if __name__=="__main__":unittest.main()
