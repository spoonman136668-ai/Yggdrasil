"""Engineering-only proof of 8 native-cell retained registers and custody."""
import hashlib
import json
import unittest
from yggdrasil.itd02_native_task_bridge_dev import (
    NativeTaskRingBridgeDev, SCHEMA
)
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, CELLS

class LocalRegisterTests(unittest.TestCase):
    def test_real_retention_per_public_transition_and_frozen_veto(self):
        self.assertEqual(SCHEMA,"ygg.itd02.native_task_ring_bridge.source_only.v6")
        m=NativeTaskRingBridgeDev()
        self.assertEqual(m.cell_trace,[0.]*CELLS)
        m.start_observation("LRV")
        m.accept_public_transition("Backup","Nothing",10,terminal=True)
        self.assertEqual(m.transitions,1)
        self.assertEqual(len(m.cell_trace),8)
        from yggdrasil.itd02_native_task_bridge_dev import _temporal_public_bits, RING
        bits=_temporal_public_bits("LRV","Backup",0)
        self.assertEqual(m.cell_trace,[
            .125*(2*bits[RING[i][0]]-1)+.125*(2*bits[RING[i][1]]-1)
            for i in range(CELLS)])
        prior=list(m.cell_trace)
        m.start_observation("MRV")
        m.accept_public_transition("TurnAround","Nothing",0,terminal=True)
        self.assertNotEqual(prior,m.cell_trace)
        ids=m.model_identities()
        m.start_frozen_evaluation(ids["native"],ids["memory"])
        before=list(m.cell_trace)
        m.start_observation("Nothing")
        with self.assertRaisesRegex(ValueError,"FITTING_FORBIDDEN"):
            m.accept_public_transition("GoForward","Nothing",10,learning=True)
        self.assertEqual(before,m.cell_trace)
        m.accept_public_transition("GoForward","Nothing",0,learning=False,terminal=True)
        self.assertEqual(before,m.cell_trace)

    def test_v4_roundtrip_and_historical_v3_schema_denial(self):
        m=NativeTaskRingBridgeDev()
        for i in range(5):
            m.start_observation("LRV")
            m.accept_public_transition(ACTIONS[i%3],"Nothing",10,terminal=True)
        raw=m.checkpoint()
        restored=NativeTaskRingBridgeDev.restore(raw)
        self.assertEqual(restored.cell_trace,m.cell_trace)
        self.assertEqual(restored.model_identities(),m.model_identities())
        self.assertEqual(restored.transitions,m.transitions)
        legacy=json.loads(raw)
        legacy["body"]["schema"]="ygg.itd02.native_task_ring_bridge.source_only.v3"
        legacy["sha256"]=hashlib.sha256(json.dumps(
            legacy["body"],sort_keys=True,separators=(",",":"),
            allow_nan=False).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,"UNTRUSTED"):
            NativeTaskRingBridgeDev.restore(json.dumps(legacy).encode())

    def test_tampered_cell_value_outside_bound_fail_closed(self):
        m=NativeTaskRingBridgeDev()
        o=json.loads(m.checkpoint())
        o["body"]["cell_trace"][3]=1.4
        o["sha256"]=hashlib.sha256(json.dumps(
            o["body"],sort_keys=True,separators=(",",":"),
            allow_nan=False).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,"UNTRUSTED"):
            NativeTaskRingBridgeDev.restore(json.dumps(o).encode())

    def test_one_native_training_event_per_transition(self):
        m=NativeTaskRingBridgeDev()
        for i in range(11):
            m.start_observation("MRV")
            m.accept_public_transition("Backup","Nothing",-3,terminal=True)
        self.assertEqual(m.native.core.events,11)
        self.assertEqual(m.memory.updates,11)
        self.assertEqual(m.transitions,11)
        self.assertTrue(all(-1<=x<=1 for x in m.cell_trace))

if __name__=="__main__":
    unittest.main()
