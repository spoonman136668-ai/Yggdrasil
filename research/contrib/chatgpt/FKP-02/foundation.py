"""FKP-02 DEV foundation priming: acquire generic 2-input Boolean motifs FROM public experiences.

This module reads only PublicView allowed actions and their observed consequences.
No source-private parent, family, seed, HMAC key or protected outcomes are used.
The 3-input program synthesizer operates on the LEARNED 2-input truth tables,
not a pre-loaded MUX/MAJ instruction library.

This is a foundation-mechanism TEST, not a predictive model qualification.
"""
from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import INPUT_BITS, EFFECT_BITS, PublicCausalWorld

PUBLIC_FOUNDATION = range(10000, 10256)
N_INPUTS = 16
N_SAMPLES = 64


def infer_pair_tables(observed: tuple[tuple[int, int], ...], output_bit: int):
    """Possible (parent1,parent2,full two-input truth-table) from ONLY observed data."""
    if not 0 <= output_bit < EFFECT_BITS or len(observed) != N_SAMPLES:
        raise ValueError("FKP02_BAD_FOUNDATION_EVIDENCE")
    possibilities = []
    for first, second in combinations(range(INPUT_BITS), 2):
        observed_bits = [-1] * 4
        consistent = True
        for action, consequence in observed:
            row = ((action >> first) & 1) | (((action >> second) & 1) << 1)
            bit = (consequence >> output_bit) & 1
            if observed_bits[row] != -1 and observed_bits[row] != bit:
                consistent = False
                break
            observed_bits[row] = bit
        if consistent and all(x >= 0 for x in observed_bits):
            truth_table = sum(v << i for i, v in enumerate(observed_bits))
            possibilities.append((first, second, truth_table))
    return tuple(possibilities)


def acquire_foundation_bank():
    """Precisely 256 x64 real public actions; no teacher gates or hidden rule labels."""
    histogram: dict[int, int] = {}
    unique_effects = 0
    ambiguous_effects = 0
    input_sha = hashlib.sha256()
    for seed in PUBLIC_FOUNDATION:
        source = PublicCausalWorld(seed)
        public = source.public_view()
        history = tuple((x, source.observe(x)) for x in public.allowed_actions)
        assert len(history) == N_SAMPLES
        for x, y in history:
            input_sha.update(x.to_bytes(2, "big") + bytes([y]))
        for out in range(EFFECT_BITS):
            candidates = infer_pair_tables(history, out)
            if len(candidates) != 1:
                ambiguous_effects += 1
                continue
            unique_effects += 1
            _, _, table = candidates[0]
            histogram[table] = histogram.get(table, 0) + 1
    checkpoint = json.dumps(
        {"learned_two_input_tables": dict(sorted(histogram.items()))},
        sort_keys=True, separators=(",", ":"))
    restored = json.loads(checkpoint)
    assert {int(k):v for k,v in restored["learned_two_input_tables"].items()} == histogram
    return {
        "foundation_worlds": len(PUBLIC_FOUNDATION),
        "source_actions_observed": len(PUBLIC_FOUNDATION) * N_SAMPLES,
        "source_effect_bits_observed": len(PUBLIC_FOUNDATION) * N_SAMPLES * EFFECT_BITS,
        "unique_effects": unique_effects,
        "ambiguous_effects": ambiguous_effects,
        "learned_table_counts": dict(sorted(histogram.items())),
        "public_history_sha256": input_sha.hexdigest(),
        "cold_checkpoint_sha256": hashlib.sha256(checkpoint.encode()).hexdigest(),
        "cold_restore_equal": True,
    }


def apply_learned_table(gate: int, a: int, b: int) -> int:
    """Apply an arbitrary learned two-input table to two 3-bit-domain functions."""
    result = 0
    for state in range(8):
        x = (a >> state) & 1
        y = (b >> state) & 1
        result |= ((gate >> (x + 2*y)) & 1) << state
    return result


def compose_generic_programs(gates: tuple[int, ...], max_depth=5):
    """Generic closure over symbolic 3-input signals; no target operator names used."""
    if not gates or any(not isinstance(g, int) or not 0 <= g <= 15 for g in gates):
        raise ValueError("FKP02_BAD_LEARNED_GATE")
    known = {}
    for input_number in range(3):
        table = sum(((i >> input_number) & 1) << i for i in range(8))
        known[table] = {"depth": 0, "expression": ("input", input_number)}
    counts = [len(known)]
    for depth in range(1, max_depth + 1):
        states = sorted(known)
        new = {}
        for left in states:
            for right in states:
                for gate in gates:
                    value = apply_learned_table(gate, left, right)
                    if value not in known and value not in new:
                        new[value] = {
                            "depth": depth, "expression": (gate, left, right)
                        }
        known.update(new)
        counts.append(len(known))
        if len(known) == 256:
            break
    return known, counts


def development_foundation_audit():
    foundation = acquire_foundation_bank()
    gates = tuple(int(k) for k in foundation["learned_table_counts"])
    grammar, counts = compose_generic_programs(gates, max_depth=5)
    # Checker-only evaluator targets; NONE of these operators are given to
    # acquire_foundation_bank() or compose_generic_programs().
    from source import evaluate_gate
    kinds = {
        name: sum(evaluate_gate(state, name, (0, 1, 2)) << state
                  for state in range(8))
        for name in ("mux3", "majority3")
    }
    return {
        "schema": "fkp02.foundation-mechanism-dev.v1",
        "claim": "GENERIC_COMPOSITION_POSSIBLE_NOT_NEW_LAW_LEARNED",
        "protected_worlds_opened": False,
        "foundation": foundation,
        "learned_generic_function_count_by_depth": counts,
        "novel_operator_representations": {
            name: {"constructible": value in grammar,
                   "generic_depth": grammar[value]["depth"] if value in grammar else None}
            for name, value in kinds.items()
        },
        "no_native_yggdrasil_main_change": True,
        "science_status": "DEV_MECHANISM_ONLY_UNVERIFIED",
    }


if __name__ == "__main__":
    print(json.dumps(development_foundation_audit(), sort_keys=True, indent=2))
