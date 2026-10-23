"""CS04 focused source-free model-fitting and role tests, no source episodes."""
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_cs04_public_minigrid_memory import (
 HistoryTable,LogisticHistory,EpisodicK3,FrameOnlyTable,ErasedHistory,FixedUpper,
 seed,REPS,ROLE_COUNTS,ARMS
)
def synthetic():
    return [{"cue_public_bit":c,"upper_public_bit":u,"fork_branch":a,
             "success":int((a==0)==(c==u)),"original_reward":0.,
             "source_native_steps":17,"seed":x}
            for x,(c,u,a) in enumerate(
                (c,u,a) for _ in range(8) for c in (0,1) for u in (0,1) for a in (0,1))]
class Tests(unittest.TestCase):
 def test_model_fit_without_source_access(self):
    rows=synthetic()
    for model in (HistoryTable(),LogisticHistory(),EpisodicK3(),FrameOnlyTable()):
        model.fit(rows)
        self.assertGreater(model.updates,0)
        for c in (0,1):
            for u in (0,1):
                self.assertIn(model.choose(c,u),(0,1))
 def test_history_learned_from_reward(self):
    m=HistoryTable();m.fit(synthetic())
    self.assertEqual(m.choose(0,0),0)
    self.assertEqual(m.choose(1,1),0)
    self.assertEqual(m.choose(1,0),1)
    self.assertEqual(m.choose(0,1),1)
    self.assertEqual(ErasedHistory(m).choose(0,0),ErasedHistory(m).choose(1,0))
 def test_source_seed_role_disjoint(self):
    ids={seed(t,r,i) for r in REPS for t,n in ROLE_COUNTS.items() for i in range(n)}
    self.assertEqual(len(ids),3*(192+64+128))
    self.assertNotIn(940003,ids)
    self.assertEqual(len(ARMS),6)
 def test_fixed_control(self):
    m=FixedUpper()
    self.assertEqual(m.choose(0,1),0)
if __name__=="__main__":
 unittest.main()
