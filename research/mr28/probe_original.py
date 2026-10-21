"""MR28 prospectively compares a DIFFERENT fixed-size public-innovation state.

Reuse unchanged MR27 genuine original Farama source-native episode recorder
and MR26 publicly observable bounded exploration. Run MR28 and the original
MR19 competitor on separate independently reset *identical-seed* original
source instances; REQUIRE exact action+public observation event digests to
match for every paired episode. Both train the same conventional 45-weight
recurrent/stateless/count controls from identical source observations.

No world-coordinate access, object labels, teacher rewards, evaluator
teleports, pseudo-outcomes or protected scientific cohorts.
"""
import json
from pathlib import Path
import sys
import time

from research.mr18.native_public_learning import Native45,Recurrent45,PublicCount
from research.mr19.native_local_predictive_state import NativeLocalPredictiveState
from research.mr27.natural_memory import causal_episode,source_guard
from research.mr28.native_innovation import NativeInnovation45

PROTOCOL=Path(__file__).with_name("frozen_protocol.json")
NAMES=("native","native_same_weights_ablated","recurrent","stateless",
       "public_count","constant_zero","constant_half")


def source_models(candidate):
    return {
        "native":NativeInnovation45() if candidate else
                 NativeLocalPredictiveState(),
        "recurrent":Recurrent45(),
        "stateless":Native45("public"),
        "public_count":PublicCount()
    }


def trainable_identity(models):
    native=json.loads(models["native"].snapshot())
    recurrent=json.loads(models["recurrent"].snapshot())
    return {
        "native":native["native_runtime"]["core"],
        "recurrent":[recurrent["local"],recurrent["shared"]],
        "stateless":models["stateless"].snapshot(),
        "count":models["public_count"].snapshot()
    }


def verify_model_resource(model):
    genome=model["native"].runtime.core.genome
    role=model["native"].runtime.core.roles
    recurrent=model["recurrent"]
    conventional=model["stateless"].rt.core
    counts={
        "native":sum(map(len,genome))+sum(map(len,role)),
        "recurrent":sum(map(len,recurrent.local))+len(recurrent.shared),
        "stateless":sum(map(len,conventional.genome))+
                    sum(map(len,conventional.roles)),
    }
    if (any(v!=45 for v in counts.values()) or
        len(model["native"].state)!=8 or
        len(recurrent.state)!=8):
        raise ValueError("MR28_NATIVE_LEARNER_OR_CONTROL_CAPACITY_DRIFT")
    return counts


def aggregate(episodes):
    result={}
    for family in ("DoorKeyEnv(size=8)","EmptyEnv(size=8)"):
        original=[r for r in episodes if r["original_environment"]==family]
        amount=sum(r["original_native_steps"] for r in original)
        if amount<=0:
            raise ValueError("MR28_ZERO_FROZEN_SOURCE_STEPS")
        result[family]={
            "original_source_steps":amount,
            "natural_authentic_visible_pickup_to_unlock_episodes":sum(
                r["natural_complete_visible_causal_experience"]
                for r in original),
            "prequential_Brier":{
                name:sum(
                    r["source_prequential_brier"][name]*
                    r["original_native_steps"] for r in original)/amount
                for name in NAMES},
        }
    return result


def main(upstream):
    protocol=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (protocol["schema"]!="yggdrasil.mr28.predictive-innovation-bounded-state.dev.v1" or
        protocol["original_project_exact_parent"]!="dd545998912e0f7149fb0cbaf44c20c9b81f594c" or
        protocol["source_train_seeds_MR26_consumed_development"]!=
          [263,269,271,277,281,283,293,307] or
        protocol["precommitted_new_nonprotected_dev_eval_seeds"]!=
          [383,389,397,401] or
        protocol["max_source_steps_per_episode"]!=256 or
        protocol["strict_science_first_use"] is not False):
        raise ValueError("MR28_FROZEN_PROTOCOL_OR_SOURCE_IDENTITY_DRIFT")
    original=source_guard(upstream)
    if original.name!="minigrid":
        # Fail-closed against accidental use of another extracted original
        # source root; git custody has already verified exact source SHA.
        raise ValueError("MR28_UPSTREAM_CHECKOUT_ROOT_CHANGED")
    sys.path.insert(0,str(original))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    families=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )

    experimental=source_models(True)
    conventional=source_models(False)
    start=time.process_time_ns()
    trained={"innovation":[],"original_MR19":[]}
    evaluation={"innovation":[],"original_MR19":[]}
    for family,factory in families:
        for seed in protocol["source_train_seeds_MR26_consumed_development"]:
            a=causal_episode(factory,family,seed,256,experimental,training=True)
            b=causal_episode(factory,family,seed,256,conventional,training=True)
            if (a["original_source_event_sha256"]!=b["original_source_event_sha256"] or
                a["original_native_steps"]!=b["original_native_steps"] or
                a["natural_complete_visible_causal_experience"]!=
                b["natural_complete_visible_causal_experience"]):
                raise ValueError("MR28_ORIGINAL_NATIVE_TWIN_EVENT_DRIFT")
            trained["innovation"].append(a)
            trained["original_MR19"].append(b)

    snapshots={
        "innovation":{name:m.snapshot() for name,m in experimental.items()},
        "original_MR19":{name:m.snapshot() for name,m in conventional.items()}
    }
    experimental["native"]=NativeInnovation45.restore(
        snapshots["innovation"]["native"])
    conventional["native"]=NativeLocalPredictiveState.restore(
        snapshots["original_MR19"]["native"])
    for names,models in (("innovation",experimental),
                         ("original_MR19",conventional)):
        models["recurrent"]=Recurrent45.restore(snapshots[names]["recurrent"])
        models["stateless"]=Native45.restore(
            "public",snapshots[names]["stateless"])
        if any(models[n].snapshot()!=snapshots[names][n]
               for n in ("native","recurrent","stateless")):
            raise ValueError("MR28_ORIGINAL_NATIVE_COLD_RESTART_DRIFT")
    original_weights={
        name:trainable_identity(models)
        for name,models in (
            ("innovation",experimental),("original_MR19",conventional))}
    for family,factory in families:
        for seed in protocol["precommitted_new_nonprotected_dev_eval_seeds"]:
            a=causal_episode(factory,family,seed,256,experimental,training=False)
            b=causal_episode(factory,family,seed,256,conventional,training=False)
            if (a["original_source_event_sha256"]!=b["original_source_event_sha256"] or
                a["original_native_steps"]!=b["original_native_steps"] or
                a["natural_complete_visible_causal_experience"]!=
                b["natural_complete_visible_causal_experience"]):
                raise ValueError("MR28_PROSPECTIVE_ORIGINAL_TWIN_SOURCE_MISMATCH")
            evaluation["innovation"].append(a)
            evaluation["original_MR19"].append(b)
    if (trainable_identity(experimental)!=original_weights["innovation"] or
        trainable_identity(conventional)!=original_weights["original_MR19"]):
        raise ValueError("MR28_FROZEN_WEIGHT_EVALUATION_MUTATION")
    if any(experimental[n].snapshot()!=conventional[n].snapshot()
           for n in ("recurrent","stateless","public_count")):
        # Both separately trained against authentic IDENTICAL original
        # source events. This equality is a direct conventional fairness
        # and native result synchronization check.
        raise ValueError("MR28_CONVENTIONAL_CONTROL_TRAINING_OR_STATE_DRIFT")

    train_summary={name:aggregate(rows) for name,rows in trained.items()}
    dev_summary={name:aggregate(rows) for name,rows in evaluation.items()}
    gate={}
    for fam,_ in families:
        cand=dev_summary["innovation"][fam]["prequential_Brier"]
        prev=dev_summary["original_MR19"][fam]["prequential_Brier"]
        gate[fam]={
            "native_innovation_state_better_than_its_exact_weight_ablation":
                cand["native"]<cand["native_same_weights_ablated"],
            "native_innovation_beats_original_retained_state":
                cand["native"]<prev["native"],
            "native_innovation_beats_fully_trained_recurrent":
                cand["native"]<cand["recurrent"],
            "nonconstant_source_predictor_better_than_zero_and_half":
                cand["native"]<min(cand["constant_zero"],cand["constant_half"]),
        }
    train_exposure=train_summary["innovation"]["DoorKeyEnv(size=8)"][
        "natural_authentic_visible_pickup_to_unlock_episodes"]
    dev_exposure=dev_summary["innovation"]["DoorKeyEnv(size=8)"][
        "natural_authentic_visible_pickup_to_unlock_episodes"]
    capacity={
        "innovation":verify_model_resource(experimental),
        "original_MR19":verify_model_resource(conventional)
    }
    print("MR28_NATIVE_ORIGINAL_PREDICTIVE_INNOVATION="+json.dumps({
        "exact_original_farama_sha":protocol["original_farama_source_sha"],
        "frozen_source_protocol_path":"research/mr28/frozen_protocol.json",
        "source_training_seeds":protocol["source_train_seeds_MR26_consumed_development"],
        "new_nonprotected_development_evaluation_seeds":
            protocol["precommitted_new_nonprotected_dev_eval_seeds"],
        "authentic_original_twin_source_training_native_steps":sum(
            r["original_native_steps"] for r in trained["innovation"]),
        "authentic_original_twin_source_eval_native_steps":sum(
            r["original_native_steps"] for r in evaluation["innovation"]),
        "all_original_step_calls_including_two_independent_model_runs":sum(
            r["original_native_steps"] for source in (trained,evaluation)
            for rows in source.values() for r in rows),
        "authentic_natural_train_door_unlock_episodes":train_exposure,
        "authentic_natural_eval_door_unlock_episodes":dev_exposure,
        "source_training":train_summary,
        "frozen_development_evaluation":dev_summary,
        "necessary_learning_conditions":gate,
        "identical_source_action_histories_and_postaction_public_outcomes":True,
        "two_independently_trained_conventional_controls_bit_identical":True,
        "original_45_coefficient_budget_all_parametric_models":capacity,
        "native_and_recurrent_episodic_state_count":8,
        "candidate_snapshot_bytes":{
            name:len(s.encode()) for name,s in snapshots["innovation"].items()},
        "original_MR19_snapshot_bytes":len(
            snapshots["original_MR19"]["native"].encode()),
        "source_untrained_MR15_sensor_sidecar_bytes":32,
        "original_full_public_MR26_explorer_max_cached_hashes":128,
        "source_policy_rng_durable_restart":"NOT_QUALIFIED",
        "shared_process_cpu_ns":time.process_time_ns()-start,
        "all_in_isolated_CPU_peak_RSS_messages_and_equal_total_memory":"NOT_QUALIFIED",
        "predictive_state_formation_is_frozen_online_surrogate_not_BPTT":True,
        "newly_authenticated_full_input_hidden_world_alias":"NOT_TESTED",
        "independent_scientific_first_use":False,
        "farama_original_upstream_licensing":"UNRESOLVED",
        "original_G29_atlas_final_integration":"BLOCKED",
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr28.probe_original ORIGINAL_FARAMA")
    main(sys.argv[1])
