"""MR34C original Crafter evaluator-only world vs rendering divergence audit.

The unmodified Crafter env.reset/step and Env._obs execute naturally. An
interpreter profiling callback snapshots original SOURCE-PRIVATE fields solely
into an offline scientific trace at the ENTRY and RETURN of original _obs.
No source-private state is supplied to the actor, learner or environment.
"""
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import sys
import time
import numpy as np

from research.mr34b.admit_source import exact_source, peak_resident

FROZEN = Path(__file__).with_name("frozen_protocol.json")
EXPECTED_SOURCE="e04542a2159f1aad3d4c5ad52e8185717380ee3a"
EXPECTED_PARENT="2f7553633979224338a82e5e3aa38bada1d59be6"

def sha(value):
    return sha256(value).hexdigest()

def encoded(value):
    if isinstance(value,np.ndarray):
        return {"dtype":str(value.dtype),"shape":list(value.shape),
                "values":value.tolist()}
    if isinstance(value,np.generic):
        return encoded(value.item())
    if isinstance(value,dict):
        return {str(k):encoded(v) for k,v in sorted(
            value.items(), key=lambda p:str(p[0]))}
    if isinstance(value,(list,tuple)):
        return [encoded(x) for x in value]
    if isinstance(value,(set,frozenset)):
        parts=[encoded(x) for x in value]
        return sorted(parts,key=lambda v:json.dumps(v,sort_keys=True))
    if value is None or isinstance(value,(int,float,bool,str)):
        return value
    raise ValueError("MR34C_UNSUPPORTED_SOURCE_OBJECT_FIELD_"+type(value).__name__)

def canonical_digest(obj):
    return sha(json.dumps(obj,sort_keys=True,separators=(",",":"),
                          allow_nan=False).encode())

def source_rng(env):
    state=env._world.random.get_state()
    return sha(state[0].encode()+state[1].tobytes()+
        json.dumps([int(state[2]),int(state[3]),float(state[4])],
                   separators=(",",":")).encode())

def native_state(env):
    world=env._world
    material=sha(world._mat_map.tobytes())
    index=sha(world._obj_map.tobytes())
    actual_order=[]
    for obj in world.objects:
        payload={
          "type":type(obj).__module__+"."+type(obj).__qualname__,
          "fields":{k:encoded(v) for k,v in sorted(vars(obj).items())
                    if k not in ("world","random","player")}
        }
        actual_order.append(payload)
    canonical=sorted(actual_order,
        key=lambda o:json.dumps(o,sort_keys=True,separators=(",",":")))
    model={
      "material_map":material,
      "canonical_typed_objects":canonical_digest(canonical),
      "original_source_player_pos_inventory_in_object_snapshot":True,
      "source_env_step":int(env._step),
      "source_unlocked":encoded(env._unlocked),
    }
    return {
      "original_material_grid_digest":material,
      "original_object_slot_index_digest":index,
      "original_canonical_physical_object_state_digest":
           model["canonical_typed_objects"],
      "original_actual_object_update_order_digest":canonical_digest(actual_order),
      "original_physical_state_digest":canonical_digest(model),
      "original_rng_before_render_digest":source_rng(env)
    }

def original_protocol():
    p=json.loads(FROZEN.read_text(encoding="utf-8"))
    prior=json.loads((Path(__file__).parent.parent/"mr34b"/
                      "frozen_protocol.json").read_text(encoding="utf-8"))
    if (p["schema"]!="yggdrasil.mr34c.original-crafter-world-versus-render-readonly.v1" or
        p["exact_previous_mr34b_head"]!=EXPECTED_PARENT or
        p["original_crafter_sha"]!=EXPECTED_SOURCE or
        p["frozen_mr34b_protocol_sha256"]!=
            sha((Path(__file__).parent.parent/"mr34b"/
                 "frozen_protocol.json").read_bytes()) or
        p["previously_consumed_development_seeds"]!=[911,919,929,937] or
        p["public_actor_stream_ids"]!=[0,1] or
        p["original_source_native_step_cap"]!=96 or
        p["original_source_native_episodes"]!=8 or
        prior["preregistered_new_development_only_seeds"]!=[911,919,929,937] or
        prior["public_action_stream_ids"]!=[0,1] or
        prior["maximum_original_native_actions_per_episode"]!=96 or
        p["no_source_or_environment_mutation"] is not True or
        p["no_actor_model_training"] is not True or
        p["source_native_first_use"] is not False):
        raise ValueError("MR34C_SOURCE_OR_PRECOMMIT_DRIFT")
    return p

def run(original):
    p=original_protocol()
    root=exact_source(original,EXPECTED_SOURCE)
    sys.path.insert(0,str(root))
    import crafter
    obs_code=crafter.Env._obs.__code__
    started=time.process_time_ns()
    audited=[]
    total_actions=0
    for seed in p["previously_consumed_development_seeds"]:
      for stream in p["public_actor_stream_ids"]:
        env=crafter.Env(seed=seed,reward=False,length=96)
        rng=random.Random(1000003*seed+337+10007*stream)
        frames=[]
        pending=[None]
        def inspect(frame,event,arg):
            if frame.f_code is obs_code and frame.f_locals.get("self") is env:
                if event=="call":
                    if pending[0] is not None:
                        raise ValueError("MR34C_SOURCE_RENDER_REENTRANCY")
                    pending[0]=native_state(env)
                elif event=="return":
                    if pending[0] is None:
                        raise ValueError("MR34C_ORIGINAL_RENDER_WITHOUT_ENTRY")
                    image=arg
                    if (not isinstance(image,np.ndarray) or
                        image.dtype!=np.uint8 or image.shape!=(64,64,3)):
                        raise ValueError("MR34C_ORIGINAL_PUBLIC_IMAGE_DRIFT")
                    event_data=dict(pending[0])
                    event_data["original_rng_after_render_digest"]=source_rng(env)
                    event_data["original_public_image_digest"]=sha(image.tobytes())
                    frames.append(event_data)
                    pending[0]=None
        try:
            sys.setprofile(inspect)
            initial=env.reset()
            if not np.array_equal(initial,np.asarray(initial)):
                raise ValueError("MR34C_INVALID_PUBLIC_RESET_IMAGE")
            for _ in range(p["original_source_native_step_cap"]):
                action=rng.randrange(len(env.action_names))
                # The original engine controls all physical and rendered changes.
                public,reward,done,info=env.step(action)
                total_actions+=1
                if done:
                    break
        finally:
            sys.setprofile(None)
            if hasattr(env,"close"):
                env.close()
        if pending[0] is not None or len(frames)<2:
            raise ValueError("MR34C_INCOMPLETE_EVALUATOR_ONLY_RENDER_TRACE")
        audited.append({"seed":seed,"stream":stream,
                        "original_native_actions":len(frames)-1,
                        "source_reset_and_next_public_image_state_trace":frames})
    if len(audited)!=8 or sum(x["original_native_actions"] for x in audited)!=total_actions:
        raise ValueError("MR34C_FROZEN_ORIGINAL_EPISODE_ACTION_DRIFT")
    exact_source(root,EXPECTED_SOURCE)
    print("MR34C_CRAFTER_ORIGINAL_WORLD_RENDER_AUDIT="+json.dumps({
        "original_source_sha":EXPECTED_SOURCE,
        "protocol_sha256":sha(FROZEN.read_bytes()),
        "original_source_reset_seeds_previously_consumed":[911,919,929,937],
        "authentic_original_episodes":len(audited),
        "native_original_actions":total_actions,
        "evaluator_only_original_state_and_public_image_trace":audited,
        "original_method_called_once_with_sys_profile_readonly_observation":True,
        "source_native_world_mutations_performed_by_auditor":False,
        "hidden_source_world_to_actor":False,
        "OS_process_cpu_ns_including_evaluator":time.process_time_ns()-started,
        "OS_peak_rss_bytes_including_evaluator":peak_resident(),
        "independent_first_use_consumed":False,
        "science_admission":"NO_GO",
        "G29_source_atlas":"FAIL_CLOSED"
    },sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr34c.crafter_world_render ORIGINAL")
    run(sys.argv[1])
