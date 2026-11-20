"""Read-only historical original-archive and negative controls for CKAD22 return audit."""
from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "research" / "contrib" / "chatgpt" / "CAUSAL-AMALGAM" / "ckad22_true_return.py"
spec = importlib.util.spec_from_file_location("ckad22_true_return", SRC)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    def evaluated():
        return {k: {'episodes': 96, 'reward_sum': 80,
                    'transition_brier': [1, 4],
                    'terminal_brier': [1, 4],
                    'pooled_brier': [1, 4]} for k in m.ARMS}
    return {'schema': m.SCHEMA, 'source_sha256': m.SOURCE_SHA256,
            'scientific_pass': False, 'accepted_native': False,
            'deployment': 'NONE', 'classification': 'DEVELOPMENT_GO',
            'scope': {'original_source_actions': 0, 'protected_first_use': 0, 'held_updates': 0},
            'seeds': [
                {'seed': seed, 'source_seed': seed + 7000,
                 'sessions': [{'session': i, 'family': family, 'regime': regime,
                               'probe_cohort': f'ckad22-probe-{i}',
                               'held_cohort': f'ckad22-held-{i}',
                               'training_episodes': 320+32*(i+1),
                               'evaluation': evaluated()}
                              for i, (family, regime) in enumerate(m.WORLDS)]}
                for seed in m.SEEDS]}


class Ckad22TrueReturnTests(unittest.TestCase):
    def test_synthetic_receipt_exact_parity_and_no_gain(self):
        d = m.audit(fixture())
        self.assertEqual(set(d['independent_mixture_parity_over_12_seed_sessions'].values()), {12})
        self.assertEqual(d['frozen_historical_return_advantage_screen'], 'RETURN_SCREEN_NO_GO')
        self.assertEqual(d['sessions'][2]['native_minus_best_control'], 0)
        self.assertFalse(d['scientific_gain_verified'])

    def test_held_return_wins_does_not_override_original_science(self):
        d = fixture()
        # Identical exact_mix => no false new-world gain despite large control gap.
        for s in d['seeds']:
            e = s['sessions'][2]['evaluation']
            e['novel_active']['reward_sum'] = 85
            e['exact_mixture']['reward_sum'] = 85
            for arm in m.BASELINES: e[arm]['reward_sum'] = 50
        result = m.audit(d)
        self.assertEqual(result['frozen_historical_return_advantage_screen'], 'RETURN_SCREEN_PASS')
        self.assertFalse(result['scientific_gain_verified'])

    def test_wrong_world_identity_rejected(self):
        d=fixture(); d['seeds'][0]['sessions'][2]['regime'] = 1
        with self.assertRaisesRegex(ValueError,'FROZEN_SOURCE_WORLD_CLOCK'): m.audit(d)

    def test_wrong_source_seed_rejected(self):
        d=fixture(); d['seeds'][1]['source_seed']+=1
        with self.assertRaisesRegex(ValueError,'FROZEN_SOURCE_SEED'): m.audit(d)

    def test_missing_control_rejected(self):
        d=fixture();d['seeds'][0]['sessions'][0]['evaluation'].pop('exact_mixture')
        with self.assertRaisesRegex(ValueError,'FROZEN_CONTROL_SET'): m.audit(d)

    def test_malformed_brier_rejected(self):
        d=fixture();d['seeds'][0]['sessions'][0]['evaluation']['beta']['pooled_brier']=[1,0]
        with self.assertRaisesRegex(ValueError,'SCORED_BRIER_FRACTION'):m.audit(d)

    def test_science_flag_rejected(self):
        d=fixture();d['scientific_pass']=True
        with self.assertRaisesRegex(ValueError,'FROZEN_SOURCE_SCIENCE_BOUNDARY'):m.audit(d)

    def test_exact_parity_drift_rejected(self):
        d=fixture();d['seeds'][2]['sessions'][2]['evaluation']['exact_mixture']['reward_sum']-=1
        with self.assertRaisesRegex(ValueError,'ORIGINAL_INDEPENDENT_EXACT_MIXTURE_PARITY'):m.audit(d)

    def test_invalid_archive_sha_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'untrusted.zip';p.write_bytes(b'not the original archive')
            with self.assertRaisesRegex(ValueError,'ORIGINAL_ZIP_SHA256_MISMATCH'):m.read_original(p)

    def test_source_world_return_frozen_exactly(self):
        self.assertEqual(m.WORLDS[0],m.WORLDS[2]);self.assertNotEqual(m.WORLDS[0],m.WORLDS[3])
        self.assertEqual(tuple(m.SEEDS),(101,202,303))


if __name__ == '__main__':
    unittest.main()
