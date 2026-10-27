"""Conflict-triggered local refinement of shared public feature cells.

Starts with a shared feature prefix; on contradictory rewarded actions for
distinct public frames, isolates the conflicting observations. Source-free
experimental candidate, not a general causal representation.
"""
from feature_eligibility_cells import FeatureEligibilityCells

class AdaptiveFeatureCells(FeatureEligibilityCells):
    def __init__(self, max_states=128, trace_limit=4, feature_bytes=2):
        super().__init__(max_states, trace_limit, feature_bytes)
        self.exemplars = {}
        self.split = set()
        self.pending_frame = None

    def _feature(self, public_frame):
        prefix = super()._feature(public_frame)
        if prefix in self.split:
            return b"exact:" + public_frame
        return b"shared:" + prefix

    def observe(self, public_frame, legal_actions):
        if not isinstance(public_frame, bytes):
            raise ValueError("PUBLIC_FRAME_REQUIRED")
        self.pending_frame = public_frame
        return super().observe(public_frame, legal_actions)

    def learn(self, chosen_action, next_public_frame, reward, done):
        if self.current is None or chosen_action not in self.current[1]:
            raise ValueError("OWNED_ACTION_REQUIRED")
        if not isinstance(next_public_frame, bytes) or type(reward) not in (int, float) or type(done) is not bool:
            raise ValueError("PUBLIC_CONSEQUENCE_REQUIRED")
        frame = self.pending_frame
        prefix = frame[:self.feature_bytes]
        if reward > 0:
            prior = self.exemplars.get(prefix)
            if prior is not None and prior[0] != frame and prior[1] != chosen_action:
                self.split.add(prefix)
            else:
                self.exemplars[prefix] = (frame, chosen_action)
        super().learn(chosen_action, next_public_frame, reward, done)
        self.pending_frame = None
