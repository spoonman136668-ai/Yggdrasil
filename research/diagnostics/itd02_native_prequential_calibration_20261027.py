"""Prequential source-only diagnosis of the original Yggdrasil predictive-action readout.

Frozen original source, no first use, no interventions/privileged oracle in learner.
An independent evaluator calculates outcome and optimal action *after* the
learner chooses, and records whether the predicted action ranking was helpful.
Replay EMA sees only the same chosen-action public events as the native learner.
"""
import collections
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS

TRAIN=("LRV","MRV","Nothing")
UNSEEN=("docked_LRV","docked_MRV")
OBS=TRAIN+UNSEEN
FAMILIES=range(38,46)
SEEDS=range(36,44)
PHASES=(("initial",90,TRAIN),("unfamiliar",90,OBS))
FIELDS=("phase","observation","action","reward","native_selected","native_best",
        "memory_selected","memory_best","combined_selected","combined_best",
        "replay_ema_pred","replay_window_pred","native_correct","memory_correct",
        "combined_correct","native_greedy_was_selected","native_scores",
        "memory_scores")

def target(label,family,seed,observation,salt=0):
    source=("%s:%d:%d:%s:%d"%(label,family,seed,observation,salt)).encode("ascii")
    return ACTIONS[hashlib.sha256(source).digest()[0]%len(ACTIONS)]

def hidden_evaluator_laws(family,seed):
    initial={obs:target("initial",family,seed,obs) for obs in OBS}
    for salt in range(100):
        changed={obs:target("unfamiliar",family,seed,obs,salt) for obs in OBS}
        if sum(initial[o]!=changed[o] for o in TRAIN)>=2:
            return initial,changed
    raise AssertionError("EVALUATOR_CANNOT_GENERATE_ALTERNATE_LAW")

def cold_process_restore(checkpoint,identities,transitions):
    program=(
      "import sys,json,hashlib;"
      "from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev;"
      "raw=sys.stdin.buffer.read();m=NativeTaskRingBridgeDev.restore(raw);"
      "print(json.dumps({'identities':m.model_identities(),"
      "'transitions':m.transitions,"
      "'sha':hashlib.sha256(m.checkpoint()).hexdigest()}))"
    )
    result=subprocess.run([sys.executable,"-B","-c",program],
                          input=checkpoint,capture_output=True,
                          check=True,timeout=20)
    parsed=json.loads(result.stdout)
    expected={"identities":identities,"transitions":transitions,
              "sha":hashlib.sha256(checkpoint).hexdigest()}
    if parsed!=expected:
        raise AssertionError("COLD_PROCESS_DID_NOT_RETAIN_STATE")
    return NativeTaskRingBridgeDev.restore(checkpoint)

def estimate(table,mode,obs,action):
    records=table.get((obs,action),[])
    if not records:
        return 0.
    if mode=="window":
        return statistics.mean(records[-6:])
    if mode=="ema":
        value=float(records[0])
        for reward in records[1:]:
            value=0.5*reward+0.5*value
        return value
    raise AssertionError("BAD_REPLAY_CONTROL")

def score_max(values):
    return ACTIONS[max(range(len(ACTIONS)),key=lambda k:values[k])]

def aggregate(records):
    n=len(records)
    if n==0:
        raise AssertionError("NO_CALIBRATION_EVENTS")
    means={}
    for key in ("native_selected","memory_selected","combined_selected",
                "replay_ema_pred","replay_window_pred"):
        error=[abs(event[key]-event["reward"]) for event in records]
        sq=[(event[key]-event["reward"])**2 for event in records]
        means[key+"_mae"]=statistics.mean(error)
        means[key+"_rmse"]=(statistics.mean(sq))**0.5
        means[key+"_bias"]=statistics.mean(event[key]-event["reward"] for event in records)
    for key in ("native_correct","memory_correct","combined_correct",
                "native_greedy_was_selected"):
        means[key+"_rate"]=sum(event[key] for event in records)/n
    means["actual_mean_reward"]=statistics.mean(event["reward"] for event in records)
    means["positive_outcome_rate"]=sum(event["reward"]==10 for event in records)/n
    means["chosen_action_counts"]=dict(collections.Counter(e["action"] for e in records))
    means["events"]=n
    return means

def trial(family,seed):
    initial,changed=hidden_evaluator_laws(family,seed)
    model=NativeTaskRingBridgeDev()
    replay={}
    output={"family":family,"seed":seed,"phases":{}}
    native_before=model.model_identities()
    for phase,steps,observations in PHASES:
        law=initial if phase=="initial" else changed
        phase_events=[]
        for episode in range(steps):
            obs=observations[(episode+seed)%len(observations)]
            model.start_observation(obs)
            native_values=model.native_reward_scores()
            memory_values=model.memory.q_values()
            combined=[memory_values[i]+0.15*native_values[i] for i in range(len(ACTIONS))]
            n_top=score_max(native_values)
            m_top=score_max(memory_values)
            c_top=score_max(combined)
            chosen=model.choose()
            if chosen!=c_top:
                raise AssertionError("ORIGINAL_CHOOSE_PARITY_FAILED")
            index=ACTIONS.index(chosen)
            # All three estimates are pre-outcome values; the source-owning
            # evaluator has not yet provided its action consequence.
            native_value=float(native_values[index])
            memory_value=float(memory_values[index])
            combined_value=float(combined[index])
            ema_value=estimate(replay,"ema",obs,chosen)
            window_value=estimate(replay,"window",obs,chosen)
            # EVALUATOR-ONLY: this choice targets the reward rule;
            # hidden_evaluator_laws and the optimal action NEVER enter a
            # candidate action score or any model training call.
            optimal=law[obs]
            reward=10 if chosen==optimal else -3
            phase_events.append(dict(zip(FIELDS,(
                phase,obs,chosen,reward,native_value,n_top,
                memory_value,m_top,combined_value,c_top,
                ema_value,window_value,int(n_top==optimal),
                int(m_top==optimal),int(c_top==optimal),int(n_top==chosen),
                [round(v,9) for v in native_values],
                [round(v,9) for v in memory_values]
            ))))
            model.accept_public_transition(chosen,"Nothing",reward,
                                           learning=True,terminal=True)
            replay.setdefault((obs,chosen),[]).append(reward)
        output["phases"][phase]={
            "metrics":aggregate(phase_events),
            "by_action":{action:aggregate([e for e in phase_events if e["action"]==action])
                         for action in ACTIONS if any(e["action"]==action for e in phase_events)},
            "by_observation":{
                obs:aggregate([e for e in phase_events if e["observation"]==obs])
                for obs in observations
            },
            "last30_metrics":aggregate(phase_events[-30:]),
            "events":phase_events
        }
        if phase=="initial":
            checkpoint=model.checkpoint()
            identities=model.model_identities()
            model=cold_process_restore(checkpoint,identities,steps)
            output["cold_restart"]={
                "verified_new_interpreter":True,
                "checkpoint_bytes":len(checkpoint),
                "parameter_identities_retained":identities==model.model_identities(),
                "checkpoint_sha256":hashlib.sha256(checkpoint).hexdigest()
            }
    if model.transitions!=180:
        raise AssertionError("NATIVE_EXPERIENCE_ACCOUNTING_DRIFT")
    output["real_native_weights_changed"]=model.model_identities()!=native_before
    output["final_checkpoint_bytes"]=len(model.checkpoint())
    output["law_fingerprints"]={
        "initial":hashlib.sha256(json.dumps(initial,sort_keys=True).encode()).hexdigest(),
        "unfamiliar":hashlib.sha256(json.dumps(changed,sort_keys=True).encode()).hexdigest(),
    }
    return output

start=time.perf_counter()
trials=[trial(f,s) for f in FAMILIES for s in SEEDS]
metrics={}
for phase,_,_ in PHASES:
    events=[event for item in trials for event in item["phases"][phase]["events"]]
    metrics[phase]={
        "all":aggregate(events),
        "last30_per_trial":aggregate([event for t in trials
                                    for event in t["phases"][phase]["events"][-30:]]),
        "by_action":{
            action:aggregate([e for e in events if e["action"]==action])
            for action in ACTIONS if any(e["action"]==action for e in events)
        },
        "by_observation":{
            obs:aggregate([e for e in events if e["observation"]==obs])
            for obs in OBS if any(e["observation"]==obs for e in events)
        },
        "family_means":{
            str(f):{
              "native_selected_mae":statistics.mean(
                 t["phases"][phase]["metrics"]["native_selected_mae"]
                 for t in trials if t["family"]==f),
              "ema_selected_mae":statistics.mean(
                 t["phases"][phase]["metrics"]["replay_ema_pred_mae"]
                 for t in trials if t["family"]==f),
              "native_rank_accuracy":statistics.mean(
                 t["phases"][phase]["metrics"]["native_correct_rate"]
                 for t in trials if t["family"]==f)
            } for f in FAMILIES
        }
    }

receipt={
  "schema":"itd02.native-prequential-calibration.source-frozen.v1",
  "authority":"source-free-engineering-diagnostic-only-NO-FSA",
  "scientific_first_use":False,
  "original_native_source_sha":os.environ["SOURCE_SHA"],
  "platform":platform.platform(),
  "python_version":platform.python_version(),
  "families":list(FAMILIES),"seeds":list(SEEDS),
  "native_episode_count":len(trials)*sum(x[1] for x in PHASES),
  "original_native_topology":"unchanged-eight-cell-ring",
  "policy":"genuine-original-source-only-bridge.choose",
  "predictions_recorded":"before_each_chosen_public_consequence",
  "replay_ema_and_window":"same-native-selected-events-not-independent-actors",
  "oracle_optimal_action":"evaluator-only-ranking-ground-truth-not-shown-to-model",
  "raw_native_reward_score":"weighted-native-readout-not-certified-probability-or-calibrated-value",
  "snapshot_scope":"fresh-python-process-exact-intra-platform-identity",
  "pooled":metrics,
  "checkpoint_bytes_max":max(t["final_checkpoint_bytes"] for t in trials),
  "all_cold_restarts_verified":all(t["cold_restart"]["verified_new_interpreter"]
                                    for t in trials),
  "all_native_parameters_changed":all(t["real_native_weights_changed"] for t in trials),
  "elapsed_wall_seconds":round(time.perf_counter()-start,5)
}
if len(trials)!=64 or receipt["native_episode_count"]!=11520:
    raise AssertionError("SOURCE_FREE_TRACE_BUDGET_INVALID")
if not receipt["all_cold_restarts_verified"] or not receipt["all_native_parameters_changed"]:
    raise AssertionError("NATIVE_MODEL_OR_CHECKPOINT_AUTHORITY_NOT_PROVEN")

folder=os.environ["RUNNER_TEMP"]
with open(os.path.join(folder,"itd02_native_calibration_summary.json"),"w",encoding="utf-8") as f:
    json.dump(receipt,f,sort_keys=True,indent=2)
with open(os.path.join(folder,"itd02_native_calibration_trials.json"),"w",encoding="utf-8") as f:
    json.dump(trials,f,sort_keys=True,separators=(",",":"))
print("ITD02_PREQUENTIAL_CALIBRATION="+json.dumps({
  k:v for k,v in receipt.items() if k!="pooled"
} | {"pooled":metrics},sort_keys=True))
