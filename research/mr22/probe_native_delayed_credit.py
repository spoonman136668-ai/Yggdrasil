"""MR22: genuine native source-delayed retention credit vs matched fixed-gate.

Independent protected science is *not* consumed. Training/evaluation source,
actions, seed lists and feature/gate definitions are frozen by MR22 manifest.
The native MiniGrid step belongs solely to original Farama Git checkout.
"""
import copy
import hashlib
import json
import pathlib
import subprocess
import sys
import time

from research.mr15.public_view_delta import (
    SOURCE_COMMIT,PublicViewLocalDelta,public_raw_view
)
from research.mr18.native_public_learning import Recurrent45,PublicCount
from research.mr21.native_learned_retention import LearnedRetention
from research.mr22.delayed_native_credit import DelayedLocalEligibility

CONTRACT=pathlib.Path(__file__).with_name("frozen_protocol.json")
FAMILIES=("DoorKeyEnv(size=5)","EmptyEnv(size=8)")


def verified_contract_and_source(path):
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (contract["schema"]!="yggdrasil.mr22.delayed-credit.frozen-development.v1"
        or contract["original_farama_sha"]!=SOURCE_COMMIT or
        contract["training_seeds"]!=[97,101] or
        contract["eval_seeds"]!=[103,107] or
        len(contract["train_actions"])!=24 or
        len(contract["eval_actions"])!=24 or
        contract["temporary_eligibility_scalars"]!=8):
        raise ValueError("MR22_UNAUTHORIZED_FROZEN_PROTOCOL_CHANGE")
    root=pathlib.Path(path).resolve()
    sha=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if sha!=SOURCE_COMMIT or dirty:
        raise ValueError("MR22_SOURCE_ORIGINAL_CUSTODY_DRIFT")
    return root,contract


def models():
    return {
        "delayed_gate":DelayedLocalEligibility(learn_delayed=True),
        "fixed_gate_same_arch":DelayedLocalEligibility(learn_delayed=False),
        "mr21_immediate_surrogate":LearnedRetention(learn_selection=True),
        "recurrent_45":Recurrent45(),
        "public_count":PublicCount(),
    }


def restored(original):
    return {
        "delayed_gate":DelayedLocalEligibility.restore(
            original["delayed_gate"].snapshot()),
        "fixed_gate_same_arch":DelayedLocalEligibility.restore(
            original["fixed_gate_same_arch"].snapshot()),
        "mr21_immediate_surrogate":LearnedRetention.restore(
            original["mr21_immediate_surrogate"].snapshot()),
        "recurrent_45":Recurrent45.restore(
            original["recurrent_45"].snapshot()),
        "public_count":copy.deepcopy(original["public_count"]),
    }


def score(probs,observed):
    if (len(probs)!=8 or len(observed)!=8 or
        any(type(p) not in (int,float) or not 0<=p<=1 for p in probs)):
        raise ValueError("MR22_INVALID_NATIVE_PREACTION_PROBABILITIES")
    return sum((p-y)**2 for p,y in zip(probs,observed))/8


def sequence(env,models,family,seed,actions,training,receipt):
    try:
        observation,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(observation["image"])
        models["delayed_gate"].reset_episode()
        models["fixed_gate_same_arch"].reset_episode()
        models["mr21_immediate_surrogate"].reset_episode()
        models["recurrent_45"].reset_episode()
        phase="training" if training else "dev_evaluation"
        executed=0
        for idx,action in enumerate(actions):
            raw=public_raw_view(observation["image"])
            bits=tuple(sensor.bits)
            pred={
                "delayed_gate":models["delayed_gate"].predict(
                    raw,bits,action)[0],
                "fixed_gate_same_arch":models["fixed_gate_same_arch"].predict(
                    raw,bits,action)[0],
                "mr21_immediate_surrogate":models[
                    "mr21_immediate_surrogate"].predictions(raw,bits,action)[0],
                "recurrent_45":models["recurrent_45"].predict(
                    raw,bits,action),
                "public_count":models["public_count"].predict(
                    raw,bits,action),
            }
            zero=models["delayed_gate"].predict(raw,bits,action)[1]
            before_elig=list(models["delayed_gate"].eligibilities)
            native_next,_reward,terminated,truncated,_info=env.step(action)
            event=sensor.observe_after_native_step(
                action,native_next["image"])
            if (event["source_commit"]!=SOURCE_COMMIT or
                event["observed_action"]!=action or
                event["prior_local_bits"]!=list(bits)):
                raise ValueError("MR22_NATIVE_ORIGINAL_EVENT_ORDER_DRIFT")
            y=event["observed_next_local_bits"]
            key=(phase,family,seed)
            for name,p in pred.items():
                receipt["losses"].setdefault(key,{}).setdefault(
                    name,[]).append(score(p,y))
            receipt["losses"][key].setdefault(
                "delayed_gate_state_zeroed",[]).append(score(zero,y))
            if idx>0 and any(abs(x)>1e-12 for x in before_elig):
                receipt["delayed_eligibility_present_at_prediction"]+=1
            t=time.process_time_ns()
            p,_,_=models["delayed_gate"].observe_real_native_consequence(
                raw,bits,action,y,training)
            receipt["delayed_model_cpu_ns"]+=time.process_time_ns()-t
            if p!=pred["delayed_gate"]:
                raise ValueError("MR22_PRIOR_PREDICTION_REPLACED_BY_TARGET")
            models["fixed_gate_same_arch"].observe_real_native_consequence(
                raw,bits,action,y,training)
            models["mr21_immediate_surrogate"].step_after_native(
                raw,bits,action,y,training)
            if training:
                models["recurrent_45"].observe(raw,bits,action,y)
                models["public_count"].observe(raw,bits,action,y)
            else:
                models["recurrent_45"].advance_public_history(raw)
            if idx==9:
                s=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(s)
                if sensor.snapshot()!=s:
                    raise ValueError("MR22_SENSOR_SERIALIZATION_DRIFT")
                models=restored(models)
                receipt["serialization_roundtrips"]+=1
            observation=native_next
            executed+=1
            if terminated or truncated:
                break
        receipt["native_steps"][key]=executed
    finally:
        env.close()
    return models


def mean(seq):
    if not seq:
        raise ValueError("MR22_EMPTY_REAL_SOURCE_EVENTS")
    return sum(seq)/len(seq)


def main(upstream):
    source,contract=verified_contract_and_source(upstream)
    sys.path.insert(0,str(source))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factory=(lambda:DoorKeyEnv(size=5,render_mode=None),
             lambda:EmptyEnv(size=8,render_mode=None))
    learned=models()
    result={"losses":{},"native_steps":{},
            "serialization_roundtrips":0,
            "delayed_eligibility_present_at_prediction":0,
            "delayed_model_cpu_ns":0}
    for maker,family in zip(factory,FAMILIES):
        for seed in contract["training_seeds"]:
            learned=sequence(maker(),learned,family,seed,
                contract["train_actions"],True,result)
    snapshots={name:obj.snapshot() for name,obj in learned.items()}
    learned=restored(learned)
    if any(learned[name].snapshot()!=snapshots[name] for name in learned):
        raise ValueError("MR22_TRAINED_STATE_SERIALIZATION_FAILED")
    weights={
        "delayed_gate":learned["delayed_gate"].native.snapshot(),
        "fixed_gate_same_arch":learned["fixed_gate_same_arch"].native.snapshot(),
        "mr21_immediate_surrogate":learned[
            "mr21_immediate_surrogate"].native.snapshot(),
        "recurrent_45":copy.deepcopy(
            (learned["recurrent_45"].local,learned["recurrent_45"].shared)),
        "public_count":learned["public_count"].snapshot(),
    }
    for maker,family in zip(factory,FAMILIES):
        for seed in contract["eval_seeds"]:
            learned=sequence(maker(),learned,family,seed,
                contract["eval_actions"],False,result)
    if (learned["delayed_gate"].native.snapshot()!=weights["delayed_gate"] or
        learned["fixed_gate_same_arch"].native.snapshot()!=weights[
            "fixed_gate_same_arch"] or
        learned["mr21_immediate_surrogate"].native.snapshot()!=weights[
            "mr21_immediate_surrogate"] or
        (learned["recurrent_45"].local,learned["recurrent_45"].shared)!=
            weights["recurrent_45"] or
        learned["public_count"].snapshot()!=weights["public_count"]):
        raise ValueError("MR22_EVAL_OUTCOME_WEIGHT_LEAK")
    score_names=("delayed_gate","fixed_gate_same_arch",
                 "mr21_immediate_surrogate","recurrent_45",
                 "public_count","delayed_gate_state_zeroed")
    evaluation={}
    for family in FAMILIES:
        keys=[("dev_evaluation",family,seed)
              for seed in contract["eval_seeds"]]
        evaluation[family]={
            name:mean([x for key in keys
                       for x in result["losses"][key][name]])
            for name in score_names
        }
    decisions={
        "delayed_beats_same_arch_fixed_gate_both_families":all(
            v["delayed_gate"]<v["fixed_gate_same_arch"]
            for v in evaluation.values()),
        "delayed_beats_mr21_surrogate_both_families":all(
            v["delayed_gate"]<v["mr21_immediate_surrogate"]
            for v in evaluation.values()),
        "delayed_beats_recurrent_both_families":all(
            v["delayed_gate"]<v["recurrent_45"]
            for v in evaluation.values()),
        "delayed_beats_count_both_families":all(
            v["delayed_gate"]<v["public_count"]
            for v in evaluation.values()),
        "memory_necessary_both_families":all(
            v["delayed_gate"]<v["delayed_gate_state_zeroed"]
            for v in evaluation.values())
    }
    trained_bias=[row[2] for row in learned[
        "delayed_gate"].native.core.roles]
    result_receipt={
        "frozen_protocol_sha256":hashlib.sha256(
            CONTRACT.read_bytes()).hexdigest(),
        "source_commit":SOURCE_COMMIT,
        "native_training_seeds":contract["training_seeds"],
        "native_dev_evaluation_seeds":contract["eval_seeds"],
        "native_evaluation_brier_lower_better":evaluation,
        "decision_criteria":decisions,
        "original_trainable_coefficients":45,
        "original_genome_third_pathway_kept_reserved":True,
        "additional_ephemeral_eligibilities":8,
        "camera_relative_retained_activations":8,
        "source_sensor_raw_sidecar_bytes":24,
        "source_sensor_last_delta_bits":8,
        "delayed_eligibility_present_at_prediction":
            result["delayed_eligibility_present_at_prediction"],
        "post_training_gate_biases":trained_bias,
        "original_model_snapshot_bytes":{
            name:len(s.encode()) for name,s in snapshots.items()},
        "native_source_steps":{"/".join(map(str,k)):v
                               for k,v in result["native_steps"].items()},
        "canonical_model_and_sensor_restorations":
            result["serialization_roundtrips"],
        "candidate_model_only_cpu_ns_not_full_process":
            result["delayed_model_cpu_ns"],
        "full_isolated_cpu_peak_rss_and_wire":"NOT_QUALIFIED",
        "count_budget_memory_matched":False,
        "source_hidden_grid_reward_role_labels_consumed":False,
        "source_unseen_first_use":False,
        "world_cell_specialization_proven":False,
        "causal_delayed_gate_credit_is_local_eligibility_approximation":True,
        "atlas_g29_full_regression":"BLOCKED",
        "upstream_license_custody":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    }
    print("MR22_ORIGINAL_NATIVE_DELAYED_ELIGIBILITY="+
          json.dumps(result_receipt,sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr22.probe_native_delayed_credit ORIGINAL")
    main(sys.argv[1])
