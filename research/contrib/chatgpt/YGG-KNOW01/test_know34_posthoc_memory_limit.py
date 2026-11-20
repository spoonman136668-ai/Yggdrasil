"""KNOW34-POSTHOC: deterministic structural memory-limit control, NOT HELD.

This is an after-result mechanism audit of already-frozen KNOW34 source, not
a preregistered scientific trial or independent repetition of its 24 worlds.
No private_witness, proof(), original #426 source, hidden seed, or model owner.

Test claim (narrow): after six observed A returns per physical cell, the
six-slot recency windows contain no B outcomes; the first-six immutable A
Beta heads cannot encode a learned B posterior. On this deterministic mock,
the end-of-return readout is identical to never having visited B, even when
local evidence briefly detected B. This does NOT prove all possible hidden
states or prior history are identical, nor that a conventional HMM is beaten.
"""
import unittest

from know34_local_contradiction_dev import (
    GuardedCells, cold, private_law_bit, public_tape,
)


class Know34PosthocMemoryLimit(unittest.TestCase):
    def test_deterministic_a_b_a_loses_functional_b_recall(self):
        for kind in ("local", "rewired"):
            with self.subTest(topology=kind):
                a_only = GuardedCells(kind)
                a_b_a = GuardedCells(kind)
                post_prefix_slow = None
                witnessed_differences = 0
                for t in range(192):
                    _c, _a, x = public_tape(t)
                    old = private_law_bit("A", x)
                    new = private_law_bit("B1", x)
                    if 64 <= t < 128 and old != new:
                        witnessed_differences += 1
                    a_only.observe(t, x, old)
                    a_b_a.observe(t, x,
                                  new if 64 <= t < 128 else old)
                    if t == 63:
                        post_prefix_slow = a_b_a.slow_sha()

                # The private B law REALLY altered the public consequences.
                self.assertGreater(witnessed_differences, 0)
                self.assertEqual((a_only.received, a_b_a.received),
                                 (192, 192))
                # Live slow weights never learned B; this is freeze-by-design.
                self.assertEqual(a_b_a.slow_sha(), post_prefix_slow)
                self.assertEqual(a_only.slow_sha(), a_b_a.slow_sha())
                # Each input is visited eight times on return: its six-slot
                # window now contains ONLY A observations, not learned B.
                self.assertEqual([len(w) for w in a_b_a.windows], [6] * 8)
                self.assertEqual(a_only.windows, a_b_a.windows)
                self.assertTrue(all(
                    a_b_a.windows[x] == [private_law_bit("A", x)] * 6
                    for x in range(8)))
                # In this explicitly deterministic mock, both local topologies
                # return to slow mode, erasing functional evidence of B.
                self.assertEqual(a_only.mode, ["slow"] * 4)
                self.assertEqual(a_b_a.mode, ["slow"] * 4)
                self.assertGreater(a_b_a.fast_switches, 0)
                self.assertEqual(a_only.fast_switches, 0)
                self.assertEqual(
                    [a_only.prob(x) for x in range(8)],
                    [a_b_a.prob(x) for x in range(8)])
                self.assertEqual(
                    [cold(a_b_a).prob(x) for x in range(8)],
                    [a_b_a.prob(x) for x in range(8)])


if __name__ == "__main__":
    unittest.main()
