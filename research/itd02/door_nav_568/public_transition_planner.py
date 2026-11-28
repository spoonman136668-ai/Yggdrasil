"""Source-free public transition memory: no original DoorKey interaction.

Tabular observed-action transition counts with finite-horizon planning.
This is a conventional reference mechanism, NOT demonstrated native cognition.
"""
import hashlib
import json
import math

class PublicTransitionPlanner:
    ACTIONS = tuple(range(7))
    def __init__(self, capacity=256):
        if type(capacity) is not int or capacity < 1 or capacity > 256:
            raise ValueError("INVALID_CAPACITY")
        self.capacity = capacity
        self.edges = {}
        self.current = None

    @staticmethod
    def state(frame):
        if not isinstance(frame, (bytes, bytearray)):
            raise ValueError("PUBLIC_BYTES_REQUIRED")
        return hashlib.sha256(frame).hexdigest()

    def observe(self, frame, legal_actions):
        legal = tuple(legal_actions)
        if not legal or len(set(legal)) != len(legal) or any(type(a) is not int or a not in self.ACTIONS for a in legal):
            raise ValueError("LEGAL_ACTIONS_REQUIRED")
        self.current = (self.state(frame), legal)

    def learn(self, chosen_action, next_frame, reward, done):
        if self.current is None or chosen_action not in self.current[1]:
            raise ValueError("OWNED_LEGAL_ACTION_REQUIRED")
        if type(reward) not in (float, int) or not math.isfinite(reward) or type(done) is not bool:
            raise ValueError("PUBLIC_REWARD_DONE_REQUIRED")
        next_state = self.state(next_frame)
        state, _ = self.current
        key = state + ":" + str(chosen_action)
        if key not in self.edges and len(self.edges) >= self.capacity:
            raise ValueError("MEMORY_CAP_REACHED")
        bucket = self.edges.setdefault(key, {})
        target = next_state + (":T" if done else ":N")
        n, total = bucket.get(target, [0, 0.0])
        bucket[target] = [n + 1, total + float(reward)]
        self.current = None

    def choose(self, horizon=3):
        if self.current is None or type(horizon) is not int or not 1 <= horizon <= 8:
            raise ValueError("OBSERVE_AND_BOUNDED_HORIZON_REQUIRED")
        state, legal = self.current
        memo = {}
        def value(s, depth):
            if depth == 0:
                return 0.0
            key = (s, depth)
            if key in memo:
                return memo[key]
            best = 0.0
            for action in self.ACTIONS:
                bucket = self.edges.get(s + ":" + str(action), {})
                n = sum(v[0] for v in bucket.values())
                if n:
                    expected = sum((count / n) * (total / count + (0 if target.endswith(":T") else 0.9 * value(target[:-2], depth - 1))) for target, (count, total) in bucket.items())
                    best = max(best, expected)
            memo[key] = best
            return best
        def score(a):
            bucket = self.edges.get(state + ":" + str(a), {})
            n = sum(v[0] for v in bucket.values())
            if not n:
                return 0.0
            return sum((count / n) * (total / count + (0 if target.endswith(":T") else 0.9 * value(target[:-2], horizon - 1))) for target, (count, total) in bucket.items())
        return max(legal, key=lambda a: (score(a), -a))

    def checkpoint(self):
        payload = {"schema": "public-transition-v0", "capacity": self.capacity, "edges": self.edges}
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        if len(raw) > 131072:
            raise ValueError("CHECKPOINT_CAP")
        return raw

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not 0 < len(raw) <= 131072:
            raise ValueError("INVALID_CHECKPOINT")
        payload = json.loads(raw)
        if set(payload) != {"schema", "capacity", "edges"} or payload["schema"] != "public-transition-v0":
            raise ValueError("INVALID_SCHEMA")
        obj = cls(payload["capacity"])
        obj.edges = payload["edges"]
        if len(obj.edges) > obj.capacity or obj.checkpoint() != raw:
            raise ValueError("NONCANONICAL_OR_OVER_CAP")
        return obj
