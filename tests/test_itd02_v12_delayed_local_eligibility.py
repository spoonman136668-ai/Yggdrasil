"""Source-only v12 bounded original eight-cell two-step prior-action credit safety."""
import hashlib
import json
import unittest

from yggdrasil.itd02_native_task_bridge_dev import (
    NativeTaskRingBridgeDev, _temporal_public_bits, SCHEMA, RING, CELLS, _canonical,
)


class GenuinePublicTemporalEligibilityTests(unittest.TestCase):
    def test_first_chosen_public_action_is_preserved_and_delayed_full8_fit(self):
        m = NativeTaskRingBridgeDev()
        initial = m.model_identities()
        self.assertIsNone(m.temporal_eligibility)
        self.assertEqual(CELLS, 8)
        self.assertEqual(m.native.neighbors,RING)
        m.start_observation("LRV")
        original=m._task_bits("LRV","Backup",0)
        self.assertEqual(original,_temporal_public_bits("LRV","Backup",0))
        m.accept_public_transition("Backup","Nothing",0,learning=True,terminal=False)
        self.assertEqual(m.native.core.events,1)
        self.assertEqual(m.memory.updates,1)
        self.assertEqual(m.temporal_eligibility,[
            _temporal_public_bits("LRV","Backup",0),
            _temporal_public_bits("LRV","Backup",1)])
        mid=m.checkpoint()
        cold=NativeTaskRingBridgeDev.restore(mid)
        self.assertEqual(cold.checkpoint(),mid)
        for phase in (0,1):
            before=_temporal_public_bits("Nothing","GoForward",phase)
            after=cold._task_bits("Nothing","GoForward",phase)
            self.assertEqual(after,[a^b for a,b in zip(
                before,cold.temporal_eligibility[phase])])
        cold.start_observation("Nothing")
        action=cold.choose()
        cold.accept_public_transition(action,"Nothing",10,learning=True,terminal=True)
        self.assertEqual(cold.native.core.events,2)
        self.assertEqual(cold.memory.updates,2)
        self.assertEqual(cold.transitions,2)
        self.assertIsNone(cold.temporal_eligibility)
        self.assertNotEqual(initial,cold.model_identities())

    def test_previous_public_action_changes_second_step_feature_without_lookup(self):
        a=NativeTaskRingBridgeDev()
        b=NativeTaskRingBridgeDev()
        for m,first in ((a,"Backup"),(b,"TurnAround")):
            m.start_observation("MRV")
            m.accept_public_transition(first,"Nothing",0,learning=True,terminal=False)
        enc_a=a._task_bits("Nothing","GoForward",0)
        enc_b=b._task_bits("Nothing","GoForward",0)
        assert enc_a!=enc_b
        self.assertEqual(len(enc_a),8)
        self.assertEqual(a.native.neighbors,b.native.neighbors)

    def test_frozen_public_history_advances_but_never_trains_weights(self):
        m=NativeTaskRingBridgeDev()
        for action in ("Backup","GoForward","TurnAround"):
            m.start_observation("LRV")
            m.accept_public_transition(action,"Nothing",0,learning=True,terminal=True)
        ids=m.model_identities()
        m.start_frozen_evaluation(ids["native"],ids["memory"])
        m.start_observation("MRV")
        m.accept_public_transition("GoForward","Nothing",0,learning=False,terminal=False)
        self.assertIsNotNone(m.temporal_eligibility)
        self.assertEqual(m.model_identities(),ids)
        checkpoint=m.checkpoint()
        copy=NativeTaskRingBridgeDev.restore(checkpoint)
        self.assertEqual(copy.checkpoint(),checkpoint)
        copy.start_observation("Nothing")
        a=copy.choose()
        with self.assertRaisesRegex(ValueError,"FITTING_FORBIDDEN"):
            copy.accept_public_transition(a,"Nothing",-3,learning=True,terminal=True)
        copy.accept_public_transition(a,"Nothing",-3,learning=False,terminal=True)
        self.assertEqual(copy.model_identities(),ids)
        self.assertIsNone(copy.temporal_eligibility)

    def test_signed_checkpoint_rejects_malformed_temporal_register(self):
        m=NativeTaskRingBridgeDev()
        m.start_observation("LRV")
        m.accept_public_transition("Backup","Nothing",0,terminal=False)
        raw=json.loads(m.checkpoint())
        for bad in ([[0]*8],[["0"]*8,[0]*8],[[2]*8,[0]*8]):
            x=json.loads(json.dumps(raw))
            x["body"]["temporal_eligibility"]=bad
            x["sha256"]=hashlib.sha256(_canonical(x["body"])).hexdigest()
            with self.assertRaisesRegex(ValueError,"UNTRUSTED"):
                NativeTaskRingBridgeDev.restore(json.dumps(x).encode())
        old=json.loads(json.dumps(raw))
        old["body"]["schema"]="ygg.itd02.native_task_ring_bridge.source_only.v8"
        old["body"].pop("temporal_eligibility")
        old["sha256"]=hashlib.sha256(_canonical(old["body"])).hexdigest()
        with self.assertRaisesRegex(ValueError,"UNTRUSTED"):
            NativeTaskRingBridgeDev.restore(json.dumps(old).encode())
        self.assertEqual(SCHEMA,"ygg.itd02.native_task_ring_bridge.source_only.v12")


if __name__=="__main__":
    unittest.main()
