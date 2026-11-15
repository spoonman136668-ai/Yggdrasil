"""FKP-11 static fixtures only: no reserved original Gym DEV episodes opened."""
import hashlib
import unittest
from pathlib import Path
import numpy as np

from study import (
    PublicAssociationMemory, observed_state, paired_ci, source_custody,
    episode, PROTOCOL, PROTOCOL_SHA256, SEEDS, TASKS, ARMS
)

class FixtureTests(unittest.TestCase):
    def test_frozen_protocol_and_research_first_use_fence(self):
        self.assertEqual(hashlib.sha256(PROTOCOL.encode()).hexdigest(),PROTOCOL_SHA256)
        self.assertEqual(SEEDS,tuple(range(971000,971008)))
        self.assertEqual(len(TASKS),2)
        self.assertEqual(len(ARMS),3)
        with self.assertRaises(PermissionError):
            episode(TASKS[0],973000,"curiosity")
        with self.assertRaises(PermissionError):
            episode(TASKS[0],970100,"curiosity")
        with self.assertRaises(PermissionError):
            episode(TASKS[0],SEEDS[0],"oracle")
        with self.assertRaises(PermissionError):
            episode("private-raw-game-world",SEEDS[0],"curiosity")

    def test_public_pixels_only_produce_deterministic_8x8_footprint(self):
        a=np.zeros((84,84,3),dtype=np.uint8)
        first,full,shape=observed_state(a)
        self.assertEqual(len(first),64)
        self.assertEqual(len(full),32)
        self.assertEqual(shape,(84,84,3))
        b=a.copy();b[0,0,:]=255
        second,full2,_=observed_state(b)
        self.assertNotEqual(first,second)
        self.assertNotEqual(full,full2)
        self.assertEqual(observed_state(a)[0],first)
        with self.assertRaises(ValueError):
            observed_state(np.empty((0,),dtype=np.uint8))
        with self.assertRaises(ValueError):
            observed_state(np.array([object()],dtype=object))

    def test_public_action_memory_counts_real_observed_transitions(self):
        memory=PublicAssociationMemory(971000)
        feature=bytes([2]*64)
        other=bytes([3]*64)
        third=bytes([4]*64)
        self.assertEqual(memory.choose(feature,0),971000%9)
        self.assertEqual(memory.choose(feature,1),(971000+1)%9)
        choice=memory.choose(feature,9)
        memory.update(feature,choice,other)
        self.assertEqual(memory.summary()["memory_entries"],1)
        self.assertNotEqual(memory.choose(feature,9),choice)
        memory.update(feature,choice,third)
        report=memory.summary()
        self.assertEqual(report["repeated_state_action_pairs"],1)
        self.assertEqual(report["conflicting_repeated_state_action_outcomes"],1)
        self.assertEqual(sum(report["global_action_counts"]),2)
        self.assertEqual(report["distinct_action_conditioned_transitions"],2)
        with self.assertRaises(ValueError):
            memory.update(feature,9,other)
        with self.assertRaises(ValueError):
            memory.choose(b"short",9)

    def test_paired_context_bootstrap_has_exact_zero_for_identical_controls(self):
        self.assertEqual(paired_ci([0.0]*8),[0.0,0.0])
        ci=paired_ci([0.1]*8)
        self.assertAlmostEqual(ci[0],0.1,places=7)
        self.assertAlmostEqual(ci[1],0.1,places=7)

    def test_unverified_original_source_must_fail_closed(self):
        with self.assertRaises(ValueError):
            source_custody(Path("/nonexistent/fkp11-upstream"))

if __name__=="__main__":
    unittest.main()
