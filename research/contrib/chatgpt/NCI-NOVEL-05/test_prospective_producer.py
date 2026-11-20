"""Source-free negative controls; no archived world is invoked by these tests."""
import tempfile
import json
import unittest
from pathlib import Path
import subprocess
from unittest.mock import patch

import prospective_producer as p
from receipt_guard import read_verified, commit_world

SHA = 'b' * 64


class ProducerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'engineering.jsonl'

    @staticmethod
    def fake(seed, family):
        return {'seed': seed, 'family': family, 'held': {'CAND': 0.2}, 'old_stable': True}

    def run_one(self, seed=917201, family='fourfold', single=None):
        return p.run_engineering_world(ledger=self.path, archive=Path('unused_archive'),
                                       seed=seed, family=family, single=single or self.fake,
                                       source_key=SHA)

    def test_one_world_durable_receipt_and_attempt(self):
        digest = self.run_one()
        rows = read_verified(self.path, SHA)
        self.assertEqual(rows[0]['entry_sha256'], digest)
        self.assertTrue(rows[0]['result']['complete'])
        self.assertEqual(rows[0]['result']['mode'], 'ENGINEERING_ONLY')
        self.assertTrue((self.path.parent / (self.path.name+'.engineering-917201-fourfold.attempt')).exists())

    def test_consumed_science_seeds_denied_without_calling(self):
        for seed in p.CONSUMED:
            with self.subTest(seed=seed):
                with self.assertRaisesRegex(ValueError, 'engineering-only'):
                    self.run_one(seed, single=lambda *_: self.fail('source executed'))
        self.assertFalse(self.path.exists())

    def test_other_seed_denied(self):
        with self.assertRaisesRegex(ValueError, 'engineering-only'):
            self.run_one(seed=11111)

    def test_bool_seed_denied(self):
        with self.assertRaisesRegex(ValueError, 'engineering-only'):
            self.run_one(seed=True)

    def test_unknown_family_denied(self):
        with self.assertRaisesRegex(ValueError, 'unknown engineering family'):
            self.run_one(family='another_world')

    def test_duplicate_without_second_execution(self):
        self.run_one()
        original = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'no replay'):
            self.run_one(single=lambda *_: self.fail('unexpected replay'))
        self.assertEqual(self.path.read_bytes(), original)

    def test_crash_claim_prevents_replay(self):
        def crash(*_):
            raise RuntimeError('simulated crash after claim')
        with self.assertRaisesRegex(RuntimeError, 'simulated crash'):
            self.run_one(single=crash)
        with self.assertRaises(FileExistsError):
            self.run_one(single=lambda *_: self.fail('unexpected replay'))
        self.assertFalse(self.path.exists())

    def test_result_identity_mismatch_no_receipt(self):
        with self.assertRaisesRegex(ValueError, 'result identity mismatch'):
            self.run_one(single=lambda s,f: {'seed': 999, 'family': f})
        self.assertFalse(self.path.exists())
        with self.assertRaises(FileExistsError):
            self.run_one()

    def test_sha_source_mismatch_fail_closed(self):
        self.run_one()
        with self.assertRaisesRegex(ValueError, 'source mismatch'):
            p.run_engineering_world(ledger=self.path, archive=Path('unused_archive'),
                                    seed=917203, family='fourfold', single=self.fake,
                                    source_key='c'*64)

    def test_bad_timeout_rejected_before_execution(self):
        for invalid in (0, -1, float('nan'), float('inf'), True):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, 'invalid bounded'):
                    p.run_engineering_world(ledger=self.path, archive=Path('unused_archive'),
                                            seed=917201, family='fourfold', single=self.fake,
                                            source_key=SHA, max_world_seconds=invalid)
        self.assertFalse(self.path.exists())

    def test_timed_out_child_claim_consumed(self):
        with patch.object(p, '_engine', side_effect=RuntimeError('engineering world timed out')):
            with self.assertRaisesRegex(RuntimeError, 'timed out'):
                p.run_engineering_world(ledger=self.path, archive=Path('unused_archive'),
                                        seed=917201, family='fourfold', source_key=SHA,
                                        max_world_seconds=2)
        with self.assertRaises(FileExistsError):
            self.run_one()

    def test_internal_worker_denies_unreserved_seed(self):
        with self.assertRaisesRegex(ValueError, 'internal worker seed/family denied'):
            p._worker(archive=Path('unused_archive'), seed=809011, family='fourfold',
                      claim=self.path, source_key=SHA, output=self.path)

    def test_complete_profile_budget(self):
        for seed in p.ENGINEERING_SEEDS:
            for family in p.FAMILIES:
                self.run_one(seed, family)
        q = p.qualify_budget(ledger=self.path, source_key=SHA, target_worlds=4,
                             budget_seconds=600)
        self.assertEqual(q['worlds_measured'], 21)
        self.assertEqual(q['families_measured'], 7)
        self.assertTrue(q['qualified'])
        self.assertFalse(q['science_executed'])

    def test_incomplete_profile_denied(self):
        self.run_one()
        with self.assertRaisesRegex(ValueError, 'incomplete engineering'):
            p.qualify_budget(ledger=self.path, source_key=SHA, target_worlds=4,
                             budget_seconds=100)

    def test_foreign_receipt_denied(self):
        commit_world(self.path,source_sha256=SHA,world_id='unknown', elapsed_ms=1,
                     result={'complete':True,'mode':'PRIMARY_ONCE','seed':1,'family':'fourfold'})
        with self.assertRaisesRegex(ValueError, 'foreign or invalid'):
            p.qualify_budget(ledger=self.path, source_key=SHA, target_worlds=4,
                             budget_seconds=100)

    def test_archive_mismatch_denied(self):
        archive = Path(self.tmp.name)/'source_preprimary.tar.gz'
        archive.write_bytes(b'bad frozen source')
        with self.assertRaisesRegex(ValueError, 'frozen archive mismatch'):
            p.frozen_experiment(archive)

    def test_internal_worker_cli_reaches_seed_guard_without_ledger(self):
        cmd = [p.sys.executable, str(Path(p.__file__).resolve()),
               '--internal-worker', '--seed', str(p.CONSUMED[1]),
               '--family', p.FAMILIES[0], '--claim', str(self.path),
               '--source-key', SHA, '--worker-out', str(self.path.with_suffix('.result'))]
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('internal worker seed/family denied', run.stderr)
        self.assertNotIn('arguments are required', run.stderr)
        self.assertFalse(self.path.exists())

    def test_public_cli_still_requires_ledger(self):
        cmd = [p.sys.executable, str(Path(p.__file__).resolve()),
               '--engineering-world', '--seed', str(p.ENGINEERING_SEEDS[0]),
               '--family', p.FAMILIES[0], '--max-world-seconds', '1']
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('ledger required outside internal worker', run.stderr)
        self.assertFalse(self.path.exists())

    def test_dynamic_module_pickle_with_mock_only(self):
        claim = self.path.with_suffix('.claim')
        claim.write_text(json.dumps({
            'schema': p.PROTOCOL, 'world_id': 'engineering:917201:fourfold',
            'source_sha256': SHA
        }))
        out = self.path.with_suffix('.result')
        source = (
            'import pickle\n'
            'class Dummy:\n    pass\n'
            'def single(seed, family):\n'
            '    obj = Dummy()\n'
            "    raw = pickle.dumps(obj)\n"
            "    return {'seed':seed, 'family':family, "
            "'pickle_bytes':len(raw), 'cold_restore':isinstance(pickle.loads(raw), Dummy)}\n"
        )
        with patch.object(p, 'source_identity', return_value=SHA), \
             patch.object(p, 'frozen_experiment', return_value=source):
            p._worker(archive=Path('unused'), seed=917201, family='fourfold',
                      claim=claim, source_key=SHA, output=out)
        self.assertTrue(json.loads(out.read_text())['cold_restore'])
        self.assertNotIn('_frozen_nci05_engineering', p.sys.modules)

    def test_child_failure_exposes_bounded_stderr_no_retry(self):
        err = subprocess.CalledProcessError(1, ['fake-child'], stderr=b'pickle-failed')
        with patch.object(p.subprocess, 'run', side_effect=err):
            with self.assertRaisesRegex(RuntimeError, 'pickle-failed'):
                p._engine(917201, 'fourfold', Path('unused'), self.path, SHA, 5)

    def test_not_a_scientific_runner_cli(self):
        self.assertFalse(hasattr(p, 'run_primary'))
        self.assertNotIn('809011', str(p.ENGINEERING_SEEDS))


if __name__ == '__main__':
    unittest.main()
