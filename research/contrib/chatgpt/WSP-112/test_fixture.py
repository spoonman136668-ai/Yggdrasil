"""Fixture only: fabricated causal feedback. No import of hidden law evaluator."""
from __future__ import annotations
import unittest
from pathlib import Path
import numpy as np
from core import (FEATURES,invert_truth,prior_from_full_training,
                  DirectWriter,SymbolicGF2,ConventionalGP)

def make_table(offset):
    return np.asarray([[int(((x^offset)&1)>0),int((x>>1)&1)]
                       for x in range(16)],dtype=np.uint8)

class TestSyntheticActiveCausalProgramming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=np.stack([make_table(i) for i in range(8)])
        cls.prior=prior_from_full_training(cls.train)
        cls.target=make_table(2)

    def test_boolean_coefficient_inverse(self):
        for src in self.train:
            w=invert_truth(src)
            self.assertTrue(np.array_equal((FEATURES@w)%2,src))

    def test_unique_interventions_observed_recall_and_budgets(self):
        for model in (DirectWriter(self.prior),SymbolicGF2(),ConventionalGP(self.train)):
            visited=[]
            for _ in range(8):
                x=model.choose()
                self.assertNotIn(x,visited)
                visited.append(x)
                y=int(self.target[x,0]+2*self.target[x,1])
                model.observe(x,y)
                self.assertEqual(model.predict(x),y)
            self.assertEqual(len(set(visited)),8)
            with self.assertRaises(ValueError):model.choose()

    def test_cold_native_replay_and_tamper_rejection(self):
        m=DirectWriter(self.prior)
        for _ in range(8):
            x=m.choose()
            m.observe(x,int(self.target[x,0]+2*self.target[x,1]))
        snapshot=m.checkpoint()
        r=DirectWriter.restore(snapshot)
        self.assertTrue(np.array_equal(r.numeric_effect_weights,m.numeric_effect_weights))
        self.assertTrue(np.array_equal(r.synapses,m.synapses))
        self.assertEqual([m.predict(x) for x in range(16)],
                         [r.predict(x) for x in range(16)])
        tampered={"schema":snapshot["schema"],"sha256":snapshot["sha256"],
                  "blocks":dict(snapshot["blocks"])}
        s=tampered["blocks"]["effects"]
        tampered["blocks"]["effects"]=("ff" if s[:2]!="ff" else "00")+s[2:]
        with self.assertRaises(ValueError):
            DirectWriter.restore(tampered)
        with self.assertRaises(ValueError):
            m.observe(0,0)

    def test_no_original_transfer_oracle_fixtures(self):
        code=(Path(__file__).parent/"core.py").read_text(encoding="utf-8")
        self.assertNotIn("from oracle import",code)
        self.assertNotIn("import oracle",code)
        self.assertFalse((Path(__file__).parent/"SCIENTIFIC_PASS.json").exists())
        self.assertFalse((Path(__file__).parent/"PROTECTED_FIRST_USE.json").exists())

if __name__=="__main__":
    unittest.main()
