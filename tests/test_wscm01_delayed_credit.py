"""WSCM-01 ring: bounded delayed-credit proposals only, no native writes."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import random
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          'research/contrib/chatgpt/CAUSAL-AMALGAM/wscm01_delayed_credit.py')
SPEC = spec_from_file_location('wscm01_delayed_credit', SOURCE)
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DelayedCreditTests(unittest.TestCase):
    def test_surprise_gates_retrospective_proposals(self):
        ring = MODULE.DelayedCreditRing()
        for i in range(4):
            ring.stage(i, 100+i, 0, candidate_role=i)
        rows = ring.reveal(3, 21, 1, charged=True, controlled=True)
        self.assertEqual(len(rows), 4)
        self.assertEqual([r[2] for r in rows], [3, 2, 1, 0])
        self.assertEqual([r[3] for r in rows], [4096, 8192, 16384, 32768])
        self.assertTrue(all(r[4] == 256 for r in rows))
        self.assertEqual(ring.reveal(3, 21, 1, charged=True, controlled=True), rows)

    def test_nonsurprising_outcome_creates_no_credit(self):
        ring = MODULE.DelayedCreditRing().stage(1, 9, 192)
        self.assertEqual(ring.reveal(1, 19, 1, charged=True, controlled=True), ())
        self.assertEqual(ring.snapshot()[3][0][3], ())

    def test_hard_capacity_expires_old_events_and_proposals(self):
        ring = MODULE.DelayedCreditRing()
        for i in range(17):
            ring.stage(i, i+5, 0)
        self.assertEqual(len(ring.snapshot()[2]), 16)
        with self.assertRaisesRegex(ValueError, 'WSCM_TARGET_EXPIRED_OR_UNKNOWN'):
            ring.reveal(0, 19, 1, charged=True, controlled=True)
        self.assertEqual(len(ring.reveal(16, 20, 1, charged=True, controlled=True)), 16)
        for i in range(17, 30):
            ring.stage(i, i, 0)
        self.assertEqual(len(ring.snapshot()[2]), 16)
        self.assertTrue(len(ring.snapshot()[3]) <= 16)

    def test_cold_restore_remains_exact_after_ring_wrap(self):
        ring = MODULE.DelayedCreditRing()
        for i in range(16):
            ring.stage(i, i, 0)
        ring.reveal(15, 16, 1, charged=True, controlled=True)
        self.assertEqual(len(ring.snapshot()[3][0][3]), 16)
        ring.stage(16, 16, 0)  # evicts first credited entry
        self.assertEqual(ring.snapshot()[3], ())
        self.assertEqual(MODULE.DelayedCreditRing.restore(ring.snapshot()).snapshot(),
                         ring.snapshot())
        with self.assertRaisesRegex(ValueError, 'WSCM_OUTCOME_REORDER'):
            ring.reveal(15, 16, 1, charged=True, controlled=True)
        for i in range(17, 40):
            ring.stage(i, i, 0)
            self.assertEqual(MODULE.DelayedCreditRing.restore(ring.snapshot()).snapshot(),
                             ring.snapshot())

    def test_source_claims_cannot_skip_validation(self):
        ring = MODULE.DelayedCreditRing().stage(4, 2, 0)
        before = ring.snapshot()
        for flags in ((False, True), (True, False)):
            with self.assertRaisesRegex(ValueError, 'WSCM_SOURCE_AUTHORITY_ABSENT'):
                ring.reveal(4, 5, 1, charged=flags[0], controlled=flags[1])
        self.assertEqual(ring.snapshot(), before)

    def test_receipt_conflicts_and_reordering_fail_closed(self):
        ring = MODULE.DelayedCreditRing().stage(10, 3, 0)
        ring.stage(10, 3, 0)
        with self.assertRaisesRegex(ValueError, 'WSCM_EVENT_REPLAY_OR_REORDER'):
            ring.stage(10, 4, 0)
        with self.assertRaisesRegex(ValueError, 'WSCM_EVENT_REPLAY_OR_REORDER'):
            ring.stage(9, 3, 0)
        ring.reveal(10, 5, 1, charged=True, controlled=True)
        with self.assertRaisesRegex(ValueError, 'WSCM_CONFLICTING_REVEAL'):
            ring.reveal(10, 5, 0, charged=True, controlled=True)
        ring.stage(11, 3, 0)
        with self.assertRaisesRegex(ValueError, 'WSCM_OUTCOME_REORDER'):
            ring.reveal(11, 4, 1, charged=True, controlled=True)

    def test_cold_replay_exact_and_untrusted_forgery_rejected(self):
        ring = MODULE.DelayedCreditRing()
        for i in range(7):
            ring.stage(i, i, 64, candidate_role=i)
        ring.reveal(4, 22, 1, charged=True, controlled=True)
        snap = ring.snapshot()
        recovered = MODULE.DelayedCreditRing.restore(snap)
        self.assertEqual(recovered.snapshot(), snap)
        last_event, last_outcome, events, reveals = snap
        forged = (last_event, last_outcome, events,
                  ((4, 22, 1, ((999, None, 0, 1, 42),)),))
        with self.assertRaisesRegex(ValueError, 'WSCM_SNAPSHOT_PROPOSALS'):
            MODULE.DelayedCreditRing.restore(forged)

    def test_snapshot_caps_and_canonical_order(self):
        ring = MODULE.DelayedCreditRing().stage(2, 3, 0)
        with self.assertRaisesRegex(ValueError, 'WSCM_SNAPSHOT_EVENT_ID'):
            MODULE.DelayedCreditRing.restore((10, -1, ring.snapshot()[2], ()))
        with self.assertRaisesRegex(ValueError, 'WSCM_SNAPSHOT_CAPACITY'):
            MODULE.DelayedCreditRing.restore((-1, -1, ((),)*17, ()))

    def test_seven_deterministic_streams_replay_exactly_through_wraps(self):
        for seed in (1, 2, 3, 4, 5, 11, 37):
            rng = random.Random(seed)
            ring = MODULE.DelayedCreditRing()
            outcome_id = 100000
            for i in range(300):
                candidate = rng.randrange(0, 16) if rng.randrange(2) == 0 else None
                ring.stage(i, rng.randrange(0, 64), rng.randrange(0, 257),
                           candidate_role=candidate)
                eligible = ({row[0] for row in ring._events}
                            - {row[0] for row in ring._reveals})
                if eligible and rng.random() < 0.66:
                    outcome_id += 1
                    ring.reveal(rng.choice(sorted(eligible)), outcome_id,
                                rng.randrange(0, 2), charged=True, controlled=True)
                snap = ring.snapshot()
                self.assertEqual(MODULE.DelayedCreditRing.restore(snap).snapshot(), snap)
                self.assertLessEqual(len(ring._events), MODULE.WINDOW)
                self.assertLessEqual(len(ring._reveals), MODULE.WINDOW)

    def test_invalid_types_and_capacity_fail_closed(self):
        ring = MODULE.DelayedCreditRing()
        with self.assertRaises(ValueError):
            ring.stage(True, 1, 256)
        with self.assertRaises(ValueError):
            ring.stage(1, 1, 257)
        with self.assertRaises(ValueError):
            ring.stage(1, 1, 100, candidate_role=16)
        self.assertEqual(ring.snapshot(), (-1, -1, (), ()))


if __name__ == '__main__':
    unittest.main()
