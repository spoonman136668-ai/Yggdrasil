"""FKP-19 source-first frozen design and source-isolation qualification."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent


class FrozenScientificBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((ROOT/"prereg.json").read_text("utf-8"))

    def test_frozen_preimplementation_parent_and_predecessor(self):
        self.assertEqual(self.p["schema"],"yggdrasil.external-research-prereg.v1")
        self.assertEqual(self.p["experiment_id"],"FKP-19-OBSERVED-DELAYED-INTERVENTION-CREDIT")
        self.assertEqual(self.p["exact_parent_sha"],
                         "362b63ed081298284ac66470e06f9ff7653c4562")
        self.assertIn(1114,[x["pr"] for x in self.p["predecessor_evidence"]])

    def test_action_budget_source_controls_and_held_denials(self):
        design=self.p["frozen_design"]
        self.assertEqual(design["world_seed_train"],{"start":991100,"end":991115,"count":16})
        self.assertTrue(design["protected_dev"]["no_first_use"])
        self.assertTrue(design["reserved_transfer"]["no_first_use"])
        self.assertEqual(design["exploration"]["episodes_per_world"],8)
        self.assertEqual(design["scoring"]["episodes_per_world"],16)
        self.assertEqual(len(design["arms"]),7)
        self.assertIn("EXACT_BAYES_CONTEXT",design["arms"])
        self.assertIn("FULLY_FITTED_INTERACTION_LOGISTIC",design["arms"])
        self.assertEqual(design["logistic_baseline"]["epochs_max"],1024)
        self.assertEqual(design["logistic_baseline"]["training_loss_must_be_at_most"],0.05)

    def test_reserve_native_and_science_authority(self):
        self.assertEqual(self.p["changed_paths"],[
            "research/contrib/chatgpt/FKP-19/**",
            ".ice/code-atlas.html",".ice/code-atlas.ice",".ice/code-atlas.json"])
        for v in self.p["authority"].values():
            self.assertFalse(v)
        self.assertIn("not SCIENTIFIC_PASS",self.p["classification_rules"]["supported"])

    def test_inputs_have_no_hidden_experiment_first_use(self):
        self.assertIn("no use of held", self.p["frozen_design"]["loss_protocol"])
        self.assertTrue(self.p["frozen_design"]["protected_dev"]["no_first_use"])
        self.assertTrue(self.p["frozen_design"]["reserved_transfer"]["no_first_use"])
        self.assertTrue((ROOT/"public_delayed_source.py").is_file())
        self.assertTrue((ROOT/"lag_credit.py").is_file())
        self.assertTrue((ROOT/"run_known_train.py").is_file())


if __name__=="__main__":
    unittest.main()
