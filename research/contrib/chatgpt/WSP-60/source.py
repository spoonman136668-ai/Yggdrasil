"""WSP60 evaluator-only fresh-seed world wrapper.

Reuses the EXACT physical/task source family of the frozen WSP59 negative
experiment, but creates 12 disjoint fresh SELFTEST worlds. The tested learner
does not import this file or the WSP59 evaluator.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
from random import Random
import sys

SEEDS = tuple(range(2601, 2613))
SOURCE_PATH = Path(__file__).resolve().parents[1] / "WSP-59" / "source.py"
_spec = importlib.util.spec_from_file_location("_wsp59_pinned_evaluator", SOURCE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("missing frozen WSP59 generator")
_engine = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _engine
_spec.loader.exec_module(_engine)

STATES = _engine.STATES
CHANNELS = _engine.CHANNELS
PREDICATES = _engine.PREDICATES


def build_world(seed, cohort="SELFTEST"):
    if cohort != "SELFTEST" or type(seed) is not int or seed not in SEEDS:
        raise PermissionError("WSP60 is fresh-seed SELFTEST only")
    maps, subsets, roles = _engine._hidden_physics(seed)
    rng = _engine._rng(seed, "grounded-lexicon")
    names = [f"n{idx:02x}".encode("ascii") for idx in range(128)]
    rng.shuffle(names)
    world = _engine.World(
        seed, maps, subsets, roles, tuple(names[:len(PREDICATES)])
    )
    assert len(world.demonstrations()) == 9
    assert len(world.tasks()) == 32
    assert all(_engine._nonaffine(p) for p in maps)
    return world
