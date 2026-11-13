"""HC07 preregistered synthetic physical causal-graph discovery DEV evaluation.

Hidden causal graph and signs live only in SourceWorld. All learners observe
public before/action/after for one actually charged physical action at a time.
No free training queries, simulator resets or evaluator-answer access.
"""
from __future__ import annotations
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
from time import perf_counter_ns
import tracemalloc

from affine_cells import AffineCausalCells,canonical as encode_candidate
from bayesian_graph_control import BayesianGraphController

HERE=Path(__file__).resolve().parent
HC05=HERE.parent/"dg1-hc05-20261113"/"model.py"
def _load_hc05():
    sp=importlib.util.spec_from_file_location("immutable_hc05_for_hc07",HC05)
    mod=importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod
hc05=_load_hc05()

SEEDS={
    "rewired":tuple(range(51001,51009)),
    "old_ring":tuple(range(51009,51017)),
    "non_affine":tuple(range(51017,51025)),
    "phase_switch":tuple(range(51025,51033)),
}
POLICIES=("graph_cells","bayesian_graph","fixed_hc05","round_robin")


class SourceWorld:
    def __init__(self,seed,family):
        if family not in SEEDS or seed not in SEEDS[family]:
            raise ValueError("HC07_UNREGISTERED_WORLD")
        self.seed=seed
        self.family=family
        self.signs=[]
        self.own=[]
        for action in range(4):
            rng=random.Random(seed*101+action*31)
            self.signs.append(rng.randrange(2))
            self.own.append(rng.randrange(2))
        self.physical_actions=0

    def true_successor_for_audit(self,state,action,phase=0):
        if type(state) is not int or not 0<=state<16 or type(action) is not int or not 0<=action<4:
            raise ValueError("HC07_INVALID_AUDIT_LOCATOR")
        a,b=(
            ((action-1)%4,(action+1)%4)
            if self.family=="old_ring" else
            ((action+1)%4,(action+2)%4)
        )
        x=(state>>a)&1
        y=(state>>b)&1
        own=(state>>action)&1
        if self.family=="non_affine":
            effect=int(x+y+own>=2)
        else:
            effect=x^y^(own&self.own[action])
        effect^=self.signs[action]
        if self.family=="phase_switch" and phase==1:
            effect^=1
        return state^(effect<<action)

    def execute_real_action(self,state,action,phase):
        self.physical_actions+=1
        return self.true_successor_for_audit(state,action,phase)


def audit(model,world,visited):
    stats={k:0 for k in ("correct","wrong_confident","abstained",
                         "unseen_correct","unseen_wrong_confident","unseen_abstained")}
    for state in range(16):
        for action in range(4):
            expected=world.true_successor_for_audit(state,action,0)
            guessed=model.predict(state,action)
            mark=("abstained" if guessed is None else
                  "correct" if guessed==expected else "wrong_confident")
            stats[mark]+=1
            if (state,action) not in visited:
                stats["unseen_"+mark]+=1
    stats["unseen_total"]=sum(stats["unseen_"+k] for k in ("correct","wrong_confident","abstained"))
    assert stats["correct"]+stats["wrong_confident"]+stats["abstained"]==64
    return stats


def single(seed,family,arm):
    world=SourceWorld(seed,family)
    model=(
        AffineCausalCells() if arm in ("graph_cells","round_robin")
        else BayesianGraphController() if arm=="bayesian_graph"
        else hc05.CausalProbeCells()
    )
    state=seed%16
    visited=set()
    trace=[]
    policy_time_ns=0
    t0=perf_counter_ns()
    budget=25 if family=="phase_switch" else 32
    for t in range(budget):
        phase=int(family=="phase_switch" and 16<=t<24)
        start=perf_counter_ns()
        if arm=="graph_cells":
            action=model.choose(state)
        elif arm=="bayesian_graph":
            action=model.choose(state)
        elif arm=="fixed_hc05":
            action=model.choose_greedy(state)
        elif arm=="round_robin":
            action=t%4
        else:
            raise ValueError("HC07_UNKNOWN_ARM")
        policy_time_ns+=perf_counter_ns()-start
        after=world.execute_real_action(state,action,phase)
        model.observe(state,action,after)
        trace.append((state,action,after))
        visited.add((state,action))
        state=after
    train_time_ns=perf_counter_ns()-t0
    assert world.physical_actions==budget
    assert (model.events if arm=="bayesian_graph" else model.observations)==budget
    checkpoint=model.snapshot()
    restoration=(
        BayesianGraphController.restore(checkpoint) if arm=="bayesian_graph"
        else hc05.CausalProbeCells.restore(checkpoint) if arm=="fixed_hc05"
        else AffineCausalCells.restore(checkpoint)
    )
    assert restoration.snapshot()==checkpoint
    assert all(model.predict(s,a)==restoration.predict(s,a)
               for s in range(16) for a in range(4))
    assert len(checkpoint)<=1024
    logical=(24 if arm=="fixed_hc05" else 128)
    return {
        "score":audit(model,world,visited),
        "real_physical_actions":budget,
        "distinct_public_pairs":len(visited),
        "ledger_sha256":sha256(encode_candidate(trace)).hexdigest(),
        "hypothesis_support":(
            model.program_support() if arm in ("graph_cells","round_robin")
            else model.evidence_support() if arm=="bayesian_graph"
            else [x.bit_count() for x in model.masks]
        ),
        "logical_rule_bits":logical,
        "checkpoint_bytes":len(checkpoint),
        "cold_restore_exact":True,
        "total_train_ns":train_time_ns,
        "policy_decision_ns":policy_time_ns,
    }


def one_world(seed,family):
    receipts={arm:single(seed,family,arm) for arm in POLICIES}
    assert all(r["real_physical_actions"]==(25 if family=="phase_switch" else 32)
               for r in receipts.values())
    return {"seed":seed,"family":family,"arms":receipts}


def run():
    tracemalloc.start()
    worlds=[one_world(seed,family) for family,seeds in SEEDS.items() for seed in seeds]
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    def sum_metric(family,arm,key):
        return sum(x["arms"][arm]["score"][key] for x in worlds if x["family"]==family)
    def record(family,arm):
        return {k:sum_metric(family,arm,k) for k in
                ("correct","wrong_confident","abstained",
                 "unseen_correct","unseen_wrong_confident","unseen_abstained")}
    metrics={family:{arm:record(family,arm) for arm in POLICIES} for family in SEEDS}
    rewired=(
        record("rewired","graph_cells")["wrong_confident"]==0 and
        all(w["arms"]["graph_cells"]["score"]["correct"]>=32
            for w in worlds if w["family"]=="rewired") and
        record("rewired","graph_cells")["correct"]>=
        record("rewired","fixed_hc05")["correct"]+128
    )
    old=record("old_ring","graph_cells")["correct"]>=256 and record("old_ring","graph_cells")["wrong_confident"]==0
    switch=record("phase_switch","graph_cells")["correct"]>=256 and record("phase_switch","graph_cells")["wrong_confident"]==0
    negative_confident=record("non_affine","graph_cells")["wrong_confident"]
    status=("DEV_MECHANISM_SUPPORTED_NOT_SCIENCE" if rewired and old and switch and not negative_confident
            else "MIXED_DEV" if (rewired or old or switch)
            else "NEGATIVE_DEV")
    return {
        "schema":"ygg.dg1-hc07.graph-discovery-dev.v1",
        "classification":status,
        "frozen_primary_rewired_pass":rewired,
        "old_ring_pass":old,"return_A_pass":switch,
        "non_affine_confident_wrong":negative_confident,
        "source_only_science_pass":"UNVERIFIED",
        "matches_conventional_same_capacity_physical_action_budget":True,
        "matches_conventional_whole_process_compute":False,
        "action_budgets":{"stationary":32,"phase_switch":25,"worlds":32,"arms":4},
        "total_charged_actions":sum(r["real_physical_actions"] for w in worlds for r in w["arms"].values()),
        "runtime_peak_tracemalloc_bytes":peak,
        "aggregate":metrics,
        "worlds":worlds,
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
