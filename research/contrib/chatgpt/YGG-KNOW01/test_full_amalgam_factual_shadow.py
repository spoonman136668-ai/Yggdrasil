"""KNOW10 source-only negative controls; no protected model owner actions."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from full_amalgam_factual_shadow import (
    DONOR_FILE_SHA, DONOR_PARENT_SHA, EXPECTED_PROBES, JOINT_SHA,
    NATIVE_PARENT_SHA, NATIVE_SHA, STEPS_PER_HEAD, FrozenJoint,
    canonical, digest, original_parents, read_exact, readout,
)


class FakeReadout:
    def __init__(self, probability=0.375):
        self.calls = []
        self.probability = probability

    def specialist_forecasts(self, *inputs):
        self.calls.append(inputs)
        return self.probability, self.probability + 0.1


class Know10Tests(unittest.TestCase):
    def test_original_source_pins_match_archival_parents(self):
        self.assertEqual(NATIVE_PARENT_SHA,
                         'a00119c73a6431172c19b39ec67a1d94b470897a32c55c1c946071793f37dcc4')
        self.assertEqual(DONOR_FILE_SHA,
                         '7e7507af589ae6b08a7599f1abafa9dd998895299fbb423cfc2995ecbcf741cd')
        self.assertEqual(DONOR_PARENT_SHA,
                         'ae83529696b566a12765f16749c258d9ed6addf111da41ef76dc1027938910da')
        self.assertEqual(STEPS_PER_HEAD, 2109)

    def test_frozen_probes_cover_full_160_specialist_readouts(self):
        x = FakeReadout()
        result = readout(x)
        self.assertEqual(result['probes'], EXPECTED_PROBES)
        self.assertEqual(len(x.calls), 80)
        self.assertEqual(result, readout(FakeReadout()))

    def test_changed_specialist_forecast_is_detected(self):
        self.assertNotEqual(readout(FakeReadout(0.375))['readout_sha256'],
                            readout(FakeReadout(0.38))['readout_sha256'])

    def test_rejects_outside_probability_support(self):
        for bad in (-0.1, 1.0, float('nan'), True, 0):
            with self.subTest(bad=bad), self.assertRaisesRegex(
                    ValueError, 'SPECIALIST_READOUT_INVALID'):
                readout(FakeReadout(bad))

    def test_parent_hash_mismatch_and_symlink_fail_closed(self):
        with TemporaryDirectory() as d:
            name = Path(d) / 'native.json'
            name.write_bytes(b'not the parent')
            with self.assertRaisesRegex(ValueError, 'EXTERNAL_PARENT_SHA'):
                read_exact(name, NATIVE_PARENT_SHA, 1 << 20)
            link = Path(d) / 'link.json'
            link.symlink_to(name)
            with self.assertRaisesRegex(ValueError, 'PARENT_MISSING_OR_OVERSIZE'):
                read_exact(link, NATIVE_PARENT_SHA, 1 << 20)

    def test_parent_missing_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'PARENT_MISSING_OR_OVERSIZE'):
            original_parents('/nonexistent/ckad26', '/nonexistent/jepa2')

    def test_oversized_parent_fails_before_parsing(self):
        with TemporaryDirectory() as d:
            name = Path(d) / 'oversized.json'
            name.write_bytes(b'x' * 33)
            with self.assertRaisesRegex(ValueError, 'PARENT_MISSING_OR_OVERSIZE'):
                read_exact(name, NATIVE_PARENT_SHA, 32)

    def test_no_stage_or_training_on_readonly_joint_wrapper(self):
        self.assertFalse(hasattr(FrozenJoint, 'observe_experience'))
        self.assertFalse(hasattr(FrozenJoint, 'stage'))
        self.assertFalse(hasattr(FrozenJoint, 'train'))

    def test_forged_joint_unsupported_without_source(self):
        self.assertNotEqual(digest(canonical({'schema': 'fake'})), JOINT_SHA)
        self.assertNotEqual(digest(canonical({'schema': 'fake'})), NATIVE_SHA)

    def test_structural_bound_does_not_pretend_science(self):
        x = readout(FakeReadout())
        self.assertNotIn('scientific_pass', x)
        self.assertEqual(x['probes'], 160)
        self.assertEqual(len(x['readout_sha256']), 64)


if __name__ == '__main__':
    unittest.main()
