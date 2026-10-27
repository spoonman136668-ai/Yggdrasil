"""Independent conventional sliding-window tabular control."""
class SlidingTabularControl:
    def __init__(self, capacity=128):
        if type(capacity) is not int or not 1 <= capacity <= 512:
            raise ValueError("CAPACITY_INVALID")
        self.capacity = capacity
        self.table = {}
        self.examples = 0

    def observe(self, key, value):
        if (not isinstance(key, tuple) or len(key) != 2 or
                not isinstance(key[0], bytes) or
                not isinstance(key[1], int) or
                not isinstance(value, bytes) or not value):
            raise ValueError("ACTION_OWNED_PUBLIC_OBSERVATION_REQUIRED")
        if key not in self.table and len(self.table) >= self.capacity:
            raise ValueError("TABULAR_CAP_REACHED")
        old = self.table.get(key, ())
        self.table[key] = (old + (value,))[-2:]
        self.examples += 1

    def predict(self, key):
        recent = self.table.get(key, ())
        if len(recent) != 2 or recent[0] != recent[1]:
            return None
        return recent[0]

    def records(self):
        return sum(len(v) for v in self.table.values())
