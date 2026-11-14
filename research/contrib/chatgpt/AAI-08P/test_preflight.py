"""Mechanical AAI-08P only; reserve external science splits."""
import ast
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("aai08p",HERE/"preflight.py")
x=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(x)


class BridgeTests(unittest.TestCase):
    def test_source_and_budget(self):
        self.assertEqual(x.UPSTREAM,"127df4b714fe4fcf680721d8e9278a96090acd7e")
        self.assertEqual(x.MECHANICAL_SEEDS,(996000,996001,996002,996003))
        self.assertEqual(x.ACTIONS,(2,0,2,2))

    def test_hidden_notification_disabled(self):
        self.assertEqual(x.INITIAL,(1.,0.,0.))
        self.assertEqual(x.CHANGED,(0.,1.,0.))
        p=ast.parse((HERE/"preflight.py").read_text(encoding="utf8"))
        # The experimental adapter never reads the environment's private state
        # or the diagnostic info returned by the NS-Gym wrapper.
        forbidden={"unwrapped","get_planning_env","transition_matrix"}
        self.assertFalse(any(isinstance(z,ast.Attribute) and z.attr in forbidden
                             for z in ast.walk(p)))

    def test_official_environment_real_transition_change(self):
        result=x.mechanical()
        self.assertEqual(result["mechanical_worlds"],4)
        self.assertTrue(result["same_action_data_before_change"])
        self.assertTrue(result["official_transition_change_affects_real_reward"])
        self.assertFalse(result["scientific_primary_consumed"])
        self.assertEqual(len(result["trace_sha256"]),64)
