"""MR8 native model-source integration, not a scientific family/holdout.

Execute unchanged G7A -> G6 -> G5 -> H components from an identical epoch
and test guarded all-or-nothing repair. MR7's real sequential negative stays
separate and must continue to reproduce.
"""
import json
import pathlib
import subprocess
import tempfile
import unittest

from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04i_atomic_pair import NativeAtomicPairRepair


ROOT = pathlib.Path(__file__).resolve().parents[1]


class NativeAtomicTransport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mr8-source-pin-")
        self.addCleanup(self.temp.cleanup)
        self.checkout = pathlib.Path(self.temp.name) / "native"
        subprocess.run(["git", "clone", "--quiet", "--no-hardlinks",
                        "--no-checkout", str(ROOT), str(self.checkout)],
                       capture_output=True, check=True)
        subprocess.run(["git", "-C", str(self.checkout), "config",
                        "core.autocrlf", "false"], capture_output=True, check=True)
        head = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        subprocess.run(["git", "-C", str(self.checkout), "checkout", "--quiet",
                        "--detach", head], capture_output=True, check=True)

    def test_two_real_world_messages_same_epoch_commit_local_roles(self):
        rt = LocalTaskRuntime()
        bits = [1, 0, 1, 0, 1, 0, 1, 0]
        before_intact = list(rt.predict(bits))
        rt.lesion([0])
        pre = rt.snapshot()
        pre_damaged_response = rt.component(bits, 0)
        outcome = NativeAtomicPairRepair(self.checkout, rt).observe_and_repair(
            bits, 0, 0, 5
        )
        self.assertTrue(outcome["changed"], outcome)
        self.assertEqual(outcome["classification"],
                         "ATOMIC_NATIVE_PAIR_TRANSPORT_INTEGRATION_ONLY")
        self.assertEqual(outcome["wire_bytes"], 76)
        self.assertFalse(outcome["external_sensor_attested"])
        self.assertFalse(outcome["functional_regeneration_proven"])
        self.assertEqual(outcome["new_learned_coefficients"], 0)
        self.assertEqual(outcome["matched_all_in_process_cpu_rss"], "NOT_QUALIFIED")
        self.assertEqual(rt.core.events, 2)
        self.assertEqual(rt.steps, 1)
        self.assertEqual(rt.damaged, {0})
        self.assertNotEqual(rt.core.roles[0], [0.0] * 3)
        self.assertNotEqual(rt.component(bits, 0), pre_damaged_response)
        self.assertEqual(rt.core.genome, LocalTaskRuntime.restore(pre).core.genome)
        for other in (2, 3, 4, 5, 6):
            self.assertEqual(rt.core.roles[other],
                             LocalTaskRuntime.restore(pre).core.roles[other])
        self.assertEqual(LocalTaskRuntime.restore(rt.snapshot()).snapshot(),
                         rt.snapshot())
        self.assertEqual(len(before_intact), 8)
        print("MR8_NATIVE_ATOMIC_PAIR=" + json.dumps({
            "result": "NATIVE_SAME_EPOCH_PRODUCER_TO_REPAIR_EXECUTED",
            "source_commit": outcome["source_commit"],
            "messages": outcome["messages"],
            "wire_bytes": outcome["wire_bytes"],
            "damaged_role_updated": True,
            "native_task_response_delta": rt.component(bits, 0) - pre_damaged_response,
            "original_intact_roles_untouched_except_sender_learning": True,
            "original_genome_unchanged": True,
            "cold_restart_equivalent": True,
            "new_learned_coefficients": 0,
            "source_simulated_external_attestation": False,
            "functional_recovery": "NOT_PROVEN",
            "strong_control_and_matched_resource": "NOT_QUALIFIED",
            "scientific_first_use": False,
        }, sort_keys=True))

    def test_opposing_native_sender_residuals_abstain_without_mutation(self):
        rt = LocalTaskRuntime()
        rt.lesion([0])
        bits = [0, 0, 1, 0, 1, 0, 0, 0]
        before = rt.snapshot()
        outcome = NativeAtomicPairRepair(self.checkout, rt).observe_and_repair(
            bits, 0, 0, 6
        )
        self.assertFalse(outcome["changed"])
        self.assertEqual(outcome["classification"], "ATOMIC_NATIVE_PAIR_ABSTAINED")
        self.assertEqual(rt.snapshot(), before)
        self.assertEqual(rt.core.events, 0)

    def test_illegal_source_request_does_not_change_state(self):
        rt = LocalTaskRuntime()
        rt.lesion([0])
        baseline = rt.snapshot()
        for args in (
            ([0] * 7, 0, 0, 1),
            ([0] * 8, 2, 0, 1),
            ([0] * 8, 0, 2, 1),
            ([0] * 8, 0, 0, -1),
        ):
            with self.assertRaises(ValueError):
                NativeAtomicPairRepair(self.checkout, rt).observe_and_repair(*args)
        self.assertEqual(rt.snapshot(), baseline)


if __name__ == "__main__":
    unittest.main()
