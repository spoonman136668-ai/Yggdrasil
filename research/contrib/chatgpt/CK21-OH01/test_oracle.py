"""Frozen oracle mathematical and negative controls, without private input."""
import importlib.util
import inspect
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ck21oh01_campaign",HERE/"campaign.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class OracleControls(unittest.TestCase):
    def test_enumeration_exact(self):
        self.assertEqual(len(m.mathematical_controls()),12)
        from fractions import Fraction
        self.assertEqual(Fraction(113,128),(Fraction(219,256)+Fraction(233,256))/2)

    def test_non_clairvoyant_policy_signatures(self):
        self.assertEqual(list(inspect.signature(m.informed_first).parameters),
                         ["initial","family","regime"])
        self.assertEqual(list(inspect.signature(m.informed_second).parameters),
                         ["initial","first","next_state","family","regime"])
        for family in m.FAMILIES:
            for regime in (0,1):
                for initial in (0,1):
                    a1=m.informed_first(initial,family,regime)
                    e1,e2,value=m.independent_exact_plan(initial,family,regime)
                    self.assertEqual(a1,e1)
                    for next_state in (0,1):
                        self.assertEqual(m.informed_second(initial,a1,next_state,family,regime),e2[next_state])

    def test_invalid_public_input_rejected(self):
        cases=[
           lambda:m.informed_first(True,"invariant",0),
           lambda:m.informed_first(0,"not-a-family",0),
           lambda:m.informed_first(0,"invariant",2),
           lambda:m.informed_second(0,1,True,"invariant",0),
           lambda:m.joint_reward(0,"invariant",0,0,2,1),
        ]
        for item in cases:
            with self.subTest(case=repr(item)),self.assertRaises(ValueError):
                item()

    def test_source_pin_and_preexisting_frozen_result(self):
        self.assertEqual(m.digest((m.HERE.parent/"CKAD-20"/"synthetic_world.py").read_bytes()),
                         m.PIN_SOURCE)
        import json
        d=json.loads((m.HERE.parent/"CKAD-21"/"result.json").read_bytes())
        self.assertEqual(d["stable_sha256"],m.PIN_RESULT)
        self.assertFalse(d["scientific_pass"])
        self.assertEqual([s["seed"] for s in d["seeds"]],list(m.SEEDS))

if __name__=="__main__":
    unittest.main()
