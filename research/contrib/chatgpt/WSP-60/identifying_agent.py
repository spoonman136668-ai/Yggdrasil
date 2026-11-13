"""WSP60: preserve all consistent causal hypotheses, actively disambiguate.

Minimal extension of WSP59's source-blind grounded causal learner. The sole
changes are (a) not prematurely selecting the minimum-parent explanation,
and (b) choosing new charged states where plausible explanations disagree.
No WSP59/WSP60 evaluator-source import or hidden physics functions.
"""
from __future__ import annotations
from collections import Counter
from itertools import combinations
from math import log2
from pathlib import Path
import sys

_PARENT = Path(__file__).resolve().parents[1] / "WSP-59"
sys.path.insert(0, str(_PARENT))
from agent import GroundedCausalAgent, DOMAINS, STATES, CHANNELS, PARENT_SETS

BaseAgent = GroundedCausalAgent


class IdentifyingAgent(BaseAgent):
    gradient_updates = 0

    @staticmethod
    def _candidate_rules(observations, register):
        """Preserve every fully covered, evidence-consistent <=2-parent map.

        The real source's true causal parent subset is included because the
        common 10-state pairwise design covers every 2-parent combination.
        As long as that source prior holds, unanimous predictions are sound.
        """
        candidates = []
        for parents in PARENT_SETS:
            rule = {}
            consistent = True
            for before, after in observations:
                key = tuple(before[j] for j in parents)
                value = after[register]
                if key in rule and rule[key] != value:
                    consistent = False
                    break
                rule[key] = value
            possible = 1
            for j in parents:
                possible *= DOMAINS[j]
            if consistent and len(rule) == possible:
                candidates.append((parents, rule))
        return tuple(candidates)

    def candidate_counts(self):
        self._compile()
        return tuple(tuple(len(self._rules[action][k]) for k in range(3))
                     for action in CHANNELS)

    def select_disambiguating(self, action):
        """Find a counterexample separating retained explanations.

        This is a query of the *candidate models*, never the source
        simulator. The caller must separately charge/reveal its chosen
        physical action. Tie-break deterministically on state tuple.
        """
        if type(action) is not int or action not in CHANNELS:
            raise ValueError("invalid action channel")
        self._compile()
        observed = {b for b, a, y in self.rows if a == action}
        if len(observed) < 10 or len(observed) >= 12:
            raise ValueError("requires 10 or 11 charged probes/channel")
        candidate_states = [state for state in STATES if state not in observed]
        if not candidate_states:
            raise ValueError("no remaining chargeable physical state")
        scored = []
        for state in candidate_states:
            uncertainty = 0.0
            disagreement = 0
            for options in self._rules[action]:
                votes = Counter(
                    mapping[tuple(state[j] for j in parents)]
                    for parents, mapping in options
                )
                if not votes:
                    continue
                total = sum(votes.values())
                entropy = -sum((count/total) * log2(count/total)
                               for count in votes.values())
                uncertainty += entropy
                disagreement += int(len(votes) > 1)
            scored.append((disagreement, uncertainty, state))
        best_disagreements = max(row[0] for row in scored)
        tied = [row for row in scored if row[0] == best_disagreements]
        best_entropy = max(row[1] for row in tied)
        return min(row[2] for row in tied if abs(row[1]-best_entropy) <= 1e-12)
