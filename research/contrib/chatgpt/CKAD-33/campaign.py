"""CKAD33: compile witnessed causal consequences into existing native numeric weights.

Conventional quadratic feature class is PREDECLARED. The degree-2 basis is a
source-only inductive bias, not inferred structure or scientific superiority.
This is a research-only opt-in readout; no accepted state or owner credentials.
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
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, coordinates
from yggdrasil.native_property_knowledge import NativePropertyKnowledge

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "CKAD-30" / "campaign.py"
SPEC = importlib.util.spec_from_file_location("ckad33_conventional_controls", BASE)
C30 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C30)

SCHEMA = "yggdrasil.ckad33.native-compilation.v1"
PREREG = "dce7ad6e81d33d5cf69731440397b86a37928fc0"
PILOT = (13531, 13532)
RESERVED_PRIMARY = (23531, 23532, 23533)
PAIR_BITS = tuple(range(5))
TRIPLES = tuple(itertools.combinations(PAIR_BITS, 3))
GRAPHS = ("xor3", "majority3", "gate3")
CLASS_FAMILIES = ("quadratic", "cubic_shift")
OLD_SLOTS = tuple(range(6))
PRESSURE_SLOTS = tuple(range(6,12))
ALL_ARMS = {
    "quadratic": (
        "compiled_native", "native_original", "native_sparse",
        "gf2_conventional", "exact_2880_bayes", "polynomial_logistic",
        "smoothed_frequency", "sham"
    ),
    "cubic_shift": (
        "compiled_native", "uncalibrated_native", "native_original",
        "gf2_conventional", "gf2_degree3", "sham"
    ),
}


def seed_int(*keys):
    raw = hashlib.sha256(canonical(["ckad33-independent-source-v1", *keys])).digest()
    return int.from_bytes(raw[:8], "big")


def hidden_law(seed, slot):
    """Environment/revealer ONLY; not supplied to fit, cal decision or readout."""
    r = random.Random(seed_int("private-law", seed, slot))
    first, second = r.sample(range(10), 2)
    law = (r.randrange(2), r.randrange(32), first, second)
    if slot in (3,4,5):
        return law, TRIPLES[r.randrange(len(TRIPLES))]
    return law, None


def effect(law, triple, x):
    outcome = C30.effect(law, x)
    if triple is not None:
        outcome ^= int(all((x >> k) & 1 for k in triple))
    return outcome


def reveal(seed, slot, x):
    law, triple = hidden_law(seed, slot)
    return effect(law, triple, x)


def feature_mask(x, degree=2):
    """Independent conventional algebra implementation, 5-bit subset features."""
    if type(x) is not int or not 0 <= x < 32 or degree not in (2,3):
        raise ValueError("CKAD33_FEATURE_INPUT")
    features = tuple(mask for mask in range(32) if mask.bit_count() <= degree)
    return sum(1 << i for i, mask in enumerate(features) if (x & mask) == mask)


def reduce_row(pivots, row, y=0):
    """Pure input or witnessed-output GF(2) eliminator for CONVENTIONAL control."""
    while row:
        k = row.bit_length()-1
        if k not in pivots:
            return row, y, k
        p, v = pivots[k]
        row ^= p
        y ^= v
    return 0, y, None


def source_span(rows, degree=2):
    pivots = {}
    seen = set()
    for c, a, y in rows:
        if type(y) is not int or y not in (0,1):
            raise ValueError("CKAD33_SOURCE_OUTCOME")
        x = c | (a<<4)
        if x in seen:
            raise ValueError("CKAD33_DUPLICATE_SOURCE")
        seen.add(x)
        row, rhs, pivot = reduce_row(pivots, feature_mask(x,degree),y)
        if pivot is not None:
            pivots[pivot]=(row,rhs)
        elif rhs:
            raise ValueError("CKAD33_SOURCE_CLASS_INADEQUATE")
    return pivots


def forecast_conventional(pivots, x, degree=2):
    row, rhs, pivot = reduce_row(pivots, feature_mask(x,degree))
    return float(rhs) if pivot is None else 0.5


def rank_design(seed):
    """Choose an entire 16-dimensional input basis without reading a consequence."""
    order = sorted(range(32), key=lambda x:(seed_int("unlabeled-order",seed,x),x))
    pivots,fit = {},[]
    for x in order:
        v,_,k = reduce_row(pivots, feature_mask(x))
        if k is not None:
            pivots[k]=(v,0)
            fit.append(x)
        if len(fit)==16:
            break
    if len(fit)!=16 or len(pivots)!=16:
        raise AssertionError("CKAD33_NO_FULL_RANK_DESIGN")
    remaining = [x for x in range(32) if x not in fit]
    ranked = sorted(remaining,key=lambda x:(seed_int("source-calibration-order",seed,x),x))
    cal = ranked[:4]
    held = ranked[4:]
    if len(set(fit+cal+held))!=32 or len(held)!=12:
        raise AssertionError("CKAD33_PARTITION_INVALID")
    return tuple(fit),tuple(cal),tuple(held)


def rows(seed, slot, inputs):
    return [[x & 15,x >> 4,reveal(seed,slot,x)] for x in inputs]


def stage(acc, slot, source, degree):
    a,r = coordinates(slot)
    return acc.stage_update(a,source,digest(canonical(source)),
                            max_degree=degree,retained=r)


def read_compiled(acc, slot, x):
    a,r = coordinates(slot)
    y = acc.predict(a,x&15,x>>4,retained=r)
    if y is None:
        return 0.5
    if type(y) is not int or y not in (0,1):
        raise ValueError("CKAD33_BAD_NATIVE_READOUT")
    return float(y)


def compile_native(seed,fit,cal,held):
    """Only existing native compiler/restore. Four cal outcomes NOT fitted."""
    m = NativeContextAccumulator(4)
    source = {slot: rows(seed,slot,fit) for slot in OLD_SLOTS}
    calibration={slot: rows(seed,slot,cal) for slot in OLD_SLOTS}
    for slot in OLD_SLOTS:
        m = stage(m,slot,source[slot],2)
    original_sha = digest(m.checkpoint())
    original_size = len(m.checkpoint())
    info = {str(slot):m.profile_info(*coordinates(slot)) for slot in OLD_SLOTS}
    if not all(x["rank"]==16 and x["degree"]==2 for x in info.values()):
        raise AssertionError("CKAD33_COMPILER_RANK_MISMATCH")
    cal_pass={
        slot:all(read_compiled(m,slot,x)==float(y)
                 for (c,a,y) in calibration[slot]
                 for x in [c|(a<<4)])
        for slot in OLD_SLOTS
    }
    before = [[read_compiled(m,slot,x) for x in range(32)] for slot in OLD_SLOTS]
    pressure={slot:rows(seed,slot,fit) for slot in PRESSURE_SLOTS}
    for slot in PRESSURE_SLOTS:
        m = stage(m,slot,pressure[slot],5)
    raw=m.checkpoint()
    cold=NativeContextAccumulator.restore(raw,digest(raw))
    if raw!=cold.checkpoint():
        raise AssertionError("CKAD33_NATIVE_COLD_BYTES")
    if any([read_compiled(cold,slot,x) for x in range(32)]!=before[slot]
           for slot in OLD_SLOTS):
        raise AssertionError("CKAD33_NATIVE_RETENTION")
    for slot in (*OLD_SLOTS,*PRESSURE_SLOTS):
        a,r=coordinates(slot)
        observed=source[slot] if slot in OLD_SLOTS else pressure[slot]
        pi=cold.profile_info(a,retained=r)
        if pi["source_records"]!=16 or pi["rank"]!=16:
            # Degree-5 pressure has rank=16 with unique inputs, no reuse.
            raise AssertionError("CKAD33_SOURCE_LEDGER_OR_PRESSURE")
    old_bytes=cold.checkpoint()
    conflict = [list(source[0][0])]
    conflict[0][2] ^= 1
    try:
        stage(cold,0,conflict,2)
    except ValueError:
        pass
    else:
        raise AssertionError("CKAD33_CONTRADICTION_NOT_REJECTED")
    if cold.checkpoint()!=old_bytes:
        raise AssertionError("CKAD33_REJECTED_PACKET_MUTATED_NATIVE")
    return cold,source,calibration,cal_pass,{
        "before_pressure_sha256":original_sha,"before_bytes":original_size,
        "after_pressure_sha256":digest(raw),"after_bytes":len(raw),
        "slot_profiles":info,"cold_restore_exact":True,
        "retention_exact_all_32_inputs":True,
        "conflict_rejection_atomic":True,
        "pressure_slot_count":len(PRESSURE_SLOTS),
    }


def new_control():
    raw=NativePropertyKnowledge("ckad33",entities=1,context_bits=4).checkpoint()
    return NativeCumulativeLearner(raw,digest(raw))


def native_control(seed,fit,cal,old,held):
    m=new_control()
    for slot in OLD_SLOTS:
        all_rows=old[slot]+cal[slot]
        blob=canonical(all_rows)
        m=m.observe(slot,all_rows,digest(blob),
                    source_ref=digest(canonical(["ckad33/unmodified-source",seed,slot,digest(blob)])))
    # Original sparse repair is restricted to old IN-CLASS slots 0..2.
    repaired, solver = C30.fit_repaired(m)
    before={
        "native_original":[[C30.readout(m,s,x) for x in held] for s in range(3)],
        "native_sparse":[[C30.readout(repaired,s,x) for x in held] for s in range(3)]
    }
    baseline_ood=[[C30.readout(m,s,x) for x in held] for s in (3,4,5)]
    before_raw = digest(m.checkpoint())
    after_raw = digest(repaired.checkpoint())
    # Both baseline learners receive matched pressure witness inputs.
    for slot in PRESSURE_SLOTS:
        source=rows(seed,slot,fit)
        blob=canonical(source)
        source_ref=digest(canonical(["ckad33/control-pressure",seed,slot,digest(blob)]))
        m=m.observe(slot,source,digest(blob),source_ref=source_ref)
        repaired=repaired.observe(slot,source,digest(blob),source_ref=source_ref)
    for name,model in (("native_original",m),("native_sparse",repaired)):
        raw=model.checkpoint()
        cold=NativeCumulativeLearner.restore(raw,digest(raw))
        if cold.checkpoint()!=raw:
            raise AssertionError("CKAD33_BASELINE_COLD_DRIFT")
        for s in range(3):
            expected=before[name][s]
            got=[C30.readout(cold,s,x) for x in held]
            if expected!=got:
                raise AssertionError("CKAD33_BASELINE_OLD_INTERFERENCE")
    return before,baseline_ood,solver,{
        "native_before_sha256":before_raw,
        "sparse_before_sha256":after_raw,
        "baseline_cold_and_retention_exact":True
    }


def brier_slot():
    return {"squared":0.,"cases":0}


def record_metrics(stats):
    return {name:{"brier":round(v["squared"]/v["cases"],10),"cases":v["cases"]}
            for name,v in stats.items()}


def score(seed):
    if seed not in PILOT:
        raise ValueError("CKAD33_PRIMARY_SEED_FORBIDDEN")
    start,cpu = time.perf_counter(),time.process_time()
    fit,cal,held = rank_design(seed)
    compiled,old,calibration,admit,custody=compile_native(seed,fit,cal,held)
    native,ood_native,solver,baselines = native_control(seed,fit,cal,old,held)
    conventional={}
    cal_conventional={}
    gf3={}
    post={}
    fitted={}
    for slot in OLD_SLOTS:
        p=source_span(old[slot],2)
        conventional[slot]=p
        cal_conventional[slot]=all(
            forecast_conventional(p,c|(a<<4),2)==float(y)
            for c,a,y in calibration[slot]
        )
        if admit[slot]!=cal_conventional[slot]:
            raise AssertionError("CKAD33_NATIVE_CONVENTIONAL_CALIBRATION_DRIFT")
        if slot<3:
            post[slot]=C30.posterior(old[slot]+calibration[slot])
            fitted[slot]=C30.fit_logistic(old[slot]+calibration[slot])
        else:
            gf3[slot]=source_span(old[slot]+calibration[slot],3)
    stats={family:{name:brier_slot() for name in names}
           for family,names in ALL_ARMS.items()}
    coverage={family:{name:0 for name in names if name in (
        "compiled_native","uncalibrated_native","native_original","native_sparse",
        "gf2_conventional","gf2_degree3")}
        for family,names in ALL_ARMS.items()}
    confident_wrong={family:{name:0 for name in coverage[family]} for family in CLASS_FAMILIES}
    for i,x in enumerate(held):
        for family,offset in (("quadratic",0),("cubic_shift",3)):
            truth=[reveal(seed,offset+s,x) for s in range(3)]
            raw_comp=[read_compiled(compiled,offset+s,x) for s in range(3)]
            admitted=[raw_comp[s] if admit[offset+s] else .5 for s in range(3)]
            gf2=[forecast_conventional(conventional[offset+s],x,2)
                 if cal_conventional[offset+s] else .5 for s in range(3)]
            if family=="quadratic":
                preds={
                    "compiled_native":admitted,
                    "native_original":[native["native_original"][s][i] for s in range(3)],
                    "native_sparse":[native["native_sparse"][s][i] for s in range(3)],
                    "gf2_conventional":gf2,
                    "exact_2880_bayes":[C30.bayes_prob(post[s],x) for s in range(3)],
                    "polynomial_logistic":[C30.logistic_prob(fitted[s],x) for s in range(3)],
                    "smoothed_frequency":[C30.frequency_prob(old[s]+calibration[s],x) for s in range(3)],
                    "sham":[.5]*3,
                }
            else:
                preds={
                    "compiled_native":admitted,
                    "uncalibrated_native":raw_comp,
                    "native_original":[ood_native[s][i] for s in range(3)],
                    "gf2_conventional":gf2,
                    "gf2_degree3":[forecast_conventional(gf3[3+s],x,3) for s in range(3)],
                    "sham":[.5]*3
                }
            for name in coverage[family]:
                for s in range(3):
                    val=preds[name][s]
                    if val!=.5:
                        coverage[family][name]+=1
                        confident_wrong[family][name]+=int(val!=float(truth[s]))
            for graph in GRAPHS:
                expected=C30.composition(graph,truth)
                for arm,triple in preds.items():
                    value=C30.composition(graph,triple)
                    if not -1.e-12<=value<=1.+1.e-12:
                        raise AssertionError("CKAD33_COMPOSED_OUT_OF_RANGE")
                    stats[family][arm]["squared"]+=(max(0.,min(1.,value))-expected)**2
                    stats[family][arm]["cases"]+=1
    pilot={
        "seed":seed,"source_rows":216,
        "inclass_source_rows":60,"ood_source_rows":60,
        "pressure_source_rows":96,"held_cases_each_family":36,
        "fit_input_indices":list(fit),"calibration_input_indices":list(cal),
        "held_input_indices":list(held),
        "calibration_pass":{str(s):admit[s] for s in OLD_SLOTS},
        "metrics":{k:record_metrics(v) for k,v in stats.items()},
        "coverage":{k:{name:round(v/36,10) for name,v in z.items()}
                    for k,z in coverage.items()},
        "confident_wrong":confident_wrong,
        "native_compiler":custody,
        "baseline_native":baselines,
        "sparse_solver":solver,
        "exact_bayes_rule_counts":[len(post[s]) for s in range(3)],
        "degree3_source_ranks":[len(gf3[s]) for s in (3,4,5)],
        "wall_seconds":round(time.perf_counter()-start,6),
        "cpu_seconds":round(time.process_time()-cpu,6),
    }
    return pilot


def classify(cases):
    if tuple(c["seed"] for c in cases)!=PILOT:
        raise AssertionError("CKAD33_FROZEN_SEED_ORDER")
    if any(not (c["native_compiler"]["cold_restore_exact"]
                and c["native_compiler"]["retention_exact_all_32_inputs"]
                and c["native_compiler"]["conflict_rejection_atomic"]
                and c["baseline_native"]["baseline_cold_and_retention_exact"])
           for c in cases):
        return {"decision":"INVALID","engineering_feasible":False}
    def eligible(c):
        ins=c["metrics"]["quadratic"]
        outs=c["metrics"]["cubic_shift"]
        native=ins["compiled_native"]["brier"]
        if not (
            native<=.01 and native<=ins["native_original"]["brier"]-.10
            and native==ins["gf2_conventional"]["brier"]
            and c["coverage"]["quadratic"]["compiled_native"]>=.95
            and outs["compiled_native"]["brier"]<=outs["uncalibrated_native"]["brier"]
            and c["confident_wrong"]["cubic_shift"]["compiled_native"]==0
            and sum(not c["calibration_pass"][str(s)] for s in (3,4,5))>=2):
            return False
        return True
    go=all(eligible(c) for c in cases)
    return {"decision":"ENGINEERING_FEASIBLE" if go else "SCREEN_NO_GO",
            "engineering_feasible":go,
            "scientific_pass":False,
            "conventional_superiority":False,
            "reserved_primary_scored":False}


def verify_lock():
    lock=json.loads((HERE/"source_lock.json").read_text())
    raw=Path(__file__).read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if lock["campaign_blob_sha1"]!=blob or lock["prereg_commit"]!=PREREG:
        raise AssertionError("CKAD33_SOURCE_PIN_MISMATCH")
    return lock


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("preflight","pilot"),required=True)
    ap.add_argument("--seed",type=int)
    args=ap.parse_args()
    lock=verify_lock()
    if args.mode=="preflight":
        if args.seed is not None:raise ValueError("CKAD33_PREFLIGHT_SEED")
        assert len(TRIPLES)==10 and len(C30.PAIR_CHOICES)==45
        assert len(set(PILOT+RESERVED_PRIMARY))==5
        assert all(C30.composition(g,bits) in (0,1)
                   for g in GRAPHS for bits in itertools.product((0,1),repeat=3))
        print(json.dumps({"schema":SCHEMA,"mode":"preflight","status":"PASS",
                          "source_lock":lock,"primary_scored":False},sort_keys=True))
    else:
        if args.seed not in PILOT:raise ValueError("CKAD33_UNREGISTERED_PILOT")
        print(json.dumps({"schema":SCHEMA,"mode":"pilot","seed":args.seed,"source_lock":lock,
                          "primary_scored":False,"case":score(args.seed)},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
