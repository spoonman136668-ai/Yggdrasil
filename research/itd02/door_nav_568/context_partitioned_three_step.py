"""Two-compartment public context memory, preserving old learned behavior.

At an explicit FIT boundary a bounded snapshot preserves the prior learner
and the *observed* first-byte context set. The active learner remains plastic.
Public observations matching previous contexts are routed to the snapshot for
decision-making, while previously unseen contexts use active learning. This
is a predeclared byte-context partition, not self-discovered causal identity.
No original DoorKey evidence or privileged regime labels.
"""
from copy import deepcopy
from three_step_feature_cells import ThreeStepFeatureCells

class ContextPartitionedThreeStep:
    def __init__(self, positions=2, capacity=128):
        self.active = ThreeStepFeatureCells(positions, capacity)
        self.snapshot = None
        self.prior_contexts = frozenset()
        self.current = None
        self.positions = positions
        self.capacity = capacity

    def freeze_boundary(self):
        if self.snapshot is not None:
            raise ValueError("ONE_SNAPSHOT_CAP")
        if not self.active.model.examples:
            raise ValueError("NO_PRIOR_FIT")
        self.snapshot = deepcopy(self.active)
        self.prior_contexts = frozenset(frame[0] for frame, _, _ in
                                        self.active.model.examples)
        self.current = None

    def observe(self, frame, legal):
        self.active.observe(frame, legal)
        if self.snapshot is not None:
            self.snapshot.observe(frame, legal)
        self.current = (frame, tuple(legal))

    def learn(self, action, next_frame, reward, done):
        if self.current is None:
            raise ValueError("OBSERVE_FIRST")
        self.active.learn(action, next_frame, reward, done)
        self.current = None

    def choose(self, horizon=3):
        if self.current is None:
            raise ValueError("OBSERVE_FIRST")
        frame, _ = self.current
        prior = (self.snapshot is not None and frame[0] in self.prior_contexts)
        candidate = self.snapshot if prior else self.active
        return candidate.choose(horizon)

    def stored_examples(self):
        return len(self.active.model.examples) + (
            len(self.snapshot.model.examples) if self.snapshot else 0)
