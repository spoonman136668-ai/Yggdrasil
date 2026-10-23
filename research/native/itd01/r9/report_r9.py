"""R9 one-shot source-free native action-state experiment and retained negatives."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import tracemalloc

from action_cells import (
    FAMILIES, SEEDS, LocalActionColony, PairwisePerceptron,
    EpisodicActionMemory, CurrentOnlyZero,
    canonical, train_equal_public_interventions, evaluate
)

SCHEMA="itd01.r9.native-action-causal-public-dev.v1"
BUDGETS={
    "FIT_A":256,"FIT_B":256,"FIT_C":128,
    "VALID_A_PRE":96,"VALID_A_POST":96,"VALID_B":96,
    "VALID_C_ZERO":96,"DEV_C_POST":96,"DEV_A_RETAINED":96,
}


def process_peak_rss():
    # No per-model isolated memory claim. Linux ru_maxrss is KiB.
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024), \
               "LINUX_RUSAGE_PROCESS_PEAK_RSS"
    if sys.platform=="win32":
        try:
            import ctypes
            from ctypes import wintypes
            class Counters(ctypes.Structure):
                _fields_=[
                    ("cb",wintypes.DWORD),
                    ("PageFaultCount",wintypes.DWORD),
                    ("PeakWorkingSetSize",ctypes.c_size_t),
                    ("WorkingSetSize",ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage",ctypes.c_size_t),
                    ("QuotaPagedPoolUsage",ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage",ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage",ctypes.c_size_t),
                    ("PagefileUsage",ctypes.c_size_t),
                    ("PeakPagefileUsage",ctypes.c_size_t),
                ]
            psapi=ctypes.WinDLL("psapi")
            kernel=ctypes.WinDLL("kernel32")
            kernel.GetCurrentProcess.restype=wintypes.HANDLE
            process=kernel.GetCurrentProcess()
            c=Counters()
            c.cb=ctypes.sizeof(Counters)
            func=psapi.GetProcessMemoryInfo
            func.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
            func.restype=wintypes.BOOL
            if not func(process,ctypes.byref(c),c.cb):
                raise OSError("GetProcessMemoryInfo returned false")
            return int(c.PeakWorkingSetSize),"WINDOWS_PSAPI_PROCESS_PEAK_WORKING_SET"
        except (OSError,AttributeError,ValueError):
            return None,"PROCESS_PEAK_RSS_UNAVAILABLE_NOT_ZERO"
    return None,"PROCESS_PEAK_RSS_UNAVAILABLE_NOT_ZERO"


def stage(agents,seed,source_role,family,n,models):
    before=[x.feedback_updates for x in agents]
    info=train_equal_public_interventions(agents,seed,source_role,family,n)
    for i,x in enumerate(agents):
        if x.feedback_updates-before[i]!=n:
            raise AssertionError("R9_MODELS_NOT_EQUALLY_INFORMED")
    models.append(info)
    return info


def experiment(seed, smoke=False):
    if seed not in SEEDS and not smoke:
        raise ValueError("R9_UNPREREGISTERED_INIT_SEED")
    if smoke and seed!=3:
        raise ValueError("R9_SMOKE_ONLY_FIXED_SEED_3")
    counts={k:(8 if k.startswith("FIT") else 4) for k in BUDGETS} if smoke \
           else dict(BUDGETS)
    total_start=time.process_time()
    tracemalloc.start()
    native=LocalActionColony()
    standard=PairwisePerceptron()
    memory=EpisodicActionMemory()
    agents=[native,standard,memory]
    baseline=CurrentOnlyZero()
    reported_agents=agents+[baseline]
    source_receipts=[]
    results={}
    stage(agents,seed,"FIT_A","A",counts["FIT_A"],source_receipts)
    results["A_PRE"]=evaluate(reported_agents,seed,"VALID_A_PRE","A",
                              counts["VALID_A_PRE"])
    stage(agents,seed,"FIT_B","B",counts["FIT_B"],source_receipts)
    # Deliberately no inference-time feedback in validation.
    results["A_POST"]=evaluate(reported_agents,seed,"VALID_A_POST","A",
                               counts["VALID_A_POST"])
    results["B_POST"]=evaluate(reported_agents,seed,"VALID_B","B",
                               counts["VALID_B"])
    results["C_ZERO_SHOT"]=evaluate(reported_agents,seed,"VALID_C_ZERO","C",
                                    counts["VALID_C_ZERO"])
    stage(agents,seed,"FIT_C","C",counts["FIT_C"],source_receipts)
    frozen_checkpoints={a.name:hashlib.sha256(a.save()).hexdigest()
                        for a in agents}
    checkpoint_bytes={a.name:len(a.save()) for a in agents}
    # Parameter-only source state excludes inference measurement counters.
    def learned_bytes(a):
        if isinstance(a,LocalActionColony):
            return json.dumps({"cells":{
                f:[(c.fast,c.slow,c.public_updates) for c in a.cells[f]]
                for f in FAMILIES},
                "bias":a.bias,
                "feedback_updates":a.feedback_updates,
                "weight_changes":a.weight_changes}, sort_keys=True,
                separators=(",",":")).encode()
        if isinstance(a,PairwisePerceptron):
            return json.dumps({"weights":a.weights,"bias":a.bias,
                "feedback_updates":a.feedback_updates,
                "weight_changes":a.weight_changes},sort_keys=True,
                separators=(",",":")).encode()
        return json.dumps({"memory":a.memory,
            "feedback_updates":a.feedback_updates,
            "weight_changes":a.weight_changes},sort_keys=True,
            separators=(",",":")).encode()
    frozen_learned={a.name:hashlib.sha256(learned_bytes(a)).hexdigest()
                    for a in agents}
    restored=LocalActionColony.restore(native.save())
    if restored.save()!=native.save():
        raise AssertionError("R9_NATIVE_SAVE_COLD_RESTORE_FAILED")
    results["C_POST"]=evaluate(reported_agents,seed,"DEV_C_POST","C",
                               counts["DEV_C_POST"])
    results["A_RETAINED"]=evaluate(reported_agents,seed,"DEV_A_RETAINED","A",
                                   counts["DEV_A_RETAINED"])
    # Evaluating DEV never updates the trained state. If it does, fail closed.
    observed_learned={a.name:hashlib.sha256(learned_bytes(a)).hexdigest()
                      for a in agents}
    if observed_learned!=frozen_learned:
        raise AssertionError("R9_DEV_OR_VALID_UPDATED_FITTED_PARAMETERS")
    fitted_sizes=checkpoint_bytes
    cpu=time.process_time()-total_start
    py_heap=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    rss,rss_source=process_peak_rss()
    if cpu<=0 or cpu>5400 or any(n>32768 for n in fitted_sizes.values()):
        raise ValueError("R9_PROCESS_CPU_OR_MODEL_SIZE_LIMIT")
    if rss is not None and rss>2*1024**3:
        raise ValueError("R9_PROCESS_RSS_LIMIT")
    def success(role,model,family):
        return results[role]["success"][model]
    learned=native.name
    direct=(
        all(success(role,learned,family)>=.75 for role,family in (
            ("A_POST","A"),("B_POST","B"),("C_POST","C"))) and
        native.feedback_updates==sum(counts[k] for k in (
            "FIT_A","FIT_B","FIT_C")) and
        native.weight_changes>0 and
        all(results[k]["all_actions_legal"] for k in results)
    )
    native_zero=success("C_ZERO_SHOT",learned,"C")
    transfer=(
        native_zero>=.70 and all(
            native_zero-success("C_ZERO_SHOT",a.name,"C")>=.05
            for a in (standard,memory))
    )
    communication_benefit=any(
        results[r]["native_neighbor_action_disagreement"]>0 and
        success(r,learned,results[r]["family"])>
        results[r]["native_no_neighbor_success"]
        for r in ("A_POST","B_POST","C_ZERO_SHOT","C_POST","A_RETAINED")
    )
    report={
        "schema":SCHEMA, "frozen_seed":seed,
        "role_counts_per_family":counts,
        "source_roles_not_original_held":True,
        "public_action_and_delayed_success_equal_for_all_fitted_models":True,
        "training_action_intervention_policy":
            "PARITY_OF_SENSOR_POPCOUNT_PLUS_PUBLIC_INDEX",
        "train_public_trace_receipts":source_receipts,
        "native_delayed_public_feedback_updates":native.feedback_updates,
        "native_actual_weight_changes":native.weight_changes,
        "native_evaluated_neighbor_terms":native.message_evaluations,
        "native_nonzero_neighbor_terms":native.neighbor_contributions,
        "conventional_delayed_public_updates":{
            a.name:a.feedback_updates for a in (standard,memory)
        },
        "fitted_source_checkpoint_sha256":frozen_checkpoints,
        "fitted_parameter_only_sha256":frozen_learned,
        "fitted_parameter_unchanged_through_dev":True,
        "fitted_source_checkpoint_bytes":fitted_sizes,
        "native_cold_restore_exact":True,
        "family_evidence":results,
        "whole_process_cpu_seconds":round(cpu,6),
        "whole_process_peak_rss_bytes":rss,
        "whole_process_rss_measurement_source":rss_source,
        "tracemalloc_python_peak_bytes_not_whole_process_rss":py_heap,
        "isolated_per_model_cpu_rss_parity":False,
        "native_source_state_retention_dev_pass":direct,
        "native_c_zero_shot_transfer_provisionally_pass":transfer,
        "native_neighbor_causal_benefit_provisionally_pass":communication_benefit,
        "original_Ygg_R7_disposition":"NO_GO_UNCHANGED",
        "r8_observational_nonidentifiability_result":"PRESERVED",
        "original_H1_H2_source_first_use":False,
        "native_Wingless_executed":False,
        "scientific_admission":"NOT_GRANTED_BY_SOURCE_FREE_DEV",
        "full_itd01_novel_source_transfer":"NOT_TESTED",
        "disposition":(
            "SOURCE_FREE_NATIVE_ACTION_LEARNING_ALL_PROVISIONAL_GATES_PASS"
            if direct and transfer and communication_benefit and not smoke else
            "SOURCE_FREE_NATIVE_R9_PARTIAL_OR_NEGATIVE_RETAIN_ALL_EVIDENCE"
        ),
        "development_smoke_only":smoke,
    }
    return report


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--seed",type=int,default=101)
    cli.add_argument("--smoke",action="store_true")
    arg=cli.parse_args()
    result=experiment(3,True) if arg.smoke else experiment(arg.seed)
    print(json.dumps(result,sort_keys=True,separators=(",",":"),
                     allow_nan=False))


if __name__=="__main__":
    main()
