"""CS19 source-free prospectively frozen role, feature, oracle, fit checks."""
from __future__ import annotations
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs19_original_popgym_rank_history import (
   ARMS,DECK_SIZES,K,FIT_PER_REP,DEV_PER_REP,source_seed,
   rank_bit_features,TrainedRank,TrainedLogistic,SourceKnownFull,SourceKnownPrior
)
class SourceFree(unittest.TestCase):
 def test_exact_source_roles(self):
    seeds=[source_seed(role,di,rep,i) for role,n in
      (("FIT",FIT_PER_REP),("DEV",DEV_PER_REP))
      for di in range(2) for rep in range(2) for i in range(n)]
    self.assertEqual(len(seeds),len(set(seeds)))
    self.assertEqual(len(seeds),640)
 def test_frozen_policies_and_bounded_counters(self):
    self.assertEqual(K,3)
    self.assertEqual(DECK_SIZES,(1,3))
    self.assertEqual(len(ARMS),5)
    seen=[0]*13;seen[5]=1
    self.assertEqual(len(rank_bit_features(5,seen,1,0,None)),17)
    self.assertEqual(len(rank_bit_features(5,seen,1,0,K)),17)
 def test_genuine_history_changes_public_source_known_action(self):
    full=SourceKnownFull();prior=SourceKnownPrior()
    seen=[0]*13;seen[6]=1
    self.assertEqual(full.choose(6,seen,1,0),prior.choose(6,seen,1,0))
    for rank in (7,8,9,10,11,12):
        seen[rank]=4
    # Exhaustion of all high ranks changes source future probabilities.
    self.assertNotEqual(full.choose(6,seen,1,25),prior.choose(6,seen,1,25))
 def test_frozen_learned_competitor_masks(self):
    m=TrainedRank()
    fake={"public_current_rank":4,"original_binary_next_higher":True}
    m.learn(fake)
    self.assertEqual(m.fit_rows,1)
    self.assertEqual(m.choose(4,[0]*13,1,0),0)
    z=TrainedLogistic(K)
    self.assertEqual(len(z.weights),17)
if __name__=="__main__":unittest.main()
