"""Independently generated 4-bit public sensor families: scalable interference.

The fixture generates permutations and parity outcomes. Models receive only
public sensor vectors and completed outcomes; neither receives a hidden family
identifier, test label, or future result. All attempted training actions count.
"""
import json
import random
from time import process_time_ns
from local_cell_specialization import SpecializedColony
from sliding_tabular_control import SlidingTabularControl
from multi_regime_online_comparison import deep_bytes

def families(seed):
    rng = random.Random(seed)
    vectors = [tuple(bool((number >> bit) & 1) for bit in range(4))
               for number in range(16)]
    rng.shuffle(vectors)
    # Fixture-only public outcome rule; not passed to either learner.
    return [(bits, sum(bits) % 2 == 1) for bits in vectors]

def measure(seed, count, slots=4):
    cases = families(seed)
    trained, heldout = cases[:count], cases[count:]
    colony = SpecializedColony(slots_per_cell=slots)
    table = SlidingTabularControl(capacity=16)
    cpu_native = cpu_table = rejected = actions = 0
    for _ in range(2):
        for bits, outcome in trained:
            actions += 1
            start = process_time_ns()
            try:
                colony.learn_completed_public_feedback("A", bits, outcome, 2)
            except ValueError as exc:
                if str(exc) != "LOCAL_RECEPTIVE_FIELD_CAP":
                    raise
                rejected += 1
            cpu_native += process_time_ns() - start
            start = process_time_ns()
            table.observe((bytes(map(int, bits)), 0), b"1" if outcome else b"0")
            cpu_table += process_time_ns() - start
    def grade(predict, examples):
        values = [predict(bits) for bits, _ in examples]
        return {"correct":sum(v is not None and v == y for v, (_, y) in zip(values,examples)),
                "wrong":sum(v is not None and v != y for v, (_, y) in zip(values,examples)),
                "abstentions":sum(v is None for v in values)}
    def native_predict(bits):
        return colony.predict_public("A", bits)
    def table_predict(bits):
        answer = table.predict((bytes(map(int, bits)), 0))
        return None if answer is None else answer == b"1"
    frozen = colony.checkpoint()
    restored = SpecializedColony.restore(frozen)
    return {
        "seed":seed, "relationships":count, "slots_per_cell":slots,
        "actions":actions, "native_accepted":colony.feedback_updates,
        "native_rejected":rejected, "table_accepted":table.examples,
        "native_trained":grade(native_predict, trained),
        "table_trained":grade(table_predict, trained),
        "native_heldout":grade(native_predict, heldout),
        "table_heldout":grade(table_predict, heldout),
        "cold_restore_exact":all(
            native_predict(bits) == restored.predict_public("A",bits)
            for bits, _ in cases),
        "native_checkpoint_bytes":len(frozen),
        "table_bytes":deep_bytes(table.table),
        "native_cpu_ns":cpu_native,"table_cpu_ns":cpu_table,
    }

def run():
    return {
        "runs":[measure(seed, count, 4) for seed in (3,17,41)
                for count in (2,4,8,12)],
        "capacity_controls":[measure(3,8,cap) for cap in (1,2,3,4)],
        "scope":"Three seeded, generated binary public sensory families; four relationship counts; action ownership and two-sample training",
        "limitations":"Handcrafted 4-bit parity environment; fixed topology with only four distinct local receptive signatures per cell. Not original DoorKey, learned-feature discovery or a conventional generalization benchmark.",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
