"""AAI-12S source-only mechanical invariants and negative controls."""
import json
import subprocess
import sys
import unittest
import dev


class AAI12STests(unittest.TestCase):
    def test_world_source_budget(self):
        self.assertEqual((len(dev.FIT),len(dev.TRANSFER),len(dev.NEGATIVE),len(dev.FIXTURES)),(4,12,4,2))
        self.assertEqual(len(set(dev.TRANSFER)),12)

    def test_real_do_pairs_and_disjoint_heldouts(self):
        for fixture in dev.FIXTURES:
            for group,size in (('fit',4),('transfer',12),('negative',4)):
                for i in range(size):
                    pairs=dev.witness_pairs(fixture,f'{group}:{i}')
                    xs=[x for p in pairs for x in p]
                    self.assertEqual(len(pairs),8)
                    self.assertEqual(len(set(xs)),16)
                    self.assertEqual(len(set(range(64))-set(xs)),48)
                    self.assertTrue(all((a^b).bit_count()==1 for a,b in pairs))

    def test_unknown_scientific_source_denied(self):
        with self.assertRaises(PermissionError):dev.order_key('unseen:heldout','fit:0',0)
        with self.assertRaises(PermissionError):dev.order_key('mechanical:alpha','scientific:0',0)

    def test_expression_induction_grammar_covers_synthetic_compositions(self):
        pool={mask for _,mask in dev.COMPOSED_PROGRAMS}
        self.assertTrue(len(pool)>len(dev.SINGLE_PROGRAMS))
        for src in (*dev.FIT,*dev.TRANSFER):self.assertIn(dev.expr_mask(src),pool)

    def test_out_of_grammar_negative_is_genuinely_out(self):
        pool={mask for _,mask in dev.COMPOSED_PROGRAMS}
        for neg in dev.NEGATIVE:self.assertNotIn(dev.negative_mask(neg),pool)

    def test_public_rows_equal_per_model(self):
        pairs=dev.witness_pairs(dev.FIXTURES[0],'transfer:0')
        public=dev.observations(dev.expr_mask(dev.TRANSFER[0]),pairs)
        self.assertEqual(len(public),16)
        self.assertEqual(len(set(x for x,_ in public)),16)
        for arm in dev.ARMS:
            model=dev.train_arm(arm,public)
            self.assertIn(dev.predict_arm(arm,model,0),(0,1))

    def test_full_support_recovers_expressions_without_hidden_structure(self):
        for src in dev.TRANSFER:
            truth=dev.expr_mask(src)
            public=tuple((x,(truth>>x)&1) for x in range(64))
            inferred=dev.train_arm('synth_composed',public)
            self.assertEqual(inferred,truth)

    def test_pure_conventional_repeatability(self):
        pairs=dev.witness_pairs(dev.FIXTURES[1],'transfer:3')
        public=dev.observations(dev.expr_mask(dev.TRANSFER[3]),pairs)
        for arm in dev.ARMS:
            self.assertEqual(dev.train_arm(arm,public),dev.train_arm(arm,public))

    def test_primary_cli_is_disarmed(self):
        proc=subprocess.run([sys.executable,dev.__file__,'--primary'],capture_output=True,text=True)
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('SCIENTIFIC FIRST USE DISARMED',proc.stderr)

    def test_frozen_all_gate_no_go(self):
        first=dev.score_screen()
        second=dev.score_screen()
        self.assertEqual(first['trace_sha256'],second['trace_sha256'])
        self.assertEqual(first['accuracy'],second['accuracy'])
        self.assertEqual(first['classification'],'DEV_NO_GO_NO_SCIENCE')
        self.assertEqual(first['scientific_cohorts_consumed'],0)
        self.assertEqual(len(first['frozen_checks']),6)


if __name__=='__main__':unittest.main()
