"""G39 source/archival preflight. A green unit test is NOT native-class proof."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from hashlib import sha256
import os
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1] / 'research/contrib/chatgpt/CAUSAL-AMALGAM'
SPEC = spec_from_file_location('g39_qualification', HERE / 'native_segment_qualification.py')
G39 = module_from_spec(SPEC)
SPEC.loader.exec_module(G39)


class G39NativeClassQualificationTests(unittest.TestCase):
    def test_absent_source_rejects_before_native_import(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'G39_NATIVE_SOURCE_ABSENT'):
                G39.pin_sources(Path(d))

    def test_source_blob_drift_rejects(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for relative in G39.SOURCE_BLOBS:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('not original source', encoding='ascii')
            with self.assertRaisesRegex(ValueError, 'G39_NATIVE_SOURCE_DRIFT'):
                G39.pin_sources(root)

    def test_missing_archive_and_bad_archive_reject(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'missing.zip'
            with self.assertRaisesRegex(ValueError, 'G39_ARCHIVE_ABSENT'):
                G39.extract_original(p, 'linux')
            p.write_bytes(b'bad zip')
            with self.assertRaisesRegex(ValueError, 'G39_ARCHIVE_PIN'):
                G39.extract_original(p, 'linux')

    def test_authentic_linux_and_windows_archive_cold_bytes(self):
        paths = tuple(Path(os.environ.get(key, '/nonexistent/not-provided.zip'))
                      for key in ('YGG_G38_ORIGINAL_LINUX', 'YGG_G38_ORIGINAL_WINDOWS'))
        if not all(path.is_file() for path in paths):
            self.skipTest('Archived ZIPs not supplied; native-class qualification must not be inferred')
        pairs = [G39.extract_original(p, target)
                 for p, target in zip(paths, ('linux', 'windows'), strict=True)]
        self.assertEqual(pairs[0], pairs[1])
        native, episode = pairs[0]
        self.assertEqual(sha256(native).hexdigest(), G39.NATIVE_SHA)
        self.assertEqual(sha256(episode).hexdigest(), G39.EPISODE_SHA)
        manifest, chunks = G39.CODEC.seal(episode)
        self.assertEqual(G39.CODEC.restore(manifest, chunks), episode)
        self.assertEqual(len(chunks), 33)
        self.assertEqual(G39.CODEC.seal(episode), (manifest, chunks))
        # This calls the codec, not original NativeEpisodeExperience.restore.


    def test_json_transport_parity_and_real_forecast_drift(self):
        import json
        original = {
            'native_sha256': 'a' * 64, 'episode_count': 1025,
            'plans': {'(0, 0)': {
                'first_action': 0,
                'first_values': ((1, 3), (2, 5)),
                'second_actions': ((0, 1), (1, 0)),
            }},
        }
        child = json.loads(json.dumps(original))
        self.assertNotEqual(original, child)  # Tuples become lists over JSON.
        G39.require_cold_parity(original, (child, child))
        drift = json.loads(json.dumps(child))
        drift['plans']['(0, 0)']['second_actions'][1][0] = 0
        with self.assertRaisesRegex(ValueError, 'G39_COLD_PROCESS_PARITY'):
            G39.require_cold_parity(original, (child, drift))
        with self.assertRaisesRegex(ValueError, 'G39_COLD_CHILD_COUNT'):
            G39.require_cold_parity(original, (child,))


if __name__ == '__main__':
    unittest.main()
