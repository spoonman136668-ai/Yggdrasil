"""HC09 frozen synthetic physical action-consequence evaluation.

World physics is evaluator-only. No hidden phase labels, mechanism names or
counterfactual answers reach learner. No source import from candidate model.
"""
from __future__ import annotations
from hashlib import sha256
import importlib.util
import json,random
from time import perf_counter_ns
import tracemalloc
from pathlib import Path

from model import DualRegimeCausalCells,encode
from conventional_control import ConventionalContextModel

HERE=Path(__file__).resolve().parent
HC07=HERE.parent/"dg1-hc07-20261113"/"affine_cells.py"
HC08=HERE.parent/"dg1-hc08-20261113"/"steering_policy.py"
m_spec=importlib.util.spec_from_file_location("hc09_old_graph",HC07)
old=importlib.util.module_from_spec(m_spec)
m_spec.loader.exec_module(old)
p_spec=importlib.util.spec_from_file_location("hc09_old_steer",HC08)
old_policy=importlib.util.module_from_spec(p_spec)
p_spec.loader.exec_module(old_policy)

SEEDS={
 "stationary_affine":tuple(range(71001,71009)),
 "stationary_majority":tuple(range(71009,71017)),
 "A_B_A":tuple(range(71017,71025)),
 "out_of_grammar":tuple(range(71025,71029)),
}
ARMS=("candidate","conventional","no_reactivation","single_bank","fixed_hc08","round_robin")
FORCE_AT=(4,9,14,19,24,29,34,39)


class World:
    def __init__(self,seed,group):
        if group not in SEEDS or seed not in SEEDS[group]:
            raise ValueError("HC09_UNPREREGISTERED_WORLD")
        self.group=group
        self.sign=[]
        self.slope=[]
        for a in range(4):
            r=random.Random(seed*101+a*31)
            self.sign.append(r.randrange(2))
            self.slope.append(r.randrange(2))
        self.causal=0
        self.perturbations=0

    def true_next_for_evaluator(self,state,action,phase):
        if (type(state) is not int or not 0<=state<16 or
            type(action) is not int or not 0<=action<4 or
            type(phase) is not int or phase not in (0,1)):
            raise ValueError("HC09_BAD_EVALUATOR_QUERY")
        left=(state>>((action+1)%4))&1
        right=(state>>((action+2)%4))&1
        own=(state>>action)&1
        if self.group=="stationary_majority":
            base=int(left+right+own>=2)
        elif self.group=="out_of_grammar":
            base=int(state==15)
        else:
            base=left^right^(own&self.slope[action])
        effect=base^self.sign[action]
        if self.group=="A_B_A" and phase==1:
            effect^=1
        return state^(effect<<action)

    def charge_causal(self,state,action,phase):
        self.causal+=1
        return self.true_next_for_evaluator(state,action,phase)

    def charge_flip(self,state,bit):
        if type(bit) is not int or not 0<=bit<4:
            raise ValueError("HC09_BAD_ACTUATION_BIT")
        self.perturbations+=1
        return state^(1<<bit)

    @property
    def used(self):return self.causal+self.perturbations


def audit(model,world,fitted):
    score={key:0 for key in (
        "correct","wrong_confident","abstained",
        "unseen_correct","unseen_wrong_confident","unseen_abstained")}
    for state in range(16):
        for a in range(4):
            expected=world.true_next_for_evaluator(state,a,0)
            pred=model.predict(state,a)
            mark=("abstained" if pred is None else
                  "correct" if pred==expected else "wrong_confident")
            score[mark]+=1
            if (state,a) not in fitted:
                score["unseen_"+mark]+=1
    score["unseen_total"]=sum(score["unseen_"+k] for k in
                              ("correct","wrong_confident","abstained"))
    assert score["correct"]+score["wrong_confident"]+score["abstained"]==64
    return score


def one_arm(seed,group,arm):
    world=World(seed,group)
    if arm=="conventional":model=ConventionalContextModel()
    elif arm=="single_bank":model=DualRegimeCausalCells(bank_limit=1)
    elif arm=="no_reactivation":model=DualRegimeCausalCells(reactivate=False)
    elif arm=="fixed_hc08":model=old.AffineCausalCells()
    else:model=DualRegimeCausalCells()
    state=seed%16
    visited={state}
    fitted=set()
    ledger=[]
    used_flips=0
    decision_ns=0
    t0=perf_counter_ns()
    total=32 if group=="A_B_A" else 48
    cap=6 if group=="A_B_A" else 8
    for step in range(total):
        phase=int(group=="A_B_A" and 16<=step<28)
        before=state
        td=perf_counter_ns()
        if arm=="round_robin":
            if step in FORCE_AT and used_flips<cap:
                kind,idx="flip",used_flips%4
            else:
                kind,idx="causal",step%4
        elif arm=="fixed_hc08":
            kind,idx=old_policy.choose_intervention(model,state,used_flips,cap)
        else:
            kind,idx=model.choose(state,used_flips,cap)
        decision_ns+=perf_counter_ns()-td
        if kind=="causal":
            state=world.charge_causal(before,idx,phase)
            model.observe(before,idx,state)
            fitted.add((before,idx))
        elif kind=="flip":
            if used_flips>=cap:raise AssertionError("HC09_FLIP_OVERRUN")
            state=world.charge_flip(before,idx)
            used_flips+=1
            # This forced change does not give a mechanism training label.
        else:raise AssertionError("HC09_BAD_ACTION")
        visited.add(state)
        ledger.append([before,kind,idx,state])
    training_ns=perf_counter_ns()-t0
    assert world.used==total
    assert used_flips==world.perturbations and used_flips<=cap
    assert (model.n if arm=="conventional" else model.observations)==world.causal
    snap=model.snapshot()
    if arm=="conventional":restored=ConventionalContextModel.restore(snap)
    elif arm=="fixed_hc08":restored=old.AffineCausalCells.restore(snap)
    else:restored=DualRegimeCausalCells.restore(snap)
    assert restored.snapshot()==snap and len(snap)<=4096
    assert all(model.predict(s,a)==restored.predict(s,a)
               for s in range(16) for a in range(4))
    return {
        "score":audit(model,world,fitted),
        "total_charged":world.used,
        "causal_observations":world.causal,
        "charged_flips":world.perturbations,
        "distinct_states":len(visited),
        "distinct_fitted_state_actions":len(fitted),
        "hypothesis_support":(
            model.supports() if arm!="fixed_hc08"
            else [tuple(m.bit_count() for m in model.surviving)]),
        "logical_hypothesis_bits":(128 if arm=="fixed_hc08" else
                                   160 if arm=="single_bank" else 320),
        "split_events":(model.created if arm=="conventional" else
                        model.splits if arm!="fixed_hc08" else 0),
        "reactivation_events":(model.switches if arm=="conventional" else
                                model.reactivations if arm!="fixed_hc08" else 0),
        "unexplained_events":(model.unexplained if arm=="conventional" else
                              model.unresolved_events if arm!="fixed_hc08" else
                              model.violations),
        "snapshot_bytes":len(snap),
        "cold_restore":True,
        "action_ledger_sha256":sha256(encode(ledger)).hexdigest(),
        "decision_ns":decision_ns,
        "whole_training_ns":training_ns
    }


def one_world(seed,group):
    receipts={a:one_arm(seed,group,a) for a in ARMS}
    assert all(z["total_charged"]==(32 if group=="A_B_A" else 48)
               for z in receipts.values())
    return {"seed":seed,"group":group,"arms":receipts}


def run():
    tracemalloc.start()
    rows=[one_world(seed,grp) for grp,seeds in SEEDS.items() for seed in seeds]
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    def total(group,arm,key):
        return sum(x["arms"][arm]["score"][key] for x in rows if x["group"]==group)
    summary={
        group:{arm:{key:total(group,arm,key) for key in
              ("correct","wrong_confident","abstained",
               "unseen_correct","unseen_wrong_confident","unseen_abstained")}
               for arm in ARMS} for group in SEEDS
    }
    affine=(total("stationary_affine","candidate","correct")>=384 and
            total("stationary_affine","candidate","wrong_confident")==0)
    nonlinear=(total("stationary_majority","candidate","correct")>=256 and
               total("stationary_majority","candidate","wrong_confident")==0 and
               total("stationary_majority","candidate","correct")>=
               total("stationary_majority","fixed_hc08","correct")+64)
    retention=(total("A_B_A","candidate","correct")>=128 and
               total("A_B_A","candidate","wrong_confident")==0 and
               total("A_B_A","candidate","correct")>=
               total("A_B_A","no_reactivation","correct")+64)
    ood=total("out_of_grammar","candidate","wrong_confident")
    classification=("DEV_MECHANISM_SUPPORTED_NOT_SCIENCE"
                    if affine and nonlinear and retention and ood==0
                    else "MIXED_DEV" if (affine or nonlinear or retention)
                    else "NEGATIVE_DEV")
    return {
        "schema":"ygg.dg1-hc09.multiregime-nonlinear-dev.v1",
        "classification":classification,
        "stationary_affine_pass":affine,
        "stationary_majority_pass":nonlinear,
        "A_B_A_retention_pass":retention,
        "out_of_grammar_confident_wrong":ood,
        "scientific_acceptance":"UNVERIFIED",
        "matched_equal_capacity_context_bayesian":True,
        "matched_physical_action_rights":True,
        "matched_compute":False,
        "total_physical_charges":sum(x["arms"][a]["total_charged"]
                                     for x in rows for a in ARMS),
        "peak_python_tracemalloc_bytes":peak,
        "aggregate":summary,
        "worlds":rows,
    }


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
