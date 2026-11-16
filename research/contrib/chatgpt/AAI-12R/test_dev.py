import json
import subprocess
import sys
import unittest
import dev

class AAI12RTests(unittest.TestCase):
    def test_fixed_source_cardinality_and_novelty(self):
        self.assertEqual((len(dev.FIT),len(dev.TRANSFER),len(dev.FIXTURES)),(4,12,2))
        self.assertEqual(len(set(dev.TRANSFER)),12)
        self.assertTrue(all(any(mask not in (6,8,14) for mask in w) for w in dev.TRANSFER))
    def test_truth_tables_and_causal_dag(self):
        for mask in range(16):
            for a in (0,1):
                for b in (0,1):
                    x=(a,b,0,0,0,0,0,0)
                    self.assertEqual(dev.ops_forward((mask,8,8,8),x)[0],(mask>>(2*a+b))&1)
    def test_public_filter_and_action(self):
        row=dev.start(dev.FIT[0],(0,)*8,(0,)*4)
        self.assertEqual(set(row),dev.PUBLIC)
        with self.assertRaises(ValueError):dev.Learner(dev.ARMS[0]).observe({**row,'true_ops':(8,)*4})
        with self.assertRaises(ValueError):dev.Learner(dev.ARMS[0]).observe({**row,'reward':99.})
        final=dev.intervene(dev.FIT[0],row,(0,1))
        self.assertEqual(final['actions_taken'],1)
    def test_denies_unnamed_science_fixture(self):
        with self.assertRaises(PermissionError):dev.index('scientific:hidden','eval',0,0,'x',256)
        with self.assertRaises(PermissionError):dev.index('mechanical:alpha','scientific',0,0,'x',256)
    def test_full16_arms_share_inference_before_acting(self):
        rows=[r for j in range(4) for r in dev.example_pair(dev.TRANSFER[0],dev.FIXTURES[0],'challenge',0,j)]
        agents=[dev.Learner(n,rows) for n in (dev.ARMS[0],dev.ARMS[1],dev.ARMS[3])]
        for x in [(0,)*8,(1,)*8,(1,0,1,0,1,0,1,0)]:
            self.assertEqual(agents[0].predict(x),agents[1].predict(x))
            self.assertEqual(agents[0].predict(x),agents[2].predict(x))
    def test_bounded_cold_restore(self):
        agent=dev.Learner(dev.ARMS[-1]);row=dev.start(dev.FIT[0],(0,)*8,(0,)*4)
        for i in range(30):agent.observe(row)
        self.assertEqual(len(agent.rows),16)
        snapshot=agent.checkpoint()
        self.assertEqual(dev.Learner.restore(snapshot).checkpoint(),snapshot)
        tampered=json.loads(snapshot);tampered['rows'].append(row)
        with self.assertRaises(ValueError):dev.Learner.restore(json.dumps(tampered,sort_keys=True,separators=(',',':')))
    def test_actual_actions_capped_two(self):
        actor=dev.Learner(dev.ARMS[-1]);ops=dev.FIT[0]
        row,actions=dev.episode_run(actor,ops,dev.FIXTURES[0],0,0)
        self.assertLessEqual(len(actions),2)
        self.assertEqual(row['actions_taken'],len(actions))
        if len(actions)==2:
            with self.assertRaises(ValueError):dev.intervene(ops,row,(0,0))
    def test_deterministic_context_and_unique_phase(self):
        fix=dev.FIXTURES[0]
        self.assertEqual(dev.context(fix,'eval',0,5),dev.context(fix,'eval',0,5))
        self.assertNotEqual(dev.context(fix,'eval',0,5),dev.context(fix,'familiar',0,5))
    def test_familiar_does_not_explore(self):
        for name in (dev.ARMS[1],dev.ARMS[3]):
            actor=dev.Learner(name)
            before=dev.start(dev.FIT[0],(0,)*8,(0,)*4)
            self.assertEqual(actor.choose(before,4,dev.FIXTURES[0],0),actor.greedy(before))
    def test_first_use_cli_refused(self):
        p=subprocess.run([sys.executable,dev.__file__,'--primary'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('DISARMED',p.stderr)

if __name__=='__main__':unittest.main()
