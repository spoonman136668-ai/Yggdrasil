"""F14 DEV-only public-wire negative tests; no protected worlds or benchmarks."""
import json
import unittest

from f14_boundary import reset_frame, step_frame


class Poison:
    def __getattribute__(self, name):
        raise AssertionError("PRIVATE_EVALUATOR_INFO_ACCESSED")


class BoundaryTests(unittest.TestCase):
    def test_reset_redacts_regime_and_graph(self):
        raw = ([0, 1.25], {"regime": ["hidden"], "get_graph": "secret"})
        packet = reset_frame(raw)
        self.assertEqual(json.loads(packet), {"observation": [0.0, 1.25], "done": False})
        self.assertNotIn("regime", packet)
        self.assertNotIn("get_graph", packet)

    def test_step_redacts_optimal_reward_regret_and_oracle(self):
        raw = ([1, -2.5], 0.75, False, True,
               {"optimal_reward": 99, "regret": 98.25, "answer_key": "PRIVATE"})
        packet = step_frame(raw)
        self.assertEqual(json.loads(packet),
                         {"observation": [1.0, -2.5], "reward": 0.75, "done": True})
        self.assertFalse(any(s in packet for s in ("optimal", "regret", "answer_key")))

    def test_info_is_not_even_inspected(self):
        self.assertEqual(json.loads(reset_frame(([1], Poison())))["observation"], [1.0])
        self.assertEqual(json.loads(step_frame(([1], 1, False, False, Poison())))["reward"], 1.0)

    def test_nonfinite_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError): reset_frame(([bad], {}))
                with self.assertRaises(ValueError): step_frame(([1], bad, False, False, {}))

    def test_no_python_object_graph_allowed(self):
        for bad in (Poison(), {"secret": 7}, [[2]], "hello", [], [1] * 257):
            with self.subTest(kind=type(bad).__name__):
                with self.assertRaises(ValueError): reset_frame((bad, {}))

    def test_boolean_and_non_numeric_rejected(self):
        for bad in (True, "1", None, 3j):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ValueError): reset_frame(([bad], {}))
                with self.assertRaises(ValueError): step_frame(([1], bad, False, False, {}))

    def test_malformed_tuple_and_flags_rejected(self):
        for raw in (([1],), [([1], {})], ()):  # never publish arbitrary object structure
            with self.assertRaises(ValueError): reset_frame(raw)
        for raw in (([1], 1, False, False), ([1], 1, 0, False, {}),
                    ([1], 1, False, "False", {})):
            with self.assertRaises(ValueError): step_frame(raw)

    def test_reproducible_wire_format_and_no_info_dependency(self):
        left = step_frame(([1, 2], 3, False, False, {"regime": 1}))
        right = step_frame(([1, 2], 3, False, False, {"regime": 999}))
        self.assertEqual(left, right)
        self.assertEqual(set(json.loads(left)), {"observation", "reward", "done"})

    def test_numpy_vector_and_scalar_are_supported_if_available(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy not required by F14 boundary")
        packet = step_frame((np.array([0.25, -3], dtype=np.float32),
                             np.float32(1.5), False, False, {}))
        self.assertEqual(json.loads(packet)["observation"], [0.25, -3.0])
        self.assertEqual(json.loads(packet)["reward"], 1.5)
        with self.assertRaises(ValueError): step_frame(([1], np.bool_(True), False, False, {}))


if __name__ == "__main__":
    unittest.main()
