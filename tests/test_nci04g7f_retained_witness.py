"""NCI-04G7F: fixed-budget distributed native functional witness.

Two admissible, otherwise indistinguishable after-lesion worlds differ in an
internal PRE-lesion model response. The target emits one observed response bit
while alive; a pair of surviving cells persists the bit. This does not mean
the target phenotype or any novel task function was reconstructed.
"""
import dataclasses
import json
import pathlib
import time
import unittest

from yggdrasil.developmental import K, N, softmax
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g7d_native_lesion import NativeNeighborLesionObserver
from yggdrasil.nci04g7f_retained_witness import (
    PROBE, retain_native_probe, read_retained_probe,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]


def counterfactual_worlds():
    a = LocalTaskRuntime()
    b = LocalTaskRuntime()
    a.core.roles[0] = [12.,-12.,-12.]
    b.core.roles[0] = [-12.,-12.,12.]
    return a, b


class FixedBudgetRetainedWitness(unittest.TestCase):
    def test_two_functional_worlds_become_distinguishable_after_lesion(self):
        worlds = counterfactual_worlds()
        responses = [r.component(PROBE,0) for r in worlds]
        self.assertGreater(responses[0],0.5)
        self.assertLess(responses[1],0.5)
        bits = []
        snapshots_before = []
        snapshots_after = []
        process_start = time.process_time_ns()
        for world in worlds:
            core_shape = (len(world.core.genome),len(world.core.genome[0]),
                          len(world.core.roles), len(world.core.roles[0]))
            baseline = (world.component(PROBE,1),world.component(PROBE,7))
            routes = (softmax(world.core.roles[1]),softmax(world.core.roles[7]))
            snapshots_before.append(len(world.snapshot().encode()))
            receipt = retain_native_probe(world, ROOT, 0)
            self.assertEqual(receipt.kind,"NATIVE_MODEL_OUTPUT_NOT_EXTERNAL_TASK_TRUTH")
            self.assertEqual(len(receipt.source_commit),40)
            self.assertEqual((world.component(PROBE,1),world.component(PROBE,7)),
                             baseline)
            for i,old in zip((1,7),routes):
                self.assertTrue(all(abs(a-b)<1e-12 for a,b in
                                    zip(softmax(world.core.roles[i]),old)))
            NativeNeighborLesionObserver(world,ROOT).intervene_and_measure(7,0)
            after = world.snapshot()
            copy = LocalTaskRuntime.restore(after)
            self.assertEqual(copy.snapshot(),after)
            readout = read_retained_probe(copy,0)
            self.assertEqual(readout.status,"RETAINED_NATIVE_PROBE_BIT")
            self.assertFalse(readout.complete_function_recovery)
            self.assertEqual(readout.bit,receipt.retained_bit)
            self.assertEqual((len(copy.core.genome),len(copy.core.genome[0]),
                              len(copy.core.roles),len(copy.core.roles[0])),core_shape)
            bits.append(readout.bit)
            snapshots_after.append(len(after.encode()))
            self.assertEqual(copy.core.roles[0],[0.]*K)
            self.assertEqual(copy.core.events,0)
        self.assertEqual(bits,[1,0])
        report={
            "gate":"NCI-04G7F-Y",
            "native_prelesion_model_responses":responses,
            "postlesion_distinguishable_retained_bits":bits,
            "two_survivors_use_existing_role_coefficients":True,
            "genome_coefficients":3*7,
            "existing_role_coefficients":N*K,
            "new_trainable_coefficients":0,
            "prelesion_snapshot_bytes":snapshots_before,
            "postlesion_snapshot_bytes":snapshots_after,
            "witness_message_and_cpu_full_budget":"NOT_QUALIFIED",
            "event_custody_replay":"NOT_QUALIFIED",
            "native_task_correctness":"NOT_INDEPENDENTLY_MEASURED",
            "recoverable_function_scope":"ONE_FROZEN_PROBE_BIT_ONLY",
            "full_function_regeneration":"NOT_PROVEN",
            "transfer_to_unfamiliar_native_task":"NOT_PROVEN",
            "scientific_first_use":False,
            "classification":"BOUNDED_LOCAL_WITNESS_DEVELOPMENT_PASS__SCIENTIFIC_NO_GO",
            "parent_cpu_ns":time.process_time_ns()-process_start,
        }
        print("NCI04G7F_RETENTION_REPORT="+json.dumps(report,sort_keys=True))

    def test_no_witness_ambiguous_or_missing_neighbor_abstains(self):
        empty=LocalTaskRuntime()
        empty.lesion([0])
        self.assertEqual(read_retained_probe(empty,0).status,
                         "ABSTAIN_MISSING_WITNESS_MARKER")
        present=LocalTaskRuntime()
        retain_native_probe(present,ROOT,0)
        present.lesion([0])
        self.assertEqual(read_retained_probe(present,0,tuple(0 for _ in PROBE)).status,
                         "ABSTAIN_UNSEEN_PROBE")
        present.core.roles[1]=[0.]*K
        self.assertEqual(read_retained_probe(present,0).status,
                         "ABSTAIN_MISSING_WITNESS_MARKER")
        present=LocalTaskRuntime()
        retain_native_probe(present,ROOT,0)
        present.lesion([0,1])
        self.assertEqual(read_retained_probe(present,0).status,
                         "ABSTAIN_WITNESS_UNAVAILABLE")

    def test_source_and_budget_constraints_are_transactional(self):
        original=LocalTaskRuntime()
        original.core.roles[7]=[1.,1.,1.]
        start=original.snapshot()
        with self.assertRaisesRegex(ValueError,"occupied native common mode"):
            retain_native_probe(original,ROOT,0)
        self.assertEqual(original.snapshot(),start)
        healthy=LocalTaskRuntime()
        start=healthy.snapshot()
        with self.assertRaises(ValueError):
            retain_native_probe(healthy,ROOT,True)
        self.assertEqual(healthy.snapshot(),start)
        with self.assertRaises(TypeError):
            retain_native_probe(object(),ROOT,0)
        with self.assertRaises(ValueError):
            read_retained_probe(healthy,0,())
        with self.assertRaises(ValueError):
            retain_native_probe(healthy,ROOT.parent,0)
        self.assertEqual(healthy.snapshot(),start)

if __name__=="__main__":
    unittest.main()
