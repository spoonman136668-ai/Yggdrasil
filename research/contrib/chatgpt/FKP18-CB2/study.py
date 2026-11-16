"""CB2 PUBLIC diagnostic: interleaved delayed-credit relations and one revision.

Four source-law definitions below exist only in this source-owner evaluation
module. None is imported by context_bank.py or strong_control.py.
"""
from __future__ import annotations
from collections import namedtuple
from hashlib import sha256
import json
import random
import statistics
import time

import binding
from context_bank import GatedRelationBank, ConventionalFourSlotBank

Step = namedtuple("Step", binding.FIELDS)
Past = namedtuple("Past", binding.PAST_FIELDS)
FAMILIES = ((1, 6, 6), (18, 32, 6), (5, 35, 8), (10, 32, 6))
SOURCE_SEEDS = (82210, 82211)
VALID_SEEDS = (82220, 82221)


def truth(bits, mode, *, revised=False):
    a, b, table = FAMILIES[mode]
    if revised and mode == 1:
        table = 9  # NEGATION of previous mode-1 XOR output, not told to learner
    index = (((bits >> a) & 1) << 1) | ((bits >> b) & 1)
    return (table >> index) & 1


def tape(seed, *, revised=False, n=515):
    if (seed not in SOURCE_SEEDS or type(seed) is not int or
            type(n) is not int or n < 515 or n > 600):
        raise ValueError("CB2_PUBLIC_TAPE_SCOPE")
    rng = random.Random(seed)
    states = []
    for t in range(n + 1):
        state = [rng.randrange(16) for _ in range(8)]
        state[7] = (state[7] & ~3) | (t & 3)
        states.append(tuple(state))
    actions = tuple(rng.randrange(2) for _ in range(n))
    rewards = [0] * n
    for t in range(3, n):
        credited = t - 2
        mode = states[credited][7] & 3
        bits = binding._feature_bits(states[credited], actions[credited - 1],
                                    actions[credited - 2] if credited >= 2 else 0)
        desired = truth(bits, mode, revised=revised)
        rewards[t] = 1 if actions[credited] == desired else -1
    result = []
    for t in range(n):
        hist = tuple(Past(states[j], actions[j], rewards[j], states[j + 1], False)
                     for j in range(max(0, t - 16), t))
        result.append(Step(states[t], actions[t], states[t + 1],
                           rewards[t], False, hist))
    return tuple(result)


def queries(seed, n_per_mode=128):
    if type(seed) is not int or seed not in VALID_SEEDS:
        raise ValueError("CB2_UNKNOWN_PUBLIC_VALIDATION_SEED")
    rng = random.Random(seed)
    for mode in range(4):
        for _ in range(n_per_mode):
            s0 = tuple(rng.randrange(16) for _ in range(8))
            s1 = tuple(rng.randrange(16) for _ in range(8))
            state = [rng.randrange(16) for _ in range(8)]
            state[7] = (state[7] & ~3) | mode
            state = tuple(state)
            p0, p1 = rng.randrange(2), rng.randrange(2)
            history = (Past(s0, p0, 0, s1, False),
                       Past(s1, p1, 0, state, False))
            bits = binding._feature_bits(state, p1, p0)
            yield mode, state, history, truth(bits, mode, revised=seed == 82221)


def evaluate(candidate, conventional, seed):
    scores = {"candidate": [0] * 4, "conventional": [0] * 4,
              "no_scope": [0] * 4, "no_revision": [0] * 4}
    for mode, state, history, target in queries(seed):
        chosen = candidate.choose_public(state, history)
        baseline = conventional.choose_public(state, history)
        wrong_scope = candidate._models[3].choose_public(state, history)
        original_mode = candidate._initial_cold._models[mode].choose_public(state, history) if hasattr(candidate, '_initial_cold') else chosen
        scores["candidate"][mode] += chosen == target
        scores["conventional"][mode] += baseline == target
        scores["no_scope"][mode] += wrong_scope == target
        scores["no_revision"][mode] += original_mode == target
    return scores


def study():
    started = time.perf_counter()
    candidate = GatedRelationBank()
    conventional = ConventionalFourSlotBank()
    initial = tape(82210)
    for row in initial:
        candidate.observe_public(row)
        conventional.observe_public(row)
    candidate.seal()
    conventional.seal()
    initial_slot_receipts = candidate.slot_receipts()
    initial_snapshot = candidate.snapshot()
    original = GatedRelationBank.restore(initial_snapshot)
    candidate._initial_cold = original  # harness-only frozen negative reference
    initial_scores = evaluate(candidate, conventional, 82220)
    initial_training_seconds = time.perf_counter() - started
    if initial_scores["candidate"] != initial_scores["conventional"]:
        raise AssertionError("CB2_INITIAL_STRONG_CONTROL_DIFFERENCE")
    # Negative: model receives identical public evidence, but files each
    # delayed consequence under CURRENT instead of CREDITED public gate.
    wrong = [binding.ConditionalTemporalBinder() for _ in range(4)]
    for row in initial:
        credit, _ = binding._credit_public(row)
        if credit is not None:
            wrong[row.before[7] & 3].observe_public(row)
    for m in wrong:
        m.seal()
    wrong_score = [0]*4
    for mode, state, history, target in queries(82220):
        wrong_score[mode] += wrong[mode].choose_public(state, history) == target
    repair_start = time.perf_counter()
    revised_stream = tape(82211, revised=True, n=600)
    mismatch_counts = [0] * 4
    for row in revised_stream:
        credit, _ = binding._credit_public(row)
        if credit is not None:
            bits, target = credit
            mode = (bits >> 28) & 3
            if mode == 1:
                initial_rule = original._models[mode].binding
                mismatch_counts[mode] += binding._feature_bits(row.history[-2].before,
                    row.history[-3].action,
                    row.history[-4].action if len(row.history)>=4 else 0) == bits and (
                        target != ((initial_rule[2] >> (((bits>>initial_rule[0]&1)<<1)|(bits>>initial_rule[1]&1))) & 1))
        candidate.observe_public(row)
        conventional.observe_public(row)
    changed_receipts = candidate.slot_receipts()
    cold = GatedRelationBank.restore(candidate.snapshot())
    revised_scores = evaluate(candidate, conventional, 82221)
    cold_scores = evaluate(cold, conventional, 82221)
    if revised_scores["candidate"] != revised_scores["conventional"]:
        raise AssertionError("CB2_REVISED_STRONG_CONTROL_DIFFERENCE")
    if revised_scores["candidate"] != cold_scores["candidate"]:
        raise AssertionError("CB2_COLD_PREDICTION_DIFFERENCE")
    digest_data = {
        "initial": initial_scores, "after_revision": revised_scores,
        "wrong_current_mode_score": wrong_score,
        "old_receipts": initial_slot_receipts, "new_receipts": changed_receipts,
        "versions": candidate.versions, "repairs": candidate.repairs,
    }
    return {
        "classification": "PUBLIC_DEV_INTERFERENCE_CAPABILITY_ONLY_STRONG_CONTROL_TIE",
        "public_initial_actions": len(initial),
        "public_repair_actions": len(revised_stream),
        "public_earned_credits": candidate.credits,
        "original_snapshot_bytes": len(initial_snapshot),
        "revised_snapshot_bytes": len(candidate.snapshot()),
        "logical_model_bytes": candidate.logical_persisted_relation_bytes,
        "initial_scores": initial_scores,
        "wrong_current_mode_score": wrong_score,
        "revised_scores": revised_scores,
        "mode_versions": candidate.versions,
        "earned_repairs": candidate.repairs,
        "initial_and_revised_receipts": [list(initial_slot_receipts), list(changed_receipts)],
        "unchanged_slot_bit_exact": all(initial_slot_receipts[i] == changed_receipts[i] for i in (0,2,3)),
        "revised_slot_changed": initial_slot_receipts[1] != changed_receipts[1],
        "cold_snapshot_exact": cold.snapshot() == candidate.snapshot(),
        "control_equal_at_all_1024_scored_examples": (
            initial_scores["candidate"] == initial_scores["conventional"] and
            revised_scores["candidate"] == revised_scores["conventional"]),
        "original_mode1_mismatch_credits": mismatch_counts[1],
        "initial_full_wall_seconds": initial_training_seconds,
        "repair_and_replay_wall_seconds": time.perf_counter()-repair_start,
        "stable_sha256": sha256(json.dumps(digest_data,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        "scientific_pass": False, "protected_first_use": False,
    }


if __name__ == "__main__":
    print(json.dumps(study(), sort_keys=True, indent=2))
