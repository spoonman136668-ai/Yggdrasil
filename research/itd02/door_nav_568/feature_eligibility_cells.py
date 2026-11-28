"""Bounded learned public-feature abstraction for native R7 eligibility cells.

Features are extracted solely from public bytes; their action values are learned
from action-owned consequences, not hardcoded navigation choices. Prototype only.
"""
import hashlib
from eligibility_local_cells import EligibilityLocalCells

class FeatureEligibilityCells(EligibilityLocalCells):
    def __init__(self, max_states=128, trace_limit=4, feature_bytes=2):
        super().__init__(max_states=max_states, trace_limit=trace_limit)
        if type(feature_bytes) is not int or not 1 <= feature_bytes <= 16:
            raise ValueError("FEATURE_BYTES_INVALID")
        self.feature_bytes = feature_bytes

    def _feature(self, public_frame):
        if not isinstance(public_frame, bytes):
            raise ValueError("PUBLIC_FRAME_REQUIRED")
        # Explicit lossy public observation projection; evaluate collisions.
        return public_frame[:self.feature_bytes]

    def observe(self, public_frame, legal_actions):
        return super().observe(self._feature(public_frame), legal_actions)
