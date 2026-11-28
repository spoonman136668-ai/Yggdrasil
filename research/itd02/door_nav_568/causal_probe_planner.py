"""Bounded information-seeking probe selection from learned public transitions.

Enumerates two-action candidate chains already represented in BOTH learned
maps. Ranks them by disagreement in predicted second-step consequences; the
first-step successor must agree, so the probe actually isolates the disputed
causal link. No environment label, hard-coded probe action, reward oracle or
access to future observations. Only the publicly legal actions supplied by
the caller may be selected. Do not confuse candidate ranking with physical
execution: the caller must execute each action and deliver public outcomes.
"""
class CausalProbePlanner:
    def __init__(self, max_candidates=128):
        if type(max_candidates) is not int or not 2 <= max_candidates <= 256:
            raise ValueError("PROBE_SEARCH_LIMIT_INVALID")
        self.max_candidates = max_candidates

    def rank(self, active_links, archived_links, starts):
        proposals = []
        seen = set()
        for frame, legal in starts:
            if not isinstance(frame, bytes):
                raise ValueError("PUBLIC_START_REQUIRED")
            if len(legal) != len(set(legal)):
                raise ValueError("LEGAL_ACTIONS_INVALID")
            for first_action in legal:
                first = (frame, first_action)
                if first not in active_links or first not in archived_links:
                    continue
                middle = active_links[first]
                if middle != archived_links[first]:
                    continue  # A second-hop-only hypothesis test.
                # Candidate second actions must have been observed from the
                # same public middle state in both models.
                next_actions = sorted(
                    {a for (s, a) in active_links if s == middle} &
                    {a for (s, a) in archived_links if s == middle}
                )
                for second_action in next_actions:
                    second = (middle, second_action)
                    if first == second:
                        continue
                    if active_links[second] == archived_links[second]:
                        continue
                    identity = (first, second)
                    if identity in seen:
                        continue
                    seen.add(identity)
                    proposals.append((first, middle, second))
                    if len(proposals) > self.max_candidates:
                        raise ValueError("PROBE_CANDIDATE_CAP_REACHED")
        return sorted(proposals, key=lambda p: (p[0][0], p[0][1], p[2][1]))

    def select_pair(self, active_links, archived_links, starts):
        candidates = self.rank(active_links, archived_links, starts)
        for i, left in enumerate(candidates):
            for right in candidates[i+1:]:
                if left[0][0] != right[0][0] and left[2] != right[2]:
                    return (left, right)
        return None
