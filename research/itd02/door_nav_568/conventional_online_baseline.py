"""Conventional bounded tabular online transition learner, no native cells.

For each public (frame, action), count observed successor states. Predict
unique modal successor only after two concordant observations; tied or
insufficient evidence abstains. This is an independent conventional online
baseline with explicit storage and update accounting.
"""
class TabularOnlineBaseline:
    def __init__(self, capacity=128, min_support=2):
        if type(capacity) is not int or capacity < 1 or capacity > 512:
            raise ValueError("INVALID_CAPACITY")
        if type(min_support) is not int or min_support < 1:
            raise ValueError("INVALID_SUPPORT")
        self.capacity = capacity
        self.min_support = min_support
        self.counts = {}
        self.examples = 0

    def observe(self, key, successor):
        if (not isinstance(key, tuple) or len(key) != 2 or
                not isinstance(key[0], bytes) or not isinstance(successor, bytes)):
            raise ValueError("PUBLIC_TRANSITION_REQUIRED")
        if key not in self.counts and len(self.counts) >= self.capacity:
            raise ValueError("CAPACITY_EXCEEDED")
        bucket = self.counts.setdefault(key, {})
        bucket[successor] = bucket.get(successor, 0) + 1
        self.examples += 1

    def predict(self, key):
        bucket = self.counts.get(key, {})
        if not bucket:
            return None
        winning = max(bucket.values())
        tied = [successor for successor, count in bucket.items()
                if count == winning]
        if len(tied) != 1 or winning < self.min_support:
            return None
        return tied[0]

    def records(self):
        return sum(len(bucket) for bucket in self.counts.values())
