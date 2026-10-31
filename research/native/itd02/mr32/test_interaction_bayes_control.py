import json
import unittest
from interaction_bayes_control import InteractionBayesControl, DIM, TARGETS
from residual_belief import FEATURES

def xvec(i):
    return tuple(1.0 if j == i % FEATURES else 0.0 for j in range(FEATURES))

def yvec(i):
    return tuple(1.0 if j == i % TARGETS else 0.0 for j in range(TARGETS))

class InteractionBayesTests(unittest.TestCase):
    def test_action_feature_interaction_basis(self):
        phi0=InteractionBayesControl._phi(xvec(2),0)
        phi1=InteractionBayesControl._phi(xvec(2),1)
        self.assertEqual(len(phi0),DIM)
        self.assertNotEqual(phi0,phi1)
        self.assertEqual(DIM,1+16+3+48)

    def test_posterior_updates_after_feedback(self):
        m=InteractionBayesControl()
        before=[r[:] for r in m.precision]
        m.predict(xvec(0),1)
        self.assertEqual(before,m.precision)
        m.observe_selected_outcome(yvec(2))
        self.assertGreater(m.precision[0][0],before[0][0])

    def test_action_context_separation(self):
        m=InteractionBayesControl()
        for _ in range(8):
            m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
            m.predict(xvec(0),1);m.observe_selected_outcome(yvec(1))
        p0=m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
        p1=m.predict(xvec(0),1);m.observe_selected_outcome(yvec(1))
        self.assertNotEqual(p0.values,p1.values)

    def test_uncertainty_and_cold_restore(self):
        m=InteractionBayesControl()
        p0=m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
        p1=m.predict(xvec(0),0);m.observe_selected_outcome(yvec(0))
        self.assertLess(p1.uncertainty,p0.uncertainty)
        blob=m.snapshot()
        a=InteractionBayesControl.restore(blob);b=InteractionBayesControl.restore(blob)
        self.assertEqual(a.predict(xvec(1),2),b.predict(xvec(1),2))

    def test_pending_feedback_and_tamper_fail_closed(self):
        m=InteractionBayesControl()
        with self.assertRaisesRegex(RuntimeError,"NO_PENDING"):m.observe_selected_outcome(yvec(0))
        m.predict(xvec(0),0)
        with self.assertRaisesRegex(RuntimeError,"PENDING"):m.snapshot()
        m.observe_selected_outcome(yvec(0))
        doc=json.loads(m.snapshot());doc["payload"]["steps"]=99
        with self.assertRaisesRegex(ValueError,"HASH_MISMATCH"):InteractionBayesControl.restore(json.dumps(doc).encode())

    def test_invalid_dimensions_and_action(self):
        m=InteractionBayesControl()
        with self.assertRaisesRegex(ValueError,"SELECTED_ACTION"):
            m.predict(xvec(0),3)
        with self.assertRaisesRegex(ValueError,"DIMENSION"):
            InteractionBayesControl._phi((0.0,),0)

    def test_action_feature_interaction_generalizes_heldout_sign(self):
        from diagonal_bayes_control import DiagonalBayesControl
        interaction=InteractionBayesControl()
        additive=DiagonalBayesControl()
        # Balanced development fit: y0 = feature[0] for action 0,
        # and y0 = -feature[0] for action 1. Action and feature main effects
        # alone cannot represent the sign reversal.
        for _ in range(40):
            for action in (0,1):
                for sign in (-1.0,1.0):
                    features=(sign,)+(0.0,)*(FEATURES-1)
                    target=(sign if action==0 else -sign,)+(0.0,)*(TARGETS-1)
                    interaction.predict(features,action);interaction.observe_selected_outcome(target)
                    additive.predict(features,action);additive.observe_selected_outcome(target)
        squared_interaction=0.0
        squared_additive=0.0
        cases=0
        for action in (0,1):
            for sign in (-1.0,1.0):
                features=(sign,)+(0.0,)*(FEATURES-1)
                expected=sign if action==0 else -sign
                pi=interaction.predict(features,action)
                pa=additive.predict(features,action)
                squared_interaction+=(pi.values[0]-expected)**2
                squared_additive+=(pa.values[0]-expected)**2
                interaction.observe_selected_outcome((expected,)+(0.0,)*(TARGETS-1))
                additive.observe_selected_outcome((expected,)+(0.0,)*(TARGETS-1))
                cases+=1
        self.assertLess(squared_interaction/cases,squared_additive/cases)


if __name__=="__main__":unittest.main()
