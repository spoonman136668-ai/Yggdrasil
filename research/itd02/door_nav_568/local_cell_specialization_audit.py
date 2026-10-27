"""Matched coexisting-relationship interference audit with local specialization.

The R7 reversal candidate, receptive-field local specialization, and
conventional keyed tabular baseline all see the same completed public actions.
Untrained sensor recombinations are scored independently from retention.
"""
import json
from time import process_time_ns
from local_cell_specialization import SpecializedColony
from local_cell_reversal_candidate import ReversalColony
from sliding_tabular_control import SlidingTabularControl
from multi_relation_interference_audit import PATTERNS, UNSEEN, CTX, grade
from multi_regime_online_comparison import deep_bytes

def measure():
    specialist = SpecializedColony()
    original = ReversalColony()
    conventional = SlidingTabularControl(capacity=16)
    elapsed = {"specialized":0, "original":0, "tabular":0}
    history = []

    def predict_tab(bits):
        value = conventional.predict((bytes(int(x) for x in bits), 0))
        return None if value is None else value == b"1"

    def review(stage):
        history.append({
            "phase": stage,
            "specialized_training": grade(lambda x:specialist.predict_public(CTX,x), PATTERNS),
            "original_training": grade(lambda x:original.predict_public(CTX,x), PATTERNS),
            "tabular_training": grade(predict_tab, PATTERNS),
            "specialized_unseen": grade(lambda x:specialist.predict_public(CTX,x), UNSEEN),
            "original_unseen": grade(lambda x:original.predict_public(CTX,x), UNSEEN),
            "tabular_unseen": grade(predict_tab, UNSEEN),
        })

    review("untrained")
    for index, (bits, target) in enumerate(PATTERNS):
        for _ in range(2):
            for label, learner in (("specialized", specialist), ("original",original)):
                start = process_time_ns()
                learner.learn_completed_public_feedback(CTX,bits,target,2)
                elapsed[label] += process_time_ns() - start
            start = process_time_ns()
            conventional.observe((bytes(int(x) for x in bits),0),
                                 b"1" if target else b"0")
            elapsed["tabular"] += process_time_ns() - start
        review("relationship_" + str(index + 1))
    raw = specialist.checkpoint()
    restored = SpecializedColony.restore(raw)
    return {
        "phases": history,
        "actions": 4,
        "specialized_updates": specialist.feedback_updates,
        "original_updates": original.feedback_updates,
        "conventional_examples": conventional.examples,
        "specialized_messages": specialist.neighbor_messages,
        "cold_restore_equal": all(
            restored.predict_public(CTX,x) == specialist.predict_public(CTX,x)
            for x,_ in PATTERNS + UNSEEN),
        "specialized_checkpoint_bytes": len(raw),
        "original_checkpoint_bytes": len(original.checkpoint()),
        "conventional_state_bytes": deep_bytes(conventional.table),
        "cpu_ns": elapsed,
        "scope": "Public-local two-field specialization, simultaneous relationship retention and withheld binary recombinations",
        "limitation": "Fixed binary sensory topology, not autonomous feature discovery or original DoorKey evidence.",
    }

if __name__ == "__main__":
    print(json.dumps(measure(),sort_keys=True))
