"""Preregistered source-free two-step delayed action-consequence ACTING evaluation.

Every reward is issued only for the actor's real chosen second action.
History intervention readouts are separate, frozen diagnostic clones.
No original environment, source-model acceptance, oracle feedback or promotion.
"""
import argparse
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

ACTIONS=("TurnAround","GoForward","Backup")
CUES=(("LRV","MRV"),("docked_LRV","docked_MRV"),("LRV","MRV"))
PHASES=("initial","unfamiliar","reversal")
PERMS=tuple(itertools.permutations(ACTIONS))
FAMILIES=tuple(range(280,286))
SEEDS=(1301,1327)
EPISODES_PER_PHASE=48
ARMS=("original","parity","history_ema","history_count","blind_ema")
PIN={
 "original":"658b855d1b217d20ed9d431fe99b2e866469b7e9",
 "parity":"cd3821f8429ce48580f3132bb2ca0d93e2c94782",
}
assert len(PERMS)==6 and len(ARMS)==5

def canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

def sha(obj):
    return hashlib.sha256(canon(obj)).hexdigest()

def task(family,phase,cue,first):
    assert family in FAMILIES and phase in PHASES
    assert first in ACTIONS and cue in CUES[PHASES.index(phase)]
    cue_ix=CUES[PHASES.index(phase)].index(cue)
    return PERMS[family-280][
        (ACTIONS.index(first)+cue_ix+PHASES.index(phase))%3
    ]

def earned(family,phase,cue,first,second):
    return 10 if second==task(family,phase,cue,first) else -3

def probe_action(episode,step,seed):
    if (episode+1)%7:
        return None
    return ACTIONS[(((episode+1)//7)+seed+step)%3]

def choose_control_second(state,cue,first,arm):
    context=(cue+"|"+first) if arm!="blind_ema" else "Nothing"
    scores=[]
    for a in ACTIONS:
        observed=state["history"].get(context+"|"+a,[])
        if not observed:
            scores.append(0.)
        elif arm=="history_count":
            scores.append(sum(observed)/len(observed))
        else:
            v=observed[0]
            for r in observed[1:]:
                v=.5*v+.5*r
            scores.append(v)
    return ACTIONS[max(range(3),key=lambda i:scores[i])]

def control_first(state,cue,seed):
    n=state["visits"].get(cue,0)
    state["visits"][cue]=n+1
    return ACTIONS[(n+seed)%3]

def restore_native_process(raw,root):
    program=("import sys,hashlib;"
        "from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev as M;"
        "s=sys.stdin.buffer.read(); m=M.restore(s);"
        "assert m.checkpoint()==s;"
        "print(hashlib.sha256(s).hexdigest())")
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",PYTHONPATH=str(root))
    p=subprocess.run((sys.executable,"-B","-c",program),input=raw,
        cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        check=True,timeout=25)
    assert p.stdout.decode().strip()==hashlib.sha256(raw).hexdigest()

def frozen_native(model,cls,phase,family):
    frozen=model.checkpoint()
    ids=model.model_identities()
    score=0
    contexts=[]
    for cue in CUES[PHASES.index(phase)]:
        for first in ACTIONS:
            m=cls.restore(frozen)
            m.start_frozen_evaluation(ids["native"],ids["memory"])
            m.start_observation(cue)
            # Frozen public first action is a DIAGNOSTIC INTERVENTION,
            # not an acting choice and has no model reward/law access.
            m.accept_public_transition(first,"Nothing",0,learning=False,terminal=False)
            m.start_observation("Nothing")
            n=m.native_reward_scores()
            r=m.memory.q_values()
            fused=[r[i]+.15*n[i] for i in range(3)]
            guess=m.choose()
            assert guess==ACTIONS[max(range(3),key=lambda i:fused[i])]
            assert m.model_identities()==ids and model.checkpoint()==frozen
            reward=earned(family,phase,cue,first,guess)
            score+=reward
            contexts.append({"cue":cue,"prior_public_action":first,
                             "second_frozen_choice":guess,"second_scores":fused,
                             "correct_under_private_evaluator":reward==10})
    distinct=0
    changed_choices=0
    for i in (0,3):
        for a in range(3):
            for b in range(a+1,3):
                lhs=contexts[i+a];rhs=contexts[i+b]
                distinct+=int(max(abs(x-y) for x,y in zip(lhs["second_scores"],
                                                           rhs["second_scores"]))>1.e-12)
                changed_choices+=int(lhs["second_frozen_choice"]!=rhs["second_frozen_choice"])
    return {"reward_of_six_frozen_interventions":score,
            "different_history_frozen_score_pairs":distinct,
            "different_history_frozen_choice_pairs":changed_choices,
            "probes":contexts,
            "trained_weights_unchanged":True}

def frozen_control(state,arm,phase,family):
    contexts=[];score=0
    for cue in CUES[PHASES.index(phase)]:
        for first in ACTIONS:
            action=choose_control_second(state,cue,first,arm)
            score+=earned(family,phase,cue,first,action)
            contexts.append({"cue":cue,"prior_public_action":first,
                             "second_frozen_choice":action})
    diff=0
    for i in (0,3):
        for j in range(3):
            for k in range(j+1,3):
                diff+=int(contexts[i+j]["second_frozen_choice"]!=
                          contexts[i+k]["second_frozen_choice"])
    return {"reward_of_six_frozen_interventions":score,
            "different_history_frozen_choice_pairs":diff,
            "probes":contexts,"trained_weights_unchanged":True}

def trial(arm,family,seed,cls=None,root=None):
    native=cls() if cls else None
    state={"visits":{},"history":{},"events":0,"episodes":0} if not cls else None
    fit_baseline=native.model_identities() if cls else None
    phases={}
    decision_history=[]
    all_public_events=0
    for phase_idx,phase in enumerate(PHASES):
        outcomes=[]
        for episode_idx in range(EPISODES_PER_PHASE):
            episode=phase_idx*EPISODES_PER_PHASE+episode_idx
            cue=CUES[phase_idx][(episode_idx+seed)%2]
            exploratory_first=probe_action(episode,0,seed)
            exploratory_second=probe_action(episode,1,seed)
            if cls:
                native.start_observation(cue)
                recommended_first=native.choose()
            else:
                recommended_first=control_first(state,cue,seed)
            first=exploratory_first if exploratory_first is not None else recommended_first
            if cls:
                native.accept_public_transition(first,"Nothing",0,
                                                 learning=True,terminal=False)
                native.start_observation("Nothing")
                recommended_second=native.choose()
            else:
                state["events"]+=1
                recommended_second=choose_control_second(state,cue,first,arm)
            second=exploratory_second if exploratory_second is not None else recommended_second
            reward=earned(family,phase,cue,first,second)
            if cls:
                native.accept_public_transition(second,"Nothing",reward,
                                                 learning=True,terminal=True)
            else:
                key=(cue+"|"+first) if arm!="blind_ema" else "Nothing"
                state["history"].setdefault(key+"|"+second,[]).append(reward)
                state["events"]+=1
                state["episodes"]+=1
            all_public_events+=2
            outcomes.append({"cue":cue,"first":first,"second":second,
                             "first_recommendation":recommended_first,
                             "second_recommendation":recommended_second,
                             "first_exploration":exploratory_first is not None,
                             "second_exploration":exploratory_second is not None,
                             "public_delayed_reward":reward,
                             "second_action_correct":reward==10})
        if cls:
            assert native.transitions==2*EPISODES_PER_PHASE*(phase_idx+1)
            assert native.memory.updates==native.transitions
            assert native.native.core.events==native.transitions
            assert native._observation is None and not native.memory.pending
            raw=native.checkpoint()
            restore_native_process(raw,root)
            checkpoint_bytes=len(raw)
            identities=native.model_identities()
            frozen=frozen_native(native,cls,phase,family)
            native=cls.restore(raw)
            assert native.checkpoint()==raw
        else:
            assert state["events"]==2*EPISODES_PER_PHASE*(phase_idx+1)
            assert state["episodes"]==EPISODES_PER_PHASE*(phase_idx+1)
            raw=canon(state)
            assert canon(json.loads(raw))==raw
            checkpoint_bytes=len(raw)
            identities=None
            frozen=frozen_control(state,arm,phase,family)
            state=json.loads(raw)
        phases[phase]={
            "episode_count":len(outcomes),
            "event_count":len(outcomes)*2,
            "training_delayed_reward":sum(o["public_delayed_reward"] for o in outcomes),
            "training_success_count":sum(o["second_action_correct"] for o in outcomes),
            "first_action_probes":sum(o["first_exploration"] for o in outcomes),
            "second_action_probes":sum(o["second_exploration"] for o in outcomes),
            "second_action_recommendation_differed":
                 sum(o["second"]!=o["second_recommendation"] for o in outcomes),
            "checkpoint_sha256":hashlib.sha256(raw).hexdigest(),
            "checkpoint_bytes":checkpoint_bytes,
            "native_identities":identities,
            "frozen_evaluation":frozen,
            "chosen_event_trace_sha256":sha(outcomes),
            "episodes":outcomes,
        }
        decision_history.extend(outcomes)
    if cls:
        assert native.model_identities()!=fit_baseline,"NATIVE_FAILED_TO_LEARN"
    assert all_public_events==288
    return {"family":family,"seed":seed,"arm":arm,
            "selected_public_feedback_events":all_public_events,
            "two_step_episodes":144,
            "phase_results":phases,
            "total_decision_sha256":sha(decision_history)}

def run_arm(arm,root,output):
    if arm not in ARMS or output.exists():
        raise ValueError("INVALID_ARM_OR_EXISTING_OUTPUT")
    cls=None
    if arm in PIN:
        if root is None or subprocess.check_output(
                ("git","rev-parse","HEAD"),cwd=root,text=True).strip()!=PIN[arm]:
            raise ValueError("SOURCE_PIN_MISMATCH")
        sys.path.insert(0,str(root))
        from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev
        from yggdrasil.itd02_native_task_bridge_dev import RING
        assert RING==tuple(((i-1)%8,(i+1)%8) for i in range(8))
        cls=NativeTaskRingBridgeDev
    cpu=time.process_time();wall=time.perf_counter()
    tracemalloc.start()
    trials=[trial(arm,family,seed,cls,root) for family in FAMILIES for seed in SEEDS]
    used_cpu=time.process_time()-cpu;used_wall=time.perf_counter()-wall
    _cur,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    try:
        import resource
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rss_units="KiB on Linux hosted runner"
    except ImportError:
        rss=None;rss_units="Unavailable on Windows hosted runner"
    earned_means={p:statistics.mean(t["phase_results"][p]["training_delayed_reward"]
                                  for t in trials) for p in PHASES}
    successes={p:statistics.mean(t["phase_results"][p]["training_success_count"]
                                for t in trials) for p in PHASES}
    frozen={p:statistics.mean(
         t["phase_results"][p]["frozen_evaluation"]["reward_of_six_frozen_interventions"]
         for t in trials) for p in PHASES}
    distinct={p:statistics.mean(
         t["phase_results"][p]["frozen_evaluation"]["different_history_frozen_choice_pairs"]
         for t in trials) for p in PHASES}
    summary={
        "schema":"ygg.itd02.delayed-action-two-step.acting-source-free.v1",
        "classification":"SOURCE_FREE_DEV_ONLY__NO_SCIENCE",
        "arm":arm,"source_sha":PIN.get(arm),"families":list(FAMILIES),
        "seeds":list(SEEDS),"episodes_per_phase":EPISODES_PER_PHASE,
        "trials":trials,"actual_delayed_feedback_events":3456,
        "actual_two_step_episodes":1728,"phase_earned_mean":earned_means,
        "phase_success_count_mean":successes,
        "frozen_six_histories_mean":frozen,
        "frozen_choice_history_distinct_mean":distinct,
        "max_checkpoint_bytes":max(t["phase_results"][p]["checkpoint_bytes"]
                                   for t in trials for p in PHASES),
        "cpu_seconds":used_cpu,"wall_seconds":used_wall,
        "peak_python_allocated_bytes":peak,"maxrss":rss,"maxrss_units":rss_units,
        "real_native_recommendations_during_fit":arm in PIN,
        "source_private_hidden_state_in_actor":False,
        "scientific_first_use":False,"original_world_training":False,
        "retail_pc_evidence":False,"promotion_authorized":False,
    }
    assert all(t["selected_public_feedback_events"]==288
               and t["two_step_episodes"]==144 for t in trials)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(canon(summary)+b"\n")
    print("ITD02_TWO_STEP_ACTING_ARM="+json.dumps({
        "arm":arm,"earned":earned_means,"success":successes,
        "frozen":frozen,"different_frozen_choices":distinct,
        "events":summary["actual_delayed_feedback_events"],
        "cpu_seconds":used_cpu,"max_checkpoint_bytes":summary["max_checkpoint_bytes"],
        "classification":summary["classification"]},sort_keys=True))
    return summary

def aggregate(folder,output):
    if output.exists():
        raise ValueError("REFUSE_OVERWRITE_AGGREGATE")
    docs={arm:json.loads((folder/(arm+".json")).read_text("utf-8")) for arm in ARMS}
    assert all(x["actual_delayed_feedback_events"]==3456
       and x["actual_two_step_episodes"]==1728
       and len(x["trials"])==12 for x in docs.values())
    keys=[(t["family"],t["seed"]) for t in docs["original"]["trials"]]
    assert all([(t["family"],t["seed"]) for t in d["trials"]]==keys
               for d in docs.values())
    assert len(set(keys))==12
    # Source implies a stronger strict null: fitting behavior and all fitted
    # checkpoint digests must be equal original versus parity. Divergence is
    # an engineering failure, not evidence of superior causal cognition.
    for first,second in zip(docs["original"]["trials"],docs["parity"]["trials"]):
        assert first["total_decision_sha256"]==second["total_decision_sha256"],"ACTING_SOURCE_PARITY_FAIL"
        for phase in PHASES:
            a=first["phase_results"][phase];b=second["phase_results"][phase]
            assert a["checkpoint_sha256"]==b["checkpoint_sha256"],"FITTED_CHECKPOINT_PARITY_FAIL"
            assert a["native_identities"]==b["native_identities"],"FITTED_WEIGHT_PARITY_FAIL"
            assert a["training_delayed_reward"]==b["training_delayed_reward"]
    stronger={p:max(docs["history_ema"]["phase_earned_mean"][p],
                   docs["history_count"]["phase_earned_mean"][p]) for p in PHASES}
    native=docs["parity"]
    classification=("SOURCE_FREE_ACTING_LEARNING_SIGNAL_ONLY__NO_SCIENCE"
        if (all(native["phase_earned_mean"][p]>stronger[p]
               for p in ("unfamiliar","reversal"))
            and native["max_checkpoint_bytes"]<=1.25*docs["original"]["max_checkpoint_bytes"]
            and native["cpu_seconds"]<=1.25*docs["original"]["cpu_seconds"])
        else "DEVELOPMENT_NEGATIVE_OR_MIXED__SCIENCE_NO_GO")
    comparison={
      "schema":"ygg.itd02.delayed-action-two-step.acting-comparison.v1",
      "classification":classification,
      "acting_source_equivalent":True,
      "fitted_checkpoint_sha_equal":True,
      "source_free_only":True,
      "actual_feedback_events_per_arm":3456,
      "actual_feedback_events_all_arms":17280,
      "two_step_episodes_per_arm":1728,
      "original_vs_parity_delayed_training_reward_delta":
          {p:native["phase_earned_mean"][p]-docs["original"]["phase_earned_mean"][p]
           for p in PHASES},
      "strongest_history_aware_acting_control_by_phase":stronger,
      "phase_earned_mean":{a:x["phase_earned_mean"] for a,x in docs.items()},
      "phase_success_mean":{a:x["phase_success_count_mean"] for a,x in docs.items()},
      "frozen_history_choice_distinct_mean":
           {a:x["frozen_choice_history_distinct_mean"] for a,x in docs.items()},
      "frozen_six_histories_mean":
           {a:x["frozen_six_histories_mean"] for a,x in docs.items()},
      "native_cpu_seconds":{a:docs[a]["cpu_seconds"] for a in PIN},
      "checkpoint_max_bytes":{a:x["max_checkpoint_bytes"] for a,x in docs.items()},
      "first_use":False,"scientific_promotion":False,
      "original_world_tested":False,"retail_pc_validated":False,
    }
    output.write_bytes(canon(comparison)+b"\n")
    print("ITD02_TWO_STEP_ACTING_COMPARISON="+json.dumps(comparison,sort_keys=True))
    return comparison

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--arm",choices=ARMS)
    parser.add_argument("--root",type=Path)
    parser.add_argument("--compare",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.compare:
        assert not args.arm and not args.root
        aggregate(args.compare,args.output)
    else:
        assert args.arm and (args.arm not in PIN or args.root)
        run_arm(args.arm,args.root.resolve() if args.root else None,args.output)

if __name__=="__main__":
    main()
