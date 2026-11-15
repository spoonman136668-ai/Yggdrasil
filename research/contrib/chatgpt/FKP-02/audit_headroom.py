"""FKP-02 source-only independent exact-family reference, DEVELOPMENT WORLDS ONLY.

This is an identifiability/headroom audit, NOT a Yggdrasil learner.
It is deliberately given the held *operator family* and so is a strong
reference, not a weakened control. It never opens protected primary seeds.
"""
from __future__ import annotations
from itertools import combinations
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import EFFECT_BITS, INPUT_BITS, PublicCausalWorld

FULL64 = (1 << 64) - 1
MASK16 = (1 << 16) - 1


def bit_tables(inputs: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(((value >> j) & 1) << i
                     for i, value in enumerate(inputs))
                 for j in range(INPUT_BITS))


def signatures(tables: tuple[int, ...], family: str):
    """Distinct family hypotheses with the FULL source-generator prior."""
    # Use OR/XOR/composition only on the public intervention bit columns.
    for a, b, c in combinations(range(INPUT_BITS), 3):
        if family == "majority3":
            yield ((tables[a] & tables[b]) |
                   (tables[a] & tables[c]) |
                   (tables[b] & tables[c]))
        elif family == "mux3":
            trio = (a, b, c)
            for ctrl in trio:
                d1, d2 = (v for v in trio if v != ctrl)
                yield (tables[ctrl] & tables[d1]) | (~tables[ctrl] & tables[d2])
                yield (tables[ctrl] & tables[d2]) | (~tables[ctrl] & tables[d1])
        else:
            raise ValueError("FKP02_AUDIT_FAMILY_INVALID")


def signature_pair(probes: tuple[int, ...], held: tuple[int, ...], family: str):
    """Single pass program enumeration; no evaluator-private rule access."""
    source_mask = (1 << len(probes)) - 1
    held_mask = (1 << len(held)) - 1
    a = bit_tables(probes)
    b = bit_tables(held)
    for x, y in zip(signatures(a, family), signatures(b, family)):
        yield x & source_mask, y & held_mask


def fit_and_score(
    candidates: tuple[tuple[int, int], ...],
    observed_truth: int, held_truth: int, revealed_count: int
) -> tuple[tuple[int, ...], int]:
    mask = (1 << revealed_count) - 1
    # Distinct functions get one equal prior weight in the allowed family.
    matches = sorted({held for exposed, held in candidates
                      if (exposed & mask) == (observed_truth & mask)})
    if not matches:
        raise AssertionError("FKP02_SOURCE_TRUE_LAW_MISSING_FROM_REFERENCE")
    predictions = []
    for bit in range(128):
        supporting = sum((signature >> bit) & 1 for signature in matches)
        # Deterministic ties abstain toward 0; all arms share identical rule.
        predictions.append(int(supporting * 2 > len(matches)))
    assert len(predictions) == 128
    return tuple(predictions), len(matches)


def source_headroom_dev() -> dict[str, object]:
    scores = {16: [], 64: []}
    total_ambiguous_worlds = 0
    candidate_counts = {16: [], 64: []}
    per_world = []

    for seed in range(200, 216):
        src = PublicCausalWorld(seed)
        public = src.public_view()
        # Source owner's DEV-only consequences, not protected scientific data.
        public_truth = tuple(src.observe(x) for x in public.allowed_actions)
        held_truth = tuple(src.development_only_eval(x)
                           for x in public.held_inputs)
        family = "mux3" if seed % 2 == 0 else "majority3"
        program_signatures = tuple(
            signature_pair(public.allowed_actions, public.held_inputs, family))
        assert len(program_signatures) == (3360 if family == "mux3" else 560)
        preds = {16: [], 64: []}
        count_by_budget = {16: [], 64: []}

        for output in range(EFFECT_BITS):
            observations = sum(((y >> output) & 1) << i
                               for i, y in enumerate(public_truth))
            truth = sum(((y >> output) & 1) << i
                        for i, y in enumerate(held_truth))
            for count in (16, 64):
                predictions, n_matches = fit_and_score(
                    program_signatures, observations, truth, count)
                preds[count].append(predictions)
                count_by_budget[count].append(n_matches)
                candidate_counts[count].append(n_matches)

        if any(v > 1 for v in count_by_budget[16]):
            total_ambiguous_worlds += 1

        world_scores = {}
        for count in (16, 64):
            correct_vectors = 0
            for i, target in enumerate(held_truth):
                pred = sum(preds[count][out][i] << out
                           for out in range(EFFECT_BITS))
                correct_vectors += int(pred == target)
            accuracy = correct_vectors / len(held_truth)
            world_scores[str(count)] = accuracy
            scores[count].append(accuracy)
        per_world.append({
            "cohort": "development", "family": family,
            "unseen_states": len(public.held_inputs),
            "16_action_vector_accuracy": world_scores["16"],
            "64_action_vector_accuracy": world_scores["64"],
            "consistent_functions_16": count_by_budget[16],
            "consistent_functions_64": count_by_budget[64],
        })

    mean16 = sum(scores[16]) / len(scores[16])
    mean64 = sum(scores[64]) / len(scores[64])
    gap = mean64 - mean16
    passed = gap >= 0.02 and mean64 >= 0.98 and total_ambiguous_worlds >= 4
    return {
        "schema": "fkp02.source-dev-identifiability.v1",
        "claim": "SOURCE_DEV_HEADROOM_ONLY_NOT_MODEL_LEARNING",
        "protected_primary_opened": False,
        "dev_worlds": 16,
        "held_per_dev_world": 128,
        "family_aware_exact_reference": True,
        "exact_reference_candidate_family_counts": {"mux3": 3360, "majority3": 560},
        "source_oracle_only_for_development_scoring": True,
        "strong_reference_16_vector_accuracy": mean16,
        "strong_reference_64_vector_accuracy": mean64,
        "accuracy_headroom_gap": gap,
        "worlds_with_ambiguous_16_action_laws": total_ambiguous_worlds,
        "stage0_thresholds": {"gap_min": 0.02, "strong_64_min": 0.98,
                              "ambiguous_worlds_min": 4},
        "stage0_dev_headroom_pass": passed,
        "science_status": "UNVERIFIED_NO_PRIMARY",
        "per_world": per_world,
    }


if __name__ == "__main__":
    print(json.dumps(source_headroom_dev(), sort_keys=True, indent=2))
