"""MR34H: original native held-development recurrence generalization.

Train on new original source reset seeds, select by TRAIN only, then collect
and score original disjoint held-development episodes. Never use hidden
source state; no protected scientific first-use, Ygg model or merge.
"""
from pathlib import Path
import json
import sys
import time
import numpy as np
from research.mr34f.prospective_controls import (
    INPUT,TARGET,LATENT,SOURCES,Logistic,Counts,episodes,
    verify_source,canon,sha,peak_rss,score)
from research.mr34g.train_adequacy import (
    AdamRecurrent,mean_episode_brier,ADAM_EPOCHS)

FROZEN=Path(__file__).with_name("frozen_protocol.json")
TRAIN=(1801,1811,1823,1831,1847,1861,1867,1871,1877,1879,
       1889,1901,1907,1913,1931,1933,1949,1951,1973,1979)
HELD=(2003,2011,2017,2027,2029,2039,2053,2063,2069,2081,2083,2087)
PARAMS={"logistic_epochs":100,"logistic_lr":.8,"logistic_l2":.0002,
        "recurrent_epochs":24,"recurrent_lr":.04,
        "recurrent_init_seeds":[17,31],"recurrent_gradient_clip":5.}

def contract():
    p=json.loads(FROZEN.read_text(encoding="utf-8"))
    expected={"adam_epochs":192,"adam_lr":0.01,"beta1":0.9,
        "beta2":0.999,"epsilon":1e-8,"global_gradient_l2_clip":5,
        "init_seeds":[17,31],
        "train_order":"original source reset-seed ascending fixed",
        "logistic_epochs":100,"max_symbolic_keys":128}
    if (p["schema"]!="yggdrasil.mr34h.prospective-held-development-trained-recurrence-v1"
        or p["exact_parent_mr34g_source_sha"]!="0961d803f55273f1d6764af3813764692e2c0231"
        or p["fresh_training_development_seeds"]!=list(TRAIN)
        or p["disjoint_held_development_seeds"]!=list(HELD)
        or set(TRAIN)&set(HELD) or p["optimizer"]!=expected
        or p["max_original_source_native_actions"]!=96
        or p["protected_science_first_use"] is not False
        or p["no_new_yggdrasil_cognitive_training"] is not True
        or p["no_evaluation_data_collection_before_all_models_sealed"] is not True
        or any(p["original_source_sha"].get(k)!=v[0] for k,v in SOURCES.items())):
        raise ValueError("MR34H_PRECOMMITTED_PROTOCOL_IDENTITY_DRIFT")
    return p

class FeedforwardAdam(AdamRecurrent):
    """Equally parameter-allocated eight-unit hidden control trained WITHOUT history."""
    def forward(self,episode,ablate=False):
        hlist=[np.zeros(LATENT)]
        preds=[]
        for x,_,_ in episode:
            h=np.tanh(x@self.wx+self.bh)
            z=np.clip(h@self.wy+self.by,-30,30)
            preds.append(1/(1+np.exp(-z)))
            hlist.append(h)
        return np.array(preds),hlist
    def episode_gradient(self,episode):
        pred,h=self.forward(episode)
        dwx=np.zeros_like(self.wx)
        dwh=np.zeros_like(self.wh)
        dbh=np.zeros_like(self.bh)
        dwy=np.zeros_like(self.wy)
        dby=np.zeros_like(self.by)
        for i,(x,_,y) in enumerate(episode):
            err=(pred[i]-y)/(len(episode)*TARGET)
            dwy+=np.outer(h[i+1],err)
            dby+=err
            delta=(err@self.wy.T)*(1-h[i+1]**2)
            dwx+=np.outer(x,delta)
            dbh+=delta
        return [dwx,dwh,dbh,dwy,dby]

def fit_adam(klass,training):
    started=time.process_time_ns()
    fits=[]
    for seed in (17,31):
        m=klass(seed,PARAMS)
        init=mean_episode_brier(m,training)[0]
        checkpoints={"0":init}
        for epnum in range(1,ADAM_EPOCHS+1):
            for episode in training:
                m.train_episode_adam(episode)
            if epnum in (24,64,128,192):
                checkpoints[str(epnum)]=mean_episode_brier(m,training)[0]
        final=mean_episode_brier(m,training)[0]
        fits.append((final,seed,m,{
            "initialization_seed":seed,"initial_training_brier":init,
            "final_training_brier":final,"training_curve":checkpoints,
            "full_model_checkpoint_bytes":m.checkpoint_bytes(),
            "adam_training_only_moments_bytes":
                sum(v.nbytes for v in m.first_moments+m.second_moments)+8,
            "original_source_training_episode_updates":m.adam_step}))
    winning=min(fits,key=lambda f:(f[0],f[1]))
    return winning[2],{
        "training_only_init_selection":winning[1],
        "selected_train_seed_mean_brier":winning[0],
        "all_frozen_training_initializations":[item[3] for item in fits],
        "both_init_full_training_cpu_ns":time.process_time_ns()-started}

def evaluate(name,model,held,ablate=False):
    now=time.process_time_ns()
    if isinstance(model,Logistic):
        preds=[model.forecast(e,ablate) for e in held]
    elif isinstance(model,Counts):
        preds=[model.forecast(e) for e in held]
    else:
        preds=[model.forward(e,ablate)[0] for e in held]
    avg,cluster=score(preds,held)
    return {"proper_held_source_action_weighted_brier":avg,
            "held_reset_seed_cluster_mean_brier":{
                str(s):v for s,v in zip(HELD,cluster)},
            "model_inference_cpu_ns":time.process_time_ns()-now}

def params_hash(model):
    if isinstance(model,AdamRecurrent):
        return sha(b"".join(x.tobytes() for x in model.params()))
    if isinstance(model,Logistic):
        return sha(model.w.tobytes()+model.b.tobytes())
    return sha(canon([[list(k),v[0],v[1].tolist()]
                    for k,v in model.table.items()]).encode())

def source_test(source_name,source_path):
    training,train_receipts=episodes(source_path,source_name,TRAIN)
    all_models={}
    times={}
    for key,instance in [
        ("memoryless_logistic",Logistic(False,PARAMS)),
        ("two_step_history_logistic",Logistic(True,PARAMS)),
        ("bayesian_current_counts",Counts(False)),
        ("symbolic_two_step_history",Counts(True))]:
        start=time.process_time_ns()
        instance.fit(training)
        times[key]=time.process_time_ns()-start
        all_models[key]=instance
    rn,rn_receipt=fit_adam(AdamRecurrent,training)
    ff,ff_receipt=fit_adam(FeedforwardAdam,training)
    all_models["trained_recurrent_adam"]=rn
    all_models["separately_trained_nonrecurrent_adam"]=ff
    times["trained_recurrent_adam"]=rn_receipt["both_init_full_training_cpu_ns"]
    times["separately_trained_nonrecurrent_adam"]=ff_receipt["both_init_full_training_cpu_ns"]
    log_train=mean_episode_brier(all_models["memoryless_logistic"],training)[0]
    initialized=min(x["initial_training_brier"]
                    for x in rn_receipt["all_frozen_training_initializations"])
    adequacy=(rn_receipt["selected_train_seed_mean_brier"]<=log_train+.01
              and rn_receipt["selected_train_seed_mean_brier"]<=initialized*.75)
    # No helddevelopment source original episode or label exists until here:
    sealed={name:params_hash(model) for name,model in all_models.items()}
    held,held_receipts=episodes(source_path,source_name,HELD)
    scored={name:evaluate(name,model,held) for name,model in all_models.items()}
    scored["history_same_weights_zeroed"]=evaluate(
        "two_step_history_logistic",all_models["two_step_history_logistic"],held,True)
    scored["recurrent_same_weights_hidden_destroyed"]=evaluate(
        "trained_recurrent_adam",rn,held,True)
    for name,model in all_models.items():
        if params_hash(model)!=sealed[name]:
            raise ValueError("MR34H_HELD_DEVELOPMENT_EVALUATION_WEIGHT_LEAK")
    def avg(name):
        return scored[name]["proper_held_source_action_weighted_brier"]
    current=("memoryless_logistic","bayesian_current_counts",
             "separately_trained_nonrecurrent_adam")
    strongest=min(current,key=lambda c:(avg(c),c))
    delta=avg(strongest)-avg("trained_recurrent_adam")
    ablation_damage=avg("recurrent_same_weights_hidden_destroyed")-avg("trained_recurrent_adam")
    wins=sum(scored["trained_recurrent_adam"]["held_reset_seed_cluster_mean_brier"][str(s)]<
         scored[strongest]["held_reset_seed_cluster_mean_brier"][str(s)]
         for s in HELD)
    go=adequacy and delta>=.003 and wins>=8 and ablation_damage>=.001
    return {
        "original_exact_source_sha":SOURCES[source_name][0],
        "source_training_episode_count":len(training),
        "source_evaluation_episode_count":len(held),
        "native_original_training_actions":sum(len(e) for e in training),
        "native_original_held_actions":sum(len(e) for e in held),
        "train_original_action_consequence_sha256":sha(canon(train_receipts).encode()),
        "eval_original_action_consequence_sha256":sha(canon(held_receipts).encode()),
        "training_source_original_episode_receipts":train_receipts,
        "held_source_original_episode_receipts":held_receipts,
        "all_model_pre_eval_sha256":sealed,
        "training_only_recurrent_evidence":rn_receipt,
        "training_only_nonrecurrent_evidence":ff_receipt,
        "training_seed_mean_current_only_logistic_brier":log_train,
        "precommitted_recurrent_training_adequacy_reproduced":bool(adequacy),
        "prospective_model_helddevelopment_scores":scored,
        "strongest_current_only_control_helddevelopment":strongest,
        "full_rnn_held_brier_improvement_vs_best_current":delta,
        "independent_original_held_seed_recurrent_wins":wins,
        "recurrent_same_weight_memory_ablation_brier_damage":ablation_damage,
        "precommitted_helddevelopment_recurrent_history_GO":bool(go),
        "per_model_training_cpu_ns_including_all_candidates":times,
        "retained_model_checkpoint_bytes":{
            name:model.checkpoint_bytes() for name,model in all_models.items()},
        "source_public_raw_frame_bytes_processed_by_original_steps":int(
            sum(len(e) for e in training+held)*np.prod(SOURCES[source_name][1])*2),
        "recurrent_state_8_float64_bytes_in_process_proxy":
            sum(len(e) for e in held)*LATENT*8,
        "all_weights_frozen_before_held_source_evaluation":True
    }

def main(farama,pycolab):
    cfg=contract()
    roots={
        "FaramaMiniGridDoorKey8":verify_source(farama,SOURCES["FaramaMiniGridDoorKey8"][0]),
        "DeepMindPycolabApprehend":verify_source(
            pycolab,SOURCES["DeepMindPycolabApprehend"][0])}
    sys.path.insert(0,str(roots["FaramaMiniGridDoorKey8"]))
    sys.path.insert(0,str(roots["DeepMindPycolabApprehend"]))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    now=time.process_time_ns()
    out={name:source_test(name,roots[name]) for name in SOURCES}
    for name,root in roots.items():
        verify_source(root,SOURCES[name][0])
    go=all(z["precommitted_helddevelopment_recurrent_history_GO"]
           for z in out.values())
    print("MR34H_ORIGINAL_RECURRENT_HELD_GENERALIZATION="+canon({
        "precode_frozen_protocol_sha256":sha(FROZEN.read_bytes()),
        "authentic_independent_source_results":out,
        "frozen_two_source_development_generalization_GO":bool(go),
        "source_all_controls_total_process_cpu_ns":time.process_time_ns()-now,
        "source_all_controls_total_peak_os_rss_bytes":peak_rss(),
        "physical_network_communication_bytes":0,
        "resource_matched_conventional_architectures":"NOT_ESTABLISHED",
        "all_public_sensor_access_original_equivalent":True,
        "helddevelopment_original_sources_created_after_all_models_frozen":True,
        "protected_independent_scientific_first_use_consumed":False,
        "new_yggdrasil_cognitive_model_trained":False,
        "unfamiliar_independent_source_task_transfer":"NOT_TESTED",
        "G29_source_bound_atlas_and_full_regressions":"FAIL_CLOSED",
        "scientific_admission":"NO_GO"}))
if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.mr34h.generalization FARAMA PYCOLAB")
    main(sys.argv[1],sys.argv[2])
