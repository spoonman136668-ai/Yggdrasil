"""Source-free negative and arithmetic tests for forensic interference audit."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

SRC = (Path(__file__).resolve().parents[1] / 
       "research/contrib/chatgpt/WSCM-INTERFERENCE-01/audit.py")
SPEC = spec_from_file_location("wscm_interference", SRC)
MOD = module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def rows():
    return [dict(stage=1 + i//24, id=f"{i:064x}",
                 views=[[i % 2, 0], [i % 2, 0]],
                 row=dict(s1=i % 2, x1=i % 2, s2=1, y=0),
                 forecast=dict(pinned=[0, 0], unguarded=[1000000, 0]))
            for i in range(72)]


class InterferenceAuditTests(unittest.TestCase):
    def test_exact_sign_is_positive_for_harm(self):
        self.assertEqual(MOD.score(1000000, 0, 1), 10**12)
        self.assertEqual(MOD.score(0, 1000000, 1), -(10**12))

    def test_separate_transition_and_reward_targets(self):
        out = MOD.aggregate(rows())
        self.assertEqual(len(out['stages']), 3)
        for stage in out['stages']:
            self.assertEqual(stage['count'], 24)
            self.assertEqual(stage['transition_delta'], -1)
            self.assertEqual(stage['reward_delta'], 0)

    def test_public_context_without_hidden_regime_identity(self):
        out = MOD.aggregate(rows())
        self.assertEqual(len(out['cells']), 6)
        self.assertEqual(set(tuple(x['coordinates'][1:]) for x in out['cells']),
                         {(0, 0), (1, 1)})

    def test_original_stage_contract_required(self):
        x = rows(); x[24]['stage'] = 1
        with self.assertRaisesRegex(ValueError, 'WSCM_CELL_STAGE'):
            MOD.aggregate(x)

    def test_bad_receipt_or_reorder_rejected(self):
        x = rows(); x[2]['id'] = x[1]['id']
        with self.assertRaisesRegex(ValueError, 'WSCM_CELL_RECEIPT'):
            MOD.aggregate(x)

    def test_forged_hidden_world_s1_does_not_change_public_context(self):
        x = rows(); x[5]['row']['s1'] = 1 - x[5]['views'][0][0]
        with self.assertRaisesRegex(ValueError, 'WSCM_CELL_PUBLIC_COORDINATE'):
            MOD.aggregate(x)

    def test_missing_paired_prediction_rejected(self):
        x = rows(); x[0]['forecast'].pop('pinned')
        with self.assertRaisesRegex(ValueError, 'WSCM_CELL_PREDICTION'):
            MOD.aggregate(x)

    def test_invalid_outcome_and_probability_fail_closed(self):
        for bad in (2, -1, 0.5):
            x = rows(); x[0]['row']['s2'] = bad
            with self.assertRaises(ValueError):
                MOD.aggregate(x)
        with self.assertRaises(ValueError):
            MOD.score(-1, 0, 1)

    def test_source_pin_failure_before_parsing(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            p = Path(d)/'research/contrib/chatgpt/CAUSAL-AMALGAM/staged-retention-dev-01/seed-818621/trace.json'
            p.parent.mkdir(parents=True); p.write_text('[]')
            with self.assertRaisesRegex(ValueError, 'WSCM_CELL_SOURCE_BLOB'):
                MOD.audit(Path(d))

    def test_determinism_and_conservation_of_target_deltas(self):
        x = rows(); a = MOD.aggregate(x); b = MOD.aggregate(x)
        self.assertEqual(a, b)
        for stage in range(1, 4):
            c = [q for q in a['cells'] if q['coordinates'][0] == stage]
            s = next(q for q in a['stages'] if q['coordinates'][0] == stage)
            self.assertEqual(sum(q['count'] for q in c), s['count'])
            self.assertEqual(sum(int(q['transition_sum_raw']) for q in c),
                             int(s['transition_sum_raw']))
            self.assertEqual(sum(int(q['reward_sum_raw']) for q in c),
                             int(s['reward_sum_raw']))

if __name__ == '__main__':
    unittest.main()
