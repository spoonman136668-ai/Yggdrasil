import json
import unittest
from recurrent_control import RecurrentStateSpaceControl, HIDDEN, TARGETS
from residual_belief import FEATURES


def xvec(i):
    return tuple(1.0 if j == i % FEATURES else 0.0 for j in range(FEATURES))

def yvec(i):
    return tuple(1.0 if j == i % TARGETS else 0.0 for j in range(TARGETS))


class RecurrentControlTests(unittest.TestCase):
    def test_fixed_state_and_readout_dimensions(self):
        m=RecurrentStateSpaceControl()
        for i in range(40):
            m.predict(xvec(i),i%3);m.observe_selected_outcome(yvec(i))
        self.assertEqual(len(m.state),HIDDEN)
        self.assertEqual(len(m.readout),TARGETS)
        self.assertTrue(all(len(row)==HIDDEN for row in m.readout))

    def test_action_is_part_of_recurrent_input(self):
        m=RecurrentStateSpaceControl()
        m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
        p0=m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
        p1=m.predict(xvec(0),1);m.observe_selected_outcome(yvec(1))
        self.assertNotEqual(p0.values,p1.values)

    def test_feedback_order_and_invalid_action(self):
        m=RecurrentStateSpaceControl()
        with self.assertRaisesRegex(RuntimeError,"NO_PENDING"):
            m.observe_selected_outcome(yvec(0))
        with self.assertRaisesRegex(ValueError,"SELECTED_ACTION"):
            m.predict(xvec(0),3)

    def test_cold_restart_preserves_next_prediction(self):
        m=RecurrentStateSpaceControl()
        for i in range(12):
            m.predict(xvec(i),i%3);m.observe_selected_outcome(yvec(i))
        data=m.snapshot()
        a=RecurrentStateSpaceControl.restore(data)
        b=RecurrentStateSpaceControl.restore(data)
        self.assertEqual(a.predict(xvec(20),2),b.predict(xvec(20),2))

    def test_pending_checkpoint_rejected_and_tamper_detected(self):
        m=RecurrentStateSpaceControl()
        m.predict(xvec(0),0)
        with self.assertRaisesRegex(RuntimeError,"PENDING"):
            m.snapshot()
        m.observe_selected_outcome(yvec(0))
        doc=json.loads(m.snapshot());doc["payload"]["steps"]=999
        with self.assertRaisesRegex(ValueError,"HASH_MISMATCH"):
            RecurrentStateSpaceControl.restore(json.dumps(doc).encode())


if __name__=="__main__":unittest.main()
