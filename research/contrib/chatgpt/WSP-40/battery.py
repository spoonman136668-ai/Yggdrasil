"""Frozen WSP40 broad intervention-discovery assay. PRIMARY only on hosted CI."""
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
from model import NumericModel, IndependentIdentifier, FittedRegression, acquire, rotate


def rng_for(tag):
    return random.Random(int.from_bytes(hashlib.sha256(tag.encode()).digest(), "big"))


class World:
    def __init__(self, width, family, tag):
        self.width = width
        rng = rng_for(tag)
        self.terms = []
        for _ in range(2):
            degree = {"pair": 2, "triple": 3, "quartic_ood": 4, "xor_pairs_ood": 2}[family]
            term = sum(1 << i for i in rng.sample(range(width), degree))
            terms = [term]
            if family == "xor_pairs_ood":
                other = term
                while other == term:
                    other = sum(1 << i for i in rng.sample(range(width), 2))
                terms.append(other)
            self.terms.append(tuple(terms))

    def apply(self, action, state):
        residual = 0
        for term in self.terms[action]:
            residual ^= int((state & term) == term)
        return rotate(self.width, action, state) ^ residual

    rollout = NumericModel.rollout


def run(cohort):
    p = json.loads(Path(__file__).with_name("prereg.json").read_text())
    if cohort not in ("DEV", "PRIMARY"):
        raise ValueError("cohort")
    start_time = time.perf_counter()
    result = {"schema": "wsp40.result.v1", "cohort": cohort, "episodes": [], "timings": {}, "source": {}}
    trace = hashlib.sha256()
    for width, family, budget, seed in itertools.product(p["dimensions_max_first"], p["families"], p["budgets_per_action"], p["split"][cohort]):
        tag = f"WSP40|{cohort}|{seed}|{width}|{family}"
        world = World(width, family, tag)
        transcripts = {}
        remaining = {}
        arms = {}
        costs = {}
        for policy in ("active", "random", "singleton"):
            # Policy randomness independent of hidden world seed, support/family.
            t = time.perf_counter()
            arms[policy], transcripts[policy], remaining[policy] = acquire(width, world.apply, budget, policy, 733 + width)
            costs[policy + "_construct_s"] = time.perf_counter() - t
            assert len(transcripts[policy]) == 2 * budget
            assert len(set((a, x) for a, x, y in transcripts[policy])) == 2 * budget
        t = time.perf_counter()
        arms["identifier"] = IndependentIdentifier(width, transcripts["active"])
        costs["identifier_construct_s"] = time.perf_counter() - t
        t = time.perf_counter()
        fitted = FittedRegression(width, transcripts["active"])
        arms["trained"] = fitted
        costs["trained_construct_s"] = time.perf_counter() - t
        arms["zero"] = NumericModel(width, (0, 0))
        rng = rng_for(tag + "|evaluation")
        # Unseen to the active arm and its same-transcript strong/trained controls.
        # Other policies may have seen these states: report that advantage explicitly.
        used = {(a, x) for a, x, y in transcripts["active"]}
        eligible = [(a, x) for a in range(2) for x in range(1 << width) if (a, x) not in used]
        if not eligible:
            raise AssertionError("heldout exhausted")
        probes = [rng.choice(eligible) for _ in range(64)]
        sequences = [(rng.randrange(1 << width), tuple(rng.randrange(2) for _ in range((2, 3, 4)[i % 3]))) for i in range(24)]
        goals = []
        for _ in range(4):
            state = rng.randrange(1 << width)
            actions = tuple(rng.randrange(2) for _ in range(3))
            goals.append((state, world.rollout(state, actions)))
        scores = {}
        for name, model in arms.items():
            t = time.perf_counter()
            predictions = [model.apply(a, x) for a, x in probes]
            composed = [model.rollout(x, aa) for x, aa in sequences]
            plans = [model.plan(x, goal) for x, goal in goals]
            scores[name] = {
                "heldout": sum(y == world.apply(a, x) for y, (a, x) in zip(predictions, probes)),
                "composed": sum(y == world.rollout(x, aa) for y, (x, aa) in zip(composed, sequences)),
                "plans": sum(plan is not None and world.rollout(x, plan) == goal for plan, (x, goal) in zip(plans, goals))}
            costs[name + "_inference_plan_s"] = time.perf_counter() - t
            if name == "identifier":
                assert predictions == active_predictions and composed == active_composed
            if name == "active":
                active_predictions, active_composed = predictions, composed
        original = arms["active"].snapshot()
        restored = NumericModel.restore(original)
        assert [restored.apply(a, x) for a, x in probes] == active_predictions
        second = World(width, family, tag + "|second")
        second_model, _, _ = acquire(width, second.apply, budget, "active", 733 + width)
        assert arms["active"].snapshot() == original
        second_snapshot = second_model.snapshot()
        # A real additional contrary witness, if any, filters existing hypotheses.
        support_before = arms["active"].supports
        repair = []
        for action in range(2):
            witness = next((x for x in range(1 << width) if restored.apply(action, x) != world.apply(action, x)), None)
            if witness is None:
                repair.append({"witness": False, "corrected": False})
                continue
            residual = world.apply(action, witness) ^ rotate(width, action, witness)
            updated = IndependentIdentifier(width, transcripts["active"] + ((action, witness, residual),))
            repair.append({"witness": True, "corrected": updated.apply(action, witness) == world.apply(action, witness)})
        assert arms["active"].supports == support_before and second_model.snapshot() == second_snapshot
        corrupt = original[:-1] + (b"0" if original[-1:] != b"0" else b"1")
        try:
            NumericModel.restore(corrupt)
        except ValueError:
            pass
        else:
            raise AssertionError("tamper accepted")
        e = {"width": width, "family": family, "budget": budget, "seed": seed, "scores": scores,
             "evaluation_seen_by_other_policies": {name: sum((a, x) in {(aa, xx) for aa, xx, yy in transcript} for a, x in probes) for name, transcript in transcripts.items()},
             "remaining": remaining, "trained_fit_errors": fitted.train_errors,
             "trained_converged": all(e == 0 for e in fitted.train_errors),
             "unique_correct": sum(n == 1 and (m,) == truth for n, m, truth in zip(remaining["active"], restored.supports, world.terms)),
             "cold": True, "repair": repair, "snapshot_bytes": len(original)}
        # Hash integers and query receipts, never walltime/platform floats.
        trace.update(json.dumps([e, transcripts], sort_keys=True, separators=(",", ":")).encode())
        result["episodes"].append(e)
        for name, seconds in costs.items():
            result["timings"][name] = result["timings"].get(name, 0) + seconds
    result["trace_sha256"] = trace.hexdigest()
    result["total_seconds"] = time.perf_counter() - start_time
    result["source"] = {"python": sys.version, "platform": platform.platform(), "prereg_sha256": hashlib.sha256(Path(__file__).with_name("prereg.json").read_bytes()).hexdigest()}
    try:
        result["source"]["sha"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        result["source"]["tree"] = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip()
    except subprocess.CalledProcessError:
        result["source"]["sha"] = "LOCAL_DEV"
    known = [e for e in result["episodes"] if e["family"] in ("pair", "triple") and e["budget"] == 12]
    random4 = [e for e in result["episodes"] if e["family"] in ("pair", "triple") and e["budget"] == 4]
    acc = sum(e["scores"]["active"]["heldout"] for e in known) / (64 * len(known))
    comp = sum(e["scores"]["active"]["composed"] for e in known) / (24 * len(known))
    plans = sum(e["scores"]["active"]["plans"] for e in known) / (4 * len(known))
    identified = sum(e["unique_correct"] for e in known) / (2 * len(known))
    rand = sum(e["scores"]["random"]["heldout"] for e in random4) / (64 * len(random4))
    result["bounded_metrics"] = dict(accuracy=acc, composition=comp, planning=plans, identified=identified, active12_minus_random4=acc-rand)
    supported = acc >= .95 and comp >= .90 and plans >= .90 and identified >= .90 and acc-rand >= .05
    result["classification"] = "DEV_SUPPORTED_STRONG_CONTROL_TIE" if supported else "MIXED_OR_NEGATIVE_BOUNDED_THRESHOLD_MISSED"
    result["independent_scientific_pass"] = False
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", choices=("DEV", "PRIMARY"), default="DEV")
    args = parser.parse_args()
    print("WSP40_RESULT " + json.dumps(run(args.cohort), sort_keys=True))
