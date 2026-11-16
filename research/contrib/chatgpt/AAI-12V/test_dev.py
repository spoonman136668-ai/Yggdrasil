"""AAI-12V pre-screen structural, action-budget, information-boundary tests."""
import json
import subprocess
import sys
import unittest
import dev
import learner
import world

class DevelopmentTests(unittest.TestCase):
    def test_world_inventory(self):
        self.assertEqual((len(world.GROUPS),len(world.FIXTURES)),(20,2))
        self.assertEqual([sum(g[0]==category for g in world.GROUPS) for category in ('reuse','changed','novel','familiar')],[8,4,4,4])
    def test_source_disarmed(self):
        with self.assertRaises(PermissionError):world.train_rows('scientific:unseen',0,'donor')
        with self.assertRaises(PermissionError):world.train_rows(world.FIXTURES[0],100,'donor')
    def test_actual_intervention_and_port_codes(self):
        for fix in world.FIXTURES:
            for gi in range(len(world.GROUPS)):
                for phase,n in (('donor',16),('interference',16),('receiver',4)):
                    rows=world.train_rows(fix,gi,phase)
                    self.assertEqual(len(rows),n)
                    codes=learner.public_events(rows,n//2)
                    self.assertEqual(len(codes),n//2)
                    self.assertTrue(all(set(r)==learner.FIELDS for r in rows))
    def test_heldout_nuisance_context_disjoint(self):
        for fix in world.FIXTURES:
            for gi in range(len(world.GROUPS)):
                held=world.heldout(fix,gi)
                self.assertEqual(len(held),128)
                all_exposure=set(tuple(r['x']) for r in world.train_rows(fix,gi,'receiver'))
                for code in range(8):
                    all_exposure.update(tuple(r['x']) for r in world.make_pair(fix,gi,'receiver',code))
                self.assertFalse(all_exposure & {x for x,y in held})
    def test_equal_initial_state(self):
        fix=world.FIXTURES[0];gi=2
        d=world.train_rows(fix,gi,'donor')
        i=world.train_rows(fix,gi,'interference')
        r=world.train_rows(fix,gi,'receiver')
        self.assertEqual(len(set(learner.fit(d,i,r,arm,b'seed')[0] for arm in learner.ARMS)),1)
        self.assertEqual(len(set(tuple(sorted(learner.fit(d,i,r,arm,b'seed')[1].items())) for arm in learner.ARMS)),1)
    def test_one_probe_per_arm_and_action_is_real(self):
        fix=world.FIXTURES[0];gi=4
        d=world.train_rows(fix,gi,'donor');i=world.train_rows(fix,gi,'interference')
        r=world.train_rows(fix,gi,'receiver')
        for arm in learner.ARMS:
            masks,obs,chosen=learner.fit(d,i,r,arm,b'seed')
            probe=world.make_pair(fix,gi,'receiver',chosen)
            self.assertEqual(learner.public_events(probe,1)[chosen],world.GROUPS[gi][3]>>chosen&1)
            self.assertEqual(len(probe),2)
            self.assertEqual(chosen in obs,arm=='sham_probe')
    def test_predictive_policy_baseline_true_entropy(self):
        masks=(232,150);obs={0:0,1:1}
        for arm in learner.ARMS:
            selected=learner.choose(arm,masks,obs,b'seed')
            self.assertIn(selected,range(8))
            if arm!='sham_probe':self.assertNotIn(selected,obs)
    def test_posterior_normalized(self):
        probs=learner.posterior((232,150),{0:0,1:1})
        self.assertAlmostEqual(sum(probs),1)
        self.assertTrue(all(0<p<1 for p in probs))
    def test_cold_restore_and_tamper_denial(self):
        m=(232,150);seen={0:1,1:0,2:0};p=(1,3,6,0)
        for arm in learner.ARMS:
            observations=seen if arm!='sham_probe' else {0:1,1:0}
            snap=learner.cold(m,observations,p,arm)
            self.assertEqual(learner.restore(snap),(m,observations,p))
            data=json.loads(snap);data['masks'][0]^=1
            with self.assertRaises(ValueError):learner.restore(json.dumps(data,sort_keys=True,separators=(',',':')))
    def test_no_hidden_world_import_in_learner(self):
        with open(learner.__file__,encoding='utf8') as f:code=f.read()
        self.assertNotIn('import world',code)
        self.assertNotIn('from world',code)
    def test_science_first_use_command_denied(self):
        p=subprocess.run([sys.executable,dev.__file__,'--primary'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('SCIENTIFIC FIRST USE DISARMED',p.stderr)

if __name__=='__main__':unittest.main()
