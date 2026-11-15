"""FKP-02 development-only native-style numerical relationship selector.

Directly stores an inferred parent-triplet plus a learned-gate-built truth table
for each public effect bit. The input relation basis is acquired separately
from 16,384 public foundation interventions. The target family/parents/held
labels never enter fit(). This is NOT the accepted Yggdrasil native substrate.

Frozen research candidate on 2026-11-15, before first DEV fit-and-score:
- Search all 3-parent Boolean functions constructible from learned binary gates.
- Exact match to 16 PUBLIC observed (action, consequence) pairs.
- Choose shallowest constructed function, then function and parent IDs.
- Compare identical candidate space with depth prior ablated.
- No external model/API, hidden source internals, online held updates, or seeds.
"""
from __future__ import annotations

import hashlib
import json
from itertools import combinations


def truly_three_input(function: int) -> bool:
    """Every one of the three abstract inputs changes this Boolean function."""
    if type(function) is not int or not 0 <= function <= 255:
        return False
    for shift in range(3):
        if not any(((function >> row) ^ (function >> (row ^ (1 << shift)))) & 1
                   for row in range(8)):
            return False
    return True


def hypothesis_functions(learned_compositions: dict[int, dict]) -> tuple[tuple[int, int], ...]:
    """Discover program functions from the acquired foundation; NOT source law."""
    found = tuple(sorted(
        (int(v["depth"]), int(fn))
        for fn, v in learned_compositions.items()
        if truly_three_input(fn)
    ))
    if not found:
        raise ValueError("FKP02_NO_COMPOSITIONAL_FUNCTIONS")
    return found


def _patterns(inputs: tuple[int, ...], triple: tuple[int, int, int]) -> tuple[int, ...]:
    """Eight pattern masks; each bit is one public action input."""
    out = [0] * 8
    a, b, c = triple
    for idx, value in enumerate(inputs):
        row = ((value >> a) & 1) | (((value >> b) & 1) << 1) | (((value >> c) & 1) << 2)
        out[row] |= 1 << idx
    return tuple(out)


def _signatures(pattern_masks: tuple[int, ...]) -> list[int]:
    """Every abstract 3-variable Boolean function expressed on public inputs."""
    result = [0] * 256
    for table in range(1, 256):
        lowest = table & -table
        result[table] = result[table ^ lowest] | pattern_masks[lowest.bit_length() - 1]
    return result


def fit(
    observed_actions: tuple[int, ...],
    observed_outcomes: tuple[int, ...],
    learned_functions: tuple[tuple[int, int], ...],
    *,
    use_learned_depth: bool = True
) -> dict[str, object]:
    """Fit exactly 16 real outcomes; no training input ever uses held labels."""
    if (len(observed_actions) != 16 or len(observed_outcomes) != 16
        or len(set(observed_actions)) != 16
        or any(type(x) is not int or not 0 <= x < 65536 for x in observed_actions)
        or any(type(y) is not int or not 0 <= y < 16 for y in observed_outcomes)):
        raise ValueError("FKP02_PUBLIC_TRAINING_EVIDENCE_INVALID")
    if not learned_functions:
        raise ValueError("FKP02_MISSING_LEARNED_BASIS")
    for depth, function in learned_functions:
        if type(depth) is not int or depth < 1 or not truly_three_input(function):
            raise ValueError("FKP02_LEARNED_BASIS_INVALID")
    targets = tuple(sum(((value >> effect) & 1) << idx
                        for idx, value in enumerate(observed_outcomes))
                    for effect in range(4))
    chosen = [None] * 4
    scores = [None] * 4
    compatible = [0] * 4
    searched = 0
    # This exact candidate search is a development algorithm, NOT a learned
    # exploration policy. All temporary candidates count toward resource cost.
    for triple in combinations(range(16), 3):
        signatures = _signatures(_patterns(observed_actions, triple))
        for depth, function in learned_functions:
            searched += 1
            sig = signatures[function]
            for effect, target in enumerate(targets):
                if sig == target:
                    compatible[effect] += 1
                    priority = ((depth if use_learned_depth else 0),
                                function, *triple)
                    if scores[effect] is None or priority < scores[effect]:
                        scores[effect] = priority
                        chosen[effect] = (*triple, function)
    if any(value is None for value in chosen):
        raise ValueError("FKP02_UNEXPLAINED_PUBLIC_OUTCOME_ABSTAIN")
    return {
        "schema": "fkp02.native-style-direct-program.v1",
        "programs": [list(p) for p in chosen],
        "compatible_hypotheses_per_effect": compatible,
        "programs_searched": searched,
        "learned_depth_prior_enabled": bool(use_learned_depth),
        "public_training_actions": 16,
        "learned_functions": len(learned_functions),
    }


def predict(program_state: dict[str, object], query: int) -> int:
    """Execute the four newly written numerical causal relationships."""
    if (type(query) is not int or not 0 <= query < 65536
        or program_state.get("schema") != "fkp02.native-style-direct-program.v1"):
        raise ValueError("FKP02_PREDICTION_STATE_INVALID")
    result = 0
    programs = program_state["programs"]
    if len(programs) != 4:
        raise ValueError("FKP02_PROGRAM_COUNT_INVALID")
    for output, (a, b, c, function) in enumerate(programs):
        local_state = ((query >> a) & 1) | (((query >> b) & 1) << 1) | (((query >> c) & 1) << 2)
        result |= ((function >> local_state) & 1) << output
    return result


def cold_roundtrip(program_state: dict[str, object]) -> tuple[dict[str, object], str]:
    checkpoint = json.dumps(program_state, sort_keys=True, separators=(",", ":"))
    restored = json.loads(checkpoint)
    assert restored == program_state
    return restored, hashlib.sha256(checkpoint.encode("utf-8")).hexdigest()
