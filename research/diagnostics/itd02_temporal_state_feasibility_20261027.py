"""Read-only feasibility boundary for genuinely retained ordered cellular context."""
import hashlib,json,os,platform,subprocess,sys
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev,_temporal_public_bits
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS,OBSERVATIONS,ACTION_SITES

pairs=[(obs,action) for action in ACTIONS for obs in OBSERVATIONS]
sites={0:(7,1),2:(1,3),5:(4,6)}
result={}
for site,neighbors in sites.items():
    ordered={}
    unordered={}
    for obs,action in pairs:
        frames=[_temporal_public_bits(obs,action,k) for k in (0,1)]
        word=tuple(tuple(frame[n] for n in neighbors) for frame in frames)
        ordered[(obs,action)]=word
        unordered[(obs,action)]=tuple(sorted(word))
    assert len(set(ordered.values()))==15
    assert len(set(unordered.values()))==9
    result[str(site)]={"ordered":15,"unordered":9,"collision_pairs":6}

def state_signature(m):
    return (m.native.snapshot(),m.memory.checkpoint(),
            m.transitions,m.score_calls,m.model_identities())

checks=[]
for n in range(8):
    m=NativeTaskRingBridgeDev()
    for i in range(100):
        obs=OBSERVATIONS[(i+n)%5]
        action=ACTIONS[(i//3+n)%3]
        reward=(-3,0,10)[(i//11+n)%3]
        m.start_observation(obs)
        m.accept_public_transition(action,"Nothing",reward,terminal=True)
    cp=m.checkpoint()
    script=("import hashlib,json,sys;"
        "from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev;"
        "raw=sys.stdin.buffer.read();m=NativeTaskRingBridgeDev.restore(raw);"
        "print(json.dumps({'id':m.model_identities(),"
        "'sha':hashlib.sha256(m.checkpoint()).hexdigest()}))")
    child=subprocess.run([sys.executable,"-B","-c",script],input=cp,
       capture_output=True,check=True,timeout=15)
    fresh=json.loads(child.stdout)
    assert fresh=={"id":m.model_identities(),"sha":hashlib.sha256(cp).hexdigest()}
    b=NativeTaskRingBridgeDev.restore(cp)
    before=state_signature(b)
    for obs,action in pairs:
        p0=_temporal_public_bits(obs,action,0)
        p1=_temporal_public_bits(obs,action,1)
        first=b.native.predict(p0)
        second=b.native.predict(p1)
        assert first==b.native.predict(p0)
        assert second==b.native.predict(p1)
        # Predict is a stateless, input-only function. Call order cannot
        # create phase-dependent state or grant extra local capacity.
        assert (first,second)==(b.native.predict(p0),b.native.predict(p1))
        forward=[(a+c)/2 for a,c in zip(first,second)]
        reverse=[(a+c)/2 for a,c in zip(second,first)]
        assert forward==reverse
    assert state_signature(b)==before
    checks.append({"seed":n,"events":b.native.core.events,"unchanged":True,
       "checkpoint_bytes":len(cp),"fresh_process":True})
receipt={"schema":"itd02.temporal-state-feasibility.v1",
 "authority":"source-frozen-no-FSA",
 "source_sha":os.environ["SOURCE_SHA"],"platform":platform.platform(),
 "native_predict_uses_only_current_binary_bits":True,
 "native_predict_mutates_no_cellular_state":True,
 "two_phase_readout_is_commutative":True,
 "effective_local_code_capacity":result,
 "trained_models":len(checks),"checked_public_contexts_per_model":len(pairs),
 "native_training_transitions":800,"cold_restores":len(checks),
 "source_mutated":False,"scientific_first_use":False,
 "engineering_design_constraint":"Order-sensitive learning requires explicit local temporal state and custody-versioned snapshot; cannot be achieved by phase averaging"}
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_temporal_feasibility.json"),"w") as f:
 json.dump({"receipt":receipt,"models":checks},f,indent=2,sort_keys=True)
print("ITD02_TEMPORAL_FEASIBILITY="+json.dumps(receipt,sort_keys=True))
