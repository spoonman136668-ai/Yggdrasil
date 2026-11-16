"""AAI-12W mechanical source, causal action, isolation and control preflight tests."""
import hashlib
import json
import subprocess
import sys
import unittest
import dev
import learner
import world

class ProtocolChecks(unittest.TestCase):
    def test_fixed_world_budget(self):
        self.assertEqual((len(world.NOVEL),len(world.FAMILIAR),len(world.NEGATIVE),len(world.FIXTURES)),(12,4,4,2))
    def test_no_unregistered_science_first_use(self):
        with self.assertRaises(PermissionError):world.train('scientific:primary','novel',0)
        with self.assertRaises(PermissionError):world.train(world.FIXTURES[0],'hidden',0)
        with self.assertRaises(PermissionError):world.train(world.FIXTURES[0],'novel',100)
    def test_true_single_input_intervention(self):
        for f in world.FIXTURES:
            for phase in world.WORLDS:
                for i in range(len(world.WORLDS[phase])):
                    for row in world.train(f,phase,i):
                        x,xx=learner.check(row)
                        self.assertEqual(sum(a!=b for a,b in zip(x,xx)),1)
                        self.assertEqual(world.true_step(f,phase,i,x,row['y'],row['flipped_index']),(xx,row['ynext']))
    def test_heldout_no_predecessor_overlap(self):
        for f in world.FIXTURES:
            for phase in world.WORLDS:
                for i in range(len(world.WORLDS[phase])):
                    starts={tuple(r['x']) for r in world.train(f,phase,i)}
                    trials=world.evaluations(f,phase,i)
                    self.assertEqual(len(trials),64)
                    for trial in trials:
                        self.assertEqual(len(trial['actions']),3)
                        self.assertFalse(any(tuple(x) in starts for x in trial['predecessor_path']))
    def test_no_private_fields_to_learner(self):
        r=world.train(world.FIXTURES[0],'novel',0)[0]
        with self.assertRaises(ValueError):learner.check({**r,'hidden_state':0})
        with open(learner.__file__,encoding='utf8') as f:s=f.read()
        self.assertNotIn('import world',s)
        self.assertNotIn('from world',s)
    def test_all_fully_fitted_arms(self):
        rows=world.train(world.FIXTURES[0],'novel',0)
        for name in learner.METHODS:
            model=learner.train(name,rows)
            snapshot=learner.checkpoint(model)
            restored=learner.restore(snapshot)
            self.assertEqual(learner.checkpoint(restored),snapshot)
            self.assertIn(learner.forecast(restored,[0]*8,0,[0,1,2]),(0,1))
    def test_tampered_cold_rejected(self):
        rows=world.train(world.FIXTURES[0],'novel',0)
        for name in learner.METHODS:
            state=learner.train(name,rows)
            j=json.loads(learner.checkpoint(state))
            j['state']['training_sha256']='0'*64
            with self.assertRaises(ValueError):learner.restore(learner.canonical(j))
    def test_deterministic_roles_and_source(self):
        self.assertEqual(world.roles(world.FIXTURES[0],'novel',0),world.roles(world.FIXTURES[0],'novel',0))
        self.assertEqual(world.train(world.FIXTURES[0],'novel',0),world.train(world.FIXTURES[0],'novel',0))
    def test_candidate_bound(self):
        rows=world.train(world.FIXTURES[0],'novel',0)
        model=learner.train('ternary_causal',rows)['model']
        self.assertEqual(len(model['abc']),3)
        self.assertNotIn(model['k'],model['abc'])
        self.assertLess(model['mask'],256)
    def test_primary_disarmed(self):
        p=subprocess.run([sys.executable,dev.__file__,'--primary'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('SCIENTIFIC FIRST USE DISARMED',p.stderr)

if __name__=='__main__':unittest.main()
