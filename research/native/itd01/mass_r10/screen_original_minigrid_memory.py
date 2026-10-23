#!/usr/bin/env python3
"""CS03 genuine Farama MiniGrid Memory public cue visibility and fork-alias screen.

Only source-owned MemoryEnv.reset/step used; fixed scripted navigator is
EVALUATOR-PRIVILEGED and absolutely not a trained learned memory agent.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from collections import defaultdict

PIN = "7f5853792ea7f04f75614661006d87fcf949f26d"
FIRST = "5992c17ff3730332171475f7913d7de27e00cb2e"
BLOBS = {
    "minigrid/envs/memory.py": "660b0a1b769948034c87bb421759c2b9a4f24548",
    "minigrid/minigrid_env.py": "eb29e9a902de0715ab77ec981a2113576d7664fa",
    "minigrid/__init__.py": "41b4a731255d19bdf61072b7100e752a759a3ae4",
    "pyproject.toml": "61ab88372ca553af255a42564260994be808ac12",
}
SEEDS = tuple(range(940000, 940128))
EXPECTED_PUBLIC_EPISODES = 256
SIZE = 13

def guard(c,reason):
    if not c:
        raise RuntimeError(reason)

def cmd(args,cwd):
    p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,timeout=25)
    return p.returncode,p.stdout.strip(),p.stderr[-1500:]

def original_source(root):
    rc,got,_=cmd(["git","rev-parse","HEAD"],root)
    guard(rc==0 and got==PIN,"UPSTREAM_HEAD_MISMATCH")
    for path,sha in sorted(BLOBS.items()):
        rc,got,_=cmd(["git","hash-object","--",path],root)
        guard(rc==0 and got==sha,"ORIGINAL_SOURCE_BLOB_MISMATCH:"+path)
    rc,_,_=cmd(["git","diff","--exit-code","--","minigrid","pyproject.toml"],root)
    guard(rc==0,"UPSTREAM_SOURCE_TRACKED_DIFF")
    return {"source_git_sha":PIN,"source_original_blobs":BLOBS}

def public_image(obs):
    from minigrid.core.constants import OBJECT_TO_IDX
    import numpy as np
    guard(set(("image","direction","mission"))<=set(obs),"ORIGINAL_OBS_SCHEMA")
    image=obs["image"]
    guard(image.shape==(7,7,3),"ORIGINAL_PARTIAL_IMAGE_SHAPE")
    indices=(OBJECT_TO_IDX["key"],OBJECT_TO_IDX["ball"])
    located=np.argwhere(np.isin(image[:,:,0],indices))
    guard(len(located)==1,"CUE_OR_UPPER_OBJECT_NOT_UNIQUE_IN_PUBLIC_IMAGE")
    pos=tuple(int(x) for x in located[0])
    t=int(image[pos[0],pos[1],0])
    return "key" if t==indices[0] else "ball"

def fork_hash(obs):
    image=obs["image"]
    data=image.tobytes()+(
        json.dumps({"shape":list(image.shape),"dtype":str(image.dtype),
                    "direction":int(obs["direction"]),"mission":obs["mission"]},
                   sort_keys=True,separators=(",",":"))).encode()
    return hashlib.sha256(data).hexdigest()

def public_step(env,action,steps):
    from minigrid.core.actions import Actions
    guard(action in (Actions.left,Actions.right,Actions.forward),"ILLEGAL_NAV_ACTION")
    obs,reward,end,trunc,info=env.step(action)
    steps.append(int(action))
    guard(end is False and trunc is False,"PRE_FORK_SOURCE_TERMINATED")
    guard(float(reward)==0.0,"UNEXPECTED_PRE_FORK_REWARD")
    guard(isinstance(info,dict),"UNEXPECTED_ORIGINAL_INFO")
    return obs

def original_episode(seed,branch):
    from minigrid.envs.memory import MemoryEnv
    from minigrid.core.actions import Actions
    from minigrid.core.constants import OBJECT_TO_IDX
    env=MemoryEnv(size=SIZE,random_length=False,agent_view_size=7,render_mode=None)
    try:
        reset_obs,info=env.reset(seed=seed)
        guard(isinstance(info,dict),"SOURCE_RESET_INFO")
        guard(reset_obs["image"].shape==(7,7,3),"SOURCE_RESET_IMAGE")
        start_x,start_y=(int(z) for z in env.agent_pos)  # EVALUATOR-ONLY navigator
        guard(start_y==SIZE//2 and 1<=start_x<=SIZE-3 and env.agent_dir==0,
              "ORIGINAL_START_LAYOUT_CHANGED")
        initial_cue_visible=bool(env.agent_sees(1,SIZE//2-1)) # auditor-only; NOT policy
        steps=[]
        obs=public_step(env,Actions.left,steps)
        obs=public_step(env,Actions.left,steps)
        for _ in range(start_x-1):
            obs=public_step(env,Actions.forward,steps)
        guard(tuple(int(z) for z in env.agent_pos)==(1,SIZE//2),"BACKTRACK_NOT_AT_CUE")
        obs=public_step(env,Actions.right,steps) # west -> north
        guard(int(env.agent_dir)==3 and bool(env.agent_sees(1,SIZE//2-1)),
              "ORIGINAL_CUE_NOT_LEGALLY_OBSERVABLE")
        cue=public_image(obs) # one bit read STRICTLY from public original OBS
        obs=public_step(env,Actions.right,steps) # north -> east
        for _ in range(SIZE-3): # x=1 -> x=11
            obs=public_step(env,Actions.forward,steps)
        guard(tuple(int(z) for z in env.agent_pos)==(SIZE-2,SIZE//2),
              "ORIGINAL_FORK_LOCATION_DRIFT")
        obs=public_step(env,Actions.left,steps) # east -> north
        guard(int(env.agent_dir)==3 and not bool(env.agent_sees(1,SIZE//2-1)),
              "EARLIER_CUE_STILL_VISIBLE_AT_FORK")
        upper=public_image(obs) # only upper object in public fork view
        frozen_choice="upper" if (cue==upper if branch=="remember" else True) else "lower"
        snap=fork_hash(obs)
        # Evaluator truth checked AFTER the public fork action has been frozen.
        upper_success=tuple(env.success_pos)==(SIZE-2,SIZE//2-1)
        guard(tuple(env.failure_pos) in ((SIZE-2,SIZE//2-1),
                                        (SIZE-2,SIZE//2+1)),
              "ORIGINAL_END_OBJECT_LAYOUT_INVALID")
        guard(upper_success == (cue==upper),
              "SOURCE_PUBLIC_CUE_DOES_NOT_IDENTIFY_END")
        if frozen_choice=="lower":
            obs=public_step(env,Actions.left,steps)
            obs=public_step(env,Actions.left,steps)
        action=Actions.forward
        final,r,terminated,truncated,final_info=env.step(action)
        steps.append(int(action))
        guard(terminated is True and truncated is False,"NO_NATIVE_TERMINAL")
        guard(isinstance(final_info,dict),"SOURCE_END_INFO")
        actual_correct=float(r)>0
        expected_correct=(frozen_choice=="upper")==upper_success
        guard(actual_correct==expected_correct,"ORIGINAL_REWARD_OR_TARGET_MISMATCH")
        guard(env.step_count==len(steps),"ORIGINAL_STEP_COUNT_MISMATCH")
        guard(env.step_count<env.max_steps,"ORIGINAL_TIME_BUDGET_EXCEEDED")
        return {
            "seed":seed,"branch":branch,"evaluator_start_x":start_x,
            "original_initial_cue_visible":initial_cue_visible,
            "original_cue_legally_observed_after_backtrack":True,
            "public_cue":cue,"public_upper_exit_object":upper,
            "fork_public_observation_sha256":snap,
            "public_fork_choice":frozen_choice,
            "source_success_upper":upper_success, # auditor evidence ONLY
            "source_native_success":actual_correct,
            "original_reward":float(r),
            "original_step_calls":len(steps),
            "original_step_trace_sha256":hashlib.sha256(bytes(steps)).hexdigest()
        }
    finally:
        env.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    target=Path(args.out)
    target.mkdir(parents=True,exist_ok=True)
    receipt={
        "schema":"mass.cs03.original-minigrid-memory-source-audit.v1",
        "frozen_first_prereg":FIRST,
        "source_role":"PUBLIC_DEVELOPMENT_ENGINEERING_ONLY",
        "scripted_navigation_uses_privileged_position_for_normalization":True,
        "decision_cue_derived_from_public_observation_only":True,
        "trained_learner_executed":False,
        "original_episodes_required":EXPECTED_PUBLIC_EPISODES,
        "original_source_steps_completed":0,
        "original_episodes_completed":0,
        "protected_first_use_consumed":False,
        "native_yggdrasil_model_tested":False,
        "controller_science_authority_exercised":False,
        "public_source_records":[],
        "disposition":"PUBLIC_CS03_HISTORY_REQUIREMENT_NO_GO"
    }
    try:
        receipt["source"]=original_source(Path(args.upstream).resolve())
        from minigrid.envs.memory import MemoryEnv
        import inspect
        required=(Path(args.upstream).resolve()/"minigrid"/"envs"/"memory.py")
        guard(Path(inspect.getfile(MemoryEnv)).resolve()==required,
              "NOT_ORIGINAL_MINIGRID_ENV_CLASS")
        seen={}
        groups=defaultdict(list)
        for seed in SEEDS:
            pair=[original_episode(seed,branch) for branch in ("remember","fixed_upper")]
            m,f=pair
            guard(m["public_cue"]==f["public_cue"] and
                  m["fork_public_observation_sha256"]==f["fork_public_observation_sha256"] and
                  m["evaluator_start_x"]==f["evaluator_start_x"],
                  "SEED_PAIR_RESET_NOT_DETERMINISTIC")
            guard(m["source_native_success"] is True,"PUBLIC_CUE_MEMORY_SCRIPT_FAILED")
            receipt["public_source_records"].append(pair)
            receipt["original_episodes_completed"]+=2
            receipt["original_source_steps_completed"]+=sum(z["original_step_calls"] for z in pair)
            groupkey=(m["evaluator_start_x"],m["fork_public_observation_sha256"])
            groups[groupkey].append({"seed":seed,"cue":m["public_cue"],
                                      "must_choose_upper":m["source_success_upper"]})
        guard(receipt["original_episodes_completed"]==256,"SOURCE_EPISODE_BUDGET_DRIFT")
        witness=None
        for (start_x,h),items in sorted(groups.items()):
            for i in items:
                for j in items:
                    if i["seed"]<j["seed"] and i["cue"]!=j["cue"] and (
                        i["must_choose_upper"]!=j["must_choose_upper"]):
                        witness={"same_evaluator_start_x":start_x,
                                 "identical_fork_public_observation_sha256":h,
                                 "seed_a":i["seed"],"seed_b":j["seed"],
                                 "cue_a":i["cue"],"cue_b":j["cue"],
                                 "correct_upper_a":i["must_choose_upper"],
                                 "correct_upper_b":j["must_choose_upper"]}
                        break
                if witness is not None:break
            if witness is not None:break
        guard(witness is not None,"NO_HISTORY_RELEVANT_SAME_OBSERVATION_PAIR")
        receipt["fork_alias_opposite_action_witness"]=witness
        flat=[x for pair in receipt["public_source_records"] for x in pair]
        receipt["scripted_cue_memory_successes"]=sum(z["source_native_success"] for z in flat if z["branch"]=="remember")
        receipt["fixed_upper_successes"]=sum(z["source_native_success"] for z in flat if z["branch"]=="fixed_upper")
        receipt["initial_cue_visible_on_reset"]=sum(m["original_initial_cue_visible"] for m,_ in receipt["public_source_records"])
        receipt["initial_cue_not_visible_on_reset"]=128-receipt["initial_cue_visible_on_reset"]
        receipt["public_fixed_seeds_used"]=list(SEEDS)
        receipt["all_public_source_records_sha256"]=hashlib.sha256(
            json.dumps(receipt["public_source_records"],sort_keys=True,separators=(",",":")).encode()).hexdigest()
        receipt["disposition"]="PUBLIC_CS03_HISTORY_NECESSARY_SOURCE_ALIAS_VERIFIED"
    except Exception as exc:
        receipt["first_failure"]=type(exc).__name__+":"+str(exc)[:650]
    finally:
        (target/"cs03-original-memory-source-receipt.json").write_text(
            json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("CS03_DISPOSITION="+receipt["disposition"],flush=True)
    print("PUBLIC_ORIGINAL_EPISODES="+str(receipt["original_episodes_completed"]),flush=True)
    return 0 if receipt["disposition"]=="PUBLIC_CS03_HISTORY_NECESSARY_SOURCE_ALIAS_VERIFIED" else 2

if __name__=="__main__":
    sys.exit(main())
