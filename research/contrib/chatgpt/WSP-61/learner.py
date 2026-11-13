"""WSP61 source-blind no-reset finite-state causal hypothesis learner.

This learner knows neither the hidden source family nor which shuffled
action affects which state variable. It receives only chronological charged
state-action-consequence observations. Candidate causal parent subsets are
enumerated over public sensor bits; UNKNOWN outcomes force abstention.
No source module import, gradient descent or next-token objective.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha256
from itertools import combinations, product
import json

INITIAL = (0, 0, 0, 0)
ACTIONS = tuple(range(4))
MAX_ACTIONS = 80
MAX_PARENT_ARITY = 3
MAX_SNAPSHOT_BYTES = 300000


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _state(x):
    if (type(x) is not tuple or len(x) != 4 or
            any(type(v) is not int or v not in (0, 1) for v in x)):
        raise ValueError("invalid 4-bit public sensor state")
    return x


class ReachableCausalLearner:
    gradient_updates = 0

    def __init__(self):
        self.ledger = []
        self.state = INITIAL
        self.state_visits = {INITIAL: 1}
        self._compiled = {}
        self.last_expansions = 0

    def observe(self, experience):
        before = _state(experience.before)
        after = _state(experience.after)
        action = experience.action
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("invalid physical action channel")
        if (type(experience.action_cost) is not int or
                experience.action_cost != 1):
            raise ValueError("incorrect action charge")
        if len(self.ledger) >= MAX_ACTIONS:
            raise ValueError("action budget exceeded")
        if before != self.state:
            raise ValueError("illegal teleport/reset in sequential causal ledger")
        self.ledger.append((before, action, after))
        self.state = after
        self.state_visits[after] = self.state_visits.get(after, 0) + 1
        self._compiled.clear()

    @staticmethod
    def _make_hypotheses(rows, output_bit):
        # Retain all evidence-consistent partial truth tables with <=3 parents.
        # Unknown table contexts are not imputed, including for larger models.
        hypotheses = []
        for arity in range(MAX_PARENT_ARITY + 1):
            for parents in combinations(range(4), arity):
                table = {}
                consistent = True
                for before, after in rows:
                    key = tuple(before[i] for i in parents)
                    value = after[output_bit]
                    prior = table.get(key)
                    if prior is not None and prior != value:
                        consistent = False
                        break
                    table[key] = value
                if consistent:
                    hypotheses.append((parents, table))
        return tuple(hypotheses)

    def _hypotheses(self, action):
        if action not in self._compiled:
            rows = [(b, after) for b, a, after in self.ledger if a == action]
            if not rows:
                self._compiled[action] = None
            else:
                self._compiled[action] = tuple(
                    self._make_hypotheses(rows, bit) for bit in range(4))
        return self._compiled[action]

    def predict(self, before, action, memory_only=False):
        before = _state(before)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("bad action channel")
        if memory_only:
            outputs = {after for b, a, after in self.ledger
                       if b == before and a == action}
            return next(iter(outputs)) if len(outputs) == 1 else None
        hypotheses = self._hypotheses(action)
        if hypotheses is None:
            return None
        after = []
        for choices in hypotheses:
            if not choices:
                return None
            values = set()
            for parents, table in choices:
                key = tuple(before[i] for i in parents)
                if key not in table:
                    return None
                values.add(table[key])
                if len(values) > 1:
                    return None
            after.append(next(iter(values)))
        return tuple(after)

    def select_action(self):
        """Online curiosity selection at the *current reachable state only*.

        Never asks the source to simulate alternatives. Prefers unmeasured
        current-state actions, known transitions to previously unvisited
        states, and balanced coverage of action channels; tie deterministic.
        """
        now = self.state
        seen = {(b, a) for b, a, y in self.ledger}
        by_action = {a: sum(action == a for _, action, _ in self.ledger)
                     for a in ACTIONS}
        scores = []
        for action in ACTIONS:
            novel_pair = int((now, action) not in seen)
            predicted = self.predict(now, action)
            novel_state = int(predicted is not None and
                              predicted not in self.state_visits)
            uncertainty = int(predicted is None)
            scores.append((novel_state * 8 + novel_pair * 4 +
                           uncertainty * 2 - by_action[action] / 1000,
                           -action, action))
        return max(scores)[2]

    def plan(self, start, target, horizon=6, memory_only=False):
        start = _state(start)
        target = _state(target)
        if type(horizon) is not int or horizon != 6:
            raise ValueError("frozen planning horizon")
        self.last_expansions = 0
        if start == target:
            return ()
        q = deque([(start, ())])
        visited = {start}
        while q:
            before, path = q.popleft()
            if len(path) >= horizon:
                continue
            self.last_expansions += 1
            for action in ACTIONS:
                after = self.predict(before, action, memory_only=memory_only)
                if after is None:
                    continue
                next_path = path + (action,)
                if after == target:
                    return next_path
                if after not in visited:
                    visited.add(after)
                    q.append((after, next_path))
        return None

    def hypothesis_counts(self):
        return tuple(
            tuple(len(h) for h in self._hypotheses(action))
            if self._hypotheses(action) is not None else (0, 0, 0, 0)
            for action in ACTIONS)

    def numeric_entry_count(self):
        return sum(
            len(table)
            for action in ACTIONS
            for options in (self._hypotheses(action) or ())
            for _, table in options
        )

    def snapshot(self):
        payload = {
            "schema": "wsp61.no-reset-learner.v1",
            "ledger": [[list(b), a, list(y)] for b, a, y in self.ledger],
            "gradient_updates": self.gradient_updates
        }
        h = sha256(_canon(payload).encode("ascii")).hexdigest()
        text = _canon({"payload": payload, "sha256": h})
        if len(text.encode("ascii")) > MAX_SNAPSHOT_BYTES:
            raise OverflowError("snapshot budget exceeded")
        return text

    @classmethod
    def restore(cls, raw):
        if type(raw) is not str or len(raw.encode("utf-8")) > MAX_SNAPSHOT_BYTES:
            raise ValueError("invalid snapshot size")
        try:
            env = json.loads(raw)
            if type(env) is not dict or set(env) != {"payload", "sha256"}:
                raise ValueError("invalid snapshot envelope")
            payload = env["payload"]
            if (type(payload) is not dict or
                    payload.get("schema") != "wsp61.no-reset-learner.v1" or
                    payload.get("gradient_updates") != 0 or
                    sha256(_canon(payload).encode("ascii")).hexdigest()
                    != env["sha256"]):
                raise ValueError("invalid memory schema/hash")
            rows = payload["ledger"]
            if type(rows) is not list or len(rows) > MAX_ACTIONS:
                raise ValueError("invalid ledger rows")
            learner = cls()
            for row in rows:
                if type(row) is not list or len(row) != 3:
                    raise ValueError("invalid stored observation")
                b, action, y = row
                class PublicExperience:
                    pass
                v = PublicExperience()
                v.before, v.action, v.after, v.action_cost = (
                    tuple(b), action, tuple(y), 1)
                learner.observe(v)
            if learner.snapshot() != raw:
                raise ValueError("noncanonical or inconsistent snapshot")
            return learner
        except (ValueError, TypeError, KeyError, IndexError, UnicodeError,
                json.JSONDecodeError) as ex:
            raise ValueError("malformed/modified snapshot") from ex

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii")) * 8
