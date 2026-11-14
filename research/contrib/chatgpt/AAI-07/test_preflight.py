"""Checks bounded MiniGrid preflight on mechanical reserved seeds."""
import importlib.util
import pathlib
import unittest

HERE=pathlib.Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("aai07_preflight",HERE/"preflight.py")
app=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class ExternalPreflightTests(unittest.TestCase):
    def test_frozen_source(self):
        self.assertEqual(len(app.EXTERNAL_SHA), 40)
        self.assertEqual(len(app.SOURCE_BLOB), 40)

    def test_reserved_seed_boundary(self):
        self.assertEqual(app.PRECHECK_SEEDS, tuple(range(970000, 970008)))
        self.assertEqual(len(app.ENVIRONMENTS),2)
        self.assertEqual(app.TEST_ACTIONS,(2,0,2,1,2,2,0,2))

    def test_same_seed_reproducibility_and_obs(self):
        output=app.run()
        self.assertTrue(output["reproducible_same_seed"])
        self.assertTrue(output["no_hidden_simulator_state_consumed"])
        self.assertEqual(output["scientific_first_use"],False)
        self.assertEqual(len(output["trace_receipt_sha256"]),64)
