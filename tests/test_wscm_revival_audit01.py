"""Focused no-leak and source-custody negative tests for WSCM replay audit."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / 'research/contrib/chatgpt/WSCM-REVIVAL-AUDIT-01/audit.py'
SPEC = spec_from_file_location('wscm_revival_audit', SRC)
MOD = module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def synthetic_rows(y_second=0, p_first=0, p_second=1000000):
    rows = []
    for i in range(72):
        forecast = {key: [p_first, p_second] for key in MOD.EXPERTS if key != 'prequential_gate'}
        rows.append({'id': format(i, '064x'), 'stage': 1+i//24,
                     'forecast': forecast, 'row': {'s2': 0, 'y': y_second}})
    return rows


class RevivalAuditTests(unittest.TestCase):
    def test_shadow_never_uses_future_outcomes(self):
        a = synthetic_rows()
        report_a = MOD.audit_rows(a)
        a[-1]['row']['y'] = 1
        report_b = MOD.audit_rows(a)
        self.assertEqual(report_a['phases']['1'], report_b['phases']['1'])
        self.assertEqual(report_a['phases']['2'], report_b['phases']['2'])

    def test_equal_forecasts_stay_pinned(self):
        r = MOD.audit_rows(synthetic_rows())
        self.assertEqual(r['selected_unguarded'], 0)
        self.assertEqual(r['switches'], 0)
        self.assertEqual(r['phases']['3']['revival_gain_vs_pinned'], 0)

    def test_unguarded_chosen_only_after_four_outcomes(self):
        r = synthetic_rows(y_second=1)
        for row in r:
            row['forecast']['pinned'] = [0, 0]
            row['forecast']['unguarded'] = [0, 1000000]
        result = MOD.audit_rows(r)
        self.assertEqual(result['selected_unguarded'], 68)
        self.assertEqual(result['phases']['1']['selected_unguarded'], 20)

    def test_nonbinary_reveal_rejected(self):
        x = synthetic_rows(); x[0]['row']['y'] = 2
        with self.assertRaisesRegex(ValueError, 'REVIVAL_PUBLIC_FORECAST_CONTRACT'):
            MOD.audit_rows(x)

    def test_wrong_stage_metadata_rejected(self):
        x = synthetic_rows(); x[24]['stage'] = 3
        with self.assertRaisesRegex(ValueError, 'REVIVAL_STAGE_CONTRACT'):
            MOD.audit_rows(x)

    def test_duplicate_receipt_rejected(self):
        x = synthetic_rows(); x[5]['id'] = x[4]['id']
        with self.assertRaisesRegex(ValueError, 'REVIVAL_RECEIPT_CONTRACT'):
            MOD.audit_rows(x)

    def test_forged_extra_expert_rejected(self):
        x = synthetic_rows(); x[0]['forecast']['oracle_regime'] = [1, 1]
        with self.assertRaisesRegex(ValueError, 'REVIVAL_EXPERT_CONTRACT'):
            MOD.audit_rows(x)

    def test_missing_or_changed_source_fails_closed(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            root = Path(d)
            p = MOD.source_trace_path(root, 818621)
            p.parent.mkdir(parents=True)
            p.write_text('[]')
            with self.assertRaisesRegex(ValueError, 'REVIVAL_SOURCE_BLOB_MISMATCH'):
                MOD.audit_sources(root)

    def test_score_scaling_and_contract(self):
        self.assertEqual(MOD._loss_pair([0, 1000000], {'s2': 0, 'y': 1}), 0)
        self.assertEqual(MOD._score(1000000000000, 1), 0.5)
        with self.assertRaisesRegex(ValueError, 'REVIVAL_ROW_COUNT'):
            MOD.audit_rows([])


if __name__=='__main__':
    unittest.main()
