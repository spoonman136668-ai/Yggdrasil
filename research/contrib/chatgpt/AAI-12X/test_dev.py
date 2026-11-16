"""AAI-12X pre-outcome protocol, exact-control, and cold-restore tests."""
import json
import subprocess
import sys
import unittest
import world
import reference_w
import optimized
import dev

class Protocol(unittest.TestCase):
    def test_novelty_cohorts_independent(self):
        self.assertEqual((len(world.NOVEL),len(world.FAMILIAR),len(world.NEGATIVE),len(world.FIXTURES)),(16,4,4,3))
        self.assertEqual(len(set(world.NOVEL)),16)
        self.assertTrue(all(world.essential(m) for m in world.NOVEL))
        self.assertFalse(world.PREVIOUS_MASKS & set(world.NOVEL))
    def test_w_reference_unchanged_public_contract(self):
        self.assertEqual(len(reference_w.METHODS),6)
        self.assertEqual(reference_w.NF,154)
        self.assertEqual(len(optimized.TRIPLES),280)
    def test_private_hidden_source_never_imported(self):
        with open(optimized.__file__,encoding='utf-8') as f:s=f.read()
        self.assertNotIn('import world',s)
        self.assertNotIn('from world',s)
    def test_denied_science_first_use(self):
        with self.assertRaises(PermissionError):world.train('heldout:secret','novel',0)
        with self.assertRaises(PermissionError):world.train(world.FIXTURES[0],'scientific',0)
    def test_actual_do_pairs(self):
        for f in world.FIXTURES:
            for phase,items in world.WORLDS.items():
                for wid in range(len(items)):
                    rows=world.train(f,phase,wid)
                    self.assertEqual(len(rows),48)
                    for r in rows:
                        x,y=reference_w.check(r)
                        self.assertEqual(world.true_step(f,phase,wid,x,r['y'],r['flipped_index']),(y,r['ynext']))
    def test_source_disjointness(self):
        for f in world.FIXTURES:
            for phase,items in world.WORLDS.items():
                for wid in range(len(items)):
                    fit={tuple(r['x']) for r in world.train(f,phase,wid)}
                    evals=world.evaluations(f,phase,wid)
                    self.assertEqual(len(evals),64)
                    self.assertFalse(any(tuple(x) in fit for e in evals for x in e['predecessor_path']))
    def test_model_exact_equivalence_of_programs(self):
        for f in world.FIXTURES:
            for phase,items in world.WORLDS.items():
                for wid in range(len(items)):
                    rows=world.train(f,phase,wid)
                    self.assertEqual(optimized.fit(rows),reference_w.fit_ternary(rows))
    def test_cold_equivalence(self):
        rows=world.train(world.FIXTURES[0],'novel',0)
        for a in dev.ARMS:
            m=optimized.train(rows) if a=='optimized_ternary' else reference_w.train('ternary_causal' if a=='reference_ternary_AAI12W' else a,rows)
            snap=reference_w.checkpoint(m)
            self.assertEqual(reference_w.restore(snap),m)
            self.assertEqual(reference_w.checkpoint(reference_w.restore(snap)),snap)
            corrupted=json.loads(snap);corrupted['state']['training_sha256']='0'*64
            with self.assertRaises(ValueError):reference_w.restore(reference_w.canonical(corrupted))
    def test_no_hidden_train_model_fields(self):
        row=world.train(world.FIXTURES[0],'novel',0)[0]
        with self.assertRaises(ValueError):reference_w.check({**row,'oracle':world.NOVEL[0]})
    def test_primary_disarmed(self):
        p=subprocess.run([sys.executable,dev.__file__,'--primary'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('SCIENTIFIC FIRST USE DISARMED',p.stderr)

if __name__=='__main__':unittest.main()
