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


if __name__=="__main__":
    unittest.main()
