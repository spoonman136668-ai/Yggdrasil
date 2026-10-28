"""V11 source-free native eight-cell residuals: locality, source custody, restart."""
import hashlib
import json
import unittest

from yggdrasil.itd02_native_task_bridge_dev import (
    NativeTaskRingBridgeDev, SCHEMA, _canonical, _temporal_public_bits,
    public_outcome, CELLS, RING, ACTIONS,
)


class EightLocalResidualTests(unittest.TestCase):
    def test_all_eight_original_public_cell_targets_train(self):
        m = NativeTaskRingBridgeDev()
        self.assertEqual(SCHEMA, "ygg.itd02.native_task_ring_bridge.source_only.v11")
        self.assertEqual(m.site_residual, [0.] * CELLS)
        self.assertEqual(m.native.neighbors, RING)
        self.assertEqual(len(m.native.core.genome), 3)
        self.assertEqual(len(m.native.core.roles), CELLS)
        bits = _temporal_public_bits("LRV", "Backup", 0)
        original = m.native.predict(bits)
        self.assertEqual(m._calibrated_predictions(bits), original)
        target = public_outcome("Nothing", 10)
        identities = m.model_identities()
        m.start_observation("LRV")
        m.accept_public_transition("Backup", "Nothing", 10, learning=True, terminal=True)
        self.assertEqual((m.native.core.events, m.memory.updates, m.transitions), (1,1,1))
        self.assertEqual(len(m.site_residual), CELLS)
        for i in range(CELLS):
            self.assertAlmostEqual(m.site_residual[i], .05 * (target[i] - original[i]))
            self.assertGreaterEqual(m.site_residual[i], -2.)
            self.assertLessEqual(m.site_residual[i], 2.)
        self.assertNotEqual(m.model_identities(), identities)
        self.assertNotEqual(m._calibrated_predictions(bits), m.native.predict(bits))

    def test_cold_checkpoint_and_legacy_v8_rejected(self):
        m = NativeTaskRingBridgeDev()
        for _ in range(12):
            m.start_observation("docked_LRV")
            chosen = m.choose()
            self.assertIn(chosen, ACTIONS)
            m.accept_public_transition(chosen, "Nothing", 10 if chosen == "Backup" else -3,
                                       terminal=True)
        raw = m.checkpoint()
        r = NativeTaskRingBridgeDev.restore(raw)
        self.assertEqual(r.checkpoint(), raw)
        self.assertEqual(r.site_residual, m.site_residual)
        self.assertEqual(r.native.core.events,12)
        self.assertEqual(r.memory.updates,12)
        legacy = json.loads(raw)
        legacy["body"]["schema"] = "ygg.itd02.native_task_ring_bridge.source_only.v8"
        legacy["body"].pop("site_residual")
        legacy["body"].pop("frozen_site_residual_sha256")
        legacy["sha256"] = hashlib.sha256(_canonical(legacy["body"])).hexdigest()
        with self.assertRaisesRegex(ValueError, "UNTRUSTED"):
            NativeTaskRingBridgeDev.restore(json.dumps(legacy).encode())

    def test_tamper_frozen_and_precommit_veto(self):
        m = NativeTaskRingBridgeDev()
        m.start_observation("MRV")
        m.accept_public_transition("GoForward", "Nothing", -3, terminal=True)
        ids = m.model_identities()
        m.start_frozen_evaluation(ids["native"], ids["memory"])
        frozen = m.checkpoint()
        g = NativeTaskRingBridgeDev.restore(frozen)
        self.assertEqual(g.checkpoint(), frozen)
        self.assertEqual(g._frozen_site_residual, g._residual_digest())
        g.start_observation("LRV")
        selected = g.choose()
        with self.assertRaisesRegex(ValueError, "FITTING_FORBIDDEN"):
            g.accept_public_transition(selected, "Nothing", 10, learning=True)
        g.accept_public_transition(selected, "Nothing", 10, learning=False, terminal=True)
        self.assertEqual(g.site_residual, m.site_residual)
        tampered = json.loads(frozen)
        tampered["body"]["site_residual"][0] = 100.
        tampered["sha256"] = hashlib.sha256(_canonical(tampered["body"])).hexdigest()
        with self.assertRaisesRegex(ValueError, "UNTRUSTED"):
            NativeTaskRingBridgeDev.restore(json.dumps(tampered).encode())
        reloaded = NativeTaskRingBridgeDev.restore(frozen)
        reloaded.site_residual[0] += .01
        with self.assertRaisesRegex(ValueError, "FROZEN_SITE_RESIDUAL"):
            reloaded.start_observation("LRV")

if __name__ == "__main__":
    unittest.main()
