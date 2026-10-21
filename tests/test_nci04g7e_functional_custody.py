"""NCI-04G7E: native evaluator sees lost phenotype, learner does not.

This is an adversarial necessary-condition test, not new scientific first-use.
"""
import dataclasses
import json
import pathlib
import time
import unittest
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g7e_functional_custody import (
    evaluate_indistinguishable_functional_loss,
)

ROOT=pathlib.Path(__file__).resolve().parents[1]
INPUT=(1,0,0,0,0,0,0,0)

def two_native_functions():
    a=LocalTaskRuntime()
    b=LocalTaskRuntime()
    # Two admissible fixed-size native phenotypes sharing identical genome,
    # environment topology, other-cell state and observation history.
    # This is a counterfactual information proof, NOT claimed to be training.
    a.core.roles[0]=[12.,-12.,-12.]
    b.core.roles[0]=[-12.,-12.,12.]
    return a,b

class G7ENativeFunctionalNoGo(unittest.TestCase):
    def test_actual_output_changes_but_lost_identity_cannot_be_recovered(self):
        a,b=two_native_functions()
        original_a,original_b=a.snapshot(),b.snapshot()
        before_a=a.component(INPUT,0)
        before_b=b.component(INPUT,0)
        self.assertGreater(abs(before_a-before_b),.01)
        start=time.process_time_ns()
        proof=evaluate_indistinguishable_functional_loss(a,b,INPUT,0,7,ROOT)
        process_ns=time.process_time_ns()-start
        self.assertEqual((a.snapshot(),b.snapshot()),(original_a,original_b),
                         "evaluator must not change the provided native worlds")
        self.assertEqual(proof.classification,
                         "ABSTAIN_INFORMATION_THEORETICALLY_UNIDENTIFIABLE")
        self.assertTrue(proof.abstain)
        self.assertTrue(proof.evaluator_only)
        self.assertTrue(proof.surviving_state_identical)
        self.assertTrue(proof.after_repair_state_identical)
        self.assertEqual(proof.repaired_response_a,proof.repaired_response_b)
        self.assertEqual(proof.damaged_response_a,proof.damaged_response_b)
        self.assertGreater(abs(proof.prelesion_response_a-proof.prelesion_response_b),.01)
        self.assertEqual(len(proof.source_commit),40)
        self.assertFalse(hasattr(proof,"recovered_function"))
        envelope={
            "gate":"NCI-04G7E-Y",
            "native_functional_response_before_lesion":[before_a,before_b],
            "native_functional_response_after_lesion":[proof.damaged_response_a,proof.damaged_response_b],
            "native_functional_response_after_local_repair":[proof.repaired_response_a,proof.repaired_response_b],
            "surviving_custody_ambiguous":proof.surviving_state_identical,
            "native_repair_not_given_reference_output":True,
            "information_theoretic_required_abstention":proof.abstain,
            "trusted_external_task_success_measurement":"NOT_AVAILABLE",
            "genuine_function_recovery":"NOT_ESTABLISHED",
            "source_commit":proof.source_commit,
            "evaluator_cpu_ns":process_ns,
            "prelesion_native_snapshot_bytes":[len(original_a.encode()),len(original_b.encode())],
            "evaluator_receipt_bytes":len(json.dumps(dataclasses.asdict(proof)).encode()),
            "paired_end_to_end_candidate_vs_control_cpu_rss":"NOT_QUALIFIED",
            "independently_protected_scientific_first_use":False,
            "classification":"NATIVE_FUNCTIONAL_BEHAVIOR_OBSERVED / IDENTIFIABILITY_NEGATIVE / SCIENTIFIC_NO_GO"
        }
        print("NCI04G7E_NATIVE_FUNCTIONAL_NO_GO="+json.dumps(envelope,sort_keys=True))

    def test_reject_unmatched_information_and_missing_function_contrast(self):
        a,b=two_native_functions()
        b.core.roles[7][0]=1.
        with self.assertRaisesRegex(ValueError,"survivor prelesion information differs"):
            evaluate_indistinguishable_functional_loss(a,b,INPUT,0,7,ROOT)
        self.assertEqual(a.damaged,set())
        self.assertEqual(b.damaged,set())
        a,b=two_native_functions()
        b.core.roles[0]=a.core.roles[0][:]
        with self.assertRaisesRegex(ValueError,"no distinguishable prelesion"):
            evaluate_indistinguishable_functional_loss(a,b,INPUT,0,7,ROOT)

    def test_reject_wrong_owner_or_nonadjacent_witness(self):
        a,b=two_native_functions()
        with self.assertRaises(ValueError):
            evaluate_indistinguishable_functional_loss(a,b,INPUT,0,3,ROOT)
        with self.assertRaises(TypeError):
            evaluate_indistinguishable_functional_loss(a,object(),INPUT,0,7,ROOT)
        with self.assertRaises(ValueError):
            evaluate_indistinguishable_functional_loss(a,b,INPUT,0,True,ROOT)
        self.assertEqual(a.damaged,set())
        self.assertEqual(b.damaged,set())

if __name__=="__main__":
    unittest.main()
