"""MR29: prospective source-native FULL-current-input alias causal-memory test.

Train original MR28 innovation and same-data conventional controls on already
CONSUMED original development training seeds. Freeze weights. Independently
execute NEW original source-native public-only trajectories with pre-outcome
forecasts for every actual native action; compare only retrospectively.

Read-only source-world truth is captured by a SEPARATE evaluator accumulator
to validate genuine natural same-observation/pose/action different-world
contrasts; it NEVER enters actor, predictor, state update or training.
Source memory, original learning budget and no protected first use preserved.
"""
from collections import defaultdict
import copy
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import time

import psutil

from research.mr15.public_view_delta import (
    SOURCE_COMMIT,PublicViewLocalDelta,public_raw_view
)
from research.mr18.native_public_learning import Native45,Recurrent45
from research.mr24.natural_history import public_only_action
# Keep this research stream independent of the parallel unmerged MR25B PR.
# Evaluator-only original world truth is never supplied to the learner.
def readonly_evaluator_truth(env,_unused):
    pos=tuple(int(x) for x in env.agent_pos)
    direction=int(env.agent_dir)
    carried=env.carrying
    cargo=None if carried is None else (
        type(carried).__name__,getattr(carried,"color",None))
    grid=env.grid.encode().tobytes()
    return pos,direction,cargo,grid,None
from research.mr27.natural_memory import causal_episode,brier,source_guard
from research.mr28.native_innovation import NativeInnovation45
from research.mr28.probe_original import source_models

PROTOCOL=Path(__file__).with_name("frozen_protocol.json")
NAME=("innovation","same_weights_no_state","recurrent","stateless","count")
STATS=("innovation","same_weights_no_state","recurrent","stateless","count","zero","half")


def prepare_training(factories,seeds):
    m=source_models(True)
    reports=[]
    for name,factory in factories:
        for seed in seeds:
            reports.append(causal_episode(
                factory,name,seed,256,m,training=True))
    snapshots={
        k:m[k].snapshot() for k in
        ("native","recurrent","stateless","public_count")
    }
    return m,snapshots,reports


def episode_models(snapshots,frozen_count):
    m={
        "native":NativeInnovation45.restore(snapshots["native"]),
        "recurrent":Recurrent45.restore(snapshots["recurrent"]),
        "stateless":Native45.restore("public",snapshots["stateless"]),
        "count":copy.deepcopy(frozen_count)
    }
    m["native"].reset_episode()
    m["recurrent"].reset_episode()
    if m["count"].snapshot()!=snapshots["public_count"]:
        raise ValueError("MR29_CONVENTIONAL_COUNT_COLD_COPY_DRIFT")
    return m


def source_episode(factory,family,seed,stream,cap,snapshots,frozen_count):
    env=factory()
    m=episode_models(snapshots,frozen_count)
    rng=random.Random(1000003*seed+337+10007*stream)
    start=time.process_time_ns()
    proc=psutil.Process()
    peak_rss=proc.memory_info().rss
    rows=[]
    losses={k:[] for k in STATS}
    digest=sha256()
    try:
        obs,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(obs["image"])
        for index in range(cap):
            # Current learner sees only PUBLIC raw sampled image, eight
            # actual temporal change bits, and ORIGINAL announced action.
            raw=public_raw_view(obs["image"])
            bits=tuple(sensor.bits)
            before_image=obs["image"].tobytes()
            action=public_only_action(obs,rng)
            if type(action) is not int or not 0<=action<=6:
                raise ValueError("MR29_UNQUALIFIED_SOURCE_ACTOR_ACTION")
            forecast={
                "innovation":m["native"].predict(raw,bits,action),
                "same_weights_no_state":m["native"].predict(
                    raw,bits,action,drop_temporal_state=True),
                "recurrent":m["recurrent"].predict(raw,bits,action),
                "stateless":m["stateless"].predict(raw,bits,action),
                "count":m["count"].predict(raw,bits,action),
                "zero":[0.]*8,"half":[0.5]*8
            }
            # Evaluator-only private source labels are read AFTER action
            # and predictions are frozen, but BEFORE source transition.
            # No evaluator field is used by any action/model above or
            # source postaction state updater below.
            world_eval=readonly_evaluator_truth(env,None)
            history_before=digest.hexdigest()
            next_obs,_reward,done,truncated,_info=env.step(action)
            event=sensor.observe_after_native_step(
                action,next_obs["image"])
            targets=tuple(event["observed_next_local_bits"])
            afterraw=public_raw_view(next_obs["image"])
            expected=tuple(int(
                raw[3*i:3*i+3]!=afterraw[3*i:3*i+3]
            ) for i in range(8))
            if (tuple(event["prior_local_bits"])!=bits or
                event["source_commit"]!=SOURCE_COMMIT or
                event["observed_action"]!=action or
                event["privileged_world_fields_consumed"]!=0 or
                targets!=expected or sensor.steps!=index+1):
                raise ValueError("MR29_ORIGINAL_REAL_SOURCE_PROVENANCE")
            for key in STATS:
                losses[key].append(brier(forecast[key],targets))
            # All chronological source-native postaction observations are
            # delivered only NOW, with learned weights FROZEN.
            m["native"].observe(
                raw,bits,action,list(targets),train=False)
            m["recurrent"].advance_public_history(raw)
            digest.update(bytes([action]))
            digest.update(before_image)
            digest.update(next_obs["image"].tobytes())
            rows.append({
                "family":family,"seed":seed,"stream":stream,"step":index,
                "public":before_image,"priorbits":bits,"action":action,
                "targets":targets,"forecast":forecast,
                "history_before":history_before,
                "pose":world_eval[0],"direction":world_eval[1],
                "carried":world_eval[2],"world":world_eval[3],
            })
            peak_rss=max(peak_rss,proc.memory_info().rss)
            obs=next_obs
            if index==11:
                state=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(state)
                if sensor.snapshot()!=state:
                    raise ValueError("MR29_ORIGINAL_SENSOR_RESTART_DRIFT")
            if done or truncated:
                break
        if not rows:
            raise ValueError("MR29_ZERO_SOURCE_NATIVE_ACTIONS")
        if (m["native"].runtime.core.events!=
            NativeInnovation45.restore(snapshots["native"]).runtime.core.events):
            raise ValueError("MR29_EVALUATION_CHANGED_TRAINED_MODEL_WEIGHTS")
        if (m["recurrent"].local!=
            Recurrent45.restore(snapshots["recurrent"]).local or
            m["recurrent"].shared!=
            Recurrent45.restore(snapshots["recurrent"]).shared):
            raise ValueError("MR29_CONVENTIONAL_EVALUATION_WEIGHTS_CHANGED")
        if (m["stateless"].snapshot()!=snapshots["stateless"] or
            m["count"].snapshot()!=snapshots["public_count"]):
            raise ValueError("MR29_FROZEN_CONVENTIONAL_EVALUATION_MUTATED")
        return rows,{
            "family":family,"seed":seed,"stream":stream,
            "genuine_original_steps":len(rows),
            "genuine_original_source_history_sha256":digest.hexdigest(),
            "per_model_brier":{
                key:sum(vals)/len(vals) for key,vals in losses.items()},
            "single_process_cpu_ns":time.process_time_ns()-start,
            "sampled_single_process_peak_rss_bytes":peak_rss,
            "original_untrained_sensor_sidecar_bytes":32,
            "model_world_privilege":False,
            "native_pose_staging":False
        }
    finally:
        env.close()


def audit_aliases(rows,limit):
    buckets=defaultdict(list)
    for row in rows:
        # Exact bytes and all current prior bits, not hash-only matches.
        buckets[(row["family"],row["seed"],row["public"],
                 row["priorbits"],row["action"])].append(row)
    result={
        "cross_stream_identical_entire_current_input_groups":0,
        "source_alias_pairs_world_pose_inventory_matched":0,
        "strict_natural_full_input_causal_pairs":0,
        "source_pair_checks":0,
        "truncated_pair_groups":0,
        "representative_source_aliases":[],
    }
    pair_scores={k:{"n":0,"loss_sum":0.,"conflict_loss_sum":0.,
                    "signed_margin_sum":0.} for k in STATS}
    for members in buckets.values():
        if len({r["stream"] for r in members})<2:
            continue
        result["cross_stream_identical_entire_current_input_groups"]+=1
        tested=0
        for pos,a in enumerate(members):
            for b in members[pos+1:]:
                if a["stream"]==b["stream"] or (
                    a["history_before"]==b["history_before"]):
                    continue
                if tested>=limit:
                    result["truncated_pair_groups"]+=1
                    break
                tested+=1
                result["source_pair_checks"]+=1
                same_truth=(a["pose"]==b["pose"] and
                            a["direction"]==b["direction"] and
                            a["carried"]==b["carried"])
                distinct_world=a["world"]!=b["world"]
                if same_truth and distinct_world:
                    result["source_alias_pairs_world_pose_inventory_matched"]+=1
                changes=[i for i in range(8)
                         if a["targets"][i]!=b["targets"][i]]
                if not(same_truth and distinct_world and changes):
                    continue
                result["strict_natural_full_input_causal_pairs"]+=1
                for model in STATS:
                    pa=a["forecast"][model]
                    pb=b["forecast"][model]
                    single=pair_scores[model]
                    single["n"]+=1
                    single["loss_sum"]+=0.5*(
                        brier(pa,a["targets"])+brier(pb,b["targets"]))
                    single["conflict_loss_sum"]+=sum(
                        (pa[i]-a["targets"][i])**2+
                        (pb[i]-b["targets"][i])**2
                        for i in changes)/(2*len(changes))
                    single["signed_margin_sum"]+=sum(
                        (pa[i]-pb[i])*(a["targets"][i]-b["targets"][i])
                        for i in changes)/len(changes)
                if len(result["representative_source_aliases"])<12:
                    result["representative_source_aliases"].append({
                        "family":a["family"],"seed":a["seed"],
                        "streams":[a["stream"],b["stream"]],
                        "native_steps":[a["step"],b["step"]],
                        "source_current_public_sha256":
                            sha256(a["public"]).hexdigest(),
                        "source_current_previous_eight_bits":
                            list(a["priorbits"]),
                        "native_action":a["action"],
                        "different_actual_next_public_bits":changes,
                        "genuine_next_source_public_targets":[
                            list(a["targets"]),list(b["targets"])],
                        "same_evaluator_only_true_pose_and_inventory":True,
                        "source_private_world_grids_differ":True,
                        "model_ran_preoutcome":True,
                        "no_evaluator_world_truth_to_model":True,
                    })
            if tested>=limit:
                break
    result["predictor_per_strict_pair"]={
        name:{
            "pairs":v["n"],
            "mean_eightbit_source_brier":(
                v["loss_sum"]/v["n"] if v["n"] else None),
            "mean_conflicting_bit_source_brier":(
                v["conflict_loss_sum"]/v["n"] if v["n"] else None),
            "mean_directional_preoutcome_margin":(
                v["signed_margin_sum"]/v["n"] if v["n"] else None)
        } for name,v in pair_scores.items()
    }
    return result


def main(folder):
    frozen=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (frozen["schema"]!="yggdrasil.mr29.native-natural-full-current-input-contrast.dev.v1" or
        frozen["exact_source_parent"]!="461aa9222cc36c4fb9a3c7f7aae95ed825ff5568" or
        frozen["farama_upstream_sha"]!=SOURCE_COMMIT or
        frozen["native_training_seeds_consumed"]!=
            [263,269,271,277,281,283,293,307] or
        frozen["new_nonprotected_development_evaluation_door_seeds"]!=
            [409,419,421,431,433,439,443,449,457,461,463,467] or
        frozen["new_nonprotected_development_evaluation_empty_seeds"]!=
            [409,419,421,431] or
        frozen["source_eval_policy_stream_ids"]!=[0,1,2,3] or
        frozen["original_native_step_cap"]!=256 or
        frozen["bounded_pair_comparisons_per_input_key"]!=20000 or
        frozen["protected_scientific_first_use"] is not False):
        raise ValueError("MR29_FROZEN_SOURCE_OR_SCIENCE_PROTOCOL_DRIFT")
    source=source_guard(folder)
    sys.path.insert(0,str(source))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    trained,snapshots,train_receipts=prepare_training(
        factories,frozen["native_training_seeds_consumed"])
    # Individual source-native scenarios start at same frozen learned
    # weights, their own independent eight episodic activations.
    source_rows=[]
    receipts=[]
    start=time.process_time_ns()
    for family,factory in factories:
        seeds=(frozen["new_nonprotected_development_evaluation_door_seeds"]
               if family=="DoorKeyEnv(size=8)" else
               frozen["new_nonprotected_development_evaluation_empty_seeds"])
        for seed in seeds:
            for stream in frozen["source_eval_policy_stream_ids"]:
                rows,receipt=source_episode(
                    factory,family,seed,stream,256,snapshots,trained["public_count"])
                source_rows.extend(rows)
                receipts.append(receipt)
    measured=audit_aliases(
        source_rows,frozen["bounded_pair_comparisons_per_input_key"])
    aggregate={}
    for family,_ in factories:
        events=[r for r in receipts if r["family"]==family]
        total=sum(r["genuine_original_steps"] for r in events)
        aggregate[family]={
            "genuine_original_native_actions":total,
            "prequential_original_source_brier":{
                name:sum(r["per_model_brier"][name]*r["genuine_original_steps"]
                         for r in events)/total for name in STATS
            }
        }
    pairs=measured["strict_natural_full_input_causal_pairs"]
    v=measured["predictor_per_strict_pair"]
    criteria={
        "naturally_reached_strict_same_full_input_source_future_contrast":pairs>0,
        "candidate_correct_positive_causal_directional_difference":
            bool(pairs and v["innovation"]["mean_directional_preoutcome_margin"]>0),
        "candidate_conflict_bit_Brier_better_than_state_ablation":
            bool(pairs and v["innovation"]["mean_conflicting_bit_source_brier"]<
                 v["same_weights_no_state"]["mean_conflicting_bit_source_brier"]),
        "candidate_conflict_bit_Brier_better_than_conventional_recurrent":
            bool(pairs and v["innovation"]["mean_conflicting_bit_source_brier"]<
                 v["recurrent"]["mean_conflicting_bit_source_brier"]),
        "door_source_prequential_better_than_recurrent_and_state_ablation":
            aggregate["DoorKeyEnv(size=8)"]["prequential_original_source_brier"]["innovation"]<
            min(aggregate["DoorKeyEnv(size=8)"]["prequential_original_source_brier"]["recurrent"],
                aggregate["DoorKeyEnv(size=8)"]["prequential_original_source_brier"]["same_weights_no_state"]),
        "empty_conventional_recurrent_nonregression":
            aggregate["EmptyEnv(size=8)"]["prequential_original_source_brier"]["innovation"]<=
            aggregate["EmptyEnv(size=8)"]["prequential_original_source_brier"]["recurrent"],
    }
    original_weights={
        "candidate":sum(map(len,trained["native"].runtime.core.genome))+
                    sum(map(len,trained["native"].runtime.core.roles)),
        "recurrent":len(trained["recurrent"].shared)+sum(
                    map(len,trained["recurrent"].local)),
        "stateless":sum(map(len,trained["stateless"].rt.core.genome))+
                    sum(map(len,trained["stateless"].rt.core.roles))
    }
    if (any(x!=45 for x in original_weights.values()) or
        len(trained["native"].state)!=8 or
        len(trained["recurrent"].state)!=8):
        raise ValueError("MR29_SOURCE_NATIVE_MEMORY_BUDGET_DRIFT")
    print("MR29_NATURAL_ORIGINAL_FULL_INPUT_CAUSAL_CONTRAST="+json.dumps({
        "original_upstream_exact_source_commit":SOURCE_COMMIT,
        "frozen_source_protocol":"research/mr29/frozen_protocol.json",
        "original_source_train_episodes":len(train_receipts),
        "source_original_training_steps":sum(r["original_native_steps"]
                                             for r in train_receipts),
        "fresh_development_original_native_episodes":len(receipts),
        "fresh_development_native_steps":len(source_rows),
        "source_development_by_family":aggregate,
        "native_strict_full_input_future_alias_audit":measured,
        "predeclared_acceptance_conditions":criteria,
        "source_native_original_training_model_weight_slots":original_weights,
        "candidate_and_recurrent_eight_episodic_activations":8,
        "original_untrained_MR15_sensor_sidecar_bytes":32,
        "original_public_MR26_training_explorer_fifo_max_entries":128,
        "native_trained_model_checkpoint_bytes":{
            name:len(value.encode()) for name,value in snapshots.items()},
        "frozen_original_count_table_entries":len(trained["public_count"].table),
        "total_eval_model_checkpoints_reinitialized_each_source_stream":True,
        "authentic_full_public_and_prior_eightbits_action_matched_by_exact_bytes":True,
        "private_native_pose_grid_inventory_diagnostic_only_not_model_inputs":True,
        "full_alternative_memory_process_CPU_peak_RSS_communications":"NOT_QUALIFIED",
        "source_process_SHARED_CPU_ns":time.process_time_ns()-start,
        "new_independent_protected_source_first_use":False,
        "genuine_unseen_task_family_transfer":"NOT_TESTED",
        "source_original_G29_index_full_regression":"BLOCKED",
        "Farama_upstream_license_disagreement":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr29.native_causal_alias ORIGINAL_FARAMA_SOURCE")
