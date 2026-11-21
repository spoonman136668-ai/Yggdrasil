"""Fixture-only matched prequential scoring; never opens reserved sources."""
from __future__ import annotations
import math
import time
from num05 import NumericRegimeMemory, canonical, digest, error, target
from num05_dev import CellHistory, KNNHistory, RidgeHistory, ZeroPredictor
from bayesian_filter import BayesianTwoBank, HYPER_GRID
from bocpd import ExactArchiveBOCPD
from numerical_source import EPISODES, FIXTURES, fixture_world

ARM_NAMES=("candidate","two_bank_bayes","runlength_bocpd","single_bank",
           "cell_full","cell_recent40","cell_recent80","knn_full",
           "knn_recent80","ridge_full","zero_sham")


def _new(name, params):
    if name=="candidate":
        return NumericRegimeMemory()
    if name=="single_bank":
        return NumericRegimeMemory(single_bank=True)
    if name in ("two_bank_bayes","runlength_bocpd"):
        if params not in HYPER_GRID:
            raise ValueError("NUM06_HYPERPARAM_NOT_FROZEN_GRID")
        cls=BayesianTwoBank if name=="two_bank_bayes" else ExactArchiveBOCPD
        return cls(hazard=params[0],noise_sigma=params[1],prior_std=params[2])
    factories={"cell_full":CellHistory,"cell_recent40":lambda:CellHistory(window=40),
               "cell_recent80":lambda:CellHistory(window=80),"knn_full":KNNHistory,
               "knn_recent80":lambda:KNNHistory(window=80),"ridge_full":RidgeHistory,
               "zero_sham":ZeroPredictor}
    return factories[name]()


def _predict(m,r):
    if isinstance(m,NumericRegimeMemory):
        return m.forecast(r["observation"],r["action"])
    return m.predict(r["observation"],r["action"])


def _cold(m,name,params,rows,next_row):
    before=_predict(m,next_row)
    if hasattr(m,"checkpoint"):
        raw=m.checkpoint()
        restored=type(m).restore(raw,digest(raw))
        exact=restored.checkpoint()==raw
        size=len(raw)
        representation="native_checkpoint_bytes"
    else:
        # Existing conventional controls store observed rows only (or no state).
        # Cold rebuild uses exactly that same witnessed prefix, never future data.
        state=vars(m)
        raw=canonical(state)
        restored=_new(name,params)
        for r in rows:
            restored.observe(r)
        exact=canonical(vars(restored))==raw
        size=len(raw)
        representation="canonical_control_state_bytes"
    return restored,exact and _predict(restored,next_row)==before,size,representation


def score_arm_fixture(seed,name,params=(.02,.04,.5)):
    # Fresh identical source packet stream for each arm. The learner API only
    # receives public observations/action and then the actual public witness.
    rows,meta=fixture_world(seed)
    if name not in ARM_NAMES:
        raise ValueError("NUM06_UNKNOWN_ARM")
    t1,t2=meta["t1"],meta["t2"]
    model=_new(name,params)
    late,back,all_errors=[],[],[]
    old1=old2=None
    recalled=0
    peak_novel=0.
    cold_exact=False
    cold_bytes=0
    cold_representation=None
    spent_predict=spent_observe=spent_cold=0
    for i,r in enumerate(rows):
        if i==t1 and name=="candidate":
            old1=model.info()["old_bank_sha256"]
        if i==t2:
            if name=="candidate":
                old2=model.info()["old_bank_sha256"]
            started=time.process_time_ns()
            model,cold_exact,cold_bytes,cold_representation=_cold(model,name,params,rows[:i],r)
            spent_cold+=time.process_time_ns()-started
        if name=="candidate" and i>=EPISODES-48:
            recalled+=int(model.active==0)
        tick=time.process_time_ns()
        forecast=_predict(model,r)
        spent_predict+=time.process_time_ns()-tick
        if len(forecast)!=3 or not all(math.isfinite(x) for x in forecast):
            raise ValueError("NUM06_BAD_FORECAST")
        loss=error(forecast,target(r))
        all_errors.append(loss)
        if t1+80<=i<t2:
            late.append(loss)
        if t2+32<=i<EPISODES:
            back.append(loss)
        tick=time.process_time_ns()
        model.observe(r)
        spent_observe+=time.process_time_ns()-tick
        if i>=100 and name in ("two_bank_bayes","runlength_bocpd"):
            mass=(model.posterior[1] if name=="two_bank_bayes"
                  else model.info()["novel_posterior"])
            peak_novel=max(peak_novel,mass)
    mean=lambda x:sum(x)/len(x)
    result={"name":name,"source_sha256":digest(canonical(rows)),"witness_count":len(rows),
            "late_count":len(late),"return_count":len(back),"full_mse":mean(all_errors),
            "late_mse":mean(late),"return_mse":mean(back),
            "pooled_mse":(mean(late)+mean(back))/2,
            "cold_exact":cold_exact,"cold_bytes":cold_bytes,"state_representation":cold_representation,
            "final_state_bytes":len(model.checkpoint()) if hasattr(model,"checkpoint") else len(canonical(vars(model))),
            "predict_cpu_ns":spent_predict,"observe_cpu_ns":spent_observe,"cold_cpu_ns":spent_cold,
            "peak_rss_bytes":None,"resource_qualification":False,
            "source_owner_authenticated":False,"scientific_gain_verified":False}
    if name=="candidate":
        result.update(old_bank_retained=old1==old2,old_bank_hash_t1=old1,old_bank_hash_t2=old2,
                      old_bank_last48_fraction=recalled/48,bank_count=len(model.banks))
    if name in ("two_bank_bayes","runlength_bocpd"):
        result["peak_novel_posterior_after_warmup"]=peak_novel
    return result


def score_fixture_suite(seed):
    if type(seed) is not int or seed not in FIXTURES:
        raise ValueError("NUM06_RESERVED_SCORING_DENIED")
    arms=[score_arm_fixture(seed,name) for name in ARM_NAMES]
    if len({a["source_sha256"] for a in arms})!=1 or any(a["witness_count"]!=448 for a in arms):
        raise ValueError("NUM06_EXPOSURE_MISMATCH")
    c=arms[0]
    best=min(arms[1:],key=lambda a:a["pooled_mse"])
    gap=best["pooled_mse"]-c["pooled_mse"]
    return {"schema":"yggdrasil.num06.fixture-scoring.v1","classification":"FIXTURE_ONLY",
            "arms":arms,"best_control":best["name"],"pooled_gap":gap,
            "threshold_checks_only":{"absolute_margin":gap>=.005,
                 "relative_margin":best["pooled_mse"]>0 and gap/best["pooled_mse"]>=.1,
                 "late_guard":c["late_mse"]<=min(a["late_mse"] for a in arms[1:])+.01,
                 "return_guard":c["return_mse"]<=min(a["return_mse"] for a in arms[1:])+.01,
                 "retention":c["old_bank_retained"],"recall":c["old_bank_last48_fraction"]>=.8,
                 "cold_exact":all(a["cold_exact"] for a in arms)},
            "null":FIXTURES[seed][2],
            "null_checks_only":({"candidate_single_bank":c["bank_count"]==1,
                "bayes_no_false_novel":all(a["peak_novel_posterior_after_warmup"]<=.8
                   for a in arms if "peak_novel_posterior_after_warmup" in a)}
                if FIXTURES[seed][2] else None),
            "registered_cohorts_consumed":0,"source_owner_authenticated":False,
            "resource_qualification":False,"scientific_gain_verified":False}
