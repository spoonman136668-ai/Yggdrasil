"""Experimental feedback-selected public-byte feature learner.

Candidate features are single public byte positions. The selected position is
learned from rewarded, action-owned observations, not supplied as a fixed prefix.
Finite training data can confound positions; held-out controls are required.
"""
from native_cells_r7 import LocalCell

class LearnedByteCells:
    def __init__(self, feature_positions=8, max_groups=128):
        if type(feature_positions) is not int or not 1 <= feature_positions <= 16:
            raise ValueError("FEATURE_POSITION_CAP")
        if type(max_groups) is not int or not 1 <= max_groups <= 128:
            raise ValueError("GROUP_CAP")
        self.positions = feature_positions
        self.max_groups = max_groups
        self.examples = []
        self.current = None
        self.feature_position = None
        self.cells = {}

    def observe(self, public_frame, legal_actions):
        if not isinstance(public_frame, bytes) or len(public_frame) < self.positions:
            raise ValueError("BOUNDED_PUBLIC_BYTES_REQUIRED")
        legal = tuple(legal_actions)
        if not legal or len(set(legal)) != len(legal) or any(type(a) is not int or a not in range(7) for a in legal):
            raise ValueError("LEGAL_ACTIONS_REQUIRED")
        self.current = (public_frame, legal)

    def learn(self, action, next_public_frame, reward, done):
        if self.current is None or action not in self.current[1]:
            raise ValueError("OWNED_ACTION_REQUIRED")
        if not isinstance(next_public_frame, bytes) or type(reward) not in (int, float) or type(done) is not bool:
            raise ValueError("PUBLIC_CONSEQUENCE_REQUIRED")
        frame, _ = self.current
        self.examples.append((frame, action, int(reward > 0)))
        # Choose the smallest public-byte position whose conditional
        # (byte value, action) buckets have least contradictory feedback.
        def contradictions(pos):
            buckets = {}
            for f, a, positive in self.examples:
                pair = (f[pos], a)
                zero, one = buckets.get(pair, (0, 0))
                buckets[pair] = (zero + (not positive), one + positive)
            return sum(min(zero, one) for zero, one in buckets.values())
        self.feature_position = min(range(self.positions), key=lambda p: (contradictions(p), p))
        self.cells = {}
        for f, a, positive in self.examples:
            group = f[self.feature_position]
            if group not in self.cells:
                if len(self.cells) >= self.max_groups:
                    raise ValueError("GROUP_CAP_REACHED")
                self.cells[group] = [LocalCell() for _ in range(7)]
            self.cells[group][a].feel(True, bool(positive))
        self.current = None

    def choose(self):
        if self.current is None:
            raise ValueError("OBSERVE_FIRST")
        frame, legal = self.current
        if self.feature_position is None:
            return min(legal)
        cells = self.cells.get(frame[self.feature_position])
        if cells is None:
            return min(legal)
        return max(legal, key=lambda a: (cells[a].signal(True), -a))
