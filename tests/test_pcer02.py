"""Source-free contract tests, never a native-world scientific trial."""
import copy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / "research/contrib/chatgpt/PCER-02/selector.py"
spec = importlib.util.spec_from_file_location("pcer02_selector", SCRIPT)
pcer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pcer)


def fixture():
    # Source-free invented FIT shape; deliberate asymmetric outcome frequencies.
    cells = [(0, 0, 11, 6), (0, 1, 11, 7),
             (1, 0, 14, 3), (1, 1, 14, 11)]
    all_rows = []
    for public, action, count, positives in cells:
        for j in range(count):
            y = int(j < positives)
            pred = (public * 270_000 + action * 100_000 + j * 18_751) % 1_000_001
            all_rows.append((public, action, y, pred))
    # Shuffle deterministically without changing any per-cell outcome totals.
    all_rows.sort(key=lambda entry: sha256(repr(entry).encode()).hexdigest())
    rows = []
    for i, (context, action, y, prediction) in enumerate(all_rows):
        ident = sha256(f"PCER02-fixture|{i}|{context}|{action}|{y}".encode()).hexdigest()
        rows.append({"id": ident, "phase": i // 32, "origin": "source-free",
                     "views": [[context, 0], [context, 1]],
                     "row": {"s1": context, "x1": action,
                             "s2": y, "x2": 0, "y": y},
                     "prediction": {"native": prediction}})
    return rows


class ConditionalReplayContract(unittest.TestCase):
    def test_frozen_capacity_and_conditional_distribution(self):
        rows = fixture()
        a = pcer.select(rows)
        self.assertTrue(a["fit_engineering_gate_met"])
        self.assertLessEqual(a["fit_max_gap"], 0.1)
        self.assertEqual(len(a["selected"]), 10)
        self.assertEqual(a["active_reference_reduction"], 0.8)
        self.assertEqual(set(a["fit_absolute_gaps"]),
                         {"(0, 0)", "(0, 1)", "(1, 0)", "(1, 1)"})
        self.assertEqual(pcer.select(rows), a)
        self.assertEqual(len(a["controls"]["uniform10"]), 10)
        self.assertEqual(len(a["controls"]["pureerror10"]), 10)
        self.assertEqual(len(a["controls"]["frozen_pcer01_10"]), 10)

    def test_exact_sufficient_statistics_bound(self):
        rows = fixture()
        result = pcer.select(rows)
        for key, (positives, count) in result["controls"]["exact_sufficient_statistics"].items():
            self.assertEqual((positives + 1) / (count + 2),
                             result["full_fit_posterior"][key])
        # Exact four-cell counts can beat approximate witnesses for the
        # Beta-only scoring model: no scientific superiority claim.
        self.assertTrue(any(gap > 0 for gap in result["fit_absolute_gaps"].values()))

    def test_invalid_fits_fail_closed(self):
        rows = fixture()
        for mutation in ("duplicate", "phase", "outcome", "context", "prediction"):
            case = copy.deepcopy(rows)
            if mutation == "duplicate":
                case[1]["id"] = case[0]["id"]
            elif mutation == "phase":
                case[30]["phase"] = 1
            elif mutation == "outcome":
                case[0]["row"]["s2"] = 2
            elif mutation == "context":
                case[0]["views"][1][0] ^= 1
            elif mutation == "prediction":
                case[0]["prediction"]["native"] = 1_000_001
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                pcer.select(case)
        with self.assertRaisesRegex(ValueError, "FIT_LENGTH"):
            pcer.select(rows + [copy.deepcopy(rows[0])])

    def test_cold_manifest_tampering_and_held_isolation(self):
        rows = fixture()
        result = pcer.select(rows)
        self.assertTrue(pcer.cold_verify(rows, result))
        changed = copy.deepcopy(result)
        changed["selected"][0] = "f" * 64
        with self.assertRaisesRegex(ValueError, "COLD_INDEX_DIVERGENCE"):
            pcer.cold_verify(rows, changed)
        # No function receives a held/VALID row; it refuses 96 as a FIT input.
        with self.assertRaisesRegex(ValueError, "FIT_LENGTH"):
            pcer.select(rows + [copy.deepcopy(rows[0]) for _ in range(46)])

    def test_run_pins_original_and_refuses_overwrite(self):
        rows = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "source.json"
            prereg = root / "prereg.json"
            output = root / "output.json"
            held = [{"unread_held_outcome": i % 2} for i in range(46)]
            trace.write_bytes(pcer.canonical(rows + held))
            protocol = {"experiment_id": "PCER-02", "exact_parent_sha": "a" * 40,
                        "source": {"sha256": pcer.digest(trace.read_bytes())}}
            prereg.write_bytes(pcer.canonical(protocol))
            original = trace.read_bytes()
            report = pcer.run(trace, prereg, output)
            self.assertEqual(report["fresh_science"], "NOT_RUN")
            self.assertEqual(original, trace.read_bytes())
            with self.assertRaisesRegex(ValueError, "OUTPUT_EXISTS"):
                pcer.run(trace, prereg, output)
            output.unlink()
            # Same 50 FIT, completely opposite held values: identical selection.
            held = [{"unread_held_outcome": (i + 1) % 2} for i in range(46)]
            trace.write_bytes(pcer.canonical(rows + held))
            with self.assertRaisesRegex(ValueError, "SOURCE_SHA"):
                pcer.run(trace, prereg, output)
            protocol["source"]["sha256"] = pcer.digest(trace.read_bytes())
            prereg.write_bytes(pcer.canonical(protocol))
            fresh = pcer.run(trace, prereg, output)
            self.assertEqual(report["fit_result"], fresh["fit_result"])


if __name__ == "__main__":
    unittest.main()
