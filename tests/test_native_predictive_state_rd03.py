"""CAP04-RD03 retrospective source/selector diagnostics, not new science."""
import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/YGG-CAP04/rd03_diagnostic.py")
spec = importlib.util.spec_from_file_location("cap04_rd03", SOURCE)
rd03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd03)


class RD03RetrospectiveDiagnostics(unittest.TestCase):
    def test_original_score_pins_and_history_gating_report(self):
        for name in rd03.SOURCE_PINS:
            with self.subTest(source=name):
                result = rd03.replay(name)
                proof = rd03.audit(canonical(result))
                self.assertEqual(result["events"], 256)
                self.assertEqual(result["old_rd02_status"],
                                 "RD02_ENGINEERING_NO_GO")
                self.assertEqual(result["source_sha256"],
                                 rd03.SOURCE_PINS[name])
                self.assertTrue(result["prior_score_verified"])
                self.assertIs(proof["scientific_pass"], False)
                self.assertEqual(
                    set(result["phase_results"]), set(rd03.PHASES))
                self.assertEqual(
                    set(result["boundary_evidence"]), {"64", "96", "192", "256"})
                for phase, (a, b) in rd03.PHASES.items():
                    for model in rd03.MODEL_NAMES:
                        stage = result["phase_results"][phase][model]
                        self.assertEqual(
                            sum(stage["selected_features"].values()), b - a)
                        self.assertEqual(
                            set(stage["selected_features"]), set(rd03.FEATURE_NAMES))
                        self.assertEqual(
                            set(stage["terminal_brier"]), set(rd03.METRICS))

    def test_source_and_post_hoc_tampering_rejected(self):
        for forbidden in ("99917", 99917, "cap04-rd02-source-c"):
            with self.assertRaisesRegex(ValueError, "SOURCE_ID"):
                rd03.replay(forbidden)
        report = rd03.replay(rd03.SOURCE_PINS.keys().__iter__().__next__())
        raw = canonical(report)
        self.assertEqual(rd03.audit(raw)["source"], report["source"])
        for path, value in (
                (("phase_results", "b_scored", "direct",
                  "terminal_brier", "selected_terminal"), 0.01),
                (("phase_results", "b_scored", "direct",
                  "selected_features", "none"), 0),
                (("boundary_evidence", "192", "direct",
                  "selected_feature"), "forged_feature")):
            modified = json.loads(raw)
            current = modified
            for key in path[:-1]:
                current = current[key]
            current[path[-1]] = value
            with self.assertRaisesRegex(ValueError, "AUDIT_REJECTED"):
                rd03.audit(canonical(modified))


if __name__ == "__main__":
    unittest.main()
