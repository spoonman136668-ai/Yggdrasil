"""NCI-04G7: independent PROCESS provenance vs independent external sensor.

This focused engineering test preserves no-science-first-use and does not
claim hidden truth, physical cell sensing or recovery of the damaged target.
"""
import json
import pathlib
try:
    import resource
except ImportError:
    resource = None  # POSIX process metering unavailable: measurement test unsupported
import time
import tracemalloc
import unittest
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g7_source_producer import SourceBoundNativeCellSensor
from yggdrasil.nci04g6_native_credit import NativeSurvivorCredit
from yggdrasil.cells import DevelopmentalCells

ROOT=pathlib.Path(__file__).resolve().parents[1]

class ExactLocalCounts:
    def __init__(self):
        self.cells={}
    def observe(self,prior,target):
        item=self.cells.setdefault(tuple(prior),[0,0])
        item[target]+=1
    def predict(self,prior):
        a,b=self.cells.get(tuple(prior),(0,0))
        return (b+1)/(a+b+2)
    def storage_bytes(self):
        return sum(3+16 for _ in self.cells)

def history():
    # Development-only, deterministic native local training stream.
    return [(
        [((n//(1+i%3))+i)%2 for i in range(8)],
        [((n//(1+(i+1)%3))+i+1)%2 for i in range(8)]
    ) for n in range(16)]

class NativeSourceBoundSensor(unittest.TestCase):
    @unittest.skipIf(resource is None, "POSIX resource accounting unavailable: cannot qualify CPU/RSS")
    def test_separate_native_model_output_and_equal_information_controls(self):
        baseline=LocalTaskRuntime()
        experiences=history()
        for bits,outcomes in experiences:
            baseline.observe(bits,outcomes)
        checkpoint=baseline.snapshot()
        baseline.lesion([0])
        runtime_initial=baseline.snapshot()
        sensor=SourceBoundNativeCellSensor(ROOT,baseline)
        credit=NativeSurvivorCredit(baseline)
        learned_before=json.dumps(baseline.core.genome)
        destroyed_before=list(baseline.core.roles[0])
        original_sender=list(baseline.core.roles[7])
        counts=ExactLocalCounts()
        recurrent=DevelopmentalCells()
        for bits,outcomes in experiences:
            recurrent.observe(bits,outcomes)
            prior=(bits[7],bits[6],bits[0])
            counts.observe(prior,outcomes[7])
        bitvector=[1,0,1,0,1,0,1,0]
        prior=(bitvector[7],bitvector[6],bitvector[0])
        pred_candidate=credit.predict_survivor(7,prior)
        pred_counts=counts.predict(prior)
        pred_recurrent=recurrent.predict(bitvector)[7]
        tracemalloc.start()
        t0=time.process_time_ns()
        child_before=resource.getrusage(resource.RUSAGE_CHILDREN)
        message,source=sensor.observe_native_source(0,7,experiences,bitvector,1)
        child_after=resource.getrusage(resource.RUSAGE_CHILDREN)
        parent_cpu=time.process_time_ns()-t0
        heap_current,heap_peak=tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertEqual(len(message),38)
        self.assertEqual(source["producer"]["attestation"],"EXACT_LOCAL_GIT_SOURCE_NOT_EXTERNAL_SENSOR")
        self.assertTrue(source["not_externally_observed"])
        self.assertEqual(source["postlesion_true_target_labels"],0)
        self.assertEqual(len(source["producer"]["git_source_sha256"]),2)
        self.assertEqual(learned_before,json.dumps(baseline.core.genome))
        self.assertEqual(destroyed_before,baseline.core.roles[0])
        self.assertNotEqual(original_sender,baseline.core.roles[7])
        after=baseline.snapshot()
        self.assertEqual(LocalTaskRuntime.restore(after).snapshot(),after)
        own=source["own_model_bit"]
        ledger={
          "gate":"NCI-04G7-Y","source_commit":source["producer"]["commit"],
          "source_provenance":"GIT_PINNED_SEPARATE_NATIVE_PRODUCER",
          "observed_source_type":source["origin"],
          "external_sensor_authentication":"NOT_AVAILABLE",
          "postlesion_target_labels":0,
          "native_steps_from_original_project":16,
          "candidate_prequential_loss":(own-pred_candidate)**2,
          "trained_local_count_loss":(own-pred_counts)**2,
          "fully_trained_native_recurrent_loss":(own-pred_recurrent)**2,
          "candidate_snapshot_bytes_before":len(runtime_initial.encode()),
          "candidate_snapshot_bytes_after":len(after.encode()),
          "baseline_prelesion_snapshot_bytes":len(checkpoint.encode()),
          "conventional_count_storage_bytes":counts.storage_bytes(),
          "source_model_trainable_coefficients":8*7,
          "candidate_new_trainable_coefficients":0,
          "fixed_message_bytes":len(message),
          "source_execution_parent_cpu_ns":parent_cpu,
          "source_execution_child_cpu_us":int((child_after.ru_utime+child_after.ru_stime-child_before.ru_utime-child_before.ru_stime)*1_000_000),
          "source_execution_child_peak_rss_native_units":child_after.ru_maxrss,
          "tracemalloc_peak_bytes":heap_peak,
          "all_in_efficient_transfer":"NOT_QUALIFIED: unpaired snapshots/RSS, source-trained model costs, no unseen native task or true sensor",
          "scientific_first_use":False,
          "classification":"ENGINEERING_SOURCE_PROCESS_PASS / SCIENTIFIC_NO_GO"}
        print("NCI04G7_YGGDRASIL_SOURCE_RESOURCE="+json.dumps(ledger,sort_keys=True))
        self.assertNotEqual(source["origin"],"REAL_WORLD_SENSOR")

    def test_fail_closed_on_unsupported_topology_and_bad_history(self):
        task=LocalTaskRuntime([((i+2)%8,(i+5)%8) for i in range(8)])
        task.lesion([0])
        sensor=SourceBoundNativeCellSensor(ROOT,task)
        before=task.snapshot()
        with self.assertRaises(ValueError):
            sensor.observe_native_source(0,2,history(),[0]*8,1)
        self.assertEqual(before,task.snapshot())
        natural=LocalTaskRuntime()
        natural.lesion([0])
        sensor=SourceBoundNativeCellSensor(ROOT,natural)
        with self.assertRaises(ValueError):
            sensor.observe_native_source(0,7,history(),[0]*7,1)
        with self.assertRaises(ValueError):
            sensor.observe_native_source(0,7,history()*8,[0]*8,1)
        self.assertEqual(natural.core.roles[0],[0.]*3)

if __name__=="__main__": unittest.main()
