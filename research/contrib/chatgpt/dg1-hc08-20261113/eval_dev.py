"""HC08 prospectively frozen source-only charged-controllability experiment.

World equations and regime labels are evaluator-only. Causal learners see
public physical (before,action,after) ONLY from charged mechanism actions;
charged exogenous bit flips provide a changed state but NO fitted transition.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
import random
from time import perf_counter_ns
import tracemalloc

from steering_policy import base,choose_intervention
from bayesian_steering_policy import bayes,decide_bayesian

COHORTS={
    "known_absorbing_dev":(51001,51002,51007),
    "unseen_rewired":tuple(range(61001,61009)),
    "unseen_ring":tuple(range(61009,61013)),
    "negative_majority":tuple(range(61013,61017)),
    "unseen_ABA":tuple(range(61017,61021)),
}
POLICIES=("candidate","bayesian","no_actuator","sham","round_robin_steer")
FORCE_AT={4,9,14,19,24,29,34,39}


class PhysicalWorld:
    def __init__(self,seed,cohort):
        if cohort not in COHORTS or seed not in COHORTS[cohort]:
            raise ValueError("HC08_UNREGISTERED_WORLD")
        self.cohort=cohort
        self.sign=[]
        self.own=[]
        for action in range(4):
            r=random.Random(seed*101+action*31)
            self.sign.append(r.randrange(2))
            self.own.append(r.randrange(2))
        self.costed_causal=0
        self.costed_forced=0
        self.costed_sham=0

    def physical_effect_for_evaluator(self,state,action,phase):
        if type(state) is not int or not 0<=state<16 or type(action) is not int or not 0<=action<4:
            raise ValueError("HC08_BAD_PUBLIC_PHYSICAL_IO")
        if self.cohort=="unseen_ring":
            left=(action-1)%4
            right=(action+1)%4
        else:
            left=(action+1)%4
            right=(action+2)%4
        x=(state>>left)&1
        y=(state>>right)&1
        own=(state>>action)&1
        if self.cohort=="negative_majority":
            effect=int(x+y+own>=2)
        else:
            effect=x^y^(own & self.own[action])
        effect^=self.sign[action]
        if self.cohort=="unseen_ABA" and phase==1:
            effect^=1
        return effect

    def evaluate_without_charge(self,state,action,phase):
        return state^(self.physical_effect_for_evaluator(state,action,phase)<<action)

    def apply_causal(self,state,action,phase):
        self.costed_causal+=1
        return self.evaluate_without_charge(state,action,phase)

    def apply_forced_flip(self,state,bit):
        if type(bit) is not int or not 0<=bit<4:
            raise ValueError("HC08_BAD_ACTUATION")
        self.costed_forced+=1
        return state^(1<<bit)

    def apply_sham(self,state):
        self.costed_sham+=1
        return state

    @property
    def total_charged(self):
        return self.costed_causal+self.costed_forced+self.costed_sham


def audit(model,world,seen):
    score={k:0 for k in
           ("correct","wrong_confident","abstained",
            "unseen_correct","unseen_wrong_confident","unseen_abstained")}
    for state in range(16):
        for action in range(4):
            physical=world.evaluate_without_charge(state,action,phase=0)
            prediction=model.predict(state,action)
            tag=("abstained" if prediction is None else
                 "correct" if prediction==physical else "wrong_confident")
            score[tag]+=1
            if (state,action) not in seen:
                score["unseen_"+tag]+=1
    score["unseen_total"]=sum(score["unseen_"+k] for k in
                                ("correct","wrong_confident","abstained"))
    assert score["correct"]+score["wrong_confident"]+score["abstained"]==64
    return score


def experiment_arm(seed,cohort,policy):
    source=PhysicalWorld(seed,cohort)
    learner=(bayes.BayesianGraphController() if policy=="bayesian"
             else base.AffineCausalCells())
    state=seed%16
    states_seen={state}
    model_fitted=set()
    trajectory=[]
    flips=0
    decision_ns=0
    total=25 if cohort=="unseen_ABA" else 48
    limit=4 if cohort=="unseen_ABA" else 8
    t0=perf_counter_ns()
    for step in range(total):
        phase=int(cohort=="unseen_ABA" and 16<=step<24)
        tdecision=perf_counter_ns()
        if policy=="candidate" or policy=="sham":
            kind,index=choose_intervention(learner,state,flips,limit)
        elif policy=="bayesian":
            kind,index=decide_bayesian(learner,state,flips,limit)
        elif policy=="no_actuator":
            kind,index=("causal",learner.choose(state))
        elif policy=="round_robin_steer":
            if step in FORCE_AT and flips<limit:
                kind,index=("flip",flips%4)
            else:
                kind,index=("causal",step%4)
        else:
            raise ValueError("HC08_UNKNOWN_POLICY")
        decision_ns+=perf_counter_ns()-tdecision
        prior=state
        if kind=="causal":
            state=source.apply_causal(state,index,phase)
            learner.observe(prior,index,state)
            model_fitted.add((prior,index))
        elif kind=="flip":
            if flips>=limit:
                raise AssertionError("HC08_FLIP_BUDGET_VIOLATION")
            if policy=="sham":
                state=source.apply_sham(state)
            else:
                state=source.apply_forced_flip(state,index)
            flips+=1
            # NO model.observe for a forced intervention. Its post-state is
            # public, but does not label a previously unknown causal law.
        else:
            raise AssertionError("HC08_BAD_INTERVENTION_KIND")
        states_seen.add(state)
        trajectory.append([prior,kind,index,state])
    total_time_ns=perf_counter_ns()-t0
    assert source.total_charged==total
    assert (learner.events if policy=="bayesian" else learner.observations)==source.costed_causal
    assert flips==source.costed_forced+source.costed_sham
    assert flips<=limit
    snapshot=learner.snapshot()
    restored=(bayes.BayesianGraphController.restore(snapshot)
              if policy=="bayesian" else base.AffineCausalCells.restore(snapshot))
    assert snapshot==restored.snapshot()
    assert all(restored.predict(s,a)==learner.predict(s,a)
               for s in range(16) for a in range(4))
    return {
        "score":audit(learner,source,model_fitted),
        "total_charged":source.total_charged,
        "causal_observations":source.costed_causal,
        "forced_flips":source.costed_forced,
        "sham_actions":source.costed_sham,
        "distinct_public_states":len(states_seen),
        "distinct_causal_state_action_pairs":len(model_fitted),
        "hypotheses_per_action":(
            learner.evidence_support() if policy=="bayesian"
            else learner.program_support()),
        "logical_program_mask_bits":128,
        "checkpoint_bytes":len(snapshot),
        "cold_restore_exact":True,
        "ledger_sha256":sha256(base.canonical(trajectory)).hexdigest(),
        "policy_decision_ns":decision_ns,
        "whole_training_ns":total_time_ns
    }


def one_world(seed,cohort):
    arms={p:experiment_arm(seed,cohort,p) for p in POLICIES}
    required=25 if cohort=="unseen_ABA" else 48
    assert all(z["total_charged"]==required for z in arms.values())
    assert all(z["logical_program_mask_bits"]==128 for z in arms.values())
    return {"seed":seed,"cohort":cohort,"arms":arms}


def run():
    tracemalloc.start()
    rows=[one_world(seed,cohort) for cohort,seeds in COHORTS.items() for seed in seeds]
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    def total(cohort,arm,key):
        return sum(row["arms"][arm]["score"][key] for row in rows
                   if row["cohort"]==cohort)
    known=[r for r in rows if r["cohort"]=="known_absorbing_dev"]
    known_pass=all(
        r["arms"]["candidate"]["score"]["correct"]>=16 and
        r["arms"]["candidate"]["score"]["wrong_confident"]==0 and
        r["arms"]["candidate"]["distinct_public_states"]>1 and
        r["arms"]["no_actuator"]["score"]["correct"]<=4 and
        r["arms"]["no_actuator"]["distinct_public_states"]==1 for r in known)
    newrows=[r for r in rows if r["cohort"]=="unseen_rewired"]
    new_pass=all(
        r["arms"]["candidate"]["score"]["correct"]>=16 and
        r["arms"]["candidate"]["score"]["wrong_confident"]==0 for r in newrows
    ) and total("unseen_rewired","candidate","correct")>=(
        total("unseen_rewired","no_actuator","correct")+64)
    ABA_pass=(total("unseen_ABA","candidate","correct")>=64 and
              total("unseen_ABA","candidate","wrong_confident")==0)
    outside_wrong=total("negative_majority","candidate","wrong_confident")
    classification=("DEV_MECHANISM_SUPPORTED_NOT_SCIENCE"
                    if known_pass and new_pass and ABA_pass and outside_wrong==0
                    else "MIXED_DEV" if (known_pass or new_pass or ABA_pass)
                    else "NEGATIVE_DEV")
    summary={
        cohort:{arm:{k:total(cohort,arm,k) for k in
          ("correct","wrong_confident","abstained",
           "unseen_correct","unseen_wrong_confident","unseen_abstained")}
            for arm in POLICIES} for cohort in COHORTS}
    return {
        "schema":"ygg.dg1-hc08.costed-controllability-dev.v1",
        "classification":classification,
        "scientific_acceptance":"UNVERIFIED",
        "known_absorbing_replay_pass":known_pass,
        "new_rewired_primary_pass":new_pass,
        "ABA_retention_pass":ABA_pass,
        "outside_grammar_confident_wrong":outside_wrong,
        "source_charged_actions_across_arms":sum(
            a["total_charged"] for row in rows for a in row["arms"].values()),
        "source_worlds":len(rows),
        "model_logical_program_bits":128,
        "matched_physical_action_count":True,
        "matched_actuation_rights_among_candidate_and_bayesian":True,
        "matched_total_compute":False,
        "full_process_peak_tracemalloc_bytes":peak,
        "cohort_accuracy":summary,
        "worlds":rows,
    }


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
