"""Bounded whole-process cost telemetry is ENGINEERING data, not science."""
import json
import unittest
from yggdrasil.itd02_local_resource_probe_dev import run_source_free_resource_probe


class SourceFreeCostProbeTests(unittest.TestCase):
    def test_only_bounded_sourcefree_native_learning_reported(self):
        receipt = run_source_free_resource_probe(episodes=2, steps=3)
        self.assertEqual(receipt["schema"],
                         "ygg.itd02.source-free-local-resource-probe.v1")
        self.assertEqual(receipt["evidence_class"],
                         "SOURCE_FREE_HOSTED_CI_ENGINEERING_ONLY")
        self.assertEqual(receipt["public_interactions"], 6)
        self.assertEqual(receipt["authentic_environment_steps"], 0)
        self.assertFalse(receipt["consumer_retail_acceptance"])
        self.assertFalse(receipt["scientific_first_use"])
        for field in (
            "training_and_checkpoint_wall_ns", "training_and_checkpoint_cpu_ns",
            "python_tracemalloc_peak_bytes", "durable_journal_bytes",
            "checkpoint_bytes"
        ):
            self.assertIs(type(receipt[field]), int, field)
            self.assertGreater(receipt[field], 0 if field !=
                               "training_and_checkpoint_cpu_ns" else -1)
        self.assertIsInstance(receipt["native_model_identities"], dict)
        self.assertIsNone(receipt["peak_power_watts"])
        self.assertIsNone(receipt["gpu_vram_bytes"])
        self.assertTrue(receipt["whole_process_peak_rss_bytes"] is None or
                        type(receipt["whole_process_peak_rss_bytes"]) is int)
        self.assertEqual(json.loads(json.dumps(receipt)), receipt)

    def test_budget_overflow_refused_before_any_source(self):
        for episodes, steps in ((0, 1), (5, 1), (1, 0),
                                (1, 129), (True, 1), (1, True)):
            with self.subTest(episodes=episodes, steps=steps):
                with self.assertRaisesRegex(ValueError,
                                            "SOURCE_FREE_METER_BUDGET_INVALID"):
                    run_source_free_resource_probe(
                        episodes=episodes, steps=steps)


if __name__ == "__main__":
    unittest.main()
