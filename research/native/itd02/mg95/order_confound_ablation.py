"""MG95-C training-order confound falsification; synthetic development only."""
from itertools import product
from conditional_memory_control import Lookup
from intervention_memory_screen import environment

BASE = list(product((0, 1), repeat=3))


def evaluate(order):
    test = list(product((0, 1), repeat=3))
    result = {}
    for key in ("full", "action", "context"):
        model = Lookup(key)
        for a, c, i in order * 3:
            model.learn(a, c, i, environment(a, c, i))
        result[key] = {
            "correct": sum(
                model.predict(a, c, i) == environment(a, c, i)
                for a, c, i in test
            ),
            "state": (model.out[:], model.seen[:]),
        }
    return result


def run():
    forward = evaluate(BASE)
    reverse = evaluate(list(reversed(BASE)))
    assert forward["full"]["correct"] == 8
    assert reverse["full"]["correct"] == 8
    assert forward["action"]["correct"] == reverse["action"]["correct"] == 6
    assert forward["context"]["correct"] == reverse["context"]["correct"] == 4
    assert forward["context"]["state"] != reverse["context"]["state"]
    return {
        "forward": forward,
        "reverse": reverse,
        "heldout_size": 8,
        "classification": "SYNTHETIC_ORDER_SENSITIVITY_ONLY",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), sort_keys=True, indent=2))
