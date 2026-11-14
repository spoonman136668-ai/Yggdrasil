"""QTR F15 open DEV-only algebraic information/ceiling screen.
No native model, no protected source; no external environment, no training.
"""
from itertools import combinations, product
from collections import defaultdict
import json

EVENTS = list(product((0, 1), repeat=3))  # features x0,x1 and forced action


def hypotheses():
    h = {}
    for source, flip in product(range(2), range(2)):
        h[f"xor.s{source}.f{flip}"] = lambda e, source=source, flip=flip: e[source] ^ e[2] ^ flip
        h[f"gate.s{source}.f{flip}"] = lambda e, source=source, flip=flip: (e[source] & e[2]) ^ flip
    for flip in (0, 1):
        h[f"majority.f{flip}"] = lambda e, flip=flip: int(sum(e) >= 2) ^ flip
    return h


def run():
    h = hypotheses()
    full = {name: tuple(int(fn(e)) for e in EVENTS) for name, fn in h.items()}
    if len(set(full.values())) != len(full):
        return {"classification": "FAIL_DUPLICATE_CAUSAL_LAWS"}
    mins = None
    for n in range(1, len(EVENTS) + 1):
        for ix in combinations(range(len(EVENTS)), n):
            if len({tuple(outputs[j] for j in ix) for outputs in full.values()}) == len(full):
                mins = ix
                break
        if mins is not None:
            break
    if mins is None:
        return {"classification": "FAIL_NONIDENTIFIABLE"}
    # World-blind evidence consists of exactly the same measured intervention data for all strategies.
    # An exact-event retrieval control can only answer observed events; a symbolic enumerator
    # assigns the unique hypothesis consistent with observed outcomes and predicts the rest.
    raw_seen = set(mins)
    exact_coverage = sum(i in raw_seen for _name in full for i in range(len(EVENTS)))
    symbolic_correct = 0
    for truth_name, truth_outputs in full.items():
        observed = {i: truth_outputs[i] for i in mins}
        matching = [name for name, ys in full.items() if all(ys[i] == v for i,v in observed.items())]
        assert matching == [truth_name]
        symbolic_correct += sum(full[matching[0]][i] == truth_outputs[i] for i in range(len(EVENTS)))
    return {
        "schema": "yggdrasil.qtr.f15.open-development-identifiability.v1",
        "model_count": len(full),
        "public_observation_action_cases": len(EVENTS),
        "min_fixed_probe_budget": len(mins),
        "probe_cases": [EVENTS[i] for i in mins],
        "total_world_case_queries": len(full) * len(EVENTS),
        "exact_event_retrieval_covered": exact_coverage,
        "exact_event_retrieval_abstains": len(full) * len(EVENTS) - exact_coverage,
        "fully_informed_symbolic_correct": symbolic_correct,
        "classification": "DEV_CEILING_FOR_SYMBOLIC_CONTROL_NO_SCIENTIFIC_HEADROOM",
        "scientific_pass": False,
        "native_transfer_tested": False,
        "source_benchmark_executed": False,
    }

if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
