"""MR32 deterministic source-only state/resource inventory.

Reports JSON checkpoint bytes, recursively measured Python object bytes,
tracemalloc peak and wall time. These host measurements are descriptive and
must not be interpreted as equal-resource scientific qualification.
"""
from __future__ import annotations
import argparse, json, sys, time, tracemalloc
from dataclasses import fields, is_dataclass
from residual_belief import ResidualBelief
from mr32_controls import MemorylessMean, ConventionalPrototypeControl
from recurrent_control import RecurrentStateSpaceControl
from diagonal_bayes_control import DiagonalBayesControl


def vector(n, size):
    return tuple(1.0 if i == n % size else 0.0 for i in range(size))


def deep_size(obj, seen=None):
    if seen is None:
        seen = set()
    ident = id(obj)
    if ident in seen:
        return 0
    seen.add(ident)
    total = sys.getsizeof(obj)
    if isinstance(obj, dict):
        total += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        total += sum(deep_size(v, seen) for v in obj)
    elif is_dataclass(obj):
        total += sum(deep_size(getattr(obj, f.name), seen) for f in fields(obj))
    elif hasattr(obj, "__dict__"):
        total += deep_size(vars(obj), seen)
    return total


def execute(model, steps):
    started = time.perf_counter()
    tracemalloc.start()
    for i in range(steps):
        x = vector(i % 97, 16)
        action = i % 3
        y = vector((i * 5 + action) % 8, 8)
        model.predict(x, action)
        model.observe_selected_outcome(y)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = time.perf_counter() - started
    if isinstance(model, ResidualBelief):
        checkpoint = model.snapshot()
    else:
        checkpoint = model.state_bytes()
    return {
        "steps": steps,
        "serialized_state_bytes": len(checkpoint),
        "deep_python_object_bytes": deep_size(model),
        "tracemalloc_peak_bytes": peak,
        "wall_seconds": elapsed,
    }


def run(steps):
    return {
        "schema": "yggdrasil.mr32.resource_inventory.v1",
        "classification": "SINGLE_HOST_DEVELOPMENT_INVENTORY_NOT_RESOURCE_PARITY",
        "steps": steps,
        "results": {
            "residual_belief": execute(ResidualBelief(), steps),
            "memoryless_mean": execute(MemorylessMean(), steps),
            "conventional_prototype": execute(ConventionalPrototypeControl(), steps),
            "recurrent_state_space": execute(RecurrentStateSpaceControl(), steps),
            "diagonal_bayes": execute(DiagonalBayesControl(), steps),
        },
        "limits": [
            "One deterministic synthetic stream; not a training/evaluation experiment.",
            "Python deep-size and tracemalloc depend on interpreter/platform and omit allocator/OS process RSS.",
            "Serialized MR32 state uses an integrity envelope while controls emit compact state JSON; formats are not yet semantically equal persistence contracts.",
            "No exact total-resource parity claim; use same interpreter/build and common serialization envelopes before comparing.",
            "Diagonal Bayesian linear control is included; no nonlinear Bayesian network or full planning agent is included.",
            "No scientific efficacy, causal improvement, terminal reward or transfer is measured."
        ]
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=256)
    args = parser.parse_args()
    if args.steps < 1 or args.steps > 10000:
        raise SystemExit("steps must be in 1..10000")
    print(json.dumps(run(args.steps), indent=2, sort_keys=True))
