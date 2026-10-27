"""Read-only observational decomposition of original native public learning.

Fixed protocol: research/itd02_v8_credit_path_preregister_20261027.md
This evaluator owns toy-law knowledge but cannot provide unchosen feedback,
source-private state, learned weights, or model choices to the native learner.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import tracemalloc

FAMILIES = tuple(range(210,216))
SEEDS = (1013,1031)
STEPS = 48
PHASES = ("initial","unfamiliar","reversal")
PIN = {
  "v7": "3a32bd54f270058462d662302eb5732878d2edee",
  "v8": "658b855d1b217d20ed9d431fe99b2e866469b7e9",
}

def canonical(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def argmax(a, labels):
    return labels[max(range(len(a)), key=lambda i:a[i])]

def exact_cold_restore(snapshot, root):
    program = (
      "import sys,hashlib;"
      "from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev as B;"
      "x=sys.stdin.buffer.read(); m=B.restore(x);"
      "assert m.checkpoint()==x;"
      "print(hashlib.sha256(x).hexdigest())"
    )
    env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(root))
    p=subprocess.run((sys.executable,"-B","-c",program), input=snapshot,
      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
      timeout=25, cwd=root, env=env)
    assert p.stdout.decode().strip() == hashlib.sha256(snapshot).hexdigest(), "COLD_CHECKPOINT_FAILED"

def credit_from_native(m, obs, actions, reward_sites, public_rewards, word_fn):
    credits=[]
    for a_i,action in enumerate(actions):
        if word_fn is not None:
            credits.append(.15 * sum(
              float(value)*m.action_credit[i][word_fn(obs,action,site)]
              for i,(site,value) in enumerate(zip(reward_sites,public_rewards))
            ))
        else:
            from yggdrasil.itd02_local_ring_memory_dev import OBSERVATIONS
            credits.append(.15*m.action_credit[OBSERVATIONS.index(obs)][a_i])
    return credits

def sample(m,obs,cls,actions,reward_sites,public_rewards,word_fn):
    before=m.checkpoint()
    p=cls.restore(before)
    p.start_observation(obs)
    native=p.native_reward_scores()
    mem=p.memory.q_values()
    credit=credit_from_native(p,obs,actions,reward_sites,public_rewards,word_fn)
    assert len(native)==len(mem)==len(credit)==3
    fused=[mem[i]+.15*native[i] for i in range(3)]
    minus_credit=[fused[i]-.15*credit[i] for i in range(3)]
    # Probe has no real source/feedback access and cannot affect m.
    assert m.checkpoint()==before, "REAL_MODEL_CHANGED_BY_PROBE"
    return {
      "fused":argmax(fused,actions), "native":argmax(native,actions),
      "memory":argmax(mem,actions), "without_credit":argmax(minus_credit,actions),
      "max_absolute_credit_fused":max(abs(.15*x) for x in credit),
      "fused_margin":sorted(fused)[-1]-sorted(fused)[-2],
      "native_margin":sorted(native)[-1]-sorted(native)[-2],
      "memory_margin":sorted(mem)[-1]-sorted(mem)[-2],
    }

def run_trial(family,seed,cls,actions,reward_sites,public_rewards,word_fn,root):
    permutation=tuple(itertools.permutations(actions))[family-210]
    a,b,c=permutation
    laws={
      "initial":{"LRV":a,"MRV":b},
      "unfamiliar":{"docked_LRV":b,"docked_MRV":c},
      "reversal":{"LRV":c,"MRV":a}
    }
    labels={
      "initial":("LRV","MRV"),
      "unfamiliar":("docked_LRV","docked_MRV"),
      "reversal":("LRV","MRV")
    }
    m=cls()
    initial_sha=m.model_identities()
    result={"family":family,"seed":seed,"phases":{}}
    assert set(PHASES)==set(laws)
    for n,phase in enumerate(PHASES,1):
        counters=Counter()
        phase_rewards=0
        sums=Counter()
        for t in range(STEPS):
            obs=labels[phase][(t+seed)%2]
            diagnostic=sample(m,obs,cls,actions,reward_sites,public_rewards,word_fn)
            m.start_observation(obs)
            selected=m.choose()
            if selected != diagnostic["fused"]:
                raise AssertionError("SELECTED_ACTION_NOT_FUSED_ORIGINAL_NATIVE")
            correct=laws[phase][obs]
            actual=10 if selected==correct else -3
            phase_rewards += actual
            counters["decisions"]+=1
            counters["selected_optimal"] += int(selected==correct)
            counters["selected_regret"] += 10-actual
            counters["credit_changes_selection"] += int(selected!=diagnostic["without_credit"])
            counters["credit_flip_beneficial"] += int(selected==correct and diagnostic["without_credit"]!=correct)
            counters["credit_flip_harmful"] += int(selected!=correct and diagnostic["without_credit"]==correct)
            counters["native_argmax_optimal_offline"] += int(diagnostic["native"]==correct)
            counters["memory_argmax_optimal_offline"] += int(diagnostic["memory"]==correct)
            counters["no_credit_argmax_optimal_offline"] += int(diagnostic["without_credit"]==correct)
            counters["native_agrees_selected"] += int(diagnostic["native"]==selected)
            counters["memory_agrees_selected"] += int(diagnostic["memory"]==selected)
            sums.update({name:round(diagnostic[name],12) for name in
                ("max_absolute_credit_fused","fused_margin","native_margin","memory_margin")})
            m.accept_public_transition(selected,"Nothing",actual,learning=True,terminal=True)
        assert m.transitions==STEPS*n and m.memory.updates==STEPS*n
        assert m._observation is None and not m.memory.pending
        checkpoint=m.checkpoint()
        exact_cold_restore(checkpoint,root)
        restored=cls.restore(checkpoint)
        assert restored.checkpoint()==checkpoint and restored.model_identities()==m.model_identities()
        m=restored
        result["phases"][phase]={
          "public_selected_reward":phase_rewards,
          "counts":dict(counters),
          "score_magnitudes":{name:sums[name]/STEPS for name in
               ("max_absolute_credit_fused","fused_margin","native_margin","memory_margin")},
          "checkpoint_bytes":len(checkpoint),
          "checkpoint_sha256":hashlib.sha256(checkpoint).hexdigest(),
          "native_identity":m.model_identities(),
          "cold_process_restored":True,
        }
    assert result["phases"]["reversal"]["native_identity"] != initial_sha, "NATIVE_UNCHANGED_AFTER_FIT"
    return result

def evaluate(variant,root,output):
    assert variant in PIN
    assert not output.exists(),"NO_OVERWRITE"
    actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
    assert actual == PIN[variant],"SOURCE_SHA_DRIFT"
    sys.path.insert(0,str(root))
    from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev, ACTIONS, ACTION_SITES, REWARDS, RING
    import yggdrasil.itd02_native_task_bridge_dev as bridge
    assert len(ACTIONS)==3 and len(ACTION_SITES)==3 and REWARDS==(-3,0,10)
    assert RING==tuple(((i-1)%8,(i+1)%8) for i in range(8))
    word_fn=getattr(bridge,"_local_ordered_word",None)
    assert (word_fn is not None)==(variant=="v8"),"NATIVE_CREDIT_SCOPE_DRIFT"
    word_uniqueness={}
    if word_fn is not None:
        from yggdrasil.itd02_local_ring_memory_dev import OBSERVATIONS
        for site in ACTION_SITES:
            words={word_fn(o,a,site) for o in OBSERVATIONS for a in ACTIONS}
            assert len(words)==15 and all(0<=w<16 for w in words), "LOCAL_WORD_IDENTITY_DRIFT"
            word_uniqueness[str(site)]={"distinct":len(words),"capacity":16}
    tracemalloc.start()
    cpu=time.process_time()
    wall=time.perf_counter()
    trials=[run_trial(family,seed,NativeTaskRingBridgeDev,ACTIONS,
                 ACTION_SITES,REWARDS,word_fn,root)
            for family in FAMILIES for seed in SEEDS]
    cpu_elapsed=time.process_time()-cpu
    wall_elapsed=time.perf_counter()-wall
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    try:
        import resource
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        unit="KiB on Unix hosted runner"
    except ImportError:
        rss=None
        unit="unavailable on Windows"
    summary={}
    for phase in PHASES:
        rows=[t["phases"][phase] for t in trials]
        summary[phase]={
          "mean_reward":statistics.mean(x["public_selected_reward"] for x in rows),
          "total_decisions":sum(x["counts"]["decisions"] for x in rows),
          "mean_selected_optimal":statistics.mean(x["counts"]["selected_optimal"] for x in rows),
          "credit_selection_flips":sum(x["counts"]["credit_changes_selection"] for x in rows),
          "beneficial_credit_flips":sum(x["counts"]["credit_flip_beneficial"] for x in rows),
          "harmful_credit_flips":sum(x["counts"]["credit_flip_harmful"] for x in rows),
          "native_only_optimal_offline":sum(x["counts"]["native_argmax_optimal_offline"] for x in rows),
          "memory_only_optimal_offline":sum(x["counts"]["memory_argmax_optimal_offline"] for x in rows),
          "mean_credit_effect_size":statistics.mean(x["score_magnitudes"]["max_absolute_credit_fused"] for x in rows),
          "max_checkpoint_bytes":max(x["checkpoint_bytes"] for x in rows),
        }
    report={
      "schema":"ygg.itd02.v8.credit_path_diagnostic.v1",
      "classification":"CREDIT_PATH_DIAGNOSTIC_ONLY__NO_SCIENCE",
      "source_sha":actual, "variant":variant, "host_os":sys.platform,
      "families":list(FAMILIES), "seeds":list(SEEDS), "phase_steps":STEPS,
      "native_acted_selected_public_events":len(trials)*STEPS*len(PHASES),
      "local_word_coverage":word_uniqueness,
      "summary":summary,"trials":trials,
      "cpu_seconds":cpu_elapsed,"wall_seconds":wall_elapsed,
      "peak_python_traced_bytes":peak,"process_highwater":rss,
      "process_highwater_units":unit,
      "independent_scientific_first_use":False,
      "resource_retail_device":False,
      "source_free":True,"accepted_model_updated":False,
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(canonical(report)+b"\n")
    print("ITD02_NATIVE_CREDIT_PATH="+json.dumps({
      "variant":variant,"source_sha":actual,"summary":summary,
      "local_words":word_uniqueness,"events":report["native_acted_selected_public_events"],
      "cpu_seconds":cpu_elapsed,"checkpoint_max":max(p["max_checkpoint_bytes"] for p in summary.values()),
      "class":report["classification"],
    },sort_keys=True))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--variant",choices=PIN,required=True)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    evaluate(a.variant,a.root.resolve(),a.output)

if __name__=="__main__":
    main()
