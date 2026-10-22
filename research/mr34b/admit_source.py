"""MR34B: original third-party independently authored source admission only.

Two unchanged upstream repositories, frozen exact Git identities and public-only
native action-consequence experiences. No classifier, source-private supervision,
new protected scientific first use, or causal-information sufficiency claim.
"""
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import sys
import time

import numpy as np
import psutil

FROZEN=Path(__file__).with_name("frozen_protocol.json")
ENGINES=("farama","crafter")
ORIGINAL={
    "farama":"7f5853792ea7f04f75614661006d87fcf949f26d",
    "crafter":"e04542a2159f1aad3d4c5ad52e8185717380ee3a",
}

def protocol():
    cfg=json.loads(FROZEN.read_text(encoding="utf-8"))
    if (cfg["schema"]!="yggdrasil.mr34b.independent-original-source-admission.dev.v1" or
        cfg["exact_yggdrasil_parent_sha"]!="a7e85db2eefe975799acd2f2b23e981db0fcf91a" or
        cfg["primary_source"]["sha"]!=ORIGINAL["farama"] or
        cfg["independent_second_source"]["sha"]!=ORIGINAL["crafter"] or
        cfg["preregistered_new_development_only_seeds"]!=[911,919,929,937] or
        cfg["public_action_stream_ids"]!=[0,1] or
        cfg["maximum_original_native_actions_per_episode"]!=96 or
        cfg["planned_native_episodes_per_source"]!=8 or
        cfg["heldout_science_families_consumed"] is not False or
        cfg["protected_first_use"] is not False or
        cfg["no_native_yggdrasil_learner_training"] is not True or
        cfg["no_tuning_after_results"] is not True):
        raise ValueError("MR34B_FROZEN_INDEPENDENT_SOURCE_PROTOCOL_DRIFT")
    return cfg

def exact_source(original, expected):
    folder=Path(original).resolve()
    if not folder.is_dir():
        raise ValueError("MR34B_ORIGINAL_SOURCE_ABSENT")
    head=subprocess.check_output(["git","-C",str(folder),"rev-parse","HEAD"],text=True).strip()
    if head!=expected:
        raise ValueError("MR34B_INDEPENDENT_ORIGINAL_GIT_HEAD_DRIFT")
    dirty=subprocess.check_output(["git","-C",str(folder),"status","--porcelain"],text=True)
    if dirty.strip():
        raise ValueError("MR34B_INDEPENDENT_ORIGINAL_SOURCE_NOT_CLEAN")
    return folder

def peak_resident():
    proc=psutil.Process()
    if sys.platform=="win32":
        value=getattr(proc.memory_info(),"peak_wset",None)
        if not value:
            raise ValueError("MR34B_WINDOWS_OS_PEAK_RSS_UNSUPPORTED")
        return int(value)
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    raise ValueError("MR34B_PEAK_RSS_PLATFORM_NOT_SUPPORTED")

def public_bytes(obs, shape):
    if not isinstance(obs,np.ndarray) or obs.dtype!=np.uint8 or obs.shape!=shape:
        raise ValueError("MR34B_UNAUTHENTIC_NATIVE_PUBLIC_OBSERVATION")
    return obs.tobytes()

def run(engine,source):
    cfg=protocol()
    if engine not in ENGINES:
        raise ValueError("MR34B_UNREGISTERED_ORIGINAL_SOURCE_FAMILY")
    root=exact_source(source,ORIGINAL[engine])
    sys.path.insert(0,str(root))
    if engine=="farama":
        # Import unmodified source directly and use no mission, reward, pose,
        # inventory or hidden env fields as inputs.
        from research.mr27.natural_memory import source_guard
        source_guard(root)
        from minigrid.envs.doorkey import DoorKeyEnv
        make=lambda seed:DoorKeyEnv(size=8,render_mode=None)
        shape=(7,7,3)
        actions=7
    else:
        import crafter
        make=lambda seed:crafter.Env(seed=seed,reward=False,length=96)
        shape=(64,64,3)
        actions=17
    started=time.process_time_ns()
    receipts=[]
    public_frame_audits=[]
    total_steps=0
    total_public_bytes=0
    ended_early=0
    for seed in cfg["preregistered_new_development_only_seeds"]:
        for stream in cfg["public_action_stream_ids"]:
            rng=random.Random(1000003*seed+337+10007*stream)
            env=make(seed)
            # Source-native step, never source-generated secret state.
            if engine=="farama":
                initial,_=env.reset(seed=seed)
                obs=initial["image"]
            else:
                obs=env.reset()
            history=sha256()
            public_step_hashes=[]  # evaluator-side diagnostic only
            initial_public_digest=None
            steps=0
            try:
                before=public_bytes(obs,shape)
                initial_public_digest=sha256(before).hexdigest()
                for index in range(cfg["maximum_original_native_actions_per_episode"]):
                    action=rng.randrange(actions)
                    if engine=="farama":
                        after_obs,_reward,done,truncated,_info=env.step(action)
                        following=after_obs["image"]
                        finished=bool(done or truncated)
                    else:
                        after_obs,_reward,done,_info=env.step(action)
                        following=after_obs
                        finished=bool(done)
                    after=public_bytes(following,shape)
                    history.update(before)
                    history.update(bytes([action]))
                    history.update(after)
                    public_step_hashes.append(sha256(after).hexdigest())
                    before=after
                    steps+=1
                    total_public_bytes+=len(after)
                    if finished:
                        ended_early+=1
                        break
                if steps<=0:
                    raise ValueError("MR34B_ORIGINAL_SOURCE_NO_NATIVE_ACTIONS")
                receipts.append({
                    "reset_seed":seed,"source_stream":stream,
                    "actual_original_steps":steps,
                    "public_action_consequence_sha256":history.hexdigest(),
                })
                public_frame_audits.append({
                    "reset_seed":seed,
                    "source_stream":stream,
                    "initial_public_image_sha256":initial_public_digest,
                    "after_each_original_step_public_image_sha256":public_step_hashes,
                })
                total_steps+=steps
            finally:
                # Neither environment is allowed to expose hidden state to actor.
                if hasattr(env,"close"):
                    env.close()
    if len(receipts)!=8:
        raise ValueError("MR34B_FROZEN_SOURCE_EPISODE_COUNT_DRIFT")
    digest=sha256(json.dumps(receipts,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    print("MR34B_INDEPENDENT_ORIGINAL_SOURCE_ADMISSION="+json.dumps({
        "original_source_type":engine,
        "independently_authored_original_source_git_sha":ORIGINAL[engine],
        "protocol_sha256":sha256(FROZEN.read_bytes()).hexdigest(),
        "native_original_episode_count":len(receipts),
        "native_original_action_count":total_steps,
        "original_terminated_early_episodes":ended_early,
        "source_native_public_shape":list(shape),
        "source_native_actions":actions,
        "original_source_public_observation_bytes_processed":total_public_bytes,
        "original_native_action_consequence_digest":digest,
        "per_seed_stream_original_receipts":receipts,
        "read_only_public_image_divergence_diagnostics":public_frame_audits,
        "extra_public_hash_instrumentation_cost_included":True,
        "full_isolated_worker_cpu_ns":time.process_time_ns()-started,
        "full_original_source_process_os_peak_rss_bytes":peak_resident(),
        "new_protected_first_use_consumed":False,
        "actor_or_model_receives_original_private_info":False,
        "native_yggdrasil_learner_trained":False,
        "external_source_two_independent_repositories_admitted":True,
        "complete_two_family_model_comparison":"NOT_STARTED",
        "information_sufficiency_science_admission":"NO_GO",
        "G29_source_bound_atlas":"BLOCKED"
    },sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.mr34b.admit_source ENGINE ORIGINAL_SOURCE_DIR")
    run(sys.argv[1],sys.argv[2])
