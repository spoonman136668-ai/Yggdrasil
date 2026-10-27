"""Source-frozen audit: temporal phase averaging collapses distinct local codes.

On this source, the native predictor is a memoryless function of own+neighbor
binary bits, while reward heads at sites 0,2,5 always see own input=0. Two
predictions averaged commute, losing phase order; this proof never calls an
external task source or changes any original Yggdrasil implementation.
"""
import collections
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
from yggdrasil.itd02_native_task_bridge_dev import (
    NativeTaskRingBridgeDev, _temporal_public_bits, public_outcome, REWARDS
)
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, OBSERVATIONS, ACTION_SITES

SITES={0:(7,1), 2:(1,3), 5:(4,6)}
SOURCE=os.environ["SOURCE_SHA"]
CODES=[(o,a) for a in ACTIONS for o in OBSERVATIONS]
assert len(CODES)==15 and ACTION_SITES==(0,2,5)

def local_word(obs,action,site):
    neighbors=SITES[site]
    return tuple(
        tuple(_temporal_public_bits(obs,action,p)[n] for n in neighbors)
        for p in (0,1)
    )

def unordered_word(obs,action,site):
    return tuple(sorted(local_word(obs,action,site)))

capacity={}
all_collisions=set()
for site in ACTION_SITES:
    ordered={local_word(o,a,site) for o,a in CODES}
    unordered=collections.defaultdict(list)
    for obs,action in CODES:
        unordered[unordered_word(obs,action,site)].append((obs,action))
    aliases=[items for items in unordered.values() if len(items)>1]
    assert len(ordered)==15
    assert len(unordered)==9
    assert len(aliases)==6
    assert sorted(len(x) for x in aliases)==[2]*6
    capacity[str(site)]={
        "ordered_neighbor_words":len(ordered),
        "actual_phase_averaged_unordered_neighbor_words":len(unordered),
        "indistinguishable_context_pairs":aliases,
        "theoretical_unordered_two_phase_ceiling":10,
        "theoretical_ordered_two_phase_ceiling":16,
    }
    all_collisions.update(tuple(sorted(tuple(x) for x in group)) for group in aliases)
assert len(all_collisions)==6

def score(model,observation,action):
    vals=[]
    for phase in (0,1):
        pred=model.native.predict(_temporal_public_bits(observation,action,phase))
        vals.append(sum(float(reward)*pred[site]
                        for reward,site in zip(REWARDS,ACTION_SITES)))
    return statistics.mean(vals)

def cold(source,ids,transitions):
    program=(
        "import json,hashlib,sys;"
        "from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev;"
        "raw=sys.stdin.buffer.read();m=NativeTaskRingBridgeDev.restore(raw);"
        "print(json.dumps({'ids':m.model_identities(),'transitions':m.transitions,"
        "'sha':hashlib.sha256(m.checkpoint()).hexdigest()}))"
    )
    r=subprocess.run([sys.executable,"-B","-c",program],input=source,
                     capture_output=True,check=True,timeout=20)
    v=json.loads(r.stdout)
    assert v=={
        "ids":ids,"transitions":transitions,
        "sha":hashlib.sha256(source).hexdigest()
    },v

samples=[]
for seed in range(8):
    m=NativeTaskRingBridgeDev()
    orig=m.model_identities()
    for i in range(120):
        obs=OBSERVATIONS[(i+seed)%len(OBSERVATIONS)]
        act=ACTIONS[((i//3)+seed)%len(ACTIONS)]
        reward=(-3,0,10)[(i//7+seed)%3]
        m.start_observation(obs)
        m.accept_public_transition(act,"Nothing",reward,learning=True,terminal=True)
    assert m.transitions==120 and m.native.core.events==120
    ids=m.model_identities()
    assert ids!=orig
    snapshot=m.checkpoint()
    cold(snapshot,ids,120)
    restored=NativeTaskRingBridgeDev.restore(snapshot)
    contrasts=[]
    for group in sorted(all_collisions):
        (o1,a1),(o2,a2)=group
        x=score(restored,o1,a1)
        y=score(restored,o2,a2)
        if abs(x-y)>1e-12:
            raise AssertionError("SOURCE_FIXED_PHASE_AVERAGING_ALIAS_NOT_REAL")
        contrasts.append({"pair":[list(group[0]),list(group[1])],
                          "source_readout_score_1":x,
                          "source_readout_score_2":y,
                          "absolute_delta":abs(x-y)})
    samples.append({
        "seed":seed,
        "fresh_interpreter":True,
        "native_parameters_changed":True,
        "original_native_event_count":restored.native.core.events,
        "checkpoint_bytes":len(snapshot),
        "contrasts":contrasts
    })

receipt={
    "schema":"itd02.source-frozen.phase-average-invariance.v1",
    "source_sha":SOURCE,
    "authority":"source-free-structural-proof-only-NO-FSA",
    "scientific_first_use":False,
    "platform":platform.platform(),
    "architecture":"two native phase readouts averaged, one locally trained original runtime",
    "capacity_by_reward_output_site":capacity,
    "trained_native_models_checked":len(samples),
    "exact_trained_alias_checks":len(samples)*len(all_collisions),
    "source_original_native_public_training_events":len(samples)*120,
    "all_cold_process_restores":True,
    "no_input_action_bit_at_reward_site":True,
    "original_source_modified":False,
    "claim_boundary":"readout-equivalence for local native reward score, not equality of full agent chooser",
    "sample_models":samples,
}
assert receipt["exact_trained_alias_checks"]==48
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_phase_averaging_capacity.json"),
          "w",encoding="utf-8") as f:
    json.dump(receipt,f,indent=2,sort_keys=True)
print("ITD02_PHASE_AVERAGE_CAPACITY="+json.dumps({
    k:v for k,v in receipt.items() if k!="sample_models"
},sort_keys=True))
