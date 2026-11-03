"""G39 synthetic-only retention and interpolation checks. NOT transfer science."""
import hashlib
import math
import struct
import unittest
from native_dg1a import DG1APrototype, SharedGenome, seeded_genome, GENOME_PARAMETER_COUNT
from g38_native_learning import run_development, action, score

PARTS = ("first", "first_bias", "second", "second_bias")
CUES = (-1.0, -0.5, -0.1, 0.1, 0.5, 1.0)

def freeze_genome(genome):
    values = tuple(v for part in PARTS for v in getattr(genome, part))
    if len(values) != GENOME_PARAMETER_COUNT or any(not math.isfinite(v) for v in values):
        raise ValueError("YGG_G39_INVALID_GENOME")
    return struct.pack("<" + "d" * len(values), *values)

def restore_genome(blob):
    if type(blob) is not bytes or len(blob) != 8 * GENOME_PARAMETER_COUNT:
        raise ValueError("YGG_G39_INVALID_BYTES")
    values = struct.unpack("<" + "d" * GENOME_PARAMETER_COUNT, blob)
    lengths = tuple(len(getattr(seeded_genome(17), part)) for part in PARTS)
    pos, parts = 0, []
    for length in lengths:
        parts.append(tuple(values[pos:pos + length]))
        pos += length
    return SharedGenome(*parts)

class G39RetentionDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = DG1APrototype()
        cls.results = {c: run_development(c) for c in
                       ("mapped", "reversed", "sham", "no_feedback")}

    def test_retention_exact_round_trip_and_fresh_instance_parity(self):
        for condition, result in self.results.items():
            with self.subTest(condition=condition):
                blob = freeze_genome(result.genome)
                restored = restore_genome(blob)
                self.assertEqual(restored, result.genome)
                self.assertEqual(freeze_genome(restored), blob)
                self.assertEqual(len(blob), 8 * GENOME_PARAMETER_COUNT)
                self.assertEqual(len(hashlib.sha256(blob).hexdigest()), 64)
                self.assertEqual([action(DG1APrototype(), restored, cue) for cue in CUES],
                                 [action(self.model, result.genome, cue) for cue in CUES])

    def test_invalid_serialization_fail_closed(self):
        for invalid in (b"", b"zero", bytes(8 * GENOME_PARAMETER_COUNT - 8), None):
            with self.subTest(value=type(invalid).__name__):
                with self.assertRaises(ValueError):
                    restore_genome(invalid)

    def test_interpolation_and_no_adaptation_reversal_not_transfer(self):
        for condition, result in self.results.items():
            with self.subTest(condition=condition):
                genome = restore_genome(freeze_genome(result.genome))
                expanded = score(self.model, genome, CUES)
                reversed_rule = sum(action(self.model, genome, cue) ==
                                    (-1 if cue > 0 else 1) for cue in CUES) / len(CUES)
                self.assertAlmostEqual(expanded + reversed_rule, 1.0)
                self.assertIn(expanded, tuple(i / len(CUES) for i in range(len(CUES) + 1)))

    def test_no_feedback_no_weight_change(self):
        self.assertEqual(self.results["no_feedback"].genome, seeded_genome(17))

if __name__ == "__main__":
    unittest.main()
