#!/usr/bin/env python3
"""Offline unit tests only; never invoke F84 diagnostic source cohorts."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location(
    "f84_exposed_reachability",
    Path(__file__).with_name("forensic_reachability.py"),
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FrozenCodecContractDouble:
    """Test double for the exact 12-byte record shape; not qualification."""
    def pack(self, start, end, codes):
        if not 1 <= len(codes) <= 6:
            raise ValueError("wrong length")
        encoded = sum(c << (3 * i) for i, c in enumerate(codes))
        return struct.pack("<II", start, end) + encoded.to_bytes(
            3, "little"
        ) + bytes((len(codes),))

    def unpack(self, payload):
        assert len(payload) == 12
        start, end = struct.unpack("<II", payload[:8])
        n = payload[-1]
        encoded = int.from_bytes(payload[8:11], "little")
        return (start, end, tuple((encoded >> (3 * i)) & 7 for i in range(n)))

    def solve(self, records, question):
        at = question["start"]
        remaining = tuple(
            2 * role + int(direction == -1) for role, direction in question["ops"]
        )
        for a, b, codes in records:
            if a == at and codes == remaining:
                return b
        return None


class ReachabilityUnitTests(unittest.TestCase):
    def source(self):
        path = [
            (100, 0, 101), (102, 1, 101), (102, 2, 103),
            (104, 3, 103), (104, 0, 105), (106, 1, 105),
        ]
        noise = [(1000 + 2 * i, i % 4, 1001 + 2 * i) for i in range(66)]
        self.assertEqual(len(set(path + noise)), 72)
        return tuple(path + noise)

    def question(self):
        return dict(start=100, answer=106, ops=(
            (0, 1), (1, -1), (2, 1),
            (3, -1), (0, 1), (1, -1)
        ))

    def test_independent_directed_six_step_witness(self):
        answers, counts = module.independently_resolve_public(
            self.source(), self.question())
        self.assertEqual(answers, {106})
        self.assertEqual(counts, [1] * 7)

    def test_reversed_edge_in_question_fails(self):
        q = self.question()
        q["ops"] = ((0, -1),) + q["ops"][1:]
        answers, counts = module.independently_resolve_public(self.source(), q)
        self.assertEqual(answers, set())
        self.assertEqual(counts[-1], 0)

    def test_query_aware_codec_ceiling_is_one_12_byte_record(self):
        q = self.question()
        record = module.hindsight_encoded_path(q, FrozenCodecContractDouble())
        self.assertEqual(record[0:2], (100, 106))
        self.assertEqual(len(record[2]), 6)

    def test_invalid_path_codec_capacity_rejected(self):
        q = self.question()
        q["ops"] += ((2, 1),)
        with self.assertRaises(AssertionError):
            module.hindsight_encoded_path(q, FrozenCodecContractDouble())

    def test_public_source_must_contain_exactly_72_unique_events(self):
        source = list(self.source())
        source[-1] = source[0]
        with self.assertRaises(AssertionError):
            module.independently_resolve_public(tuple(source), self.question())


if __name__ == "__main__":
    unittest.main()
