"""Source-frozen causal feature-sensitivity probe. No intervention in training."""
import collections
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time

from yggdrasil.itd02_native_task_bridge_dev import (
  NativeTaskRingBridgeDev, REWARDS, public_bits
)
from yggdrasil.itd02_local_ring_memory_dev import (
  ACTIONS, ACTION_SITES, OBSERVATIONS, OBS_SITES, _public_pulse
)

assert ACTIONS==("TurnAround","GoForward","Backup")
assert REWARDS==(-3,0,10) and ACTION_SITES==(0,2,5)
TRAIN=("LRV","MRV","Nothing")
ALL=TRAIN+("docked_LRV","docked_MRV")
FAMILIES=range(54,62)
SEEDS=range(52,60)
START=time.perf_counter()

def task_index(tag,family,seed,obs,salt=0):
    digest=hashlib.sha256(f"{tag}:{family}:{seed}:{obs}:{salt}".encode()).digest()
    return digest[0]%3

def private_laws(family,seed):
    old={obs:task_index("old",family,seed,obs) for obs in ALL}
    for salt in range(100):
        changed={obs:task_index("new",family,seed,obs,salt) for obs in ALL}
        if sum(old[o]!=changed[o] for o in TRAIN)>=2:
            return old,changed
    raise AssertionError("NO_CAUSALLY_CHANGED_PUBLIC_LAW")

def reward(optimal,action):
    chosen=ACTIONS.index(action)
    return 10 if chosen==optimal else (0 if chosen==(optimal+1)%3 else -3)

def fresh_restore(raw,expected_ids,expected_n):
    program=(
      "import json,sys,hashlib;"
      "from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev;"
      "raw=sys.stdin.buffer.read();m=NativeTaskRingBridgeDev.restore(raw);"
      "print(json.dumps({'ids':m.model_identities(), 'n':m.transitions,"
      "'sha':hashlib.sha256(m.checkpoint()).hexdigest()}))"
    )
    actual=json.loads(subprocess.run([sys.executable,"-B","-c",program],
      input=raw,capture_output=True,check=True,timeout=20).stdout)
    expected={"ids":expected_ids,"n":expected_n,
              "sha":hashlib.sha256(raw).hexdigest()}
    if actual!=expected:
        raise AssertionError("COLD_NATIVE_CHECKPOINT_RESTORE_FAILED")
    return NativeTaskRingBridgeDev.restore(raw)

def diagnostic(model,stage,family,seed):
    rows=[]
    for obs in ALL:
        zeros=_public_pulse(obs)
        native_only=model.native.predict([int(v) for v in zeros])
        # Zero action bit is held identical across all three comparisons.
        for aidx,action in enumerate(ACTIONS):
            with_action=model.native.predict(public_bits(obs,action))
            site=ACTION_SITES[aidx]
            other=[v for v in ACTION_SITES if v!=site]
            difference=[with_action[j]-native_only[j] for j in ACTION_SITES]
            own_diff=difference[aidx]
            reward_readout_diff=10*difference[2]-3*difference[0]
            rows.append({
                "family":family,"seed":seed,"stage":stage,
                "observation":obs,"action":action,
                "input_action_cell":site,
                "native_output_sites_with_action":[with_action[j] for j in ACTION_SITES],
                "native_output_sites_without_action":[native_only[j] for j in ACTION_SITES],
                "site_deltas":difference,
                "own_output_site_delta":own_diff,
                "other_output_site_deltas":[with_action[j]-native_only[j] for j in other],
                "source_reward_readout_delta":reward_readout_diff,
                "source_reward_readout_with_action":
                    -3*with_action[ACTION_SITES[0]]+10*with_action[ACTION_SITES[2]],
                "source_reward_readout_without_action":
                    -3*native_only[ACTION_SITES[0]]+10*native_only[ACTION_SITES[2]]
            })
    assert len(rows)==15
    return rows

def trial(family,seed):
    old,new=private_laws(family,seed)
    model=NativeTaskRingBridgeDev()
    initial_identity=model.model_identities()
    probes=diagnostic(model,"untrained",family,seed)
    visits=collections.Counter()
    earned=[]
    for phase,law,contexts in (("initial",old,TRAIN),("unfamiliar",new,ALL)):
        for episode in range(80):
            obs=contexts[(episode+seed)%len(contexts)]
            model.start_observation(obs)
            greedy=model.choose()
            v=visits[obs]
            forced=v<3 or (v>=3 and (v+seed)%9==0)
            selected=(ACTIONS[(v+seed)%3] if forced and v<3
                      else ACTIONS[(((v+seed)//9)+seed)%3] if forced
                      else greedy)
            visits[obs]+=1
            actual=reward(law[obs],selected)
            earned.append([phase,obs,selected,actual,forced])
            model.accept_public_transition(selected,"Nothing",actual,
                                           learning=True,terminal=True)
        stage="after80" if phase=="initial" else "after160"
        if stage=="after80":
            cp=model.checkpoint()
            model=fresh_restore(cp,model.model_identities(),80)
        probes.extend(diagnostic(model,stage,family,seed))
    if model.transitions!=160 or model.model_identities()==initial_identity:
        raise AssertionError("NATIVE_ORIGINAL_FIT_OR_COUNT_INVALID")
    return {"family":family,"seed":seed,"rows":probes,
            "public_consequences":earned,
            "checkpoint_bytes":len(model.checkpoint()),
            "fresh_process_after_80":True,
            "fitted_native_original":True}

data=[trial(f,s) for f in FAMILIES for s in SEEDS]
rows=[row for trial_result in data for row in trial_result["rows"]]

def aggregate(group):
    if not group:
        raise AssertionError("EMPTY_ACTION_OUTPUT_PROBE")
    means=lambda key:statistics.mean(x[key] for x in group)
    return {
        "n":len(group),
        "own_site_delta_mean":means("own_output_site_delta"),
        "own_site_delta_positive_fraction":
            statistics.mean(x["own_output_site_delta"]>0 for x in group),
        "absolute_own_site_delta":statistics.mean(abs(x["own_output_site_delta"]) for x in group),
        "mean_other_site_absolute_delta":
            statistics.mean(statistics.mean(abs(v) for v in x["other_output_site_deltas"]) for x in group),
        "source_reward_score_shift_mean":means("source_reward_readout_delta"),
        "native_reward_score_with_action":means("source_reward_readout_with_action"),
        "native_reward_score_observation_only":means("source_reward_readout_without_action")
    }

metrics={}
for stage in ("untrained","after80","after160"):
    stage_rows=[row for row in rows if row["stage"]==stage]
    metrics[stage]={
        "overall":aggregate(stage_rows),
        "by_action":{action:aggregate([r for r in stage_rows if r["action"]==action])
                     for action in ACTIONS},
        "by_family":{str(f):aggregate([r for r in stage_rows if r["family"]==f])
                     for f in FAMILIES}
    }
assert len(rows)==64*3*15
summary={
 "schema":"itd02.native-input-action-vs-reward-output-overlap.v1",
 "source_sha":os.environ["SOURCE_SHA"],
 "authority":"evaluation-only-structural-intervention-not-usable-as-policy",
 "scientific_first_use":False,
 "original_public_training_events":64*160,
 "source_free_task_families":list(FAMILIES),
 "seeds":list(SEEDS),
 "source_reward_labels":REWARDS,
 "original_action_and_output_site_overlap":ACTION_SITES,
 "original_local_genome_unchanged":True,
 "native_state_fresh_process_after80":all(t["fresh_process_after_80"] for t in data),
 "all_native_parameters_changed":all(t["fitted_native_original"] for t in data),
 "peak_full_checkpoint_bytes":max(t["checkpoint_bytes"] for t in data),
 "platform":platform.platform(),
 "metrics":metrics,
 "wall_seconds":round(time.perf_counter()-START,4)
}
if summary["original_public_training_events"]!=10240 or len(rows)!=2880:
    raise AssertionError("ORIGINAL_SOURCE_COUNT_OR_PROBE_ACCOUNTING_BAD")
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_native_action_bit_summary.json"),
          "w",encoding="utf-8") as f:
    json.dump(summary,f,sort_keys=True,indent=2)
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_native_action_bit_trials.json"),
          "w",encoding="utf-8") as f:
    json.dump(data,f,sort_keys=True,separators=(",",":"))
print("ITD02_ACTION_BIT_ABLATION="+json.dumps({
    k:v for k,v in summary.items() if k!="metrics"
} | {"metrics":{k:{"overall":v["overall"],"by_action":v["by_action"]}
                for k,v in metrics.items()}},sort_keys=True))
