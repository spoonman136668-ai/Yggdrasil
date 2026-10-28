"""Preregistered frozen action-history trace parity experiment.

Public-only legal actions, source-free fixture, exactly pinned original and
one-line-behavior inference-only candidate. Not an autonomous acting result.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import tracemalloc

PIN = {
 "original": "658b855d1b217d20ed9d431fe99b2e866469b7e9",
 "parity": "cd3821f8429ce48580f3132bb2ca0d93e2c94782",
}
STEPS = (0,27,54)
CUES = ("LRV","MRV")
ACTIONS = ("TurnAround","GoForward","Backup")
REWARDS = (-3,0,10)
EPS=1.e-12

def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

def source_sha(root):
    return subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()

def cold_process_restore(blob, root):
    program = ("import sys,hashlib;"
       "from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev as M;"
       "s=sys.stdin.buffer.read(); x=M.restore(s);"
       "assert x.checkpoint()==s;"
       "print(hashlib.sha256(s).hexdigest())")
    env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",PYTHONPATH=str(root))
    proc=subprocess.run([sys.executable,"-B","-c",program],
      input=blob,cwd=root,env=env,stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,check=True,timeout=25)
    assert proc.stdout.decode().strip()==hashlib.sha256(blob).hexdigest()

def prepare_checkpoint(model,cls,root):
    blob=model.checkpoint()
    cold_process_restore(blob,root)
    clone=cls.restore(blob)
    assert clone.checkpoint()==blob
    return blob

def fit_fixture_event(m,i):
    obs=("LRV","MRV","Nothing")[i%3]
    action=ACTIONS[i%3]
    reward=REWARDS[i%3]
    assert m._observation is None and not m.memory.pending
    m.start_observation(obs)
    m.accept_public_transition(action,"Nothing",reward,
                               learning=True,terminal=True)
    assert m.native.core.events==i+1 and m.memory.updates==i+1
    assert m.transitions==i+1

def frozen_history(cls,original_blob,cue,first_action):
    probe=cls.restore(original_blob)
    fixed=probe.model_identities()
    fitted_weight_sha = hashlib.sha256(canonical({
        "genome":probe.native.core.genome,
        "roles":probe.native.core.roles,
        "gates":probe.memory.gates,
        "heads":probe.memory.heads,
        "credit":probe.action_credit,
    })).hexdigest()
    probe.start_frozen_evaluation(fixed["native"],fixed["memory"])
    probe.start_observation(cue)
    probe.accept_public_transition(first_action,"Nothing",0,
                                   learning=False,terminal=False)
    assert probe.model_identities()==fixed, "FROZEN_WT_ID_CHANGED"
    assert probe.memory.pending is False
    assert probe._observation is None
    trace_after_first=list(probe.cell_trace)
    probe.start_observation("Nothing")
    native=probe.native_reward_scores()
    memory=probe.memory.q_values()
    fused=[memory[i]+.15*native[i] for i in range(3)]
    assert probe.model_identities()==fixed
    assert probe._frozen_native==fixed["native"]
    assert probe.memory._frozen_hash==fixed["memory"]
    learned_sha_after=hashlib.sha256(canonical({
        "genome":probe.native.core.genome,
        "roles":probe.native.core.roles,
        "gates":probe.memory.gates,
        "heads":probe.memory.heads,
        "credit":probe.action_credit,
    })).hexdigest()
    assert learned_sha_after==fitted_weight_sha, "FROZEN_FIT_DATA_MUTATED"
    return {
      "cue":cue,"prefix_action":first_action,
      "inference_trace":trace_after_first,
      "native_scores":native,"memory_scores":memory,
      "combined_scores":fused,
      "selected_frozen_action":ACTIONS[max(range(3),key=lambda i:fused[i])],
      "fitted_parameters_sha256":fitted_weight_sha,
      "fitted_parameters_mutated":False,
    }

def diffs(rows, field):
    pairs={}
    for i in range(3):
        for j in range(i+1,3):
            left=rows[i][field]
            right=rows[j][field]
            if field=="selected_frozen_action":
                d=int(left!=right)
            else:
                d=max(abs(x-y) for x,y in zip(left,right))
            pairs[ACTIONS[i]+"__"+ACTIONS[j]]=d
    return pairs

def run_arm(variant,root,path):
    if variant not in PIN or path.exists():
        raise ValueError("ARM_OR_OUTPUT_INVALID")
    if source_sha(root)!=PIN[variant]:
        raise ValueError("EXACT_NATIVE_SOURCE_DRIFT")
    sys.path.insert(0,str(root))
    from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev as M
    from yggdrasil.itd02_native_task_bridge_dev import CELLS
    from yggdrasil.itd02_local_ring_memory_dev import ACTIONS as M_ACTIONS
    if tuple(M_ACTIONS)!=ACTIONS or CELLS!=8:
        raise ValueError("ORIGINAL_PUBLIC_NATIVE_TOPOLOGY_DRIFT")
    t0=time.process_time()
    tracemalloc.start()
    m=M()
    all_snapshots=[]
    trained=0
    for target in STEPS:
        for i in range(trained,target):
            fit_fixture_event(m,i)
        trained=target
        raw=prepare_checkpoint(m,M,root)
        trial={"fit_events":target,"checkpoint_sha256":hashlib.sha256(raw).hexdigest(),
               "checkpoint_bytes":len(raw),"fitted_model_ids":m.model_identities(),
               "by_first_cue":{}}
        for cue in CUES:
            rows=[frozen_history(M,raw,cue,action) for action in ACTIONS]
            trace=diffs(rows,"inference_trace")
            nscore=diffs(rows,"native_scores")
            mscore=diffs(rows,"memory_scores")
            fused=diffs(rows,"combined_scores")
            decision=diffs(rows,"selected_frozen_action")
            trial["by_first_cue"][cue]={
               "history_probes":rows,"trace_action_pair_deltas":trace,
               "native_action_pair_deltas":nscore,
               "memory_action_pair_deltas":mscore,
               "fused_action_pair_deltas":fused,
               "decision_pair_deltas":decision,
               "trace_distinct_pairs":sum(x>EPS for x in trace.values()),
               "native_score_distinct_pairs":sum(x>EPS for x in nscore.values()),
               "fused_score_distinct_pairs":sum(x>EPS for x in fused.values()),
               "selected_action_different_pairs":sum(bool(x) for x in decision.values()),
            }
        assert m.checkpoint()==raw,"ACTUAL_NATIVE_MODEL_CHANGED_BY_PROBES"
        all_snapshots.append(trial)
    assert m.transitions==54 and m.native.core.events==54 and m.memory.updates==54
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    report={
       "schema":"ygg.itd02.frozen-local-action-trace.parity.v1",
       "classification":"SOURCE_FREE_ENGINEERING_TRACE_DIAGNOSTIC__NO_SCIENCE",
       "variant":variant,"source_sha":PIN[variant],
       "training_events":54,"frozen_prefix_probes":len(STEPS)*len(CUES)*len(ACTIONS),
       "public_cues":list(CUES),"prefix_actions":list(ACTIONS),
       "snapshots":all_snapshots,
       "cpu_seconds":time.process_time()-t0,
       "python_peak_bytes":peak,"platform":sys.platform,
       "scientific_first_use":False,"promotion_authorized":False,
       "real_action_performance_claim":False,"consumer_hardware_qualified":False,
    }
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(canonical(report)+b"\n")
    summary={
       "variant":variant,
       "checkpoints":[(v["fit_events"],v["checkpoint_sha256"],v["checkpoint_bytes"])
                      for v in all_snapshots],
       "history_distinctions":[{
          "fitted_events":v["fit_events"],"cue":cue,
          "trace_pairs":v["by_first_cue"][cue]["trace_distinct_pairs"],
          "native_score_pairs":v["by_first_cue"][cue]["native_score_distinct_pairs"],
          "fused_score_pairs":v["by_first_cue"][cue]["fused_score_distinct_pairs"],
          "action_rank_pairs":v["by_first_cue"][cue]["selected_action_different_pairs"],
        }for v in all_snapshots for cue in CUES],
       "cpu_seconds":report["cpu_seconds"],
       "source_free_only":True,
    }
    print("ITD02_FROZEN_ACTION_TRACE_ARM="+json.dumps(summary,sort_keys=True))
    return report

def compare(path, output):
    if output.exists():
        raise ValueError("REFUSE_REPLACE_WITNESS")
    arms={name:json.loads((path/(name+".json")).read_text("utf-8"))
          for name in PIN}
    src=[x["snapshots"] for x in arms.values()]
    assert len(src[0])==len(src[1])==3
    for a,b in zip(*src):
        assert a["fit_events"]==b["fit_events"],"MISMATCHED_TRAINING_EVENTS"
        assert a["checkpoint_sha256"]==b["checkpoint_sha256"], "TRAINING_CHECKPOINTS_CHANGED"
        assert a["fitted_model_ids"]==b["fitted_model_ids"], "TRAINED_MODEL_DISAGREES"
    old=arms["original"];new=arms["parity"]
    old_pairs=sum(v["by_first_cue"][cue]["trace_distinct_pairs"]
                 for v in old["snapshots"] for cue in CUES)
    new_pairs=sum(v["by_first_cue"][cue]["trace_distinct_pairs"]
                 for v in new["snapshots"] for cue in CUES)
    old_score=sum(v["by_first_cue"][cue]["fused_score_distinct_pairs"]
                 for v in old["snapshots"] for cue in CUES)
    new_score=sum(v["by_first_cue"][cue]["fused_score_distinct_pairs"]
                 for v in new["snapshots"] for cue in CUES)
    verdict=("SOURCE_FREE_TRACE_PARITY_PARTIAL_ENGINEERING_SIGNAL__NO_SCIENCE"
            if old_pairs==0 and new_pairs>0 and new_score>old_score
            else "SOURCE_FREE_TRACE_PARITY_UNSUPPORTED__NO_SCIENCE")
    doc={
     "schema":"ygg.itd02.frozen-local-action-trace.comparison.v1",
     "verdict":verdict,
     "trained_checkpoint_sha256_equal":True,
     "original_history_trace_different_action_pairs":old_pairs,
     "parity_history_trace_different_action_pairs":new_pairs,
     "original_fused_score_different_action_pairs":old_score,
     "parity_fused_score_different_action_pairs":new_score,
     "max_action_pair_splits":len(STEPS)*len(CUES)*3,
     "actual_multi_step_learning_success_tested":False,
     "scientific_first_use":False,"promotion_authorized":False,
    }
    output.write_bytes(canonical(doc)+b"\n")
    print("ITD02_FROZEN_ACTION_TRACE_COMPARISON="+json.dumps(doc,sort_keys=True))
    return doc

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--variant",choices=tuple(PIN))
    p.add_argument("--root",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--compare",type=Path)
    a=p.parse_args()
    if a.compare:
        assert a.variant is None and a.root is None
        compare(a.compare,a.output)
    else:
        assert a.variant and a.root
        run_arm(a.variant,a.root.resolve(),a.output)

if __name__=="__main__":
    main()
