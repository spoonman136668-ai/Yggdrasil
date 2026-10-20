"""NCI-01 bounded Yggdrasil source-only native cell tests."""
import unittest
from nativecognition.developmental import Colony


class TestDevelopmentalCells(unittest.TestCase):
    def test_neighbors_only_and_synchronous_update(self):
        c = Colony(0)
        input_signal = [0.0]*8
        input_signal[0] = 1.0
        first = c.step(input_signal)
        self.assertGreater(first[0], 0)
        self.assertEqual(tuple(first[1:]), (0.0,)*7)
        second = c.step([0.0]*8)
        self.assertGreater(second[1], 0)
        self.assertGreater(second[7], 0)
        self.assertEqual(second[4], 0.0)

    def test_shared_genome_learns_and_frozen_control_does_not(self):
        learned, frozen = Colony(.1), Colony(0)
        start = learned.genome.copy()
        for _ in range(64):
            learned.step([1.0]*8, [.7]*8)
            frozen.step([1.0]*8, [.7]*8)
        self.assertNotEqual(learned.genome, start)
        self.assertEqual(frozen.genome, start)
        self.assertEqual(len(learned.genome), 3)
        self.assertEqual(len(learned.state), 8)

    def test_loss_and_regrowth_uses_only_surviving_context(self):
        c=Colony(0)
        c.step([1.0]*8)
        pre = c.state[3]
        c.lesion(3)
        self.assertFalse(c.alive[3])
        self.assertEqual(c.state[3], 0.0)
        c.step([0.0]*8)
        regrown = c.regrow(3, -.5)
        self.assertNotEqual(regrown, pre)
        self.assertTrue(c.alive[3])
        with self.assertRaises(ValueError):
            c.regrow(3, 0)

    def test_genome_custody_omits_phenotype(self):
        c=Colony(.1)
        c.step([.8]*8, [.2]*8)
        code=c.genome_checkpoint()
        self.assertNotIn(b"state", code)
        self.assertNotIn(b"alive", code)
        recovered=Colony.from_genome(code)
        self.assertEqual(c.genome, recovered.genome)
        self.assertEqual(recovered.state, [0.0]*8)
        self.assertEqual(recovered.alive, [True]*8)

    def test_invalid_input_and_limits_fail_closed(self):
        c=Colony(.1)
        snapshot=(c.state.copy(),c.genome.copy(),c.steps)
        for case in ([0.0]*7,[0.0]*7+[float("nan")],[0.0]*7+[2.0]):
            with self.assertRaises(ValueError):
                c.step(case)
        self.assertEqual(snapshot, (c.state,c.genome,c.steps))
        with self.assertRaises(ValueError):
            c.lesion(8)
        with self.assertRaises(ValueError):
            Colony.from_genome(b'{"version":1,"weights":[4,0,0]}')
        with self.assertRaises(ValueError):
            Colony(-.1)


if __name__ == "__main__":
    unittest.main()
