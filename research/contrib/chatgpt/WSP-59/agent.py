"""WSP59 source-blind numerical causal rule writer and grounded-goal planner.

Inputs are only charged public state/action/consequence observations and
nine labeled UTF-8 byte demonstrations. No evaluator import, hidden action
roles, pretrained network, gradient updates, next-token objective, source
simulator calls, or access to withheld tasks/goals. Strong stated structural
prior: 3 registers with fixed domains and <=2 causal parents per output.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha256
from itertools import combinations, product
import json

DOMAINS = (5, 2, 2)
STATES = tuple(product(*(range(n) for n in DOMAINS)))
CHANNELS = tuple(range(4))
PREDICATES = tuple((i, v) for i, n in enumerate(DOMAINS) for v in range(n))
MAX_PROBES = 40
MAX_DEMOS = 9
MAX_SNAPSHOT_BYTES = 200000
PARENT_SETS = tuple(p for size in (0, 1, 2)
                    for p in combinations(range(3), size))


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _valid_state(state):
    if (type(state) is not tuple or len(state) != 3 or
            any(type(v) is not int or v not in range(n)
                for v, n in zip(state, DOMAINS))):
        raise ValueError("invalid public physical state")
    return state


def pairwise_coverage_probes():
    """Source-blind max-coverage design of 10 unique state contexts."""
    observed = []
    for _ in range(10):
        before_keys = {
            (parents, tuple(s[k] for k in parents))
            for s in observed for parents in combinations(range(3), 2)
        }
        available = []
        for s in STATES:
            if s in observed:
                continue
            after_keys = {
                (parents, tuple(s[k] for k in parents))
                for parents in combinations(range(3), 2)
            }
            available.append((len(after_keys-before_keys), s))
        best = max(a for a, s in available)
        selected = min(s for a, s in available if a == best)
        observed.append(selected)
    for parents in combinations(range(3), 2):
        assert len({tuple(s[k] for k in parents) for s in observed}) == (
            DOMAINS[parents[0]] * DOMAINS[parents[1]])
    return tuple(observed)


class GroundedCausalAgent:
    gradient_updates = 0

    def __init__(self):
        self.rows = []
        self.demos = []
        self._rules = None
        self.last_expansions = 0

    def observe(self, before, action, after):
        _valid_state(before)
        _valid_state(after)
        if type(action) is not int or action not in CHANNELS:
            raise ValueError("invalid action")
        if len(self.rows) >= MAX_PROBES:
            raise ValueError("physical action budget exceeded")
        if (before, action) in {(b, a) for b, a, _ in self.rows}:
            raise ValueError("duplicate charged physical action")
        if sum(a == action for _, a, _ in self.rows) >= 10:
            raise ValueError("per-action budget exceeded")
        self.rows.append((before, action, after))
        self._rules = None

    def teach(self, raw_instruction, predicate):
        if (type(raw_instruction) is not bytes or len(raw_instruction) < 2 or
                len(raw_instruction) > 64 or b" & " in raw_instruction or
                type(predicate) is not tuple or predicate not in PREDICATES or
                len(self.demos) >= MAX_DEMOS):
            raise ValueError("bad grounded byte demonstration")
        if (raw_instruction in {raw for raw, _ in self.demos} or
                predicate in {goal for _, goal in self.demos}):
            raise ValueError("nonbijective grounded demonstration")
        self.demos.append((raw_instruction, predicate))

    @staticmethod
    def _candidate_rules(observations, register):
        """Choose smallest fully covered consistent causal-parent lookup."""
        candidates = []
        for parents in PARENT_SETS:
            mapping = {}
            consistent = True
            for before, after in observations:
                key = tuple(before[j] for j in parents)
                value = after[register]
                if key in mapping and mapping[key] != value:
                    consistent = False
                    break
                mapping[key] = value
            possible = 1
            for j in parents:
                possible *= DOMAINS[j]
            if consistent and len(mapping) == possible:
                candidates.append((parents, mapping))
        if not candidates:
            return ()
        min_size = min(len(parents) for parents, _ in candidates)
        return tuple((parents, mapping) for parents, mapping in candidates
                     if len(parents) == min_size)

    def _compile(self):
        if self._rules is not None:
            return
        rules = {}
        for action in CHANNELS:
            relevant = [(b, y) for b, a, y in self.rows if a == action]
            if not relevant:
                rules[action] = ((), (), ())
            else:
                rules[action] = tuple(
                    self._candidate_rules(relevant, register)
                    for register in range(3)
                )
        self._rules = rules

    def predict(self, before, action, memory_only=False):
        _valid_state(before)
        if type(action) is not int or action not in CHANNELS:
            raise ValueError("invalid physical action")
        if memory_only:
            for b, a, after in self.rows:
                if b == before and a == action:
                    return after
            return None
        self._compile()
        output = []
        for possibilities in self._rules[action]:
            if not possibilities:
                return None
            values = {
                mapping[tuple(before[k] for k in parents)]
                for parents, mapping in possibilities
            }
            if len(values) != 1:
                return None
            output.append(next(iter(values)))
        return tuple(output)

    def decode(self, instruction):
        if type(instruction) is not bytes or len(instruction) > 256:
            raise ValueError("invalid instruction byte stream")
        chunks = instruction.split(b" & ")
        if len(chunks) != 2:
            return None
        meanings = dict(self.demos)
        if chunks[0] not in meanings or chunks[1] not in meanings:
            return None
        left, right = meanings[chunks[0]], meanings[chunks[1]]
        if left[0] == right[0]:
            return None
        return (left, right)

    def plan(self, start, instruction, max_depth=4, memory_only=False):
        _valid_state(start)
        if type(max_depth) is not int or max_depth != 4:
            raise ValueError("frozen horizon is four")
        desired = self.decode(instruction)
        self.last_expansions = 0
        if desired is None:
            return None
        goal = lambda s: all(s[dim] == value for dim, value in desired)
        if goal(start):
            return ()
        queue = deque([(start, ())])
        seen = {start}
        while queue:
            state, path = queue.popleft()
            if len(path) >= max_depth:
                continue
            self.last_expansions += 1
            for action in CHANNELS:
                next_state = self.predict(state, action, memory_only=memory_only)
                if next_state is None:
                    continue
                new_path = path + (action,)
                if goal(next_state):
                    return new_path
                if next_state not in seen:
                    seen.add(next_state)
                    queue.append((next_state, new_path))
        return None

    def numeric_table_entries(self):
        self._compile()
        return sum(len(table) for action in CHANNELS
                   for options in self._rules[action]
                   for parents, table in options)

    def snapshot(self):
        payload = {
            "schema": "wsp59.grounded-causal-agent.v1",
            "observations": [[list(b), action, list(y)]
                             for b, action, y in self.rows],
            "demonstrations": [[raw.hex(), list(predicate)]
                               for raw, predicate in self.demos],
            "gradient_updates": self.gradient_updates
        }
        h = sha256(_canonical(payload).encode("ascii")).hexdigest()
        result = _canonical({"payload": payload, "sha256": h})
        if len(result.encode("ascii")) > MAX_SNAPSHOT_BYTES:
            raise OverflowError("snapshot beyond memory ceiling")
        return result

    @classmethod
    def restore(cls, raw):
        if type(raw) is not str or len(raw.encode("utf-8")) > MAX_SNAPSHOT_BYTES:
            raise ValueError("invalid memory snapshot")
        try:
            env = json.loads(raw)
            if type(env) is not dict or set(env) != {"payload", "sha256"}:
                raise ValueError("invalid memory envelope")
            p = env["payload"]
            if (type(p) is not dict or p.get("schema") !=
                    "wsp59.grounded-causal-agent.v1" or
                    p.get("gradient_updates") != 0 or
                    sha256(_canonical(p).encode("ascii")).hexdigest() != env["sha256"]):
                raise ValueError("invalid snapshot hash/schema")
            result = cls()
            for row in p["observations"]:
                if type(row) is not list or len(row) != 3:
                    raise ValueError("invalid stored experience")
                b, action, y = row
                result.observe(tuple(b), action, tuple(y))
            for item in p["demonstrations"]:
                if type(item) is not list or len(item) != 2:
                    raise ValueError("invalid stored symbol demonstration")
                symbol, predicate = item
                result.teach(bytes.fromhex(symbol), tuple(predicate))
            if result.snapshot() != raw:
                raise ValueError("noncanonical or inconsistent memory snapshot")
            return result
        except (TypeError, KeyError, IndexError, UnicodeError,
                json.JSONDecodeError, ValueError) as ex:
            raise ValueError("invalid/corrupted memory snapshot") from ex

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii")) * 8
