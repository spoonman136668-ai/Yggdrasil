"""Source-free bridge engineering tests against genuine Yggdrasil native runtime.

No original Shuttle environment, source transitions, simulator, or scientific
first use is executed. Public tuples below are synthetic interface fixtures.
"""
import json
import subprocess
import sys
import unittest

from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, NativeRingMemoryDev
from yggdrasil.itd02_native_task_bridge_dev import (
    NativeTaskRingBridgeDev, OBSERVATIONS, RING, public_bits, public_outcome,
)


def fit_public(bridge, count=45):
    """Explicit fixture observations/rewards, not an authored environment."""
    for _ in range(count):
        bridge.start_observation("LRV")
        bridge.accept_public_transition("Backup", "MRV", 10, terminal=True)
        bridge.start_observation("Nothing")
        bridge.accept_public_transition("GoForward", "Nothing", -3, terminal=True)


class RealNativeRuntimeBridgeTests(unittest.TestCase):
    def test_actual_native_runtime_and_public_wire_parity(self):
        m = NativeTaskRingBridgeDev()
        self.assertIs(type(m.native), LocalTaskRuntime)
        self.assertEqual(m.native.neighbors, RING)
        self.assertIs(type(m.memory), NativeRingMemoryDev)
        self.assertEqual(len(m.native.core.roles), 8)
        self.assertEqual(len(m.native.core.genome), 3)
        self.assertEqual(set(ACTIONS), {"TurnAround", "GoForward", "Backup"})
        self.assertEqual(len(OBSERVATIONS), 5)
        self.assertEqual(sum(public_bits("Nothing", "Backup")), 2)
        self.assertEqual(sum(public_outcome("MRV", 10)), 2)
        self.assertEqual(public_bits("docked_MRV", "Backup").count(1), 2)
        self.assertEqual(public_outcome("docked_LRV", -3).count(1), 2)

    def test_real_native_parameters_learn_from_public_feedback(self):
        m = NativeTaskRingBridgeDev()
        before_ids = m.model_identities()
        m.start_observation("LRV")
        q_before = m.native_reward_scores()
        m.accept_public_transition("Backup", "MRV", 10, terminal=True)
        self.assertEqual(m.native.core.events, 1)
        self.assertEqual(m.memory.updates, 1)
        self.assertEqual(m.transitions, 1)
        fit_public(m, count=30)
        after_ids = m.model_identities()
        self.assertNotEqual(after_ids["native"], before_ids["native"])
        self.assertNotEqual(after_ids["memory"], before_ids["memory"])
        self.assertEqual(m.native.core.events, 61)
        m.start_observation("LRV")
        q_after = m.native_reward_scores()
        self.assertNotEqual(q_before, q_after)
        self.assertIn(m.choose(), ACTIONS)
        m.accept_public_transition("Backup", "MRV", 0, terminal=True,
                                   learning=True)
        self.assertEqual(m.native.core.events, 62)

    def test_native_predictions_affect_candidate_scores_without_oracle(self):
        m = NativeTaskRingBridgeDev()
        m.start_observation("LRV")
        start_scores = m.native_reward_scores()
        m.accept_public_transition("Backup", "MRV", 10, terminal=True)
        fit_public(m, count=20)
        m.start_observation("LRV")
        changed_scores = m.native_reward_scores()
        self.assertNotEqual(start_scores, changed_scores)
        self.assertEqual(len(changed_scores), len(ACTIONS))
        self.assertTrue(all(-3 <= value <= 10 for value in changed_scores))
        # No separate source model/hidden reward oracle is permitted.
        self.assertNotIn("hidden", set(m.model_identities()))
        m.accept_public_transition("Backup", "MRV", 0, terminal=True)

    def test_frozen_both_models_and_cold_restart_preserve_parameters(self):
        m = NativeTaskRingBridgeDev()
        fit_public(m, count=8)
        sealed = m.model_identities()
        m.start_frozen_evaluation(sealed["native"], sealed["memory"])
        m.start_observation("MRV")
        self.assertIn(m.choose(), ACTIONS)
        with self.assertRaisesRegex(ValueError, "FITTING_FORBIDDEN"):
            m.accept_public_transition("GoForward", "Nothing", -3, learning=True)
        self.assertEqual(m.model_identities(), sealed)
        m.accept_public_transition("GoForward", "Nothing", -3,
                                   learning=False, terminal=True)
        self.assertEqual(m.model_identities(), sealed)
        saved = m.checkpoint()
        restored = NativeTaskRingBridgeDev.restore(saved)
        self.assertEqual(restored.model_identities(), sealed)
        restored.start_frozen_evaluation(sealed["native"], sealed["memory"])
        restored.start_observation("MRV")
        action = restored.choose()
        restored.accept_public_transition(action, "Nothing", 0,
                                          learning=False, terminal=True)
        self.assertEqual(restored.model_identities(), sealed)
        self.assertLess(len(saved), 65536)

    def test_illegal_public_data_and_native_lesions_fail_closed(self):
        m = NativeTaskRingBridgeDev()
        for bad in ("u_wind", "hidden_state", None, {"obs": "Nothing"}):
            with self.assertRaises(ValueError):
                m.start_observation(bad)
        m.start_observation("LRV")
        native_before = m.native.snapshot()
        memory_before = m.memory.checkpoint()
        for action, obs, reward in (
            ("Teleport", "MRV", 10),
            ("Backup", "hidden_state", 10),
            ("Backup", "MRV", 9),
            ("Backup", "MRV", True),
        ):
            with self.subTest(action=action, obs=obs, reward=reward):
                with self.assertRaises(ValueError):
                    m.accept_public_transition(action, obs, reward)
                self.assertEqual(m.native.snapshot(), native_before)
                self.assertEqual(m.memory.checkpoint(), memory_before)
        m.accept_public_transition("Backup", "MRV", 10, terminal=True)
        m.native.lesion([0])
        m.start_observation("MRV")
        with self.assertRaisesRegex(ValueError, "LESION"):
            m.accept_public_transition("Backup", "MRV", 0)
        with self.assertRaisesRegex(ValueError, "REQUIRES_INTACT"):
            NativeTaskRingBridgeDev(native=m.native)

    def test_midtrial_restore_and_tamper_veto(self):
        m = NativeTaskRingBridgeDev()
        fit_public(m, count=2)
        m.start_observation("Nothing")
        original = m.choose()
        snap = m.checkpoint()
        restored = NativeTaskRingBridgeDev.restore(snap)
        self.assertEqual(restored.choose(), original)
        self.assertEqual(restored.model_identities(), m.model_identities())
        tampered = json.loads(snap)
        tampered["body"]["native"]["core"]["events"] += 1
        with self.assertRaisesRegex(ValueError, "UNTRUSTED"):
            NativeTaskRingBridgeDev.restore(json.dumps(tampered).encode())
        script = """
import json,sys
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev
obj=NativeTaskRingBridgeDev.restore(sys.stdin.buffer.read())
print(json.dumps({"action":obj.choose(),"native":obj.model_identities()["native"]}))
"""
        cp = subprocess.run([sys.executable, "-B", "-c", script],
                            input=snap, capture_output=True, timeout=20, check=True)
        got = json.loads(cp.stdout)
        self.assertEqual(got["action"], original)
        self.assertEqual(got["native"], m.model_identities()["native"])

    def test_topology_rejection_is_not_relaxed(self):
        altered = LocalTaskRuntime(neighbors=tuple(
            ((i - 2) % 8, (i + 2) % 8) for i in range(8)))
        with self.assertRaisesRegex(ValueError, "REQUIRES_ORIGINAL"):
            NativeTaskRingBridgeDev(native=altered)


if __name__ == "__main__":
    unittest.main()
