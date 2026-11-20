"""Fabricated public tuples only, no original worlds, scientific seeds or outcomes."""
import unittest

from protocol_guard import (AuditError, assert_cold_functional_retention,
                            assert_paired_evidence, public_tape_digest)


class ProtocolGuardTests(unittest.TestCase):
    def setUp(self):
        self.tape = [
            {"observation": 0, "action": 0, "outcome": 1},
            {"observation": 1, "action": 1, "outcome": 0},
        ]

    def test_identical_arm_evidence(self):
        a = assert_paired_evidence({"candidate": self.tape,
                                    "HMM": [dict(x) for x in self.tape]},
                                   ("candidate", "HMM"), max_witnesses=2)
        self.assertEqual(a["witnesses_per_arm"], 2)
        self.assertFalse(a["scientific_gain_verified"])
        self.assertFalse(a["source_custody_authenticated"])

    def test_digest_determinism(self):
        self.assertEqual(public_tape_digest(self.tape), public_tape_digest(self.tape))

    def test_hidden_phase_rejected(self):
        tape = [dict(self.tape[0], phase="A")]
        with self.assertRaisesRegex(AuditError, "NONPUBLIC"):
            public_tape_digest(tape)

    def test_oracle_counterfactual_rejected(self):
        for key in ("source_id", "counterfactual", "oracle", "reset"):
            with self.subTest(key=key), self.assertRaises(AuditError):
                public_tape_digest([dict(self.tape[0], **{key: 1})])

    def test_unmatched_tapes_rejected(self):
        modified = [dict(self.tape[0]), dict(self.tape[1], outcome=1)]
        with self.assertRaisesRegex(AuditError, "UNMATCHED"):
            assert_paired_evidence({"candidate": self.tape, "HMM": modified},
                                   ("candidate", "HMM"), max_witnesses=2)

    def test_budget_rejected(self):
        with self.assertRaisesRegex(AuditError, "BUDGET"):
            assert_paired_evidence({"candidate": self.tape},
                                   ("candidate",), max_witnesses=1)

    def test_missing_arm_rejected(self):
        with self.assertRaisesRegex(AuditError, "ARM_CONTRACT"):
            assert_paired_evidence({"candidate": self.tape},
                                   ("candidate", "HMM"), max_witnesses=2)

    def test_floats_and_bools_rejected(self):
        for altered in ({"observation": 1.0}, {"action": True}, {"outcome": -1}):
            with self.subTest(altered=altered), self.assertRaises(AuditError):
                public_tape_digest([dict(self.tape[0], **altered)])

    def test_empty_tape_rejected(self):
        with self.assertRaises(AuditError):
            public_tape_digest([])

    def test_cold_retention_pass(self):
        self.assertAlmostEqual(assert_cold_functional_retention(
            {0: 0.8, 1: 0.15}, {0: 0.805, 1: 0.148}), 0.005)

    def test_cold_retention_drift_rejected(self):
        with self.assertRaisesRegex(AuditError, "DRIFT"):
            assert_cold_functional_retention({0: 0.8}, {0: 0.5})

    def test_cold_query_mismatch_rejected(self):
        with self.assertRaisesRegex(AuditError, "QUERY_SET"):
            assert_cold_functional_retention({0: 0.8}, {1: 0.8})


if __name__ == "__main__":
    unittest.main()
