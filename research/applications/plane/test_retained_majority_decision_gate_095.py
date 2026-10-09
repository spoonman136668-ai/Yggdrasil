"""Focused pre-freeze Y095 mechanism tests: no science-data access or evaluation."""
import importlib.util
import os
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parent
R095 = BASE / "exp-dgr-external-cumulative-dependent-pipeline-retained-majority-decision-gate-095.py"
R094 = Path(os.environ.get("Y095_R094_SOURCE", str(BASE / "exp-dgr-external-cumulative-dependent-pipeline-consolidation-consumer-coupling-diagnosis-094.py")))


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


y095 = module(R095, "y095_prefreeze")
y094 = module(R094, "y094_frozen_parent")


def states():
    target = {
        "key": (2, 3, 4, 5), "best": 11, "map_best": 11,
        "total": 9, "best_count": 3, "consistency": 0.75,
        "utility": 2.5, "cell_index": 9,
    }
    retained = {
        "key": (10, 32, 32, 32), "best": 32, "map_best": 32,
        "total": 9, "best_count": 5, "consistency": 0.8,
        "utility": 4.75, "cell_index": 12,
    }
    return target, retained


class TestY095FrozenMechanism(unittest.TestCase):
    def test_exact_three_arm_no_learned_capacity_ceiling(self):
        self.assertEqual(y095.ARMS, ("A0", "A1", "A2"))
        self.assertEqual(y095.CAPACITY, (16, 7, 9))
        self.assertEqual(y095.LEARNED_SCALARS, 0)
        self.assertEqual(y095.EXTERNAL_MODEL_CALLS, 0)

    def test_a0_exact_negative_parent_y094(self):
        target, retained = states()
        actual = y095.project_consumer(target, retained, "A0")
        expected = y094.coupled(target, retained, y094.ARMS[0])
        self.assertEqual(actual, expected)

    def test_a1_exact_retained_endpoint_y094(self):
        target, retained = states()
        actual = y095.project_consumer(target, retained, "A1")
        expected = y094.coupled(target, retained, y094.ARMS[3])
        self.assertEqual(actual, expected)

    def test_a2_coherent_strict_majority_selects_retained(self):
        target, retained = states()
        actual = y095.project_consumer(target, retained, "A2")
        self.assertEqual((actual["best"], actual["map_best"]), (32, 32))
        self.assertEqual(actual["key"], retained["key"])
        self.assertEqual(
            {k: actual[k] for k in y095.CONTINUOUS_FIELDS},
            {k: retained[k] for k in y095.CONTINUOUS_FIELDS},
        )

    def test_a2_half_tie_falls_back_to_target(self):
        target, retained = states()
        retained.update(total=8, best_count=4)
        actual = y095.project_consumer(target, retained, "A2")
        self.assertEqual((actual["best"], actual["map_best"]), (11, 11))

    def test_a2_incoherent_retained_falls_back_to_target(self):
        target, retained = states()
        retained["map_best"] = 17
        actual = y095.project_consumer(target, retained, "A2")
        self.assertEqual((actual["best"], actual["map_best"]), (11, 11))

    def test_a2_no_majority_falls_back_to_target(self):
        target, retained = states()
        retained["best_count"] = 4
        actual = y095.project_consumer(target, retained, "A2")
        self.assertEqual((actual["best"], actual["map_best"]), (11, 11))

    def test_a2_target_projection_sets_map_equal_selected_best(self):
        target, retained = states()
        target["map_best"] = 44
        retained.update(best_count=4, total=9)
        actual = y095.project_consumer(target, retained, "A2")
        self.assertEqual((actual["best"], actual["map_best"]), (11, 11))
        self.assertEqual(y095.project_consumer(target, retained, "A0")["map_best"], 44)

    def test_no_input_mutation_or_hidden_fields(self):
        target, retained = states()
        before_target, before_retained = dict(target), dict(retained)
        for arm in y095.ARMS:
            output = y095.project_consumer(target, retained, arm)
            self.assertIsNot(output, retained)
            self.assertEqual(set(output), set(retained))
            self.assertEqual(output["key"], retained["key"])
        self.assertEqual(target, before_target)
        self.assertEqual(retained, before_retained)

    def test_fail_closed_on_bad_integer_invalid_counts_nonfinite_or_missing(self):
        changes = [
            ("total", 0), ("best_count", -1), ("best_count", 10),
            ("best_count", True), ("best", 32.0), ("map_best", None),
            ("consistency", float("nan")), ("utility", float("inf")),
        ]
        for key, bad in changes:
            with self.subTest(key=key, bad=bad):
                target, retained = states()
                retained[key] = bad
                with self.assertRaises(y095.InvalidConsumerState):
                    y095.project_consumer(target, retained, "A2")
        target, retained = states()
        del retained["key"]
        with self.assertRaises(y095.InvalidConsumerState):
            y095.project_consumer(target, retained, "A0")

    def test_undeclared_arm_fails_closed(self):
        target, retained = states()
        with self.assertRaises(y095.InvalidConsumerState):
            y095.project_consumer(target, retained, "A3")

    def test_no_experiment_runner_or_source_access(self):
        contents = R095.read_text(encoding="utf-8")
        self.assertNotIn("def run(", contents)
        self.assertNotIn("def main(", contents)
        self.assertNotIn("read_bytes(", contents)
        self.assertNotIn("write_text(", contents)
        self.assertNotIn("run_variant(", contents)
        self.assertNotIn("import argparse", contents)


if __name__ == "__main__":
    unittest.main()
