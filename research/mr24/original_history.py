"""MR24: real source history training for native 45-weight retained state.

Original MiniGrid world and action steps are unmodified. The diagnostic
evaluator stages all positions. No model reads grid, coordinates, identities,
reward, mission, arm labels or future targets before its prediction.
Retained-state Ygg and recurrent conventional: 45 weights + 8 state values
each. Stateless conventional: 45 weights. DEVELOPMENT ONLY.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from research.mr15.public_view_delta import PublicViewLocalDelta, SOURCE_COMMIT, public_raw_view
from research.mr18.native_public_learning import Native45, Recurrent45
from research.mr19.native_local_predictive_state import NativeLocalPredictiveState
from research.mr23b.hidden_door import original_objects, staging_neighbor

ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/"research"/"mr24"/"frozen_protocol.json"
KEYS=("candidate","recurrent","stateless")
ACTIONS=((3,5,4),(4,4,4))


def verified(root):
    root=Path(root).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if sha!=SOURCE_COMMIT or dirty:
        raise ValueError("MR24_ORIGINAL_SOURCE_DRIFT")
    return root


def fresh():
    return {"candidate":NativeLocalPredictiveState(),
            "recurrent":Recurrent45(),"stateless":Native45("public")}


def clones(weights):
    return {
        "candidate":NativeLocalPredictiveState.restore(weights["candidate"].snapshot()),
        "recurrent":Recurrent45.restore(weights["recurrent"].snapshot()),
        "stateless":Native45.restore("public",weights["stateless"].snapshot())
    }


def brier(pred,targets):
    return sum((p-y)**2 for p,y in zip(pred,targets))/8.


def original_step(env,pose,action,m,train):
    # Fresh public image after EVALUATOR teleport is seen; reset the
    # temporal sensor only, preserving learned episodic memory.
    env.agent_pos=tuple(pose[:2])
    env.agent_dir=pose[2]
    image=env.gen_obs()["image"]
    raw=public_raw_view(image)
    sensor=PublicViewLocalDelta()
    sensor.prime(image)
    bits=tuple(sensor.bits)
    pred={
        "candidate":m["candidate"].predict(raw,bits,action),
        "recurrent":m["recurrent"].predict(raw,bits,action),
        "stateless":m["stateless"].predict(raw,bits,action),
        "state_ablated":m["candidate"].predict(raw,bits,action,drop_temporal_state=True)
    }
    observed,_reward,ended,cut,_info=env.step(action)
    if ended or cut:
        raise ValueError("MR24_NATIVE_SOURCE_STOPPED")
    event=sensor.observe_after_native_step(action,observed["image"])
    targets=event["observed_next_local_bits"]
    if (event["observed_action"]!=action or event["source_commit"]!=SOURCE_COMMIT or
        event["prior_local_bits"]!=[0]*8 or
        event["privileged_world_fields_consumed"]!=0):
        raise ValueError("MR24_NATIVE_SENSOR_IDENTITY_DRIFT")
    # Each model receives identical observed source outcomes AFTER forecast.
    m["candidate"].observe(raw,bits,action,targets,train=train)
    if train:
        m["recurrent"].observe(raw,bits,action,targets)
        m["stateless"].observe(raw,bits,action,targets)
    else:
        m["recurrent"].advance_public_history(raw)
    return {"before":pred,"next":targets,"brier":{
        key:brier(value,targets) for key,value in pred.items()},
        "public_input_hash":hashlib.sha256(bytes(raw)).hexdigest()}


def run_pair(seed,global_weights,*,train,pose,action):
    from minigrid.envs.doorkey import DoorKeyEnv
    a,b=DoorKeyEnv(size=8,render_mode=None),DoorKeyEnv(size=8,render_mode=None)
    try:
        a.reset(seed=seed);b.reset(seed=seed)
        if not np.array_equal(a.grid.encode(),b.grid.encode()):
            raise ValueError("MR24_PAIR_INITIAL_WORLD_DRIFT")
        (dx,dy,door),(kx,ky,key)=original_objects(a)
        poses=(staging_neighbor(a,(kx,ky)),staging_neighbor(a,(dx,dy)),
               staging_neighbor(a,(kx,ky)))
        ms=[];receipts=[]
        for arm,env in enumerate((a,b)):
            m=global_weights if train else clones(global_weights)
            m["candidate"].reset_episode()
            m["recurrent"].reset_episode()
            for p,real_action in zip(poses,ACTIONS[arm]):
                original_step(env,p,real_action,m,train)
            ms.append(m)
        diff=np.any(a.grid.encode()!=b.grid.encode(),axis=2)
        different=[(int(x),int(y)) for x,y in zip(*np.where(diff))]
        if (different!=[(dx,dy)] or a.carrying is not None or
            b.carrying is not None or a.step_count!=3 or b.step_count!=3):
            raise ValueError("MR24_SOURCE_HIDDEN_DOOR_ONLY_CONTRAST_DRIFT")
        a.agent_pos=b.agent_pos=tuple(pose[:2])
        a.agent_dir=b.agent_dir=pose[2]
        same_public=np.array_equal(a.gen_obs()["image"],b.gen_obs()["image"])
        if not train and not same_public:
            raise ValueError("MR24_EVAL_CURRENT_PUBLIC_INPUT_NOT_EQUAL")
        for arm,env in enumerate((a,b)):
            receipts.append(original_step(env,pose,action,ms[arm],train))
        if not train and receipts[0]["public_input_hash"]!=receipts[1]["public_input_hash"]:
            raise ValueError("MR24_EVAL_SOURCE_VISIBLE_INPUT_NOT_EQUAL")
        different_future=sum(u!=v for u,v in zip(receipts[0]["next"],receipts[1]["next"]))
        scores={}
        for name in ("candidate","recurrent","stateless","state_ablated"):
            pa,pb=receipts[0]["before"][name],receipts[1]["before"][name]
            scores[name]={
                "pair_preoutcome_prediction_difference":
                    sum(abs(u-v) for u,v in zip(pa,pb))/8,
                "mean_real_native_two_arm_brier":
                    (receipts[0]["brier"][name]+receipts[1]["brier"][name])/2,
                "per_arm_source_brier":[receipts[0]["brier"][name],receipts[1]["brier"][name]]
            }
        return {"seed":seed,"training":train,
                "agent_pose_staged_not_naturally_navigated":True,
                "equal_original_public_input_at_probe":same_public,
                "only_source_door_tile_different":True,
                "actual_native_steps_per_arm":4,
                "different_real_eight_bit_next_consequences":different_future,
                "source_original_next_targets":[r["next"] for r in receipts],
                "comparators":scores}
    finally:
        a.close();b.close()


def main(path):
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    if (cfg["schema"]!="yggdrasil.mr24.native-occluded-public-history-learning.dev.v1" or
        cfg["parent_exact_yggdrasil_sha"]!="e1c4a90f5695cbd64a217c450808b4f9203bad9c" or
        cfg["original_farama_source_commit"]!=SOURCE_COMMIT or
        cfg["source_training_epochs"]!=3 or cfg["fixed_trainable_slots"]!=45 or
        cfg["evaluation_known_development_seed"]!=11):
        raise ValueError("MR24_FROZEN_PROTOCOL_MISMATCH")
    src=verified(path)
    sys.path.insert(0,str(src))
    m=fresh();training=[]
    start=time.process_time_ns()
    for epoch in range(cfg["source_training_epochs"]):
        for seed in cfg["train_development_seeds"]:
            training.append({"epoch":epoch,**run_pair(
                seed,m,train=True,pose=cfg["known_original_probe_pose"],
                action=cfg["known_original_probe_action"])})
    fixed={name:m[name].snapshot() for name in KEYS}
    restored=clones(m)
    if any(restored[name].snapshot()!=fixed[name] for name in KEYS):
        raise ValueError("MR24_MODEL_PERSISTENCE_FAILED")
    eval_receipt=run_pair(cfg["evaluation_known_development_seed"],restored,
                          train=False,pose=cfg["known_original_probe_pose"],
                          action=cfg["known_original_probe_action"])
    if any(m[name].snapshot()!=fixed[name] for name in KEYS):
        raise ValueError("MR24_EVAL_MUTATED_GLOBAL_WEIGHTS")
    if eval_receipt["different_real_eight_bit_next_consequences"]==0:
        raise ValueError("MR24_EVALUATION_HIDDEN_SOURCE_WITNESS_DISAPPEARED")
    z=eval_receipt["comparators"]
    conditions={
        "native_state_changes_preoutcome_paired_prediction":
            z["candidate"]["pair_preoutcome_prediction_difference"]>1e-8,
        "native_state_beats_same_weights_zero_state":
            z["candidate"]["mean_real_native_two_arm_brier"]<
            z["state_ablated"]["mean_real_native_two_arm_brier"],
        "native_state_beats_equal_data_conventional_recurrent":
            z["candidate"]["mean_real_native_two_arm_brier"]<
            z["recurrent"]["mean_real_native_two_arm_brier"]
    }
    count={
        "candidate":sum(map(len,m["candidate"].runtime.core.genome))+
                    sum(map(len,m["candidate"].runtime.core.roles)),
        "recurrent":sum(map(len,m["recurrent"].local))+len(m["recurrent"].shared),
        "stateless":sum(map(len,m["stateless"].rt.core.genome))+
                    sum(map(len,m["stateless"].rt.core.roles))
    }
    if any(k!=45 for k in count.values()):
        raise ValueError("MR24_NATIVE_FIXED_TRAINABLE_BUDGET_DRIFT")
    print("MR24_ORIGINAL_NATIVE_HIDDEN_HISTORY_LEARNING="+json.dumps({
        "independent_original_source":SOURCE_COMMIT,
        "frozen_development_training_episodes":len(training)*2,
        "training_actual_original_native_steps":len(training)*8,
        "known_previous_mr23b_development_evaluation":eval_receipt,
        "frozen_acceptance_conditions":conditions,
        "all_trainable_coefficient_counts":count,
        "native_and_recurrent_bounded_episodic_state_values":8,
        "persistent_model_checkpoint_bytes":{n:len(v.encode()) for n,v in fixed.items()},
        "original_untrained_sensor_sidecar_bytes":32,
        "parent_process_only_cpu_ns":time.process_time_ns()-start,
        "all_in_parent_child_peak_rss_and_cpu":"NOT_QUALIFIED",
        "original_evaluator_staging_not_natural_navigation":True,
        "no_privileged_world_truth_used_by_models":True,
        "source_origin_license_conflict":"UNRESOLVED",
        "g29_exact_source_full_regression":"BLOCKED",
        "scientific_first_use":False,"independent_transfer":"NOT_TESTED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr24.original_history UPSTREAM")
    main(sys.argv[1])
