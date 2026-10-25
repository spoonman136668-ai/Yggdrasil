"""C32 negative/source-only preflight. No original environment run in unit tests."""
import unittest
from research.mass_r7c32.run import P
from research.mass_r7c32.compare import compare

class FrozenPhysicalFITTest(unittest.TestCase):
    def test_frozen_actors_and_unconsumed_worlds(self):
        self.assertEqual(len(P["actors"]),7)
        self.assertEqual(sum(len(x) for x in P["prospectivePublicFIT"]["families"].values()),8)
        self.assertEqual(P["priorFIT"]["authenticatedEvents"],805)
        self.assertFalse(P["governance"]["protectedScientificFirstUse"])
        self.assertFalse(P["governance"]["scientificAccepted"])
        self.assertTrue(P["prospectivePublicFIT"]["allArmsOwnIdenticallySeededOriginalWorld"])
        self.assertEqual(P["prospectivePublicFIT"]["actionSet"],[0,1,2])
    def test_source_only_comparison_fails_on_missing_actual_episodes(self):
        a={"schema":P["schema"],"gate":"ITD02-C32",
           "source_DEV_or_protected_episodes":0,"scientific_first_use":False,
           "scientific_accepted":False,"all_actor_actions_physically_executed":True,
           "prior_original_native_R3_modified":False,
           "original_world_episode_records":[],"verdict":P["acceptance"]["noGo"]}
        with self.assertRaisesRegex(ValueError,"MISSING_REAL_SOURCE_EPISODE"):
            compare(a,a)
    def test_comparison_does_not_synthesize_second_execution(self):
        a={"schema":P["schema"],"gate":"ITD02-C32","resources":{"cpu":3},
           "source_DEV_or_protected_episodes":0,"scientific_first_use":False,
           "scientific_accepted":False,"all_actor_actions_physically_executed":True,
           "prior_original_native_R3_modified":False,
           "original_world_episode_records":[],"verdict":P["acceptance"]["noGo"]}
        b={**a,"verdict":P["acceptance"]["positive"]}
        with self.assertRaisesRegex(ValueError,"DIVERGED"):
            compare(a,b)

if __name__=="__main__":unittest.main()
