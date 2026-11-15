"""ST2 source-free public-byte mechanics; fixtures are NOT MiniGrid science.

No original environments, reset seeds, protected cohorts, networking,
controller, scheduler or new learned original S1 coefficients are consumed.
"""
import json
import unittest

from research.nci04_s1.local_messages import LocalPredictiveMessages45
from research.nci04_st2.event_memory import (
    EventGroundedMemory45, canonical, correspondences, cross_position_headroom
)


def frame(position, duplicate=None):
    raw = [0] * 24
    for i in (position, duplicate):
        if i is not None:
            raw[3*i:3*i+3] = [11, 12, 13]
    return tuple(raw)


def public_changes(before, after):
    return tuple(int(before[3*i:3*i+3] != after[3*i:3*i+3])
                 for i in range(8))


class ST2SourceFreeFixtures(unittest.TestCase):
    def setUp(self):
        self.m = EventGroundedMemory45(LocalPredictiveMessages45().snapshot())
        self.bits = (0,) * 8
        self.weights = self.m.native.runtime.core.snapshot()

    def move(self, before, after, *, train=True):
        return self.m.observe(
            before, self.bits, 0, public_changes(before, after), after,
            train=train
        )

    def test_unique_cross_position_only_and_no_future_frame_lookup(self):
        self.assertEqual(correspondences(None, frame(0)), (None,) * 8)
        pairs = correspondences(frame(0), frame(1))
        self.assertEqual(pairs[1], ((11, 12, 13), 0))
        self.assertEqual(sum(p is not None for p in pairs), 1)
        self.assertEqual(cross_position_headroom(frame(0), frame(1)), 1)
        self.assertEqual(cross_position_headroom(frame(0), frame(0)), 0)
        self.assertTrue(all(x is None for x in correspondences(
            frame(0, 1), frame(2)
        )))
        self.assertTrue(all(x is None for x in correspondences(
            frame(0), frame(1, 2)
        )))
        self.assertEqual(correspondences((0,) * 24, (0,) * 24),
                         (None,) * 8)

    def test_new_state_requires_four_authentic_shaped_consequences(self):
        x, y = frame(0), frame(1)
        initial = self.m.predict(x, self.bits, 0)
        self.assertEqual(initial, self.m.native.predict(x, self.bits, 0))
        self.move(x, y)
        # Previous observation is x, and y matches it, but no counts yet.
        self.assertEqual(self.m.predict(y, self.bits, 0),
                         self.m.native.predict(y, self.bits, 0))
        for step in range(4):
            current, following = (y, x) if step % 2 == 0 else (x, y)
            self.move(current, following)
            self.assertEqual(self.m.native.runtime.core.snapshot(),
                             self.weights)
        self.assertEqual(self.m.accounting()["tracked_signatures"], 1)
        self.assertEqual(sum(self.m.counts[0][0]), 4)
        predicted = self.m.predict(y, self.bits, 0)
        original = self.m.native.predict(y, self.bits, 0)
        self.assertAlmostEqual(
            predicted[1], 0.5 * original[1] + 0.5 * (5.0 / 6.0)
        )
        for i in range(8):
            if i != 1:
                self.assertEqual(predicted[i], original[i])
        self.assertEqual(self.m.accounting()["persistent_uint16_counter_bytes"],
                         192)
        self.assertEqual(self.m.accounting()["reserved_public_signature_bytes"],
                         24)
        self.assertFalse(self.m.accounting()["scientific_first_use_qualified"])

    def test_duplicate_appearance_forces_unknown_and_no_training(self):
        a, b, c = frame(0), frame(1, 2), frame(3)
        self.move(a, b)
        self.assertEqual(self.m.predict(b, self.bits, 0),
                         self.m.native.predict(b, self.bits, 0))
        self.move(b, c)
        self.assertEqual(self.m.labels, [None] * 8)
        self.assertTrue(all(pair == [0, 0]
                            for row in self.m.counts for pair in row))

    def test_episode_reset_retains_memory_not_correspondence(self):
        a, b = frame(0), frame(1)
        self.move(a, b)
        self.move(b, a)
        checkpoint = self.m.snapshot()
        self.assertEqual(EventGroundedMemory45.restore(checkpoint).snapshot(),
                         checkpoint)
        previous_counts = json.loads(checkpoint)["counts"]
        self.m.reset_episode()
        self.assertEqual(self.m.previous_raw, None)
        self.assertEqual(self.m.counts, previous_counts)
        self.assertEqual(self.m.predict(a, self.bits, 0),
                         self.m.native.predict(a, self.bits, 0))
        self.assertEqual(self.m.native.runtime.core.snapshot(), self.weights)

    def test_train_false_never_changes_learned_counters_or_age(self):
        a, b = frame(0), frame(1)
        self.move(a, b)
        self.move(b, a)
        before = (json.loads(self.m.snapshot())["counts"],
                  self.m.clock, self.m.last_used[:])
        self.move(a, b, train=False)
        after = (json.loads(self.m.snapshot())["counts"],
                 self.m.clock, self.m.last_used[:])
        self.assertEqual(before, after)

    def test_uint16_overflow_halves_both_before_increment(self):
        a, b = frame(0), frame(1)
        self.move(a, b)
        self.move(b, a)
        slot = self.m.labels.index((11, 12, 13))
        self.m.counts[slot][0] = [0, 65535]
        self.move(a, b)
        self.assertEqual(self.m.counts[slot][0], [1, 32767])

    def test_invalid_public_source_claims_and_checkpoint_are_fail_closed(self):
        a, b = frame(0), frame(1)
        self.move(a, b)
        snap = self.m.snapshot()
        for f in (
            lambda: self.m.observe(a, self.bits, 0, (0,)*8, b),
            lambda: self.m.observe(a[:-1], self.bits, 0,
                                   public_changes(a, b), b),
            lambda: self.m.observe(a, self.bits, 6,
                                   public_changes(a, b), b),
            lambda: self.m.observe(a, self.bits, 0,
                                   public_changes(a, b), b, train=1),
            lambda: self.m.predict(a, self.bits[:-1], 0),
        ):
            with self.assertRaises(ValueError):
                f()
            self.assertEqual(self.m.snapshot(), snap)
        for mutate in (
            lambda d: d.update(schema="corrupted"),
            lambda d: d["counts"][0][0].__setitem__(0, -1),
            lambda d: d["counts"][0][0].__setitem__(1, 65536),
            lambda d: d["counts"][0][0].__setitem__(0, True),
            lambda d: d.update(weights_sha256="0" * 64),
            lambda d: d["labels"].__setitem__(1, [0, 0, 0]),
        ):
            data = json.loads(snap)
            mutate(data)
            with self.assertRaises(ValueError):
                EventGroundedMemory45.restore(canonical(data))
        with self.assertRaises(ValueError):
            EventGroundedMemory45.restore('{"schema":"oops"}')


if __name__ == "__main__":
    unittest.main()
