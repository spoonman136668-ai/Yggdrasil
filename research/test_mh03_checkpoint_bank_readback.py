"""MH03 independent, outcome-free mechanical parity and negative checkpoint controls."""
import hashlib
import math
import struct
import unittest

from research import mh03_checkpoint_bank_readback as mh
from research import itd02_v32e_pair_consensus_audit as native


def fixture():
    """Manufactured legal checkpoint: no training, simulated reward or new source."""
    b = bytearray(mh.MAGIC + struct.pack("<Q", 2))
    for i in range(8):
        b += struct.pack("<8Q", 2, i % 2, 2, 0, 0, 0, 0, 0)
        b += bytes(24)
        weights = []
        for bank in range(2):
            for action in range(3):
                for cue in range(4):
                    v = (i + 1) * (action + 1) * (cue + 1) / 1000.0
                    weights.append(v if bank == 0 else -v * 1.1)
        b += struct.pack("<24d", *weights)
    assert len(b) == mh.SIZE - 8, len(b)
    b += struct.pack("<Q", mh.fnv64(b))
    return bytes(b)


def altered(data, offset, encoded):
    b = bytearray(data)
    b[offset:offset + len(encoded)] = encoded
    b[-8:] = struct.pack("<Q", mh.fnv64(b[:-8]))
    return bytes(b)


class MH03CheckpointBankTests(unittest.TestCase):
    def test_original_source_and_fixture_custody(self):
        native.original_source_guard()
        self.assertEqual(native.API.source_sha256,
                         hashlib.sha256(mh.SOURCE.read_bytes()).hexdigest())
        self.assertEqual(native.API.size(), mh.SIZE)
        snap = fixture()
        state = mh.parse_checkpoint(snap)
        self.assertEqual(len(state["cells"]), 8)
        self.assertEqual(state["update_calls"], 2)
        self.assertEqual(tuple(c["active"] for c in state["cells"]),
                         (0, 1, 0, 1, 0, 1, 0, 1))
        self.assertEqual(mh.fnv64(snap[:-8]),
                         struct.unpack("<Q", snap[-8:])[0])

    def test_original_native_score_parity_for_all_bank_modes(self):
        start = fixture()
        report = mh.inspect_snapshot(start)
        self.assertTrue(report["forced_bank_readouts_are_evaluator_only"])
        self.assertFalse(report["scientific_gain_verified"])
        self.assertNotEqual(report["readouts"]["forced_bank0"],
                            report["readouts"]["forced_bank1"])
        for mode in ("active", "forced_bank0", "forced_bank1"):
            if mode == "active":
                snap = start
            else:
                chosen = 0 if mode == "forced_bank0" else 1
                snap = start
                for i in range(8):
                    snap = altered(snap, 16 + 280 * i + 8, struct.pack("<Q", chosen))
            h = native.API.new()
            try:
                native.API.layout(h)
                self.assertEqual(native.API.restore(h, snap), 0)
                self.assertEqual(native.API.checkpoint(h), snap)
                for cue in range(4):
                    native.API.observe_one(h, cue)
                    actual = native.API.native_scores(h)
                    expected = report["readouts"][mode][cue]
                    for a in range(3):
                        self.assertLessEqual(abs(actual[a] - expected[a]), 1e-12,
                                             (mode, cue, a, actual[a], expected[a]))
                self.assertEqual(native.API.checkpoint(h), snap)
            finally:
                native.API.free(h)
        self.assertEqual(fixture(), start)  # no mutation of test source

    def test_reject_invalid_size_magic_checksum_and_non_bytes(self):
        snap = fixture()
        for bad in (snap[:-1], snap + b"\0", bytearray(snap),
                    bytes([snap[0] ^ 1]) + snap[1:],
                    snap[:51] + bytes([snap[51] ^ 1]) + snap[52:]):
            with self.assertRaises(ValueError):
                mh.parse_checkpoint(bad)

    def test_reject_internally_resealed_corruption(self):
        snap = fixture()
        offsets = [
            (16 + 8, struct.pack("<Q", 2)),      # active bank index
            (16 + 16, struct.pack("<Q", 3)),     # age sum != local updates
            (16 + 40, struct.pack("<Q", 37)),    # evidence window too long
            (16 + 64, bytes([4])),               # bad per-pair streak
            (16 + 64 + 12, bytes([1])),          # certified count mismatch
            (16 + 88, struct.pack("<d", math.nan)),    # NaN weight
            (16 + 88, struct.pack("<d", math.inf)),    # infinity
            (16 + 88, struct.pack("<d", 8.1)),         # out of bound
        ]
        for at, value in offsets:
            with self.subTest(offset=at, value=value):
                with self.assertRaises(ValueError):
                    mh.parse_checkpoint(altered(snap, at, value))

    def test_reject_invalid_cue_and_oracle_bank(self):
        state = mh.parse_checkpoint(fixture())
        for cue in (-1, 4, True, "0"):
            with self.assertRaises(ValueError):
                mh.scores(state, cue)
        for bank in (-1, 2, True, "0"):
            with self.assertRaises(ValueError):
                mh.scores(state, 0, bank)


if __name__ == "__main__":
    unittest.main()
