"""Unscored interface fixtures only. Never call run_world_arm here."""
import unittest
from quadratic_controls import QuadraticControl, features
from transfer_study_eval import make_arm,forecast,checkpoint,expected_brier,ARMS,split,digest,pairs,probability_tenths

class ControlFixtures(unittest.TestCase):
    def test_feature_abi(self):
        self.assertEqual(len(features(511)),46)
        self.assertEqual(features(511),(1,)*46)

    def test_roundtrip_and_continuation(self):
        for arm in ARMS:
            with self.subTest(arm=arm):
                a = make_arm(arm,1)
                for i in range(520):
                    a.observe(i,i%3,i%512,(1,0,1,0))
                raw = checkpoint(a)
                b = type(a).restore(raw)
                self.assertEqual(a.predict(1,13),b.predict(1,13))
                for m in (a,b):
                    m.observe(520,2,13,(0,1,0,1))
                self.assertEqual(a.checkpoint(),b.checkpoint())

    def test_seed_capacity(self):
        m = QuadraticControl("replay",97001)
        self.assertEqual(QuadraticControl.restore(m.checkpoint()).seed,97001)

    def test_invalid_events(self):
        for mode in ("local","shared","replay"):
            m = QuadraticControl(mode,1)
            raw = m.checkpoint()
            for args in ((1,0,0,(1,)*4),(0,3,0,(1,)*4),(0,0,512,(1,)*4),(0,0,0,(True,)*4)):
                with self.assertRaises(ValueError):
                    m.observe(*args)
                self.assertEqual(raw,m.checkpoint())
            with self.assertRaises(ValueError):
                m.restore(raw[:-1])

    def test_shared_prior_and_retention(self):
        m = QuadraticControl("shared",1)
        for i in range(50):
            m.observe(i,0,511,(1,)*4)
        self.assertGreater(m.predict(2,511)[0],.5)
        before=m.predict(0,511)
        for i in range(50,100):
            m.observe(i,1,511,(0,)*4)
        self.assertEqual(before,m.predict(0,511))

    def test_generator_interface_nonstudy_seed(self):
        train,held=split(1)
        self.assertEqual((len(train),len(held)),(384,128))
        self.assertFalse(set(train)&set(held))
        self.assertEqual(len(set(train+held)),512)
        self.assertNotEqual(*pairs(1,0))
        for p in (0,1,511):
            a=probability_tenths(1,"related",0,p,0)
            self.assertEqual(probability_tenths(1,"related",3,p,0),a)
            self.assertEqual(probability_tenths(1,"conflicting_C",3,p,0),10-a)

    def test_expected_loss_and_abstention(self):
        a=make_arm("candidate",1)
        self.assertEqual(forecast(a,None,0),((.5,)*4,1))
        self.assertEqual(expected_brier(a,0,(0,511),lambda p,j:5),(.25,0))

if __name__=="__main__":
    unittest.main()
