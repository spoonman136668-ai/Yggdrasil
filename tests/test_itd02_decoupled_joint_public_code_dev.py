"""Isolated v3 native-code custody tests. No source-world access."""
import hashlib
import json
import unittest

from yggdrasil.itd02_native_task_bridge_dev import (
    NativeTaskRingBridgeDev, SCHEMA, public_bits, public_outcome
)
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, ACTION_SITES, OBSERVATIONS, OBS_SITES


class SourceFreeJointCodeTests(unittest.TestCase):
    def test_exact_joint_codebook_and_reward_site_disjointness(self):
        self.assertEqual(SCHEMA, "ygg.itd02.native_task_ring_bridge.source_only.v3")
        codes={}
        for observation in OBSERVATIONS:
            for action in ACTIONS:
                bits=public_bits(observation,action)
                self.assertEqual(len(bits),8)
                self.assertTrue(all(v in (0,1) for v in bits))
                self.assertEqual([bits[i] for i in ACTION_SITES],[0,0,0])
                self.assertTrue(all(bits[i]==0 for i in range(8) if i not in OBS_SITES))
                self.assertIn(sum(bits),(2,3))
                codes[(observation,action)]=tuple(bits)
        self.assertEqual(len(codes),15)
        self.assertEqual(len(set(codes.values())),15)
        self.assertEqual([sum(public_bits(obs,"Backup")) for obs in OBSERVATIONS],[2]*5)
        self.assertEqual([sum(public_bits(obs,"GoForward")) for obs in OBSERVATIONS],[3]*5)
        self.assertEqual([sum(public_bits(obs,"TurnAround")) for obs in OBSERVATIONS],[3]*5)

    def test_reward_category_targets_stay_in_original_disjoint_sites(self):
        for reward,site in ((-3,0),(0,2),(10,5)):
            output=public_outcome("Nothing",reward)
            self.assertEqual(output[site],1)
            self.assertEqual([output[x] for x in ACTION_SITES],
                             [int(x==site) for x in ACTION_SITES])

    def test_real_native_checkpoint_v3_cold_restore_and_legacy_v2_veto(self):
        model=NativeTaskRingBridgeDev()
        for _ in range(12):
            model.start_observation("docked_MRV")
            action=model.choose()
            model.accept_public_transition(action,"Nothing",10,terminal=True)
        identities=model.model_identities()
        raw=model.checkpoint()
        restored=NativeTaskRingBridgeDev.restore(raw)
        self.assertEqual(restored.model_identities(),identities)
        self.assertEqual(restored.transitions,12)
        restored.start_observation("MRV")
        self.assertIn(restored.choose(),ACTIONS)
        legacy=json.loads(raw)
        legacy["body"]["schema"]="ygg.itd02.native_task_ring_bridge.source_only.v2"
        envelope=json.dumps(legacy["body"],sort_keys=True,
                            separators=(",",":"),allow_nan=False).encode()
        legacy["sha256"]=hashlib.sha256(envelope).hexdigest()
        with self.assertRaisesRegex(ValueError,"UNTRUSTED"):
            NativeTaskRingBridgeDev.restore(json.dumps(legacy).encode())

    def test_frozen_training_veto_survives_native_code_change(self):
        model=NativeTaskRingBridgeDev()
        model.start_observation("LRV")
        model.accept_public_transition("Backup","Nothing",10,terminal=True)
        identities=model.model_identities()
        model.start_frozen_evaluation(identities["native"],identities["memory"])
        model.start_observation("MRV")
        with self.assertRaisesRegex(ValueError,"FITTING_FORBIDDEN"):
            model.accept_public_transition("Backup","Nothing",10,learning=True,terminal=True)
        self.assertEqual(model.model_identities(),identities)
        model.accept_public_transition("Backup","Nothing",10,learning=False,terminal=True)
        self.assertEqual(model.model_identities(),identities)


if __name__=="__main__":
    unittest.main()
