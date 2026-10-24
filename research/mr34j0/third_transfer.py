"""MR34J0: genuine original third-environment DEV-only native transfer versus fitted controls.

Fits ALL models on Farama + Pycolab before even resetting the original
third-source public BirdEye env. No source reward/private info, no new native
optimizer, no source rewriting and no protected scientific first-use.
"""
from __future__ import annotations

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
    SOURCES,Logistic,episodes,verify_source,current_vector,original_target,
    canon,sha,peak_rss)
from research.mr34g.train_adequacy import AdamRecurrent,mean_episode_brier
from research.mr34h.generalization import FeedforwardAdam
from research.mr34i.admit_gridworld import (
    ORIGINAL_GAME,UPSTREAM_SHA,source_original_git_readonly,public_observation)

SCHEMA="mass.mr34j0.original-third-source-learned-transfer-dev.v1"
FIRST="67ceb8db50db5e52fe6387358b0cd6b43947cb9d"
PARENT="06afcc66f26ef02605bdcca45ed89cada3d2ac48"
NATIVE_ORIGINAL="8e1561eb1a542e21307bac669c42435cf48e59bd"
TRAIN=(1861,1867,1871,1873,1877,1879,1889,1901,1907,1913,
       1931,1933,1949,1951,1973,1979,1987,1993,1997,1999)
THIRD_DEV=(2503,2507,2521,2531,2539,2543,2551,2557)
STREAMS=(0,1)
DEV_MAX_STEPS=48
CONTROL_EPOCHS=48
MODEL_INIT=(17,31)
TRAIN_CFG={
    "logistic_epochs":100,"logistic_lr":.8,"logistic_l2":.0002,
    "recurrent_epochs":24,"recurrent_lr":.04,
    "recurrent_init_seeds":[17,31],"recurrent_gradient_clip":5.0
}
MODEL_NAMES=("native45","trained_8state_recurrent",
             "trained_8state_nonrecurrent","current_logistic",
             "familiar_fit_beta_prior","native45_memory_zeroed")


def frozen_check():
    if (len(TRAIN)!=20 or len(THIRD_DEV)!=8 or max(TRAIN)>=min(THIRD_DEV)
        or TRAIN_CFG["logistic_epochs"]!=100 or CONTROL_EPOCHS!=48
        or MODEL_INIT!=(17,31) or STREAMS!=(0,1)
        or DEV_MAX_STEPS!=48 or len(MODEL_NAMES)!=6):
        raise ValueError("MR34J0_FROZEN_CONTRACT_IDENTITY_DRIFT")


def auth_native_git(path):
    import subprocess
    root=Path(path).resolve()
    if (subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
        !=NATIVE_ORIGINAL):
        raise ValueError("MR34J0_PINNED_NATIVE_S4C1_GIT_IDENTITY_DRIFT")
    if subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip():
        raise ValueError("MR34J0_NATIVE_ORIGINAL_DIRTY")
    return root


def third_public_bridge(observation):
    """Only actual original 3x3 public Unicode. Fixed little-endian uint32."""
    public_observation(observation)  # original author's public-view custody guard
    codes=[ord(str(c)) for c in observation.flat]
    if len(codes)!=9 or any(not (0<=n<=0x10ffff) for n in codes):
        raise ValueError("MR34J0_THIRD_SOURCE_PUBLIC_UNICODE_INVALID")
    result=np.asarray(codes,dtype="<u4").tobytes(order="C")
    if len(result)!=36:
        raise ValueError("MR34J0_PUBLIC_BRIDGE_BYTES_NOT_FIXED")
    return result


def fit_familiar(farama,pycolab):
    """Fit all 4 models on two familiar original public sources; seal before third."""
    from research.nci04_s4c1.original_native_predictive_state import (
        train_native,protocol as native_protocol)
    from research.nci04_s4c1.native_predictive_quotient import (
        NativePredictiveQuotient45)
    if not issubclass(NativePredictiveQuotient45,object):
        raise ValueError("MR34J0_NATIVE_UNAVAILABLE")
    native_protocol()
    families={}
    original_source_start=time.process_time_ns()
    for name,root in (("FaramaMiniGridDoorKey8",farama),
                      ("DeepMindPycolabApprehend",pycolab)):
        rows,auth=episodes(root,name,TRAIN)
        if len(rows)!=20 or any(len(e)==0 for e in rows):
            raise ValueError("MR34J0_ORIGINAL_FAMILIAR_TRAIN_SOURCE_EMPTY")
        families[name]={
            "data":rows,
            "source_public_original_custody_sha256":sha(canon(auth).encode()),
            "actual_original_source_actions":sum(map(len,rows)),
            "original_source_git_SHA256":SOURCES[name][0]
        }
    familiar_source_cpu=time.process_time_ns()-original_source_start
    training=(families["FaramaMiniGridDoorKey8"]["data"]+
              families["DeepMindPycolabApprehend"]["data"])
    start=time.process_time_ns()
    native,info=train_native(training)
    native_cpu=time.process_time_ns()-start
    logistic=Logistic(False,TRAIN_CFG)
    start=time.process_time_ns()
    logistic.fit(training)
    logistic_cpu=time.process_time_ns()-start
    log_fit=float(mean_episode_brier(logistic,training)[0])
    def fit_control(klass):
        clock=time.process_time_ns()
        attempts=[]
        for seed in MODEL_INIT:
            m=klass(seed,TRAIN_CFG)
            initial=float(mean_episode_brier(m,training)[0])
            for epoch in range(1,CONTROL_EPOCHS+1):
                for episode in training:
                    m.train_episode_adam(episode)
            learned=float(mean_episode_brier(m,training)[0])
            attempts.append((learned,seed,m,{
                "initialization":seed,
                "initial_training_Brier":initial,
                "final_training_Brier":learned,
                "source_adam_optimizer_updates":m.adam_step,
                "parameter_float64_bytes":m.checkpoint_bytes(),
                "Adam_optimizer_moments_bytes":sum(x.nbytes for x in
                   m.first_moments+m.second_moments)+8
            }))
        _,_,win,_=min(attempts,key=lambda x:(x[0],x[1]))
        return win,{
            "all_training_only_source_initializations":[x[3] for x in attempts],
            "train_selected_initialization":min(attempts,key=lambda x:(x[0],x[1]))[1],
            "selected_familiar_fit_Brier":min(x[0] for x in attempts),
            "full_both_initialization_training_CPU_ns":time.process_time_ns()-clock,
        }
    recurrent,rec_receipt=fit_control(AdamRecurrent)
    nonrecurrent,ff_receipt=fit_control(FeedforwardAdam)
    adequately_trained=(
        rec_receipt["selected_familiar_fit_Brier"]<=log_fit+.01
        and any(
            rec_receipt["selected_familiar_fit_Brier"]<=
            .8*a["initial_training_Brier"]
            for a in rec_receipt["all_training_only_source_initializations"])
    )
    # Fit-only global independent action source success counts: Beta(1,1).
    labels=np.vstack([np.vstack([x[2] for x in ep]) for ep in training])
    prior=(np.sum(labels,axis=0)+1.)/(len(labels)+2.)
    models={
        "native45":native,
        "trained_8state_recurrent":recurrent,
        "trained_8state_nonrecurrent":nonrecurrent,
        "current_logistic":logistic
    }
    checkpoints={
        "native45":sha(native.snapshot().encode()),
        "trained_8state_recurrent":sha(b"".join(x.tobytes() for x in recurrent.params())),
        "trained_8state_nonrecurrent":sha(b"".join(x.tobytes() for x in nonrecurrent.params())),
        "current_logistic":sha(logistic.w.tobytes()+logistic.b.tobytes()),
        "familiar_fit_beta_prior":sha(prior.tobytes())
    }
    receipts={
        "original_FIT_source_CPU_ns":familiar_source_cpu,
        "familiar_source_original_authors":{key:{
            k:v for k,v in row.items() if k!="data"}
            for key,row in families.items()},
        "familiar_FIT_original_episode_count":len(training),
        "native_original_45_full_40_epoch_training_receipt":info,
        "native_full_training_and_gradient_CPU_ns":native_cpu,
        "native_original_45_checkpoint_float64_bytes":sum(p.nbytes for p in native.params()),
        "native_original_full_serialized_checkpoint_bytes":len(native.snapshot().encode()),
        "fitted_conventional_recurrent_48epochs_both_init":rec_receipt,
        "fitted_conventional_feedforward_48epochs_both_init":ff_receipt,
        "logistic_original_source_fit_CPU_ns":logistic_cpu,
        "logistic_original_train_Brier":log_fit,
        "logistic_original_checkpoint_bytes":logistic.checkpoint_bytes(),
        "familiar_training_fitted_recurrent_adequacy":adequately_trained,
        "all_familiar_fit_model_seal_SHA256":checkpoints,
        "sealed_models_before_third_source_reset":True,
        "FIT_only_prior_source_positive_labels":np.sum(labels,axis=0).tolist(),
        "FIT_only_prior_original_native_actions":len(labels),
        "FIT_only_prior_checkpoint_bytes":prior.nbytes
    }
    return models,prior,receipts,checkpoints


def acquire_original_third(root):
    """Read only independently authored original public unicode wrapper, no rewards."""
    import gymnasium as gym
    import gym_gridworlds
    from gym_gridworlds.observation_wrappers import BirdEyeWrapper
    source_original_git_readonly(root)
    all_episodes=[]
    custody=[]
    any_changed=0
    begin=time.process_time_ns()
    for seed in THIRD_DEV:
        for stream in STREAMS:
            policy=random.Random(1000003*seed+337+10007*stream)
            env=BirdEyeWrapper(gym.make(ORIGINAL_GAME,render_mode=None),
                               view_radius=1)
            rows=[]
            episode_hash=sha256()
            transitions=0
            changed=0
            prev=[np.zeros(23,dtype=np.float64),np.zeros(23,dtype=np.float64)]
            try:
                o,_=env.reset(seed=seed)
                old_source_public=public_observation(o)
                before=third_public_bridge(o)
                for _ in range(DEV_MAX_STEPS):
                    n=int(env.action_space.n)
                    if n!=5:
                        raise ValueError("MR34J0_ORIGINAL_THIRD_LEGAL_ACTION_SPACE_DRIFT")
                    action=policy.randrange(n)
                    public_features=current_vector(before,action)
                    nxt,_reward,done,truncated,_info=env.step(action)
                    new_source_public=public_observation(nxt)
                    after=third_public_bridge(nxt)
                    target=original_target(before,after)
                    # Full original Unicode public source and chosen action as legal audit.
                    episode_hash.update(len(old_source_public).to_bytes(4,"little"))
                    episode_hash.update(old_source_public)
                    episode_hash.update(bytes([action]))
                    episode_hash.update(len(new_source_public).to_bytes(4,"little"))
                    episode_hash.update(new_source_public)
                    episode_hash.update(bytes([int(done),int(truncated)]))
                    rows.append((
                        public_features,
                        np.concatenate([public_features,prev[1],prev[0]]),
                        target
                    ))
                    changed+=int(old_source_public!=new_source_public)
                    transitions+=1
                    prev=[prev[1],public_features]
                    old_source_public=new_source_public
                    before=after
                    if done or truncated:
                        break
            finally:
                env.close()
            if not rows:
                raise ValueError("MR34J0_REAL_THIRD_SOURCE_ZERO_ACTIONS")
            custody.append({
                "source_original_dev_reset_seed":seed,
                "source_original_public_policy_stream":stream,
                "source_actual_public_action_count":transitions,
                "source_original_public_observation_changed_actions":changed,
                "original_public_source_and_action_SHA256":episode_hash.hexdigest(),
                "source_public_tensor_binary64_SHA256":sha(
                    b"".join(x.tobytes() for row in rows for x in row))
            })
            all_episodes.append((seed,stream,rows))
            any_changed+=changed
    source_original_git_readonly(root)
    if len(all_episodes)!=16 or any_changed<1:
        raise ValueError("MR34J0_ORIGINAL_SOURCE_UNINFORMATIVE_OR_ROLE_DRIFT")
    return all_episodes,{
        "genuine_third_public_development_source":ORIGINAL_GAME,
        "original_third_source_git_SHA":UPSTREAM_SHA,
        "dev_reset_seeds":list(THIRD_DEV),
        "dev_policy_streams":list(STREAMS),
        "source_original_sealed_original_public_unicode_event_receipts":custody,
        "source_original_dev_public_action_digest":sha(canon(custody).encode()),
        "source_third_original_public_changed_actions":any_changed,
        "source_all_16_public_episode_actions":sum(x["source_actual_public_action_count"]
                                                  for x in custody),
        "original_public_native_source_generation_CPU_ns":time.process_time_ns()-begin,
        "protected_scientific_first_use_consumed":False,
        "no_third_source_fitting_performed":True
    }


def model_prediction(name,model,prior,episode):
    if name=="native45":
        return model.forward(episode)
    if name=="native45_memory_zeroed":
        return model.forward(episode,zero_state=True)
    if name=="current_logistic":
        return model.forecast(episode)
    if name=="familiar_fit_beta_prior":
        return np.tile(prior,(len(episode),1))
    return model.forward(episode)[0]


def evaluate_frozen_models(models,prior,checkpoints,episodes_dev):
    evidence={}
    counts={name:0 for name in MODEL_NAMES}
    elapsed={name:0 for name in MODEL_NAMES}
    per_stream={name:{} for name in MODEL_NAMES}
    native=models["native45"]
    for seed,stream,ep in episodes_dev:
        labels=np.vstack([r[2] for r in ep])
        for name in MODEL_NAMES:
            model=(native if name=="native45_memory_zeroed"
                   else models.get(name))
            start=time.process_time_ns()
            yhat=model_prediction(name,model,prior,ep)
            elapsed[name]+=time.process_time_ns()-start
            if yhat.shape!=labels.shape or not np.isfinite(yhat).all():
                raise ValueError("MR34J0_PUBLIC_SOURCE_FIT_PREDICTION_INVALID")
            if np.min(yhat)<0 or np.max(yhat)>1:
                raise ValueError("MR34J0_PUBLIC_NATIVE_PROBABILITY_RANGE")
            error=float(np.mean((yhat-labels)**2))
            per_stream[name][f"{seed}:{stream}"]=error
            counts[name]+=len(ep)
    seed_brier={}
    averages={}
    for name in MODEL_NAMES:
        seed_brier[name]={
            str(seed):float(np.mean([per_stream[name][f"{seed}:{s}"]
                                     for s in STREAMS]))
            for seed in THIRD_DEV
        }
        averages[name]=float(np.mean(list(seed_brier[name].values())))
    for name,m in models.items():
        if name=="native45":
            actual=sha(m.snapshot().encode())
        elif name=="current_logistic":
            actual=sha(m.w.tobytes()+m.b.tobytes())
        else:
            actual=sha(b"".join(z.tobytes() for z in m.params()))
        if actual!=checkpoints[name]:
            raise ValueError("MR34J0_THIRD_DEV_WEIGHT_UPDATE_OR_EVAL_LEAK")
    if sha(prior.tobytes())!=checkpoints["familiar_fit_beta_prior"]:
        raise ValueError("MR34J0_FAMILIAR_PRIOR_ALTERED_ON_THIRD")
    admissible=("trained_8state_recurrent","trained_8state_nonrecurrent",
                "current_logistic","familiar_fit_beta_prior")
    best=min(admissible,key=lambda z:(averages[z],z))
    gain=averages[best]-averages["native45"]
    win=sum(seed_brier["native45"][str(s)]<seed_brier[best][str(s)]
            for s in THIRD_DEV)
    ablation=averages["native45_memory_zeroed"]-averages["native45"]
    return {
        "original_third_source_proper_Brier_mean_across_8_original_seed_clusters":averages,
        "per_source_public_DEV_reset_cluster_proper_Brier":seed_brier,
        "per_public_source_DEVELOPMENT_stream_Brier":per_stream,
        "source_original_held_action_counts_per_model":counts,
        "source_original_third_family_inference_CPU_ns":elapsed,
        "best_conventional_fitted_DEV_control_for_conservative_comparison":best,
        "native_improvement_against_best_DEV_control":gain,
        "native_wins_against_strong_control_independent_seed_count":win,
        "native_same_weights_zero_state_ablation_Brier_damage":ablation,
        "frozen_original_third_DEV_source_pre_action_only":True,
        "original_models_sealed_across_all_DEV_source_actions":True
    }


def main(native_original,farama,pycolab,third,output):
    frozen_check()
    native_root=auth_native_git(native_original)
    known={
        "FaramaMiniGridDoorKey8":verify_source(farama,SOURCES["FaramaMiniGridDoorKey8"][0]),
        "DeepMindPycolabApprehend":verify_source(pycolab,SOURCES["DeepMindPycolabApprehend"][0])
    }
    third_root=source_original_git_readonly(third)
    sys.path.insert(0,str(native_root))
    for path in (*known.values(),third_root):
        sys.path.insert(0,str(path))
    from research.mr27.natural_memory import source_guard
    source_guard(known["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    models,prior,fit,seal=fit_familiar(known["FaramaMiniGridDoorKey8"],
                                      known["DeepMindPycolabApprehend"])
    # The original third environment is never stepped before model seal.
    now=time.process_time_ns()
    unknown,third_custody=acquire_original_third(third_root)
    estimates=evaluate_frozen_models(models,prior,seal,unknown)
    benchmark_cpu=time.process_time_ns()-now
    for name,path in known.items():
        verify_source(path,SOURCES[name][0])
    source_original_git_readonly(third_root)
    auth_native_git(native_root)
    recurrent_cpu=fit["fitted_conventional_recurrent_48epochs_both_init"]["full_both_initialization_training_CPU_ns"]
    native_cpu=fit["native_full_training_and_gradient_CPU_ns"]
    native_inf=estimates["source_original_third_family_inference_CPU_ns"]["native45"]
    recurrent_inf=estimates["source_original_third_family_inference_CPU_ns"]["trained_8state_recurrent"]
    if min(native_cpu,recurrent_cpu,native_inf,recurrent_inf)<=0:
        raise ValueError("MR34J0_INDEPENDENT_TRAIN_OR_INFERENCE_CPU_UNMEASURABLE")
    native_model_bytes=fit["native_original_45_checkpoint_float64_bytes"]
    from research.mr34g.train_adequacy import AdamRecurrent
    conventional_model_bytes=models["trained_8state_recurrent"].checkpoint_bytes()
    resource=(native_model_bytes<conventional_model_bytes and
              native_cpu<=.7*recurrent_cpu and native_inf<=.7*recurrent_inf)
    original_science=(
        fit["familiar_training_fitted_recurrent_adequacy"] and
        estimates["native_improvement_against_best_DEV_control"]>=.003 and
        estimates["native_wins_against_strong_control_independent_seed_count"]>=6 and
        estimates["native_same_weights_zero_state_ablation_Brier_damage"]>=.001 and
        resource
    )
    out={
        "schema":SCHEMA,
        "frozen_PRECODE_PROTOCOL":FIRST,
        "source_admission_parent":PARENT,
        "original_native_Git_SHA":NATIVE_ORIGINAL,
        "source_third_Git_SHA":UPSTREAM_SHA,
        "OS":platform.system(),
        "Python":platform.python_version(),
        "NumPy":np.__version__,
        "genuine_familiar_original_source_FIT":fit,
        "genuine_original_third_source_unseen_reset_DEV":third_custody,
        "actual_fitted_models_unfamiliar_third_source_DEV":estimates,
        "new_third_source_training_gradient_steps":0,
        "native_to_recurrent_two_init_fit_CPU_ratio":native_cpu/recurrent_cpu,
        "native_to_recurrent_original_third_inference_CPU_ratio":native_inf/recurrent_inf,
        "native_model_parameter_bytes":native_model_bytes,
        "conventional_recurrent_parameter_bytes":conventional_model_bytes,
        "prospective_native_budget_conditions_met":bool(resource),
        "prospective_science_DEV_signal_all_conditions_met":bool(original_science),
        "source_all_origins_AND_models_process_CPU_ns":time.process_time_ns()-start,
        "source_all_origins_AND_models_peak_OS_RSS_bytes":peak_rss(),
        "source_original_environment_connection_bytes":0,
        "energy_measured":False,
        "known_third_source_previously_DEV_admitted":True,
        "blinded_scientific_third_source_family_FIRST_USE":False,
        "original_G29_source_bound_native_integration":"FAIL_CLOSED",
        "scientific_admission":"NO_GO"
    }
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print("MR34J0_ORIGINAL_THIRD_SOURCE_NATIVE_TRANSFER="+canon({
        "schema":SCHEMA,"OS":platform.system(),"receipt_sha256":sha(path.read_bytes()),
        "familiar_source_action_sha":{n:r["source_public_original_custody_sha256"]
            for n,r in fit["familiar_source_original_authors"].items()},
        "third_original_public_action_SHA":third_custody["source_original_dev_public_action_digest"],
        "native_trained_original_checkpoint":seal["native45"],
        "strong_fit_conventional_adequate":fit["familiar_training_fitted_recurrent_adequacy"],
        "all_models_third_public_seed_mean_brier":estimates["original_third_source_proper_Brier_mean_across_8_original_seed_clusters"],
        "best_control":estimates["best_conventional_fitted_DEV_control_for_conservative_comparison"],
        "native_improvement":estimates["native_improvement_against_best_DEV_control"],
        "native_seed_wins":estimates["native_wins_against_strong_control_independent_seed_count"],
        "native_memory_ablation_damage":estimates["native_same_weights_zero_state_ablation_Brier_damage"],
        "fit_cpu_native_over_recurrent":out["native_to_recurrent_two_init_fit_CPU_ratio"],
        "dev_inference_cpu_native_over_recurrent":out["native_to_recurrent_original_third_inference_CPU_ratio"],
        "all_frozen_DEV_requirements_met":out["prospective_science_DEV_signal_all_conditions_met"],
        "scientific_protected_first_use":False
    }))


if __name__=="__main__":
    if len(sys.argv)!=6:
        raise SystemExit("Usage: python -m research.mr34j0.third_transfer ORIGINAL_NATIVE FARAMA PYCOLAB THIRD OUTPUT")
    main(*sys.argv[1:])
