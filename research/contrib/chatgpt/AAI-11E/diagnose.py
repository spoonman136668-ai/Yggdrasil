"""AAI-11E: evaluator-only posterior calibration and risk-suppression diagnosis.

The AAI-11D learner, original MAP control, training and planner are imported
UNCHANGED. True-law simulator predictions are never supplied to a learner.
Only the three original frozen mechanical fixtures may be used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE.parent/"AAI-11D"))
import world,controls,admission
import learner as graph
import calibration as source_model
import dev as source_dev

ARMS=("graph_recent8","posterior_planner","risk_calibrated_planner")
FROZEN_MEANS={"graph_recent8":2.134027778,
              "posterior_planner":2.189756944,
              "risk_calibrated_planner":2.196701389}
FROZEN_GOALS={"graph_recent8":.375,
              "posterior_planner":.40625,
              "risk_calibrated_planner":.388888889}
REPLAY_TOLERANCE=1e-6
EPS=1e-10


def digest(obj):
    return hashlib.sha256(controls.canonical(obj).encode("utf8")).hexdigest()


def public_choice(name,payload,row):
    """Cold public initial state and the original model's first ACT/STOP."""
    actor=source_dev.restored(name,payload)
    actor.observe(world.copy_public(row))
    selection=actor.choose(world.copy_public(row))
    if selection is not None and selection not in world.ACTIONS:
        raise AssertionError("unregistered intervention")
    return (-1 if selection is None else world.ACTIONS.index(selection))


def calibration_probe(name,payload,law):
    """Private scoring ONLY. No model.observe and no teacher labels to learner."""
    actor=source_dev.restored(name,payload)
    original=source_dev.frozen(name,actor)
    sums_brier=[0.,0.,0.]
    sums_nll=[0.,0.,0.]
    bins=[[{"n":0,"forecast_sum":0.,"observed_sum":0}
           for _ in range(5)] for _ in range(3)]
    readings=[]
    for x in world.INPUTS:
        p=actor.predict(x)
        truth=world.intermediates(law,x)  # PRIVILEGED evaluator only.
        for out in range(3):
            forecast=p[out]
            observed=truth[out]
            if not 0.<=forecast<=1. or not math.isfinite(forecast):
                raise AssertionError("invalid learned causal probability")
            sums_brier[out]+=(forecast-observed)**2
            bounded=max(1e-12,min(1-1e-12,forecast))
            sums_nll[out]-=observed*math.log(bounded)+(1-observed)*math.log(1-bounded)
            index=min(int(forecast*5),4)
            bin_record=bins[out][index]
            bin_record["n"]+=1
            bin_record["forecast_sum"]+=forecast
            bin_record["observed_sum"]+=observed
        readings.append(tuple(round(v,12) for v in p))
    if source_dev.frozen(name,actor)!=original:
        raise AssertionError("private evaluator mutated learned causal memory")
    return {"brier":[sum(v for v in [sums_brier[i]])/64 for i in range(3)],
            "logloss":[sums_nll[i]/64 for i in range(3)],
            "calibration_bins":bins,
            "predictions":tuple(readings)}


def probe_pair(key,law,budget,training):
    """Read-only diagnostic on the exact original frozen public challenge source."""
    world.fixture(key)
    frozen={name:source_dev.challenge(name,training[name],law,key,budget)
            for name in ARMS}
    for name,payload in frozen.items():
        if source_dev.frozen(name,source_dev.restored(name,payload))!=payload:
            raise AssertionError("modified cold challenge checkpoint")
    calibrated={name:calibration_probe(name,frozen[name],law) for name in ARMS}
    if calibrated["posterior_planner"]["predictions"]!=calibrated["risk_calibrated_planner"]["predictions"]:
        raise AssertionError("risk and posterior forecasts not identical")
    metrics=[]
    for x,goal in admission.contexts(key,law,12):
        initial=world.copy_public(world.start(law,x,goal))
        choices={name:public_choice(name,frozen[name],initial) for name in ARMS}
        results={name:source_dev.episode(name,frozen[name],law,x,goal)
                 for name in ARMS}
        if not all(results[name][0]<=world.exact_oracle(law,x,goal)+EPS
                   for name in ARMS):
            raise AssertionError("learner exceeded privileged two-step oracle")
        post=choices["posterior_planner"]
        risk=choices["risk_calibrated_planner"]
        suppression=(risk==-1 and post>=0)
        act_more=(post==-1 and risk>=0)
        replacement=(post>=0 and risk>=0 and post!=risk)
        one_gain=None
        two_gain=None
        if suppression:
            # Diagnostic counterfactual is never supplied to either learner.
            after=world.do(law,initial,world.ACTIONS[post])
            one_gain=round(after["reward"]-initial["reward"],9)
            best=after["reward"]
            for second in world.ACTIONS:
                next_row=world.do(law,after,second)
                best=max(best,next_row["reward"])
            two_gain=round(best-initial["reward"],9)
        metrics.append({
            "first_choices":[choices[name] for name in ARMS],
            "terminal_rewards":[round(results[name][0],9) for name in ARMS],
            "terminal_goals":[results[name][1] for name in ARMS],
            "action_lengths":[len(results[name][2]) for name in ARMS],
            "posterior_vs_risk_suppressed":int(suppression),
            "risk_extra_act":int(act_more),
            "different_active_first_actions":int(replacement),
            "one_step_gain_if_suppressed":one_gain,
            "best_two_step_gain_if_suppressed":two_gain,
            "oracle_reward":round(world.exact_oracle(law,x,goal),9)
        })
    for name,payload in frozen.items():
        if source_dev.frozen(name,source_dev.restored(name,payload))!=payload:
            raise AssertionError("learning source changed after private diagnostics")
    return calibrated,metrics


def mean(seq):
    if not seq:raise ValueError("empty diagnostic sequence")
    return sum(seq)/len(seq)


def run():
    p=json.loads((HERE/"prereg.json").read_text("utf8"))
    if p["id"]!="AAI-11E" or p["science"]["used"]!=0 or p["science"]["first_use_authorized"]:
        raise PermissionError("AAI11E SCIENTIFIC FIRST USE DISARMED")
    evidence=[]
    snapshots=[]
    all_calibration={name:[] for name in ARMS}
    conditions=0
    for key in world.FIXTURES:
        # Exactly original source, same public 64-row training for all arms.
        saved,training,_=source_dev.train(key)
        if len(training)!=64:
            raise AssertionError("original model training source drifted")
        snapshots.append([key,*[digest(saved[name]) for name in ARMS]])
        for law in world.TRANSFER:
            for budget in (2,4):
                calibrated,episodes=probe_pair(key,law,budget,saved)
                for name in ARMS:
                    all_calibration[name].append(calibrated[name])
                evidence.extend(episodes)
                conditions+=1
        for name in ARMS:
            if source_dev.frozen(name,source_dev.restored(name,saved[name]))!=saved[name]:
                raise AssertionError("original training checkpoint contaminated")
    if len(evidence)!=288 or conditions!=24:
        raise AssertionError("source fixture experiment count drift")
    reward={}
    goals={}
    for k,name in enumerate(ARMS):
        reward[name]=round(mean([episode["terminal_rewards"][k] for episode in evidence]),9)
        goals[name]=round(mean([episode["terminal_goals"][k] for episode in evidence]),9)
        if (abs(reward[name]-FROZEN_MEANS[name])>REPLAY_TOLERANCE or
            abs(goals[name]-FROZEN_GOALS[name])>REPLAY_TOLERANCE):
            raise AssertionError("ORIGINAL FROZEN MODEL SCORE NOT REPRODUCED")
    brier={}
    logloss={}
    calibration_hist={}
    for name in ARMS:
        groups=all_calibration[name]
        brier[name]=round(mean([v for entry in groups for v in entry["brier"]]),12)
        logloss[name]=round(mean([v for entry in groups for v in entry["logloss"]]),12)
        histogram=[]
        for out in range(3):
            combined=[]
            for bin_index in range(5):
                n=sum(g["calibration_bins"][out][bin_index]["n"] for g in groups)
                expected=sum(g["calibration_bins"][out][bin_index]["forecast_sum"] for g in groups)
                actual=sum(g["calibration_bins"][out][bin_index]["observed_sum"] for g in groups)
                combined.append({
                    "n":n,
                    "mean_predicted":round(expected/n,9) if n else None,
                    "mean_observed":round(actual/n,9) if n else None
                })
            histogram.append(combined)
        calibration_hist[name]=histogram
    if (brier["posterior_planner"]!=brier["risk_calibrated_planner"] or
        logloss["posterior_planner"]!=logloss["risk_calibrated_planner"] or
        calibration_hist["posterior_planner"]!=calibration_hist["risk_calibrated_planner"]):
        raise AssertionError("identical posterior forecasts not identical by risk arm")
    suppressed=[z for z in evidence if z["posterior_vs_risk_suppressed"]]
    one_positive=sum(z["one_step_gain_if_suppressed"]>EPS for z in suppressed)
    two_positive=sum(z["best_two_step_gain_if_suppressed"]>EPS for z in suppressed)
    replacements=sum(z["different_active_first_actions"] for z in evidence)
    unexpected=sum(z["risk_extra_act"] for z in evidence)
    reward_diffs=[z["terminal_rewards"][2]-z["terminal_rewards"][1] for z in evidence]
    if len(suppressed)>=3 and 2*two_positive>=len(suppressed):
        diagnosis="SUPPRESSION_WITH_POSITIVE_TWO_STEP_HEADROOM"
    elif replacements>=3 and replacements>len(suppressed):
        diagnosis="MOSTLY_ACTION_REPLACEMENT"
    else:
        diagnosis="LOW_POLICY_DISAGREEMENT"
    return {
        "schema":"yggdrasil.contrib.aai11e.risk-attribution.v1",
        "status":"DIAGNOSTIC_COMPLETE_NO_SCIENCE",
        "classification":diagnosis,
        "original_exact_reward_reproduced":reward,
        "original_exact_three_goal_reproduced":goals,
        "brier_probabilistic_causal_forecast":brier,
        "logloss_probabilistic_causal_forecast":logloss,
        "calibration_histogram":calibration_hist,
        "posterior_brier_improvement_over_MAP":round(brier["graph_recent8"]-brier["posterior_planner"],12),
        "posterior_logloss_improvement_over_MAP":round(logloss["graph_recent8"]-logloss["posterior_planner"],12),
        "total_shared_initial_states":len(evidence),
        "posterior_ACT_risk_STOP":len(suppressed),
        "posterior_STOP_risk_ACT":unexpected,
        "both_ACT_different_first_action":replacements,
        "risk_suppressed_one_step_helpful":one_positive,
        "risk_suppressed_two_step_helpful":two_positive,
        "mean_suppressed_actual_one_step_gain":round(mean([x["one_step_gain_if_suppressed"] for x in suppressed]),9) if suppressed else None,
        "mean_suppressed_best_two_step_gain":round(mean([x["best_two_step_gain_if_suppressed"] for x in suppressed]),9) if suppressed else None,
        "paired_risk_better":sum(z>EPS for z in reward_diffs),
        "paired_posterior_better":sum(z< -EPS for z in reward_diffs),
        "paired_equal":sum(abs(z)<=EPS for z in reward_diffs),
        "mean_risk_minus_posterior_reward":round(mean(reward_diffs),9),
        "mean_actions_by_arm":{name:round(mean([ep["action_lengths"][i] for ep in evidence]),9)
                               for i,name in enumerate(ARMS)},
        "mean_true_oracle_reward":round(mean([z["oracle_reward"] for z in evidence]),9),
        "calibration_sample_count_per_arm":len(world.INPUTS)*len(ARMS)*0+conditions*len(world.INPUTS)*3,
        "condition_count":conditions,
        "trace_sha256":digest(evidence),
        "source_checkpoint_sha256":digest(snapshots),
        "scientific_cohorts_used":0,
        "new_candidate_trained":False,
        "native_yggdrasil_modified":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mechanical-diagnostic",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:p.error("AAI11E SCIENTIFIC FIRST USE DISARMED")
    if not args.mechanical_diagnostic:
        p.error("only original frozen synthetic mechanical fixtures allowed")
    print("AAI11E_DIAGNOSTIC="+json.dumps(run(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()
