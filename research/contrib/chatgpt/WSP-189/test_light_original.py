"""WSP189 source-free tests and frozen prior model/reference custody."""
from __future__ import annotations
import ast
from pathlib import Path
import tempfile
import unittest

from light_original import (FIT_STOP,ROWS,SHA,admit,parse_original,prior)


class OriginalPhysicalCohortTests(unittest.TestCase):
    def test_metadata_qualified_source_and_new_frozen_cohort(self):
        self.assertEqual(ROWS,{"actuators_white":20000,
                               "color_mix":10000,
                               "smooth_polarizers":10000})
        self.assertEqual(FIT_STOP,14000)
        self.assertEqual(len(SHA),3)
        self.assertEqual(prior.RANK,2)
        self.assertEqual(prior.THRESHOLD,2.0)
        self.assertEqual(prior.PATIENCE,3)

    def test_previous_predictive_algorithm_is_imported_unchanged(self):
        original=Path(__file__).resolve().parent.parent/"WSP-187"/"light_state.py"
        self.assertEqual(Path(prior.__file__).resolve(),original)
        self.assertTrue(original.is_file())
        self.assertEqual(prior.FEAT,12)

    def test_untrusted_archive_cannot_reach_model_training(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"original.zip"
            p.write_bytes(b"untrusted source")
            with self.assertRaisesRegex(ValueError,"SOURCE_ZIP_HASH"):
                admit(p)
        header=",".join(prior.INPUTS+prior.OUTPUTS)+"\n"
        values=",".join(["0"]*10)+"\n"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_ROWS"):
            parse_original((header+values).encode(),"actuators_white")
        with self.assertRaisesRegex(ValueError,"ORIGINAL_COLUMNS"):
            parse_original(b"red,blue\n0,1\n","actuators_white")

    def test_no_new_source_environment_or_network_imports(self):
        p=Path(__file__).with_name("light_original.py")
        source=p.read_text("utf-8")
        imports={i.name.partition(".")[0] for n in ast.walk(ast.parse(source))
                 if isinstance(n,ast.Import) for i in n.names}
        self.assertFalse(imports&{"requests","pandas","numpy","torch","gym",
                                  "causalchamber","boto3","openai"})
        for bad in ("urlopen(","source_env.step(","source_env.reset(",
                    "source_first_use_authority","model.train_original("):
            self.assertNotIn(bad,source)
        self.assertIn("prior.fit(base[:FIT_STOP])",source)
        self.assertIn("prior.score(base,model,start=FIT_STOP)",source)


if __name__=="__main__":
    unittest.main()
