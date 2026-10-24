"""MR34J1: prospectively frozen original public observation/history sufficiency DEV.

The genuine original third-source env and held public data are NEVER opened
until every fitted model and fit-only Unicode codebook is sealed. Native MR34J0
is not re-trained and its held DEV cohort is not reacquired.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import platform
import random
import sys
import time

import numpy as np

from research.mr34f.prospective_controls import (
    current_vector,original_target,canon,sha,peak_rss)
from research.mr34i.admit_gridworld import (
    ORIGINAL_GAME,UPSTREAM_SHA,public_observation,source_original_git_readonly)
from research.mr34j0.third_transfer import third_public_bridge

SCHEMA="mass.mr34j1.third-source-public-information-adequacy.dev.v1"
FIRST="23e336a093673f9c5a05e81a08d3f91485367f7e"
PARENT="dbdd9b75c7fb518e28441597421e86f0073421ea"
FIT=(2609,2617,2621,2633,2647,2657,2663,2671,
     2683,2687,2693,2699,2707,2711,2713,2719)
HELD=(2741,2749,2753,2767,2777,2789,2791,2797)
STREAMS=(0,1)
STEPS=48
EPOCHS=200
LR=.4
L2=.002
MAX_CODEPOINTS=32
REP_GAIN=.005
HISTORY_GAIN=.005
MIN_SEED_WINS=6
NAMES=("pooled_current","pooled_previous","categorical_current",
       "categorical_previous","categorical_sham_previous","fit_global_beta")


def source_cohort(root,seeds,cohort):
    """Only original BirdEye PUBLIC Unicode and legal original public action."""
    import gymnasium as gym
    import gym_gridworlds
    from gym_gridworlds.observation_wrappers import BirdEyeWrapper
    source_original_git_readonly(root)
    all_episodes=[]
    receipts=[]
    begin=time.process_time_ns()
    total_changes=0
    for seed in seeds:
        for stream in STREAMS:
            actor=random.Random(1000003*seed+337+10007*stream)
            env=BirdEyeWrapper(
                gym.make(ORIGINAL_GAME,render_mode=None),view_radius=1)
            records=[]
            event=sha256()
            changed=0
            try:
                obs,_=env.reset(seed=seed)
                before_unicode=public_observation(obs)
                before=third_public_bridge(obs)
                prev=None
                for step in range(STEPS):
                    n=int(env.action_space.n)
                    if n!=5:
                        raise ValueError("MR34J1_PUBLIC_SOURCE_LEGAL_ACTION_SPACE_DRIFT")
                    action=actor.randrange(n)
                    x=current_vector(before,action)
                    nxt,_reward,done,truncated,_info=env.step(action)
                    after_unicode=public_observation(nxt)
                    after=third_public_bridge(nxt)
                    y=original_target(before,after)
                    event.update(len(before_unicode).to_bytes(4,"little"))
                    event.update(before_unicode)
                    event.update(bytes([action]))
                    event.update(len(after_unicode).to_bytes(4,"little"))
                    event.update(after_unicode)
                    event.update(bytes([int(done),int(truncated)]))
                    if before_unicode!=after_unicode:
                        changed+=1
                    records.append({
                        "public36":before,
                        "previous_public36":prev,
                        "action":action,
                        "public23":x,
                        "previous_public23":(
                            np.zeros(23,dtype=np.float64)
                            if len(records)==0 else records[-1]["public23"]),
                        "target8":y
                    })
                    prev=before
                    before_unicode=after_unicode
                    before=after
                    if done or truncated:
                        break
            finally:
                env.close()
            if not records:
                raise ValueError("MR34J1_EMPTY_GENUINE_ORIGINAL_SOURCE_EPISODE")
            all_episodes.append((seed,stream,records))
            receipts.append({
                "original_source_reset_seed":seed,
                "original_source_actor_stream":stream,
                "real_original_action_count":len(records),
                "real_original_public_view_changed_actions":changed,
                "original_source_public_action_next_sha256":event.hexdigest(),
                "original_public_current_and_next_target_float64_sha256":sha(
                    b"".join(np.ascontiguousarray(v).tobytes()
                             for r in records for v in (r["public23"],r["target8"])))
            })
            total_changes+=changed
    source_original_git_readonly(root)
    if len(all_episodes)!=len(seeds)*len(STREAMS) or total_changes<1:
        raise ValueError("MR34J1_INSUFFICIENT_GENUINE_ORIGINAL_SOURCE")
    return all_episodes,{
        "original_authored_source_git_SHA":UPSTREAM_SHA,
        "source_original_role":cohort,
        "original_reset_seeds":list(seeds),
        "original_actor_streams":list(STREAMS),
        "original_source_episode_receipts":receipts,
        "original_real_source_receipt_sha256":sha(canon(receipts).encode()),
        "total_genuine_source_actions":sum(x["real_original_action_count"] for x in receipts),
        "public_unicode_changed_action_count":total_changes,
        "original_source_actor_CPU_ns":time.process_time_ns()-begin,
        "source_only_public_observations_not_reward":True,
        "protected_scientific_first_use":False
    }


def public_codepoints(frame):
    x=np.frombuffer(frame,dtype="<u4")
    if len(frame)!=36 or x.shape!=(9,):
        raise ValueError("MR34J1_ORIGINAL_PUBLIC_FRAME_UTF32_ID_DRIFT")
    return tuple(int(v) for v in x)


def fit_codebook(train):
    chars=set()
    for _,_,ep in train:
        for r in ep:
            chars.update(public_codepoints(r["public36"]))
            if r["previous_public36"] is not None:
                chars.update(public_codepoints(r["previous_public36"]))
    vocabulary=sorted(chars)
    if len(vocabulary)>MAX_CODEPOINTS or not vocabulary:
        raise ValueError("MR34J1_FIT_ONLY_CATEGORICAL_VOCAB_CAP")
    return vocabulary


def onehot_public(frame,action,book):
    width=9*(len(book)+1)+7
    a=np.zeros(width,dtype=np.float64)
    if frame is None:
        return a
    index={c:i for i,c in enumerate(book)}
    for pos,c in enumerate(public_codepoints(frame)):
        a[pos*(len(book)+1)+index.get(c,len(book))]=1.
    if not 0<=action<5:
        raise ValueError("MR34J1_TRUE_ORIGINAL_THIRD_ACTION_NOT_LEGAL")
    a[9*(len(book)+1)+action]=1.
    return a


def design(episodes,book,fit_donors):
    """The sham history is always sampled from a DIFFERENT FIT reset only."""
    tensors={name:[] for name in NAMES[:-1]}
    targets=[]
    meta=[]
    for idx,(seed,stream,ep) in enumerate(episodes):
        if len(fit_donors)<8:
            raise ValueError("MR34J1_INSUFFICIENT_ORIGINAL_FIT_DONOR_POOL")
        # For FIT: donor is a different authentic reset; for HELD: FIT donor.
        if episodes is fit_donors:
            donor_idx=(idx+7)%len(fit_donors)
        else:
            donor_idx=(idx+7)%len(fit_donors)
        donor=fit_donors[donor_idx][2]
        if episodes is fit_donors and donor_idx==idx:
            raise ValueError("MR34J1_SHAM_HISTORY_SAME_SOURCE_RESET")
        for t,r in enumerate(ep):
            pooled=np.asarray(r["public23"],dtype=np.float64)
            pooled_prev=np.asarray(r["previous_public23"],dtype=np.float64)
            cat=onehot_public(r["public36"],r["action"],book)
            actual_prev=(
                onehot_public(r["previous_public36"],ep[t-1]["action"],book)
                if t>0 else onehot_public(None,0,book))
            sham=donor[(3*t+7)%len(donor)]
            fake_prev=onehot_public(sham["public36"],sham["action"],book)
            tensors["pooled_current"].append(pooled)
            tensors["pooled_previous"].append(np.concatenate([pooled,pooled_prev]))
            tensors["categorical_current"].append(cat)
            tensors["categorical_previous"].append(np.concatenate([cat,actual_prev]))
            tensors["categorical_sham_previous"].append(np.concatenate([cat,fake_prev]))
            targets.append(np.asarray(r["target8"],dtype=np.float64))
            meta.append((seed,stream))
    X={name:np.ascontiguousarray(np.vstack(rows),dtype=np.float64)
       for name,rows in tensors.items()}
    y=np.ascontiguousarray(np.vstack(targets),dtype=np.float64)
    if not np.isfinite(y).all() or not np.all((y==0)|(y==1)):
        raise ValueError("MR34J1_ORIGINAL_PUBLIC_EIGHT_CHANGE_TARGET_INVALID")
    return X,y,meta


def sigmoid(x):
    return 1./(1.+np.exp(-np.clip(x,-30.,30.)))


def brier(yhat,truth):
    return float(np.mean((yhat-truth)**2))


def train_logistic(X,y):
    w=np.zeros((X.shape[1],8),dtype=np.float64)
    bias=np.zeros(8,dtype=np.float64)
    started=time.process_time_ns()
    beginning=brier(sigmoid(X@w+bias),y)
    for _ in range(EPOCHS):
        forecast=sigmoid(X@w+bias)
        error=forecast-y
        dw=X.T@error/len(y)+L2*w
        db=np.mean(error,axis=0)
        w-=LR*dw
        bias-=LR*db
    ending=brier(sigmoid(X@w+bias),y)
    cpu=time.process_time_ns()-started
    if not np.isfinite(w).all() or not np.isfinite(bias).all() or not math.isfinite(ending):
        raise ValueError("MR34J1_FIT_LOGISTIC_NONFINITE")
    return (w,bias),{
        "frozen_full_batch_optimizer_epochs":EPOCHS,
        "source_fit_initial_Brier":beginning,
        "source_fit_final_Brier":ending,
        "source_fit_CPU_ns":cpu,
        "checkpoint_SHA256":sha(w.tobytes()+bias.tobytes()),
        "native_float64_coefficient_checkpoint_bytes":w.nbytes+bias.nbytes,
        "original_source_fitted_example_count":len(y)
    }


def ambiguity(episodes):
    lookup={}
    for _,_,ep in episodes:
        for r in ep:
            cat=(r["public36"],r["action"])
            pooled=(r["public23"].tobytes(),)
            for name,key in (("full_public_plus_action",cat),
                             ("pooled_23_plus_action",pooled)):
                lookup.setdefault(name,defaultdict(list))[key].append(r["target8"])
    out={}
    for name,keys in lookup.items():
        repeated=0
        contradictory=0
        total=sum(len(v) for v in keys.values())
        repeated_key_count=0
        weighted_variance=0.
        for rows in keys.values():
            if len(rows)<2:
                continue
            repeated+=len(rows)
            repeated_key_count+=1
            a=np.vstack(rows)
            weighted_variance+=len(rows)*float(np.mean(np.var(a,axis=0)))
            if np.any(np.max(a,axis=0)!=np.min(a,axis=0)):
                contradictory+=len(rows)
        out[name]={
            "number_of_exact_fit_public_input_keys":len(keys),
            "number_of_fit_keys_repeated":repeated_key_count,
            "fit_source_event_fraction_in_repeated_keys":repeated/max(1,total),
            "fit_source_event_fraction_in_conflicting_keys":contradictory/max(1,total),
            "fit_source_repeated_exact_key_mean_target_variance":weighted_variance/max(1,repeated),
            "source_private_causal_information_available":False,
            "empirical_ambiguity_is_irreducibility_proof":False
        }
    return out


def score_models(models,prior,x,y,meta):
    all_scores={}
    prior_scores={}
    predictions={}
    time_ns={}
    for name in NAMES:
        started=time.process_time_ns()
        if name=="fit_global_beta":
            yhat=np.tile(prior,(len(y),1))
        else:
            w,b=models[name]
            yhat=sigmoid(x[name]@w+b)
        time_ns[name]=time.process_time_ns()-started
        predictions[name]=yhat
        per_seed={}
        per_stream={}
        for seed in HELD:
            vals=[]
            for stream in STREAMS:
                idx=[i for i,(s,st) in enumerate(meta) if s==seed and st==stream]
                if not idx:
                    raise ValueError("MR34J1_HELD_GENUINE_SOURCE_STREAM_MISSING")
                metric=brier(yhat[idx],y[idx])
                per_stream[f"{seed}:{stream}"]=metric
                vals.append(metric)
            per_seed[str(seed)]=float(np.mean(vals))
        all_scores[name]={
            "held_original_reset_seed_cluster_mean_Brier":float(np.mean(list(per_seed.values()))),
            "original_held_seed_cluster_Brier":per_seed,
            "source_stream_Brier":per_stream,
            "original_source_steps_scored":len(y)
        }
    return all_scores,time_ns


def make_decision(scores):
    def mean(k):return scores[k]["held_original_reset_seed_cluster_mean_Brier"]
    def seed(k,s):return scores[k]["original_held_seed_cluster_Brier"][str(s)]
    repr_gain=mean("pooled_current")-mean("categorical_current")
    repr_wins=sum(seed("categorical_current",s)<seed("pooled_current",s) for s in HELD)
    repr_signal=(repr_gain>=REP_GAIN and repr_wins>=MIN_SEED_WINS
                 and mean("categorical_current")<mean("fit_global_beta"))
    history_better_of_controls=min(mean("categorical_current"),
                                   mean("categorical_sham_previous"))
    history_gain=history_better_of_controls-mean("categorical_previous")
    history_wins=sum(
        seed("categorical_previous",s)<seed("categorical_current",s)
        and seed("categorical_previous",s)<seed("categorical_sham_previous",s)
        for s in HELD)
    history_signal=history_gain>=HISTORY_GAIN and history_wins>=MIN_SEED_WINS
    return {
        "frozen_representation_signal":bool(repr_signal),
        "frozen_history_incremental_signal":bool(history_signal),
        "categorical_current_vs_original_pooled_Brier_gain":repr_gain,
        "categorical_current_vs_pooled_independent_seed_wins":repr_wins,
        "categorical_previous_vs_best_current_or_FIT_sham_Brier_gain":history_gain,
        "categorical_previous_vs_both_independent_seed_wins":history_wins,
        "test_requires_actual_held_source_public_outcomes":True,
        "scientific_native_learning_admission":"NO_GO"
    }


def run(original_source,output):
    source_original_git_readonly(original_source)
    t0=time.process_time_ns()
    fit,fit_receipt=source_cohort(original_source,FIT,"original_public_development_FIT")
    book=fit_codebook(fit)
    X,y,meta=design(fit,book,fit)
    fit_features_sha={k:sha(v.tobytes()) for k,v in X.items()}
    fit_targets_sha=sha(y.tobytes())
    models={}
    training={}
    for name in NAMES[:-1]:
        models[name],training[name]=train_logistic(X[name],y)
    prior=(np.sum(y,axis=0)+1.)/(len(y)+2.)
    training["fit_global_beta"]={
        "source_fit_initial_Brier":brier(np.tile(prior,(len(y),1)),y),
        "source_fit_final_Brier":brier(np.tile(prior,(len(y),1)),y),
        "source_fit_CPU_ns":0,
        "checkpoint_SHA256":sha(prior.tobytes()),
        "native_float64_coefficient_checkpoint_bytes":prior.nbytes,
        "original_source_fitted_example_count":len(y)
    }
    seal={name:v["checkpoint_SHA256"] for name,v in training.items()}
    info_ambiguity=ambiguity(fit)
    # No original HELD reset has been invoked before this frozen checkpoint seal.
    train_public_bit_rate=np.mean(y,axis=0)
    train_cpu=time.process_time_ns()-t0
    held,held_receipt=source_cohort(
        original_source,HELD,"original_public_disjoint_development_HELD")
    held_X,held_y,held_meta=design(held,book,fit)
    held_features_sha={k:sha(v.tobytes()) for k,v in held_X.items()}
    held_targets_sha=sha(held_y.tobytes())
    results,infer_cpu=score_models(models,prior,held_X,held_y,held_meta)
    for name,(w,b) in models.items():
        if sha(w.tobytes()+b.tobytes())!=seal[name]:
            raise ValueError("MR34J1_HELD_SOURCE_FITTED_MODEL_WEIGHT_LEAK")
    if sha(prior.tobytes())!=seal["fit_global_beta"]:
        raise ValueError("MR34J1_HELD_SOURCE_BETA_PRIOR_LEAK")
    held_rate=np.mean(held_y,axis=0)
    decision=make_decision(results)
    receipt={
        "schema":SCHEMA,
        "frozen_first_precode_commit":FIRST,
        "exact_unchanged_prior_parent":PARENT,
        "third_independent_original_source_sha":UPSTREAM_SHA,
        "original_development_fit_source":fit_receipt,
        "original_development_disjoint_held_source":held_receipt,
        "FIT_only_source_codepoint_dictionary":book,
        "FIT_only_original_all_five_model_seal_SHA256":seal,
        "FIT_source_genuine_public_feature_sha256":fit_features_sha,
        "FIT_source_real_original_eightbit_next_target_sha256":fit_targets_sha,
        "HELD_source_genuine_public_feature_sha256":held_features_sha,
        "HELD_source_real_original_eightbit_next_target_sha256":held_targets_sha,
        "FIT_only_public_observation_target_collision_diagnostics":info_ambiguity,
        "source_FIT_true_eight_bin_change_frequencies":train_public_bit_rate.tolist(),
        "source_HELD_true_eight_bin_change_frequencies":held_rate.tolist(),
        "source_FIT_to_HELD_eight_bin_change_frequency_delta":(held_rate-train_public_bit_rate).tolist(),
        "fully_fitted_original_source_control_receipts":training,
        "held_original_source_per_seed_proper_Brier":results,
        "held_original_source_inference_CPU_ns_all_arms":infer_cpu,
        "independent_frozen_information_hypotheses":decision,
        "total_source_fit_read_and_all_models_CPU_ns":train_cpu,
        "total_source_real_held_and_model_CPU_ns":time.process_time_ns()-t0-train_cpu,
        "whole_process_original_source_and_models_OS_peak_RSS_bytes":peak_rss(),
        "original_source_and_models_unmodified":True,
        "models_sealed_before_held_original_source_first_action":True,
        "original_held_source_train_updates":0,
        "original_protected_scientific_first_use":False,
        "original_native45_retrained_or_retuned":False,
        "original_G29_protected_integration":"BLOCKED",
        "scientific_admission":"NO_GO"
    }
    source_original_git_readonly(original_source)
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print("MR34J1_ORIGINAL_PUBLIC_INFORMATION="+canon({
        "schema":SCHEMA,"OS":platform.system(),"receipt_sha256":sha(p.read_bytes()),
        "FIT_original_source_SHA":fit_receipt["original_real_source_receipt_sha256"],
        "HELD_original_source_SHA":held_receipt["original_real_source_receipt_sha256"],
        "source_held_original_actions":held_receipt["total_genuine_source_actions"],
        "public_codebook_size":len(book),
        "source_model_development_seed_mean_Brier":{
            n:r["held_original_reset_seed_cluster_mean_Brier"] for n,r in results.items()},
        "frozen_decision":decision,
        "original_protected_scientific_first_use":False
    }))


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.mr34j1.public_information THIRD_ORIGINAL_SOURCE RECEIPT")
    run(*sys.argv[1:])
