"""Source-free experimental local-cell action consequence learner for #568.

Reuses the original R7 LocalCell. NOT a qualified native navigation model.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "native" / "itd01" / "r7"))
from native_cells import LocalCell

class LocalActionConsequences:
    def __init__(self):
        self.cells = [LocalCell() for _ in range(7)]
        self.counts = [0] * 7
        self.last = None

    def observe(self, public_frame, legal_actions):
        if not isinstance(public_frame, bytes):
            raise ValueError("PUBLIC_FRAME_ONLY")
        legal = tuple(legal_actions)
        if not legal or any(type(a) is not int or a not in range(7) for a in legal):
            raise ValueError("LEGAL_ACTIONS_ONLY")
        self.last = legal

    def choose(self):
        if self.last is None:
            raise ValueError("OBSERVE_FIRST")
        return max(self.last, key=lambda a: (self.cells[a].signal(True) / max(1, self.counts[a]), -a))

    def learn(self, action, next_public_frame, reward, done):
        if self.last is None or action not in self.last:
            raise ValueError("OWNED_ACTION_REQUIRED")
        if not isinstance(next_public_frame, bytes) or type(reward) not in (int, float) or type(done) is not bool:
            raise ValueError("PUBLIC_CONSEQUENCE_ONLY")
        self.cells[action].feel(True, reward > 0)
        self.counts[action] += 1
        self.last = None
