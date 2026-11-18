"""CKAD31 frozen source-only uncertainty gate over the unchanged native sparse readout.

Conventional GF(2) source entailment is a *permission certificate*, not a native
architecture or a scientific claim. The evaluator's hidden law is never passed
to any model, certificate, fit or readout. This is external research only.
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
PARENT = HERE.parent / "CKAD-30" / "campaign.py"
SPEC = importlib.util.spec_from_file_location("ckad31_frozen_ckad30_controls", PARENT)
C30 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C30)

SCHEMA = "yggdrasil.ckad31.uncertainty-guard.v1"
PREREG = "837d728bde20a6b898a73b2f88ad4786785622cf"
PILOT = (9311, 9322)
PRIMARY = (1311, 1322, 1333)
GRAPHS = ("xor3", "majority3", "gate3")
ARMS = ("native_original", "native_sparse", "native_guarded",
        "gf2_conventional", "logistic_conventional", "smoothed_frequency",
        "bayes_2880", "sham")
FEATURE_COUNT = 16


def seed_int(*keys):
    d = hashlib.sha256(canonical(["ckad31-disjoint-world-v1", *keys])).digest()
    return int.from_bytes(d[:8], "big")


def hidden_law(seed, slot):
    # Generator and scorer only. Never call from any fit/guard/forecast.
    r = random.Random(seed_int("private-generator", seed, slot))
    first, second = r.sample(range(10), 2)
    return (r.randrange(2), r.randrange(32), first, second)


def outcome(law, x):
    return C30.effect(law, x)


def partition(seed):
    xs = list(range(32))
    random.Random(seed_int("partition", seed)).shuffle(xs)
    return tuple(xs[:16]), tuple(xs[16:])


def source_rows(seed, slot, inputs):
    law = hidden_law(seed, slot)
    return [[x & 15, x >> 4, outcome(law, x)] for x in inputs]


def new_native():
    raw = NativePropertyKnowledge("ckad31", entities=1, context_bits=4).checkpoint()
    return NativeCumulativeLearner(raw, digest(raw))


def observe(m, seed, slot, rows):
    raw = canonical(rows)
    source_ref = digest(canonical(["ckad31/public-witness", seed, slot, digest(raw)]))
    return m.observe(slot, rows, digest(raw), source_ref=source_ref)


def native_readout(model, slot, x):
    y = model.predict(slot, x & 15, x >> 4)
    if y is None:
        return 0.5
    if type(y) is not int or y not in (0, 1):
        raise ValueError("CKAD31_NATIVE_NONBINARY")
    return float(y)


def design_mask(x):
    """Generic degree <= 2 polynomial ANF, no family-oracle masks supplied."""
    if type(x) is not int or not 0 <= x < 32:
        raise ValueError("CKAD31_INPUT_INVALID")
    bits = [(x >> i) & 1 for i in range(5)]
    vals = [1] + bits + [bits[i] & bits[j] for i, j in C30.PAIRS]
    if len(vals) != FEATURE_COUNT:
        raise AssertionError("CKAD31_FEATURE_DRIFT")
    return sum(v << i for i, v in enumerate(vals))


def source_span(rows):
    """GF(2) elimination over *public* observed witnesses, no unseen outcomes."""
    pivots = {}
    masks = []
    for context, action, consequence in rows:
        if type(consequence) is not int or consequence not in (0, 1):
            raise ValueError("CKAD31_BAD_SOURCE_BIT")
        x = context | (action << 4)
        masks.append(x)
        v, y = design_mask(x), consequence
        while v:
            bit = v.bit_length() - 1
            if bit in pivots:
                previous, val = pivots[bit]
                v ^= previous
                y ^= val
            else:
                pivots[bit] = (v, y)
                break
        if not v and y:
            raise ValueError("CKAD31_INCONSISTENT_SOURCE")
    if len(masks) != len(set(masks)):
        raise ValueError("CKAD31_DUPLICATE_SOURCE_INPUT")
    return pivots


def entailment(pivots, x):
    """Return exact source-entailed bit or None if query is underidentified."""
    v, y = design_mask(x), 0
    while v:
        bit = v.bit_length() - 1
        if bit not in pivots:
            return None
        pv, py = pivots[bit]
        v ^= pv
        y ^= py
    return y


def gate(native_value, entailed):
    if native_value not in (0., 0.5, 1.) or entailed not in (0, 1, None):
        raise ValueError("CKAD31_INVALID_GUARD_ARGUMENTS")
    return native_value if (entailed is not None and native_value == float(entailed)) else 0.5


def metrics_slot():
    return {"squared":0., "correct":0, "cases":0}


def score(seed):
    if seed not in PILOT + PRIMARY:
        raise ValueError("CKAD31_UNREGISTERED_SEED")
    start, cpustart = time.perf_counter(), time.process_time()
    fit, held = partition(seed)
    assert len(fit) == len(held) == 16 and not set(fit) & set(held)
    rows = [source_rows(seed, slot, fit) for slot in range(9)]
    spans = [source_span(rows[slot]) for slot in range(3)]
    native = new_native()
    for slot in range(3):
        native = observe(native, seed, slot, rows[slot])
    repaired, solver = C30.fit_repaired(native)
    old_raws = {"native_original":native.checkpoint(),
                "native_sparse":repaired.checkpoint()}
    checkpoints = {k:digest(v) for k,v in old_raws.items()}
    before = {}
    for k,model in (("native_original",native),("native_sparse",repaired)):
        before[k] = [[native_readout(model,slot,x) for x in held] for slot in range(3)]
    for slot in range(3,9):
        native = observe(native,seed,slot,rows[slot])
        repaired = observe(repaired,seed,slot,rows[slot])
    restored = {}
    fullsha = {}
    for name, model in (("native_original",native),("native_sparse",repaired)):
        raw = model.checkpoint()
        fullsha[name] = digest(raw)
        restored[name] = NativeCumulativeLearner.restore(raw,digest(raw))
        if restored[name].checkpoint() != raw:
            raise AssertionError("CKAD31_COLD_RESTORE_DRIFT")
        for slot in range(3):
            if [native_readout(restored[name],slot,x) for x in held] != before[name][slot]:
                raise AssertionError("CKAD31_OLD_MEMORY_MUTATION")
    for slot in range(9):
        expected = {tuple(r) for r in rows[slot]}
        for model in restored.values():
            if {tuple(r) for r in model._rows(slot)} != expected:
                raise AssertionError("CKAD31_WITNESS_LOSS")
    contradiction=[list(rows[0][0])]
    contradiction[0][2] ^= 1
    quarantined=observe(restored["native_sparse"],seed+90000,0,contradiction)
    if not quarantined.info()["quarantined"][0] or any(
        native_readout(quarantined,slot,x)!=before["native_sparse"][slot][i]
        for slot in (1,2) for i,x in enumerate(held)
    ):
        raise AssertionError("CKAD31_QUARANTINE_DRIFT")
    logistic=[C30.fit_logistic(rows[s]) for s in range(3)]
    bayes=[C30.posterior(rows[s]) for s in range(3)]
    ms={a:metrics_slot() for a in ARMS}
    coverage={key:0 for key in ("native_original","native_sparse","native_guarded","gf2_conventional")}
    confident_wrong={key:0 for key in coverage}
    for i,x in enumerate(held):
        truth=[outcome(hidden_law(seed,s),x) for s in range(3)]
        source=[entailment(spans[s],x) for s in range(3)]
        n=[before["native_original"][s][i] for s in range(3)]
        sparse=[before["native_sparse"][s][i] for s in range(3)]
        values={
            "native_original":n,
            "native_sparse":sparse,
            "native_guarded":[gate(sparse[s],source[s]) for s in range(3)],
            "gf2_conventional":[float(t) if t is not None else 0.5 for t in source],
            "logistic_conventional":[C30.logistic_prob(logistic[s],x) for s in range(3)],
            "smoothed_frequency":[C30.frequency_prob(rows[s],x) for s in range(3)],
            "bayes_2880":[C30.bayes_prob(bayes[s],x) for s in range(3)],
            "sham":[0.5]*3,
        }
        for name in coverage:
            for s in range(3):
                v=values[name][s]
                if v!=0.5:
                    coverage[name]+=1
                    confident_wrong[name]+=int(v!=float(truth[s]))
        for g in GRAPHS:
            actual=C30.composition(g,truth)
            for name, triple in values.items():
                p=C30.composition(g,triple)
                if not -1e-12<=p<=1+1e-12:
                    raise AssertionError("CKAD31_INVALID_PROBABILITY")
                p=max(0.,min(1.,p))
                m=ms[name]
                m["squared"]+=(p-actual)**2
                m["correct"]+=int((p>=0.5)==actual)
                m["cases"]+=1
    summary={k:{"brier":round(v["squared"]/v["cases"],10),
                "accuracy":round(v["correct"]/v["cases"],10),
                "cases":v["cases"]} for k,v in ms.items()}
    return {
        "seed":seed,"source_rows":144,"held_composite_cases":48,
        "metrics":summary,
        "coverage":{k:round(v/48,10) for k,v in coverage.items()},
        "confident_wrong":confident_wrong,
        "span_ranks":[len(a) for a in spans],
        "solver":solver,
        "source_checkpoint_sha256":checkpoints,
        "cold_checkpoint_sha256":fullsha,
        "cold_restore_exact":True,
        "old_primitive_retention_exact":True,
        "local_quarantine_exact":True,
        "bayes_law_counts":[len(b) for b in bayes],
        "cpu_seconds":round(time.process_time()-cpustart,6),
        "wall_seconds":round(time.perf_counter()-start,6),
    }


def pilot_decision(cases):
    if tuple(c["seed"] for c in cases)!=PILOT:
        raise ValueError("CKAD31_PILOT_ORDER")
    custody=all(c["cold_restore_exact"] and c["old_primitive_retention_exact"]
                and c["local_quarantine_exact"] for c in cases)
    witness=any(
        c["coverage"]["native_guarded"]>=0.10 and
        c["metrics"]["native_guarded"]["brier"]<=
        min(c["metrics"]["native_original"]["brier"],
            c["metrics"]["native_sparse"]["brier"])-0.02
        for c in cases
    )
    return {"screen_go":custody and witness,
            "decision":"PILOT_GO" if custody and witness else "SCREEN_NO_GO"}


def validate_lock():
    meta=json.loads((HERE/"source_lock.json").read_text())
    raw=Path(__file__).read_bytes()
    gitblob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if (meta["campaign_blob_sha1"]!=gitblob or meta["prereg_commit"]!=PREREG):
        raise AssertionError("CKAD31_SOURCE_LOCK_DRIFT")
    return meta


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("preflight","pilot"),required=True)
    ap.add_argument("--seed",type=int)
    args=ap.parse_args()
    lock=validate_lock()
    if args.mode=="preflight":
        if args.seed is not None:
            raise ValueError("CKAD31_PREFLIGHT_NO_SEED")
        assert len(C30.PAIR_CHOICES)==45 and 2*32*45==2880
        assert set(PILOT).isdisjoint(PRIMARY)
        assert len(set(PILOT+PRIMARY))==5
        assert all(C30.composition(g,t) in (0,1) for g in GRAPHS
                   for t in itertools.product((0,1),repeat=3))
        print(json.dumps({"schema":SCHEMA,"mode":"preflight","status":"PASS",
                          "B_scored":False,"lock":lock},sort_keys=True))
    else:
        if args.seed not in PILOT:
            raise ValueError("CKAD31_PILOT_SEED_NOT_ALLOWED")
        print(json.dumps({"schema":SCHEMA,"mode":"pilot","lock":lock,
                          "B_scored":False,"case":score(args.seed)},sort_keys=True,indent=2))


if __name__=="__main__":
    main()
