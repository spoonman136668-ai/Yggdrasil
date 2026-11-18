"""WSP186 source-free security/learning-interface checks, NOT real-data training."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import tempfile
import unittest

from physical_wsp186 import (admit_public_source, RUN_SHA,
                             FIT_RUNS, VALID_RUNS, DEV_RUNS,
                             ZIP_SHA256, ZIP_MD5, prior)


class SourceSafeCohortTests(unittest.TestCase):
    def test_new_source_roster_frozen_and_excludes_short_recording(self):
        self.assertEqual(FIT_RUNS,(2,3,4,5,6))
        self.assertEqual(VALID_RUNS,(7,8))
        self.assertEqual(DEV_RUNS,(9,10))
        self.assertEqual(len(RUN_SHA),10)
        self.assertNotIn("actuators_random_walk_1",RUN_SHA)
        self.assertIn("regime_jumps_single",RUN_SHA)
        for k in range(2,11):
            self.assertIn(f"actuators_random_walk_{k}",RUN_SHA)
        self.assertEqual(len(ZIP_SHA256),64)
        self.assertEqual(len(ZIP_MD5),32)

    def test_reuses_frozen_parent_not_a_rewritten_model(self):
        origin=Path(__file__).resolve().parent.parent/"WSP-184"/"physical_context.py"
        self.assertEqual(Path(prior.__file__).resolve(),origin)
        self.assertEqual(prior.FIRST_WINDOW,200)
        self.assertEqual(prior.THRESHOLD,1.5)
        self.assertEqual(prior.PATIENCE,3)
        self.assertEqual(prior.REG,0.01)
        self.assertEqual(prior.GAIN,0.2)

    def test_source_failure_before_numerical_read_or_training(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"bad.zip"
            path.write_bytes(b"deliberately invalid publicly sourced recording")
            with self.assertRaisesRegex(ValueError,"ORIGINAL_SOURCE_HASH"):
                admit_public_source(path)
        with self.assertRaisesRegex(ValueError,"ZIP_SIZE"):
            admit_public_source(Path("/not-present-public-source.zip"))

    def test_no_original_source_imports_or_network_or_hidden_regime_forecast(self):
        source=Path(__file__).with_name("physical_wsp186.py").read_text("utf-8")
        tree=ast.parse(source)
        names={x.name.split(".")[0] for node in ast.walk(tree)
               if isinstance(node,ast.Import) for x in node.names}
        names|={node.module.split(".")[0] for node in ast.walk(tree)
                if isinstance(node,ast.ImportFrom) and node.module}
        self.assertFalse(names & {"requests","numpy","pandas","torch","gym",
                                  "causalchamber","boto3","openai","subprocess"})
        for forbidden in ("urlopen(", "source_env.step(", "source_env.reset(",
                          "remote_lab.execute(", "source_first_use_authority"):
            self.assertNotIn(forbidden,source)
        self.assertIn("prior.train_fit(fit)",source)
        self.assertIn("prior.evaluate_runs(dev, model)",source)

    def test_conservative_max_control_is_reported_not_selected_by_dev(self):
        source=Path(__file__).with_name("physical_wsp186.py").read_text("utf-8")
        self.assertIn("best_valid_control = min(prior.CONTROLS",source)
        self.assertIn("min(changed_first[",source)
        self.assertIn("for name in prior.CONTROLS",source)
        self.assertIn("original_source_actions",source)
        self.assertIn('"scientific_pass":False',source)


if __name__=="__main__":
    unittest.main()
