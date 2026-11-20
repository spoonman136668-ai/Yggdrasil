"""RD05 retrospective source-only support audit, no model training."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research/contrib/chatgpt/YGG-CAP04/rd05_source_support.py"
spec = importlib.util.spec_from_file_location("cap04_rd05_support", SRC)
rd05 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd05)


class RD05SourceOnlyMechanismAudit(unittest.TestCase):
    def test_original_source_pins_exact_and_chronological(self):
        self.assertEqual(rd05.N, 256)
        self.assertEqual(len(rd05.SOURCES), 2)
        for name in rd05.SOURCES:
            with self.subTest(source=name):
                rows = rd05.source(name)
                self.assertEqual(rd05.sha(rd05.canonical(rows)),
                                 rd05.EXPECTED_SOURCE[name])
                self.assertEqual(len({r["id"] for r in rows}), 256)
                keys = rd05.keys(rows)
                self.assertEqual(len(keys), 256)
                previous = (0,0)
                for t, (base, full, y) in enumerate(keys):
                    self.assertEqual(full[1], previous)
                    self.assertEqual(full[0], base)
                    self.assertEqual(y, rows[t]["y"])
                    if t > 0:
                        post = rows[t-1]["post"]
                        self.assertEqual(
                            rows[t]["views"],
                            ((post[0],post[1]),(post[1],post[2])))
                    previous = rows[t]["action"]
        for forged in (99917, "99917", "cap04-rd04-source-c"):
            with self.assertRaisesRegex(ValueError, "SOURCE"):
                rd05.source(forged)

    def test_lifetime_table_updates_are_not_aged_by_recent_router(self):
        s = rd05.structural_invariant()
        self.assertEqual(s["pool_and_split_counters"],
                         "lifetime_no_reset_in_observe")
        self.assertEqual(s["recent32_selects_only"],
                         "winner_via_last32_prequential_gains")
        self.assertFalse(s["model_imported"])
        self.assertEqual(len(s["predictor_file_sha256"]),64)

    def test_b_only_prequential_support_before_current_witness(self):
        for name in rd05.SOURCES:
            with self.subTest(source=name):
                rows = rd05.source(name)
                keys = rd05.keys(rows)
                result = rd05.support_report(name)
                self.assertIs(result["scientific_pass"],False)
                self.assertEqual(result["base_key_capacity"],64)
                self.assertEqual(result["historical_key_capacity"],256)
                sample = keys[96:192]
                self.assertEqual(len(sample),96)
                for bucket, sel in (
                    ("prior_all", lambda t: keys[:t]),
                    ("prior_a", lambda t: keys[:64]),
                    ("prior_b", lambda t: keys[64:t])
                ):
                    actual = [sum(prev[1] == keys[t][1] for prev in sel(t))
                              for t in range(96,192)]
                    d = result["b_scored_prior_support"][bucket]
                    self.assertEqual(d["total_prior_witnesses"],sum(actual))
                    self.assertEqual(d["zero_support_rows"],
                                     sum(n==0 for n in actual))
                self.assertGreaterEqual(
                    result["b_scored_rows_with_ambiguous_current_base"],0)
                self.assertLessEqual(
                    result["b_scored_rows_with_ambiguous_current_base"],96)
                report = rd05.audit(rd05.canonical(result))
                self.assertEqual(report["source"], name)
                self.assertFalse(report["scientific_pass"])

    def test_forged_counts_or_scope_fail_closed(self):
        doc = rd05.support_report(rd05.SOURCES[0])
        valid = rd05.canonical(doc)
        rd05.audit(valid)
        for path, value in (
            (("b_scored_prior_support","prior_b","zero_support_rows"), -1),
            (("predictor_structure","pool_and_split_counters"), "forged"),
            (("source_sha256",), "0"*64),
            (("scientific_pass",), True),
            (("previous_pair_selections_historical_rd04",), 7),
        ):
            with self.subTest(path=path):
                copy = json.loads(valid)
                dest = copy
                for key in path[:-1]:
                    dest=dest[key]
                dest[path[-1]]=value
                with self.assertRaisesRegex(ValueError, "AUDIT_INVALID"):
                    rd05.audit(rd05.canonical(copy))


if __name__ == "__main__":
    unittest.main()
