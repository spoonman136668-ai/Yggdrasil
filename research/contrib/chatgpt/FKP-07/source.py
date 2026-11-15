"""FKP-07 source-owner only. Fresh public development causal worlds.

The imported FKP-06 public *hypothesis family*, not its consumed DEV targets,
is intentionally reused. Target laws and revision changes belong to this source
owner and must never enter a policy or learner. Protected owner key is external.
"""
from __future__ import annotations
import hashlib
import hmac
import importlib.util
from pathlib import Path
from dataclasses import dataclass

PARENT = Path(__file__).resolve().parent.parent / "FKP-06" / "fkp06.py"
if not PARENT.is_file():
    raise RuntimeError("FKP07_PINNED_FKP06_SOURCE_REQUIRED")
spec = importlib.util.spec_from_file_location("fkp06_frozen", PARENT)
assert spec and spec.loader
public = importlib.util.module_from_spec(spec)
spec.loader.exec_module(public)

SOURCE_SCHEMA = "FKP07-DEV-WORLD-V1"
DEV_KEY = hashlib.sha256(b"FKP07-PUBLIC-DEVELOPMENT-WORLDS-NOT-PROTECTED-SCIENCE").digest()
ORIGINAL = range(800, 824)
REVISIONS = range(840, 848)
FIXTURES = range(880, 884)
PROTECTED = range(1800, 1864)
PROTECTED_NEGATIVE = range(2800, 2816)
MAX_INTERVENTIONS = 64
N_LAWS = public.N_HYP


def _kind(seed: int) -> str:
    if type(seed) is not int:
        raise ValueError("FKP07_WORLD_SEED_INVALID")
    if seed in ORIGINAL:
        return "dev-original"
    if seed in REVISIONS:
        return "dev-revision"
    if seed in FIXTURES:
        return "fixture"
    if seed in PROTECTED:
        return "protected"
    if seed in PROTECTED_NEGATIVE:
        return "protected-negative"
    raise ValueError("FKP07_WORLD_SEED_UNREGISTERED")


def _private_law(seed: int, laws: tuple[tuple[int, ...], ...], key: bytes):
    if seed in REVISIONS:
        old = _private_law(seed - 40, laws, key)
        digest = hmac.new(key, f"FKP07:REV:{seed}".encode(), hashlib.sha256).digest()
        keep_first = (digest[0] & 1) == 0
        original_pairs = (tuple(old[:2]), tuple(old[2:]))
        keep = original_pairs[0 if keep_first else 1]
        replaced = original_pairs[1 if keep_first else 0]
        possible = [(i, j) for i in range(32) for j in range(i + 1, 32)
                    if i not in keep and j not in keep and (i, j) != tuple(sorted(replaced))]
        other = possible[int.from_bytes(digest[1:5], "big") % len(possible)]
        revised = (*keep, *other)
        assert len(set(revised)) == 4
        return revised
    digest = hmac.new(key, f"FKP07:OLD:{seed}".encode(), hashlib.sha256).digest()
    index = int.from_bytes(digest[:8], "big") % len(laws)
    return laws[index]


@dataclass(frozen=True)
class PublicView:
    seed: int
    context_id: int
    action_pool: tuple[int, ...]
    held_inputs: tuple[int, ...]
    bit_width: int
    max_interventions: int


class SourceOwnerWorld:
    __slots__ = ("_law", "_kind", "_view", "_seen")

    def __init__(self, seed: int, laws: tuple[tuple[int, ...], ...], *,
                 owner_key: bytes | None = None):
        kind = _kind(seed)
        if kind.startswith("protected"):
            if type(owner_key) is not bytes or len(owner_key) < 32:
                raise PermissionError("FKP07_PROTECTED_OWNER_KEY_REQUIRED")
            key = owner_key
        else:
            if owner_key is not None:
                raise ValueError("FKP07_PUBLIC_AND_OWNER_KEY_MUST_NOT_MIX")
            key = DEV_KEY
        if len(laws) != N_LAWS:
            raise ValueError("FKP07_SOURCE_LAW_FAMILY_DRIFT")
        self._kind = kind
        self._law = _private_law(seed, laws, key)
        choices, held = public.inputs()
        self._view = PublicView(seed, seed - 40 if kind == "dev-revision" else seed,
                                tuple(choices), tuple(held), 32, MAX_INTERVENTIONS)
        self._seen: set[int] = set()

    def public_view(self) -> PublicView:
        return self._view

    def observe(self, action: int) -> int:
        if type(action) is not int or action not in self._view.action_pool:
            raise ValueError("FKP07_NONPUBLIC_ACTION")
        if action in self._seen:
            raise ValueError("FKP07_DUPLICATE_PAID_INTERVENTION")
        if len(self._seen) >= MAX_INTERVENTIONS:
            raise PermissionError("FKP07_PAID_ACTION_CAP")
        self._seen.add(action)
        return public.consequence(self._law, action)

    def dev_held_labels(self, held: tuple[int, ...]) -> tuple[int, ...]:
        if self._kind not in ("dev-original", "dev-revision", "fixture"):
            raise PermissionError("FKP07_NO_PROTECTED_HELD_IN_RESEARCH")
        if held != self._view.held_inputs or len(self._seen) != MAX_INTERVENTIONS:
            raise PermissionError("FKP07_HELD_ONLY_AFTER_FULL_SEALED_INTERVENTIONS")
        return tuple(public.consequence(self._law, a) for a in held)

    @property
    def used_actions(self) -> int:
        return len(self._seen)


def source_preflight():
    laws = tuple(public.laws())
    cases = []
    for seed in (880, 881):
        a = SourceOwnerWorld(seed, laws)
        b = SourceOwnerWorld(seed, laws)
        p = a.public_view()
        assert p == b.public_view()
        assert len(set(p.action_pool)) == 128
        assert len(set(p.held_inputs)) == 256
        assert not set(p.action_pool).intersection(p.held_inputs)
        results = [a.observe(x) for x in p.action_pool[:64]]
        assert results == [b.observe(x) for x in p.action_pool[:64]]
        assert all(x in (0, 1) for x in results)
        cases.append({"seed": seed, "real_feedback": len(results)})
    for seed in (1800, 1863, 2800, 2815):
        try:
            SourceOwnerWorld(seed, laws)
        except PermissionError:
            pass
        else:
            raise AssertionError("FKP07_PROTECTED_KEY_FENCE_LEAK")
    return {"schema": "fkp07.source-preflight.v1", "fixtures": cases,
            "hypotheses": len(laws), "primary_opened": False}


if __name__ == "__main__":
    import json
    print(json.dumps(source_preflight(), sort_keys=True))
