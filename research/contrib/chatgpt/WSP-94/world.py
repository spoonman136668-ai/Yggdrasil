"""WSP94 deterministic hidden causal-slot intervention world.

This simulator is an independent DEV-only source, never accepted Yggdrasil
runtime state. Learners receive ONLY observations, not private signatures or
the hidden subsets that produced requested goals.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from itertools import combinations
import random

ACTIONS = 5
OUTPUT_BITS = 5
NUISANCE_BITS = 3
MASK = (1 << OUTPUT_BITS) - 1
MAX_DRAWS = 1024

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("ascii")).hexdigest()

def gf2_rank(vectors: tuple[int, ...]) -> int:
    """Rank of bit-vector columns; no numerical float tolerance."""
    basis: dict[int, int] = {}
    for original in vectors:
        v = original
        while v:
            pivot = v.bit_length() - 1
            if pivot in basis:
                v ^= basis[pivot]
            else:
                basis[pivot] = v
                break
    return len(basis)

@dataclass(frozen=True)
class Observation:
    action_id: str
    causal_output_before: int
    causal_output_after: int
    nuisance_before: int
    nuisance_after: int

    def as_record(self) -> dict:
        return {
            "action_id": self.action_id,
            "causal_output_before": self.causal_output_before,
            "causal_output_after": self.causal_output_after,
            "nuisance_before": self.nuisance_before,
            "nuisance_after": self.nuisance_after,
        }

@dataclass(frozen=True)
class Goal:
    goal_id: int
    start: int
    target: int
    max_actions: int = 3

    def for_model(self) -> dict:
        return {
            "start": self.start,
            "target": self.target,
            "max_actions": self.max_actions,
        }

class HiddenCausalWorld:
    def __init__(self, seed: int) -> None:
        if type(seed) is not int or seed < 0 or seed > 1000000000:
            raise ValueError("invalid deterministic world seed")
        self.seed = seed
        rng = random.Random(seed)
        ids = [sha256(f"WSP94/action/{seed}/{i}")[:16] for i in range(ACTIONS)]
        rng.shuffle(ids)
        self.action_ids = tuple(ids)
        hidden = None
        for _ in range(MAX_DRAWS):
            maybe = tuple(rng.randrange(1, MASK + 1) for _ in range(ACTIONS))
            if gf2_rank(maybe) == ACTIONS:
                hidden = maybe
                break
        if hidden is None:
            raise ValueError("world source could not produce full-rank intervention effects")
        self._signatures = dict(zip(self.action_ids, hidden))
        self._observation_rng = random.Random(seed ^ 0x94BAD5)
        self._goals = None
        self.real_probe_action_count = 0

    def _apply_action(self, output: int, action_id: str) -> int:
        if not isinstance(action_id, str) or action_id not in self._signatures:
            raise ValueError("invalid hidden-world action")
        return output ^ self._signatures[action_id]

    def probe_once_per_action(self) -> tuple[Observation, ...]:
        if self.real_probe_action_count:
            raise RuntimeError("world's original single-use intervention probes consumed")
        rows = []
        for action_id in self.action_ids:
            before = self._observation_rng.randrange(0, MASK + 1)
            nuisance_before = self._observation_rng.randrange(0, 1 << NUISANCE_BITS)
            after = self._apply_action(before, action_id)
            nuisance_after = self._observation_rng.randrange(0, 1 << NUISANCE_BITS)
            rows.append(Observation(action_id, before, after,
                                    nuisance_before, nuisance_after))
            self.real_probe_action_count += 1
        return tuple(rows)

    def heldout_goals(self) -> tuple[Goal, ...]:
        if self.real_probe_action_count != ACTIONS:
            raise RuntimeError("goal creation only AFTER five fixed interventions")
        if self._goals is None:
            rng = random.Random(self.seed ^ 0x940BEEF)
            goals = []
            sorted_actions = sorted(self.action_ids)
            # Create every 2- or 3-intervention combination, never an
            # already observed single-action probe, and conceal the actions
            # from candidate/control models.
            for size in (2, 3):
                for hidden_subset in combinations(sorted_actions, size):
                    start = rng.randrange(0, MASK + 1)
                    target = start
                    for action in hidden_subset:
                        target = self._apply_action(target, action)
                    goals.append(Goal(len(goals), start, target))
            if len(goals) != 20:
                raise AssertionError("frozen 5-action held-out goal count")
            self._goals = tuple(goals)
        return self._goals

    def execute(self, start: int, plan: tuple[str, ...] | None,
                *, max_actions: int = 3) -> int | None:
        if plan is None or not isinstance(plan, tuple):
            return None
        if len(plan) > max_actions or len(set(plan)) != len(plan):
            return None
        if any(action not in self._signatures for action in plan):
            return None
        output = start
        for action in plan:
            output = self._apply_action(output, action)
        return output

    def hidden_fingerprint(self) -> str:
        # An audit digest, never passed to learner/control predict().
        return sha256("WSP94/matrix/" + str(self.seed) + "/" +
                      "/".join(f"{k}:{v}" for k,v in sorted(self._signatures.items())))
