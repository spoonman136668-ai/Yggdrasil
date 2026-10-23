"""CS11 focused pure model calculations; NO original source episodes."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs11_original_new_map_transfer import (
    WarmSourcePrior,fit_target_models,original_episode_seed,SOURCE_FIT_N,
    TARGET_FIT_N,TARGET_BUDGETS,SOURCE_MAP_KEYS,TARGET_MAP_KEYS,ARMS
)
def data(n,map_shift=0):
    samples=[]
    for e in range(n):
        signs=[1 if (e>>i)&1 else -1 for i in range(5)]
        rewards=[0]*20
        for i in range(5):rewards[(i*4+map_shift)%20]=signs[i]
        samples.append({"checks":signs,"reward10":rewards})
    return samples
class Focused(unittest.TestCase):
    def test_exact_source_prior_fixed_units(self):
        source=[data(24,0),data(24,1)]
        target=data(4,2)
        m=WarmSourcePrior(*source)
        self.assertEqual(m.target_updates,0)
        self.assertEqual(len(m.prior),5)
        self.assertEqual(len(m.prior[0]),20)
        m.fit(target)
        self.assertEqual(m.target_updates,4)
        self.assertEqual(len(m.mapping()),5)
    def test_equally_fitted_conventional_control_identity(self):
        source=[data(24,0),data(24,1)]
        target=data(12,2)
        for n in TARGET_BUDGETS:
            models,metrics=fit_target_models(source,target[:n])
            self.assertEqual(models[ARMS[1]].mapping(),models[ARMS[2]].mapping())
            self.assertEqual(models[ARMS[1]].mapping(),models[ARMS[3]].mapping())
            self.assertEqual(metrics[ARMS[0]]["target_fit_updates"],n)
            self.assertEqual(metrics[ARMS[3]]["target_fit_updates"],n)
            self.assertEqual(metrics[ARMS[4]]["target_fit_updates"],0)
    def test_original_seed_roles_and_map_keys_disjoint(self):
        ids={original_episode_seed(group,m,i) for group,count,maps
             in (("source_fit",24,2),("target_fit",12,3),("target_dev",48,3))
             for m in range(maps) for i in range(count)}
        self.assertEqual(len(ids),48+36+144)
        self.assertEqual(len(set(SOURCE_MAP_KEYS+TARGET_MAP_KEYS)),5)
        self.assertNotIn(1900000,ids)
        self.assertEqual(len(ARMS),7)
if __name__=="__main__":
    unittest.main()
