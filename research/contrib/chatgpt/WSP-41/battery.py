"""WSP41 frozen open-degree circuit construction, retained failures included."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
from model import NumericModel, SymbolicExecution, KernelRegression, acquire, random_transcript, rotate


def rng_for(tag):
    return random.Random(int.from_bytes(hashlib.sha256(tag.encode()).digest(), "big"))


class World:
    def __init__(self, width, family, tag):
        self.width, self.family, self.tag = width, family, tag
        rng = rng_for(tag)
        self.terms = []
        for action in range(2):
            terms = set()
            count = {"single_degree6": 1, "four_mixed_terms": 4, "eight_mixed_terms": 8, "arbitrary_hash": 0}[family]
            while len(terms) < count:
                degree = 6 if family == "single_degree6" else rng.randint(1, 6)
                terms.add(sum(1 << i for i in rng.sample(range(width), degree)))
            self.terms.append(tuple(sorted(terms)))

    def apply(self, action, state):
        if self.family == "arbitrary_hash":
            residual = hashlib.sha256(f"{self.tag}|{action}|{state}".encode()).digest()[0] & 1
        else:
            residual = sum((state & term) == term for term in self.terms[action]) % 2
        return rotate(self.width, action, state) ^ residual

    rollout = NumericModel.rollout


def run(cohort):
    pre_path = Path(__file__).with_name("prereg.json")
    p = json.loads(pre_path.read_text())
    started = time.perf_counter()
    result = {"schema": "wsp41.result.v1", "cohort": cohort, "episodes": [], "timings": {}}
    trace = hashlib.sha256()
    for width, family, budget, seed in itertools.product(p["dimensions_max_first"], p["families"], p["budgets_per_action"], p["split"][cohort]):
        tag = f"WSP41|{cohort}|{seed}|{width}|{family}"
        world = World(width, family, tag)
        t = time.perf_counter()
        model, transcript, stats = acquire(width, world.apply, budget)
        costs = {"active_construct_s": time.perf_counter()-t}
        random_rows = random_transcript(width, world.apply, [s["queries"] for s in stats])
        t = time.perf_counter()
        fitted = KernelRegression(width, transcript)
        costs["same_info_kernel_fit_s"] = time.perf_counter()-t
        t = time.perf_counter()
        random_fitted = KernelRegression(width, random_rows)
        costs["random_kernel_fit_s"] = time.perf_counter()-t
        arms = {"direct": model, "symbolic_execution": SymbolicExecution(model), "trained_same_info": fitted,
                "trained_random": random_fitted, "zero": NumericModel(width, ((), ()))}
        seen = {(a, x) for a, x, y in transcript}
        rng = rng_for(tag + "|evaluation")
        probes = []
        while len(probes) < 64:
            pair = (rng.randrange(2), rng.randrange(1 << width))
            if pair not in seen: probes.append(pair)
        sequences = [(rng.randrange(1 << width), tuple(rng.randrange(2) for _ in range((2, 3, 4)[i%3]))) for i in range(24)]
        goals = []
        for _ in range(4):
            x = rng.randrange(1 << width)
            aa = tuple(rng.randrange(2) for _ in range(3))
            goals.append((x, world.rollout(x, aa)))
        scores = {}
        for name, arm in arms.items():
            t = time.perf_counter()
            predictions = [arm.apply(a, x) for a, x in probes]
            composed = [arm.rollout(x, aa) for x, aa in sequences]
            plans = [arm.plan(x, goal) for x, goal in goals]
            scores[name] = {"heldout": sum(y == world.apply(a,x) for y,(a,x) in zip(predictions,probes)),
                            "composed": sum(y == world.rollout(x,aa) for y,(x,aa) in zip(composed,sequences)),
                            "plans": sum(aa is not None and world.rollout(x,aa) == goal for aa,(x,goal) in zip(plans,goals))}
            costs[name+"_infer_plan_s"] = time.perf_counter()-t
            if name == "direct": direct_predictions, direct_composed = predictions, composed
            if name == "symbolic_execution":
                assert predictions == direct_predictions and composed == direct_composed
        lookup = {(a,x): y for a,x,y in transcript}
        scores["literal"] = {"heldout": sum(rotate(width,a,x) ^ lookup.get((a,x),0) == world.apply(a,x) for a,x in probes)}
        snap = model.snapshot()
        restored = NumericModel.restore(snap)
        assert [restored.apply(a,x) for a,x in probes] == direct_predictions
        t = time.perf_counter()
        second = World(width, family, tag+"|second")
        second_model, secondary_transcript, secondary_stats = acquire(width, second.apply, budget)
        assert model.snapshot() == snap
        assert NumericModel.restore(second_model.snapshot()).snapshot() == second_model.snapshot()
        costs["secondary_retention_acquire_s"] = time.perf_counter()-t
        corrupt = snap[:-1] + (b"0" if snap[-1:] != b"0" else b"1")
        try: NumericModel.restore(corrupt)
        except ValueError: pass
        else: raise AssertionError("tamper accepted")
        e = {"width": width, "family": family, "budget": budget, "seed": seed, "scores": scores, "stats": stats,
             "exact_support_actions": sum(g == target for g,target in zip(model.terms, world.terms)) if family != "arbitrary_hash" else None,
             "trained_converged": all(e <= 1e-7 for e in fitted.max_errors + random_fitted.max_errors),
             "random_seen_eval": sum((a,x) in {(aa,xx) for aa,xx,yy in random_rows} for a,x in probes),
             "snapshot_bytes": len(snap), "resident_binary_coefficients": sum(len(g)*(width+2) for g in model.terms),
             "cache_payload_bits": len(transcript)*(width+1), "kernel_float_coefficients": len(transcript),
             "secondary_queries": len(secondary_transcript), "cold": True}
        trace.update(json.dumps([e,transcript,random_rows],sort_keys=True,separators=(",",":")).encode())
        result["episodes"].append(e)
        for name, value in costs.items(): result["timings"][name] = result["timings"].get(name,0)+value
    result["trace_sha256"] = trace.hexdigest()
    result["total_seconds"] = time.perf_counter()-started
    result["source"] = {"python":sys.version,"platform":platform.platform(),"prereg_sha256":hashlib.sha256(pre_path.read_bytes()).hexdigest()}
    try:
        result["source"].update(sha=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),tree=subprocess.check_output(["git","rev-parse","HEAD^{tree}"],text=True).strip())
    except subprocess.CalledProcessError: result["source"]["sha"]="LOCAL_DEV"
    subset=[e for e in result["episodes"] if e["family"]=="single_degree6" and e["budget"]==128]
    result["bounded_metrics"]={key:sum(e["scores"]["direct"][key] for e in subset)/(len(subset)*n) for key,n in (("heldout",64),("composed",24),("plans",4))}
    m=result["bounded_metrics"]
    result["bounded_metrics"]["exact_support_fraction"]=sum(e["exact_support_actions"] for e in subset)/(2*len(subset))
    result["classification"]="DEV_SUPPORTED_BOUNDED_GROWTH_ONLY" if m["heldout"]>=.95 and m["composed"]>=.90 and m["plans"]>=.90 and m["exact_support_fraction"]==1.0 else "MIXED_OR_NEGATIVE_BOUNDED_THRESHOLD_MISSED"
    result["independent_scientific_pass"]=False
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--cohort",choices=("DEV","PRIMARY"),default="DEV")
    print("WSP41_RESULT "+json.dumps(run(parser.parse_args().cohort),sort_keys=True))
