"""NCI06-D256 frozen SOURCE-FREE dev falsifier, NOT primary scientific first use.

Requires dev256-freeze.md prereg commit cc6def55... preceding this source.
Every 3-input Boolean mask is an openly consumed synthetic engineering world.
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import time

from operator_core import ExactCompositionBayes, OperatorBank
from residual_operator import ResidualComposer, ExactTruthTableBayes, FIXED_MASKS
from test_residual_operator import KEYS, bank_fixture


PREFIX = b"NCI06-D256:v1:"
WORLD_COUNT = 256
FIT = 96
VALID = 64
HELD = 128
DECISIONS = 32
ARM_NAMES = ("Residual", "Exact256", "Exact24", "ID3", "Prior")
NOISE = 0.06


def public_input(i):
    code = i % 64
    return tuple((code >> j) & 1 for j in range(5)), (code >> 5) & 1


def bit_index(bits, action):
    # Independent evaluator: the source-free bank_fixture's public mapping.
    # No learner receives the hidden target mask or direct lookup.
    return bits[0] | ((bits[1] ^ action) << 1) | (bits[2] << 2)


def flip(mask, i):
    digest = hashlib.sha256(PREFIX + str(mask).encode("ascii")
                            + b":" + str(i).encode("ascii")).digest()
    return int(digest[0] < 16)


def build_world(mask):
    rows = []
    for i in range(FIT + VALID + HELD):
        bits, action = public_input(i)
        truth = (mask >> bit_index(bits, action)) & 1
        outcome = truth ^ flip(mask, i)
        rows.append((bits, action, outcome))
    return rows


def bernoulli_brier(forecast, true_bit):
    p = NOISE + (1 - 2 * NOISE) * true_bit
    if forecast is None or not math.isfinite(forecast) or not 0 <= forecast <= 1:
        raise ValueError("invalid forecast; no unseen examples may be skipped")
    return p * (1 - forecast) ** 2 + (1 - p) * forecast ** 2


def entropy(rows):
    if not rows:
        return 0.0
    pos = sum(y for _, y in rows)
    p = pos / len(rows)
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def fit_id3(rows):
    """Saturating ID3 with all six public binary features, not underfit."""
    if len(rows) != FIT:
        raise ValueError("conventional control fit count must be exactly 96")
    prepared = [(tuple((*bits, action)), y) for bits, action, y in rows]

    def fit(subset, features):
        positive = sum(y for _, y in subset)
        if not subset:
            return (0.5,)
        if not features or positive == 0 or positive == len(subset):
            return ((positive + 1) / (len(subset) + 2),)
        old_entropy = entropy(subset)
        choices = []
        for axis in features:
            zero = [row for row in subset if row[0][axis] == 0]
            one = [row for row in subset if row[0][axis] == 1]
            remaining = ((len(zero) * entropy(zero) +
                          len(one) * entropy(one)) / len(subset))
            choices.append((old_entropy - remaining, -axis, axis, zero, one))
        # Even zero information-gain dimensions are split. Depth six can
        # memorize every distinct public context when evidence permits.
        _, _, axis, zero, one = max(choices, key=lambda x: (x[0], x[1]))
        rem = tuple(k for k in features if k != axis)
        return (axis, fit(zero, rem), fit(one, rem))

    return fit(prepared, tuple(range(6)))


def predict_id3(tree, bits, action):
    x = tuple((*bits, action))
    while len(tree) == 3:
        tree = tree[1 if x[tree[0]] == 0 else 2]
    return tree[0]


def compare():
    bank = bank_fixture(action_conditional=True)
    original_checkpoint = bank.snapshot()
    old_queries = [(bits, action, tuple(bank.read(key, bits, action)
                    for key in KEYS))
                   for bits, action in (
                       ((1, 0, 1, 0, 0), 0), ((1, 0, 1, 0, 0), 1),
                       ((0, 1, 0, 1, 0), 0), ((0, 1, 0, 1, 0), 1))]
    totals = {name: {"brier": 0.0, "reward": 0.0, "regret": 0.0,
                     "wins": 0, "ties": 0} for name in ARM_NAMES}
    coverage = 0
    born = 0
    false_births = 0
    retained = 0
    used_labels = 0
    per_mask = []

    for mask in range(WORLD_COUNT):
        tape = build_world(mask)
        train, valid, held = tape[:FIT], tape[FIT:FIT+VALID], tape[FIT+VALID:]
        model = ResidualComposer(bank, KEYS)
        for bits, action, outcome in train:
            model.observe(bits, action, outcome, phase="TRAIN")
        for bits, action, outcome in valid:
            model.observe(bits, action, outcome, phase="VALID")
        accepted = model.compile()
        if accepted:
            born += 1
            if mask in FIXED_MASKS:
                false_births += 1
            frozen_state = model.snapshot()
            restored = ResidualComposer.restore(
                OperatorBank.restore(original_checkpoint), frozen_state)
            if restored.snapshot() != frozen_state:
                raise RuntimeError("cold residual checkpoint mismatch")
            for bits, action, expected in old_queries:
                if tuple(bank.read(key, bits, action) for key in KEYS) != expected:
                    raise RuntimeError("old native-like public query regressed")
                if model.predict(bits, action) != restored.predict(bits, action):
                    raise RuntimeError("cold readout mismatch")
            retained += 1
        if bank.snapshot() != original_checkpoint:
            raise RuntimeError("primitive bank altered by new learning")
        exact = ExactTruthTableBayes(bank, KEYS).fit(train)
        classic = ExactCompositionBayes(bank, KEYS).fit(train)
        id3 = fit_id3(train)
        predictors = {
            "Residual": lambda b, a: model.predict(b, a) if accepted else 0.5,
            "Exact256": exact.predict,
            "Exact24": classic.predict,
            "ID3": lambda b, a: predict_id3(id3, b, a),
            "Prior": lambda b, a: 0.5,
        }
        briers = {name: 0.0 for name in ARM_NAMES}
        expected_rewards = {name: 0.0 for name in ARM_NAMES}
        regrets = {name: 0.0 for name in ARM_NAMES}
        for bits, action, _ in held:
            truth = (mask >> bit_index(bits, action)) & 1
            for name, f in predictors.items():
                q = f(bits, action)
                briers[name] += bernoulli_brier(q, truth)
            coverage += int(accepted)
        for state in range(DECISIONS):
            bits = tuple((state >> i) & 1 for i in range(5))
            p0 = NOISE + (1 - 2 * NOISE) * ((mask >> bit_index(bits, 0)) & 1)
            p1 = NOISE + (1 - 2 * NOISE) * ((mask >> bit_index(bits, 1)) & 1)
            optimal = max(p0, p1)
            for name, f in predictors.items():
                choice = int(f(bits, 1) > f(bits, 0))
                actual = p1 if choice else p0
                expected_rewards[name] += actual
                regrets[name] += optimal - actual
        reference = briers["Exact256"]
        for name in ARM_NAMES:
            totals[name]["brier"] += briers[name]
            totals[name]["reward"] += expected_rewards[name]
            totals[name]["regret"] += regrets[name]
            if briers[name] < reference - 1e-10:
                totals[name]["wins"] += 1
            elif abs(briers[name] - reference) <= 1e-10:
                totals[name]["ties"] += 1
        per_mask.append((mask, accepted, tuple(round(briers[name], 10)
                                              for name in ARM_NAMES)))
        used_labels += len(train) + len(valid)

    summary = {
        "schema": "nci06.d256.source-free-dev-result.v1",
        "classification": "DEVELOPMENT_ONLY_NOT_SCIENCE",
        "cohort": "fully_exhaustive_public_masks_0_to_255_no_seeds",
        "worlds": WORLD_COUNT, "fit_per_world": FIT, "valid_per_world": VALID,
        "held_per_world": HELD, "policy_queries_per_world": DECISIONS,
        "fit_valid_labels_seen": used_labels,
        "held_forecasts_per_arm": WORLD_COUNT * HELD,
        "policy_choices_per_arm": WORLD_COUNT * DECISIONS,
        "residual_born": born, "false_birth_fixed_mask": false_births,
        "residual_held_coverage": round(coverage / (WORLD_COUNT * HELD), 12),
        "cold_old_return_checks": retained * len(old_queries),
        "old_checkpoint_unchanged": bank.snapshot() == original_checkpoint,
        "fixed_grammar_unique_truth_masks": len(FIXED_MASKS),
        "arms": {name: {
            "expected_brier": round(totals[name]["brier"] /
                                    (WORLD_COUNT * HELD), 12),
            "expected_policy_reward": round(totals[name]["reward"] /
                                            (WORLD_COUNT * DECISIONS), 12),
            "expected_policy_regret": round(totals[name]["regret"] /
                                            (WORLD_COUNT * DECISIONS), 12),
            "world_wins_vs_exact256": totals[name]["wins"],
            "world_ties_vs_exact256": totals[name]["ties"]}
            for name in ARM_NAMES},
    }
    result_delta = (summary["arms"]["Exact256"]["expected_brier"] -
                    summary["arms"]["Residual"]["expected_brier"])
    policy_delta = (summary["arms"]["Residual"]["expected_policy_reward"] -
                    summary["arms"]["Exact256"]["expected_policy_reward"])
    summary["gain_vs_exact256_confirmed"] = (
        result_delta > 0 and policy_delta > 0)
    summary["classification_summary"] = (
        "DEV_ENG_PASS_NEGATIVE_NO_PAIRED_GAIN" if not summary["gain_vs_exact256_confirmed"]
        else "DEV_ENG_PASS_POSITIVE_TOY_ONLY_NOT_SCIENCE")
    trace = json.dumps(per_mask, separators=(",", ":"), allow_nan=False)
    summary["per_mask_trace_sha256"] = hashlib.sha256(trace.encode("ascii")).hexdigest()
    if (not summary["old_checkpoint_unchanged"] or
            summary["fit_valid_labels_seen"] != 256 * 160 or
            len(per_mask) != 256 or summary["fixed_grammar_unique_truth_masks"] != 8):
        raise RuntimeError("DEV_D256_MECHANICAL_INTEGRITY_FAIL")
    return summary


def main():
    start = time.perf_counter()
    first = compare()
    second = compare()  # Dev-only byte-identical repeat; no protected cohort.
    if first != second:
        raise RuntimeError("DEV_D256_SCORES_NONDETERMINISTIC")
    payload = json.dumps(first, sort_keys=True, separators=(",", ":"), allow_nan=False)
    digest = hashlib.sha256(payload.encode("ascii")).hexdigest()
    print("NCI06_D256_DEV_SCREEN_SHA256=" + digest)
    print("NCI06_D256_DEV_SCREEN=" + payload)
    print("NCI06_D256_DEV_SCREEN_ELAPSED_SECONDS=" +
          str(round(time.perf_counter() - start, 3)))
    print("NCI06_D256_DEV_SCREEN_INTEGRITY_PASS")


if __name__ == "__main__":
    main()
