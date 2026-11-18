"""WSP158: frozen two-stage source-learned calibration on consumed original DTR.

Actual original public FIT transcript is verified by unchanged WSP157 before
any learning. Unopened original DTR02 VALID/DEV and virgin source untouched.
Every historical held row was already exposed in WSP157: DEVELOPMENT ONLY.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import time
from yggdrasil.native_stage_calibration import (
    ProgrammedNativeStageCalibration,alpha_fraction,GRID_NUMERATOR,
    COMPOSITE_BYTES,ORIGINAL_NATIVE_BYTES
)

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"WSP-157"/"audit.py"
spec=importlib.util.spec_from_file_location("_wsp158_pinned_wsp157",OLD)
W=importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)
TRAIN_CAL=64
VALID_START=64
VALID_END=128
REFIT_END=192
HOLD_END=256
TARGETS=("transition","reward")
ARMS=("native_programmed","independent_calibrated","original_native_beta",
      "fitted_mle","logistic_diagnostic","chance")
TOL=Fraction(1,1000000000000)

def require(v,msg):
    if not v:
        raise ValueError("WSP158_"+msg)

def validate_fit_valid(fit,valid):
    require(type(fit) is tuple and type(valid) is tuple
            and len(fit)==TRAIN_CAL and len(valid)==VALID_END-VALID_START,
            "FIT_VALID_COUNT")
    require(all(type(x) is dict for x in fit+valid),"PUBLIC_ROW_TYPE")
    seeds=[x["seed"] for x in fit+valid]
    base=seeds[0]
    require(base in (1100000,1110000,1120000) and
            seeds==list(range(base,base+VALID_END)),"FIT_VALID_SEED_CUSTODY")
    require(all(set(x)=={"seed","s1","x1","s2","x2","y"} and
                all(type(x[f]) is int and x[f] in (0,1)
                    for f in ("s1","x1","s2","x2","y"))
                for x in fit+valid),"PUBLIC_BINARY_SOURCE_ONLY")

def _independent_counts(rows):
    # Deliberately independent of the native counters and WSP157 batch class.
    c={}
    for r in rows:
        for stage in TARGETS:
            if stage=="transition":
                key=(stage,r["s1"],r["x1"])
                truth=r["s2"]
            else:
                key=(stage,2+4*r["s1"]+2*r["x1"]+r["s2"],r["x2"])
                truth=r["y"]
            old=c.get(key,(0,0))
            c[key]=(old[0]+int(truth==0),old[1]+int(truth==1))
    return c

def _independent_p(counts,row,target,index):
    if target=="transition":
        key=(target,row["s1"],row["x1"])
    else:
        key=(target,2+4*row["s1"]+2*row["x1"]+row["s2"],row["x2"])
    failures,successes=counts.get(key,(0,0))
    if failures+successes==0:
        return Fraction(1,2)
    a=alpha_fraction(index)
    return (Fraction(successes)+a)/(failures+successes+2*a)

def _label(row,target):
    return row["s2"] if target=="transition" else row["y"]

def _valid_brier_independent(counts,valid,target,index):
    return sum(((_independent_p(counts,row,target,index)-_label(row,target))**2
                for row in valid),Fraction(0))

def _select_independent(fit,valid):
    counts=_independent_counts(fit)
    indices=[]
    sums=[]
    for target in TARGETS:
        rated=[(_valid_brier_independent(counts,valid,target,i),
                abs(alpha_fraction(i)-1),i)
               for i in range(len(GRID_NUMERATOR))]
        rated.sort()
        loss,_,index=rated[0]
        indices.append(index)
        sums.append(loss)
    return tuple(indices),tuple(sums)

def select_calibration(fit,valid):
    """Candidate weights chosen using ONLY FIT/VALID and original native counts."""
    validate_fit_valid(fit,valid)
    mem=W.fit_native(fit)
    snapshot=mem.snapshot()
    chosen=[]
    loss=[]
    for target in TARGETS:
        rates=[]
        for index in range(len(GRID_NUMERATOR)):
            candidate=ProgrammedNativeStageCalibration(
                snapshot,index if target=="transition" else 3,
                index if target=="reward" else 3)
            native_loss=Fraction(0)
            for row in valid:
                slot,action,truth=W.observation(row,target)
                address,retained=W.addr(slot)
                prob=candidate.probability(address,action,0 if target=="transition" else 1,
                                           retained=retained)
                native_loss+=(prob-truth)**2
            rates.append((native_loss,abs(alpha_fraction(index)-1),index))
        rated=min(rates)
        chosen.append(rated[2]);loss.append(rated[0])
    independent,ind_loss=_select_independent(fit,valid)
    require(tuple(chosen)==independent and tuple(loss)==ind_loss,
            "INDEPENDENT_VALID_SELECTION_PARITY")
    require(mem.snapshot()==snapshot,"CALIBRATION_MUTATED_NATIVE_FIT")
    return tuple(chosen),tuple(loss)

def _fraction_brier(score,truth):
    return (score-truth)**2

def run():
    cpu=time.process_time()
    sources=W.read_original_fit()
    summaries=[]
    total={arm:{"transition":Fraction(0),"reward":Fraction(0)}
           for arm in ARMS if arm!="logistic_diagnostic"}
    floats={"transition":0.,"reward":0.}
    score_digest=[]
    programs=[]
    all_fit_usages=[]
    for rid,source in enumerate(sources):
        require(len(source)==256 and
                source[0]["seed"]==1100000+10000*rid and
                source[-1]["seed"]==1100255+10000*rid,
                "ORIGINAL_REPLICA_IDENTITY")
        fit,valid=tuple(source[:TRAIN_CAL]),tuple(source[VALID_START:VALID_END])
        params,selection_loss=select_calibration(fit,valid)
        require(params==_select_independent(fit,valid)[0],"PARAMETER_CUSTODY")
        history=tuple(source[:REFIT_END])
        model=W.fit_native(history)
        original_bytes=model.snapshot()
        candidate=ProgrammedNativeStageCalibration(original_bytes,*params)
        cold=ProgrammedNativeStageCalibration.restore(candidate.checkpoint())
        require(candidate.checkpoint()==cold.checkpoint() and
                original_bytes==cold.native_checkpoint() and
                len(cold.checkpoint())==COMPOSITE_BYTES and
                len(original_bytes)==ORIGINAL_NATIVE_BYTES,
                "COLD_INHERITED_NATIVE_BYTE_PARITY")
        counts=_independent_counts(history)
        old_counts=W.independent_fits(history)
        logistic={target:W.logistic_fit(history,target)
                  for target in TARGETS}
        per={arm:{"transition":Fraction(0),"reward":Fraction(0)}
             for arm in ARMS if arm!="logistic_diagnostic"}
        per_logistic={"transition":0.,"reward":0.}
        for row in source[REFIT_END:HOLD_END]:
            for target in TARGETS:
                slot,action,truth=W.observation(row,target)
                address,retained=W.addr(slot)
                stage=0 if target=="transition" else 1
                p=cold.probability(address,action,stage,retained=retained)
                counterpart=_independent_p(counts,row,target,params[stage])
                require(p==counterpart,"FROZEN_NATIVE_CALIBRATED_PARITY")
                a,b=W.native_prob(model,row,target)
                baseline=Fraction(a,b)
                require(baseline==_independent_p(counts,row,target,3),
                        "ORIGINAL_NATIVE_BETA_PARITY")
                old_mle=W.mle(old_counts,row,target)
                # Explicit independent table fractional MLE; ensure source-match.
                mle=_independent_p(counts,row,target,0)
                require(abs(float(mle)-old_mle)<1e-12,"MATRCHED_MLE_PARITY")
                probs={
                    "native_programmed":p,
                    "independent_calibrated":counterpart,
                    "original_native_beta":baseline,
                    "fitted_mle":mle,
                    "chance":Fraction(1,2)}
                for arm,pred in probs.items():
                    err=_fraction_brier(pred,truth)
                    total[arm][target]+=err
                    per[arm][target]+=err
                lp=W.logistic_prob(logistic[target][0],row,target)
                e=(lp-truth)**2
                floats[target]+=e
                per_logistic[target]+=e
                score_digest.append([rid,row["seed"],stage,
                                     p.numerator,p.denominator,
                                     mle.numerator,mle.denominator,
                                     truth])
        require(per["native_programmed"]==per["independent_calibrated"],
                "INDEPENDENT_SOURCE_PREDICTION_PARITY")
        report={
            "replica":rid,"fit_episode_range":[0,63],
            "valid_episode_range":[64,127],
            "refit_episode_range":[0,191],
            "held_historical_original_range":[192,255],
            "chosen_pseudocount_indices":list(params),
            "chosen_pseudocounts":[str(alpha_fraction(x)) for x in params],
            "validation_brier":[round(float(x/64),12) for x in selection_loss],
            "original_native_checkpoint_sha256":W.sha(original_bytes),
            "programmed_checkpoint_sha256":W.sha(cold.checkpoint()),
            "conventional_logistic":{"transition":logistic["transition"][1],
                                     "reward":logistic["reward"][1]},
            "held":{arm:{"transition":round(float(loss["transition"]/64),12),
                         "reward":round(float(loss["reward"]/64),12),
                         "pooled":round(float(
                             (loss["transition"]+loss["reward"])/128),12)}
                    for arm,loss in per.items()},
            "logistic_held":{"transition":round(per_logistic["transition"]/64,12),
                             "reward":round(per_logistic["reward"]/64,12),
                             "pooled":round(sum(per_logistic.values())/128,12)}
        }
        summaries.append(report)
        programs.append([rid,params,W.sha(cold.checkpoint())])
        all_fit_usages.append([rid,history[0]["seed"],history[-1]["seed"],source[192]["seed"],source[255]["seed"]])
    require(len(score_digest)==384 and
            len(all_fit_usages)==3,"HELD_FORECAST_COUNT")
    require(total["native_programmed"]==total["independent_calibrated"],
            "AGGREGATE_SOURCE_EQUAL_CALIBRATION_TIE")
    summary={}
    for arm,group in total.items():
        summary[arm]={"transition":round(float(group["transition"]/192),12),
                      "reward":round(float(group["reward"]/192),12),
                      "pooled":round(float(sum(group.values())/384),12)}
    summary["logistic_diagnostic"]={
        "transition":round(floats["transition"]/192,12),
        "reward":round(floats["reward"]/192,12),
        "pooled":round(sum(floats.values())/384,12)}
    require(summary["native_programmed"]==summary["independent_calibrated"],
            "AGGREGATE_BRIER_COLD_MISMATCH")
    gap=round(summary["fitted_mle"]["pooled"]-
              summary["native_programmed"]["pooled"],12)
    transition_degrade=round(summary["native_programmed"]["transition"]-
                             summary["fitted_mle"]["transition"],12)
    positive=gap>=0.005 and transition_degrade<=0.002
    result={
        "schema":"wsp158.authentic-original-public-DTR-learned-stage-calibration-result.v1",
        "classification":"DEVELOPMENT_CALIBRATION_GAIN_VS_MLE" if positive
                          else "DEVELOPMENT_NATIVE_CALIBRATION_NO_GO",
        "frozen_historical_prior_exposure":True,
        "development_only":True,"source_first_use":False,
        "scientific_pass":False,"new_original_actions":0,
        "original_source_family":"original DTRPCH previously consumed FIT only",
        "original_source_episodes":768,"replicas":3,
        "fit_per_replica":64,"valid_per_replica":64,
        "refit_per_replica":192,"held_historical_per_replica":64,
        "forecast_targets_per_arm":384,
        "original_native_checkpoint_bytes":ORIGINAL_NATIVE_BYTES,
        "programmed_checkpoint_bytes":COMPOSITE_BYTES,
        "alpha_grid":["0","1/4","1/2","1","2"],
        "per_replica":summaries,"pooled_Brier":summary,
        "gain_over_fitted_mle":gap,
        "transition_degradation_vs_mle":transition_degrade,
        "independent_calibrated_control_exact_tie":True,
        "source_trace_receipt_sha256":W.sha(W.canonical(all_fit_usages)),
        "checkpoint_programs_sha256":W.sha(W.canonical(programs)),
        "held_development_prediction_trace_sha256":W.sha(W.canonical(score_digest)),
        "preregistered_gain_threshold":0.005,
        "preregistered_max_transition_degradation":0.002,
        "all_models_fit_same_192_original_public_events_per_replica":True,
        "new_original_source_actions":0,"native_original_file_edited":False,
        "accepted_main_mutated":False,"protected_first_use":False,
        "unfamiliar_world_transfer":False
    }
    return result,W.sha(W.canonical(result)),{"cpu_s":round(time.process_time()-cpu,6)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    opts=ap.parse_args()
    result,digest,resource=run()
    if opts.out:
        opts.out.parent.mkdir(parents=True,exist_ok=True)
        opts.out.write_text(json.dumps({**result,"semantic_sha256":digest,
                                        "diagnostic":resource},
                                        indent=2,sort_keys=True)+"\n")
    print("WSP158_SEMANTIC_SHA256="+digest,flush=True)
    print("WSP158_RESULT="+json.dumps({
        "classification":result["classification"],
        "pooled_Brier":result["pooled_Brier"],
        "per_replica_alpha":[r["chosen_pseudocounts"]
                             for r in result["per_replica"]],
        "gain_over_fitted_mle":result["gain_over_fitted_mle"],
        "transition_degradation_vs_mle":result["transition_degradation_vs_mle"],
        "logistic_training":[x["conventional_logistic"]
                             for x in result["per_replica"]],
        "cpu_s":resource["cpu_s"],"new_original_actions":0
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
