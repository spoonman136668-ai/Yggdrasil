"""WSP101 large-first synthetic relation/association capacity DEV stress.

Original causal worlds are NEVER touched. All source-only predictions are
hashed BEFORE evaluating any heldout target; no result is scientific AGI proof.
"""
from array import array
import hashlib
import json
import struct
import sys
import time

from wide_truth import source, heldout, answer, rank
from wide_models import DirectWeightMemory, infer_symbolic, predict_symbolic, baseline_lookup

TIERS = ((64,64,12), (32,32,11), (8,8,10))
DEV_MAX_WALL_SECONDS = 180
PREDICTION_UNSET = 65535
PAIR_BUDGET = 8192

def _seal(values):
    h=hashlib.sha256()
    for value in values:
        if not 0 <= value <= 65535:
            raise ValueError("impossible encoded prediction")
        h.update(struct.pack(">H",value))
    return h.hexdigest()

def _source_digest(entries):
    h = hashlib.sha256(b"WSP101-WIDE-v1-SOURCE")
    for idx, pairs in enumerate(entries):
        h.update(struct.pack(">I",idx))
        for x,y in pairs:
            h.update(struct.pack(">HH",x,y))
    return h.hexdigest()

def _append(pred, value):
    pred.append(PREDICTION_UNSET if value is None else value)

def execute(domains, relations, bits):
    """Largest-first single tier, with no oracle scoring before prediction seal."""
    start=time.perf_counter()
    start_cpu=time.process_time()
    n=domains*relations
    if not 0 < n <= 4096 or bits not in (10,11,12):
        raise ValueError("unfrozen capacity tier")
    source_start=time.process_time()
    examples=[source(d,r,bits) for d in range(domains) for r in range(relations)]
    digest=_source_digest(examples)
    source_cpu=time.process_time()-source_start

    compiled=DirectWeightMemory(n,bits)
    t=time.process_time()
    for idx,pairs in enumerate(examples[:n//2]):
        compiled.write(idx,pairs)
    cold_first=compiled.cold_image()
    memory_before=hashlib.sha256(cold_first[0]+cold_first[1]).hexdigest()
    compiled=DirectWeightMemory.restore(n,bits,cold_first)
    if compiled.cold_image()!=cold_first:
        raise AssertionError("cold restored weights changed")
    for idx,pairs in enumerate(examples[n//2:],start=n//2):
        compiled.write(idx,pairs)
    direct_fit_cpu=time.process_time()-t
    if compiled.known.count(1)!=n:
        raise AssertionError("not all direct numeric weights written")
    cold_all=compiled.cold_image()
    compiled=DirectWeightMemory.restore(n,bits,cold_all)
    memory_after=hashlib.sha256(cold_all[0]+cold_all[1]).hexdigest()

    t=time.process_time()
    symbolic=[infer_symbolic(pairs,bits) for pairs in examples]
    symbolic_fit_cpu=time.process_time()-t
    t=time.process_time()
    lookup=[baseline_lookup(pairs) for pairs in examples]
    lookup_fit_cpu=time.process_time()-t

    # Source observations and model states are frozen before heldout evaluation.
    t=time.process_time()
    prepared=[]
    output_direct=array("H")
    output_symbolic=array("H")
    output_lookup=array("H")
    for idx in range(n):
        d,r=divmod(idx,relations)
        xs=heldout(d,r,bits,128)
        prepared.append(xs)
        for x in xs:
            _append(output_direct,compiled.predict(idx,x))
            _append(output_symbolic,predict_symbolic(symbolic[idx],x,bits))
            _append(output_lookup,lookup[idx].get(x))
    one_hop_len=len(output_direct)
    compositional=[]
    for i in range(PAIR_BUDGET):
        d=i%domains
        r=(i//domains)%relations
        r2=(r+17)%relations
        idx=d*relations+r
        idx2=d*relations+r2
        x=rank(d,r,"COMPOSE",i)%(1<<bits)
        compositional.append((d,r,r2,x))
        z1=compiled.predict(idx,x)
        z2=predict_symbolic(symbolic[idx],x,bits)
        l1=lookup[idx].get(x)
        _append(output_direct,compiled.predict(idx2,z1) if z1 is not None else None)
        _append(output_symbolic,predict_symbolic(symbolic[idx2],z2,bits) if z2 is not None else None)
        _append(output_lookup,lookup[idx2].get(l1) if l1 is not None else None)
    prediction_cpu=time.process_time()-t
    receipts={
        "source_sha256":digest,
        "direct_predictions_sha256":_seal(output_direct),
        "symbolic_predictions_sha256":_seal(output_symbolic),
        "lookup_predictions_sha256":_seal(output_lookup),
        "cold_half_sha256":memory_before,
        "cold_full_sha256":memory_after
    }
    print("WSP101_WIDE_DEV_ALL_PREDICTIONS_FROZEN="+json.dumps(
        receipts,sort_keys=True,separators=(",",":")),flush=True)

    t=time.process_time()
    totals=[0,0,0]
    known=[0,0,0]
    correct=[0,0,0]
    for idx,xs in enumerate(prepared):
        d,r=divmod(idx,relations)
        for j,x in enumerate(xs):
            truth=answer(d,r,bits,x)
            pos=idx*128+j
            for q,preds in enumerate((output_direct,output_symbolic,output_lookup)):
                guess=preds[pos]
                if guess!=PREDICTION_UNSET:
                    known[q]+=1
                    correct[q]+=int(guess==truth)
                totals[q]+=1
    one_hop_counts=correct[:]
    one_hop_known=known[:]
    two_hop_correct=[0,0,0]
    two_hop_known=[0,0,0]
    for j,(d,r,r2,x) in enumerate(compositional):
        first=answer(d,r,bits,x)
        truth=answer(d,r2,bits,first)
        for q,preds in enumerate((output_direct,output_symbolic,output_lookup)):
            guess=preds[one_hop_len+j]
            if guess!=PREDICTION_UNSET:
                two_hop_known[q]+=1
                two_hop_correct[q]+=int(guess==truth)
    scoring_cpu=time.process_time()-t
    if not all(x==n*128 for x in totals):
        raise AssertionError("lost frozen heldout predictions")
    methods={}
    for q,name in enumerate(("direct_numeric","independent_symbolic","lookup")):
        methods[name]={
            "one_hop_correct":one_hop_counts[q],
            "one_hop_covered":one_hop_known[q],
            "one_hop_total":totals[q],
            "two_hop_correct":two_hop_correct[q],
            "two_hop_covered":two_hop_known[q],
            "two_hop_total":PAIR_BUDGET
        }
    report={
        "schema":"wsp101.wide-first-dev-result.v1",
        "classification":"DEV_SYNTHETIC_ONLY",
        "tier":{"domains":domains,"relations":relations,"bits":bits},
        "possible_relation_links":domains*relations*(1<<bits),
        "training_observed_links":n*8,
        "unseen_one_hop_queries":one_hop_len,
        "two_hop_queries":PAIR_BUDGET,
        "numerical_weight_slots":n*3,
        "numeric_cold_image_bytes":compiled.bytes,
        "source_cpu_seconds":source_cpu,
        "direct_fit_cpu_seconds":direct_fit_cpu,
        "symbolic_fit_cpu_seconds":symbolic_fit_cpu,
        "lookup_fit_cpu_seconds":lookup_fit_cpu,
        "prediction_all_methods_cpu_seconds":prediction_cpu,
        "scoring_cpu_seconds":scoring_cpu,
        "end_to_end_cpu_seconds":time.process_time()-start_cpu,
        "end_to_end_wall_seconds":time.perf_counter()-start,
        "methods":methods,
        "receipts":receipts,
        "scientific_superiority":False,
        "original_worlds_used":False
    }
    if all(methods[m]["one_hop_correct"]==one_hop_len and
           methods[m]["two_hop_correct"]==PAIR_BUDGET for m in
           ("direct_numeric","independent_symbolic")):
        report["engineering_class"]="DEV_BOUNDED_RULE_CAPACITY_PASS_WITH_STRONG_TIE"
    else:
        report["engineering_class"]="DEV_CAPACITY_NEGATIVE_OR_UNDERIDENTIFIED"
    if report["end_to_end_wall_seconds"]>DEV_MAX_WALL_SECONDS:
        report["engineering_class"]="DEV_RESOURCE_LIMIT"
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--fallback-only", action="store_true",
                        help="only the two preregistered smaller tiers; original max negative already consumed")
    args = parser.parse_args()
    tiers = TIERS[1:] if args.fallback_only else TIERS
    failures = []
    all_results = []
    for domains, relations, bits in tiers:
        try:
            result = execute(domains, relations, bits)
        except ValueError as exc:
            # Frozen source-size/information failure, not permission to tune
            # any generator or fitting rule after seeing the huge DEV result.
            if str(exc) not in ("ambiguous underdetermined source",
                                "symbolic source nonidentifiable",
                                "no source-consistent numerical rule",
                                "no symbolic explanation"):
                raise
            negative = {
                "tier": [domains, relations, bits],
                "classification": "DEV_SOURCE_UNDERIDENTIFIED",
                "reason": str(exc),
                "scientific_superiority": False,
                "original_worlds_used": False
            }
            failures.append(negative)
            print("WSP101_WIDE_DEV_TIER_NEGATIVE=" + json.dumps(
                negative,sort_keys=True,separators=(",",":")),flush=True)
            continue
        all_results.append(result)
        print("WSP101_WIDE_DEV_TIER=" + json.dumps(
            result,sort_keys=True,separators=(",",":")),flush=True)
        if result["engineering_class"] == "DEV_BOUNDED_RULE_CAPACITY_PASS_WITH_STRONG_TIE":
            break
    print("WSP101_WIDE_DEV_FINAL=" + json.dumps({
        "schema": "wsp101.wide-first-result.v1",
        "fallback_only": args.fallback_only,
        "preexisting_max_negative_run": 43623476680 if args.fallback_only else None,
        "attempted_successful_tiers": all_results,
        "underidentified_tiers": failures,
        "scientific_superiority": False,
        "original_worlds_used": False
    },sort_keys=True,separators=(",",":")),flush=True)

if __name__ == "__main__":
    main()
