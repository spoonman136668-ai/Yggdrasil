"""WSP110 synthetic million-fact graph source and private withheld law.

This module is a deterministic test world, not a knowledge source from the
outside world. It returns one million original *observed* facts and no
output X/Y facts. Hidden stage labels are evaluator-only, never imported
by the learner module.
"""
from __future__ import annotations

from hashlib import sha256
import numpy as np

N_GROUPS = 25_000
N_SUPPORT = 3_000
N_TEST = N_GROUPS - N_SUPPORT
N_DISTRACTORS = 925_000
N_INPUT_FACTS = 1_000_000
X_REL = 8
Y_REL = 9
LEFT_RELATIONS = tuple(range(4))
MIDDLE_RELATIONS = tuple(range(4, 8))
THIRD_RELATIONS = tuple(range(10, 14))
GENERATOR_VERSION = "WSP110|GEN|v1"


def _digest(*parts: object) -> bytes:
    return sha256("|".join(str(x) for x in parts).encode("ascii")).digest()


def types_for_group(group: int) -> tuple[int, int, int]:
    if type(group) is not int or not 0 <= group < N_GROUPS:
        raise ValueError("group out of observed world range")
    a = _digest(GENERATOR_VERSION, group, "a")[0] % 4
    b = 4 + _digest(GENERATOR_VERSION, group, "b")[0] % 4
    c = 10 + _digest(GENERATOR_VERSION, group, "c")[0] % 4
    return a, b, c


def support_groups() -> range:
    return range(N_SUPPORT)


def heldout_groups() -> range:
    return range(N_SUPPORT, N_GROUPS)


def original_facts() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exactly 25k independent length-three paths plus 925k isolated edges.

    Entities are opaque numeric IDs; no X or Y labels or target facts are
    present. The meaningful 75k edges and the distractor 925k are all equally
    written into the native sparse parameter store.
    """
    groups = np.arange(N_GROUPS, dtype=np.uint32)
    sources = np.empty(N_INPUT_FACTS, dtype=np.uint32)
    relations = np.empty(N_INPUT_FACTS, dtype=np.uint8)
    targets = np.empty(N_INPUT_FACTS, dtype=np.uint32)
    starts = groups * np.uint32(4)
    # Direct observed chain facts: (s,a,m), (m,b,n), (n,c,t).
    sources[:N_GROUPS] = starts
    targets[:N_GROUPS] = starts + np.uint32(1)
    sources[N_GROUPS:2*N_GROUPS] = starts + np.uint32(1)
    targets[N_GROUPS:2*N_GROUPS] = starts + np.uint32(2)
    sources[2*N_GROUPS:3*N_GROUPS] = starts + np.uint32(2)
    targets[2*N_GROUPS:3*N_GROUPS] = starts + np.uint32(3)
    for g in range(N_GROUPS):
        a,b,c = types_for_group(g)
        relations[g] = a
        relations[N_GROUPS+g] = b
        relations[2*N_GROUPS+g] = c
    filler = np.arange(N_DISTRACTORS, dtype=np.uint32)
    sources[3*N_GROUPS:] = np.uint32(100000) + filler * np.uint32(3)
    targets[3*N_GROUPS:] = np.uint32(100001) + filler * np.uint32(3)
    relations[3*N_GROUPS:] = np.uint8(16) + np.asarray(filler % 16, dtype=np.uint8)
    if (len(sources) != N_INPUT_FACTS or
            int(sources.max()) >= 2**22 or int(targets.max()) >= 2**22):
        raise AssertionError("million-fact native integer bounds changed")
    return sources,relations,targets


def _stage1_active() -> frozenset[int]:
    return frozenset(sorted(
        range(16), key=lambda x:_digest("WSP110","LAW1","v1",x)
    )[:6])


def _stage2_active() -> frozenset[int]:
    return frozenset(sorted(
        range(4), key=lambda x:_digest("WSP110","LAW2","v1",x)
    )[:2])


def hidden_x(group: int) -> bool:
    """Evaluator-only, never imported by learners or scored before sealing."""
    a,b,_=types_for_group(group)
    kind=a*4+(b-4)
    base=kind in _stage1_active()
    flip=int.from_bytes(_digest("WSP110","EX1","v1",group),"big") % 32 == 0
    return bool(base ^ flip)


def hidden_y(group: int) -> bool:
    """Evaluator-only, Y requires actual hidden X, then second hidden law."""
    if not hidden_x(group):
        return False
    _,_,c=types_for_group(group)
    base=(c-10) in _stage2_active()
    flip=int.from_bytes(_digest("WSP110","EX2","v1",group),"big") % 32 == 0
    return bool(base ^ flip)


def support_feedback() -> tuple[tuple[int,bool,bool], ...]:
    """Reveal *training only* outcomes; no heldout group ever returned."""
    return tuple((g,hidden_x(g),hidden_y(g)) for g in support_groups())
