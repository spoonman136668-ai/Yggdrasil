"""Source-free two-hop public causal confirmation of native memory selection.

One-hop outputs may agree between memories while action-conditioned *second*
consequences differ. This bounded auxiliary transition map is learned solely
from action-owned public feedback in FIT, then snapshotted. Selection requires
two distinct, physically linked two-action probes that uniquely corroborate
one map. Unknowns and ties abstain; there is no model-derived goal oracle.
"""
from evidence_selected_three_step import EvidenceSelectedThreeStep

class TwoHopEvidenceSelector(EvidenceSelectedThreeStep):
    def __init__(self, positions=2, capacity=128):
        super().__init__(positions, capacity)
        self.active_links = {}
        self.archived_links = {}
        self.chain_pending = None
        self.chain_evidence = []
        self.chain_probe = False
        self.selected = None

    def learn(self, action, next_frame, reward, done):
        if self.current is None:
            raise ValueError("OBSERVE_FIRST")
        frame, legal = self.current
        if action not in legal or not isinstance(next_frame, bytes) or not next_frame:
            raise ValueError("PUBLIC_LINK_REQUIRED")
        key = (frame, action)
        if self.chain_probe:
            if self.chain_pending is None:
                if len(self.chain_evidence) >= 2:
                    raise ValueError("PROBE_CHAIN_CAP_REACHED")
                self.chain_pending = (key, next_frame)
            else:
                first, middle = self.chain_pending
                if frame != middle or first == key:
                    raise ValueError("UNLINKED_TWO_ACTION_PROBE")
                self.chain_evidence.append((first, middle, key, next_frame))
                self.chain_pending = None
        else:
            if key not in self.active_links and len(self.active_links) >= self.capacity:
                raise ValueError("TRANSITION_MEMORY_CAP_REACHED")
            self.active_links[key] = next_frame
        super().learn(action, next_frame, reward, done)

    def freeze_boundary(self):
        super().freeze_boundary()
        self.archived_links = dict(self.active_links)

    def begin_chain_probe(self):
        if self.snapshot is None or self.current is not None or self.chain_probe:
            raise ValueError("FIT_AND_CLOSE_ACTION_FIRST")
        self.chain_probe = True
        self.chain_pending = None
        self.chain_evidence = []
        self.selected = None

    def resolve_chain_probe(self):
        self.chain_probe = False
        samples = tuple(self.chain_evidence)
        self.chain_evidence = []
        self.chain_pending = None
        if len(samples) != 2 or len({first for first, _, _, _ in samples}) != 2:
            return False
        # Physical continuity: each second state equals the first public
        # successor. A model must correctly predict both stages of both
        # independently started chains; a single accidental hit is insufficient.
        scores = []
        for links in (self.active_links, self.archived_links):
            scores.append(sum(links.get(first) == middle and
                              links.get(second) == terminal
                              for first, middle, second, terminal in samples))
        if scores[0] == scores[1] or max(scores) != 2:
            return False
        self.selected = "active" if scores[0] > scores[1] else "snapshot"
        return True

    def choose(self, horizon=3):
        if self.chain_probe:
            return None
        return super().choose(horizon)
