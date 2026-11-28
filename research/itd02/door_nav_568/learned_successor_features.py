"""Bounded learned public action-consequence feature abstraction.

Chooses an observation-byte position by minimizing conflicting action-owned
successor labels. The successor label (first byte of the *public* next frame)
is an explicitly supplied synthetic outcome projection, not a learned world
model or privileged source. Unknown and tied predictions abstain.
"""
class LearnedSuccessorFeatures:
    def __init__(self, positions=2, capacity=128):
        if type(positions) is not int or not 1 <= positions <= 16:
            raise ValueError("FEATURE_POSITIONS_INVALID")
        if type(capacity) is not int or not 4 <= capacity <= 512:
            raise ValueError("HISTORY_CAP_INVALID")
        self.positions = positions
        self.capacity = capacity
        self.examples = []
        self.current = None
        self.selected_position = None
        self.buckets = {}

    def observe(self, public_frame, legal_actions):
        if not isinstance(public_frame, bytes) or len(public_frame) < self.positions:
            raise ValueError("PUBLIC_FRAME_REQUIRED")
        legal = tuple(legal_actions)
        if not legal or len(set(legal)) != len(legal) or any(type(a) is not int or a not in range(7) for a in legal):
            raise ValueError("LEGAL_ACTIONS_REQUIRED")
        self.current = (public_frame, legal)

    def learn(self, action, next_public_frame, reward, done):
        if self.current is None or action not in self.current[1]:
            raise ValueError("ACTION_OWNERSHIP_REQUIRED")
        if (not isinstance(next_public_frame, bytes) or not next_public_frame
                or type(reward) not in (int, float) or type(done) is not bool):
            raise ValueError("PUBLIC_CONSEQUENCE_REQUIRED")
        frame, _ = self.current
        self.examples.append((frame, action, next_public_frame[0]))
        self.examples = self.examples[-self.capacity:]

        def build(position):
            buckets = {}
            for public, act, label in self.examples:
                counts = buckets.setdefault((public[position], act), {})
                counts[label] = counts.get(label, 0) + 1
            return buckets

        def contradictions(groups):
            return sum(sum(counts.values()) - max(counts.values())
                       for counts in groups.values())

        self.selected_position = min(range(self.positions),
                                     key=lambda p: (contradictions(build(p)), p))
        self.buckets = build(self.selected_position)
        self.current = None

    def predict_successor_label(self, action):
        if self.current is None or action not in self.current[1]:
            raise ValueError("OBSERVE_AND_LEGAL_ACTION_REQUIRED")
        if self.selected_position is None:
            return None
        frame, _ = self.current
        counts = self.buckets.get((frame[self.selected_position], action))
        if not counts:
            return None
        highest = max(counts.values())
        winners = [label for label, count in counts.items() if count == highest]
        return winners[0] if len(winners) == 1 else None
