"""Fabricated-coefficient WSP114 fixtures. Never import the hidden evaluator."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from native import (FULL_BUDGET,LADDER,NativeWriter,effect_from_parameters,
                    grammar,observed_row)
from controls import (IndependentSymbolic,ConvergedRidge,
                      independent_predict,local_grammar)

def fake_coefficients(nodes):
    values=[]
    for j in range(nodes):
        width=len(local_grammar(j))
        code=sum(1<<i for i in range(width)
                 if sha256(f"FABRICATED|{nodes}|{j}|{i}".encode()).digest()[0]%5==0)
        values.append(code)
    return values

def synthetic_effect(nodes,coeff,state,action):
    return independent_predict(state,action,coeff,nodes)

class TestNativeLargeNonlinearCausalProgramming(unittest.TestCase):
    def test_high_first_budget_is_1024_and_ladder_backwards(self):
        self.assertEqual(FULL_BUDGET,1024)
        self.assertEqual(LADDER,(1024,512,256,128,64,32,16,8))
        self.assertEqual(len(grammar(12)),78)
        self.assertEqual(len(grammar(0)),0)

    def test_numerical_parity_kernel_matches_independent_implementation(self):
        for nodes in (16,32,48,64):
            coeff=fake_coefficients(nodes)
            for step in range(24):
                d=sha256(f"WSP114|FIXTURE|{nodes}|{step}".encode()).digest()
                s=int.from_bytes(d[:8],"big")&((1<<nodes)-1)
                a=d[9]%(nodes*2)
                self.assertEqual(effect_from_parameters(s,a,coeff,nodes),
                                 independent_predict(s,a,coeff,nodes))
                after=independent_predict(s,a,coeff,nodes)
                self.assertIsInstance(observed_row(nodes-1,after),int)

    def test_native_320_new_effects_and_separate_symbolic_generalization(self):
        nodes=16
        coeff=fake_coefficients(nodes)
        native=NativeWriter(nodes,"fabricated")
        symbolic=IndependentSymbolic(nodes)
        for step in range(320):
            s,a=NativeWriter.candidate("fake",step,0,nodes,
                                       namespace="WSP114|FABRICATED")
            y=synthetic_effect(nodes,coeff,s,a)
            native.observe(s,a,y)
            symbolic.observe(s,a,y)
            self.assertEqual(native.predict(s,a),y)
        symbolic.fit()
        self.assertEqual(len(native.observations),320)
        self.assertEqual(native.active_weights,symbolic.coefficients)
        self.assertEqual(native.ranks,symbolic.ranks)
        self.assertTrue(any(row for row in native.active_weights[5:]))
        for step in range(128):
            s,a=NativeWriter.candidate("fake-heldout",step,0,nodes,
                                       namespace="WSP114|FABRICATED")
            y=synthetic_effect(nodes,coeff,s,a)
            self.assertEqual(native.predict(s,a),y)
            self.assertEqual(symbolic.predict(s,a),y)

    def test_checkpoint_cold_and_tamper_negatives(self):
        m=NativeWriter(16,"fabricated")
        coeff=fake_coefficients(16)
        for step in range(32):
            s,a=NativeWriter.candidate("cold",step,0,16,
                                       namespace="WSP114|FABRICATED")
            m.observe(s,a,synthetic_effect(16,coeff,s,a))
        frozen=m.checkpoint()
        cold=NativeWriter.restore(frozen)
        self.assertEqual(m.active_weights,cold.active_weights)
        self.assertEqual(m.ranks,cold.ranks)
        for s in (0,15,127,65535):
            for a in range(32):
                self.assertEqual(m.predict(s,a),cold.predict(s,a))
        altered={"schema":frozen["schema"],"sha256":frozen["sha256"],
                 "data":dict(frozen["data"])}
        altered["data"]["ranks"]=[x+1 for x in altered["data"]["ranks"]]
        with self.assertRaises(ValueError):NativeWriter.restore(altered)

    def test_fitted_ridge_converges_without_hidden_laws(self):
        model=ConvergedRidge(16,l2=1.0)
        coeff=fake_coefficients(16)
        for step in range(80):
            s,a=NativeWriter.candidate("ridge",step,0,16,
                                       namespace="WSP114|FABRICATED")
            model.observe(s,a,synthetic_effect(16,coeff,s,a))
        model.fit()
        self.assertEqual(model._fitted_at,80)
        self.assertLessEqual(max(model.residuals),1e-7)
        self.assertIsInstance(model.predict(357,6),int)

    def test_no_hidden_original_oracle_used_in_learners_or_fixtures(self):
        for path in ("native.py","controls.py"):
            source=(HERE/path).read_text(encoding="utf-8")
            self.assertNotIn("from oracle",source)
            self.assertNotIn("import oracle",source)
            self.assertNotIn("hidden_coefficients(",source)
            self.assertNotIn("transfer_effect(",source)
        self.assertFalse((HERE/"SCIENTIFIC_PASS.json").exists())
        self.assertFalse((HERE/"PROTECTED_FIRST_USE.json").exists())

if __name__=="__main__":
    unittest.main()
