"""CS20 source-free cohort, frozen model math and genuine evidence role checks."""
from __future__ import annotations
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs20_original_depletion_belief import (
    DECK_SIZES,REPS,FIT_N,DEV_N,ARMS,GRID,source_seed,mass,
    LearnedDepletion,FittedSummary,LearnedEpisodic
)
class SourceFree(unittest.TestCase):
    def test_role_seed_uniqueness_and_all_eight_frozen_controls(self):
        roles=[source_seed(role,di,rep,i) for role,n in (("FIT",FIT_N),("DEV",DEV_N))
               for di in range(2) for rep in REPS for i in range(n)]
        self.assertEqual(len(roles),len(set(roles)))
        self.assertEqual(len(roles),448)
        self.assertEqual(len(ARMS),8)
        self.assertEqual(GRID,(0.,.25,.5,.75,1.))
    def test_real_depletion_condition_changes_decision(self):
        c=[4.]*13;seen=[0]*13;rank=6;seen[6]=1
        self.assertEqual(LearnedDepletion(c,0.).choose(rank,seen,1,0),0)
        for j in range(7,13):seen[j]=4
        self.assertEqual(sum(seen),25)
        self.assertEqual(LearnedDepletion(c,1.).choose(rank,seen,1,24),1)
        self.assertEqual(LearnedDepletion(c,0.).choose(rank,seen,1,24),0)
    def test_summary_feature_shape_and_memory_constraint(self):
        seen=[0]*13;seen[6]=1
        self.assertEqual(len(FittedSummary.features(6,seen,1,0)),17)
        self.assertEqual(len(LearnedDepletion([4.]*13,1.,3).state()[
            "empirically_FIT_observed_public_rank_baseline"]),13)
        self.assertEqual(LearnedEpisodic.BINS,(-.30,-.08,.08,.30))
    def test_all_source_free_models_do_not_access_source_private_state(self):
        x=LearnedDepletion([4.]*13,1.)
        self.assertFalse(hasattr(x,"env"))
        self.assertFalse(hasattr(x,"deck"))
        self.assertEqual(x.state()["public_episode_counter_cap"],None)
if __name__=="__main__":
    unittest.main()
