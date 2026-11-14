"""Source/provenance-only qualification; never execute consumed science worlds."""
import ast
import hashlib
import json
import pathlib
import unittest

HERE=pathlib.Path(__file__).resolve().parent


class AAI07BContractTests(unittest.TestCase):
    def test_frozen_scientific_protocol(self):
        pre=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
        self.assertEqual(pre["experiment"],"AAI-07B")
        self.assertEqual(pre["design"]["train_seeds"],{"first":981000,"n":48})
        self.assertEqual(pre["design"]["transfer_seeds"],{"first":983000,"n":64})
        self.assertEqual(pre["external"]["source_git_commit"],
                         "64e1eaec904bc35e7de041167274e2c0dfe541d2")

    def test_source_does_not_consume_hidden_fields(self):
        parsed=ast.parse((HERE/"evaluate.py").read_text(encoding="utf-8"))
        prohibited={"unwrapped","mission","success_pos","failure_pos","agent_pos","grid"}
        self.assertFalse(any(isinstance(x,ast.Attribute) and x.attr in prohibited
                             for x in ast.walk(parsed)))

    def test_frozen_result_unchanged(self):
        data=json.loads((HERE/"result-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(data["classification"],"LEARNING_DEMONSTRATED_NOT_SUPERIOR")
        self.assertEqual(data["gaps"]["transfer_direct_minus_strongest"],0)
        self.assertEqual(data["cohorts"]["dev"]["direct"]["n"],64)
        self.assertEqual(data["cohorts"]["transfer"]["direct"]["n"],64)
        self.assertEqual(data["integration"],"NONE")

    def test_original_raw_result_custody(self):
        prov=json.loads((HERE/"provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(prov["first_use_commit"],
                         "b8a0ed1992ee9be5176274e6655bfa45abf00cd2")
        self.assertTrue(prov["source_unchanged_after_first_use"])
        self.assertTrue(prov["no_integration"])
        raw=(HERE/"primary-original.json").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         prov["original_raw_json_sha256"])
        full=json.loads(raw)
        self.assertEqual(full["world_records_sha256"],
                         json.loads((HERE/"result-summary.json").read_text(encoding="utf-8"))
                             ["world_records_sha256"])
        self.assertEqual(len(full["world_rows"]["dev"]),64)
        self.assertEqual(len(full["world_rows"]["transfer"]),64)
        self.assertEqual(len(full["world_rows"]["negative"]),64)

    def test_artifact_does_not_certify_native_yggdrasil(self):
        prov=json.loads((HERE/"provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(prov["original_run_id"],43610008504)
        self.assertEqual(prov["primary_classification"],
                         "LEARNING_DEMONSTRATED_NOT_SUPERIOR")
        self.assertTrue(prov["branch_draft"])


if __name__=="__main__":
    unittest.main()
