"""CKAD30: bounded external test of *existing* native sparse repair on novel two-interaction laws.

FROZEN: no accepted-model edits, no protected first-use, no scoring of CKAD29 cohort.
All model observations contain only public (context, action, consequence) witnesses.
The world generator's hidden mask is used exclusively for evaluator truth generation.
"""
import argparse
import hashlib
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_degree_hypothesis import NativeDegreeHypothesis
from yggdrasil.native_property_knowledge import NativePropertyKnowledge

HERE = Path(__file__).resolve().parent
SCHEMA = "yggdrasil.ckad30.two-interaction-repair.v1"
PREREG_COMMIT = "d320fb29b5cd186a71f09a5bc01de2e2ce5ffa38"
PILOT = (9101, 9102)
PRIMARY = (707, 808, 909)
PAIRS = tuple(itertools.combinations(range(5), 2))
PAIR_CHOICES = tuple(itertools.combinations(range(10), 2))
GRAPHS = ("xor3", "majority3", "gate3")
INPUT_COUNT = 32
TRAIN_COUNT = 16
SLOTS = 9
ARMS = ("native_original", "native_sparse_repair", "polynomial_logistic",
        "smoothed_frequency", "exact_2880_bayes", "uninformative_sham")


def seed_int(*keys):
    raw = hashlib.sha256(canonical(["ckad30-original-two-interaction-v1", *keys])).digest()
    return int.from_bytes(raw[:8], "big")


def hidden_law(seed, slot):
    """Generator/evaluator only. NEVER call from fit/readout/control functions."""
    r = random.Random(seed_int("private-law", seed, slot))
    return r.randrange(2), r.randrange(32), *r.sample(range(10), 2)


def effect(law, x):
    intercept, linear, first, second = law
    p, q = PAIRS[first], PAIRS[second]
    return (intercept ^ ((x & linear).bit_count() & 1)
            ^ (((x >> p[0]) & 1) & ((x >> p[1]) & 1))
            ^ (((x >> q[0]) & 1) & ((x >> q[1]) & 1)))


def partition(seed):
    order = list(range(INPUT_COUNT))
    random.Random(seed_int("disjoint-partition", seed)).shuffle(order)
    return tuple(order[:TRAIN_COUNT]), tuple(order[TRAIN_COUNT:])


def observed_rows(seed, slot, train):
    law = hidden_law(seed, slot)
    return [[x & 15, x >> 4, effect(law, x)] for x in train]


def learner():
    prop = NativePropertyKnowledge("ckad30", entities=1, context_bits=4).checkpoint()
    return NativeCumulativeLearner(prop, digest(prop))


def observe(m, seed, slot, rows):
    blob = canonical(rows)
    source_ref = digest(canonical(["ckad30/public-intervention", seed, slot, digest(blob)]))
    return m.observe(slot, rows, digest(blob), source_ref=source_ref)


def readout(m, slot, x):
    y = m.predict(slot, x & 15, x >> 4)
    if y is None:
        return 0.5
    if type(y) is not int or y not in (0, 1):
        raise ValueError("CKAD30_UNEXPECTED_NONBOOLEAN_READOUT")
    return float(y)


def fit_repaired(m):
    solver = []
    for slot in range(3):
        h = m._hypotheses[slot]  # existing native state; no hidden evaluator query
        if type(h) is NativeDegreeHypothesis and not h.eligible:
            candidate, fitted, cost = m.repair_sparse(slot)
            solver.append({"slot": slot, "attempted": True,
                           "eligible": fitted.eligible, "cost": cost})
            m = candidate
        else:
            solver.append({"slot": slot, "attempted": False,
                           "reason": "degree_eligible_or_other", "eligible": False})
    return m, solver


def features(x):
    bits = [float((x >> i) & 1) for i in range(5)]
    return [1.0] + bits + [bits[i] * bits[j] for i, j in PAIRS]


def fit_logistic(rows):
    data = [(features(c | (a << 4)), float(y)) for c, a, y in rows]
    weights = [0.0] * 16
    for t in range(1200):
        grad = [0.0] * 16
        for phi, y in data:
            z = sum(w * p for w, p in zip(weights, phi))
            pred = 1 / (1 + math.exp(-max(-40.0, min(40.0, z))))
            for j in range(16):
                grad[j] += (pred - y) * phi[j]
        lr = .18 / (1 + t / 500)
        weights = [w - lr * (g / len(data) + (0 if i == 0 else .02 * w))
                   for i, (w, g) in enumerate(zip(weights, grad))]
    return tuple(weights)


def logistic_prob(weights, x):
    z = sum(w * f for w, f in zip(weights, features(x)))
    return 1 / (1 + math.exp(-max(-40., min(40., z))))


def frequency_prob(rows, x):
    matched = [y for c, a, y in rows if (c | (a << 4)) == x]
    return (1 + sum(matched)) / (2 + len(matched))


def posterior(rows):
    """Complete declared 2880-law exact Bayesian control, trained on rows only."""
    compatible = []
    for intercept in range(2):
        for linear in range(32):
            for p, q in PAIR_CHOICES:
                law = (intercept, linear, p, q)
                if all(effect(law, c | (a << 4)) == y for c, a, y in rows):
                    compatible.append(law)
    if not compatible:
        raise AssertionError("CKAD30_EXACT_BAYES_EMPTY_MISSPECIFIED")
    return tuple(compatible)


def bayes_prob(laws, x):
    return sum(effect(law, x) for law in laws) / len(laws)


def composition(name, v):
    a, b, c = v
    if name == "xor3":
        return a+b+c-2*(a*b+a*c+b*c)+4*a*b*c
    if name == "majority3":
        return a*b+a*c+b*c-2*a*b*c
    if name == "gate3":
        return a*b+c-2*a*b*c
    raise AssertionError("CKAD30_GRAPH_UNKNOWN")


def run_seed(seed):
    if seed not in PILOT + PRIMARY:
        raise ValueError("CKAD30_UNREGISTERED_SEED")
    t0, cpu0 = time.perf_counter(), time.process_time()
    train, held = partition(seed)
    if set(train) & set(held) or len(train) != 16 or len(held) != 16:
        raise AssertionError("CKAD30_SPLIT_INVALID")
    sources = [observed_rows(seed, slot, train) for slot in range(SLOTS)]
    native = learner()
    for slot in range(3):
        native = observe(native, seed, slot, sources[slot])
    raw_before = native.checkpoint()
    repaired, solver = fit_repaired(native)
    before = {
        "native_original": [[readout(native, slot, x) for x in held] for slot in range(3)],
        "native_sparse_repair": [[readout(repaired, slot, x) for x in held] for slot in range(3)],
    }
    original_old_sha = digest(raw_before)
    repair_old_sha = digest(repaired.checkpoint())
    for slot in range(3, SLOTS):
        native = observe(native, seed, slot, sources[slot])
        repaired = observe(repaired, seed, slot, sources[slot])
    def check_cold(m):
        raw = m.checkpoint()
        cold = NativeCumulativeLearner.restore(raw, digest(raw))
        if cold.checkpoint() != raw:
            raise AssertionError("CKAD30_COLD_CHECKPOINT_MISMATCH")
        return cold, digest(raw)
    n_cold, n_sha = check_cold(native)
    r_cold, r_sha = check_cold(repaired)
    if any(
        readout(m, slot, x) != before[arm][slot][i]
        for arm, m in (("native_original", n_cold),
                       ("native_sparse_repair", r_cold))
        for slot in range(3) for i, x in enumerate(held)
    ):
        raise AssertionError("CKAD30_PRIMITIVE_INTERFERENCE")
    # Both observed ledgers must retain the exact same sixteen public witnesses.
    for slot in range(SLOTS):
        a = {tuple(x) for x in n_cold._rows(slot)}
        b = {tuple(x) for x in r_cold._rows(slot)}
        wanted = {tuple(x) for x in sources[slot]}
        if a != b or a != wanted:
            raise AssertionError("CKAD30_NATIVE_WITNESS_DRIFT")
    logit = [fit_logistic(sources[slot]) for slot in range(3)]
    bayes = [posterior(sources[slot]) for slot in range(3)]
    metrics = {arm: {"sum_squared": 0., "correct": 0, "cases": 0}
               for arm in ARMS}
    coverage = {
        arm: sum(before[arm][slot][i] != .5 for slot in range(3)
                 for i in range(len(held))) / (3*len(held))
        for arm in ("native_original", "native_sparse_repair")
    }
    for i, x in enumerate(held):
        truth = [effect(hidden_law(seed, slot), x) for slot in range(3)]
        probs = {
            "native_original": [before["native_original"][slot][i] for slot in range(3)],
            "native_sparse_repair": [before["native_sparse_repair"][slot][i] for slot in range(3)],
            "polynomial_logistic": [logistic_prob(logit[slot], x) for slot in range(3)],
            "smoothed_frequency": [frequency_prob(sources[slot], x) for slot in range(3)],
            "exact_2880_bayes": [bayes_prob(bayes[slot], x) for slot in range(3)],
            "uninformative_sham": [.5,.5,.5],
        }
        for graph in GRAPHS:
            actual = composition(graph, truth)
            for arm, triple in probs.items():
                p = composition(graph, triple)
                if not (-1.e-12 <= p <= 1+1.e-12):
                    raise AssertionError("CKAD30_PROBABILITY_RANGE")
                p = min(1., max(0., p))
                metrics[arm]["sum_squared"] += (p-actual)**2
                metrics[arm]["correct"] += int((p >= .5) == actual)
                metrics[arm]["cases"] += 1
    for arm, v in metrics.items():
        v["brier"] = round(v.pop("sum_squared") / v["cases"], 10)
        v["accuracy"] = round(v["correct"] / v["cases"], 10)
    # Negative safety control isolated clone; old sibling predictions must survive.
    contradictory = [list(sources[0][0])]
    contradictory[0][2] ^= 1
    quarantined = observe(r_cold, seed+9000, 0, contradictory)
    if not quarantined.info()["quarantined"][0] or any(
        readout(quarantined, slot, x) != before["native_sparse_repair"][slot][i]
        for slot in (1, 2) for i, x in enumerate(held)
    ):
        raise AssertionError("CKAD30_LOCAL_QUARANTINE_FAILURE")
    return {
        "seed": seed, "source_rows": SLOTS * TRAIN_COUNT,
        "held_composite_cases": len(held) * len(GRAPHS),
        "metrics": metrics, "coverage": coverage,
        "solver": solver, "candidate_repair_attempts": sum(x["attempted"] for x in solver),
        "candidate_repairs_eligible": sum(x["attempted"] and x["eligible"] for x in solver),
        "old_checkpoint_sha256": {"native_original":original_old_sha,
                                   "native_sparse_repair":repair_old_sha},
        "cold_checkpoint_sha256":{"native_original":n_sha,
                                 "native_sparse_repair":r_sha},
        "old_primitive_retention_exact":True,
        "cold_restore_exact":True,
        "local_quarantine_exact":True,
        "posterior_law_counts":[len(z) for z in bayes],
        "wall_seconds":round(time.perf_counter()-t0,6),
        "cpu_seconds":round(time.process_time()-cpu0,6),
    }


def screen(cases):
    if tuple(x["seed"] for x in cases) != PILOT:
        raise AssertionError("CKAD30_SCREEN_SEED_ORDER")
    if any(not (x["old_primitive_retention_exact"] and x["cold_restore_exact"]
                and x["local_quarantine_exact"]) for x in cases):
        return False
    return any(
        x["metrics"]["native_original"]["brier"] -
        x["metrics"]["native_sparse_repair"]["brier"] >= .03
        and x["coverage"]["native_sparse_repair"]-x["coverage"]["native_original"] >= .20
        for x in cases
    )


def classification(cases):
    if tuple(x["seed"] for x in cases) != PRIMARY:
        raise AssertionError("CKAD30_PRIMARY_SEEDS")
    mean = {arm:sum(x["metrics"][arm]["brier"] for x in cases)/len(cases)
            for arm in ARMS}
    n = mean["native_sparse_repair"]
    ctrl = min(mean["polynomial_logistic"],mean["smoothed_frequency"])
    by_seed = sum(
        x["metrics"]["native_sparse_repair"]["brier"] <
        min(x["metrics"]["native_original"]["brier"],
            x["metrics"]["polynomial_logistic"]["brier"],
            x["metrics"]["smoothed_frequency"]["brier"])
        for x in cases)
    gains=[x["coverage"]["native_sparse_repair"]-x["coverage"]["native_original"]
           for x in cases]
    go=(n<=mean["native_original"]-.05 and n<=ctrl-.05 and
        n<=mean["exact_2880_bayes"]+.03 and by_seed>=2 and
        sum(gains)/len(gains)>=.30 and
        all(x["old_primitive_retention_exact"] and x["cold_restore_exact"]
            and x["local_quarantine_exact"] for x in cases))
    mixed=(not go and n<=mean["native_original"]-.02)
    return {
        "decision":"DEVELOPMENT_GO" if go else "DEVELOPMENT_MIXED" if mixed
                   else "DEVELOPMENT_NO_GO",
        "mean_held_brier":{k:round(v,10) for k,v in mean.items()},
        "strongest_conventional_brier":round(ctrl,10),
        "mean_coverage_improvement":round(sum(gains)/len(gains),10),
        "seeds_beat_native_and_fitted_controls":by_seed,
        "scientific_pass":False, "accepted_native":False, "deployment":"NONE",
    }


def verify_source_lock():
    lock = json.loads((HERE/"source_lock.json").read_text(encoding="utf8"))
    data = Path(__file__).read_bytes()
    sha = hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if lock.get("campaign_blob_sha1") != sha or lock.get("prereg_commit") != PREREG_COMMIT:
        raise AssertionError("CKAD30_UNPINNED_CAMPAIGN")
    return lock


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("preflight","pilot","primary"),required=True)
    parser.add_argument("--seed",type=int)
    args = parser.parse_args()
    lock = verify_source_lock()
    if args.mode == "preflight":
        assert len(PAIRS)==10 and len(PAIR_CHOICES)==45 and (2*32*len(PAIR_CHOICES))==2880
        assert set(PRIMARY).isdisjoint(PILOT)
        assert all(composition(g, x) in (0,1)
                   for g in GRAPHS for x in itertools.product((0,1),repeat=3))
        print(json.dumps({"schema":SCHEMA,"mode":"preflight","status":"PASS",
                          "B_scored":False,"source_lock":lock},sort_keys=True))
        return
    if args.mode == "pilot":
        if args.seed not in PILOT:
            raise ValueError("CKAD30_UNREGISTERED_PILOT")
        result={"schema":SCHEMA,"mode":"pilot","source_lock":lock,
                "case":run_seed(args.seed),"B_scored":False}
    else:
        if args.seed is not None:
            raise ValueError("CKAD30_PRIMARY_NO_SEED_SELECTION")
        cert=json.loads((HERE/"pilot_certificate.json").read_text(encoding="utf8"))
        if (cert.get("schema")!="yggdrasil.ckad30.pilot-certificate.v1"
                or cert.get("source_lock_sha256")!=digest((HERE/"source_lock.json").read_bytes())
                or cert.get("pilot_seeds")!=list(PILOT) or cert.get("screen_go") is not True):
            raise AssertionError("CKAD30_PRIMARY_SCREEN_NOT_QUALIFIED")
        cases=[run_seed(s) for s in PRIMARY]
        result={"schema":SCHEMA,"mode":"primary","source_lock":lock,
                "cases":cases,"summary":classification(cases),"B_scored":True}
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
