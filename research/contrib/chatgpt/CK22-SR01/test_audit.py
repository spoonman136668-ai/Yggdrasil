"""Frozen CK22-SR01 robustness-audit surface and negative controls."""
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ck22_sr01",HERE/"audit.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class RobustnessAuditTests(unittest.TestCase):
    def test_exact_cluster_signflip(self):
        self.assertEqual(mod.exact_signflip([4,4,4]),[1,4])
        self.assertEqual(mod.exact_signflip([0,0,0]),[1,1])
        self.assertEqual(mod.exact_signflip([5,-5,0]),[1,1])
        for seq in ((1,-2,5),(10,0,-2),(1,3,5)):
            num,den=mod.exact_signflip(seq)
            self.assertGreaterEqual(Fraction(num,den),Fraction(1,4))

    def test_actual_retained_ckad22_proof(self):
        data=json.loads((mod.BASE/"result.json").read_text(encoding="utf-8"))
        summary=mod.validate(data)
        self.assertEqual(summary["source_stable_sha256"],mod.EXPECTED_SHA)
        self.assertEqual(len(summary["per_seed"]),3)
        self.assertEqual(len(summary["per_session"]),4)
        self.assertEqual(summary["source_case_count"],1152)
        self.assertFalse(summary["scientific_pass"])
        self.assertEqual([v["session"] for v in summary["per_session"]],[0,1,2,3])
        for c in summary["unfamiliar_group_exact_two_sided_signflip_p"].values():
            self.assertGreaterEqual(Fraction(*c),Fraction(1,4))
        num,den=summary["original_ckad22_metrics_verified"]["unfamiliar_reward"]
        n=sum(summary["per_session"][s]["rewards"]["novel_active"] for s in (0,1))
        self.assertEqual(Fraction(n,576),Fraction(num,den))

    def test_tamper_and_missing_seed_rejected(self):
        data=json.loads((mod.BASE/"result.json").read_text(encoding="utf-8"))
        forged=dict(data); forged["stable_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"SOURCE_STABLE_EXPECTED"):
            mod.validate(forged)
        missing=dict(data); missing["seeds"]=data["seeds"][:2]
        with self.assertRaisesRegex(ValueError,"SOURCE_STABLE_RECOMPUTED"):
            mod.validate(missing)
        malformed=dict(data); malformed["development_gates"]={k:False for k in data["development_gates"]}
        with self.assertRaisesRegex(ValueError,"SOURCE_STABLE_RECOMPUTED"):
            mod.validate(malformed)

if __name__=="__main__":
    unittest.main()
