"""Unexecuted-on-owner-runner integration negatives for bounded SCDR03 quarantine."""
import unittest
from unittest.mock import patch

from num05 import Bank, SOURCE_TAG, public_row
from scdr_num05_spatial_d4 import SpatialSymSCDRNumV3


def fixture(i):
    return public_row(f"{i:064x}", (0.7, 0.7), 0, (0.7, 0.7), 1.0,
                      False, False, source_tag=SOURCE_TAG)


def capacity_state():
    m = SpatialSymSCDRNumV3()
    m.frozen_banks = [Bank() for _ in range(4)]
    m.frozen_sigs = [b.signature() for b in m.frozen_banks]
    m.outer_beliefs = [0.0] * 32 + [1.0]
    m.inner_beliefs = [m._init_inner_matrix(i % 8) for i in range(32)]
    for i in range(4):
        row = fixture(i)
        row["reward"] = 0.0
        m.active_bank.observe(row)
    m.active_events = m.events_seen = 80
    return m


class QuarantineIntegrationTests(unittest.TestCase):
    def test_capacity_rejection_leaves_checkpoint_unchanged(self):
        m = capacity_state()
        before = m.checkpoint_digest()
        with self.assertRaisesRegex(ValueError, "FROZEN_CAPACITY_EXHAUSTED"):
            m.observe(fixture(100))
        self.assertEqual(before, m.checkpoint_digest())

    def test_checkpoint_rejects_excess_pending_and_bad_accounting(self):
        m = capacity_state()
        cp = m.checkpoint()
        cp["quarantine"] = [fixture(i) for i in range(3)]
        cp["consec_contradictions"] = 3
        with self.assertRaisesRegex(ValueError, "ROW_LIMIT"):
            SpatialSymSCDRNumV3.restore(cp)
        cp = m.checkpoint()
        cp["quarantine_unassigned_count"] = 1
        with self.assertRaisesRegex(ValueError, "ACCOUNTING"):
            SpatialSymSCDRNumV3.restore(cp)

    def test_interrupted_pending_has_explicit_disposition(self):
        m = capacity_state()
        m._quarantine = [fixture(100)]
        m.consec_contradictions = 1
        m._account_interrupted_quarantine()
        self.assertEqual(m.quarantine_unassigned_count, 1)
        self.assertFalse(m._quarantine)
        self.assertEqual(m.consec_contradictions, 0)
        restored = SpatialSymSCDRNumV3.restore(m.checkpoint())
        self.assertEqual(restored.checkpoint_digest(), m.checkpoint_digest())

    def test_v1_restore_not_silently_migrated(self):
        m = capacity_state()
        cp = m.checkpoint()
        cp["schema"] = "yggdrasil.scdr_num05_spatial_d4.checkpoint.v1"
        with self.assertRaisesRegex(ValueError, "BAD_CHECKPOINT_SCHEMA"):
            SpatialSymSCDRNumV3.restore(cp)
