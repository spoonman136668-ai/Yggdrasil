"""V9 source-only action-cell arbitration tests; no owner-world or science."""
import hashlib
import json
import unittest

from yggdrasil.itd02_native_task_bridge_dev import (
    ACTIONS, RING, NativeTaskRingBridgeDev, SCHEMA, _canonical
)


class ActionLocalArbitrationTests(unittest.TestCase):
    def test_selected_output_only_updates_with_public_feedback(self):
        m = NativeTaskRingBridgeDev()
        self.assertEqual(len(m.native.neighbors), 8)
        self.assertEqual(m.native.neighbors, RING)
        self.assertEqual(m.reliability, [0., 0., 0.])
        m.start_observation("LRV")
        m.accept_public_transition("GoForward", "Nothing", 10, terminal=True)
        self.assertEqual(m.reliability[0], 0.)
        self.assertEqual(m.reliability[2], 0.)
        self.assertGreater(abs(m.reliability[1]), 0.)
        self.assertEqual((m.native.core.events,m.memory.updates,m.transitions),(1,1,1))
        self.assertTrue(all(-1 <= v <= 1 for v in m.reliability))

    def test_real_choice_and_exact_cold_restart(self):
        m = NativeTaskRingBridgeDev()
        for _ in range(12):
            m.start_observation("MRV")
            a = m.choose()
            self.assertIn(a, ACTIONS)
            m.accept_public_transition(a, "Nothing", 10 if a == "Backup" else -3,
                                       learning=True, terminal=True)
        original = m.checkpoint()
        cold = NativeTaskRingBridgeDev.restore(original)
        self.assertEqual(cold.checkpoint(), original)
        self.assertEqual(cold.reliability, m.reliability)
        self.assertEqual(cold.model_identities(),m.model_identities())
        self.assertEqual(cold.transitions,12)

    def test_old_schema_and_digest_recomputed_tamper_fail_closed(self):
        m = NativeTaskRingBridgeDev()
        m.start_observation("LRV")
        m.accept_public_transition("Backup","Nothing",10,terminal=True)
        original = json.loads(m.checkpoint())
        for key,value in (("reliability",[2.,0.,0.]),
                          ("reliability",[float("nan"),0.,0.])):
            obj=json.loads(json.dumps(original))
            obj["body"][key]=value
            obj["sha256"]=hashlib.sha256(_canonical(obj["body"])).hexdigest() if value[0] == 2. else "0"*64
            with self.assertRaisesRegex(ValueError,"UNTRUSTED"):
                NativeTaskRingBridgeDev.restore(json.dumps(obj).encode())
        old=json.loads(json.dumps(original))
        old["body"]["schema"]="ygg.itd02.native_task_ring_bridge.source_only.v8"
        old["sha256"]=hashlib.sha256(_canonical(old["body"])).hexdigest()
        with self.assertRaisesRegex(ValueError,"UNTRUSTED"):
            NativeTaskRingBridgeDev.restore(json.dumps(old).encode())
        self.assertEqual(SCHEMA,"ygg.itd02.native_task_ring_bridge.source_only.v9")

    def test_frozen_gate_identity_and_training_veto(self):
        m = NativeTaskRingBridgeDev()
        m.start_observation("LRV")
        m.accept_public_transition("Backup","Nothing",10,terminal=True)
        ids=m.model_identities()
        m.start_frozen_evaluation(ids["native"],ids["memory"])
        snap=m.checkpoint()
        frozen=NativeTaskRingBridgeDev.restore(snap)
        self.assertEqual(snap,frozen.checkpoint())
        frozen.start_observation("MRV")
        selected=frozen.choose()
        with self.assertRaisesRegex(ValueError,"FITTING_FORBIDDEN"):
            frozen.accept_public_transition(selected,"Nothing",10,learning=True)
        frozen.accept_public_transition(selected,"Nothing",10,learning=False,terminal=True)
        self.assertEqual(frozen.reliability,m.reliability)
        bad=NativeTaskRingBridgeDev.restore(snap)
        bad.reliability[0]+=.01
        with self.assertRaisesRegex(ValueError,"FROZEN_RELIABILITY"):
            bad.start_observation("MRV")

if __name__=="__main__":
    unittest.main()
