"""WSP59 evaluator-only grounded planning worlds.

The learner MUST NOT import this file or receive its hidden action roles,
permutations, affordances, goal predicates, shortest paths, or heldout outcomes.
SELFTEST is the sole cohort. This is a finite, heavily structured simulator,
not a natural-world or general-language evaluation.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
from random import Random
import json

SEEDS = tuple(range(2501, 2509))
DOMAIN = (5, 2, 2)
STATES = tuple(product(*(range(n) for n in DOMAIN)))
CHANNELS = tuple(range(4))
PREDICATES = tuple((i, x) for i, n in enumerate(DOMAIN) for x in range(n))
TASKS_PER_WORLD = 32


def _rng(seed, tag):
    key = sha256(f"WSP59|SELFTEST|{seed}|{tag}".encode("ascii")).digest()
    return Random(int.from_bytes(key, "big"))


def _nonaffine(p):
    return all(any(p[x] != (a*x+b) % 5 for x in range(5))
               for a in range(5) for b in range(5))


def _hidden_physics(seed):
    r = _rng(seed, "physics")
    maps = []
    for _ in range(10000):
        a = list(range(5))
        r.shuffle(a)
        t = tuple(a)
        if t not in maps and _nonaffine(t):
            maps.append(t)
            if len(maps) == 2:
                break
    if len(maps) != 2:
        raise RuntimeError("cannot sample disjoint nonlinear mechanisms")
    subsets = []
    for _ in range(10000):
        subset = frozenset(x for x in range(5) if r.randrange(2))
        if 1 < len(subset) < 5 and subset not in subsets:
            subsets.append(subset)
            if len(subsets) == 2:
                break
    if len(subsets) != 2:
        raise RuntimeError("cannot sample independent switches")
    roles = list(range(4))
    r.shuffle(roles)
    return (tuple(maps), tuple(subsets), tuple(roles))


@dataclass(frozen=True)
class Demo:
    raw_instruction: bytes
    grounded_predicate: tuple[int, int]


@dataclass(frozen=True)
class Task:
    before: tuple[int, int, int]
    raw_instruction: bytes
    _goal: tuple[tuple[int, int], tuple[int, int]]
    _shortest: int


@dataclass(frozen=True)
class World:
    seed: int
    _maps: tuple[tuple[int, ...], tuple[int, ...]]
    _subsets: tuple[frozenset, frozenset]
    _channel_roles: tuple[int, int, int, int]
    _lexicon: tuple[bytes, ...]

    def step(self, before, action):
        if (type(before) is not tuple or len(before) != 3 or
                before not in STATES or type(action) is not int or
                action not in CHANNELS):
            raise ValueError("invalid state or charged physical action")
        p, g, m = before
        role = self._channel_roles[action]
        if role == 0 and g == 1:
            p = self._maps[0][p]
        elif role == 1:
            g ^= int(p in self._subsets[0])
        elif role == 2:
            m ^= int(p in self._subsets[1])
        elif role == 3 and m == 1:
            p = self._maps[1][p]
        return (p, g, m)

    def demonstrations(self):
        return tuple(Demo(self._lexicon[n], pred)
                     for n, pred in enumerate(PREDICATES))

    def _shortest_to(self, state, goals, limit=4):
        def good(s):
            return all(s[i] == v for i, v in goals)
        if good(state):
            return 0
        queue = deque([(state, 0)])
        seen = {state}
        while queue:
            before, dist = queue.popleft()
            if dist >= limit:
                continue
            for action in CHANNELS:
                after = self.step(before, action)
                if good(after):
                    return dist + 1
                if after not in seen:
                    seen.add(after)
                    queue.append((after, dist+1))
        return None

    def tasks(self):
        r = _rng(self.seed, "heldout-task-creation")
        # Construct a large balanced candidate set without consulting the
        # learner; select only goals with source-reachable shortest path 2..4.
        candidates = []
        for s in STATES:
            for first, second in combinations(range(3), 2):
                for v in range(DOMAIN[first]):
                    for w in range(DOMAIN[second]):
                        goals = ((first, v), (second, w))
                        distance = self._shortest_to(s, goals)
                        if distance is None or not 2 <= distance <= 4:
                            continue
                        raw = (self._lexicon[PREDICATES.index(goals[0])] + b" & " +
                               self._lexicon[PREDICATES.index(goals[1])])
                        candidates.append(Task(s, raw, goals, distance))
        if len(candidates) < TASKS_PER_WORLD:
            raise RuntimeError("insufficient reachable multistep tasks")
        r.shuffle(candidates)
        # All heldout instructions are conjunctions unseen during grounding.
        selected = tuple(candidates[:TASKS_PER_WORLD])
        assert all(t._shortest in (2, 3, 4) and
                   len(t.raw_instruction.split(b" & ")) == 2 for t in selected)
        return selected

    def evaluate(self, task, actions):
        if type(actions) not in (tuple, list) or len(actions) > 4:
            return False
        state = task.before
        for action in actions:
            state = self.step(state, action)
        return all(state[i] == v for i, v in task._goal)

    def receipt(self):
        hidden = {
            "seed": self.seed, "roles": self._channel_roles,
            "maps": self._maps, "subsets": [sorted(x) for x in self._subsets],
            "lexicon_hex": [x.hex() for x in self._lexicon]
        }
        tasks = self.tasks()
        heldout = [
            [list(t.before), t.raw_instruction.hex(),
             [list(pred) for pred in t._goal], t._shortest]
            for t in tasks
        ]
        def digest(obj):
            return sha256(json.dumps(obj, sort_keys=True,
                                     separators=(",", ":")).encode("ascii")).hexdigest()
        return {
            "schema": "wsp59.world-receipt.v1", "seed": self.seed,
            "hidden_source_sha256": digest(hidden),
            "heldout_task_sha256": digest(heldout),
            "demonstrations": len(self.demonstrations()),
            "heldout_tasks": len(tasks),
            "total_possible_physical_actions": 80,
            "model_probe_budget": 40
        }


def build_world(seed, cohort="SELFTEST"):
    if cohort != "SELFTEST" or type(seed) is not int or seed not in SEEDS:
        raise PermissionError("WSP59 new world source is SELFTEST only")
    maps, subsets, roles = _hidden_physics(seed)
    r = _rng(seed, "grounded-lexicon")
    # The format contract is a byte-encoded nonce phrase, not open language.
    names = [f"n{idx:02x}".encode("ascii") for idx in range(128)]
    r.shuffle(names)
    world = World(seed, maps, subsets, roles, tuple(names[:len(PREDICATES)]))
    assert len(set(world._lexicon)) == len(PREDICATES) == 9
    assert len(set(roles)) == 4
    assert all(_nonaffine(p) for p in maps)
    assert len(world.tasks()) == TASKS_PER_WORLD
    return world
