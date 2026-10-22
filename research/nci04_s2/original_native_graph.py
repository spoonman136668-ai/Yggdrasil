"""NCI-04 S2 — frozen S1 learned-neighbor necessity on original native source.

No learner modification, no source-private intervention or oracle, no
hyperparameter tuning. Train EXACT S1 once on already-consumed training
histories, freeze original 45 coefficient values, then use genuinely NEW
preregistered original-source DEVELOPMENT seed histories.

Graph counterfactuals change ONLY the source-independent adjacency graph
for the two learned scalar messages each local cell reads; no messages or
weights trained after the graph is changed. Native/orientation-reversed
ring is an algebraic invariant. Role permutation separately tests learned
role positional specificity, NOT a pure graph topology ablation.

All graph variants and the controls see exactly the same executed original
action and public 24-byte sample / prior 8 bits / subsequent original
source visual-change outcome. Message exchange occurs in one local Python
process. Count its 16 float64-equivalent reads/action, not network wire.
We do NOT claim a novel task family or scientific first-use result.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

from research.mr15.public_view_delta import (
    SOURCE_COMMIT, PublicViewLocalDelta, public_raw_view
)
from research.mr26.public_novelty import BoundedPublicNoveltyExplorer
from research.mr27.natural_memory import source_guard
from research.mr18.native_public_learning import Recurrent45, Native45
from research.nci04_s1.local_messages import LocalPredictiveMessages45
from research.nci04_s1.original_native_messages import (
    models_new, native_episode, loss
)

CONTRACT=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.nci04.s2.native-learned-graph-necessity.dev.v1"
EVAL=("ring","reverse_ring","skip_two","skip_three",
      "permuted_graph","roles_permuted","no_messages","no_state",
      "recurrent45","memoryless45","count_unmatched")
GRAPH=("ring","reverse_ring","skip_two","skip_three","permuted_graph")
ROLE_PERM=(0,2,4,6,1,3,5,7)
N=8


class TopologyCounterfactual(LocalPredictiveMessages45):
    """Preserve exact frozen S1 weights while allowing source-blind rewires.

    S1 correctly rejects any changed topology in its own native restore
    contract. The S2 *evaluation-only* adapter restores the S1 native
    weights/state at their ORIGINAL topology, then reapplies the frozen
    counterfactual graph and verifies the entire canonical snapshot.
    It does not weaken the S1 production/native acceptance guard.
    """
    @classmethod
    def restore(cls,payload):
        obj=json.loads(payload)
        if (type(obj) is not dict or "native" not in obj or
            "neighbors" not in obj["native"]):
            raise ValueError("NCI04_S2_NOT_A_NATIVE_S1_SNAPSHOT")
        original=obj["native"]["neighbors"]
        # All graphs are separately checked against their preregistered
        # forms, not arbitrary source-supplied network graphs.
        allowed=[graph(k) for k in (
            "ring","reverse_ring","skip_two","skip_three",
            "permuted_graph")]
        real=tuple(tuple(n) for n in original)
        if real not in allowed:
            raise ValueError("NCI04_S2_UNFROZEN_GRAPH_IN_SNAPSHOT")
        obj["native"]["neighbors"]=graph("ring")
        canonical=json.dumps(obj,sort_keys=True,separators=(",",":"))
        standard=LocalPredictiveMessages45.restore(canonical)
        adapted=cls()
        adapted.runtime=standard.runtime
        adapted.runtime.neighbors=real
        adapted.state=standard.state
        adapted.trace=standard.trace
        if adapted.snapshot()!=payload:
            raise ValueError("NCI04_S2_NATIVE_GRAPH_SNAPSHOT_DRIFT")
        return adapted


def protocol_verified(source):
    p=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (p["schema"]!=SCHEMA or
        p["exact_s1_parent_sha"]!="c8fc71d59d8e08c51e89282be4fc9f6ae0a07e02" or
        p["exact_original_farama_commit"]!=SOURCE_COMMIT or
        p["frozen_training_already_consumed_seeds"]!=[
            263,269,271,277,281,283,293,307] or
        p["fresh_development_only_native_eval_seeds"]!=[
            827,829,839,853,857,859] or
        p["native_source_max_actions_each"]!=256 or
        p["first_use_protected"] is not False or
        p["original_45_trainable_slots"] is not True or
        p["original_8_inference_states"] is not True or
        p["no_postresult_seeds_or_weight_tuning"] is not True):
        raise ValueError("NCI04_S2_FROZEN_SOURCE_OR_ACCEPTANCE_DRIFT")
    return p,source_guard(source)


def graph(name):
    if name=="ring":
        return tuple(((i-1)%N,(i+1)%N) for i in range(N))
    if name=="reverse_ring":
        return tuple(((i+1)%N,(i-1)%N) for i in range(N))
    if name=="skip_two":
        return tuple(((i-2)%N,(i+2)%N) for i in range(N))
    if name=="skip_three":
        return tuple(((i-3)%N,(i+3)%N) for i in range(N))
    if name=="permuted_graph":
        order=ROLE_PERM
        return tuple((order[(order.index(i)-1)%N],
                      order[(order.index(i)+1)%N]) for i in range(N))
    raise ValueError("NCI04_S2_UNAUTHORIZED_GRAPH")


def counterfactual_models(frozen):
    graph_models={}
    for name in GRAPH:
        m=TopologyCounterfactual.restore(frozen)
        m.runtime.neighbors=graph(name)
        # Round-trip proves all original 45 weights and the eight
        # states are still valid under the altered exact graph.
        if TopologyCounterfactual.restore(m.snapshot()).snapshot()!=m.snapshot():
            raise ValueError("NCI04_S2_GRAPH_RESTORE_NOT_CANONICAL")
        graph_models[name]=m
    m=TopologyCounterfactual.restore(frozen)
    roles=[r[:] for r in m.runtime.core.roles]
    m.runtime.core.roles=[roles[i][:] for i in ROLE_PERM]
    graph_models["roles_permuted"]=m
    return graph_models


def single_episode(factory,family,seed,graph_models,baseline_frozen,receipt):
    env=factory()
    actor=BoundedPublicNoveltyExplorer(seed)
    sensor=PublicViewLocalDelta()
    # Models are separate deployed counterfactuals only in the EVALUATOR.
    # The actual input stream and action never depend on their forecasts.
    for model in graph_models.values():
        model.reset_episode()
    recur=Recurrent45.restore(baseline_frozen["recurrent"])
    recur.reset_episode()
    memoryless=Native45.restore("public",baseline_frozen["memoryless"])
    count=baseline_frozen["count"]
    costs={name:0. for name in EVAL}
    rings=[]
    windows=[]
    actual_digest=sha256()
    graph_prediction_cpu=0
    graph_state_update_cpu=0
    steps=0
    try:
        obs,_=env.reset(seed=seed)
        sensor.prime(obs["image"])
        for tick in range(256):
            raw=public_raw_view(obs["image"])
            bits=tuple(sensor.bits)
            action=actor.choose(obs["image"])
            start=time.process_time_ns()
            predictions={name:m.predict(raw,bits,action)
                         for name,m in graph_models.items()}
            ring=graph_models["ring"]
            predictions["no_messages"]=ring.predict(
                raw,bits,action,drop_neighbors=True)
            predictions["no_state"]=ring.predict(
                raw,bits,action,drop_state=True)
            graph_prediction_cpu+=time.process_time_ns()-start
            predictions["recurrent45"]=recur.predict(raw,bits,action)
            predictions["memoryless45"]=memoryless.predict(raw,bits,action)
            predictions["count_unmatched"]=count.predict(raw,bits,action)
            if predictions["ring"]!=predictions["reverse_ring"]:
                raise ValueError("NCI04_S2_ORIGINAL_RING_ORIENTATION_INVARIANCE_FAIL")
            original_pre=obs["image"].tobytes()
            later,_ignored_reward,done,truncated,_info=env.step(action)
            event=sensor.observe_after_native_step(action,later["image"])
            next_raw=public_raw_view(later["image"])
            target=event["observed_next_local_bits"]
            if (event["source_commit"]!=SOURCE_COMMIT or
                event["observed_action"]!=action or
                event["prior_local_bits"]!=list(bits) or
                target!=[int(raw[3*i:3*i+3]!=next_raw[3*i:3*i+3])
                        for i in range(N)]):
                raise ValueError("NCI04_S2_ORIGINAL_PUBLIC_TARGET_DRIFT")
            for name in EVAL:
                costs[name]+=loss(predictions[name],target)
            rings.append(loss(predictions["ring"],target))
            windows.append({
                "ring":loss(predictions["ring"],target),
                "skip_two":loss(predictions["skip_two"],target),
                "skip_three":loss(predictions["skip_three"],target),
                "permuted_graph":loss(predictions["permuted_graph"],target),
                "no_messages":loss(predictions["no_messages"],target),
            })
            start=time.process_time_ns()
            for name,m in graph_models.items():
                returned=m.observe(raw,bits,action,target,train=False)
                if returned!=predictions[name]:
                    raise ValueError("NCI04_S2_POSTACTION_FORECAST_LEAK_"+name)
            graph_state_update_cpu+=time.process_time_ns()-start
            recur.advance_public_history(raw)
            actor.observe_original_next_public_image(action,later["image"])
            actor.validate()
            actual_digest.update(bytes((action,*bits,*target)))
            actual_digest.update(sha256(original_pre).digest())
            actual_digest.update(sha256(later["image"].tobytes()).digest())
            if tick==11:
                s=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(s)
                if sensor.snapshot()!=s:
                    raise ValueError("NCI04_S2_NATIVE_SENSOR_RESTART_DRIFT")
                for name,m in list(graph_models.items()):
                    state=m.snapshot()
                    graph_models[name]=TopologyCounterfactual.restore(state)
                    if graph_models[name].snapshot()!=state:
                        raise ValueError("NCI04_S2_NATIVE_GRAPH_COLD_RESTART_FAIL")
                receipt["native_graph_restart_checks"]+=len(graph_models)
            obs=later
            steps+=1
            if done or truncated:
                break
        if not steps:
            raise ValueError("NCI04_S2_ZERO_NATIVE_SOURCE_ACTIONS")
        return {
            "family":family,"seed":seed,"original_native_actions":steps,
            "original_native_action_public_source_sha256":actual_digest.hexdigest(),
            "preaction_brier":{name:costs[name]/steps for name in EVAL},
            "same_message_cost_per_graph_native_step_64bit_scalar_reads":16,
            "total_graph_comparison_preaction_CPU_ns_same_process":
                graph_prediction_cpu,
            "total_graph_comparison_public_state_update_CPU_ns_same_process":
                graph_state_update_cpu,
            "absolute_native_original_sequential_interventions_per_graph":0,
            "original_source_world_pose_reward_mission_labels_to_learner":False
        }
    finally:
        env.close()


def main(source):
    p,source=protocol_verified(source)
    sys.path.insert(0,str(source))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    original=models_new()
    training_receipts=[]
    training_report={"native_restart_checks":0}
    for family,make in factories:
        for seed in p["frozen_training_already_consumed_seeds"]:
            training_receipts.append(native_episode(
                make,family,seed,True,original,training_report))
    # Authentic S1 weights frozen ONCE. No graph retraining.
    learned_frozen=original["s1_messages"].snapshot()
    role_frozen=original["s1_messages"].local_roles()
    controls={
        "recurrent":original["conventional_recurrent"].snapshot(),
        "memoryless":original["conventional_memoryless"].snapshot(),
        "count":original["public_count_unmatched"]
    }
    # Must be no evaluator-induced model update after freeze.
    control_snapshot=controls["count"].snapshot()
    frozen_core=original["s1_messages"].runtime.core.snapshot()
    receipts=[]
    audit={"native_graph_restart_checks":0}
    start=time.process_time_ns()
    for family,make in factories:
        for seed in p["fresh_development_only_native_eval_seeds"]:
            graphs=counterfactual_models(learned_frozen)
            receipts.append(single_episode(
                make,family,seed,graphs,controls,audit))
            for model in graphs.values():
                if model.runtime.core.snapshot()!=frozen_core and (
                    model is not graphs.get("roles_permuted")):
                    raise ValueError("NCI04_S2_FROZEN_NATIVE_GENOME_ROLE_WEIGHT_DRIFT")
    if (original["s1_messages"].snapshot()!=learned_frozen or
        original["conventional_recurrent"].snapshot()!=controls["recurrent"] or
        original["conventional_memoryless"].snapshot()!=controls["memoryless"] or
        controls["count"].snapshot()!=control_snapshot):
        raise ValueError("NCI04_S2_ORIGINAL_TRAINED_WEIGHT_CUSTODY_DRIFT")
    source_by_family={}
    criterion={}
    margin=0.0001
    for family,_ in factories:
        selected=[r for r in receipts if r["family"]==family]
        native_steps=sum(r["original_native_actions"] for r in selected)
        scored={name:sum(r["preaction_brier"][name]*
                         r["original_native_actions"] for r in selected)/
                native_steps for name in EVAL}
        by_seed={
            other:sum(
                r["preaction_brier"]["ring"]<
                r["preaction_brier"][other]
                for r in selected) for other in
            ("skip_two","skip_three","permuted_graph")
        }
        source_by_family[family]={
            "original_native_steps":native_steps,
            "native_episode_count":len(selected),
            "frozen_original_source_preaction_brier":scored,
            "native_seed_clusters_where_original_ring_beats_rewire":by_seed
        }
        criterion[family]={
            "ring_advantage_at_least_0_0001_over_ALL_rewires_and_off":
                all(scored["ring"]+margin<scored[k] for k in (
                    "skip_two","skip_three","permuted_graph","no_messages")),
            "ring_better_than_same_weights_all_state_erased":
                scored["ring"]<scored["no_state"],
            "ring_better_than_fully_trained_45_recurrent_and_memoryless":
                scored["ring"]<min(scored["recurrent45"],scored["memoryless45"]),
            "ring_better_than_permuted_learned_roles":
                scored["ring"]+margin<scored["roles_permuted"],
            "original_ring_better_in_at_least_4_of_6_native_seeds_each_rewire":
                all(x>=4 for x in by_seed.values()),
            "original_ring_orientation_reversal_identical":
                scored["ring"]==scored["reverse_ring"],
        }
    conditions={
        "all_per_original_world_conditions_satisfied":
            all(all(x.values()) for x in criterion.values()),
        "full_isolated_equal_total_training_inference_and_wire_cost":False,
        "native_s1_original_ring_is_preassigned_not_emerged":True,
        "independently_authenticated_unfamiliar_original_source_family":False,
        "damage_recovery_tested":False
    }
    print("NCI04_S2_NATIVE_LEARNED_TOPOLOGY_NECESSITY="+json.dumps({
        "original_source_commit":SOURCE_COMMIT,
        "frozen_development_protocol_sha256":sha256(CONTRACT.read_bytes()).hexdigest(),
        "original_s1_training_native_episodes":len(training_receipts),
        "new_development_original_native_episodes":receipts,
        "source_original_native_family_results":source_by_family,
        "predeclared_topology_criteria_per_family":criterion,
        "necessary_scientific_conditions":conditions,
        "canonical_s1_frozen_original_checkpoint_bytes":
            len(learned_frozen.encode()),
        "original_s1_learned_camera_slot_role_coefficients":role_frozen,
        "original_core_trainable_coefficient_budget":45,
        "original_inference_native_cell_state_scalars":8,
        "source_MR15_untrained_public_sidecar_bytes":32,
        "per_graph_original_native_source_action_neighbor_scalar_reads":16,
        "per_graph_original_native_source_action_payload_float64_bytes":128,
        "native_graph_cold_restart_checks":audit["native_graph_restart_checks"],
        "native_source_and_all_graphs_CPU_ns_one_shared_process_diagnostic":
            time.process_time_ns()-start,
        "extra_parallel_model_copies_for_counterfactual_evaluator_only":True,
        "actual_network_wire_and_full_isolated_cpu_peak_rss":"NOT_QUALIFIED",
        "one_action_training_credit_64float_trace_extra_memory":True,
        "source_privileged_world_grid_pose_reward_goal_to_actor_or_model":False,
        "protected_scientific_first_use":False,
        "complete_original_G29_semantic_atlas":"BLOCKED",
        "external_upstream_license_disagreement":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.nci04_s2.original_native_graph ORIGINAL_FARAMA")
    main(sys.argv[1])
