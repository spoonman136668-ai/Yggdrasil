"""Source-free tests; no reserved seeds or learner/source execution."""
import unittest
from scdr_num05_quarantine import (
    ZERO_DIGEST, account_unassigned, checked_rows, stage_row, validate_accounting,
)


def normalize(row):
    if type(row) is not dict or set(row) != {"id", "observation"}:
        raise ValueError("FIXTURE_ROW")
    return {"id": row["id"], "observation": list(row["observation"])}


def row(i):
    return {"id": str(i), "observation": [0.5, 0.5]}


class QuarantinePolicyTests(unittest.TestCase):
    def test_capacity_rejects_10000_without_mutation(self):
        pending = [row(0)]
        for i in range(1, 10001):
            with self.assertRaisesRegex(ValueError, "FROZEN_CAPACITY_EXHAUSTED"):
                stage_row(pending, row(i), normalize, frozen_count=4, max_frozen=4)
        self.assertEqual(pending, [row(0)])

    def test_third_row_can_stage_but_not_persist(self):
        pending = stage_row([row(0), row(1)], row(2), normalize,
                            frozen_count=3, max_frozen=4)
        self.assertEqual(len(pending), 3)
        with self.assertRaisesRegex(ValueError, "ROW_LIMIT"):
            checked_rows(pending, normalize)
        with self.assertRaisesRegex(ValueError, "ROW_LIMIT"):
            stage_row(pending, row(3), normalize, frozen_count=3, max_frozen=4)

    def test_copy_duplicate_and_malformed(self):
        original = row(0)
        pending = checked_rows([original], normalize)
        original["observation"][0] = 9
        self.assertEqual(pending, [row(0)])
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            checked_rows([row(0), row(0)], normalize)
        with self.assertRaisesRegex(ValueError, "FIXTURE_ROW"):
            checked_rows([{"id": "0", "observation": [], "extra": True}], normalize)

    def test_byte_bound(self):
        with self.assertRaisesRegex(ValueError, "BYTE_LIMIT"):
            checked_rows([{"id": "0", "observation": [0] * 5000}], normalize)

    def test_unassigned_accounting_and_restore_validation(self):
        count, head = account_unassigned([row(0), row(1)], 0, ZERO_DIGEST)
        self.assertEqual(count, 2)
        self.assertEqual((count, head), account_unassigned([row(0), row(1)], 0, ZERO_DIGEST))
        self.assertNotEqual(head, account_unassigned([row(1), row(0)], 0, ZERO_DIGEST)[1])
        validate_accounting(count, head, 2)
        for args in [(3, head, 2), (0, head, 2), (1, ZERO_DIGEST, 2), (1, "x", 2)]:
            with self.assertRaisesRegex(ValueError, "ACCOUNTING"):
                validate_accounting(*args)


if __name__ == "__main__":
    unittest.main()
