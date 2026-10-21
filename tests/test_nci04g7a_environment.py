"""NCI-04G7A local native simulation effect and equal-stream controls.

The executable world is independent of all trained models but is authored
inside this repository. These checks never claim a physical sensor, unseen
family, recovered target, or independently accepted scientific evaluation.
"""
import json
import math
import pathlib
import resource
import time
import tracemalloc
import unittest
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g7a_environment_adapter import BoundedLocalEnvironment
from yggdrasil.developmental import sig

ROOT=pathlib.Path(__file__).resolve().parents[1]

class ConditionalCount:
    def __init__(self):self.table={}
    def predict(self,key):
        neg,pos=self.table.get(tuple(key),(0,0))
        return (pos+1)/(neg+pos+2)
    def observe(self,key,bit):
        slot=self.table.setdefault(tuple(key),[0,0]);slot[bit]+=1
    def byte_estimate(self):return len(self.table)*18

class EqualStreamRecurrent:
    """Conventional, trainable four-parameter logistic recurrent model.

    It sees only the permitted three local input bits and its own past
    state, along with the same model-independent observed consequence.
    """
    def __init__(self):self.weights=[0.0]*4;self.state=0.0
    def predict(self,prior):
        x=[1.0,float(2*prior[0]-1),float(2*prior[1]-1),self.state]
        return sig(sum(a*b for a,b in zip(self.weights,x)))
    def observe(self,prior,bit):
        x=[1.0,float(2*prior[0]-1),float(2*prior[1]-1),self.state]
        p=sig(sum(a*b for a,b in zip(self.weights,x)))
        self.weights=[w+.035*(bit-p)*v for w,v in zip(self.weights,x)]
        self.state=.5*self.state+.5*(2*bit-1)
    def bytes(self):return 8*5

class GenuineSourceFreeLocalWorld(unittest.TestCase):
    def test_executed_transition_causes_source_bound_local_difference(self):
        native=LocalTaskRuntime()
        native.lesion([0])
        world=BoundedLocalEnvironment(ROOT,native)
        count=ConditionalCount()
        recurrent=EqualStreamRecurrent()
        pre=native.snapshot()
        baseline_native_params=(len(native.core.genome)*len(native.core.genome[0])
            +sum(len(x) for x in native.core.roles))
        loss_native=loss_count=loss_recurrent=0.
        parent_candidate_cpu=parent_count_cpu=parent_recurrent_cpu=0
        total_wire=0
        seen=[]
        tracemalloc.start()
        child_before=resource.getrusage(resource.RUSAGE_CHILDREN)
        for seq in range(1,17):
            bits=[(seq//(1+i%3)+i)%2 for i in range(8)]
            action=(seq//3)%2
            prior=(bits[7],bits[6],bits[0])
            start=time.process_time_ns()
            p_native=world.credit.predict_survivor(7,prior)
            wire,proof=world.observe(bits,action,0,7,seq)
            parent_candidate_cpu+=time.process_time_ns()-start
            outcome=proof["measured_sender_next_bit"]
            start=time.process_time_ns()
            p_count=count.predict(prior);count.observe(prior,outcome)
            parent_count_cpu+=time.process_time_ns()-start
            start=time.process_time_ns()
            p_recur=recurrent.predict(prior);recurrent.observe(prior,outcome)
            parent_recurrent_cpu+=time.process_time_ns()-start
            loss_native+=(p_native-outcome)**2
            loss_count+=(p_count-outcome)**2
            loss_recurrent+=(p_recur-outcome)**2
            total_wire+=len(wire)
            self.assertEqual(proof["observed_world"],"DETERMINISTIC_SIMULATED_CAUSAL_TRANSITION")
            self.assertEqual(proof["producer"]["external_sensor_attestation"],False)
            self.assertEqual(proof["postlesion_damaged_target_labels"],0)
            seen.append((bits,action,outcome))
        child_after=resource.getrusage(resource.RUSAGE_CHILDREN)
        current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        # Distinguishing intervention at same prior bits, independent of
        # model history. Each world step remains a source-bound subprocess.
        probe_bits=[1,0,1,0,1,0,1,0]
        wire0,contrast0=world.observe(probe_bits,0,0,7,17)
        wire1,contrast1=world.observe(probe_bits,1,0,7,18)
        self.assertNotEqual(contrast0["measured_sender_next_bit"],contrast1["measured_sender_next_bit"])
        self.assertEqual(total_wire,16*38)
        self.assertEqual(baseline_native_params,45)
        self.assertEqual(len(native.core.genome)*len(native.core.genome[0])
            +sum(len(x) for x in native.core.roles),baseline_native_params)
        self.assertEqual(native.core.roles[0],[0.0]*3,"damaged target was taught forbidden labels")
        self.assertEqual(LocalTaskRuntime.restore(native.snapshot()).snapshot(),native.snapshot())
        report={
          "gate":"NCI-04G7A-Y","native_world_measurement":"PASS_SOURCE_PINNED_SIMULATED_TRANSITION",
          "independence":"environment process has no candidate/control weights",
          "external_world_sensor_attested":False,
          "same_prior_different_action_distinguishable":True,
          "postlesion_target_labels":0,"native_role_and_genome_coefficients":baseline_native_params,
          "new_candidate_learned_coefficients":0,
          "candidate_initial_snapshot_bytes":len(pre.encode()),
          "candidate_final_snapshot_bytes":len(native.snapshot().encode()),
          "local_messages_bytes":total_wire+len(wire0)+len(wire1),
          "all_in_candidate_parent_cpu_ns":parent_candidate_cpu,
          "child_cpu_us":int((child_after.ru_utime+child_after.ru_stime-child_before.ru_utime-child_before.ru_stime)*1_000_000),
          "child_peak_rss_native_units":child_after.ru_maxrss,
          "conditional_count_parent_cpu_ns":parent_count_cpu,
          "trainable_recurrent_parent_cpu_ns":parent_recurrent_cpu,
          "candidate_prequential_loss":loss_native,
          "count_prequential_loss":loss_count,
          "recurrent_prequential_loss":loss_recurrent,
          "candidate_python_tracemalloc_peak_bytes":peak,
          "count_model_bytes_estimate":count.byte_estimate(),
          "recurrent_model_bytes_estimate":recurrent.bytes(),
          "matched_all_in_cpu_memory":"NOT_QUALIFIED: subprocess and object lifetime allocation not comparable to in-process control; no true full-RSS paired budget",
          "unseen_task_transfer":"NOT_TESTED",
          "no_external_physical_sensor":"BLOCKED",
          "scientific_first_use":False,
          "disposition":"SOURCE_FREE_SIMULATED_CAUSAL_OBSERVATION_PASS / SCIENTIFIC_NO_GO"}
        print("NCI04G7A_Y_LOCAL_CONTRAST="+json.dumps(report,sort_keys=True))
        self.assertGreater(parent_candidate_cpu,parent_count_cpu)

    def test_invalid_source_mutation_and_nonlocal_source_fail_closed(self):
        rt=LocalTaskRuntime()
        rt.lesion([0])
        observer=BoundedLocalEnvironment(ROOT,rt)
        old=rt.snapshot()
        for call in [
            lambda:observer.observe([0]*7,0,0,7,1),
            lambda:observer.observe([0]*8,2,0,7,1),
            lambda:observer.observe([0]*8,0,0,2,1),
            lambda:observer.observe([0]*8,0,0,7,-1)]:
            with self.assertRaises(ValueError):call()
        self.assertEqual(old,rt.snapshot())
        self.assertFalse(observer.source_receipt()["external_sensor_attestation"])
if __name__=="__main__":unittest.main()
