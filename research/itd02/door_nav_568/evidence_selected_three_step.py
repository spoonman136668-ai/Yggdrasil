"""Action-consequence-evidence selector for active versus archived native cells.

No hard-coded public context partition: two distinct, action-owned public
transition observations must favor one candidate over another. Unknown,
ambiguous, or duplicate probes abstain. The archival compartment is immutable
during probes. A selection is local to its explicitly observed probe window;
it is not proof of zero-shot regime recognition.
"""
from context_partitioned_three_step import ContextPartitionedThreeStep

class EvidenceSelectedThreeStep(ContextPartitionedThreeStep):
    def __init__(self, positions=2, capacity=128, probe_limit=4):
        super().__init__(positions, capacity)
        if type(probe_limit) is not int or not 2 <= probe_limit <= 8:
            raise ValueError("PROBE_LIMIT_INVALID")
        self.probe_limit = probe_limit
        self.probing = False
        self.evidence = []
        self.selected = None

    def begin_probe(self):
        if self.snapshot is None or self.current is not None:
            raise ValueError("FREEZE_AND_COMPLETE_ACTION_FIRST")
        self.probing = True
        self.evidence = []
        self.selected = None

    def learn(self, action, next_frame, reward, done):
        if self.current is None:
            raise ValueError("OBSERVE_FIRST")
        frame, legal = self.current
        if action not in legal or not isinstance(next_frame, bytes) or not next_frame:
            raise ValueError("PUBLIC_ACTION_CONSEQUENCE_REQUIRED")
        if self.probing:
            if len(self.evidence) >= self.probe_limit:
                raise ValueError("PROBE_CAP_REACHED")
            observed = next_frame[0]
            predictions = []
            for candidate in (self.active, self.snapshot):
                predictions.append(candidate.model.predict_successor_label(action))
            self.evidence.append((frame, action, observed, tuple(predictions)))
        super().learn(action, next_frame, reward, done)

    def resolve_probe(self):
        if not self.probing:
            return False
        self.probing = False
        samples = tuple(self.evidence)
        self.evidence = []
        if (len(samples) < 2 or
                len({(frame, action) for frame, action, _, _ in samples}) != len(samples)):
            return False
        # Only admit a unique candidate matching all observed consequences.
        # Competing unknown predictions are not counted as observed errors.
        scores = [sum(predictions[i] == observed
                      for _, _, observed, predictions in samples) for i in (0, 1)]
        if scores[0] == scores[1] or max(scores) != len(samples):
            return False
        self.selected = ("active", "snapshot")[0 if scores[0] > scores[1] else 1]
        return True

    def choose(self, horizon=3):
        if self.current is None:
            raise ValueError("OBSERVE_FIRST")
        if self.probing or self.selected is None:
            return None
        candidate = self.active if self.selected == "active" else self.snapshot
        return candidate.choose(horizon)
