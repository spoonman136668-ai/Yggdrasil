"""MR34I0 -- source-native third independent family BIRTH; DEV only.

The original sparisi/gym_gridworlds engine and BirdEyeWrapper execute
unchanged. Actor uses only original public action-space size; it never reads
info['state'], source private grid, reward, goal, RNG or evaluator answers.
Do not mistake development source admission for unfamiliar-source transfer.
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
UPSTREAM_SHA="c6d406680d552489c3230dec9714b066c7fd303d"
SEEDS=(2309,2311,2333,2339,2341,2347,2351,2357)
STREAMS=(0,1)
ORIGINAL_GAME="Gym-Gridworlds/TwoRoom-Quicksand-3x5-v0"

def sha(x):
    return sha256(x).hexdigest()

def canonical(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False)

def frozen():
    p=json.loads(FROZEN.read_text(encoding="utf-8"))
    original=p["third_independently_authored_original_source"]
    if (p["schema"]!="yggdrasil.mr34i0.independent-third-original-native-source-birth.dev.v1"
        or p["exact_predecessor_MR34H_SHA"]!="2aa382619d59bd76f1afd6f86afbbb1eaaf719b8"
        or original["repository"]!="sparisi/gym_gridworlds"
        or original["sha"]!=UPSTREAM_SHA
        or original["source_original_factory"]!=
            "gymnasium.make('Gym-Gridworlds/TwoRoom-Quicksand-3x5-v0',render_mode=None)"
        or p["development_source_admission_only_seeds"]!=list(SEEDS)
        or p["public_policy_streams"]!=list(STREAMS)
        or p["max_native_original_actions_per_episode"]!=48
        or p["planned_original_native_source_episodes"]!=16
        or p["no_original_upstream_edits"] is not True
        or p["no_new_cognitive_model_training"] is not True):
        raise ValueError("MR34I0_FROZEN_SOURCE_OR_DECISION_IDENTITY_DRIFT")
    return p

def source_original_git_readonly(root):
    root=Path(root).resolve()
    if not root.is_dir():
        raise ValueError("MR34I0_ORIGINAL_INDEPENDENT_SOURCE_ABSENT")
    commit=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if commit!=UPSTREAM_SHA:
        raise ValueError("MR34I0_ORIGINAL_SOURCE_GIT_SHA_DRIFT")
    status=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True)
    if status.strip():
        raise ValueError("MR34I0_ORIGINAL_SOURCE_WORKTREE_MUTATED")
    license_text=(root/"LICENSE").read_text(encoding="utf-8")
    if "MIT License" not in license_text or "Simone Parisi" not in license_text:
        raise ValueError("MR34I0_UNVERIFIED_ORIGINAL_UPSTREAM_LICENSE")
    return root

def public_observation(o):
    if (not isinstance(o,np.ndarray) or
        o.shape!=(3,3) or
        o.dtype.kind!="U"):
        raise ValueError("MR34I0_NATIVE_SOURCE_PARTIAL_PUBLIC_VIEW_INVALID")
    framed=bytearray()
    for value in o.flat:
        value=str(value)
        if len(value)!=1:
            raise ValueError("MR34I0_SOURCE_PUBLIC_CELL_NOT_CHARACTER")
        encoded=value.encode("utf-8")
        framed.extend(len(encoded).to_bytes(4,"little"))
        framed.extend(encoded)
    return bytes(framed)

def original_run(root):
    cfg=frozen()
    upstream=source_original_git_readonly(root)
    sys.path.insert(0,str(upstream))
    import gymnasium as gym
    import gym_gridworlds # registered independently authored ORIGINAL environments
    from gym_gridworlds.observation_wrappers import BirdEyeWrapper
    start=time.process_time_ns()
    episodes=[]
    total_original_steps=0
    observed_public_changed=0
    source_bytes=0
    for seed in SEEDS:
      for stream in STREAMS:
        policy=random.Random(1000003*seed+337+10007*stream)
        env=BirdEyeWrapper(gym.make(ORIGINAL_GAME,render_mode=None),
                           view_radius=1)
        original_obs,_info=env.reset(seed=seed)
        before=public_observation(original_obs)
        initial_digest=sha(before)
        native_event_hash=sha256()
        steps=0
        changes=0
        try:
          for _ in range(cfg["max_native_original_actions_per_episode"]):
            # Action only from original PUBLIC action-space shape.
            action=policy.randrange(int(env.action_space.n))
            next_obs,_reward,terminated,truncated,_info=env.step(action)
            after=public_observation(next_obs)
            native_event_hash.update(len(before).to_bytes(4,"little"))
            native_event_hash.update(before)
            native_event_hash.update(bytes([action]))
            native_event_hash.update(len(after).to_bytes(4,"little"))
            native_event_hash.update(after)
            native_event_hash.update(bytes([int(terminated),int(truncated)]))
            changes+=int(before!=after)
            source_bytes+=len(before)+len(after)
            steps+=1
            before=after
            if terminated or truncated:
                break
          if steps<1:
            raise ValueError("MR34I0_ORIGINAL_NATIVE_ENV_NO_STEPS")
        finally:
          env.close()
        episodes.append({
            "original_development_reset_seed":seed,
            "policy_stream":stream,
            "original_source_native_action_count":steps,
            "source_public_initial_observation_sha256":initial_digest,
            "original_source_native_public_action_next_sha256":
                native_event_hash.hexdigest(),
            "source_genuine_partial_public_changed_steps":changes})
        total_original_steps+=steps
        observed_public_changed+=changes
    if len(episodes)!=16 or observed_public_changed<1:
        raise ValueError("MR34I0_NATIVE_SOURCE_BIRTH_SANITY_FAIL_CLOSED")
    source_original_git_readonly(upstream)
    rss=psutil.Process().memory_info()
    if sys.platform=="win32":
        peak=getattr(rss,"peak_wset",None)
        if not peak:
            raise ValueError("MR34I0_WINDOWS_OS_PEAK_RSS_UNAVAILABLE")
        peak=int(peak)
    elif sys.platform.startswith("linux"):
        import resource
        peak=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    else:
        raise ValueError("MR34I0_UNSUPPORTED_RUNNER_OS")
    serial=canonical(episodes).encode()
    print("MR34I0_INDEPENDENT_THIRD_SOURCE_BIRTH="+canonical({
        "source_author_original_repository":"sparisi/gym_gridworlds",
        "source_original_sha":UPSTREAM_SHA,
        "source_original_MIT_license_verified":True,
        "frozen_precode_protocol_sha256":sha(FROZEN.read_bytes()),
        "original_native_partial_public_source":"BirdEyeWrapper(radius=1)",
        "original_public_observation_shape":[3,3],
        "original_native_action_space":5,
        "authentic_development_only_original_episodes":len(episodes),
        "authentic_original_source_step_actions":total_original_steps,
        "genuine_native_public_response_changed_steps":observed_public_changed,
        "source_public_trace_byte_volume":source_bytes,
        "source_episode_receipts":episodes,
        "original_native_source_public_action_consequence_digest":sha(serial),
        "serialized_source_evidence_bytes":len(serial),
        "whole_source_actor_hash_process_cpu_ns":time.process_time_ns()-start,
        "whole_source_actor_hash_OS_peak_RSS_bytes":peak,
        "protected_unfamiliar_scientific_first_use_consumed":False,
        "future_source_family_unfamiliar_task_test_executed":False,
        "native_Wingless_or_Yggdrasil_cognition_trained":False,
        "native_public_observation_not_evaluator_private_state":True,
        "source_admission_scientific_transfer":"NOT_TESTED",
        "G29_exact_source_atlas_full_regression":"BLOCKED",
        "scientific_admission":"NO_GO"}))

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr34i.admit_gridworld ORIGINAL_SOURCE")
    original_run(sys.argv[1])
