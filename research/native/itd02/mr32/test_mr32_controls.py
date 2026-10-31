import unittest
from residual_belief import ACTIVE_SLOTS, RETAINED_SLOTS, TOTAL_SLOTS
from mr32_controls import MemorylessMean, ConventionalPrototypeControl


def xvec(i):
    return tuple(1.0 if j == i % 16 else 0.0 for j in range(16))

def yvec(i):
    return tuple(1.0 if j == i % 8 else 0.0 for j in range(8))


class ControlTests(unittest.TestCase):
    def test_memoryless_control_has_no_input_conditioned_state(self):
        c=MemorylessMean()
        p1=c.predict(xvec(0), 0); c.observe_selected_outcome(yvec(0))
        p2=c.predict(xvec(13), 1); c.observe_selected_outcome(yvec(1))
        self.assertEqual(p2.values,tuple(v/1 for v in yvec(0)))

    def test_conventional_control_has_same_slot_count_and_partition(self):
        c=ConventionalPrototypeControl()
        for i in range(40):
            c.predict(xvec(i), i % 3); c.observe_selected_outcome(yvec(i))
        self.assertEqual(len(c.slots),TOTAL_SLOTS)
        self.assertEqual(sum(s.active for s in c.slots),ACTIVE_SLOTS)
        self.assertEqual(sum(not s.active for s in c.slots),RETAINED_SLOTS)

    def test_controls_require_selected_feedback(self):
        c=ConventionalPrototypeControl()
        with self.assertRaisesRegex(RuntimeError,"NO_PENDING"):
            c.observe_selected_outcome(yvec(0))
        c.predict(xvec(0), 0); c.observe_selected_outcome(yvec(0))
        with self.assertRaisesRegex(RuntimeError,"NO_PENDING"):
            c.observe_selected_outcome(yvec(1))

    def test_controls_report_serialized_state_separately(self):
        self.assertTrue(MemorylessMean().state_bytes())
        self.assertTrue(ConventionalPrototypeControl().state_bytes())


if __name__=="__main__": unittest.main()
