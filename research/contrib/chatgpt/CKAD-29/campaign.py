"""CKAD29: frozen native causal composition/retention development experiment.

Source-only synthetic fixtures, not a real-world causal-learning qualification.
Only public [context, action, consequence] tuples reach NativeCumulativeLearner.
Source-hidden primitive law and held consequences are never learner inputs.
"""
import argparse
import hashlib
import itertools
import json
import math
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_property_knowledge import NativePropertyKnowledge

HERE = Path(__file__).resolve().parent
SEEDS = (404, 505, 606)
PAIR = tuple(itertools.combinations(range(5), 2))
SLOTS = 9
TRAIN = 16
GRAPHS = ("xor3", "majority3")
SCHEMA = "yggdrasil.ckad29.composition.v1"


def seed_int(*keys):
    raw = hashlib.sha256(canonical(["ckad29", *keys])).digest()
    return int.from_bytes(raw[:8], "big")


def rule(seed, slot):
    """Private generator-only truth law; no inference method receives its ID."""
    r = random.Random(seed_int("hidden-law", seed, slot))
    return r.randrange(2), r.randrange(32), r.randrange(11)


def outcome(spec, x):
    intercept, linear, quadratic = spec
    value = intercept ^ ((x & linear).bit_count() & 1)
    if quadratic:
        i, j = PAIR[quadratic-1]
        value ^= ((x >> i) & 1) & ((x >> j) & 1)
    return value


def split(seed):
    values = list(range(32))
    random.Random(seed_int("split", seed)).shuffle(values)
    return tuple(values[:TRAIN]), tuple(values[TRAIN:])


def row(x, y):
    return [x & 15, x >> 4, y]


def source_rows(seed, slot, inputs):
    spec = rule(seed, slot)
    return [row(x, outcome(spec, x)) for x in inputs]


def fixed_property():
    raw = NativePropertyKnowledge("ckad29", entities=1, context_bits=4).checkpoint()
    return raw, digest(raw)


def candidate_model():
    raw, pin = fixed_property()
    return NativeCumulativeLearner(raw, pin)


def fit_native(model, slot, rows, seed):
    packet = canonical(rows)
    ref = digest(canonical(["ckad29/public-source", seed, slot, digest(packet)]))
    return model.observe(slot, rows, digest(packet), source_ref=ref)


def native_probability(model, slot, x):
    value = model.predict(slot, x & 15, x >> 4)
    if value is None:
        return 0.5
    if value not in (0, 1):
        raise AssertionError("Native prediction is non-binary")
    return float(value)


def features(x):
    bits = [float((x >> i) & 1) for i in range(5)]
    return [1.0] + bits + [bits[i]*bits[j] for i, j in PAIR]


def fit_logistic(rows):
    """Fixed fully fitted polynomial logistic baseline, same revealed evidence."""
    data = [(features(context | (action << 4)), float(y)) for context,action,y in rows]
    weights = [0.0]*16
    for iteration in range(1200):
        gradient = [0.0]*16
        for phi, y in data:
            z = sum(a*b for a,b in zip(phi, weights))
            prediction = 1/(1+math.exp(-max(-40., min(40., z))))
            for j in range(16):
                gradient[j] += (prediction-y)*phi[j]
        rate = 0.18 / (1 + iteration/500)
        weights = [w - rate*(g/len(data) + (0 if j==0 else 0.02*w))
                   for j,(w,g) in enumerate(zip(weights,gradient))]
    return tuple(weights)


def logistic_probability(weights, x):
    z = sum(a*b for a,b in zip(weights,features(x)))
    return 1/(1+math.exp(-max(-40.,min(40.,z))))


def frequency_probability(rows, x):
    matched = [y for context,action,y in rows if context | (action<<4) == x]
    return (1+sum(matched))/(2+len(matched))


def exact_probability(rows, x):
    """Uniform Bayesian mixture over 704 disclosed finite Boolean grammar entries."""
    compatible = 0
    ones = 0
    for intercept in range(2):
        for linear in range(32):
            for quadratic in range(11):
                spec=(intercept,linear,quadratic)
                if all(outcome(spec, context | (action<<4)) == y
                       for context,action,y in rows):
                    compatible += 1
                    ones += outcome(spec, x)
    # Grammar is complete for each generated world; source consistency required.
    if not compatible:
        raise AssertionError("Exact Bayesian grammar has no compatible law")
    return ones/compatible


def compose(graph, values):
    a,b,c = values
    if graph == "xor3":
        return a+b+c-2*(a*b+a*c+b*c)+4*a*b*c
    if graph == "majority3":
        return a*b+a*c+b*c-2*a*b*c
    raise AssertionError("Unknown public graph")


def scored(seed):
    train, held = split(seed)
    model = candidate_model()
    sources = [source_rows(seed, slot, train) for slot in range(9)]
    for slot in range(3):
        model = fit_native(model, slot, sources[slot], seed)
    before = {(slot,x):native_probability(model,slot,x)
              for slot in range(3) for x in held}
    original_sha = digest(model.checkpoint())
    for slot in range(3,9):
        model = fit_native(model, slot, sources[slot], seed)
    after = {(slot,x):native_probability(model,slot,x)
             for slot in range(3) for x in held}
    if before != after:
        raise AssertionError("Primitive forecasts mutated after independent learning")
    raw=model.checkpoint()
    restored=NativeCumulativeLearner.restore(raw,digest(raw))
    if restored.checkpoint()!=raw or any(
        native_probability(restored,slot,x)!=before[slot,x]
        for slot in range(3) for x in held):
        raise AssertionError("Cold restore/persistent retention mismatch")
    control_weights=[fit_logistic(sources[slot]) for slot in range(3)]
    metrics={arm:{"squared_error":0.0,"correct":0,"cases":0}
             for arm in ("native_composed","fitted_logistic","fitted_frequency",
                         "exact_bayesian","no_composition_sham")}
    old_coverage=sum(int(before[slot,x]!=0.5) for slot in range(3) for x in held)
    for x in held:
        truth=[outcome(rule(seed,slot),x) for slot in range(3)]
        predictions={
            "native_composed":[before[slot,x] for slot in range(3)],
            "fitted_logistic":[logistic_probability(control_weights[slot],x) for slot in range(3)],
            "fitted_frequency":[frequency_probability(sources[slot],x) for slot in range(3)],
            "exact_bayesian":[exact_probability(sources[slot],x) for slot in range(3)],
            "no_composition_sham":[0.5,0.5,0.5],
        }
        for graph in GRAPHS:
            actual=int(sum(truth)%2==1) if graph=="xor3" else int(sum(truth)>=2)
            for arm, three in predictions.items():
                p=compose(graph,three)
                if not -1e-12 <= p <= 1+1e-12:
                    raise AssertionError("Composed forecast out of bounds")
                p=max(0.,min(1.,p))
                metrics[arm]["squared_error"]+=(p-actual)**2
                metrics[arm]["correct"]+=int((p>=0.5)==actual)
                metrics[arm]["cases"]+=1
    metrics={arm:{"brier":round(v["squared_error"]/v["cases"],10),
                  "accuracy":round(v["correct"]/v["cases"],10),"cases":v["cases"]}
             for arm,v in metrics.items()}
    # Negative control on an isolated clone: contradicted old witness quarantines
    # the affected slot, without changing any other learned slot.
    contradiction=source_rows(seed,0,train)[:1]
    contradiction[0][2]^=1
    quarantined=fit_native(restored,0,contradiction,seed+9000)
    if not quarantined.info()["quarantined"][0] or any(
        native_probability(quarantined,slot,x)!=before[slot,x]
        for slot in (1,2) for x in held):
        raise AssertionError("Local contradiction safety control failed")
    return {"seed":seed,"metrics":metrics,
            "native_primitive_held_coverage":old_coverage/(3*len(held)),
            "original_checkpoint_sha256":original_sha,
            "full_checkpoint_sha256":digest(raw),
            "cold_restore_exact":True,"old_prediction_retention_exact":True,
            "contradiction_quarantine_local":True,
            "revealed_source_rows":9*len(train),
            "held_composite_cases":len(held)*len(GRAPHS)}


def classify(cases):
    by_arm={arm:sum(c["metrics"][arm]["brier"] for c in cases)/len(cases)
            for arm in cases[0]["metrics"]}
    native=by_arm["native_composed"]
    strongest=min(by_arm["fitted_logistic"],by_arm["fitted_frequency"])
    exact=by_arm["exact_bayesian"]
    per_seed=sum(c["metrics"]["native_composed"]["brier"]<
                 min(c["metrics"]["fitted_logistic"]["brier"],
                     c["metrics"]["fitted_frequency"]["brier"]) for c in cases)
    full=all(c["old_prediction_retention_exact"] and c["cold_restore_exact"]
             and c["contradiction_quarantine_local"] for c in cases)
    supported=(native<=strongest-0.03 and native<=exact+0.02
               and per_seed>=2 and full)
    mixed=(native<=strongest-0.01 and not supported)
    return {"decision":"DEVELOPMENT_GO" if supported else
            "DEVELOPMENT_MIXED" if mixed else "DEVELOPMENT_NO_GO",
            "mean_brier_equal_seed":{k:round(v,10) for k,v in by_arm.items()},
            "strongest_conventional_brier":round(strongest,10),
            "exact_bayes_brier":round(exact,10),
            "native_minus_strongest_conventional":round(native-strongest,10),
            "native_minus_exact":round(native-exact,10),
            "per_seed_native_beats_strongest":per_seed,
            "scientific_pass":False,"accepted_native":False,"deployment":"NONE"}


def verify_lock():
    locked=json.loads((HERE/"source_lock.json").read_text())
    raw=Path(__file__).read_bytes()
    h=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\\0"+raw).hexdigest()
    if h!=locked["campaign_blob_sha1"]:
        raise AssertionError("Pre-first-use committed source lock mismatch")
    if locked["prereg_commit"]!="022d7477de56bb2793b52d2ae3a02e86bbf73bdd":
        raise AssertionError("Preregistration lineage mismatch")
    return locked


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("preflight","score"),default="preflight")
    args=parser.parse_args()
    lock=verify_lock()
    if args.mode=="preflight":
        # No source world, evaluation label, or candidate fitting is accessed.
        assert len(PAIR)==10 and 9<=16 and TRAIN==16
        print(json.dumps({"schema":SCHEMA,"mode":"preflight","status":"PASS",
                          "prereg_commit":lock["prereg_commit"],"B_scored":False},sort_keys=True))
        return
    start=time.perf_counter()
    cases=[scored(seed) for seed in SEEDS]
    summary=classify(cases)
    out={"schema":SCHEMA,"source_lock":lock,"cases":cases,
         "summary":summary,"training_rows":sum(c["revealed_source_rows"] for c in cases),
         "held_cases":sum(c["held_composite_cases"] for c in cases),
         "wall_seconds":round(time.perf_counter()-start,5),
         "native_model_mutated":False,"protected_first_use":False}
    print(json.dumps(out,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
