"""CS10 source-free original-model fitting and role/custody controls."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs10_future_demand_retention import (
    LearnedLogistic,LearnedTabular,PredictionCache,public_features,
    tabular_key,paired_bootstrap,public_seed,REPS,N,ARMS
)
def examples(n=120):
    return [{"source_public_features":[1.,(i%4)/4,
             (i%9)/9,(i%11)/11,float(i%3==0),i/120],
             "future_public_reappearance":int(i%5 in (0,1))}
            for i in range(n)]
class Frozen(unittest.TestCase):
    def test_fit_full_shared_supervision_and_state(self):
        x=examples()
        log=LearnedLogistic();tab=LearnedTabular()
        log.fit(x);tab.fit(x)
        self.assertEqual(log.updates,8*len(x))
        self.assertEqual(tab.updates,len(x))
        self.assertEqual(len(log.weights),6)
        self.assertGreater(len(tab.counts),0)
        for e in x:
            self.assertGreaterEqual(log.predict(e["source_public_features"]),0)
            self.assertLessEqual(tab.predict(e["source_public_features"]),1)
    def test_actual_bound_and_no_source_consumption(self):
        m=PredictionCache(4,"prediction",LearnedLogistic())
        for i in range(10):
            m.decisions=i
            m.remember(i,i%13)
        self.assertEqual(m.total_evictions,6)
        self.assertEqual(m.peak_cache,4)
        self.assertEqual(len(m.cache),4)
    def test_paired_ci_and_split_ids(self):
        self.assertEqual(len(ARMS),7)
        ids={public_seed(role,r,i) for role,n in N.items()
             for r in REPS for i in range(n)}
        self.assertEqual(len(ids),3*(24+16+48))
        self.assertNotIn(1190000,ids)
        fake=lambda delta:{"every_original_scored_seed_outcome":[
            {"source_seed":i,"source_native_original_reward":i*.01+delta}
            for i in range(48)]}
        b=paired_bootstrap(fake(1),fake(0),0,0)
        self.assertGreater(b["paired_95_lower"],.99)
        self.assertEqual(len(b["every_paired_original_source_reward_delta"]),48)
    def test_key_is_source_public_rank_recency_support_only(self):
        f=[1,0.75,0.5,.2,.25,.5]
        self.assertEqual(tabular_key(f),(3,1,1))
if __name__=="__main__":
    unittest.main()
