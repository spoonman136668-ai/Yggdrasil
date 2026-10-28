"""V30 opt-in, EXTERNAL public-count action selection; no hidden world labels.

This policy does not train weights, modify the native V22 ring, or claim
native curiosity.  It observes only actions actually selected, never
unselected rewards, reward-law families, environment identities or outcomes.
"""
import random
from .itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES

CHOICES = ("novelty", "greedy", "round_robin", "random")
SEED = 3001


class PublicProbePolicyDev:
    """Selected-public-action frequency explorer at a supplied legal context."""

    def __init__(self, mode="novelty", *, seed=SEED):
        if type(mode) is not str or mode not in CHOICES:
            raise ValueError("INVALID_V30_PROBE_POLICY")
        if type(seed) is not int or seed != SEED:
            raise ValueError("V30_RANDOM_SEED_IS_FROZEN")
        self.mode = mode
        self.counts = {}
        self.last = {}
        self.events = 0
        self.random = random.Random(seed)
        self.choices = []

    @staticmethod
    def _key(cue, first):
        if type(cue) is not str or cue not in PUBLIC_CUES:
            raise ValueError("V30_INVALID_PUBLIC_CUE")
        if type(first) is not str or first not in ACTIONS:
            raise ValueError("V30_INVALID_FIRST_ACTION")
        return (cue, first)

    def observe_selected(self, cue, first, selected):
        key = self._key(cue, first)
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("V30_INVALID_ACTUAL_SELECTED_SECOND")
        if key not in self.counts:
            self.counts[key] = [0] * len(ACTIONS)
        self.counts[key][ACTIONS.index(selected)] += 1
        self.last[key] = selected
        self.events += 1

    def select(self, cue, first, scores):
        key = self._key(cue, first)
        if (type(scores) not in (tuple,list) or len(scores) != len(ACTIONS)
                or any(type(s) not in (int,float) or
                       not (-1e6 <= s <= 1e6) for s in scores)):
            raise ValueError("V30_NONFINITE_OR_INVALID_PUBLIC_SCORES")
        count = self.counts.get(key, [0,0,0])
        if self.mode == "novelty":
            minimum = min(count)
            idx = max((i for i in range(len(ACTIONS)) if count[i] == minimum),
                      key=lambda i: (scores[i],-i))
        elif self.mode == "greedy":
            idx = max(range(len(ACTIONS)), key=lambda i: (scores[i],-i))
        elif self.mode == "round_robin":
            if key not in self.last:
                raise ValueError("V30_ROUND_ROBIN_REQUIRES_ACTUAL_PREVIOUS_ACTION")
            idx = (ACTIONS.index(self.last[key]) + 1) % len(ACTIONS)
        else:
            idx = self.random.randrange(len(ACTIONS))
        selected = ACTIONS[idx]
        self.choices.append((key, selected))
        return selected
