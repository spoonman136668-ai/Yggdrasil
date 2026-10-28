"""V23 source-only sparse unfamiliar mapping, no leakage, lesion controls."""
import itertools
import json
import math
import unittest

from research.itd02_v18_intermediate_plasticity_audit import target as source_target
from research.itd02_v23_unfamiliar_mapping_audit import (
    ACTIONS, CELLS, CONTEXTS, FAMILIES, PUBLIC_CUES,
    EDGE_LESION, damaged_scalar, damaged_readout, episode,
    evaluate, features80, new_target, target_split,
)
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev


class V23UnfamiliarSyntheticMappingTests(unittest.TestCase):
    def test_disjoint_target_labels_and_source_family_separation(self):
        observed,heldout=target_split()
        self.assertEqual(len(observed),12)
        self.assertEqual(len(heldout),24)
        self.assertEqual(len(set(observed)),12)
        self.assertEqual(set(observed)|set(heldout),set(CONTEXTS))
        self.assertFalse(set(observed)&set(heldout))
        self.assertEqual({x[2] for x in observed},set(ACTIONS))
        self.assertEqual(len(FAMILIES),2)
        for family in FAMILIES:
            diff=0
            for case in CONTEXTS:
                y=new_target(family,*case)
                self.assertTrue(-4<=y<=4)
                self.assertTrue(math.isfinite(y))
                diff+=abs(y-source_target(*case,nonlinear=True))
            self.assertGreater(diff,1.0)
            self.assertEqual(len({new_target(family,*c) for c in CONTEXTS})>1,True)
        for context in CONTEXTS:
            self.assertEqual(len(features80(*context)),80)
        with self.assertRaises(ValueError):
            new_target("private_world",*CONTEXTS[0])

    def test_ring_edge_lesion_is_only_original_one_edge(self):
        self.assertEqual(EDGE_LESION,frozenset((0,1)))
        for source_site in range(CELLS):
            values=[0.0]*CELLS
            values[source_site]=1.0
            self.assertEqual(damaged_scalar(values,hops=0),values)
            original=damaged_scalar(values,hops=4)
            damaged=damaged_scalar(values,broken=True,hops=4)
            self.assertAlmostEqual(sum(original),1.0,places=12)
            self.assertLessEqual(sum(damaged),1.0+1e-12)
            self.assertTrue(all(x>=0 for x in damaged))
        for bad_hops in (-1,5,True):
            with self.assertRaises(AssertionError):
                damaged_scalar([0.0]*CELLS,hops=bad_hops)
        m=SharedContextRingDev()
        m.start_observation("LRV")
        m.accept_first("Backup")
        before=m.checkpoint()
        with self.assertRaises(TypeError):
            m.accept_second("GoForward",0.5,private_target="secret")
        self.assertEqual(before,m.checkpoint())
        m.accept_second("GoForward",1.0)
        cloned=SharedContextRingDev.restore(m.checkpoint())
        cloned.start_frozen_evaluation()
        cloned.start_observation("MRV")
        cloned.accept_first("GoForward")
        context=("MRV","GoForward","Backup")
        predicted=cloned.score("Backup")
        intact,lesion,zero=damaged_readout(cloned,context)
        self.assertAlmostEqual(predicted,intact,places=10)
        self.assertTrue(all(math.isfinite(x) for x in (intact,lesion,zero)))
        cloned.accept_second("Backup",0.0,learning=False)

    def test_no_target_feedback_during_frozen_readout_and_checkpoint(self):
        target_context=("docked_MRV","Backup","TurnAround")
        m=SharedContextRingDev(mode="shared")
        source=source_target(*target_context,nonlinear=True)
        episode(m,target_context,source,fit=True)
        checkpoint=m.checkpoint()
        self.assertEqual(
            SharedContextRingDev.restore(checkpoint).checkpoint(),checkpoint)
        before=m.parameters_sha256()
        predictions=evaluate(
            m,[target_context],
            lambda *c:new_target("cue_second",*c))
        self.assertEqual(len(predictions),1)
        self.assertEqual(m.parameters_sha256(),before)
        self.assertEqual(m.checkpoint(),checkpoint)
        frozen=SharedContextRingDev.restore(checkpoint)
        frozen.start_frozen_evaluation()
        frozen.start_observation(target_context[0])
        frozen.accept_first(target_context[1])
        with self.assertRaises(ValueError):
            frozen.accept_second(
                target_context[2],new_target("cue_second",*target_context),
                learning=True)
        frozen.accept_second(target_context[2],0.0,learning=False)
        self.assertEqual(frozen.parameters_sha256(),before)
        tampered=json.loads(checkpoint)
        tampered["body"]["cell_weights"][0][0]=99
        with self.assertRaises(ValueError):
            SharedContextRingDev.restore(json.dumps(tampered).encode())


if __name__=="__main__":
    unittest.main()
