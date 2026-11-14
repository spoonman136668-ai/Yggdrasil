"""Source-only cross-platform AAI-07 contract tests; never re-run scientific seeds."""
import ast
import json
import pathlib
import unittest

HERE=pathlib.Path(__file__).resolve().parent


class ContractTests(unittest.TestCase):
    def test_freeze(self):
        p=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
        self.assertEqual(p["experiment_id"],"AAI-07A")
        self.assertEqual(p["frozen_design"]["seeds"]["development"]["start"],971000)
        self.assertEqual(p["frozen_design"]["seeds"]["transfer"]["start"],972000)
        self.assertEqual(p["frozen_design"]["seeds"]["reserved_mechanical"],
                         "970000..970007 (consumed; NOT used in science)")
        self.assertEqual(p["inputs"][0]["source_git_sha"],
                         "64e1eaec904bc35e7de041167274e2c0dfe541d2")

    def test_primary_classification_not_native_science(self):
        result=json.loads((HERE/"result-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(result["classification"],
                         "MEMORY_BENCHMARK_ADMITTED_DEVELOPMENT_ONLY")
        self.assertEqual(result["native_integration"],"NONE")
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["cohorts"]["development"]["n"],64)
        self.assertEqual(result["cohorts"]["transfer"]["n"],64)

    def test_official_provenance(self):
        x=json.loads((HERE/"provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(x["upstream_commit"],
                         "64e1eaec904bc35e7de041167274e2c0dfe541d2")
        self.assertEqual(x["first_use_run_id"],43608507442)
        self.assertTrue(x["no_model_integrated"])

    def test_all_sources_parse_without_importing_external_benchmark(self):
        for filename in ("preflight.py","navigator_probe.py","evaluate.py"):
            code=(HERE/filename).read_text(encoding="utf-8")
            tree=ast.parse(code,filename=filename)
            assert not any(isinstance(node,ast.Attribute) and node.attr in (
                "unwrapped","agent_pos","success_pos","failure_pos","grid")
                for node in ast.walk(tree)), filename

    def test_external_suite_not_run_as_science_here(self):
        p=json.loads((HERE/"preflight-protocol.json").read_text(encoding="utf-8"))
        self.assertEqual(p["classification"],"ENGINEERING_PREP_ONLY_NOT_PRIMARY_SCIENCE")
        self.assertEqual(p["external_source_blob"],
                         "660b0a1b769948034c87bb421759c2b9a4f24548")


if __name__=="__main__":
    unittest.main()
