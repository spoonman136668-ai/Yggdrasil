"""Developer-only fixture checks; no registered WSP80 source outcomes."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import unittest
import source,acquisition

class PrivateSourceAndActionPolicyTests(unittest.TestCase):
    def test_dev_world_session_and_no_reset(self):
        world=source.World(9001,'quartic_positive',tuple(range(6)),tuple(range(6)))
        session=world.training_session()
        policy=acquisition.InterventionPolicy()
        for i in range(20):
            a=policy.choose(session.current)
            exp=session.step(a)
            policy.observe(exp)
            self.assertEqual(exp.action_cost,1)
            self.assertEqual(exp.before,session.ledger[-1].before)
        self.assertEqual(len(session.ledger),20)
        self.assertEqual(policy.turn,20)

    def test_registered_access_disallows_non_selftest(self):
        with self.assertRaises(PermissionError):
            source.build_world(5609,'PRIMARY')
        with self.assertRaises(PermissionError):
            source.build_world(9001,'SELFTEST')
        self.assertEqual(acquisition.stage_a_action(9001,0),
                         acquisition.stage_a_action(9001,0))
        self.assertNotEqual(acquisition.stage_a_action(9001,0),6)

if __name__=='__main__':
    unittest.main()
