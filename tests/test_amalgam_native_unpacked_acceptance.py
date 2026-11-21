"""G39 fail-closed real artifact preflight; no native actor or training."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import os
import tempfile
import unittest

HERE = (Path(__file__).resolve().parents[1] / 'research/contrib/chatgpt/CAUSAL-AMALGAM')
import sys
sys.path.insert(0, str(HERE))
SPEC = spec_from_file_location('g39_unpacked_acceptance_test', HERE / 'native_segment_unpacked_acceptance.py')
G39 = module_from_spec(SPEC)
SPEC.loader.exec_module(G39)

class UnpackedNativeAcceptanceTests(unittest.TestCase):
    def test_requires_authentic_archives_and_valid_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / 'bad.json'
            with self.assertRaisesRegex(ValueError, 'G39_ORIGINAL_UNPACKED_ABSENT'):
                G39.original_from_unpacked(bad, 'linux')
            bad.write_bytes(b'fake archive')
            with self.assertRaisesRegex(ValueError, 'G39_ORIGINAL_UNPACKED_PIN'):
                G39.original_from_unpacked(bad, 'linux')
            with self.assertRaisesRegex(ValueError, 'G39_ORIGINAL_UNPACKED_ABSENT'):
                G39.original_from_unpacked(bad, 'not-a-platform')

    def test_both_authenticated_originals_share_native_and_episode(self):
        linux=Path(os.environ.get('YGG_G39_ORIGINAL_LINUX_JSON','/nonexistent/linux.json'))
        windows=Path(os.environ.get('YGG_G39_ORIGINAL_WINDOWS_JSON','/nonexistent/windows.json'))
        if not linux.is_file() or not windows.is_file():
            self.skipTest('Must supply both original authenticated JSON artifacts')
        a=G39.original_from_unpacked(linux,'linux')
        b=G39.original_from_unpacked(windows,'windows')
        self.assertEqual(a,b)
        self.assertEqual(sha256(a[0]).hexdigest(),G39.G39.NATIVE_SHA)
        self.assertEqual(sha256(a[1]).hexdigest(),G39.G39.EPISODE_SHA)
        m,parts=G39.G39.CODEC.seal(a[1])
        self.assertEqual(G39.G39.CODEC.restore(m,parts),a[1])

if __name__ == '__main__':
    unittest.main()
