"""WSCM-EPOCH-02: pre-primary isolated negative and source-custody checks."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1]/'research/contrib/chatgpt/WSCM-EPOCH-02/sealed_runner.py'
S = spec_from_file_location('wscm_epoch02',SRC)
M = module_from_spec(S)
S.loader.exec_module(M)


def fake(seed, altered, changed, ret, warm=0):
    z={name:0.20 for name in M.CONTROLS}
    z['epoch']=changed
    return {'seed':seed,'altered':altered,'episodes':112,
            'transition_brier':{'changed':z,'A_return':{'epoch':ret,'frozen':0.20},'A_warm':{}},
            'stage_activations':{'A_warm':warm},'stage_end_checkpoints':[{}, {}, {}]}


class Epoch02Tests(unittest.TestCase):
    def test_fresh_seeds_disjoint_from_consumed(self):
        self.assertEqual(M.ORDER,(('B',94011),('B',94023),('C',95011),('C',95023)))
        self.assertTrue({x for _,x in M.ORDER}.isdisjoint({92011,92023,92041,93011,93023,93041}))

    def test_immutable_original_source_read_with_only_allowlist_rebound(self):
        script=M.ORIGINAL.read_bytes()
        self.assertEqual(M.git_blob(script),M.SOURCE_BLOB)
        model=M.source_model()
        self.assertEqual(model.SEEDS,M.SEEDS)
        self.assertEqual(M.git_blob(M.ORIGINAL.read_bytes()),M.SOURCE_BLOB)
        self.assertEqual(model.A_LAW,((5,27),(7,25)))
        self.assertEqual(model.STAGES,(('A_warm',0,16),('changed',16,64),('A_return',64,112)))

    def test_original_fixture_identity_and_protocol_pin(self):
        joint=Path('/mnt/data/wscm_exact/amalgam-joint-state.json')
        if not joint.exists(): self.skipTest('fixture not available')
        expected=M.git_blob(SRC.read_bytes())
        z=M.source_preflight(joint,expected)
        self.assertEqual(z['original_joint_sha256'],M.ARTIFACT_SHA)
        self.assertEqual(z['epoch01_source_blob'],M.SOURCE_BLOB)

    def test_spurious_activation_fails_promising_gate(self):
        rows=[fake(seed,altered,.15,.20) for altered,seed in M.ORDER]
        self.assertEqual(M.classify(rows)[0],'DEV_PROMISING_ONLY')
        rows[0]['stage_activations']['A_warm']=1
        self.assertEqual(M.classify(rows)[0],'DEV_MIXED')

    def test_retention_failure_is_no_go(self):
        rows=[fake(seed,altered,.15,.20) for altered,seed in M.ORDER]
        rows[1]['transition_brier']['A_return']['epoch']=.25
        self.assertEqual(M.classify(rows)[0],'DEV_NO_GO')

    def test_all_four_changed_fail_is_no_go(self):
        rows=[fake(seed,altered,.22,.20) for altered,seed in M.ORDER]
        self.assertEqual(M.classify(rows)[0],'DEV_NO_GO')

    def test_partial_or_misidentified_cohort_rejected(self):
        rows=[fake(seed,altered,.15,.20) for altered,seed in M.ORDER]
        with self.assertRaisesRegex(ValueError,'EPOCH02_INCOMPLETE_COHORT'): M.classify(rows[:-1])
        rows[2]['episodes']=111
        with self.assertRaisesRegex(ValueError,'EPOCH02_INCOMPLETE_SEED'): M.classify(rows)

    def test_marker_is_write_once_and_fsync(self):
        with TemporaryDirectory() as td:
            f=Path(td)/'started.json';M.atomic_write(f,b'first')
            with self.assertRaisesRegex(ValueError,'EPOCH02_RECEIPT_ALREADY_EXISTS'):
                M.atomic_write(f,b'replay')
            self.assertEqual(f.read_bytes(),b'first')

    def test_no_replay_nonempty_directory(self):
        with TemporaryDirectory() as td:
            d=Path(td)/'receipts';d.mkdir();(d/'B-94011.started.json').write_text('{}')
            # Source integrity is checked before the no-replay journal gate.
            # This frozen runner now intentionally rejects the newer native
            # implementation; that independent negative must remain visible.
            with self.assertRaisesRegex(ValueError,'EPOCH02_NATIVE_SOURCE_DRIFT'):
                M.parent(Path('/mnt/data/wscm_exact/amalgam-joint-state.json'),d,M.git_blob(SRC.read_bytes()))
            # Isolate the journal gate without weakening source_preflight in
            # production or launching any child. The existing marker must win.
            with patch.object(M, 'source_preflight', return_value={}):
                with self.assertRaisesRegex(ValueError,'EPOCH02_PRIOR_ATTEMPT_FOUND_NO_REPLAY'):
                    M.parent(Path('/mnt/data/wscm_exact/amalgam-joint-state.json'),d,M.git_blob(SRC.read_bytes()))
            self.assertEqual(sorted(p.name for p in d.iterdir()), ['B-94011.started.json'])

    def test_receipt_corruption_rejected(self):
        with TemporaryDirectory() as td:
            path=Path(td)/'receipt.json';path.write_text(json.dumps({'status':'COMPLETE','seed':94011,'altered':'B','pins':{'p':'wrong'},'result':{'episodes':112}}))
            with self.assertRaisesRegex(ValueError,'EPOCH02_RECEIPT_MISMATCH'):
                M._read_receipt(path,'B',94011,{'p':'correct'})


if __name__=='__main__':
    unittest.main()
