"""Source-free seven-action public consequence learner prototype for issue 568.

No original MiniGrid execution. Not an admitted native intelligence result.
"""
import hashlib
import json

ACTIONS = tuple(range(7))

class PublicActionMemory:
    def __init__(self):
        self.counts = {}
        self.last = None

    def observe(self, public_frame, legal_actions, time):
        if not isinstance(public_frame, (bytes, bytearray)):
            raise ValueError("PUBLIC_FRAME_REQUIRED")
        legal = tuple(legal_actions)
        if not legal or any(type(a) is not int or a not in ACTIONS for a in legal):
            raise ValueError("INVALID_LEGAL_ACTIONS")
        if type(time) is not int or time < 0:
            raise ValueError("INVALID_TIME")
        self.last = (hashlib.sha256(public_frame).hexdigest(), legal)

    def choose(self):
        if self.last is None:
            raise ValueError("OBSERVE_FIRST")
        key, legal = self.last
        return max(legal, key=lambda a: (self._value(key, a), -a))

    def _value(self, key, action):
        wins, n = self.counts.get(key + ":" + str(action), (0, 0))
        return (wins + 1) / (n + 2)

    def learn(self, chosen_action, next_public_frame, reward, done):
        if self.last is None or chosen_action not in self.last[1]:
            raise ValueError("ACTION_OWNERSHIP_REQUIRED")
        if not isinstance(next_public_frame, (bytes, bytearray)):
            raise ValueError("NEXT_PUBLIC_FRAME_REQUIRED")
        if type(reward) not in (int, float) or type(done) is not bool:
            raise ValueError("RETURNED_CONSEQUENCE_REQUIRED")
        key = self.last[0] + ":" + str(chosen_action)
        wins, n = self.counts.get(key, (0, 0))
        self.counts[key] = (wins + int(reward > 0), n + 1)
        self.last = None

    def checkpoint(self):
        body = json.dumps(self.counts, sort_keys=True, separators=(",", ":")).encode()
        if len(body) > 32768:
            raise ValueError("STATE_CAP")
        return body

    @classmethod
    def restore(cls, data):
        if not isinstance(data, bytes) or len(data) > 32768:
            raise ValueError("CHECKPOINT_INVALID")
        obj = cls()
        obj.counts = {k: tuple(v) for k, v in json.loads(data).items()}
        if obj.checkpoint() != data:
            raise ValueError("NONCANONICAL_CHECKPOINT")
        return obj
