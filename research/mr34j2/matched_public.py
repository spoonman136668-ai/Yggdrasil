"""MR34J2 frozen prospective source-development parameter-matched representation test.

Only new development seeds. Reuses unmodified MR34J1 authentic source collection,
Unicode public bridge and exact optimizer. All fitting and geometry are locked
before the first genuine held original source action.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import platform
import random
import sys
import time

import numpy as np

from research.mr34j1.public_information import (
    source_cohort,fit_codebook,public_codepoints,onehot_public,train_logistic,
    sigmoid,brier,sha,canon,peak_rss,source_original_git_readonly,UPSTREAM_SHA
)

SCHEMA="mass.mr34j2.original-public-capacity-matched-transfer-dev.v1"
FIRST="789f122b92c8cc2ae644154daeafb135a27d1045"
PARENT="a8b81e674b6d583549a5c80bede3a4ee5998665f"
FIT=(2801,2803,2819,2833,2837,2843,2851,2857,
     2861,2879,2887,2897,2903,2909,2917,2927)
HELD=(2953,2957,2963,2969,2971,2999,3001,3011)
STREAMS=(0,1)
CODEPAIRS=((-1.,-1.),(-1.,0.),(-1.,1.),(1.,-1.),(1.,0.),(1.,1.))
ORDER_A=(0,1,2,3,4)
ORDER_B=(2,4,0,3,1)
GAIN=.005
WINS=6
BOOT_DRAWS=4096
LOGISTIC_NAMES=(
    "pooled23_original","pooled23_FIT_standardized",
    "symbol23_coordinates_A","symbol23_coordinates_B",
    "categorical_onehot_full_reference","source_action_only23"
)
ALL_NAMES=LOGISTIC_NAMES+("fit_global_beta_prior",)
MATCHED_NAMES=(
    "pooled23_original","pooled23_FIT_standardized",
    "symbol23_coordinates_A","symbol23_coordinates_B",
    "source_action_only23"
)


def exact_public_symbols(frame,action,book,assignment):
    """Nine injective 2-D categorical symbols + 5 public legal actions = 23."""
    if len(book)>5 or not book:
        raise ValueError("MR34J2_FIT_ONLY_SYMBOL_ALPHABET_TOO_LARGE")
    codes=public_codepoints(frame)
    code_to_loc={c:CODEPAIRS[assignment[i]] for i,c in enumerate(book)}
    out=np.zeros(23,dtype=np.float64)
    for i,c in enumerate(codes):
        out[2*i:2*i+2]=code_to_loc.get(c,CODEPAIRS[5])
    if not 0<=action<5:
        raise ValueError("MR34J2_ORIGINAL_SOURCE_ACTION_NOT_LEGAL")
    out[18+action]=1.
    return out


def source_design(data,book,mean,scale):
    tensors={name:[] for name in LOGISTIC_NAMES}
    outcomes=[]
    roles=[]
    oov=0
    bookset=set(book)
    for seed,stream,ep in data:
        for row in ep:
            raw=np.asarray(row["public23"],dtype=np.float64)
            if raw.shape!=(23,) or not np.isfinite(raw).all():
                raise ValueError("MR34J2_ORIGINAL_SOURCE_POOLED_INPUT_INVALID")
            action=int(row["action"])
            codes=public_codepoints(row["public36"])
            oov+=sum(c not in bookset for c in codes)
            actiononly=np.zeros(23,dtype=np.float64)
            actiononly[18+action]=1.
            tensors["pooled23_original"].append(raw)
            tensors["pooled23_FIT_standardized"].append((raw-mean)/scale)
            tensors["symbol23_coordinates_A"].append(
                exact_public_symbols(row["public36"],action,book,ORDER_A))
            tensors["symbol23_coordinates_B"].append(
                exact_public_symbols(row["public36"],action,book,ORDER_B))
            tensors["categorical_onehot_full_reference"].append(
                onehot_public(row["public36"],action,book))
            tensors["source_action_only23"].append(actiononly)
            outcomes.append(np.asarray(row["target8"],dtype=np.float64))
            roles.append((seed,stream))
    X={name:np.ascontiguousarray(np.vstack(items),dtype=np.float64)
       for name,items in tensors.items()}
    y=np.ascontiguousarray(np.vstack(outcomes),dtype=np.float64)
    if (y.shape!=(len(roles),8) or not np.isfinite(y).all()
        or not np.all((y==0)|(y==1))):
        raise ValueError("MR34J2_GENUINE_ORIGINAL_EIGHT_TARGET_INVALID")
    if any(x.shape[1]!=23 for n,x in X.items() if n in MATCHED_NAMES):
        raise ValueError("MR34J2_MATCHED_PUBLIC_FEATURE_COUNT_NOT_23")
    return X,y,roles,oov


def fit_statistics(data):
    raw=np.ascontiguousarray(np.vstack([r["public23"] for _,_,ep in data for r in ep]),
                             dtype=np.float64)
    if raw.shape[1]!=23:
        raise ValueError("MR34J2_ORIGINAL_PUBLIC_POOLED_INPUT_CHANGED")
    means=np.mean(raw,axis=0)
    deviations=np.std(raw,axis=0)
    scale=np.where(deviations==0.,1.,deviations)
    if not (np.isfinite(means).all() and np.isfinite(scale).all()):
        raise ValueError("MR34J2_FIT_ONLY_NORMALIZATION_NONFINITE")
    return means,scale


def original_held_scores(X,y,roles,models,prior):
    outputs={}
    infer_cpu={}
    infer_wall={}
    for name in ALL_NAMES:
        started_wall=time.perf_counter_ns()
        started_cpu=time.process_time_ns()
        if name=="fit_global_beta_prior":
            prediction=np.tile(prior,(len(y),1))
        else:
            w,b=models[name]
            prediction=sigmoid(X[name]@w+b)
        cpu=time.process_time_ns()-started_cpu
        wall=time.perf_counter_ns()-started_wall
        infer_cpu[name]=cpu if cpu>0 else None
        infer_wall[name]=wall
        if prediction.shape!=y.shape or not np.isfinite(prediction).all():
            raise ValueError("MR34J2_ORIGINAL_HELD_PREDICTION_SHAPE_INVALID")
        by_seed={}
        by_stream={}
        for seed in HELD:
            parts=[]
            for stream in STREAMS:
                idx=[i for i,(s,z) in enumerate(roles) if s==seed and z==stream]
                if not idx:
                    raise ValueError("MR34J2_ORIGINAL_HELD_SEED_STREAM_MISSING")
                score=brier(prediction[idx],y[idx])
                by_stream[f"{seed}:{stream}"]=score
                parts.append(score)
            by_seed[str(seed)]=float(np.mean(parts))
        outputs[name]={
            "source_HELD_mean_eight_independent_seed_Brier":float(np.mean(list(by_seed.values()))),
            "genuine_original_held_seed_cluster_Brier":by_seed,
            "genuine_original_held_source_stream_Brier":by_stream,
            "total_original_public_action_targets_scored":len(y)
        }
    return outputs,infer_cpu,infer_wall


def bootstrap_paired_best_pooled_delta(scores,symbol,index):
    """Bootstrap independent reset clusters, not the correlated actor streams."""
    diffs=[]
    for seed in HELD:
        s=str(seed)
        pooled_best=min(
            scores["pooled23_original"]["genuine_original_held_seed_cluster_Brier"][s],
            scores["pooled23_FIT_standardized"]["genuine_original_held_seed_cluster_Brier"][s])
        symbolic=scores[symbol]["genuine_original_held_seed_cluster_Brier"][s]
        diffs.append(float(pooled_best-symbolic))
    random_source=random.Random(341200+index)
    draws=[]
    for _ in range(BOOT_DRAWS):
        draws.append(sum(diffs[random_source.randrange(len(diffs))]
                         for _ in range(len(diffs)))/len(diffs))
    draws.sort()
    return {
        "deterministic_cluster_bootstrap_seed":341200+index,
        "independent_actual_reset_cluster_count":len(diffs),
        "draws":BOOT_DRAWS,
        "2p5th_percentile_paired_gain":draws[int(.025*BOOT_DRAWS)],
        "seedwise_best_of_two_pooled_minus_symbol_Brier":diffs
    }


def fixed_verdict(scores):
    def av(k):return scores[k]["source_HELD_mean_eight_independent_seed_Brier"]
    bench=min(av("pooled23_original"),av("pooled23_FIT_standardized"))
    reference=av("fit_global_beta_prior")
    results={}
    for i,name in enumerate(("symbol23_coordinates_A","symbol23_coordinates_B")):
        positive_seed_count=sum(
            scores[name]["genuine_original_held_seed_cluster_Brier"][str(s)]<
            min(scores["pooled23_original"]["genuine_original_held_seed_cluster_Brier"][str(s)],
                scores["pooled23_FIT_standardized"]["genuine_original_held_seed_cluster_Brier"][str(s)])
            for s in HELD
        )
        gain=bench-av(name)
        paired=bootstrap_paired_best_pooled_delta(scores,name,i)
        passed=bool(gain>=GAIN and positive_seed_count>=WINS
                    and av(name)<reference
                    and paired["2p5th_percentile_paired_gain"]>0)
        results[name]={
            "frozen_source_representation_matched_gain_Brier":gain,
            "paired_genuine_original_reset_seed_wins_vs_both_pooled":positive_seed_count,
            "strict_cluster_bootstrap":paired,
            "frozen_matched_capacity_source_DEV_screen_pass":passed,
            "native_original_model_promoted":False
        }
    return results,all(v["frozen_matched_capacity_source_DEV_screen_pass"]
                       for v in results.values())


def run(original_source,output):
    original=Path(original_source).resolve()
    source_original_git_readonly(original)
    sys.path.insert(0,str(original))
    all_started=time.process_time_ns()
    fit,fit_receipt=source_cohort(original,FIT,"genuine_original_third_public_capacity_FIT")
    book=fit_codebook(fit)
    if len(book)>5:
        raise ValueError("MR34J2_PRECOMMITTED_MAX_FIVE_SOURCE_CODEPOINTS_EXCEEDED")
    mean,scale=fit_statistics(fit)
    start_feature=time.process_time_ns()
    FIT_X,FIT_y,_,FIT_oov=source_design(fit,book,mean,scale)
    fit_feature_cpu=time.process_time_ns()-start_feature
    if FIT_oov!=0:
        raise ValueError("MR34J2_FIT_SOURCE_SYMBOL_OUTSIDE_ITS_OWN_ALPHABET")
    models={}
    train={}
    for name in LOGISTIC_NAMES:
        models[name],train[name]=train_logistic(FIT_X[name],FIT_y)
        if name in MATCHED_NAMES and train[name]["native_float64_coefficient_checkpoint_bytes"]!=1536:
            raise ValueError("MR34J2_MATCHED_FIT_PARAMETER_BYTES_CHANGED")
    prior=(np.sum(FIT_y,axis=0)+1.)/(len(FIT_y)+2.)
    train["fit_global_beta_prior"]={
        "checkpoint_SHA256":sha(prior.tobytes()),
        "native_float64_coefficient_checkpoint_bytes":prior.nbytes,
        "source_fit_CPU_ns":0,
        "original_source_fitted_example_count":len(FIT_y)
    }
    seal={name:train[name]["checkpoint_SHA256"] for name in ALL_NAMES}
    stats_sha=sha(mean.tobytes()+scale.tobytes())
    # Original HELD source cannot be reset before models/stats/source FIT seal.
    cpu_before_held=time.process_time_ns()-all_started
    held,held_receipt=source_cohort(original,HELD,"genuine_original_third_public_capacity_HELD")
    started_feature=time.process_time_ns()
    X,y,roles,held_oov=source_design(held,book,mean,scale)
    held_feature_cpu=time.process_time_ns()-started_feature
    scores,infer_cpu,infer_wall=original_held_scores(X,y,roles,models,prior)
    for name,(w,b) in models.items():
        if sha(w.tobytes()+b.tobytes())!=seal[name]:
            raise ValueError("MR34J2_HELD_SOURCE_CAUSED_FIT_MODEL_PARAMETER_UPDATE")
    if sha(prior.tobytes())!=seal["fit_global_beta_prior"]:
        raise ValueError("MR34J2_HELD_SOURCE_FIT_GLOBAL_PRIOR_ALTERED")
    if sha(mean.tobytes()+scale.tobytes())!=stats_sha:
        raise ValueError("MR34J2_HELD_SOURCE_FIT_NORMALIZER_LEAK")
    decision,signal=fixed_verdict(scores)
    cpu_total=time.process_time_ns()-all_started
    receipt={
        "schema":SCHEMA,
        "frozen_FIRST_precode_git":FIRST,
        "exact_previous_MR34J1_negative_and_positive_parent":PARENT,
        "unchanged_independent_original_upstream_git":UPSTREAM_SHA,
        "source_original_fresh_FIT_receipt":fit_receipt,
        "source_original_fresh_HELD_receipt":held_receipt,
        "FIT_only_public_unicode_vocabulary":book,
        "FIT_only_vocabulary_source_full_Unicode_original":True,
        "FIT_only_symbol2d_coordinates":CODEPAIRS,
        "FIT_only_coordinate_assignment_original":ORDER_A,
        "FIT_only_coordinate_assignment_alternative":ORDER_B,
        "FIT_only_pooled23_mean":[float(z) for z in mean],
        "FIT_only_pooled23_scale":[float(z) for z in scale],
        "FIT_only_normalizer_SHA256":stats_sha,
        "FIT_original_public_8bit_targets_sha256":sha(FIT_y.tobytes()),
        "HELD_original_public_8bit_targets_sha256":sha(y.tobytes()),
        "FIT_original_public_features_sha256":{n:sha(z.tobytes()) for n,z in FIT_X.items()},
        "HELD_original_public_features_sha256":{n:sha(z.tobytes()) for n,z in X.items()},
        "FIT_only_original_source_train_logistic_controls":train,
        "FIT_only_original_models_all_sealed_before_HELD_reset":seal,
        "HELD_original_source_eight_seed_mean_Brier":scores,
        "HELD_original_source_frozen_matched_capacity_screen":decision,
        "HELD_original_both_symbol_assignments_development_screen_pass":signal,
        "HELD_original_source_OOV_public_cell_count":held_oov,
        "FIT_original_source_OOV_public_cell_count":FIT_oov,
        "FIT_original_source_feature_construction_CPU_ns":fit_feature_cpu,
        "HELD_original_source_feature_construction_CPU_ns":held_feature_cpu,
        "HELD_original_source_batch_prediction_CPU_ns":infer_cpu,
        "HELD_original_source_batch_prediction_wall_ns":infer_wall,
        "source_FIT_true_eight_bit_change_rate":np.mean(FIT_y,axis=0).tolist(),
        "source_HELD_true_eight_bit_change_rate":np.mean(y,axis=0).tolist(),
        "source_original_all_models_and_source_CPU_ns":cpu_total,
        "source_FIT_until_held_FIRST_reset_CPU_ns":cpu_before_held,
        "source_original_process_peak_OS_RSS_bytes":peak_rss(),
        "trainable_model_parameter_counts":{n:train[n]["native_float64_coefficient_checkpoint_bytes"]//8 for n in LOGISTIC_NAMES},
        "model_training_FLOP_proxy_fit_examples_x_input_x_outputs_x_epochs":{
            n:len(FIT_y)*FIT_X[n].shape[1]*8*200 for n in LOGISTIC_NAMES},
        "models_not_refit_on_HELD":True,
        "source_original_science_protected_first_use":False,
        "original_native_recurrent_learning_retested":False,
        "source_authored_original_model_or_project_edited":False,
        "scientific_admission":"NO_GO"
    }
    source_original_git_readonly(original)
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print("MR34J2_ORIGINAL_CAPACITY_MATCHED_SOURCE="+canon({
        "schema":SCHEMA,"os":platform.system(),"receipt_sha256":sha(path.read_bytes()),
        "FIT_source_SHA":fit_receipt["original_real_source_receipt_sha256"],
        "HELD_source_SHA":held_receipt["original_real_source_receipt_sha256"],
        "FIT_source_action_count":fit_receipt["total_genuine_source_actions"],
        "HELD_source_action_count":held_receipt["total_genuine_source_actions"],
        "vocabulary_size":len(book),
        "HELD_OOV_count":held_oov,
        "models_held_Brier":{k:v["source_HELD_mean_eight_independent_seed_Brier"]
                             for k,v in scores.items()},
        "symbol_frozen_screens":{k:{
            "gain":v["frozen_source_representation_matched_gain_Brier"],
            "seeds":v["paired_genuine_original_reset_seed_wins_vs_both_pooled"],
            "cluster_bootstrap_2p5":v["strict_cluster_bootstrap"]["2p5th_percentile_paired_gain"],
            "passed":v["frozen_matched_capacity_source_DEV_screen_pass"]
        } for k,v in decision.items()},
        "both_symbol_mapping_development_pass":signal,
        "protected_first_use":False
    }))


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.mr34j2.matched_public ORIGINAL_THIRD_SOURCE RECEIPT")
    run(*sys.argv[1:])
