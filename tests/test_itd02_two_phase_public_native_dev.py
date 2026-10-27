"""Two-phase source-free native-local multiplex constraints, not science."""
import hashlib
import json
import unittest

from yggdrasil.itd02_native_task_bridge_dev import (
    NativeTaskRingBridgeDev, _temporal_public_bits, SCHEMA, public_bits
)
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, ACTION_SITES, OBSERVATIONS


class TemporalLocalPublicTests(unittest.TestCase):
    def test_each_reward_cell_sees_unique_15_contexts_across_two_phases(self):
        self.assertEqual(SCHEMA,"ygg.itd02.native_task_ring_bridge.source_only.v3")
        neighborhoods={
            0:(7,1),
            2:(1,3),
            5:(4,6)
        }
        for site,neighbors in neighborhoods.items():
            words={}
            for action in ACTIONS:
                for obs in OBSERVATIONS:
                    frames=[_temporal_public_bits(obs,action,phase) for phase in (0,1)]
                    for phase in (0,1):
                        self.assertEqual(len(frames[phase]),8)
                        self.assertEqual([frames[phase][s] for s in ACTION_SITES],[0,0,0])
                        self.assertTrue(all(type(v) is int and v in (0,1)
                                            for v in frames[phase]))
                    local=tuple(frames[phase][neighbor]
                                for phase in (0,1) for neighbor in neighbors)
                    words[(obs,action)]=local
            self.assertEqual(len(words),15)
            self.assertEqual(len(set(words.values())),15,("LOCAL_TEMPORAL_ALIAS",site))
            self.assertEqual(len({tuple(_temporal_public_bits(obs,act,0)[n]
                                        for n in neighbors)
                                  for obs in OBSERVATIONS for act in ACTIONS}),4)

    def test_public_original_wire_still_legal_and_no_global_prediction_oracle(self):
        for obs in OBSERVATIONS:
            for act in ACTIONS:
                self.assertEqual(sum(public_bits(obs,act)),2)
                for phase in (0,1):
                    self.assertTrue(set(_temporal_public_bits(obs,act,phase))<={0,1})
        with self.assertRaisesRegex(ValueError,"INVALID_PUBLIC_ENCODING_PHASE"):
            _temporal_public_bits("LRV","Backup",2)
        with self.assertRaises(ValueError):
            _temporal_public_bits("private_hidden","Backup",0)
        with self.assertRaises(ValueError):
            _temporal_public_bits("LRV","unlisted_action",1)

    def test_native_events_alternate_phases_one_reward_per_public_transition(self):
        m=NativeTaskRingBridgeDev()
        original=m.native.observe
        seen=[]
        def watch(bits,outcome,*args,**kwargs):
            seen.append(tuple(bits))
            return original(bits,outcome,*args,**kwargs)
        m.native.observe=watch
        for i in range(6):
            m.start_observation("LRV")
            m.accept_public_transition("Backup","Nothing",10,terminal=True)
            self.assertEqual(seen[-1],tuple(_temporal_public_bits("LRV","Backup",i%2)))
            self.assertEqual(m.transitions,i+1)
            self.assertEqual(m.native.core.events,i+1)
        self.assertEqual(len(seen),6)
        # Trainable native weights and retained cell memory really evolved.
        self.assertEqual(m.memory.updates,6)

    def test_checkpoint_v3_retains_phase_and_rejects_v2_semantics(self):
        m=NativeTaskRingBridgeDev()
        for i in range(13):
            m.start_observation("MRV")
            act=m.choose()
            m.accept_public_transition(act,"Nothing",10,terminal=True)
        snap=m.checkpoint()
        restored=NativeTaskRingBridgeDev.restore(snap)
        self.assertEqual(restored.transitions,13)
        self.assertEqual(m.model_identities(),restored.model_identities())
        m.start_observation("docked_MRV")
        restored.start_observation("docked_MRV")
        self.assertEqual(m.native_reward_scores(),restored.native_reward_scores())
        self.assertEqual(m.choose(),restored.choose())
        legacy=json.loads(snap)
        legacy["body"]["schema"]="ygg.itd02.native_task_ring_bridge.source_only.v2"
        raw=json.dumps(legacy["body"],sort_keys=True,
                       separators=(",",":"),allow_nan=False).encode()
        legacy["sha256"]=hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError,"UNTRUSTED"):
            NativeTaskRingBridgeDev.restore(json.dumps(legacy).encode())

    def test_frozen_original_training_veto(self):
        m=NativeTaskRingBridgeDev()
        m.start_observation("Nothing")
        m.accept_public_transition("TurnAround","Nothing",-3,terminal=True)
        ids=m.model_identities()
        m.start_frozen_evaluation(ids["native"],ids["memory"])
        m.start_observation("MRV")
        with self.assertRaisesRegex(ValueError,"FITTING_FORBIDDEN"):
            m.accept_public_transition("Backup","Nothing",10,learning=True)
        self.assertEqual(ids,m.model_identities())
        m.accept_public_transition("Backup","Nothing",10,learning=False,terminal=True)


if __name__=="__main__":
    unittest.main()
