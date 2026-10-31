import json
import unittest
from diagonal_bayes_control import DiagonalBayesControl, DIM, TARGETS
from residual_belief import FEATURES


def xvec(i):
    return tuple(1.0 if j == i % FEATURES else 0.0 for j in range(FEATURES))

def yvec(i):
    return tuple(1.0 if j == i % TARGETS else 0.0 for j in range(TARGETS))


class DiagonalBayesTests(unittest.TestCase):
    def test_posterior_updates_only_after_selected_feedback(self):
        m=DiagonalBayesControl()
        before=[row[:] for row in m.precision]
        m.predict(xvec(0),1)
        self.assertEqual(before,m.precision)
        m.observe_selected_outcome(yvec(2))
        self.assertEqual(m.steps,1)
        self.assertGreater(m.precision[0][0],before[0][0])

    def test_action_conditioned_predictions(self):
        m=DiagonalBayesControl()
        for _ in range(8):
            m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
            m.predict(xvec(0),1);m.observe_selected_outcome(yvec(1))
        p0=m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
        p1=m.predict(xvec(0),1);m.observe_selected_outcome(yvec(1))
        self.assertNotEqual(p0.values,p1.values)

    def test_posterior_uncertainty_decreases_with_repeated_evidence(self):
        m=DiagonalBayesControl()
        p0=m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
        p1=m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
        self.assertLess(p1.uncertainty,p0.uncertainty)

    def test_cold_restart_preserves_next_prediction(self):
        m=DiagonalBayesControl()
        for i in range(20):
            m.predict(xvec(i),i%3);m.observe_selected_outcome(yvec(i))
        data=m.snapshot()
        a=DiagonalBayesControl.restore(data)
        b=DiagonalBayesControl.restore(data)
        self.assertEqual(a.predict(xvec(21),2),b.predict(xvec(21),2))

    def test_feedback_order_and_checkpoint_tampering(self):
        m=DiagonalBayesControl()
        with self.assertRaisesRegex(RuntimeError,"NO_PENDING"):
            m.observe_selected_outcome(yvec(0))
        m.predict(xvec(0),0)
        with self.assertRaisesRegex(RuntimeError,"PENDING"):
            m.snapshot()
        m.observe_selected_outcome(yvec(0))
        payload=json.loads(m.snapshot());payload["payload"]["steps"]=99
        with self.assertRaisesRegex(ValueError,"HASH_MISMATCH"):
            DiagonalBayesControl.restore(json.dumps(payload).encode())

    def test_fixed_posterior_dimensions_and_invalid_action(self):
        m=DiagonalBayesControl()
        self.assertEqual(len(m.precision),TARGETS)
        self.assertTrue(all(len(r)==DIM for r in m.precision))
        with self.assertRaisesRegex(ValueError,"SELECTED_ACTION"):
            m.predict(xvec(0),3)


if __name__=="__main__":unittest.main()
