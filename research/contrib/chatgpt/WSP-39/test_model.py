import unittest
from model import NumericModel, StrongGF2Control, direct_acquire
from battery import Teacher, trial, run

class WholeCapabilityTests(unittest.TestCase):
    def test_full_hidden_affine_acquisition_and_plan(self):
        teacher=Teacher('DEV',41,64,'affine')
        model,receipt=direct_acquire(64,teacher.step,tuple(range(64)))
        for action in range(4):
            for k in [0,1,3,7,15,63,(1<<64)-1]:
                self.assertEqual(model.apply(action,k),teacher.step(action,k))
        start=7; target=teacher.rollout(start,(1,2,3))
        self.assertEqual(model.rollout(start,model.plan(start,target)),target)
        self.assertEqual(model.snapshot(),NumericModel.restore(model.snapshot()).snapshot())
        self.assertEqual(len(receipt),4*65)
    def test_negative_ood(self):
        t=Teacher('DEV',41,64,'interaction_ood')
        model,_=direct_acquire(64,t.step,tuple(range(64)))
        for action in range(4): self.assertNotEqual(model.apply(action,3),t.step(action,3))
    def test_partial_probe_and_patch(self):
        t=Teacher('DEV',41,64,'affine')
        m,_=direct_acquire(64,t.step,tuple(range(32)))
        self.assertNotEqual(m.apply(0,1<<63),t.step(0,1<<63))
        p=m.patch(0,0,0,1 - (m.rows[0][0]&1))
        self.assertEqual((p.rows[0][0]^m.rows[0][0]),1)
        self.assertNotEqual(p.snapshot(),m.snapshot())
    def test_guardrails(self):
        t=Teacher('DEV',41,64,'affine');m,_=direct_acquire(64,t.step,tuple(range(64)))
        with self.assertRaises(ValueError): m.apply(6,0)
        with self.assertRaises(ValueError): m.plan(0,-1)
        with self.assertRaises(ValueError): m.patch(0,0,0,3)
        with self.assertRaises(ValueError): direct_acquire(64,t.step,(2,2))
        raw=m.snapshot()
        with self.assertRaises(ValueError): NumericModel.restore(raw[:-1])
        with self.assertRaises(ValueError): NumericModel.restore(raw+b'!')
    def test_full_dev(self):
        result=run('DEV')
        self.assertEqual(result['engineering'],'PASS')
        self.assertTrue(result['known_affine_full_all_exact'])
        self.assertTrue(result['partial_and_nonlinear_controls_effective'])
        self.assertEqual(result['n_worlds'],40)

if __name__=='__main__':unittest.main()
