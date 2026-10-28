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
