"""FKP-20 preregistration-first and original research isolation controls."""
import json
from pathlib import Path
import unittest

BASE=Path(__file__).resolve().parent


class FrozenSourceFirst(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prereg=json.loads((BASE/"prereg.json").read_text("utf-8"))

    def test_prereg_committed_first_to_exact_predecessor(self):
        x=self.prereg
        self.assertEqual(x["schema"],"yggdrasil.external-research-prereg.v1")
        self.assertEqual(x["experiment_id"],"FKP-20-CONDITIONAL-TWO-PARENT-VARIABLE-LAG")
        self.assertEqual(x["exact_parent_sha"],
                         "b91aa2b2d9e5fb7c5d1e28ecd0dcccd20e57bfd9")
        self.assertTrue(x["prereg_first"])
        self.assertIn(1115,[a["pr"] for a in x["predecessors"]])

    def test_exact_public_training_design_and_strong_controls(self):
        source=self.prereg["frozen_public_source"]
        self.assertEqual(source["seed_train"],{"start":992100,"end":992115,"count":16})
        self.assertTrue(source["held_dev"]["no_first_use"])
        self.assertTrue(source["held_transfer"]["no_first_use"])
        self.assertEqual(source["exploration"]["episodes"],32)
        self.assertEqual(source["scoring"]["episodes"],16)
        self.assertEqual(self.prereg["diagnostic"]["paired_bootstrap_draws"],10000)
        self.assertEqual(self.prereg["diagnostic"]["seed"],2020)
        self.assertEqual(len(self.prereg["arms"]),8)
        self.assertEqual(self.prereg["strong_controls"]["conventional"].split("BCE <=0.05")[0].count("logistic"),1)
        self.assertTrue(self.prereg["no_postresult_tuning"])

    def test_no_new_accepted_main_or_scheduler_authority(self):
        a=self.prereg["autonomy"]
        self.assertTrue(a["research_only"])
        for k in ("production_authority","promotion_authority","accepted_ref_mutation",
                  "scheduler_authority","private_runner_authority"):
            self.assertFalse(a[k])
        self.assertFalse(self.prereg["classification"]["science_pass"])
        self.assertFalse(self.prereg["classification"]["original_held_first_use"])
        self.assertEqual(self.prereg["changed_paths"],
            ["research/contrib/chatgpt/FKP-20/**",
             ".ice/code-atlas.html",".ice/code-atlas.ice",".ice/code-atlas.json"])

    def test_source_and_controller_in_isolated_research_only_files(self):
        for p in ("prereg.json","public_pair_source.py","pair_credit.py",
                  "run_known_train.py","test_pair_credit.py","README.md"):
            self.assertTrue((BASE/p).is_file())


if __name__=="__main__":
    unittest.main()
