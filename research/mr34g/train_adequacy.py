"""MR34G: frozen TRAINING-ONLY genuine-source conventional RNN adequacy.

No heldout science, original source changes, evaluator labels or Yggdrasil
architecture edits. Uses ORIGINAL native Farama/Pycolab experience through the
previous frozen public encoder. No post-result tuning allowed. A good
training-fit result is not generalisation, nor proof of cognitive superiority.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import numpy as np

from research.mr34f.prospective_controls import (
    INPUT, TARGET, LATENT, SOURCES, Logistic, Recurrent, episodes,
    verify_source, canon, sha, peak_rss, frozen as previous_frozen,
)

FILE=Path(__file__).with_name("frozen_protocol.json")
TRAIN=(1613,1619,1621,1627,1637,1657,1663,1667,1669,1693,
       1697,1699,1709,1721,1723,1733,1741,1747,1753,1759)
ADAM_EPOCHS=192
ADAM_LR=.01
BETA1=.9
BETA2=.999
EPSILON=1e-8
CLIP=5.

def contract():
    p=json.loads(FILE.read_text(encoding="utf-8"))
    opt=p["optimizer_frozen"]
    if (p["schema"]!="yggdrasil.mr34g.train_only_conventional_recurrence_adequacy.v1"
        or p["exact_prior_mr34f_sha"]!="df842b5857efd1821d2712b4adb49b79c1d8db59"
        or p["new_training_only_development_native_reset_seeds"]!=list(TRAIN)
        or p["source_native_action_limit"]!=96
        or p["model_initialization_seeds"]!=[17,31]
        or opt!={"adam_epochs":192,"adam_lr":0.01,
                "beta1":0.9,"beta2":0.999,"epsilon":1e-8,
                "global_gradient_l2_clip":5.0,
                "train_order":"fixed ascending source reset seeds",
                "baseline_sgd_epochs":24,"baseline_logistic_epochs":100}
        or any(p["original_source_sha"].get(k)!=v[0] for k,v in SOURCES.items())
        or p["no_scientific_first_use"] is not True
        or p["no_prospective_evaluation"] is not True
        or p["no_yggdrasil_cognitive_model_modification"] is not True
        or p["no_retuning_of_mr34f_protocol_or_scientific_decision"] is not True):
        raise ValueError("MR34G_FROZEN_CONTROL_ADEQUACY_PROTOCOL_DRIFT")
    old=previous_frozen()
    if old["new_frozen_development_training_reset_seeds"] is None:
        raise ValueError("MR34G_ORIGINAL_PREDECESSOR_NOT_FOUND")
    if set(TRAIN)&(set(old["new_frozen_development_training_reset_seeds"])|
                   set(old["new_frozen_held_development_evaluation_seeds"])):
        raise ValueError("MR34G_SOURCE_COHORT_OVERLAP")
    return p

def mean_episode_brier(model, episodes_train):
    # The original reset-seed cluster is the independent source unit; do NOT
    # count hundreds of within-reset native steps as independent replicates.
    result=[]
    for ep in episodes_train:
        if isinstance(model,Logistic):
            forecast=model.forecast(ep)
        else:
            forecast=model.forward(ep)[0]
        labels=np.array([r[2] for r in ep])
        if len(forecast)!=len(labels):
            raise ValueError("MR34G_SOURCE_PREACTION_TARGET_MISALIGN")
        result.append(float(np.mean((forecast-labels)**2)))
    return float(np.mean(result)),result

class AdamRecurrent(Recurrent):
    """Original unchanged 23×8 tanh RNN, 8×8 memory, 8×8 event head.

    Only optimizer and precommitted TRAINING computation differ. The
    analytic episode-BPTT derivative is consistent with sigmoid cross-entropy.
    """
    def __init__(self,init_seed,cfg):
        super().__init__(init_seed,cfg)
        self.first_moments=[np.zeros_like(p) for p in self.params()]
        self.second_moments=[np.zeros_like(p) for p in self.params()]
        self.adam_step=0
        self.train_cpu=0

    def episode_gradient(self,ep):
        predictions,hidden=self.forward(ep)
        steps=len(ep)
        gradients=[np.zeros_like(p) for p in self.params()]
        dwx,dwh,dbh,dwy,dby=gradients
        downstream=np.zeros(LATENT)
        for t in reversed(range(steps)):
            current,_,label=ep[t]
            pred=predictions[t]
            # Gradient of binary cross-entropy, averaged over action events
            # and eight future PUBLIC event indicators.
            output_delta=(pred-label)/(steps*TARGET)
            dwy+=np.outer(hidden[t+1],output_delta)
            dby+=output_delta
            node_delta=(output_delta@self.wy.T+downstream) * (1-hidden[t+1]**2)
            dwx+=np.outer(current,node_delta)
            dwh+=np.outer(hidden[t],node_delta)
            dbh+=node_delta
            downstream=node_delta@self.wh.T
        return gradients

    def train_episode_adam(self,ep):
        gradients=self.episode_gradient(ep)
        grad_norm=float(np.sqrt(sum(np.sum(g*g) for g in gradients)))
        factor=min(1.,CLIP/max(grad_norm,1e-12))
        self.adam_step+=1
        n=self.adam_step
        for weights,g,m,v in zip(
                self.params(),gradients,self.first_moments,self.second_moments):
            g=g*factor
            m[:]=BETA1*m+(1.-BETA1)*g
            v[:]=BETA2*v+(1.-BETA2)*g*g
            corrected_m=m/(1.-BETA1**n)
            corrected_v=v/(1.-BETA2**n)
            weights-=ADAM_LR*corrected_m/(np.sqrt(corrected_v)+EPSILON)
        if not all(np.isfinite(w).all() for w in self.params()):
            raise ValueError("MR34G_RECURRENT_NUMERICAL_DIVERGENCE")

    def fit_frozen(self,training):
        now=time.process_time_ns()
        initial,initial_by_seed=mean_episode_brier(self,training)
        self.train_start=initial
        checkpoints={0:initial}
        for epoch in range(1,ADAM_EPOCHS+1):
            for ep in training:
                self.train_episode_adam(ep)
            if epoch in (24,64,128,192):
                checkpoints[epoch]=mean_episode_brier(self,training)[0]
        final,by_seed=mean_episode_brier(self,training)
        self.train_end=final
        self.train_cpu=time.process_time_ns()-now
        return {
            "recurrent_exact_frozen_init_seed_brier":initial,
            "trained_frozen_epoch_mean_training_brier":final,
            "training_only_per_reset_seed_final_brier":{
                str(s):z for s,z in zip(TRAIN,by_seed)},
            "development_training_convergence_checkpoints_brier":checkpoints,
            "adam_optimizer_full_state_bytes":sum(
                x.nbytes for x in self.first_moments+self.second_moments
            )+8,
            "raw_recurrent_model_parameters_checkpoint_bytes":
                self.checkpoint_bytes(),
            "recurrent_training_cpu_ns":self.train_cpu,
            "adam_source_training_native_episode_updates":self.adam_step
        }

def source_run(source_name,root):
    ep,custody=episodes(root,source_name,TRAIN)
    baseline_cfg={
        "logistic_epochs":100,
        "logistic_lr":.8,
        "logistic_l2":.0002,
        "recurrent_epochs":24,
        "recurrent_lr":.04,
        "recurrent_init_seeds":[17,31],
        "recurrent_gradient_clip":5.,
    }
    current=Logistic(False,baseline_cfg)
    current.fit(ep)
    logistic_mean,by_seed_current=mean_episode_brier(current,ep)
    initialized=[]
    optimized=[]
    for init_seed in (17,31):
        original=Recurrent(init_seed,baseline_cfg)
        original_init=mean_episode_brier(original,ep)[0]
        original.fit(ep)
        sgd_end=mean_episode_brier(original,ep)[0]
        initialized.append({
            "init_seed":init_seed,
            "original_24_epoch_SGD_initial_brier":original_init,
            "original_24_epoch_SGD_training_brier":sgd_end,
            "original_24_epoch_SGD_full_training_CPU_ns":original.training_cpu,
        })
        new=AdamRecurrent(init_seed,baseline_cfg)
        metrics=new.fit_frozen(ep)
        optimized.append((metrics["trained_frozen_epoch_mean_training_brier"],
                          init_seed,metrics))
    best_loss,best_seed,best=min(optimized,key=lambda x:(x[0],x[1]))
    adequacy=(
        best_loss<=logistic_mean+.01 and
        best_loss<=best["recurrent_exact_frozen_init_seed_brier"]*.75)
    return {
        "exact_original_source_git_sha":SOURCES[source_name][0],
        "genuine_source_train_only_independent_reset_seed_clusters":len(ep),
        "full_original_native_action_count":sum(len(x) for x in ep),
        "per_reset_seed_original_native_action_public_custody":custody,
        "source_original_native_event_sha256":sha(canon(custody).encode()),
        "equal_public_23_feature_input":True,
        "same_action_consequence_training_histories":True,
        "fully_trained_100epoch_current_only_logistic_train_reset_seed_mean_brier":
            logistic_mean,
        "original_SGD_recurrent_frozen_training_reference":initialized,
        "fixed_epoch_adam_recurrent_control_all_initializations":[{
            "init_seed":seed,**data
        } for _,seed,data in optimized],
        "precommitted_best_converged_training_only_init_seed":best_seed,
        "precommitted_qualifier_recurrent_training_adequacy_GO":bool(adequacy),
        "real_native_logistic_training_CPU_ns":current.train_cpu,
        "serialized_memoryless_logistic_checkpoint_bytes":current.checkpoint_bytes(),
        "no_eval_cohort_opened":True,
        "no_recurrent_candidate_science_qualification_claim":True,
    }

def main(original_farama,original_pycolab):
    p=contract()
    roots={
        name:verify_source(path,SOURCES[name][0])
        for name,path in zip(SOURCES,(original_farama,original_pycolab))
    }
    sys.path.insert(0,str(roots["FaramaMiniGridDoorKey8"]))
    sys.path.insert(0,str(roots["DeepMindPycolabApprehend"]))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    report={name:source_run(name,roots[name]) for name in SOURCES}
    for name in SOURCES:
        verify_source(roots[name],SOURCES[name][0])
    training_go=all(x["precommitted_qualifier_recurrent_training_adequacy_GO"]
                    for x in report.values())
    print("MR34G_CONVENTIONAL_RECURRENT_TRAIN_ONLY_ADEQUACY="+canon({
        "preregistered_precode_protocol_sha256":sha(FROZEN.read_bytes()),
        "independently_authored_original_source_controls":report,
        "frozen_training_adequacy_GO":bool(training_go),
        "original_sources_and_all_training_CPU_ns":time.process_time_ns()-start,
        "original_sources_and_all_training_OS_peak_RSS_bytes":peak_rss(),
        "same_only_public_source_data_and_announced_actions":True,
        "no_independent_first_use_or_heldout_evaluation":True,
        "all_training_optimizer_moments_measured":True,
        "whole_native_source_cpu_and_rss_includes_original_env":True,
        "resource_matched_conventional_architectures":"NOT_ESTABLISHED",
        "original_yggdrasil_native_learner_trained":False,
        "architecture_transfer_scientific_admission":"NO_GO",
        "G29_atlas_and_regressions":"BLOCKED"
    }))

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.mr34g.train_adequacy ORIGINAL_FARAMA ORIGINAL_PYCOLAB")
    main(sys.argv[1],sys.argv[2])
