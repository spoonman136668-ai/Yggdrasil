"""NCI-04H: small native local-repair necessary-condition tests.

These tests validate real LocalTaskRuntime role updates and abstention;
they do not claim recovered lost functionality or unseen-task transfer.
"""
import copy
import json
import unittest
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g5_local_residual import LocalResidualAdapter
from yggdrasil.nci04h_local_repair import LocalCausalRepair

class NativeLocalRecovery(unittest.TestCase):
    def test_local_residual_messages_change_only_damaged_role(self):
        rt=LocalTaskRuntime()
        rt.lesion([0])
        src=rt.snapshot()
        adapter=LocalResidualAdapter(rt)
        packet1=adapter.emit(0,1,(1,0,1),1,1)
        packet7=adapter.emit(0,7,(1,0,1),1,1)
        genome=copy.deepcopy(rt.core.genome)
        intact=copy.deepcopy(rt.core.roles[1:])
        result=LocalCausalRepair(rt).observe_and_recover(
            0,(0,1,1),[packet1,packet7],src)
        self.assertTrue(result["changed"])
        self.assertFalse(result["abstained"])
        self.assertEqual(result["wire_bytes"],76)
        self.assertEqual(result["fixed_native_role_coefficients"],24)
        self.assertNotEqual(rt.core.roles[0],[0.]*3)
        self.assertEqual(rt.core.roles[1:],intact)
        self.assertEqual(rt.core.genome,genome)
        self.assertEqual(sum(map(len,rt.core.genome))+
                         sum(map(len,rt.core.roles)),45)
        new=rt.snapshot()
        self.assertEqual(LocalTaskRuntime.restore(new).snapshot(),new)
        with self.assertRaises(ValueError):
            LocalCausalRepair(rt).observe_and_recover(
                0,(0,1,1),[packet1,packet7],src)
        print("NCI04H_YGGDRASIL_NATIVE_LOCAL_UPDATE="+json.dumps({
            "result":"PASS","messages":2,"wire_bytes":76,
            "new_learned_coefficients":0,
            "surviving_neighbor_roles_unchanged":True,
            "shared_genome_unchanged":True,
            "restart_equivalent":True,
            "source":"existing LocalTaskRuntime sender predictions, not external verified sensor",
            "scientific_transfer":"NOT_PROVEN"}))

    def test_nonidentifiable_contradictions_and_missing_neighbors_abstain(self):
        rt=LocalTaskRuntime()
        rt.lesion([0])
        src=rt.snapshot()
        adapter=LocalResidualAdapter(rt)
        plus=adapter.emit(0,1,(0,0,0),1,1)
        minus=adapter.emit(0,7,(0,0,0),0,1)
        result=LocalCausalRepair(rt).observe_and_recover(
            0,(0,0,0),[plus,minus],src)
        self.assertTrue(result["abstained"])
        self.assertEqual(rt.snapshot(),src)
        with self.assertRaises(ValueError):
            LocalCausalRepair(rt).observe_and_recover(
                0,(0,0,0),[plus,plus],src)
        with self.assertRaises(ValueError):
            LocalCausalRepair(rt).observe_and_recover(
                0,(0,0,0),[plus],src)
        with self.assertRaises(ValueError):
            LocalCausalRepair(rt).observe_and_recover(
                0,(0,0,0),[plus,minus],src+" ")
        self.assertEqual(rt.snapshot(),src)
        rt.lesion([7])
        still=rt.snapshot()
        outcome=LocalCausalRepair(rt).observe_and_recover(
            0,(0,0,0),[plus,minus],still)
        self.assertTrue(outcome["abstained"])
        self.assertEqual(rt.snapshot(),still)
if __name__=="__main__":unittest.main()
