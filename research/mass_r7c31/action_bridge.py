"""C31 additive source-public action bridge to UNMODIFIED original Ygg R3.

Bridge proposes source-legal actions based on *learned predicted next front bit*
for two 90-degree turns. It executes NO source action; candidate effects are
unidentified counterfactual predictions, NOT observed alternate outcomes.
"""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from pathlib import Path

from research.native.itd02.r3.navigator import Navigator
from research.native.itd02.r1.native_policy import PublicGrid,canonical,features
from research.mass_r7c29.effects import view,data_event

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text())
THRESH=float(P["fixed_candidate_criterion"]["alternate_min_predicted_obstruction_reduction"])


def learned_source_motors(training):
    """Fit public signed physical cardinal motor only from real selected FIT moves."""
    counts={d:Counter() for d in range(4)}
    for e in training:
        state,a,y=data_event(e)
        aft=view(e["returned_after"])
        if a!=2:continue
        step=(aft.x-state.x,aft.y-state.y)
        if abs(step[0])+abs(step[1])==1:
            counts[state.direction][f"{step[0]},{step[1]}"]+=1
    if not all(counts[d] for d in range(4)):
        raise ValueError("INSUFFICIENT_AUTHENTIC_FIT_MOTOR_COVERAGE")
    return {str(d):dict(counts[d]) for d in range(4)}


def source_public_navigator(motors,family):
    shape=P["exact_public_source_dims"].get(family)
    if type(shape) is not list or len(shape)!=2:
        raise ValueError("NONFROZEN_SOURCE_FAMILY")
    nav=Navigator()
    nav.motor={str(d):dict(motors[str(d)]) for d in range(4)}
    nav.reset_episode(*shape)
    return nav


def source_sensor_update(nav,public):
    """Match the prior observed front-bit episode-memory admission before choice.

    Never query hidden tile, original environment object or future after-state.
    """
    features(public)
    edge=(public.x,public.y,public.direction)
    if public.front_blocked:
        nav.blocked.add(edge)
        nav.open_edges.discard(edge)
    else:
        nav.blocked.discard(edge)


def decision(nav,s,model):
    """Return (real R3 baseline, learned proposed action, predicted probabilities).

    Prediction of next-front status under UNCHOSEN alternative is expressly
    model speculation, not an authentic source step or causal observation.
    """
    features(s)
    if type(nav) is not Navigator or nav.width==0:
        raise ValueError("NOT_QUALIFIED_NATIVE_R3")
    baseline=nav.choose(s)
    if type(baseline) is not int or baseline not in (0,1,2):
        raise ValueError("NON_SOURCE_SELECTED_BASE_ACTION")
    if baseline not in (0,1):
        return baseline,baseline,None
    other=1-baseline
    pred_original=model.predict(s,baseline)
    pred_other=model.predict(s,other)
    if not all(0<p<1 for p in (pred_original,pred_other)):
        raise ValueError("UNVERIFIED_SELECTED_EFFECT_PROBABILITY")
    # This is an explicit fixed MYOPIC proxy. It has no value-of-information
    # utility training and no original-source counterfactual attribution.
    proposed=other if pred_original-pred_other>THRESH else baseline
    return baseline,proposed,{
        "predicted_next_front_blocked_if_baseline":round(pred_original,9),
        "predicted_next_front_blocked_if_other":round(pred_other,9),
        "rule_improvement_margin":THRESH,
        "source_alt_selected_effect_observed":False,
    }


def replay_training_only_source_histories(models,fit_check,motors):
    """Identical source-public A* baseline for all predictors on ORIGINAL traces."""
    groups={}
    for e in fit_check:
        key=(e["family"],e["seed"])
        groups.setdefault(key,[]).append(e)
    totals={name:{"checked":0,"baseline_turns":0,"changed_from_r3":0,
      "original_ledger_selected_different_from_proposal":0,
      "turns_left":0,"turns_right":0,"proposed_forward":0,"decisions":[]} for name in models}
    for (family,seed),events in groups.items():
        nav=source_public_navigator(motors,family)
        for expected_step,e in enumerate(events):
            if e["step"]!=expected_step:
                raise ValueError("FIT_PUBLIC_HISTORY_STEP_GAP")
            s,a,y=data_event(e)
            successor=view(e["returned_after"])
            source_sensor_update(nav,s)
            for name,model in models.items():
                baseline,proposed,pred=decision(nav,s,model)
                t=totals[name]
                t["checked"]+=1
                if baseline in (0,1):t["baseline_turns"]+=1
                if proposed!=baseline:t["changed_from_r3"]+=1
                if proposed!=a:t["original_ledger_selected_different_from_proposal"]+=1
                if proposed==0:t["turns_left"]+=1
                elif proposed==1:t["turns_right"]+=1
                else:t["proposed_forward"]+=1
                t["decisions"].append({
                  "family":family,"seed":seed,"step":expected_step,
                  "public_state":s.__dict__,
                  "r3_original_unmodified_action":baseline,
                  "model_proposed_action_NOT_EXECUTED":proposed,
                  "historically_physically_selected_source_action":a,
                  "prediction":pred,
                })
            nav.observe(s,a,successor,e["returned_reward"],e["terminated"],False)
    # Total results include the complete clear historical source-public state,
    # but no invented source choice branch execution or gain/loss.
    return totals


def qualified_disposition(results):
    native=results["native"]["changed_from_r3"]
    frozen=results["frozen"]["changed_from_r3"]
    shifted=results["shuffled_action"]["changed_from_r3"]
    if native==0:
        return "NO_GO_NATIVE_LEARNED_CELLS_DO_NOT_CHANGE_R3_CHOICE"
    if results["native"]["decisions"]==results["frozen"]["decisions"]:
        return "NO_GO_SAME_CHOICES_AS_FROZEN_CELLS"
    if results["native"]["decisions"]==results["shuffled_action"]["decisions"]:
        return "NO_GO_SAME_CHOICES_AS_SHIFTED_ACTIONS"
    return "FIT_ONLY_NATIVE_CHOICE_LEVERAGE_WITHOUT_ORIGINAL_SOURCE_ACTION_OUTCOME"
