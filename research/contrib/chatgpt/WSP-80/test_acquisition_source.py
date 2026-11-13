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

    def test_developer_only_end_to_end_paid_384_no_reset(self):
        import structural_weights
        world=source.World(9001,'quartic_positive',tuple(range(6)),tuple(range(6)))
        session=world.training_session()
        policy=acquisition.InterventionPolicy()
        editor=structural_weights.PaidStructuralWeightEditor()
        for i in range(384):
            action=(acquisition.stage_a_action(9001,i) if i<144 else
                    policy.choose(session.current))
            exp=session.step(action)
            policy.observe(exp)
            editor.charge(exp.before,exp.action,exp.after,exp.action_cost)
            if i in (143,383):
                diag=editor.compile()
                restored=structural_weights.PaidStructuralWeightEditor.restore(editor.snapshot())
                self.assertEqual(restored.charges,i+1)
                self.assertLessEqual(diag['learned_numerical_relu_features'],342)
        self.assertEqual(len(session.ledger),384)
        self.assertEqual(policy.turn,384)

    def test_registered_source_reachability_preflight_only(self):
        # Evaluator-private generator validation; not a learner training query.
        for seed in source.SEEDS:
            world=source.build_world(seed)
            seen={(0,)*6}
            pending=[(0,)*6]
            for state in pending:
                for action in source.ACTIONS:
                    after=world._step_oracle(state,action)
                    if after not in seen:
                        seen.add(after)
                        pending.append(after)
            self.assertEqual(len(seen),64,seed)

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
