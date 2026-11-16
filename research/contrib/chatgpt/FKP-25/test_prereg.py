"""FKP-25 prereg-first exact parent and native-source first-use denied."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent


class FrozenOriginalNativeConstructorContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((ROOT/"prereg.json").read_text("utf-8"))

    def test_frozen_original_source_and_parent(self):
        p=self.p
        self.assertEqual(p["schema"],"yggdrasil.external-research-prereg.v1")
        self.assertTrue(p["prereg_first"])
        self.assertEqual(p["experiment_id"],
                         "FKP-25-PINNED-ORIGINAL-MDP-TARGETED-CONSTRUCTOR")
        self.assertEqual(p["exact_parent_sha"],
                         "a9f7a64f34275c62f507987b3d52657ec9c78f21")
        self.assertEqual(p["upstream"]["commit"],
                         "c94e9a4cd3641588b6b8507e71ccee5c27032bdf")
        self.assertEqual(len(p["upstream"]["unchanged_original_files"]),16)

    def test_original_runtime_import_is_narrow_and_exact(self):
        p=self.p
        self.assertIn("targeted",p["runtime"]["method"])
        self.assertTrue(p["runtime"]["no_first_use"])
        self.assertTrue(p["runtime"]["no_reset"])
        self.assertTrue(p["runtime"]["no_do"])
        self.assertTrue(p["runtime"]["no_model_science"])
        self.assertEqual(p["qualification"]["outside_real_source_actions"],0)
        self.assertEqual(p["runtime"]["constructor"],
                         "MDPPCH(max_step=30,task=Task(learning_regime=LearningRegime.do))")
        self.assertEqual(p["runtime"]["dependencies_pinned_top_level"]["numpy"],"1.26.4")
        self.assertEqual(len(p["qualification"]["platforms"]),2)

    def test_separate_permissions_and_all_files_present(self):
        p=self.p
        for k in ("main_ref_mutation","protected_first_use","real_source_action",
                  "merge","deploy","private_runner","scheduler_controller","paid_API"):
            self.assertFalse(p["authority"][k])
        self.assertTrue(p["no_new_workflow_file"])
        self.assertTrue(p["no_post_result_tuning"])
        for f in ("prereg.json","runtime_probe.py","test_runtime_probe.py",
                  "test_prereg.py","README.md"):
            self.assertTrue((ROOT/f).is_file())
        self.assertFalse((ROOT/"causal_gym").exists())


if __name__=="__main__":
    unittest.main()
