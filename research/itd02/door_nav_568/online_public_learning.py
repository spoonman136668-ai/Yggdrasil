"""Online owned-action public transition learning alongside native memory selection.

The selector performs its existing probe selection using frozen models for
that session. Afterwards this separate plastic map incorporates all observed
public action consequences, including surprising first hops and confirmed
second hops. Only two matching public observations are sufficient to change a
previous prediction; conflicting observations remain visible. This map is
not silently substituted into the archive or used as an oracle. Bounded
counts and measured update cost are explicit.
"""
from native_public_loop import NativePublicLoop

class PublicOnlineTransitions:
    def __init__(self, original, capacity=128):
        if not 1 <= capacity <= 512:
            raise ValueError("CAPACITY_REQUIRED")
        self.links = dict(original)
        self.capacity = capacity
        self.observations = {}
        self.changes = 0

    def observe(self, key, public_result):
        if not isinstance(key[0], bytes) or not isinstance(public_result, bytes):
            raise ValueError("PUBLIC_BYTES_ONLY")
        if key not in self.observations and len(self.observations) >= self.capacity:
            raise ValueError("ONLINE_CAPACITY_REACHED")
        counts = self.observations.setdefault(key, {})
        counts[public_result] = counts.get(public_result, 0) + 1
        ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
        winner, count = ranked[0]
        if count >= 2 and (len(ranked) == 1 or count > ranked[1][1]):
            if self.links.get(key) != winner:
                self.links[key] = winner
                self.changes += 1

    def examples(self):
        return sum(sum(values.values()) for values in self.observations.values())

class LearningPublicLoop(NativePublicLoop):
    def __init__(self, capacity=128):
        super().__init__()
        self.learned = PublicOnlineTransitions(self.model.active_links, capacity)
        self.interactions = 0

    def episode(self, world, budget=6, recheck=False):
        result = super().episode(world, budget=budget, recheck=recheck)
        for event in result["trace"]:
            _, key, observed = event[:3]
            self.learned.observe(key, observed)
            self.interactions += 1
        result["online_changes"] = self.learned.changes
        result["online_examples"] = self.learned.examples()
        result["online_records"] = len(self.learned.links)
        return result
