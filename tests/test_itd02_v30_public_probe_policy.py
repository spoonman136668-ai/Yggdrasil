"""V30 external public-count action selection provenance/falsification tests."""
import unittest
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS
from yggdrasil.itd02_v30_public_probe_policy_dev import PublicProbePolicyDev


class PublicProbePolicyTests(unittest.TestCase):
    def test_novelty_prefers_unselected_public_action(self):
        p=PublicProbePolicyDev("novelty")
        p.observe_selected("LRV", "Backup", ACTIONS[0])
        chosen=p.select("LRV","Backup",[100.0,0.0,2.0])
        self.assertEqual(chosen,ACTIONS[2])
        self.assertEqual(p.events,1)
        p.observe_selected("LRV","Backup",chosen)
        self.assertEqual(p.select("LRV","Backup",[5.0,4.0,10.0]),ACTIONS[1])

    def test_greedy_round_robin_and_random_independent(self):
        for mode in ("greedy","round_robin","random"):
            p=PublicProbePolicyDev(mode)
            p.observe_selected("MRV","GoForward",ACTIONS[0])
            if mode=="greedy":
                self.assertEqual(p.select("MRV","GoForward",[-1,0,4]),ACTIONS[2])
            elif mode=="round_robin":
                self.assertEqual(p.select("MRV","GoForward",[100,4,2]),ACTIONS[1])
            else:
                self.assertIn(p.select("MRV","GoForward",[0,0,0]),ACTIONS)
        a=PublicProbePolicyDev("random")
        b=PublicProbePolicyDev("random")
        seq_a=[a.select("LRV","Backup",[0,0,0]) for _ in range(8)]
        seq_b=[b.select("LRV","Backup",[0,0,0]) for _ in range(8)]
        self.assertEqual(seq_a,seq_b)

    def test_reject_invalid_and_hidden_information(self):
        p=PublicProbePolicyDev()
        with self.assertRaises(ValueError):
            p.select("secret_stage","Backup",[1,2,3])
        with self.assertRaises(TypeError):
            p.select("LRV","Backup",[1,2,3],world="B")
        with self.assertRaises(ValueError):
            p.select("LRV","Backup",[0,float("nan"),1])
        with self.assertRaises(ValueError):
            p.observe_selected("LRV","Backup","private_unselected_reward")
        with self.assertRaises(ValueError):
            PublicProbePolicyDev("random",seed=42)


if __name__=="__main__":
    unittest.main()
