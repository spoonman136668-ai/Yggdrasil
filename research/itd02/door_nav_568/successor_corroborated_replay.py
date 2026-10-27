"""Independent PUBLIC successor consistency guard for replay decisions.

The successor map is learned from the same action-owned public observations as
rewards, not supplied from hidden environment state or a goal oracle. This
prototype requires a distinct public successor signal; when successors are
unchanged across regimes, it refuses to claim corroboration.
"""
from evidence_gated_replay import EvidenceGatedReplay

class SuccessorCorroboratedReplay:
    def __init__(self):
        self.learner = EvidenceGatedReplay(feature_positions=2, max_examples=8)
        self.current_successors = {}
        self.archived_successors = {}
        self.probe_successors = []
        self.recording_probe = False

    def observe(self, frame, actions):
        self.learner.observe(frame, actions)

    def choose(self):
        return self.learner.choose()

    def learn(self, action, next_frame, reward, done):
        if self.learner.active.current is None:
            raise ValueError("OBSERVE_FIRST")
        frame, legal = self.learner.active.current
        if action not in legal or not isinstance(next_frame, bytes):
            raise ValueError("OWNED_PUBLIC_TRANSITION_REQUIRED")
        if self.recording_probe:
            self.probe_successors.append(((frame, action), next_frame))
        else:
            self.current_successors[(frame, action)] = next_frame
        self.learner.learn(action, next_frame, reward, done)

    def archive(self):
        self.learner.archive()
        self.archived_successors = dict(self.current_successors)
        self.current_successors = {}

    def start_probe(self):
        self.probe_successors = []
        self.recording_probe = True
        self.learner.start_probe()

    def restore_with_corrob(self):
        if not self.recording_probe:
            return False
        # The independent successor channel must match archived transitions
        # for each distinct public action, and contradict the current regime
        # for at least one such action. Unknown transitions are not evidence.
        unique = dict(self.probe_successors)
        enough = len(unique) == len(self.probe_successors) >= 2
        matches_archive = enough and all(
            key in self.archived_successors and self.archived_successors[key] == nxt
            for key, nxt in unique.items()
        )
        discriminates = matches_archive and any(
            key in self.current_successors and self.current_successors[key] != nxt
            for key, nxt in unique.items()
        )
        if not discriminates:
            self.recording_probe = False
            self.probe_successors = []
            self.learner.feedback.clear()
            self.learner.reference = ()
            self.learner.probe_active = False
            return False
        accepted = self.learner.restore_with_evidence()
        self.recording_probe = False
        self.probe_successors = []
        if accepted:
            self.current_successors = dict(self.archived_successors)
        return accepted
