"""NCI-04G3 focused engineering tests. No protected scientific outcomes."""
import unittest
from yggdrasil.nci04g_local_reconstruction import LocalReconstructor, N, PER_CELL

def evidence_pattern(n):
    return [(n>>i)&1 for i in range(N)]

class LearnedLocalReconstructionFocused(unittest.TestCase):
    def test_select_informative_surviving_neighbor_without_labels(self):
        model=LocalReconstructor()
        for n in range(128):
            bits=evidence_pattern(n)
            outcomes=[bits[(i-1)%N] for i in range(N)]
            model.observe_prelesion(bits,outcomes)
        self.assertEqual(model.prelesion_events,128)
        self.assertEqual(sum(len(x) for x in model.cells),N*PER_CELL)
        frozen=model.snapshot()
        self.assertEqual(LocalReconstructor.restore(frozen).snapshot(),frozen)
        model.lesion([0])
        before=model.snapshot()
        with self.assertRaises(ValueError):
            model.observe_prelesion(evidence_pattern(77),[0]*N)
        self.assertEqual(before,model.snapshot())
        for x in (21,33,81,106):
            bits=evidence_pattern(x)
            output,known=model.reconstruct(bits,0)
            self.assertTrue(known)
            self.assertEqual(output,bits[7]) # this target depends only on surviving neighbor 7
        self.assertTrue(all(not any(model.cells[i]) for i in model.damaged))
        self.assertEqual(LocalReconstructor.restore(model.snapshot()).snapshot(),model.snapshot())

    def test_impossible_information_abstains_and_restart_is_stable(self):
        m=LocalReconstructor()
        for n in range(128):
            bits=evidence_pattern(n)
            targets=[bits[(i-1)%N] for i in range(N)]
            targets[0]=bits[4] # neither immediate neighbor 7 nor 1 is informative
            m.observe_prelesion(bits,targets)
        m.lesion([0])
        output,known=m.reconstruct(evidence_pattern(93),0)
        self.assertIsNone(output)
        self.assertFalse(known)
        restored=LocalReconstructor.restore(m.snapshot())
        self.assertEqual(restored.reconstruct(evidence_pattern(63),0),(None,False))

    def test_negative_input_and_counter_budget_fail_closed(self):
        m=LocalReconstructor()
        before=m.snapshot()
        with self.assertRaises(ValueError):m.observe_prelesion([0]*N,[0]*(N-1))
        with self.assertRaises(ValueError):m.reconstruct([0]*N,0)
        with self.assertRaises(ValueError):m.lesion([0,0])
        self.assertEqual(before,m.snapshot())
        for i in range(128):m.observe_prelesion(evidence_pattern(i),[0]*N)
        before=m.snapshot()
        with self.assertRaises(ValueError):m.observe_prelesion(evidence_pattern(1),[0]*N)
        self.assertEqual(before,m.snapshot())

if __name__=="__main__":
    unittest.main()
