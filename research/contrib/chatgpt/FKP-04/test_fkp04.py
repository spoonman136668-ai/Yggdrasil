"""FKP-04 public-only deterministic and negative controls. No protected data."""
import unittest
from array import array
from source import Mechanisms,World,DEV_KEY,N_HIST,N_STATES,N_PAID,group
from experiment import NumericMemory,learn_real_transitions,policy_actions,fit_order

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle=Mechanisms(DEV_KEY)
        cls.data,cls.control,cls.seconds=learn_real_transitions(cls.oracle)
        cls.memory=NumericMemory(cls.data)

    def test_held_split_and_source_key_fence(self):
        w=World(500,self.oracle)
        v=w.public_view()
        self.assertEqual(len(set(v.public_pool)),128)
        self.assertEqual(len(set(v.held_states)),256)
        self.assertFalse(set(v.public_pool)&set(v.held_states))
        self.assertEqual(set(v.__dataclass_fields__),{'mechanism_a','mechanism_b','public_pool','held_states','state_size'})
        for seed in (1500,1563,2500,2515):
            with self.assertRaises(PermissionError):World(seed,self.oracle)
        with self.assertRaises(ValueError):World(500,self.oracle,protected_key=b'x'*32)
        for bad in (499,516,1499,1564,True):
            with self.assertRaises(ValueError):group(bad)

    def test_exact_one_million_transition_observations_and_cold(self):
        self.assertEqual(len(self.data),N_HIST)
        self.assertEqual(self.data.tobytes(),self.control.tobytes())
        clone,digest,nbytes=self.memory.cold()
        self.assertEqual(nbytes,2097152)
        self.assertEqual(len(digest),64)
        for m,s in ((0,0),(17,300),(255,4095)):
            self.assertEqual(clone.step(m,s),self.oracle.step(m,s))
        with self.assertRaises(ValueError):clone.step(256,15)
        with self.assertRaises(ValueError):clone.step(0,-1)
        with self.assertRaises(ValueError):clone.step(True,0)
        with self.assertRaises(ValueError):NumericMemory(array('H',[0]))

    def test_interventions_are_genuine_and_bounded(self):
        w=World(500,self.oracle)
        view=w.public_view()
        a,b=view.mechanism_a,view.mechanism_b
        choices=policy_actions(self.memory,view.public_pool,a,b,'active',500)
        self.assertEqual(len(set(choices)),N_PAID)
        self.assertTrue(any(self.memory.compose(a,b,x,0)!=self.memory.compose(a,b,x,1) for x in choices))
        obs=tuple((s,w.observe(s)) for s in choices)
        self.assertEqual(fit_order(self.memory,a,b,obs),w.dev_private_order())
        self.assertEqual(w.charged,16)
        with self.assertRaises(PermissionError):w.observe(choices[0])
        with self.assertRaises(PermissionError):w.observe(next(x for x in view.public_pool if x not in choices))
        with self.assertRaises(ValueError):w.observe(-1)
        with self.assertRaises(ValueError):w.dev_eval(view.held_states[:-1])

    def test_memory_retains_all_observed_mappings_without_source(self):
        c,sha,n=self.memory.cold()
        for m in (1,31,128,255):
            for state in range(N_STATES):
                self.assertEqual(c.step(m,state),self.oracle.step(m,state))
        self.assertEqual(c.cold()[1],sha)

    def test_unseen_mechanisms_fail_closed_instead_of_hallucinating(self):
        with self.assertRaises(ValueError):self.memory.step(256,0)
        self.assertIn(self.oracle.step(256,0),range(N_STATES))

if __name__=='__main__':unittest.main()
