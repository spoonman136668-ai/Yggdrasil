"""AAI-12T matched source, bounded memory and first-use invariant tests."""
import json
import subprocess
import sys
import unittest
import dev

class AAI12TTests(unittest.TestCase):
    def test_inventory(self):
        self.assertEqual((len(dev.NOVEL),len(dev.FAMILIAR),len(dev.NEGATIVE)),(12,4,4))
        self.assertEqual(len(set(dev.NOVEL)),12)

    def test_synthetic_unknown_relations_are_really_outside_fixed_grammar(self):
        base={mask for _,mask in dev.catalog()}
        self.assertTrue(all(dev.source_mask('novel',spec) not in base for spec in dev.NOVEL))
        self.assertTrue(all(dev.source_mask('familiar',spec) in base for spec in dev.FAMILIAR))

    def test_exact_real_one_bit_public_do_and_disjoint_heldouts(self):
        for category,worlds in dev.CATEGORIES:
            for idx,w in enumerate(worlds):
                for fix in dev.FIXTURES:
                    pairs=dev.paired_do_inputs(fix,category,idx)
                    xs=[x for a,b in pairs for x in (a,b)]
                    self.assertEqual(len(pairs),16)
                    self.assertEqual(len(set(xs)),32)
                    self.assertEqual(len(set(range(64))-set(xs)),32)
                    self.assertTrue(all((a^b).bit_count()==1 for a,b in pairs))

    def test_denied_independent_first_use(self):
        for fn in ('scientific:primary','fresh:transfer'):
            with self.assertRaises(PermissionError):dev.ranked_source(fn,'novel',0)
        with self.assertRaises(PermissionError):dev.ranked_source(dev.FIXTURES[0],'science',0)
        with self.assertRaises(PermissionError):dev.ranked_source(dev.FIXTURES[0],'novel',13)

    def test_all_models_same_public_rows(self):
        spec=dev.NOVEL[0];truth=dev.source_mask('novel',spec)
        rows=dev.public_observations(truth,dev.paired_do_inputs(dev.FIXTURES[0],'novel',0))
        self.assertEqual(len(rows),32)
        self.assertEqual(len(set(x for x,_ in rows)),32)
        for arm in dev.ARMS:
            model=dev.fit_arm(arm,rows)
            self.assertTrue(dev.cold(arm,rows,model))
            self.assertIn(dev.predict(*model,0),(0,1))

    def test_invention_not_hidden_oracle(self):
        spec=dev.NOVEL[0];truth=dev.source_mask('novel',spec)
        rows=dev.public_observations(truth,dev.paired_do_inputs(dev.FIXTURES[0],'novel',0))
        triple,fourth,table,modelmask=dev.fit_ternary(rows)
        self.assertEqual(len(triple),3)
        self.assertNotIn(fourth,triple)
        self.assertLess(table,256)
        self.assertEqual(sum(dev.predict('ternary',(triple,fourth,table,modelmask),x)==y for x,y in rows),32)

    def test_source_free_catalog_deterministic(self):
        a=dev.catalog()
        self.assertEqual(a,dev.catalog())
        self.assertTrue(len(a)>1000)

    def test_novelty_gate_does_not_always_expand(self):
        truth=dev.source_mask('familiar',dev.FAMILIAR[0])
        rows=dev.public_observations(truth,dev.paired_do_inputs(dev.FIXTURES[0],'familiar',0))
        self.assertIn(dev.fit_arm('novelty_gate',rows)[0],('fixed','knn','ternary'))
        self.assertIn(dev.fit_arm('adaptive_no_growth',rows)[0],('fixed','knn'))

    def test_stable_checkpoint_no_external_mutation(self):
        spec=dev.NOVEL[1];truth=dev.source_mask('novel',spec)
        rows=dev.public_observations(truth,dev.paired_do_inputs(dev.FIXTURES[1],'novel',1))
        for arm in dev.ARMS:
            model=dev.fit_arm(arm,rows)
            self.assertTrue(dev.cold(arm,rows,model))
            self.assertEqual(model,dev.fit_arm(arm,rows))

    def test_ternary_primitive_checkpoint_and_tamper_denial(self):
        truth=dev.source_mask('novel',dev.NOVEL[0])
        rows=dev.public_observations(truth,dev.paired_do_inputs(dev.FIXTURES[0],'novel',0))
        model=dev.fit_arm('always_ternary_256',rows)
        snapshot=dev.checkpoint('always_ternary_256',rows,model)
        encoded=json.loads(snapshot)
        self.assertIn('truth_table_u8',encoded['learned_primitive'])
        self.assertEqual(dev.restore_checkpoint(snapshot),model)
        encoded['learned_primitive']['truth_table_u8']^=1
        damaged=json.dumps(encoded,sort_keys=True,separators=(',',':'))
        with self.assertRaises(ValueError):dev.restore_checkpoint(damaged)

    def test_primary_cli_disarmed(self):
        p=subprocess.run([sys.executable,dev.__file__,'--primary'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('SCIENTIFIC FIRST USE DISARMED',p.stderr)

if __name__=='__main__':unittest.main()
