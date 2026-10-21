"""MR22: original native MiniGrid self-supervised public-pair invariance gate.

Precommitted source families/actions/seeds; no new protected first-use.
Original Yggdrasil 45 slots; independent same-budget conventional controls.
Pair equality is matched ORIGINAL public 7x7x3 image ONLY; original source
grid/pose checked in evaluator and never passed into learning algorithm.
"""
import copy
import json
import math
import pathlib
import subprocess
import sys
import time

import numpy as np

from research.mr15.public_view_delta import (
    PublicViewLocalDelta,public_raw_view,SOURCE_COMMIT
)
from research.mr18.native_public_learning import Native45,Recurrent45
from research.mr21.reversible_native import inspect_original
from research.mr22.native_pair_consistency import (
    PublicConsistency45,DeltaAgnostic45,one_pair_divergence
)

ROOT=pathlib.Path(__file__).resolve().parents[2]
PROTOCOL=ROOT/"research"/"mr22"/"frozen_protocol.json"


def source_verified(folder):
    root=pathlib.Path(folder).resolve()
    head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                 text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],
                                  text=True).strip()
    if head!=SOURCE_COMMIT or dirty:
        raise ValueError("MR22_UNQUALIFIED_ORIGINAL_SOURCE")
    return root


def mean(items):
    if not items:
        raise ValueError("MR22_EMPTY_NATIVE_MEASUREMENT")
    return sum(items)/len(items)


def brier(prob,truth):
    if len(prob)!=8 or len(truth)!=8 or any(
        type(v) not in (float,int) or not 0<=v<=1 for v in prob):
        raise ValueError("MR22_BAD_SOURCE_PREQUENTIAL_PREDICTION")
    return sum((p-y)**2 for p,y in zip(prob,truth))/8.


def fresh():
    return {
        "self_supervised_45":PublicConsistency45("public"),
        "conventional_full_45":Native45("public"),
        "conventional_delta_agnostic_45":DeltaAgnostic45("public"),
        "conventional_recurrent_45":Recurrent45(),
    }


def real_episode(factory,seed,actions,models,*,train):
    native=factory()
    losses={name:[] for name in (*models,"constant_half","zero_forecast")}
    diversity=[]
    try:
        obs,_=native.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(obs["image"])
        models["conventional_recurrent_45"].reset_episode()
        for step,action in enumerate(actions):
            raw=public_raw_view(obs["image"])
            bits=tuple(sensor.bits)
            if sensor.steps!=step:
                raise ValueError("MR22_NATIVE_PUBLIC_SEQUENCE_MISMATCH")
            pre={
                name:m.predict(raw,bits,action) for name,m in models.items()
            }
            pre["constant_half"]=[0.5]*8
            pre["zero_forecast"]=[0.]*8
            diversity.extend(pre["self_supervised_45"])
            nex,_reward,ended,truncated,_info=native.step(action)
            evidence=sensor.observe_after_native_step(action,nex["image"])
            truth=evidence["observed_next_local_bits"]
            if (evidence["source_commit"]!=SOURCE_COMMIT or
                evidence["observed_action"]!=action or
                evidence["prior_local_bits"]!=list(bits) or
                evidence["privileged_world_fields_consumed"]!=0):
                raise ValueError("MR22_ORIGINAL_ACTION_CONSEQUENCE_DRIFT")
            for name,p in pre.items():
                losses[name].append(brier(p,truth))
            if train:
                for name,m in models.items():
                    m.observe(raw,bits,action,truth)
            else:
                # Weights remain frozen. Only the conventional recurrent
                # CONTROL's public-observation history advances.
                models["conventional_recurrent_45"].advance_public_history(raw)
            if step==9:
                restored=PublicViewLocalDelta.restore(sensor.snapshot())
                if restored.snapshot()!=sensor.snapshot():
                    raise ValueError("MR22_COLD_PUBLIC_SENSOR_DRIFT")
                sensor=restored
            obs=nex
            if ended or truncated:
                break
        return {
            "steps":len(losses["self_supervised_45"]),
            "losses":{name:mean(vals) for name,vals in losses.items()},
            "candidate_prediction_range":max(diversity)-min(diversity),
            "sensor_snapshot_bytes":len(sensor.snapshot().encode()),
        }
    finally:
        native.close()


def matched_original_pair(factory,seed,turns,action,models,*,train):
    # Two actual, independently reset original native processes. We verify
    # source/world identity ONLY in evaluator. The pairing signal made
    # available to the learner is equality of COMPLETE PUBLIC image.
    a,b=factory(),factory()
    try:
        aa,_=a.reset(seed=seed)
        bb,_=b.reset(seed=seed)
        if inspect_original(a)!=inspect_original(b) or not np.array_equal(
            aa["image"],bb["image"]):
            raise ValueError("MR22_ORIGINAL_NATIVE_INITIAL_IDENTITY_DRIFT")
        sa,sb=PublicViewLocalDelta(),PublicViewLocalDelta()
        sa.prime(aa["image"]);sb.prime(bb["image"])
        if a.carrying is not None:
            raise ValueError("MR22_NATIVE_DROP_CONTROL_NOT_EMPTY")
        for _ in range(2):
            aa,_,ended,truncated,_=a.step(int(a.actions.drop))
            sa.observe_after_native_step(int(a.actions.drop),aa["image"])
            if ended or truncated:
                raise ValueError("MR22_NATIVE_REFERENCE_ENDED")
        for x in turns:
            bb,_,ended,truncated,_=b.step(x)
            sb.observe_after_native_step(x,bb["image"])
            if ended or truncated:
                raise ValueError("MR22_NATIVE_CAMERA_ENDED")
        if inspect_original(a)!=inspect_original(b):
            raise ValueError("MR22_ORIGINAL_WORLD_DIFFERENT_AFTER_INVERSE")
        if not np.array_equal(aa["image"],bb["image"]):
            raise ValueError("MR22_PUBLIC_IMAGE_NOT_EQUAL")
        if sa.steps!=sb.steps or sa.steps!=2:
            raise ValueError("MR22_SOURCE_MATCHED_TIME_MISMATCH")

        raw_a=public_raw_view(aa["image"])
        raw_b=public_raw_view(bb["image"])
        if raw_a!=raw_b:
            raise ValueError("MR22_RAW_PUBLIC_SIDECAR_MISMATCH")
        bits_a,bits_b=tuple(sa.bits),tuple(sb.bits)
        differs=sum(x!=y for x,y in zip(bits_a,bits_b))
        # Strictly pre-outcome, both before evaluator consumes future native
        # source outputs. Pair learner receives ONLY public raw and deltas,
        # NO original grid/pose/source identity, no teacher labels.
        before={
            name:one_pair_divergence(m,raw_a,bits_a,bits_b,action)
            for name,m in models.items()
            if name!="conventional_recurrent_45"
        }
        state_before=models["self_supervised_45"].snapshot()
        update=None
        if train and differs:
            update=models["self_supervised_45"].learn_matched_public_pair(
                raw_a,bits_a,bits_b,action)
        after={
            name:one_pair_divergence(m,raw_a,bits_a,bits_b,action)
            for name,m in models.items()
            if name!="conventional_recurrent_45"
        }
        if not train and models["self_supervised_45"].snapshot()!=state_before:
            raise ValueError("MR22_EVAL_TOUCHED_TRAINABLE_STATE")
        # Now and ONLY NOW observe the next original outcomes in both arms.
        nxt_a,_,end_a,cut_a,_=a.step(action)
        nxt_b,_,end_b,cut_b,_=b.step(action)
        va=sa.observe_after_native_step(action,nxt_a["image"])
        vb=sb.observe_after_native_step(action,nxt_b["image"])
        if (inspect_original(a)!=inspect_original(b) or
            not np.array_equal(nxt_a["image"],nxt_b["image"]) or
            va["observed_next_local_bits"]!=vb["observed_next_local_bits"] or
            (end_a,cut_a)!=(end_b,cut_b)):
            raise ValueError("MR22_ORIGINAL_NATIVE_NEXT_OUTCOME_NOT_EQUAL")
        return {
            "source_case_seed":seed,"camera_actions":list(turns),
            "next_native_action":action,
            "different_MR15_history_bits":differs,
            "matched_original_world_public_image_and_next_consequence":True,
            "pair_abs_before":before,"pair_abs_after":after,
            "consistency_update":update,
        }
    finally:
        a.close();b.close()


def main(folder):
    original=source_verified(folder)
    sys.path.insert(0,str(original))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    cfg=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (cfg["schema"]!="yggdrasil.mr22.public-matched-pair-learning.v1" or
        cfg["independently_authored_original_source"]!=SOURCE_COMMIT or
        cfg["parent_yggdrasil_source"]!="9f211429f75d1321fc9476e254a4d38370ae5735" or
        cfg["one_time_original_model_coefficients"]!=45):
        raise ValueError("MR22_FROZEN_PROTOCOL_DRIFT")
    factories=(
        ("Original DoorKeyEnv(size=5)",lambda:DoorKeyEnv(size=5,render_mode=None)),
        ("Original EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None)),
    )
    models=fresh()
    cpu_start=time.process_time_ns()
    trained=[]
    for family,factory in factories:
        for seed in cfg["training_episode_seeds"]:
            x=real_episode(factory,seed,cfg["train_actions"],models,train=True)
            trained.append({"family":family,"seed":seed,**x})
    training_before={n:m.snapshot() for n,m in models.items()}
    pair_training=[]
    for family,factory in factories:
        for seed in cfg["paired_train_seeds"]:
            for inverse in cfg["paired_camera_inverse_actions"]:
                for action in cfg["paired_final_actions"]:
                    pair_training.append({
                        "family":family,**matched_original_pair(
                            factory,seed,inverse,action,models,train=True)})
    frozen={n:m.snapshot() for n,m in models.items()}
    # Restore every native model from a real canonical serialized snapshot,
    # not just reusing the same Python object.
    models["self_supervised_45"]=PublicConsistency45.restore(
        frozen["self_supervised_45"])
    models["conventional_full_45"]=Native45.restore(
        "public",frozen["conventional_full_45"])
    models["conventional_delta_agnostic_45"]=DeltaAgnostic45.restore(
        "public",frozen["conventional_delta_agnostic_45"])
    models["conventional_recurrent_45"]=Recurrent45.restore(
        frozen["conventional_recurrent_45"])
    if any(models[n].snapshot()!=frozen[n] for n in models):
        raise ValueError("MR22_COLD_MODEL_STATE_NOT_RESTORABLE")

    pair_eval=[]
    for family,factory in factories:
        for seed in cfg["paired_dev_eval_seeds"]:
            for inverse in cfg["paired_camera_inverse_actions"]:
                for action in cfg["paired_final_actions"]:
                    pair_eval.append({
                        "family":family,**matched_original_pair(
                            factory,seed,inverse,action,models,train=False)})
    result={}
    for family,factory in factories:
        scores=[]
        for seed in cfg["dev_eval_episode_seeds"]:
            scores.append(real_episode(
                factory,seed,cfg["dev_eval_actions"],models,train=False))
        names=list(scores[0]["losses"])
        result[family]={
            "native_steps":sum(s["steps"] for s in scores),
            "source_prequential_Brier":{
                name:sum(s["steps"]*s["losses"][name]
                         for s in scores)/sum(s["steps"] for s in scores)
                for name in names},
            "candidate_prediction_range":max(
                s["candidate_prediction_range"] for s in scores),
        }
    # Recurrent state is allowed to advance on public dev observations;
    # trainable recurrent coefficients MUST be unchanged.
    for n in ("self_supervised_45","conventional_full_45",
              "conventional_delta_agnostic_45"):
        if models[n].snapshot()!=frozen[n]:
            raise ValueError("MR22_EVAL_UPDATED_FROZEN_MODEL_WEIGHTS")
    rec_before=json.loads(frozen["conventional_recurrent_45"])
    rec_after=json.loads(models["conventional_recurrent_45"].snapshot())
    if (rec_before["local"]!=rec_after["local"] or
        rec_before["shared"]!=rec_after["shared"]):
        raise ValueError("MR22_EVAL_UPDATED_RECURRENT_CONTROL_WEIGHTS")
    for m in models.values():
        if m is models["conventional_recurrent_45"]:
            weights=40+5
        else:
            weights=sum(map(len,m.rt.core.genome))+sum(map(len,m.rt.core.roles))
        if weights!=45:
            raise ValueError("MR22_ALL_CONTROLS_45_WEIGHT_BUDGET")

    def pair_summary(events):
        divergent=[x for x in events if x["different_MR15_history_bits"]]
        def means(where):
            return {
                name:mean([x[where][name] for x in divergent])
                if divergent else 0.
                for name in ("self_supervised_45","conventional_full_45",
                             "conventional_delta_agnostic_45")
            }
        return {
            "source_matched_cases":len(events),
            "history_divergent_cases":len(divergent),
            "before_abs_pair_prediction_discrepancy":means("pair_abs_before"),
            "after_abs_pair_prediction_discrepancy":means("pair_abs_after"),
            "same_true_source_state_next_image_and_source_delta":all(
                x["matched_original_world_public_image_and_next_consequence"]
                for x in events),
        }
    train_pairs=pair_summary(pair_training)
    eval_pairs=pair_summary(pair_eval)
    objectives={
        "evaluation_pair_self_supervised_less_disagreement_than_regular_45":
            eval_pairs["after_abs_pair_prediction_discrepancy"]["self_supervised_45"] <
            eval_pairs["after_abs_pair_prediction_discrepancy"]["conventional_full_45"],
        "evaluation_pair_nuisance_disagreement_lower_than_original_self":
            eval_pairs["after_abs_pair_prediction_discrepancy"]["self_supervised_45"] <
            train_pairs["before_abs_pair_prediction_discrepancy"]["self_supervised_45"],
        "nonconstant_dev_predictions_both_worlds":all(
            result[f]["candidate_prediction_range"]>1e-4 for f,_ in factories),
        "candidate_predictive_brier_better_than_half_and_zero_both_worlds":all(
            result[f]["source_prequential_Brier"]["self_supervised_45"] <
            min(result[f]["source_prequential_Brier"]["constant_half"],
                result[f]["source_prequential_Brier"]["zero_forecast"])
            for f,_ in factories),
        "candidate_not_worse_than_both_trained_controls_both_worlds":all(
            result[f]["source_prequential_Brier"]["self_supervised_45"] <=
            min(result[f]["source_prequential_Brier"]["conventional_full_45"],
                result[f]["source_prequential_Brier"]["conventional_delta_agnostic_45"])
            for f,_ in factories),
    }
    print("MR22_NATIVE_PUBLIC_SELF_SUPERVISED_INVARIANCE="+json.dumps({
        "original_farama_commit":SOURCE_COMMIT,
        "frozen_protocol":"research/mr22/frozen_protocol.json",
        "original_source_native_training_episode_receipts":trained,
        "original_source_training_pair":train_pairs,
        "original_source_development_evaluation_pair":eval_pairs,
        "real_native_development_prequential":result,
        "nontriviality_and_invariance_necessary_conditions":objectives,
        "all_models_exact_trainable_coefficients":45,
        "native_candidate_added_trainable_coefficients":0,
        "original_MR15_untrained_sensor_sidecar_bytes":32,
        "cold_serialization_model_bytes":{n:len(v.encode()) for n,v in frozen.items()},
        "paired_equality_signal":"same original complete publicly visible image and same announced pre-outcome action only",
        "original_grid_pose_carrying_visited_by_evaluator_only":True,
        "no_future_source_labels_given_to_pair_consistency_gradient":True,
        "pair_selection_development_only_not_hidden_source":True,
        "complete_all_in_process_cpu_peak_rss":"NOT_QUALIFIED",
        "parent_only_cpu_ns":time.process_time_ns()-cpu_start,
        "original_upstream_license":"UNRESOLVED",
        "g29_exact_source_full_qualification":"BLOCKED",
        "protected_scientific_first_use":False,
        "genuine_world_grounded_specialist_cognition":"NOT_PROVEN",
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr22.probe_original UPSTREAM")
    main(sys.argv[1])
