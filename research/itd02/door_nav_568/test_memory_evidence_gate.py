import unittest
from corroborated_memory_transfer_audit import run

class PublicEvidenceTests(unittest.TestCase):
    def test_matched_public_updates(self):
        cases=run()['cases']
        self.assertEqual(len(cases),16)
        for case in cases:
            self.assertEqual(case['source_actions_per_model'],32)
            for stage in case['stages']:
                self.assertEqual(stage['actions']['local'],stage['round'])
                self.assertEqual(stage['scores']['local'],stage['scores']['conventional'])

    def test_extra_observations_do_not_eliminate_all_unknown_errors(self):
        cases=[r for r in run()['cases'] if not r['familiar_diagnostic']]
        self.assertEqual(len(cases),12)
        for cutoff in ('1','2'):
            self.assertEqual(sum(r['stages'][1]['scores']['local'][cutoff]['wrong'] for r in cases),16)
        self.assertEqual(sum(r['stages'][1]['scores']['local']['3']['abstentions'] for r in cases),24)
        for cutoff in ('1','2','3'):
            self.assertEqual(sum(r['stages'][2]['scores']['local'][cutoff]['wrong'] for r in cases),4)
