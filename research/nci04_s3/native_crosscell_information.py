"""S3: source-native conditional predictive information shared between cells.

THIS IS AN INFORMATION DIAGNOSTIC, NOT A NEW LEARNED CELL NETWORK.
All estimators train on PREVIOUS already consumed source development
episodes and freeze complete count tables on new preregistered
development-only episodes. The label is only the next eight public
MR15 changed bits returned by original Farama env.step.

Per-receiver and per-action smoothed context counts use exactly the same
128 FIFO SHA256 lookup entries and two uint32-bounded tally slots per
entry. Exact receiver-own current raw public tile triplet, previous
observed local change bit, and native announced action condition each
local predictor. Additional donors are camera-relative neighboring
public tile triplets and prior delta bits; another treatment uses
different indexed public tiles at precisely the SAME memory capacity.
A full current-public-image conditioned count is a broader,
non-camera-corrected control. This is not conditional mutual information
in a general information-theoretic sense and is NOT a trained neural
representation, native 45-weight memory, or a source-hidden causal oracle.

The unconditional source actor sees only the original PUBLIC 7x7x3
frame, and observations/outcomes enter any training count ONLY AFTER
that original native action. No original world/private labels, stage,
mission, reward, hidden object truth or goal is used.
"""
from collections import OrderedDict
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import time

from research.mr15.public_view_delta import (
    SOURCE_COMMIT,PublicViewLocalDelta,public_raw_view
)
from research.mr26.public_novelty import BoundedPublicNoveltyExplorer
from research.mr27.natural_memory import source_guard

PROTOCOL=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.nci04.s3.original-public-crosscell-conditional-info.dev.v1"
MODES=("global","own","ring","skip_three","permuted","whole_public")
LOCAL_MODES=("own","ring","skip_three","permuted","whole_public")
WORLD=("DoorKeyEnv(size=8)","EmptyEnv(size=8)")
ORDER=(0,2,4,6,1,3,5,7)
CAP=128
SMOOTH=4
N=8
ACTIONS=6


def protocol(source):
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (p["schema"]!=SCHEMA or
        p["source_parent_s2"]!="def4e3a9d803c80631c00b7e138a5c54cda349e9" or
        p["original_independent_farama_git"]!=SOURCE_COMMIT or
        p["prior_consumed_development_train_seeds"]!=[
            263,269,271,277,281,283,293,307] or
        p["prospective_only_development_eval_seeds"]!=[
            877,881,883,887,907,911] or
        p["max_uninterrupted_original_native_actions_each"]!=256 or
        p["source_private_world_never_input"] is not True or
        p["no_new_Ygg_45_weight_learner_training"] is not True or
        p["no_new_scientific_first_use"] is not True or
        p["no_postresult_expansion_or_tuning"] is not True):
        raise ValueError("NCI04_S3_FROZEN_SOURCE_PROTOCOL_CHANGED")
    return p,source_guard(source)


def donor_pair(mode,i):
    if mode=="ring":
        return ((i-1)%N,(i+1)%N)
    if mode=="skip_three":
        return ((i-3)%N,(i+3)%N)
    if mode=="permuted":
        k=ORDER.index(i)
        return (ORDER[(k-1)%N],ORDER[(k+1)%N])
    raise ValueError("NCI04_S3_UNFROZEN_DONOR_CONTEXT")


class MatchedContextCounts:
    """Eight receiving cells, each with identical 128x32-byte-key FIFO.

    Lookup digest identity is SHA256. Although collision-resistant,
    digest equality is NOT literal equality of the public context.
    Counts store no original private world information. Experimental
    count-memory is much larger than the original 45 native coefficients.
    """
    def __init__(self,mode):
        if mode not in LOCAL_MODES:
            raise ValueError("NCI04_S3_UNKNOWN_CONTEXT")
        self.mode=mode
        self.cache=[OrderedDict() for _ in range(N)]
        self.global_n=[[0]*ACTIONS for _ in range(N)]
        self.global_yes=[[0]*ACTIONS for _ in range(N)]

    def key(self,raw,bits,action,full_image,i):
        first=bytes((i,action,bits[i]))+bytes(raw[3*i:3*i+3])
        if self.mode in ("ring","skip_three","permuted"):
            a,b=donor_pair(self.mode,i)
            first+=bytes((
                bits[a],bits[b],
            ))+bytes(raw[3*a:3*a+3])+bytes(raw[3*b:3*b+3])
        elif self.mode=="whole_public":
            first+=full_image
        return sha256(first).digest()

    def predict(self,raw,bits,action,frame):
        if (len(raw)!=24 or len(bits)!=N or
            type(action) is not int or not 0<=action<ACTIONS or
            type(frame) is not bytes or len(frame)!=147):
            raise ValueError("NCI04_S3_INVALID_ORIGINAL_PUBLIC_FEATURES")
        pp=[]
        for i in range(N):
            prior=(self.global_yes[i][action]+1)/(
                self.global_n[i][action]+2)
            key=self.key(raw,bits,action,frame,i)
            n,yes=self.cache[i].get(key,(0,0))
            pp.append((yes+SMOOTH*prior)/(n+SMOOTH))
        return pp

    def observe(self,raw,bits,action,frame,target):
        if len(target)!=N or any(y not in (0,1) for y in target):
            raise ValueError("NCI04_S3_INVALID_PUBLIC_OUTCOME")
        for i in range(N):
            key=self.key(raw,bits,action,frame,i)
            group=self.cache[i]
            if key not in group:
                if len(group)==CAP:
                    group.popitem(last=False)
                group[key]=(0,0)
            n,yes=group[key]
            if n>=2**32-1 or self.global_n[i][action]>=2**32-1:
                raise ValueError("NCI04_S3_COUNT_UINT32_EXHAUSTED")
            group[key]=(n+1,yes+target[i])
            self.global_n[i][action]+=1
            self.global_yes[i][action]+=target[i]
        self.validate()

    def validate(self):
        if (len(self.cache)!=N or any(len(g)>CAP for g in self.cache)
            or any(
                type(k) is not bytes or len(k)!=32 or
                type(v) is not tuple or len(v)!=2 or
                not 0<=v[1]<=v[0]<2**32
                for group in self.cache for k,v in group.items())):
            raise ValueError("NCI04_S3_EXCESS_CONTEXT_MEMORY")
        for row in range(N):
            if any(
                not 0<=self.global_yes[row][a]<=self.global_n[row][a]<2**32
                for a in range(ACTIONS)):
                raise ValueError("NCI04_S3_INVALID_GLOBAL_COUNTS")

    def snapshot(self):
        self.validate()
        return json.dumps({
            "mode":self.mode,
            "global_n":self.global_n,
            "global_yes":self.global_yes,
            "per_cell_fifo":[
                [[k.hex(),n,yes] for k,(n,yes) in group.items()]
                for group in self.cache]
        },separators=(",",":"),sort_keys=True)

    def capacity(self):
        return {
            "same_per_cell_fifo_entries":CAP,
            "context_digest_bytes":32,
            "two_uint32_tally_bytes_per_entry":8,
            "total_fixed_context_payload_and_global_counter_bytes":
                N*CAP*(32+8)+N*ACTIONS*2*4,
            "actual_used_fifo_entries":sum(len(g) for g in self.cache),
            "canonical_snapshot_bytes":len(self.snapshot().encode())
        }


def preaction_global(own,action):
    return [(own.global_yes[i][action]+1)/
            (own.global_n[i][action]+2) for i in range(N)]


def brier(pp,y):
    return sum((p-v)**2 for p,v in zip(pp,y))/N


def logloss(pp,y):
    return -sum(yv*math.log(max(1e-12,min(1-1e-12,p)))+
                (1-yv)*math.log(max(1e-12,min(1-1e-12,1-p)))
                for p,yv in zip(pp,y))/N


def native_episode(ctor,family,seed,models,train):
    actor=BoundedPublicNoveltyExplorer(seed)
    sensor=PublicViewLocalDelta()
    env=ctor()
    trace=sha256()
    score={mode:{"brier_sum":0.,"log_sum":0.}
           for mode in MODES}
    stationary={mode:{"loss":0.,"labels_yes":0,"bits":0}
                for mode in MODES}
    steps=0
    positives=0
    try:
        obs,_=env.reset(seed=seed)
        sensor.prime(obs["image"])
        for idx in range(256):
            raw=public_raw_view(obs["image"])
            bits=tuple(sensor.bits)
            frame=obs["image"].tobytes()
            action=actor.choose(obs["image"])
            predictions={
                name:models[name].predict(raw,bits,action,frame)
                for name in LOCAL_MODES
            }
            predictions["global"]=preaction_global(models["own"],action)
            nxt,_ignored_reward,done,truncated,_info=env.step(action)
            event=sensor.observe_after_native_step(action,nxt["image"])
            target=event["observed_next_local_bits"]
            next_raw=public_raw_view(nxt["image"])
            if (event["source_commit"]!=SOURCE_COMMIT or
                event["observed_action"]!=action or
                event["prior_local_bits"]!=list(bits) or
                target!=[int(
                    raw[3*i:3*i+3]!=next_raw[3*i:3*i+3])
                    for i in range(N)] or
                sensor.steps!=idx+1):
                raise ValueError("NCI04_S3_ORIGINAL_NATIVE_SOURCE_TARGET_INVALID")
            for name in MODES:
                pp=predictions[name]
                if len(pp)!=N or any(not 0<p<1 for p in pp):
                    raise ValueError("NCI04_S3_INVALID_PREACTION_PROBABILITIES")
                if not train:
                    score[name]["brier_sum"]+=brier(pp,target)
                    score[name]["log_sum"]+=logloss(pp,target)
                    if action>=3:
                        stationary[name]["loss"]+=brier(pp,target)
                        stationary[name]["labels_yes"]+=sum(target)
                        stationary[name]["bits"]+=N
            if train:
                for name in LOCAL_MODES:
                    models[name].observe(raw,bits,action,frame,target)
            trace.update(bytes((action,*bits,*target)))
            trace.update(sha256(frame).digest())
            trace.update(sha256(nxt["image"].tobytes()).digest())
            actor.observe_original_next_public_image(action,nxt["image"])
            actor.validate()
            steps+=1
            positives+=sum(target)
            if idx==11:
                sensor_snapshot=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(sensor_snapshot)
                if sensor.snapshot()!=sensor_snapshot:
                    raise ValueError("NCI04_S3_ORIGINAL_SENSOR_RESTART_DRIFT")
            obs=nxt
            if done or truncated:
                break
        if not steps:
            raise ValueError("NCI04_S3_EMPTY_NATIVE_EPISODE")
        return {
            "family":family,"seed":seed,
            "phase":"train_consumed_dev" if train else "prospective_dev_eval",
            "source_native_actions":steps,
            "authentic_original_public_action_history_sha256":trace.hexdigest(),
            "positive_eight_local_change_bit_outcomes":positives,
            "prequential_brier_by_model":{
                name:score[name]["brier_sum"]/steps for name in MODES}
            if not train else None,
            "prequential_logloss_by_model":{
                name:score[name]["log_sum"]/steps for name in MODES}
            if not train else None,
            "native_stationary_intervention_brier_by_model":{
                name:(stationary[name]["loss"]/
                      (stationary[name]["bits"]/N))
                if stationary[name]["bits"] else None
                for name in MODES} if not train else None,
            "native_stationary_intervention_positive_bit_outcomes":
                stationary["own"]["labels_yes"] if not train else None,
            "native_stationary_intervention_original_actions":
                stationary["own"]["bits"]//N if not train else None,
            "original_world_grid_pose_hidden_labels_consumed":False
        }
    finally:
        env.close()


def main(source):
    p,root=protocol(source)
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    reports={}
    receipts=[]
    t0=time.process_time_ns()
    for family,ctor in factories:
        models={name:MatchedContextCounts(name) for name in LOCAL_MODES}
        train=[]
        for seed in p["prior_consumed_development_train_seeds"]:
            outcome=native_episode(ctor,family,seed,models,True)
            receipts.append(outcome)
            train.append(outcome)
        frozen={name:models[name].snapshot() for name in LOCAL_MODES}
        evals=[]
        for seed in p["prospective_only_development_eval_seeds"]:
            outcome=native_episode(ctor,family,seed,models,False)
            receipts.append(outcome)
            evals.append(outcome)
        if any(models[name].snapshot()!=frozen[name]
               for name in LOCAL_MODES):
            raise ValueError("NCI04_S3_FROZEN_COUNT_TABLE_EVAL_LEAK")
        n=sum(r["source_native_actions"] for r in evals)
        means={
            name:sum(r["source_native_actions"]*
                     r["prequential_brier_by_model"][name]
                     for r in evals)/n for name in MODES
        }
        logmeans={
            name:sum(r["source_native_actions"]*
                     r["prequential_logloss_by_model"][name]
                     for r in evals)/n for name in MODES
        }
        stationary_n=sum(r[
            "native_stationary_intervention_original_actions"] for r in evals)
        stationary_loss={
            name:(sum(
                r["native_stationary_intervention_original_actions"]*
                r["native_stationary_intervention_brier_by_model"][name]
                for r in evals if r[
                    "native_stationary_intervention_original_actions"])/stationary_n)
            if stationary_n else None
            for name in MODES
        }
        reports[family]={
            "native_original_train_steps":sum(
                r["source_native_actions"] for r in train),
            "new_source_development_eval_steps":n,
            "new_eval_seed_clusters":len(evals),
            "proper_brier_lower_better":means,
            "proper_logloss_lower_better":logmeans,
            "stationary_native_actions":stationary_n,
            "stationary_positive_local_change_bits":sum(
                r["native_stationary_intervention_positive_bit_outcomes"]
                for r in evals),
            "stationary_proper_brier":stationary_loss,
            "independent_original_seed_sign_counts":{
                "ring_brier_better_than_own":sum(
                    r["prequential_brier_by_model"]["ring"]<
                    r["prequential_brier_by_model"]["own"] for r in evals),
                "ring_brier_better_than_skip_three":sum(
                    r["prequential_brier_by_model"]["ring"]<
                    r["prequential_brier_by_model"]["skip_three"]
                    for r in evals),
                "ring_brier_better_than_permuted":sum(
                    r["prequential_brier_by_model"]["ring"]<
                    r["prequential_brier_by_model"]["permuted"]
                    for r in evals)
            },
            "public_context_capacity_per_model":{
                name:models[name].capacity() for name in LOCAL_MODES},
            "training_count_models_frozen_identically_before_eval":True
        }
    criteria={}
    for family in WORLD:
        z=reports[family]
        means=z["proper_brier_lower_better"]
        ss=z["stationary_proper_brier"]
        criteria[family]={
            "ring_better_than_own_by_at_least_0_001":
                means["ring"]+0.001<=means["own"],
            "ring_better_than_equal_capacity_wrong_donors_by_0_001":
                means["ring"]+0.001<=min(
                    means["skip_three"],means["permuted"]),
            "ring_better_than_own_on_four_of_six_independent_development_seeds":
                z["independent_original_seed_sign_counts"][
                    "ring_brier_better_than_own"]>=4,
            "sufficient_stationary_positive_original_labels":
                z["stationary_positive_local_change_bits"]>=16,
            "ring_better_stationary_than_own":
                ss["ring"] is not None and ss["ring"]<ss["own"],
            "fixed_equal_128_entry_per_cell_count_state_capacity":
                len({x["total_fixed_context_payload_and_global_counter_bytes"]
                     for x in z["public_context_capacity_per_model"].values()})==1,
        }
    final_go=all(all(x.values()) for x in criteria.values())
    print("NCI04_S3_NATIVE_PUBLIC_CROSSCELL_INFO="+json.dumps({
        "original_independently_authored_farama_source_sha":SOURCE_COMMIT,
        "frozen_protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "authentic_native_source_episode_receipts":receipts,
        "cross_cell_information_prospective_dev":reports,
        "precommitted_conditions_by_source_class":criteria,
        "all_development_preconditions_passed":final_go,
        "separate_native_original_45_coefficient_model_trained":False,
        "S3_bounded_count_tables_larger_than_native_45_coefficients":True,
        "source_actor_128_public_frame_FIFO_cost_not_model_matched":True,
        "original_existing_MR15_sensor_24_raw_bytes_and_8_prior_bits":True,
        "cross_cell_public_input_apparent_information_cost_extra_bytes_per_cell":8,
        "cross_cell_information_not_learned_physical_communication":True,
        "proper_score_difference_not_universal_conditional_mutual_information":True,
        "current_own_local_history_conditioning_is_one_step_only":True,
        "full_public_context_conventional_control_not_camera_corrected":True,
        "no_authentic_unseen_independent_source_family":True,
        "no_native_damage_or_functional_recovery_test":True,
        "full_original_env_policy_model_CPU_RSS_wire_total_cost_not_matched":True,
        "shared_process_CPU_ns_diagnostic_only":
            time.process_time_ns()-t0,
        "source_private_grid_pose_mission_reward_object_labels_to_models":False,
        "G29_exact_source_atlas":"BLOCKED",
        "original_upstream_license_metadata_conflict":"UNRESOLVED",
        "protected_scientific_first_use_consumed":False,
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit(
            "Usage: python -m research.nci04_s3.native_crosscell_information ORIGINAL_FARAMA_SOURCE")
    main(sys.argv[1])
