"""Offline tests on original CB7 consumed-world expected returns only."""
import json
import unittest
import forensic

class TestCB7RegretAudit(unittest.TestCase):
    def test_exact_immutable_source_and_archive(self):
        self.assertEqual(forensic.audit()['schema'],'yggdrasil.cb7.posthoc-regret-audit.v1')

    def test_original_net_return_reproduced(self):
        r=forensic.audit()
        self.assertAlmostEqual(r['mean_net_direct'],.5305532930309593,places=12)
        self.assertAlmostEqual(r['mean_net_bayes'],.5738303377697626,places=12)

    def test_source_readonly_and_no_original_first_use(self):
        r=forensic.audit()
        self.assertFalse(r['source_first_use'])
        self.assertEqual(r['actual_new_paid_actions'],0)
        self.assertEqual(r['model_training'],0)
        self.assertFalse(r['scientific_pass'])

    def test_9_1_3_19_failure_partition(self):
        counts={k:v['worlds'] for k,v in forensic.audit()['groups'].items()}
        self.assertEqual(counts,{'stops_early':9,'different_first_probe':1,
                                 'same_first_later_diverges':3,'equal_expected_return':19})

    def test_stop_early_dominant_regret(self):
        r=forensic.audit()
        self.assertAlmostEqual(r['mean_regret'],.043277044738803214,places=12)
        self.assertGreater(r['stop_early_regret_fraction'],.985)
        self.assertLess(r['stop_early_regret_fraction'],.986)

    def test_root_nonnegativity(self):
        self.assertTrue(all(x[4]>=0 for x in forensic.audit()['per_world_decision_receipts']))

    def test_source_module_no_world_actions(self):
        from pathlib import Path
        s=Path(forensic.__file__).read_text()
        self.assertNotIn('World(',s)
        self.assertNotIn('.probe(',s)
        self.assertNotIn('study(',s)

    def test_mutated_archive_fails_closed(self):
        from pathlib import Path
        path=forensic.ROOT/'world_net.json'
        original=path.read_bytes()
        try:
            path.write_bytes(original+b' ')
            with self.assertRaisesRegex(ValueError,'ARCHIVED_WORLD_NET_DRIFT'):forensic.audit()
        finally:path.write_bytes(original)

if __name__=='__main__':unittest.main()
