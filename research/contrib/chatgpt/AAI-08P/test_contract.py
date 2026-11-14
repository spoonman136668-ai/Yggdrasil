"""AAI-08P source-only custody qualification. No external imports/science execution."""
import ast
import json
from pathlib import Path
import unittest

HOME=Path(__file__).resolve().parent

class BridgeContract(unittest.TestCase):
    def test_protocol_source(self):
        j=json.loads((HOME/"protocol.json").read_text(encoding="utf-8"))
        self.assertEqual(j["upstream"]["commit"],"127df4b714fe4fcf680721d8e9278a96090acd7e")
        self.assertEqual(j["upstream"]["bridge_blob"],"02415d65ff8a0c419d32f274e2669f9e54e8d29f")
        self.assertIn("gymnasium[mujoco]==1.2.2",j["dependencies"]["minimal"])
        self.assertEqual(j["phase"],"mechanical external source admission; NO scientific primary")

    def test_result_is_mechanical_only(self):
        j=json.loads((HOME/"preflight-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(j["classification"],"EXTERNAL_TRANSITION_SHIFT_ENGINEERING_ADMITTED_ONLY")
        self.assertFalse(j["scientific_first_use"])
        self.assertFalse(j["learner_trained"])
        self.assertEqual(j["scientific_cohorts_used"],0)

    def test_equal_os_trace_and_repro(self):
        j=json.loads((HOME/"preflight-receipt.json").read_text(encoding="utf-8"))
        x=j["os_results"]
        self.assertEqual(x["linux"]["trace_sha256"],x["windows"]["trace_sha256"])
        self.assertEqual(x["linux"]["unit"],"3/3 PASS")
        self.assertEqual(x["windows"]["unit"],"3/3 PASS")

    def test_no_learner_privileged_sources(self):
        source=(HOME/"preflight.py").read_text(encoding="utf-8")
        tree=ast.parse(source)
        blocked={"unwrapped","get_planning_env","transition_matrix"}
        self.assertFalse(any(isinstance(v,ast.Attribute) and v.attr in blocked
                             for v in ast.walk(tree)))


    def test_stochastic_source_only_contract(self):
        j=json.loads((HOME/"stochastic-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(j["classification"],"SCOPED_STOCHASTIC_SOURCE_REPLAY_MECHANICALLY_QUALIFIED")
        self.assertEqual(j["original_run_id"],43614285704)
        self.assertTrue(j["no_science_first_use"])
        self.assertFalse(j["native_environment_seed_is_sufficient"])

    def test_stochastic_same_trace_dual_platform(self):
        j=json.loads((HOME/"stochastic-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(j["linux"]["trace_sha256"],j["windows"]["trace_sha256"])
        self.assertEqual(j["linux"]["stochastic_changed_cases"],15)
        self.assertEqual(j["windows"]["stochastic_changed_cases"],15)
        self.assertEqual(j["source_adapter_blob"],"e860ebe4cca9aa255058325e01f90938c16a9432")

    def test_stochastic_no_privileged_source(self):
        t=ast.parse((HOME/"stochastic_custody.py").read_text(encoding="utf-8"))
        blocked={"unwrapped","get_planning_env","transition_matrix"}
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr in blocked
                             for n in ast.walk(t)))


if __name__=="__main__":
    unittest.main()
