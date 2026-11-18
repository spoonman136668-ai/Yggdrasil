"""Frozen CKAD23 aggregate anti-tamper and independence controls."""
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad23_score_audit",HERE/"audit.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class CKAD23AuditControls(unittest.TestCase):
    def test_exact_seed_group_signflip(self):
        self.assertEqual(m.signflip((4,4,4)),[1,4])
        self.assertEqual(m.signflip((0,0,0)),[1,1])
        self.assertEqual(m.signflip((4,-4,0)),[1,1])
        self.assertGreaterEqual(Fraction(*m.signflip((4,-2,1))),Fraction(1,4))

    def test_original_pins_and_gate_rule(self):
        d=m.read_original()
        self.assertEqual(set(d),set(m.PARENTS))
        self.assertTrue(all(m.sha_check(v) for v in d.values()))
        protocol=json.loads((HERE/"prereg.json").read_bytes())
        self.assertEqual(protocol["parent_groups"],list(m.PARENTS))
        self.assertEqual(protocol["evaluation_namespace_seeds"],list(m.ENVS))
        self.assertEqual(protocol["scientific_pass"],False)
        self.assertEqual(len(m.WORLDS),2)

    def test_fake_shard_denied(self):
        sample={"schema":"yggdrasil.ckad23.compositional-disjoint-shard.v1",
                "source_parent":m.SOURCE_COMMIT,"source_sha256":m.SOURCE_FIXTURE,
                "original_ckad22_result_sha256":m.SOURCE_STABLE,
                "parent":101,"half":0,"environment_seeds":list(m.ENVS[:4]),
                "synthetic_probe_updates":128,"cases":[],
                "original_source_actions":0,"protected_first_use":0,
                "scientific_pass":False,"accepted_native":False,"deployment":"NONE"}
        sample["stable_sha256"]=m.digest(m.canonical(sample))
        with self.assertRaisesRegex(ValueError,"SHARD_SCOPE"):
            m.audit_shard(sample)
        sample["scientific_pass"]=True
        with self.assertRaisesRegex(ValueError,"SHARD_NO_PROMOTION"):
            m.audit_shard(sample)

if __name__=="__main__":
    unittest.main()
