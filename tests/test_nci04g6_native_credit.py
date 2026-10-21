"""NCI-04G6 development-only local credit integration and resource checks."""
import json
import math
import resource
import time
import tracemalloc
import unittest
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g6_native_credit import NativeSurvivorCredit

class StrongLocalCount:
    """Fully trained conventional conditional-count comparator with exactly the
    same local prior and OWN observed next-bit evidence."""
    def __init__(self):
        self.table={}
    def observe(self,prior,own):
        count=self.table.setdefault(tuple(prior),[0,0])
        count[own]+=1
    def predict(self,prior):
        a,b=self.table.get(tuple(prior),(0,0))
        return (b+1)/(a+b+2)
    def budget(self):
        return sum(len(str(k))+16 for k in self.table)

class NCI04G6LocalCredit(unittest.TestCase):
    def test_existing_roles_learn_from_own_measured_residual_only(self):
        runtime=LocalTaskRuntime()
        baseline=StrongLocalCount()
        # Entire pre-lesion dataset is source-free DEVELOPMENT, not scientific.
        for n in range(64):
            bits=[((n+3*i)//(i+1))%2 for i in range(8)]
            outcomes=[bits[(i+1)%8] for i in range(8)]
            runtime.observe(bits,outcomes)
            baseline.observe((bits[7],bits[6],bits[0]),outcomes[7])
        native_before=runtime.snapshot()
        runtime.lesion([0])
        original_genome=json.dumps(runtime.core.genome)
        destroyed_role=list(runtime.core.roles[0])
        original_sender_role=list(runtime.core.roles[7])
        credit=NativeSurvivorCredit(runtime)
        original_coeffs=credit.resource_ledger()
        tracemalloc.start()
        elapsed_candidate=0
        elapsed_control=0
        fixed_messages=0
        candidate_loss=0.
        control_loss=0.
        for n in range(16):
            prior=((n+1)%2,((n//2)+1)%2,(n//4)%2)
            own_next=prior[1] ^ prior[0]
            start=time.process_time_ns()
            estimate=credit.predict_survivor(7,prior)
            msg=credit.observe_own_transition(0,7,prior,own_next,n+1)
            elapsed_candidate+=time.process_time_ns()-start
            start=time.process_time_ns()
            control=baseline.predict(prior)
            baseline.observe(prior,own_next)
            elapsed_control+=time.process_time_ns()-start
            candidate_loss+=(own_next-estimate)**2
            control_loss+=(own_next-control)**2
            fixed_messages+=1
            self.assertEqual(len(msg),38)
        current,peak=tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertNotEqual(original_sender_role,runtime.core.roles[7],
                            "native surviving-role plasticity did not execute")
        self.assertEqual(destroyed_role,runtime.core.roles[0],
                         "damaged receiver was illegally retrained")
        self.assertEqual(original_genome,json.dumps(runtime.core.genome),
                         "survivor observation overwrote shared genome")
        self.assertEqual(len(runtime.core.roles),8)
        self.assertEqual(len(runtime.core.roles[7]),3)
        self.assertEqual(LocalTaskRuntime.restore(runtime.snapshot()).snapshot(),runtime.snapshot())
        ledger=credit.resource_ledger(fixed_messages)
        self.assertEqual(ledger["new_learned_coefficients"],0)
        self.assertEqual(ledger["total_wire_bytes"],16*38)
        report={
          "gate":"NCI-04G6-Y","qualifying_adapter_connected":"PASS",
          "tested_own_local_credit_messages":fixed_messages,
          "damaged_target_labels":0,"new_learned_coefficients":0,
          "baseline_native_snapshot_bytes":len(native_before.encode()),
          **ledger,
          "candidate_prequential_loss":candidate_loss,
          "fully_trained_conventional_prequential_loss":control_loss,
          "candidate_cpu_ns":elapsed_candidate,"control_cpu_ns":elapsed_control,
          "candidate_tracemalloc_peak_bytes":peak,
          "process_peak_rss_native_units":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          "conventional_count_storage_estimate_bytes":baseline.budget(),
          "source_provenance":"UNVERIFIED_LOCAL_SENSOR_INPUT",
          "comparison_classification":"NOT_ADMITTED: caller-supplied own transition is not an independently authenticated native sensor; matched all-in CPU/RSS and local recoverability absent",
          "independent_scientific_first_use":False}
        print("NCI04G6_YGGDRASIL_RESOURCE_COMPARISON="+json.dumps(report,sort_keys=True))
        self.assertIn("UNVERIFIED",report["source_provenance"])
    
    def test_invalid_source_or_nonlocal_credit_is_fail_closed(self):
        runtime=LocalTaskRuntime()
        runtime.lesion([0])
        learner=NativeSurvivorCredit(runtime)
        old=runtime.snapshot()
        with self.assertRaises(ValueError):
            learner.observe_own_transition(0,2,(0,0,1),1,1)
        with self.assertRaises(ValueError):
            learner.observe_own_transition(0,1,(0,1,1),0,1,rate=10)
        self.assertEqual(old,runtime.snapshot())

if __name__=="__main__":
    unittest.main()
