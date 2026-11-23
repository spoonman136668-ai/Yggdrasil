"""Original-source archived native readout parity test; no new world actions.

Requires the original historical checkpoint supplied via WSCM_ARCHIVED_JOINT_PATH.
By default skips instead of weakening provenance or fetching an unapproved source.
"""
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import unittest

from yggdrasil.native_episode_experience import NativeEpisodeExperience
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'research/contrib/chatgpt/WSCM-COLD-READ-01/cold_ablation.py'
LOOKUP = ROOT / 'research/contrib/chatgpt/WSCM-COLD-READ-01/native-readout-lookup.json'
MODSPEC = spec_from_file_location('wscm_archived_readout', SRC)
MOD = module_from_spec(MODSPEC)
MODSPEC.loader.exec_module(MOD)
GIT_LOOKUP_SHA = '4aecd1529179fd1ddd93d5ea9dd3a1bafc980352'


def expected_lookup():
    raw = LOOKUP.read_bytes()
    actual = sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()
    if actual != GIT_LOOKUP_SHA:
        raise ValueError('WSCM_READOUT_REFERENCE_DRIFT')
    return json.loads(raw)


class OriginalArchivedNativeReadout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = os.environ.get('WSCM_ARCHIVED_JOINT_PATH')
        if not p:
            raise unittest.SkipTest('Read-only archived joint fixture not supplied; no download dispatched')
        cls.native = MOD.load_native(Path(p))

    def test_all_16_exact_native_readouts_match_original_lookup(self):
        ref = expected_lookup()
        self.assertEqual(ref['source_checkpoint_sha256'], MOD.ARTIFACT_SHA)
        self.assertEqual(ref['source_branch'], MOD.PARENT_GIT_SHA)
        x = self.native
        before = x.checkpoint()
        self.assertEqual(len(x._ledger), 1025)
        self.assertEqual(len(x._context_models), 29)
        self.assertEqual(len(ref['rows']), 16)
        seen = set()
        count = 0
        for row in ref['rows']:
            ctx, first, state, second = (row[k] for k in ('context','x1','s2','x2'))
            key = (ctx,first,state,second)
            self.assertNotIn(key, seen)
            seen.add(key)
            for arm in ('default','full','pooled'):
                got = [round(MOD.forecast(x, (ctx,0), first, arm=arm)*MOD.SCALE),
                       round(MOD.forecast(x, (ctx,0), first, state, second, arm=arm)*MOD.SCALE)]
                self.assertEqual(got, row[arm], (key,arm))
                count += 1
        self.assertEqual(count, 48)
        self.assertEqual(x.checkpoint(), before)

    def test_cold_restore_is_identical_and_replay_is_read_only(self):
        x = self.native
        first = x.checkpoint()
        resumed = NativeEpisodeExperience.restore(first, sha256(first).hexdigest())
        self.assertEqual(resumed.checkpoint(), first)
        self.assertEqual(resumed.info(), x.info())
        self.assertEqual(resumed._state_digest(), MOD.EXPERIENCE_STATE_SHA)
        for ctx in (0,1):
            for arm in ('default','full','pooled'):
                self.assertEqual(MOD.forecast(x,(ctx,0),0,arm=arm),
                                 MOD.forecast(resumed,(ctx,0),0,arm=arm))
        self.assertEqual(x.checkpoint(),first)
        altered = bytearray(first)
        altered[-1] ^= 1
        with self.assertRaises(ValueError):
            NativeEpisodeExperience.restore(bytes(altered), sha256(first).hexdigest())


if __name__=='__main__':
    unittest.main()
