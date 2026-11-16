"""AAI-12U post-screen mechanical verification; not original preregistration evidence."""
import json
import subprocess
import sys
import unittest
import learners
import source_world as source
import dev

class AAI12U(unittest.TestCase):
    def test_fixed_inventory(self):
        self.assertEqual(len(source.GROUPS),8)
        self.assertEqual((len(source.FIXTURES),len(source.PORTS)),(2,3))

    def test_genuine_do_and_public_only(self):
        for fix in source.FIXTURES:
            for idx in range(8):
                for phase,expected in [('donor',16),('interference',16),('recipient',4)]:
                    rows=source.source_rows(fix,idx,phase)
                    self.assertEqual(len(rows),expected)
                    for a,b in zip(rows[::2],rows[1::2]):
                        self.assertEqual(set(a),learners.FIELDS)
                        self.assertEqual(sum(x!=y for x,y in zip(a['x'],b['x'])),1)
                        self.assertNotEqual(a['y'],b['y'])
                        self.assertEqual(learners.code_and_truth(a),learners.code_and_truth(b))

    def test_source_disjoint_holdout(self):
        for fix in source.FIXTURES:
            for idx in range(8):
                seen={tuple(r['x']) for r in source.source_rows(fix,idx,'recipient')}
                remaining=source.withheld(fix,idx)
                self.assertEqual((len(seen),len(remaining)),(4,60))
                self.assertFalse(seen & {x for x,y in remaining})

    def test_learner_module_has_no_hidden_generator_dependency(self):
        with open(learners.__file__,encoding='utf8') as f:code=f.read()
        self.assertNotIn('import source_world',code)
        self.assertNotIn('from source_world',code)

    def test_fixed_capacity_and_true_mask_learning(self):
        for fix in source.FIXTURES:
            for idx,group in enumerate(source.GROUPS):
                for i,phase in enumerate(('donor','interference')):
                    table=learners.slot(source.source_rows(fix,idx,phase))
                    self.assertEqual(table['mask'],group[1+i])
                    self.assertEqual(table['counts'],[2]*8)

    def test_checkpoint_round_trip_and_tamper_denial(self):
        fix=source.FIXTURES[0]
        d=source.source_rows(fix,0,'donor');i=source.source_rows(fix,0,'interference');r=source.source_rows(fix,0,'recipient')
        for arm in learners.ARMS:
            m=learners.Memory(arm,d,i,r);snap=m.checkpoint();restored=learners.Memory.restore(snap)
            self.assertEqual(restored.checkpoint(),snap)
            for x,_ in source.withheld(fix,0):
                self.assertEqual(m.prediction(x),restored.prediction(x))
            damaged=json.loads(snap);damaged['payload']['slots'][0]['mask'] ^= 1
            with self.assertRaises(ValueError):learners.Memory.restore(json.dumps(damaged,sort_keys=True,separators=(',',':')))

    def test_donor_and_changed_groups_conflict(self):
        for category,donor,_,receiver in source.GROUPS:
            if category=='reuse' or category=='familiar':self.assertEqual(donor,receiver)
            else:self.assertNotEqual(donor,receiver)

    def test_wrong_public_rows_rejected(self):
        f=source.FIXTURES[0];r=list(source.source_rows(f,0,'recipient'))
        with self.assertRaises(ValueError):learners.validate({**r[0],'hidden_mask':232})
        with self.assertRaises(ValueError):learners.Memory('uncertainty_gated',source.source_rows(f,0,'donor'),source.source_rows(f,0,'interference'),r[:2])

    def test_candidate_does_not_see_group_identity(self):
        f=source.FIXTURES[0]
        o=learners.Memory('uncertainty_gated',source.source_rows(f,0,'donor'),source.source_rows(f,0,'interference'),source.source_rows(f,0,'recipient'))
        snap=json.loads(o.checkpoint())['payload']
        self.assertEqual(set(snap),{'schema','arm','slots','receiver','ports','selected'})
        self.assertNotIn('reuse',str(snap));self.assertNotIn('changed',str(snap))

    def test_frozen_source_screen_repeat(self):
        a=dev.score();b=dev.score()
        self.assertEqual(a['scores'],b['scores'])
        self.assertEqual(a['prediction_trace_sha256'],b['prediction_trace_sha256'])
        self.assertEqual(a['classification'],'DEV_NO_GO_NO_SCIENCE')
        self.assertEqual(a['counts']['all_per_arm'],960)

    def test_primary_first_use_disarmed(self):
        p=subprocess.run([sys.executable,dev.__file__,'--primary'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('SCIENTIFIC FIRST USE DISARMED',p.stderr)

if __name__=='__main__':unittest.main()
