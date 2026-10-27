"""Original native reward-site decoder diagnosis; synthetic PUBLIC-only fixture.

This file never supplies the evaluator's optimal action or outcome rule to the
model. All six score-site permutation controls are evaluation-only, computed
before the actual action outcome arrives, and never used to choose/train.
"""
import collections
import hashlib
import itertools
import json
import os
import platform
import statistics
import subprocess
import sys
import time

from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, ACTION_SITES, OBSERVATIONS
from yggdrasil.itd02_native_task_bridge_dev import (
    NativeTaskRingBridgeDev, REWARDS, public_bits, public_outcome
)

assert ACTIONS==("TurnAround","GoForward","Backup")
assert REWARDS==(-3,0,10) and ACTION_SITES==(0,2,5)
OBS_TRAIN=("LRV","MRV","Nothing")
OBS_FULL=OBS_TRAIN+("docked_LRV","docked_MRV")
FAMILIES=tuple(range(46,54))
SEEDS=tuple(range(44,52))
PHASES=(("initial",90,OBS_TRAIN),("unfamiliar",90,OBS_FULL))
SITE_PERMUTATIONS=tuple(itertools.permutations(range(3)))
assert len(SITE_PERMUTATIONS)==6
START=time.perf_counter()

def hash_target(kind,family,seed,obs,salt=0):
    h=hashlib.sha256(("%s/%d/%d/%s/%d"%(kind,family,seed,obs,salt)).encode())
    return h.digest()[0]%3

def evaluator_laws(family,seed):
    old={obs:hash_target("initial",family,seed,obs) for obs in OBS_FULL}
    for salt in range(100):
        new={obs:hash_target("unfamiliar",family,seed,obs,salt)
             for obs in OBS_FULL}
        if sum(old[o]!=new[o] for o in OBS_TRAIN)>=2:
            return old,new
    raise AssertionError("PRIVATE_EVALUATOR_SHIFT_NOT_ESTABLISHED")

def private_reward(optimal,action):
    selected=ACTIONS.index(action)
    if selected==optimal:
        return 10
    if selected==(optimal+1)%3:
        return 0
    return -3

def best(values):
    return ACTIONS[max(range(3),key=lambda i:values[i])]

def site_readout(prediction,perm):
    return sum(float(REWARDS[j])*prediction[perm[j]] for j in range(3))

def cold_restore(checkpoint,identities,transitions):
    cmd=(
     "import hashlib,json,sys;"
     "from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev;"
     "raw=sys.stdin.buffer.read();m=NativeTaskRingBridgeDev.restore(raw);"
     "print(json.dumps({'ids':m.model_identities(),'n':m.transitions,"
     "'sha':hashlib.sha256(m.checkpoint()).hexdigest()}))"
    )
    x=subprocess.run([sys.executable,"-B","-c",cmd],input=checkpoint,
                     capture_output=True,check=True,timeout=20)
    o=json.loads(x.stdout)
    if o!={"ids":identities,"n":transitions,
           "sha":hashlib.sha256(checkpoint).hexdigest()}:
        raise AssertionError("SOURCE_FROZEN_COLD_RESTART_FAILED")
    return NativeTaskRingBridgeDev.restore(checkpoint)

def trial(family,seed):
    old,new=evaluator_laws(family,seed)
    bridge=NativeTaskRingBridgeDev()
    initial_ids=bridge.model_identities()
    seen=collections.Counter()
    phases={}
    cold=False
    for phase,length,contexts in PHASES:
        law=old if phase=="initial" else new
        events=[]
        for i in range(length):
            obs=contexts[(i+seed)%len(contexts)]
            bridge.start_observation(obs)
            preds=[
                bridge.native.predict(public_bits(obs,action))
                for action in ACTIONS
            ]
            site_preds=[[float(output[site]) for site in ACTION_SITES]
                        for output in preds]
            if any(not 0<=v<=1 for item in site_preds for v in item):
                raise AssertionError("PREDICTION_OUTSIDE_SIGMOID_DOMAIN")
            perms={
                "".join(map(str,perm)):[
                    site_readout(site_preds[i],perm) for i in range(3)
                ]
                for perm in SITE_PERMUTATIONS
            }
            native_scores=bridge.native_reward_scores()
            original=perms["012"]
            if any(abs(a-b)>1e-12 for a,b in zip(original,native_scores)):
                raise AssertionError("SOURCE_REWARD_SITE_DECODER_MISMATCH")
            memory=bridge.memory.q_values()
            fusion=[memory[j]+0.15*native_scores[j] for j in range(3)]
            greedy=bridge.choose()
            assert greedy==best(fusion)
            visit=seen[obs]
            forced=visit<3 or (visit>=3 and (visit+seed)%9==0)
            if forced:
                action=ACTIONS[((visit+seed)%3 if visit<3
                                else ((visit+seed)//9+seed)%3)]
            else:
                action=greedy
            seen[obs]+=1
            action_index=ACTIONS.index(action)
            # Only evaluator owns the reward law. No oracle in bridge scoring.
            reward=private_reward(law[obs],action)
            categorical_index=REWARDS.index(reward)
            outcome=public_outcome("Nothing",reward)
            assert sum(outcome[site] for site in ACTION_SITES)==1
            assert outcome[ACTION_SITES[categorical_index]]==1
            chosen_sites=site_preds[action_index]
            bits=[int(j==categorical_index) for j in range(3)]
            cases={
               k:best(values) for k,values in perms.items()
            }
            records={
                "family":family,"seed":seed,"phase":phase,"obs":obs,
                "action":action,"reward":reward,"forced":forced,
                "correct_action":ACTIONS[law[obs]],
                "original_fused":greedy,
                "native_choice":cases["012"],
                "memory_choice":best(memory),
                "site_predictions_for_chosen":chosen_sites,
                "site_reward_bits":bits,
                "original_native_scores":native_scores,
                "native_site_probabilities_per_action":site_preds,
                "decoder_choices":cases,
                "original_fused_scores":fusion,
            }
            events.append(records)
            bridge.accept_public_transition(action,"Nothing",reward,
                                           learning=True,terminal=True)
        phases[phase]=events
        if phase=="initial":
            cp=bridge.checkpoint()
            bridge=cold_restore(cp,bridge.model_identities(),90)
            cold=True
    if bridge.transitions!=180 or not cold:
        raise AssertionError("NATIVE_EVENTS_NOT_RETAINED")
    return {
      "family":family,"seed":seed,"phases":phases,
      "native_weights_changed":bridge.model_identities()!=initial_ids,
      "fresh_interpreter_verified":cold,
      "checkpoint_bytes":len(bridge.checkpoint()),
      "task_law_fingerprints":{
          "old":hashlib.sha256(json.dumps(old,sort_keys=True).encode()).hexdigest(),
          "new":hashlib.sha256(json.dumps(new,sort_keys=True).encode()).hexdigest()
      }
    }

def aggregate(events):
    n=len(events)
    if not n:
        raise AssertionError("EMPTY_DIAGNOSTIC")
    out={
       "events":n,
       "forced_events":sum(e["forced"] for e in events),
       "public_rewards":dict(sorted(collections.Counter(str(e["reward"]) for e in events).items())),
       "native_rank_accuracy":statistics.mean(e["native_choice"]==e["correct_action"] for e in events),
       "memory_rank_accuracy":statistics.mean(e["memory_choice"]==e["correct_action"] for e in events),
       "fused_rank_accuracy":statistics.mean(e["original_fused"]==e["correct_action"] for e in events),
       "actual_action_accuracy":statistics.mean(e["action"]==e["correct_action"] for e in events),
       "native_top_actions":dict(sorted(collections.Counter(e["native_choice"] for e in events).items())),
       "fused_top_actions":dict(sorted(collections.Counter(e["original_fused"] for e in events).items())),
       "selected_action_counts":dict(sorted(collections.Counter(e["action"] for e in events).items())),
       "correct_action_counts":dict(sorted(collections.Counter(e["correct_action"] for e in events).items())),
       "reward_label_sites":{},
       "decoder_permutation_ranking":{},
       "mean_site_probabilities_by_input_action":{},
    }
    for j,label in enumerate(REWARDS):
        predictions=[e["site_predictions_for_chosen"][j] for e in events]
        bits=[e["site_reward_bits"][j] for e in events]
        label_true=[k for k,v in zip(predictions,bits) if v]
        label_false=[k for k,v in zip(predictions,bits) if not v]
        out["reward_label_sites"][str(label)]={
            "output_cell_site":ACTION_SITES[j],
            "target_bit_positive_rate":statistics.mean(bits),
            "prediction_bit_mean":statistics.mean(predictions),
            "bit_brier":statistics.mean((p-y)**2 for p,y in zip(predictions,bits)),
            "signed_prediction_bias":statistics.mean(p-y for p,y in zip(predictions,bits)),
            "mean_prediction_when_bit_on":statistics.mean(label_true) if label_true else None,
            "mean_prediction_when_bit_off":statistics.mean(label_false) if label_false else None,
        }
    for perm in SITE_PERMUTATIONS:
        key="".join(map(str,perm))
        out["decoder_permutation_ranking"][key]={
            "rank_accuracy":statistics.mean(e["decoder_choices"][key]==e["correct_action"] for e in events),
            "top_actions":dict(sorted(collections.Counter(e["decoder_choices"][key] for e in events).items()))
        }
    for a_index,action in enumerate(ACTIONS):
        out["mean_site_probabilities_by_input_action"][action]=[
            statistics.mean(e["native_site_probabilities_per_action"][a_index][j]
                            for e in events) for j in range(3)
        ]
    return out

trials=[trial(f,s) for f in FAMILIES for s in SEEDS]
metrics={}
for phase,_,_ in PHASES:
    events=[e for t in trials for e in t["phases"][phase]]
    metrics[phase]={
       "overall":aggregate(events),
       "last30_per_trial":aggregate([e for t in trials for e in t["phases"][phase][-30:]]),
       "by_actual_action":{a:aggregate([e for e in events if e["action"]==a])
                           for a in ACTIONS},
       "by_family":{str(f):aggregate([e for e in events if e["family"]==f])
                    for f in FAMILIES}
    }
receipt={
 "schema":"itd02.original-native-reward-sites.prequential-diagnostic.v1",
 "authority":"synthetic-public-interface-development-only-no-FSA",
 "source_sha":os.environ["SOURCE_SHA"],
 "platform":platform.platform(),
 "families":list(FAMILIES),"seeds":list(SEEDS),
 "original_native_public_actions":sum(len(t["phases"][p]) for t in trials
                                     for p in ("initial","unfamiliar")),
 "source_outcome_site_reward_map":dict(zip(map(str,REWARDS),ACTION_SITES)),
 "source_native_readout":"-3 * site0 + 0 * site2 + 10 * site5",
 "interpretation":"three independent native sigmoid outputs, NOT mutually-exclusive reward probabilities",
 "forced_action_schedule":"first three per public observation, then every ninth with rotating action",
 "decoder_negative_controls":"all 6 evaluation-only site permutations, no selection/training from controls",
 "model_source_unchanged":True,
 "frozen_source_snapshots_retained":all(t["fresh_interpreter_verified"] for t in trials),
 "native_learning_observed":all(t["native_weights_changed"] for t in trials),
 "maximum_checkpoint_bytes":max(t["checkpoint_bytes"] for t in trials),
 "pooled":metrics,
 "wall_seconds":round(time.perf_counter()-START,4)
}
if len(trials)!=64 or receipt["original_native_public_actions"]!=11520:
    raise AssertionError("DIAGNOSTIC_RESOURCE_ACCOUNTING_MISMATCH")
if not receipt["frozen_source_snapshots_retained"] or not receipt["native_learning_observed"]:
    raise AssertionError("NATIVE_SOURCE_NO_COLD_PERSISTENCE")
out=os.environ["RUNNER_TEMP"]
with open(os.path.join(out,"itd02_native_reward_site_summary.json"),"w",encoding="utf-8") as f:
    json.dump(receipt,f,indent=2,sort_keys=True)
with open(os.path.join(out,"itd02_native_reward_site_trials.json"),"w",encoding="utf-8") as f:
    json.dump(trials,f,separators=(",",":"),sort_keys=True)
print("ITD02_REWARD_SITE_SUMMARY="+json.dumps({
    k:v for k,v in receipt.items() if k!="pooled"
}|{"pooled":{stage:{"overall":metrics[stage]["overall"],
                   "last30_per_trial":metrics[stage]["last30_per_trial"]}
            for stage in metrics}},sort_keys=True))
