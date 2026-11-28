"""Two simultaneous public relationships: interference and unseen-feature probes.

A single public colony context receives two distinct binary sensor patterns
with opposite completed public outcomes, alternated and then consolidated.
A conventional keyed online control receives exactly the same pairs. The
predeclared sensory patterns are TEST FIXTURES, not hidden regime labels.
Reports both pre-training and after each phase, held-out recombinations and
cold-restore equality; predictions have no access to withheld labels.
"""
import json
from time import process_time_ns
from local_cell_reversal_candidate import ReversalColony
from sliding_tabular_control import SlidingTabularControl
from multi_regime_online_comparison import deep_bytes

PATTERNS = (
    ((True, True, False, False), True),
    ((True, False, True, False), False),
)
UNSEEN = (
    ((False, True, False, False), True),
    ((True, False, False, True), False),
)
CTX = "A"

def grade(predict, cases):
    predictions = [predict(bits) for bits, _ in cases]
    return {
        "correct": sum(v is not None and v == y for v, (_, y) in zip(predictions, cases)),
        "wrong": sum(v is not None and v != y for v, (_, y) in zip(predictions, cases)),
        "abstentions": sum(v is None for v in predictions),
    }

def measure():
    colony = ReversalColony()
    tabular = SlidingTabularControl(capacity=16)
    steps = []
    ns = {"native": 0, "tabular": 0}
    def local_prediction(bits):
        return colony.predict_public(CTX, bits)
    def table_prediction(bits):
        v = tabular.predict((bytes(int(b) for b in bits), 0))
        return None if v is None else v == b"1"
    def evaluate(phase):
        steps.append({
            "phase": phase,
            "native_trained": grade(local_prediction, PATTERNS),
            "tabular_trained": grade(table_prediction, PATTERNS),
            "native_heldout": grade(local_prediction, UNSEEN),
            "tabular_heldout": grade(table_prediction, UNSEEN),
        })
    evaluate("untrained")
    for index, (bits, result) in enumerate(PATTERNS):
        for _ in range(2):
            start = process_time_ns()
            colony.learn_completed_public_feedback(CTX, bits, result, 2)
            ns["native"] += process_time_ns() - start
            start = process_time_ns()
            tabular.observe((bytes(int(b) for b in bits), 0),
                            b"1" if result else b"0")
            ns["tabular"] += process_time_ns() - start
        evaluate("relationship_" + str(index + 1))
    checkpoint = colony.checkpoint()
    restored = ReversalColony.restore(checkpoint)
    return {
        "phases": steps,
        "actions": 4,
        "native_feedback_updates": colony.feedback_updates,
        "tabular_examples": tabular.examples,
        "cold_restore_equal": all(
            local_prediction(bits) == restored.predict_public(CTX, bits)
            for bits, _ in PATTERNS + UNSEEN),
        "cpu_ns": ns,
        "native_checkpoint_bytes": len(checkpoint),
        "tabular_state_bytes": deep_bytes(tabular.table),
        "scope": "Public multi-relation interference and withheld sensor recombination in one cell context",
        "limitation": "Handcrafted binary synthetic public features; no original DoorKey task, no independently learned feature representation.",
    }

if __name__ == "__main__":
    print(json.dumps(measure(),sort_keys=True))
