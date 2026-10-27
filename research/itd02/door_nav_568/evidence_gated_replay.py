"""Bounded history archive with evidence-gated restoration of learned local cells.

Regimes A/B are not observable labels. Restoration is permitted only after
public action-owned feedback identifies which historical response mapping fits.
No original DoorKey data and no claim of zero-shot regime detection.
"""
from learned_byte_cells import LearnedByteCells

class EvidenceGatedReplay:
    def __init__(self, feature_positions=2, max_examples=8, max_archives=2):
        if type(max_archives) is not int or not 1 <= max_archives <= 8:
            raise ValueError("ARCHIVE_LIMIT_INVALID")
        self.feature_positions = feature_positions
        self.max_examples = max_examples
        self.max_archives = max_archives
        self.active = LearnedByteCells(feature_positions, max_examples=max_examples)
        self.archives = []
        self.feedback = []
        self.reference = ()
        self.probe_active = False

    def start_probe(self):
        # Only explicitly admitted post-training feedback can restore an archive.
        self.feedback.clear()
        self.reference = ()
        self.probe_active = True

    def observe(self, frame, actions):
        self.active.observe(frame, actions)

    def choose(self):
        return self.active.choose()

    def learn(self, action, next_frame, reward, done):
        frame, _ = self.active.current
        if self.probe_active:
            if not self.feedback:
                self.reference = tuple(self.active.examples)
            self.feedback.append((frame, action, int(reward > 0)))
            self.feedback = self.feedback[-2:]
        self.active.learn(action, next_frame, reward, done)

    def archive(self):
        snapshot = tuple(self.active.examples)
        if snapshot and snapshot not in self.archives:
            self.archives.append(snapshot)
            self.archives = self.archives[-self.max_archives:]

    def restore_with_evidence(self):
        if not self.probe_active or len(self.feedback) < 2:
            self.feedback.clear()
            self.reference = ()
            self.probe_active = False
            return False
        # Compare observed outcomes under the same public frame and tested
        # action. Restore only on a unique strictly better retrospective fit.
        def match(snapshot):
            known = {(f, a): positive for f, a, positive in snapshot}
            return sum(known.get((f, a)) == outcome for f, a, outcome in self.feedback
                       if (f, a) in known)
        active_score = match(self.reference)
        archive_scores = [match(snapshot) for snapshot in self.archives]
        if (not archive_scores or max(archive_scores) <= active_score or
                archive_scores.count(max(archive_scores)) != 1):
            # An evaluated but unsuccessful probe cannot be reused alongside
            # one subsequent observation to manufacture two confirmations.
            self.feedback.clear()
            self.reference = ()
            self.probe_active = False
            return False
        best = archive_scores.index(max(archive_scores))
        selected = self.archives[best]
        self.active = LearnedByteCells(self.feature_positions, max_examples=self.max_examples)
        for frame, action, outcome in selected:
            self.active.observe(frame, [0, 1])
            self.active.learn(action, b"replay-public-placeholder", outcome, True)
        self.feedback.clear()
        self.reference = ()
        self.probe_active = False
        return True
