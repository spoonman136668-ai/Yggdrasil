"""Archive-pin regression checks; actual archived source gated by presence of original files.

CI without exact original Actions artifacts exercises source-free negatives; do not
claim archived historical checkpoints were tested in CI when these tests are skipped.
"""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'research' / 'contrib' /
          'chatgpt' / 'CAUSAL-AMALGAM' / 'ckad22_exact_intermediate.py')
SPEC = importlib.util.spec_from_file_location('ckad22_exact_intermediate', SOURCE)
a = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(a)
ARCHIVE_DIR = Path(os.environ.get('CKAD22_ARCHIVE_DIR', '/mnt/data'))
PARENT = ARCHIVE_DIR / 'ckad21-original.zip'
CHILD = ARCHIVE_DIR / 'ckad22-original.zip'
WINDOWS = ARCHIVE_DIR / 'ckad22-original-windows-proof.zip'
HAS_ARCHIVES = PARENT.exists() and CHILD.exists() and WINDOWS.exists()


class SourceOnlyGuards(unittest.TestCase):
    def test_empty_pinned_zip_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'corrupt.zip'
            p.write_bytes(b'corrupted')
            with self.assertRaisesRegex(ValueError, 'ARCHIVE_SHA_MISMATCH'):
                a.open_pinned(p, a.CKAD22_SHA)

    def test_canonical_json_no_whitespace(self):
        obj = {'z': 0, 'a': [1, 2]}
        self.assertEqual(a.canonical(obj), b'{"a":[1,2],"z":0}')

    def test_wrong_checkpoint_event_count_rejected(self):
        with self.assertRaisesRegex(ValueError, 'SESSION_COUNT'):
            a.reconstruct({}, {'experience': {'count': 1}}, 384)

    def test_wrong_context_rejected(self):
        with self.assertRaisesRegex(ValueError, 'CONTEXT_BOUNDARY'):
            a.reconstruct({}, {'experience': {'count': 384, 'context': {
                'context_start': 384, 'novel_enabled': True}}}, 384)

    def test_source_mode_flags_fail_closed(self):
        self.assertEqual(a.SCHEDULE, (352, 384, 416, 448))
        self.assertEqual(a.SEEDS, (101, 202, 303))


@unittest.skipUnless(HAS_ARCHIVES, 'original Actions archives unavailable; source-custody test UNVERIFIED')
class OriginalArchiveCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import zipfile
        with zipfile.ZipFile(CHILD) as z:
            r = json.loads(z.read('campaign-result.json'))
            cls.session = r['seeds'][0]['sessions'][1]['states']['novel_active']
            cls.final = json.loads(z.read(r['seeds'][0]['final_checkpoint_name']))

    def test_all_twelve_original_sha_and_cross_os(self):
        results = a.audit(PARENT, CHILD, WINDOWS)
        self.assertEqual(results['historical_exact_checkpoints_verified'], 12)
        self.assertEqual(results['pre_return_384_checkpoints_verified'], 3)
        self.assertFalse(results['original_native_model_executed_now'])

    def test_no_windows_input_same_original_state(self):
        self.assertEqual(a.audit(PARENT, CHILD)['results'],
                         a.audit(PARENT, CHILD, WINDOWS)['results'])

    def test_exact_384_authentic_bytes(self):
        raw = a.reconstruct(self.final, self.session, 384)
        self.assertEqual(a.digest(raw), self.session['checkpoint_sha256'])
        self.assertEqual(len(raw), self.session['checkpoint_bytes'])
        self.assertEqual(json.loads(json.loads(raw)['experience_ascii'])['context_start'], 352)

    def test_pinned_archive_sha(self):
        self.assertEqual(a.digest(CHILD.read_bytes()), a.CKAD22_SHA)
        self.assertEqual(a.digest(PARENT.read_bytes()), a.CKAD21_SHA)
        self.assertEqual(a.digest(WINDOWS.read_bytes()), a.CKAD22_WINDOWS_SHA)

    def test_corrupted_episode_rejected(self):
        f = json.loads(json.dumps(self.final))
        e = json.loads(f['experience_ascii'])
        e['episodes'][383][3] ^= 1
        f['experience_ascii'] = a.canonical(e).decode('ascii')
        with self.assertRaisesRegex(ValueError, 'HISTORICAL_CHECKPOINT_SHA'):
            a.reconstruct(f, self.session, 384)

    def test_wrong_session_count(self):
        with self.assertRaisesRegex(ValueError, 'SESSION_COUNT'):
            a.reconstruct(self.final, self.session, 352)

    def test_context_shift_rejected(self):
        state = json.loads(json.dumps(self.session))
        state['experience']['context']['context_start'] = 384
        with self.assertRaisesRegex(ValueError, 'CONTEXT_BOUNDARY'):
            a.reconstruct(self.final, state, 384)

    def test_checkpoint_pin_change_rejected(self):
        state = json.loads(json.dumps(self.session))
        state['checkpoint_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'HISTORICAL_CHECKPOINT_SHA'):
            a.reconstruct(self.final, state, 384)

    def test_derived_hash_drift_rejected(self):
        state = json.loads(json.dumps(self.session))
        state['experience']['derived_state_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'DERIVED_DIGEST_DRIFT'):
            a.reconstruct(self.final, state, 384)

    def test_wrong_original_seed_source_rejected(self):
        import zipfile
        with zipfile.ZipFile(CHILD) as z:
            r = json.loads(z.read('campaign-result.json'))
            wrong = r['seeds'][2]['sessions'][1]['states']['novel_active']
        with self.assertRaises(ValueError):
            a.reconstruct(self.final, wrong, 384)

    def test_canonical_roundtrip(self):
        original = a.reconstruct(self.final, self.session, 384)
        self.assertEqual(a.canonical(json.loads(original)), original)


if __name__ == '__main__':
    unittest.main()
