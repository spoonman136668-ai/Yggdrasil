"""DG1-HC05 prospective synthetic physically-charged causal intervention DEV.

World physics is evaluator-only. Models receive exactly public consequences
from twelve actually executed interventions on one continuous trajectory.
No rollout oracle, resets, hidden-rule queries, or science-first-use.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import tracemalloc

from model import (
    CausalProbeCells, ConventionalEquivalentPlanner, HYPOTHESES, ACTIONS,
    MAX_CHECKPOINT_BYTES, canonical, local_effect,
)

STATIONARY_SEEDS = tuple(range(31001, 31009))
ROUTING_SEEDS = tuple(range(31009, 31013))
OUT_OF_GRAMMAR_SEEDS = tuple(range(31013, 31017))
CHARGED_ACTIONS = 12


class PhysicalWorld:
    """4-bit physical system, fixed unknown law and sign per action."""
    def __init__(self, seed, *, negative=False):
        self.seed = seed
        self.negative = negative
        self.rules = []
        for action in range(ACTIONS):
            rng = random.Random(seed * 97 + action * 37)
            self.rules.append((rng.randrange(3), rng.randrange(2)))
        self.executed_actions = 0

    def physics_effect(self, state, action):
        family, sign = self.rules[action]
        left = (state >> ((action - 1) % 4)) & 1
        own = (state >> action) & 1
        right = (state >> ((action + 1) % 4)) & 1
        if self.negative:
            # Majority(own,left,right) is deliberately not one of six forms.
            base = int(left + own + right >= 2)
        elif family == 0:
            base = left ^ right
        elif family == 1:
            base = left ^ right ^ own
        else:
            base = left & right
        return base ^ sign

    def counterfactual_for_evaluator_only(self, state, action):
        return state ^ (self.physics_effect(state, action) << action)

    def execute(self, state, action):
        self.executed_actions += 1
        return self.counterfactual_for_evaluator_only(state, action)


class FirstViableUngated:
    def __init__(self, delegate):
        self.delegate = delegate

    def predict(self, state, action):
        mask = self.delegate.masks[action]
        for hypothesis in range(HYPOTHESES):
            if mask & (1 << hypothesis):
                return state ^ (local_effect(state, action, hypothesis) << action)
        return None


def evaluate(model, world, observed):
    counts = {
        "correct":0,"wrong_confident":0,"abstained":0,
        "unseen_correct":0,"unseen_wrong_confident":0,"unseen_abstained":0,
    }
    for state in range(16):
        for action in range(4):
            true_after = world.counterfactual_for_evaluator_only(state, action)
            predicted = model.predict(state, action)
            suffix = "unseen_" if (state, action) not in observed else ""
            if predicted is None:
                kind="abstained"
            elif predicted==true_after:
                kind="correct"
            else:
                kind="wrong_confident"
            counts[kind]+=1
            if suffix:
                counts[suffix+kind]+=1
    counts["unseen_total"] = sum(counts["unseen_"+key] for key in
                                  ("correct","wrong_confident","abstained"))
    return counts


def one_policy(seed, kind, negative=False):
    world = PhysicalWorld(seed, negative=negative)
    model = (ConventionalEquivalentPlanner() if kind == "conventional"
             else CausalProbeCells())
    state = seed % 16
    rng = random.Random(seed + 919)
    trace = []
    seen=set()
    begin = time.perf_counter()
    for t in range(CHARGED_ACTIONS):
        if kind in ("lookahead", "conventional"):
            action = model.choose_lookahead(state)
        elif kind == "greedy":
            action = model.choose_greedy(state)
        elif kind == "round_robin":
            action = t % ACTIONS
        elif kind == "random":
            action = rng.randrange(ACTIONS)
        else:
            raise ValueError("HC05_UNKNOWN_POLICY")
        before = state
        # This is the one and only physical charge this time step.
        after = world.execute(before, action)
        model.observe(before, action, after)
        trace.append((before, action, after))
        seen.add((before, action))
        state=after
    elapsed_ms=round((time.perf_counter()-begin)*1000, 5)
    assert world.executed_actions==CHARGED_ACTIONS
    assert model.observations==CHARGED_ACTIONS
    assert model.logical_mask_bits==24
    checkpoint=model.snapshot()
    restored=CausalProbeCells.restore(checkpoint)
    assert restored.snapshot()==checkpoint
    assert len(checkpoint)<=MAX_CHECKPOINT_BYTES
    assert all(model.predict(s,a)==restored.predict(s,a)
               for s in range(16) for a in range(4))
    return {
        "scored":evaluate(model,world,seen),
        "ungated":evaluate(FirstViableUngated(model),world,seen),
        "distinct_observed_pairs":len(seen),
        "real_actions":world.executed_actions,
        "ledger_sha256":hashlib.sha256(canonical(trace)).hexdigest(),
        "checkpoint_bytes":len(checkpoint),
        "cold_restore_parity":True,
        "logical_hypothesis_bits":model.logical_mask_bits,
        "unrepresentable_contradictions":model.contradictions,
        "training_elapsed_ms":elapsed_ms,
    }


def one_world(seed, group):
    if group not in ("stationary","routing","out_of_grammar"):
        raise ValueError("HC05_BAD_GROUP")
    negative=group=="out_of_grammar"
    arms={k:one_policy(seed,k,negative=negative) for k in
          ("lookahead","conventional","greedy","round_robin","random")}
    assert arms["lookahead"]["ledger_sha256"]==arms["conventional"]["ledger_sha256"]
    assert arms["lookahead"]["scored"]==arms["conventional"]["scored"]
    assert all(z["real_actions"]==CHARGED_ACTIONS for z in arms.values())
    return {"seed":seed,"group":group,"arms":arms}


def run():
    tracemalloc.start()
    rows=(
      [one_world(seed,"stationary") for seed in STATIONARY_SEEDS] +
      [one_world(seed,"routing") for seed in ROUTING_SEEDS] +
      [one_world(seed,"out_of_grammar") for seed in OUT_OF_GRAMMAR_SEEDS]
    )
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    stationary,routing,negative=rows[:8],rows[8:12],rows[12:]
    avg=lambda group,name:sum(
        row["arms"][name]["scored"]["correct"] for row in group
    )/(len(group)*64)
    no_wrong=lambda group:all(
        row["arms"]["lookahead"]["scored"]["wrong_confident"]==0
        for row in group)
    stationary_pass=(
        no_wrong(stationary) and
        avg(stationary,"lookahead")>=max(
            avg(stationary,"greedy"),avg(stationary,"round_robin"))+0.0625 and
        avg(stationary,"lookahead")>=avg(stationary,"random")
    )
    routing_pass=(
        no_wrong(routing) and
        avg(routing,"lookahead")>=avg(routing,"greedy")+0.03125
    )
    out_wrong=sum(
        row["arms"]["lookahead"]["scored"]["wrong_confident"]
        for row in negative)
    return {
       "schema":"yggdrasil.dg1-hc05.intervention-value-dev.v1",
       "classification":(
           "DEV_SIGNAL_ONLY_NOT_SCIENCE" if stationary_pass and routing_pass else
           "MIXED_DEV" if stationary_pass != routing_pass else "NEGATIVE_DEV"),
       "stationary_main_pass":stationary_pass,
       "routing_pass":routing_pass,
       "out_of_grammar_confident_wrong":out_wrong,
       "out_of_grammar_status":(
           "UNSAFE_OUT_OF_CLASS" if out_wrong else
           "FINITE_NEGATIVE_NO_GENERAL_SAFETY_PROOF"),
       "scientific_acceptance":"UNVERIFIED",
       "equal_algorithmic_conventional_control_tied":all(
           row["arms"]["lookahead"]["ledger_sha256"]==
           row["arms"]["conventional"]["ledger_sha256"] and
           row["arms"]["lookahead"]["scored"]==
           row["arms"]["conventional"]["scored"] for row in rows),
       "no_gradient":True, "no_model_calls":True,
       "total_physical_actions":len(rows)*5*CHARGED_ACTIONS,
       "actions_per_policy_per_world":CHARGED_ACTIONS,
       "max_python_traced_bytes":peak,
       "cohort_accuracy":{
           group:{name:round(avg(rows[start:end],name),6) for name in
                  ("lookahead","greedy","round_robin","random","conventional")}
           for group,start,end in (
               ("stationary",0,8),("routing",8,12),("out_of_grammar",12,16))
       },
       "worlds":rows,
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
