"""QTR F20: preregistered public DEV test of REAL native PublicCausalCells.

The evaluator knows the six causal laws. Both native and raw retrieval receive
only public 3-bit context IDs, binary interventions and observed success. The
symbolic method is explicitly privileged with the six-law hypothesis class.
Not evidence about Yggdrasil's full architecture or scientific first-use.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from yggdrasil.public_causal_cells import PublicCausalCells

PREREG = "8db53cb53b7f69f024a70b5e39c9d61123066926"
TRAIN = (0, 1, 2, 4)
TEST = (3, 5, 6, 7)
LAWS = ("bit0", "bit1", "bit2", "xor01", "xor12", "majority")
TRIALS = 8


def bits(ctx):
    if type(ctx) is not int or ctx not in range(8):
        raise ValueError("F20_BAD_CONTEXT")
    return (ctx & 1, (ctx >> 1) & 1, (ctx >> 2) & 1)


def law_action(name, ctx):
    a, b, c = bits(ctx)
    rules = {
        "bit0": a, "bit1": b, "bit2": c,
        "xor01": a ^ b, "xor12": b ^ c,
        "majority": int(a + b + c >= 2)
    }
    if name not in rules:
        raise ValueError("F20_BAD_LAW")
    return rules[name]


def slot(ctx):
    bits(ctx)
    return (ctx, False) if ctx <= 6 else (0, True)


def experiences(law):
    return tuple(
        (ctx, action, int(action == law_action(law, ctx)))
        for ctx in TRAIN for action in (0, 1) for _ in range(TRIALS)
    )


def native_fit(rows):
    cells = PublicCausalCells()
    for ctx, action, public_reward in rows:
        addr, retained = slot(ctx)
        cells.observe(addr, action, public_reward, retained=retained)
    return cells


def native_choose(cells, ctx):
    addr, retained = slot(ctx)
    return cells.choose(addr, retained=retained)


def raw_retrieval(rows, ctx):
    count, wins = [0, 0], [0, 0]
    for observed_ctx, action, reward in rows:
        if observed_ctx == ctx:
            count[action] += 1
            wins[action] += reward
    if not all(count):
        return None
    left, right = wins[0] * count[1], wins[1] * count[0]
    return None if left == right else (0 if left > right else 1)


def symbolic_infer(rows):
    # Exactly disclosed six-law structural prior. This is NOT prior-matched
    # to the fixed-address native memory or raw-event retrieval control.
    return tuple(name for name in LAWS if all(
        public_reward == int(action == law_action(name, ctx))
        for ctx, action, public_reward in rows
    ))


def run():
    fingerprints = {tuple(law_action(law, ctx) for ctx in TRAIN) for law in LAWS}
    if len(fingerprints) != 6:
        raise ValueError("F20_UNIDENTIFIABLE_TRAINING_SPLIT")
    metrics = {
        "native_train_correct": 0, "native_test_covered": 0,
        "native_test_correct_given_answer": 0,
        "raw_test_covered": 0, "symbolic_test_correct": 0,
        "cold_exact_checkpoints": 0, "cold_train_correct": 0,
        "retained_slot_isolated": 0, "single_arm_abstention": 0
    }
    for law in LAWS:
        rows = experiences(law)
        if len(rows) != 64:
            raise ValueError("F20_BUDGET_DRIFT")
        native = native_fit(rows)
        checkpoint = native.snapshot()
        restored = PublicCausalCells.restore(checkpoint)
        metrics["cold_exact_checkpoints"] += restored.snapshot() == checkpoint
        symbols = symbolic_infer(rows)
        if symbols != (law,):
            raise ValueError("F20_PRIOR_AMBIGUITY")
        for ctx in TRAIN:
            truth = law_action(law, ctx)
            metrics["native_train_correct"] += native_choose(native, ctx) == truth
            metrics["cold_train_correct"] += native_choose(restored, ctx) == truth
        for ctx in TEST:
            truth = law_action(law, ctx)
            action = native_choose(native, ctx)
            metrics["native_test_covered"] += action is not None
            if action is not None:
                metrics["native_test_correct_given_answer"] += action == truth
            metrics["raw_test_covered"] += raw_retrieval(rows, ctx) is not None
            metrics["symbolic_test_correct"] += law_action(symbols[0], ctx) == truth
        if native.snapshot() != checkpoint:
            raise ValueError("F20_TEST_CHANGED_LEARNED_SOURCE")

        # Post-evaluation cold clone only; never contaminates held-out results.
        clone = PublicCausalCells.restore(checkpoint)
        old_active = native_choose(clone, 0)
        clone.observe(0, 0, 0, retained=True)
        clone.observe(0, 1, 1, retained=True)
        metrics["retained_slot_isolated"] += (
            native_choose(clone, 0) == old_active
            and native_choose(clone, 7) == 1)
        single = PublicCausalCells()
        single.observe(0, 0, 1)
        metrics["single_arm_abstention"] += single.choose(0) is None
    expected = {
        "native_train_correct": 24, "native_test_covered": 0,
        "native_test_correct_given_answer": 0, "raw_test_covered": 0,
        "symbolic_test_correct": 24, "cold_exact_checkpoints": 6,
        "cold_train_correct": 24, "retained_slot_isolated": 6,
        "single_arm_abstention": 6
    }
    if metrics != expected:
        raise ValueError("F20_FROZEN_RESULT_MISMATCH")
    return {
        "schema": "yggdrasil.qtr.f20.public-native-transfer.v1",
        "prereg": PREREG,
        "native_module_blob": "5c9a9904e31688bebc2e53723569e1fb988a981f",
        "learned_bytes": PublicCausalCells.LEARNED_BYTES,
        "checkpoint_bytes": PublicCausalCells.CHECKPOINT_BYTES,
        "law_families": list(LAWS), "train_contexts": list(TRAIN),
        "heldout_contexts": list(TEST),
        "public_events": 384, "heldout_queries": 24,
        "metrics": metrics,
        "strong_symbolic_control_has_privileged_prior": True,
        "candidate_is_memory_comparator_not_full_yggdrasil": True,
        "native_semantic_context_transfer_observed": False,
        "scientific_pass": False,
        "classification": "DEV_NATIVE_CONTEXT_TRANSFER_NO_GO"
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
