"""CKAD32: source-only causal tournament choosing actual interventions, research-only.

A complete 2880-law *conventional* grammar is supplied to EVERY proposal
control. A 24-law hash committee estimates disagreement, then the native
cumulative learner observes only the selected action consequences. Never
describe this supplied causal grammar as native discovery or SCIENTIFIC_PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_property_knowledge import NativePropertyKnowledge

HERE = Path(__file__).resolve().parent
C30_PATH = HERE.parent / "CKAD-30" / "campaign.py"
SPEC = importlib.util.spec_from_file_location("ckad32_frozen_ckad30_controls", C30_PATH)
C30 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C30)

SCHEMA = "yggdrasil.ckad32.causal-tournaments.v1"
PREREG_SHA = "fe11284f07f13ad218e014536075b73f2042e7c0"
PILOT = (9451, 9452)
PRIMARY = (1451, 1452, 1453)
POLICIES = ("bounded_committee24", "uniform_random", "fixed_public_order",
            "full_exact_information_gain")
READOUTS = ("native_original", "native_sparse", "bayes_2880",
            "polynomial_logistic", "smoothed_frequency", "sham")
GRAPHS = ("xor3", "majority3", "gate3")
HELD = 12
INITIAL = 6
PROBES = 10
COMMITTEE = 24
OLD_SLOTS = 3
PRESSURE_SLOTS = 6


def seed_int(*parts):
    d = hashlib.sha256(canonical(["ckad32-disjoint-causal-interventions-v1", *parts])).digest()
    return int.from_bytes(d[:8], "big")


def hidden_law(seed, slot):
    """Evaluator/revealer only; NEVER pass this tuple to any policy/model fit."""
    r = random.Random(seed_int("hidden-generator", seed, slot))
    x, y = r.sample(range(10), 2)
    return r.randrange(2), r.randrange(32), x, y


def reveal(seed, slot, x):
    """Simulates a real observed action consequence; one invocation per query."""
    return C30.effect(hidden_law(seed, slot), x)


def input_partition(seed):
    xs = list(range(32))
    random.Random(seed_int("public-held-partition", seed)).shuffle(xs)
    held = tuple(xs[:HELD])
    initial = tuple(xs[HELD:HELD + INITIAL])
    pool = tuple(xs[HELD + INITIAL:])
    if (len(held), len(initial), len(pool)) != (12, 6, 14):
        raise AssertionError("CKAD32_PARTITION_WIDTH")
    if len(set(held+initial+pool)) != 32:
        raise AssertionError("CKAD32_PARTITION_OVERLAP")
    return held, initial, pool


def row(x, y):
    return [x & 15, x >> 4, y]


def public_rows(seed, slot, xs):
    return [row(x, reveal(seed, slot, x)) for x in xs]


def law_key(seed, slot, step, law):
    return seed_int("committee-hash", seed, slot, step, *law)


def survivor_posterior(rows):
    return C30.posterior(rows)


def select_probe(policy, seed, slot, step, pool, survivors):
    """Input proposals inspect posterior predictions only, never actual outcomes."""
    if not pool or not survivors or step < 0 or step >= PROBES:
        raise ValueError("CKAD32_POLICY_INPUT_INVALID")
    available = tuple(pool)
    if policy == "uniform_random":
        choice = random.Random(seed_int("random-proposal",seed,slot,step)).choice(available)
        return choice, {"committee_size":0, "disagreement":None}
    if policy == "fixed_public_order":
        return min(available), {"committee_size":0, "disagreement":None}
    if policy not in ("bounded_committee24","full_exact_information_gain"):
        raise ValueError("CKAD32_POLICY_UNKNOWN")
    if policy == "bounded_committee24":
        active = sorted(survivors, key=lambda law: (law_key(seed,slot,step,law),law))[:COMMITTEE]
    else:
        active = survivors
    def priority(x):
        positive = sum(C30.effect(law,x) for law in active)
        uncertainty = positive*(len(active)-positive)  # no floating-point drift
        return (-uncertainty, seed_int("tie-probe",seed,slot,step,x), x)
    choice = min(available,key=priority)
    positive = sum(C30.effect(law,choice) for law in active)
    return choice, {"committee_size":len(active),
                    "disagreement":round(positive*(len(active)-positive) /
                                         (len(active)*len(active)), 10)}


def intervention_stream(policy, seed, slot, initial, pool):
    rows = public_rows(seed,slot,initial)
    survivors = survivor_posterior(rows)
    if not survivors:
        raise AssertionError("CKAD32_INITIAL_GRAMMAR_EMPTY")
    remaining = tuple(pool)
    history = []
    initial_count = len(survivors)
    for step in range(PROBES):
        x, meta = select_probe(policy,seed,slot,step,remaining,survivors)
        if x not in remaining:
            raise AssertionError("CKAD32_INVALID_PUBLIC_ACTION")
        old_count = len(survivors)
        # Exactly one source outcome is revealed after selection; never peek
        # at a different candidate before the proposal is fixed.
        y = reveal(seed,slot,x)
        rows.append(row(x,y))
        survivors = tuple(l for l in survivors if C30.effect(l,x)==y)
        if not survivors:
            raise AssertionError("CKAD32_TRUE_SOURCE_OUTSIDE_GRAMMAR")
        remaining = tuple(a for a in remaining if a != x)
        history.append({
            "step":step,"public_input":x,"revealed_consequence":y,
            "survivors_before":old_count,"survivors_after":len(survivors),
            "committee_size":meta["committee_size"],
            "disagreement":meta["disagreement"]
        })
    if len(rows)!=16 or len(history)!=10 or len(set(a["public_input"] for a in history))!=10:
        raise AssertionError("CKAD32_INTERVENTION_BUDGET")
    return rows, survivors, {"initial_survivors":initial_count,
                             "final_survivors":len(survivors),
                             "probes":history}


def new_native():
    raw = NativePropertyKnowledge("ckad32",entities=1,context_bits=4).checkpoint()
    return NativeCumulativeLearner(raw,digest(raw))


def observe(model,seed,policy,slot,rows):
    raw=canonical(rows)
    source_ref=digest(canonical(["ckad32/public-action-consequence",seed,policy,slot,digest(raw)]))
    return model.observe(slot,rows,digest(raw),source_ref=source_ref)


def native_prediction(model,slot,x):
    result=model.predict(slot,x & 15,x >> 4)
    if result is None:return 0.5
    if type(result) is not int or result not in (0,1):
        raise ValueError("CKAD32_NONBOOLEAN_NATIVE_PREDICTION")
    return float(result)


def train_native(seed, policy, old_rows,held):
    native=new_native()
    for slot in range(OLD_SLOTS):
        native=observe(native,seed,policy,slot,old_rows[slot])
    repaired,solver=C30.fit_repaired(native)
    forecasts={}
    before_sha={}
    for name,model in (("native_original",native),("native_sparse",repaired)):
        forecasts[name]=[[native_prediction(model,slot,x) for x in held] for slot in range(OLD_SLOTS)]
        before_sha[name]=digest(model.checkpoint())
    # Independent interference witnesses: the same public source for every policy.
    pressure_input=tuple(range(16))
    pressure=[public_rows(seed,slot,pressure_input) for slot in range(3,9)]
    for offset,rows in enumerate(pressure):
        slot=offset+3
        native=observe(native,seed,policy,slot,rows)
        repaired=observe(repaired,seed,policy,slot,rows)
    final_sha={}
    restored={}
    for name,model in (("native_original",native),("native_sparse",repaired)):
        raw=model.checkpoint()
        final_sha[name]=digest(raw)
        restored[name]=NativeCumulativeLearner.restore(raw,digest(raw))
        if restored[name].checkpoint()!=raw:
            raise AssertionError("CKAD32_COLD_RESTORE_DRIFT")
        if any(native_prediction(restored[name],slot,x)!=forecasts[name][slot][i]
               for slot in range(OLD_SLOTS) for i,x in enumerate(held)):
            raise AssertionError("CKAD32_CUMULATIVE_MEMORY_INTERFERENCE")
        for slot in range(9):
            wanted=old_rows[slot] if slot<3 else pressure[slot-3]
            if {tuple(r) for r in restored[name]._rows(slot)}!={tuple(r) for r in wanted}:
                raise AssertionError("CKAD32_PUBLIC_SOURCE_WITNESS_DRIFT")
    conflict=[list(old_rows[0][0])]
    conflict[0][2]^=1
    q=observe(restored["native_sparse"],seed+90000,policy,0,conflict)
    if not q.info()["quarantined"][0] or any(
        native_prediction(q,slot,x)!=forecasts["native_sparse"][slot][i]
        for slot in (1,2) for i,x in enumerate(held)
    ):
        raise AssertionError("CKAD32_SCOPED_CONTRADICTION_FAILURE")
    return forecasts,{
        "before_sha256":before_sha,"cold_sha256":final_sha,
        "cold_restore_exact":True,"retention_exact":True,
        "quarantine_exact":True,
        "solver_attempts":sum(x["attempted"] for x in solver),
        "solver_eligible":sum(x["attempted"] and x["eligible"] for x in solver),
        "solver":solver
    }


def score_policy(seed,policy,held,initial,pool):
    streams=[intervention_stream(policy,seed,s,initial,pool) for s in range(OLD_SLOTS)]
    old_rows=[s[0] for s in streams]
    posterior=[s[1] for s in streams]
    counts=[s[2] for s in streams]
    base,checks=train_native(seed,policy,old_rows,held)
    fitted=[C30.fit_logistic(old_rows[s]) for s in range(OLD_SLOTS)]
    stats={arm:{"squared":0.,"cases":0} for arm in READOUTS}
    held_primitive_coverage={arm:0 for arm in ("native_original","native_sparse")}
    held_primitive_wrong={arm:0 for arm in ("native_original","native_sparse")}
    for i,x in enumerate(held):
        truth=[reveal(seed,slot,x) for slot in range(OLD_SLOTS)] # evaluator only
        triple={
            "native_original":[base["native_original"][s][i] for s in range(3)],
            "native_sparse":[base["native_sparse"][s][i] for s in range(3)],
            "bayes_2880":[C30.bayes_prob(posterior[s],x) for s in range(3)],
            "polynomial_logistic":[C30.logistic_prob(fitted[s],x) for s in range(3)],
            "smoothed_frequency":[C30.frequency_prob(old_rows[s],x) for s in range(3)],
            "sham":[0.5]*3
        }
        for name in held_primitive_coverage:
            for s in range(3):
                if triple[name][s]!=0.5:
                    held_primitive_coverage[name]+=1
                    held_primitive_wrong[name]+=int(triple[name][s]!=truth[s])
        for graph in GRAPHS:
            target=C30.composition(graph,truth)
            for arm,values in triple.items():
                p=C30.composition(graph,values)
                if not -1e-12<=p<=1+1e-12:
                    raise AssertionError("CKAD32_INVALID_COMPOSITION_PROBABILITY")
                stats[arm]["squared"]+=(max(0.,min(1.,p))-target)**2
                stats[arm]["cases"]+=1
    metrics={name:{"brier":round(v["squared"]/v["cases"],10),"cases":v["cases"]}
             for name,v in stats.items()}
    return {
        "policy":policy,"source_rows":144,"old_source_rows":48,"pressure_rows":96,
        "held_composite_cases":len(held)*len(GRAPHS),
        "metrics":metrics,
        "primitive_coverage":{k:round(v/(3*len(held)),10)
                              for k,v in held_primitive_coverage.items()},
        "primitive_wrong":held_primitive_wrong,
        "posterior_survivors":[len(p) for p in posterior],
        "streams":counts,"model":checks,
        "observed_source":[old_rows[s] for s in range(3)]
    }


def score_seed(seed):
    if seed not in PILOT+PRIMARY:raise ValueError("CKAD32_SEED_UNREGISTERED")
    start=time.perf_counter()
    cpu=time.process_time()
    held, initial, pool=input_partition(seed)
    results={policy:score_policy(seed,policy,held,initial,pool) for policy in POLICIES}
    return {
        "seed":seed,"shared_held_inputs":list(held),
        "shared_initial_inputs":list(initial),"legal_probe_inputs":list(pool),
        "policy_results":results,
        "cpu_seconds":round(time.process_time()-cpu,6),
        "wall_seconds":round(time.perf_counter()-start,6),
        "primary_first_use":False
    }


def screen(cases):
    if tuple(c["seed"] for c in cases)!=PILOT:
        raise AssertionError("CKAD32_PILOT_ORDER")
    if any(not all(
        z["model"]["cold_restore_exact"] and z["model"]["retention_exact"] and z["model"]["quarantine_exact"]
        for z in c["policy_results"].values()
    ) for c in cases):
        return {"decision":"INVALID","screen_go":False}
    witness=any(
        c["policy_results"]["bounded_committee24"]["metrics"]["native_sparse"]["brier"]
        <= min(c["policy_results"][p]["metrics"]["native_sparse"]["brier"]
               for p in ("uniform_random","fixed_public_order"))-.025
        and sum(c["policy_results"]["bounded_committee24"]["posterior_survivors"])/3
        <= sum(c["policy_results"]["uniform_random"]["posterior_survivors"])/3
        for c in cases
    )
    return {"decision":"PILOT_GO" if witness else "SCREEN_NO_GO","screen_go":witness}


def source_lock():
    meta=json.loads((HERE/"source_lock.json").read_text())
    data=Path(__file__).read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if meta["campaign_blob_sha1"]!=sha or meta["prereg_commit"]!=PREREG_SHA:
        raise AssertionError("CKAD32_SOURCE_BLOB_PIN_FAILURE")
    return meta


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("preflight","pilot"),required=True)
    parser.add_argument("--seed",type=int)
    args=parser.parse_args()
    lock=source_lock()
    if args.mode=="preflight":
        if args.seed is not None:raise ValueError("CKAD32_PREFLIGHT_NO_SEED")
        assert 2*32*len(C30.PAIR_CHOICES)==2880
        assert len(set(PILOT+PRIMARY))==5
        assert all(C30.composition(g,x) in (0,1)
                   for g in GRAPHS for x in itertools.product((0,1),repeat=3))
        print(json.dumps({"schema":SCHEMA,"mode":"preflight","lock":lock,
                          "status":"PASS","primary_scored":False},sort_keys=True))
    else:
        if args.seed not in PILOT:raise ValueError("CKAD32_PILOT_UNAUTHORIZED_SEED")
        print(json.dumps({"schema":SCHEMA,"mode":"pilot","seed":args.seed,"lock":lock,
                          "case":score_seed(args.seed),"primary_scored":False},
                         sort_keys=True,indent=2))


if __name__=="__main__":
    main()
