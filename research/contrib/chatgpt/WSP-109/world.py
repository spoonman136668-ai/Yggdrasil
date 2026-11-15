"""WSP109 sealed synthetic causal law family and observed interventions.

The law oracle is *evaluator-owned*. Learner modules never import it. The
world has 36 possible four-active-rule templates, three feedback interventions
per model policy, and 64 novel compound add/remove queries per held-out world.
This remains synthetic DEV research, not independent original scientific use.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations
from pathlib import Path
import struct
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "WSP-108"))
from world import query_scene, path_features

FIT_SEEDS = tuple(range(31001, 31013))
TRANSFER_SEEDS = tuple(range(41001, 41013))
FIXTURE_SEEDS = (51001, 51002)
N_RULES = 9
N_HYPOTHESES = 36
ACTION_BUDGET = 3
QUERIES_PER_WORLD = 64
HYPOTHESIS_DOMAIN = b"WSP109-HYPOTHESIS-v1\x00"
RANDOM_DOMAIN = b"WSP109-RANDOM-v1\x00"
ALL_4_BIT_MASKS = tuple(
    sum(1 << i for i in kinds) for kinds in combinations(range(N_RULES), 4)
)
HYPOTHESES = tuple(sorted(
    ALL_4_BIT_MASKS,
    key=lambda mask: (sha256(HYPOTHESIS_DOMAIN + struct.pack("<H",mask)).digest(), mask)
)[:N_HYPOTHESES])


def private_law(seed: int) -> int:
    """Not for learners: oracle-only mapping never passed to policy."""
    if seed in FIT_SEEDS:
        return HYPOTHESES[seed - FIT_SEEDS[0]]
    if seed in TRANSFER_SEEDS:
        return HYPOTHESES[18 + seed - TRANSFER_SEEDS[0]]
    if seed in FIXTURE_SEEDS:
        return HYPOTHESES[30 + seed - FIXTURE_SEEDS[0]]
    raise ValueError("unregistered prospective synthetic world seed")


def masked_feedback(seed: int, kind: int) -> bool:
    """Actual consequence of an allowed singleton edge-add intervention."""
    if type(kind) is not int or not 0 <= kind < N_RULES:
        raise ValueError("invalid intervention kind")
    return bool(private_law(seed) & (1 << kind))


def feature_bits(features) -> int:
    f = tuple(features)
    if len(f) != N_RULES or any(type(x) not in (int, bool) or x not in (0, 1) for x in f):
        raise ValueError("exact nine observed two-hop features required")
    return sum(1 << i for i, present in enumerate(f) if present)


def private_query_truth(seed: int, features) -> bool:
    """Harness may call only AFTER every frozen prediction is SHA-sealed."""
    return bool(private_law(seed) & feature_bits(features))


def random_action_priority(seed: int, kind: int) -> bytes:
    return sha256(RANDOM_DOMAIN + struct.pack("<IB", seed, kind)).digest()


def random_action_sequence(seed: int) -> tuple[int, ...]:
    return tuple(sorted(range(N_RULES),
                        key=lambda i: (random_action_priority(seed,i),i))[:ACTION_BUDGET])


def validate_world_schedule() -> None:
    if (len(HYPOTHESES) != 36 or len(set(HYPOTHESES)) != 36 or
            any(x.bit_count() != 4 for x in HYPOTHESES)):
        raise AssertionError("hypothesis family changed")
    if set(FIT_SEEDS) & set(TRANSFER_SEEDS) or set(FIXTURE_SEEDS) & (set(FIT_SEEDS) | set(TRANSFER_SEEDS)):
        raise AssertionError("cohort overlap")
    fit = {private_law(seed) for seed in FIT_SEEDS}
    transfer = {private_law(seed) for seed in TRANSFER_SEEDS}
    if len(fit) != 12 or len(transfer) != 12 or fit & transfer:
        raise AssertionError("unfamiliar hidden causal laws overlap")
    if len(ALL_4_BIT_MASKS) != 126:
        raise AssertionError("unexpected combinatorial hypothesis count")
