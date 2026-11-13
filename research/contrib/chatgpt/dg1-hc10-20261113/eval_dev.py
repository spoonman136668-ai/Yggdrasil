"""Preregistered HC10 source-only, physically charged context-probe evaluation.

True phase and causal source available only to evaluator. Learners see
public before/action/after from genuinely charged mechanism actions;
exogenous physical flips consume steps and NEVER fit causal programs.
"""
from __future__ import annotations
import hashlib
import json
import random
import time
import tracemalloc

from interbank_policy import base,choose as choose_candidate
from conventional_jsd import control,choose as choose_conventional

SEEDS={
 "ABA":tuple(range(81001,81009)),
 "stationary_majority":tuple(range(81009,81017)),
 "OOD_cubic":tuple(range(81017,81025)),
}
ARMS=("candidate","conventional_jsd","unmodified_HC09",
      "no_reactivation","single_bank","cyclic")
FLIP_STEPS={4,9,14,19,24,29,34,39}


class PhysicalWorld:
    def __init__(self,seed,group):
        if group not in SEEDS or seed not in SEEDS[group]:
            raise ValueError("HC10_UNREGISTERED_WORLD")
        self.group=group
        self.sign=[]
        self.slope=[]
        for action in range(4):
            rng=random.Random(seed*101+action*31)
            self.sign.append(rng.randrange(2))
            self.slope.append(rng.randrange(2))
        self.causal_count=0
        self.external_flips=0

    def evaluator_only_next(self,state,action,phase):
        if type(state) is not int or not 0<=state<16:
            raise ValueError("HC10_BAD_PUBLIC_STATE")
        if type(action) is not int or not 0<=action<4:
            raise ValueError("HC10_BAD_PHYSICAL_ACTION")
        if type(phase) is not int or phase not in (0,1):
            raise ValueError("HC10_BAD_PHASE")
        a=(state>>((action+1)%4))&1
        b=(state>>((action+2)%4))&1
        own=(state>>action)&1
        if self.group=="stationary_majority":
            eff=int(a+b+own>=2)
        elif self.group=="OOD_cubic":
            eff=int(state==15)
        else:
            eff=a^b^(own&self.slope[action])
        eff^=self.sign[action]
        if self.group=="ABA" and phase==1:
            eff^=1
        return state^(eff<<action)

    def execute_causal(self,state,action,phase):
        self.causal_count+=1
        return self.evaluator_only_next(state,action,phase)

    def execute_physical_flip(self,state,bit):
        if type(bit) is not int or not 0<=bit<4:
            raise ValueError("HC10_BAD_FLIP")
        self.external_flips+=1
        return state^(1<<bit)

    @property
    def charged(self):
        return self.causal_count+self.external_flips


def audit(model,world,visited,phase):
    score={k:0 for k in ("correct","wrong_confident","abstained",
                         "unseen_correct","unseen_wrong_confident","unseen_abstained")}
    for state in range(16):
        for action in range(4):
            expected=world.evaluator_only_next(state,action,phase)
            got=model.predict(state,action)
            k=("abstained" if got is None else
               "correct" if got==expected else "wrong_confident")
            score[k]+=1
            if (state,action) not in visited:
                score["unseen_"+k]+=1
    score["unseen_total"]=sum(score["unseen_"+k] for k in
                                 ("correct","wrong_confident","abstained"))
    assert sum(score[k] for k in ("correct","wrong_confident","abstained"))==64
    return score


def one_arm(seed,group,arm):
    world=PhysicalWorld(seed,group)
    model=(control.ConventionalContextModel() if arm=="conventional_jsd"
           else base.DualRegimeCausalCells(bank_limit=1) if arm=="single_bank"
           else base.DualRegimeCausalCells(reactivate=False) if arm=="no_reactivation"
           else base.DualRegimeCausalCells())
    before=seed%16
    seen=set()
    ledger=[]
    checkpoints={}
    used_flips=0
    total_steps=40 if group=="ABA" else 48
    start=time.perf_counter_ns()
    decision_ns=0
    for step in range(total_steps):
        phase=int(group=="ABA" and 16<=step<32)
        started=time.perf_counter_ns()
        if arm=="candidate" or arm in ("no_reactivation","single_bank"):
            kind,action=choose_candidate(model,before,used_flips,8)
        elif arm=="conventional_jsd":
            kind,action=choose_conventional(model,before,used_flips,8)
        elif arm=="unmodified_HC09":
            kind,action=model.choose(before,used_flips,8)
        elif arm=="cyclic":
            kind,action=(("flip",used_flips%4) if
                         step in FLIP_STEPS and used_flips<8 else
                         ("causal",step%4))
        else:
            raise ValueError("HC10_UNKNOWN_POLICY")
        decision_ns+=time.perf_counter_ns()-started
        if kind=="causal":
            after=world.execute_causal(before,action,phase)
            model.observe(before,action,after)
            seen.add((before,action))
        elif kind=="flip":
            if used_flips>=8:raise AssertionError("HC10_UNCHARGED_FLIP")
            after=world.execute_physical_flip(before,action)
            used_flips+=1
            # Exogenous intervention is NOT a mechanism training label.
        else:raise AssertionError("HC10_BAD_ACTION_KIND")
        ledger.append([before,kind,action,after])
        before=after
        timestep=step+1
        if group=="ABA" and timestep in (16,32,40):
            # Evaluator-only interim audits, not used by any next choice.
            audit_phase=1 if timestep==32 else 0
            checkpoints[str(timestep)]=audit(model,world,seen,audit_phase)
    elapsed_ns=time.perf_counter_ns()-start
    assert world.charged==total_steps and world.external_flips==used_flips
    assert (model.n if arm=="conventional_jsd" else model.observations)==world.causal_count
    raw=model.snapshot()
    restored=(control.ConventionalContextModel.restore(raw) if arm=="conventional_jsd"
              else base.DualRegimeCausalCells.restore(raw))
    assert raw==restored.snapshot() and len(raw)<=4096
    assert all(model.predict(s,a)==restored.predict(s,a)
               for s in range(16) for a in range(4))
    final=audit(model,world,seen,0)
    if group=="ABA":assert final==checkpoints["40"]
    return {
        "final":final,"intermediate_evaluator_only":checkpoints,
        "charged_real_actions":world.charged,"charged_mechanism_actions":world.causal_count,
        "charged_exogenous_flips":world.external_flips,
        "distinct_training_state_actions":len(seen),
        "logical_mask_bits":160 if arm=="single_bank" else 320,
        "banks":len(model.contexts) if arm=="conventional_jsd" else len(model.banks),
        "reconnections":model.switches if arm=="conventional_jsd" else model.reactivations,
        "unexplained":model.unexplained if arm=="conventional_jsd" else model.unresolved_events,
        "snapshot_bytes":len(raw),"cold_restore_identical":True,
        "action_ledger_sha256":hashlib.sha256(base.encode(ledger)).hexdigest(),
        "policy_decision_ns":decision_ns,"whole_learning_ns":elapsed_ns,
    }


def one_world(seed,group):
    arms={arm:one_arm(seed,group,arm) for arm in ARMS}
    expected=40 if group=="ABA" else 48
    assert all(r["charged_real_actions"]==expected for r in arms.values())
    return {"seed":seed,"group":group,"arms":arms}


def run():
    tracemalloc.start()
    worlds=[one_world(s,g) for g,seeds in SEEDS.items() for s in seeds]
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    def total(group,arm,k):
        return sum(w["arms"][arm]["final"][k] for w in worlds if w["group"]==group)
    fields=("correct","wrong_confident","abstained",
            "unseen_correct","unseen_wrong_confident","unseen_abstained")
    agg={g:{arm:{k:total(g,arm,k) for k in fields} for arm in ARMS}
         for g in SEEDS}
    ABA_pass=(total("ABA","candidate","correct")>=160 and
              total("ABA","candidate","correct")>=
                  total("ABA","unmodified_HC09","correct")+64 and
              total("ABA","candidate","wrong_confident")==0)
    majority_pass=(total("stationary_majority","candidate","correct")>=384 and
                   total("stationary_majority","candidate","wrong_confident")==0)
    cubic_errors=total("OOD_cubic","candidate","wrong_confident")
    verdict=("DEV_SIGNAL_ONLY_NOT_SCIENCE" if ABA_pass and majority_pass and not cubic_errors
             else "MIXED_DEV" if (ABA_pass or majority_pass)
             else "NEGATIVE_DEV")
    return {
        "schema":"ygg.dg1-hc10.discriminating-context-probe-dev.v1",
        "classification":verdict,"scientific_acceptance":"UNVERIFIED",
        "ABA_primary_pass":ABA_pass,"majority_regression_pass":majority_pass,
        "out_of_class_confident_wrong":cubic_errors,
        "actual_charged_actions":sum(r["charged_real_actions"]
                                    for w in worlds for r in w["arms"].values()),
        "same_capacity_and_action_budget_conventional":True,
        "matched_total_compute":False,
        "world_count":len(worlds),"cohort_accuracy":agg,
        "peak_python_tracemalloc_bytes":peak,
        "worlds":worlds
    }

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
