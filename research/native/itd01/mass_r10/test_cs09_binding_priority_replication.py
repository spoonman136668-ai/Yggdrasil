"""CS09 focused source-free tests, no original POPGym source sampling."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs09_binding_priority_replication import (
   LearnedWeightedEviction, RecordedEviction, WEIGHTS, role_seed,
   percentile_bootstrap, N, REPS
)
class Tests(unittest.TestCase):
 def test_weight_menu_and_unique_source_roles(self):
    self.assertEqual(len(WEIGHTS),12)
    self.assertEqual(len(set(WEIGHTS)),12)
    ids={role_seed(role,r,i) for r in REPS
         for role,n in N.items() for i in range(n)}
    self.assertEqual(len(ids),3*(12+8+40))
    self.assertNotIn(1170000,ids)
 def test_real_binding_audit_and_aux_state(self):
    for policy in (RecordedEviction(4,"fifo"),
                   LearnedWeightedEviction(WEIGHTS[1])):
        for t in range(9):
            policy.decisions=t
            policy.remember(t,t%13)
        self.assertEqual(policy.total_evictions,5)
        self.assertEqual(len(policy.cache),4)
        self.assertEqual(len(policy.eviction_events),5)
        budget=policy.state_for_budget()
        self.assertEqual(len(budget["all_thirteen_public_rank_frequency_counters"]),13)
        self.assertEqual(len(budget["public_seen_positions_bitmap_as_indices"]),9)
        self.assertIn("association_items",budget)
 def test_weighted_priority_distinguishable(self):
    a=LearnedWeightedEviction((-2.0,0.0,0.0))
    b=LearnedWeightedEviction((1.0,0.0,0.0))
    for p in (a,b):
        for t,(pos,rank) in enumerate(((0,0),(1,1),(2,1),(3,2))):
            p.decisions=t
            p.remember(pos,rank)
    self.assertNotEqual(a._priority(1)[0],b._priority(1)[0])
 def test_pair_bootstrap_full_seeds(self):
    result=percentile_bootstrap([.1]*40,20261023)
    self.assertEqual(result["bootstrap_resamples"],10000)
    self.assertAlmostEqual(result["confidence_interval_95_percentile"][0],.1)
    self.assertAlmostEqual(result["confidence_interval_95_percentile"][1],.1)
if __name__=="__main__":unittest.main()
