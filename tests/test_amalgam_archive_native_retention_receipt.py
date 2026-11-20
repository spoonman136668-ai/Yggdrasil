"""Source-free negative tests; no original source generation or model imports."""
import importlib.util
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

PATH=Path(__file__).resolve().parents[1] / "research" / "contrib" / "chatgpt" / "CAUSAL-AMALGAM" / "archive_native_retention_receipt.py"
s=importlib.util.spec_from_file_location('archive_native_retention_receipt',PATH)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

def report():
    def step(c):
        item={'episodes':96,'reward_sum':20,'pooled_brier':[1,4],
              'terminal_brier':[1,8],'transition_brier':[3,8]}
        return {'count':c,'evaluation':{arm:deepcopy(item) for arm in m.ARMS}}
    return {'schema':m.SCHEMA,'source_sha256':m.SOURCE_SHA,
            'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
            'seeds':[{'seed':s,'source_seed':s+56000,'stream':[step(c) for c in m.CHECKPOINTS]}
                     for s in m.SEEDS]}

class ArchiveNativeReceiptTests(unittest.TestCase):
    def test_hash_pin(self):
        self.assertEqual(len(m.ZIP_SHA),64)
    def test_exact_39_control_parity(self):
        d=m.audit(report())
        self.assertEqual(set(d['exact_native_vs_exact_control_parity'].values()),{39})
        self.assertFalse(d['scientific_gain_verified'])
        self.assertEqual(d['original_world_first_use'],0)
    def test_control_stronger_is_not_marked_as_native_gain(self):
        q=report();q['seeds'][0]['stream'][-1]['evaluation']['trailing_mle']['reward_sum']=31
        a=m.audit(q)['checkpoints']['192']
        self.assertEqual(a['candidate_minus_best_control_rewards'],-11)
    def test_original_source_phase_all_frozen_checkpoints(self):
        # CKAD25 held evaluation uses previous completed episode at a boundary.
        expected = {
            0: 'context_switch_regime_0',
            16: 'context_switch_regime_0',
            32: 'context_switch_regime_0',
            48: 'context_switch_regime_0',
            64: 'terminal_switch_regime_0',
            80: 'terminal_switch_regime_0',
            96: 'context_switch_regime_1',
            112: 'context_switch_regime_1',
            128: 'context_switch_regime_1',
            144: 'context_switch_regime_1',
            160: 'invariant_regime_0',
            176: 'invariant_regime_0',
            192: 'invariant_regime_0',
        }
        self.assertEqual(set(expected), set(m.CHECKPOINTS))
        for count, phase in expected.items():
            with self.subTest(count=count):
                self.assertEqual(m.checkpoint_source_phase(count), phase)
        readout = m.audit(report())['checkpoints']
        for count in (80, 96, 144, 160, 176, 192):
            with self.subTest(readout_count=count):
                self.assertEqual(readout[str(count)]['cohort_source_phase'], expected[count])

    def test_source_phase_fails_closed_outside_frozen_clock(self):
        for count in (True, False, None, -1, 49, 79, 81, 143, 145, 193):
            with self.subTest(count=count):
                with self.assertRaisesRegex(ValueError, 'CHECKPOINT_CLOCK'):
                    m.checkpoint_source_phase(count)

    def test_science_flag_tamper_rejected_by_reader(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fake.zip';p.write_bytes(b'untrusted')
            with self.assertRaisesRegex(ValueError,'ARCHIVE_SHA_MISMATCH'):
                m.read_archive(p)
    def test_seed_shift_rejected(self):
        q=report();q['seeds'][0]['source_seed']+=1
        with self.assertRaisesRegex(ValueError,'SOURCE_SEED_OFFSET'):m.audit(q)
    def test_clock_shift_rejected(self):
        q=report();q['seeds'][0]['stream'][0]['count']=1
        with self.assertRaisesRegex(ValueError,'CHECKPOINT_CLOCK'):m.audit(q)
    def test_missing_control_rejected(self):
        q=report();q['seeds'][1]['stream'][0]['evaluation'].pop('exact_mixture')
        with self.assertRaisesRegex(ValueError,'ARM_SET'):m.audit(q)
    def test_unmatched_episode_budget_rejected(self):
        q=report();q['seeds'][2]['stream'][0]['evaluation']['coverage_active']['episodes']=95
        with self.assertRaisesRegex(ValueError,'HELD_RECEIPT_SCOPE'):m.audit(q)

if __name__ == '__main__':unittest.main()
