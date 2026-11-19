"""Research-only cross-action relationship proposals from the native witness ledger.

This module is intentionally not imported by the native planner or trainer.  It
reads accepted public witness rows and never mutates checkpoints, action choice,
source data, or specialist weights.  It does not assert transfer to new contexts.
"""

from collections import defaultdict
from hashlib import sha256
from math import exp, lgamma
import json
import re

HYPOTHESES = ("equal", "complement", "independent")
_HALF = 0.5
_LOG_BETA_HALF = 2 * lgamma(_HALF) - lgamma(1.0)
_ID = re.compile(r"[0-9a-f]{64}\Z")


def _bit(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("RELATION_PUBLIC_BIT_REQUIRED")
    return value


def _log_integrated(zeros, ones):
    """Log Beta-Bernoulli evidence under the fixed Jeffreys Beta(1/2,1/2) prior."""
    return (lgamma(zeros + _HALF) + lgamma(ones + _HALF)
            - lgamma(zeros + ones + 1.0) - _LOG_BETA_HALF)


def _context_evidence(counts):
    a0, a1 = counts
    zero0, one0 = a0
    zero1, one1 = a1
    return {
        "equal": _log_integrated(zero0 + zero1, one0 + one1),
        "complement": _log_integrated(zero0 + one1, one0 + zero1),
        "independent": _log_integrated(zero0, one0) + _log_integrated(zero1, one1),
    }


class RelationShadow:
    """Shadow-only three-hypothesis selector; construction requires accepted rows.

    Pass the immutable ledger from a separately restored and verified native
    checkpoint, not free-form simulator output.  Each row has the existing native
    shape (receipt_id, paired_public_views, first_action, transition,
    second_action, reward).  The retained rows are copied, never modified.
    """

    def __init__(self, accepted_ledger):
        seen = set()
        self._cells = defaultdict(lambda: [[0, 0], [0, 0]])
        canonical_rows = []
        for entry in accepted_ledger:
            if type(entry) not in (list, tuple) or len(entry) != 6:
                raise ValueError("RELATION_ACCEPTED_ROW_SHAPE")
            identifier, views, first, transition, second, reward = entry
            if type(identifier) is not str or _ID.fullmatch(identifier) is None:
                raise ValueError("RELATION_WITNESS_ID")
            if identifier in seen:
                raise ValueError("RELATION_DUPLICATE_WITNESS")
            seen.add(identifier)
            if (type(views) not in (list, tuple) or len(views) != 2
                    or any(type(view) not in (list, tuple) or len(view) != 2
                           for view in views)):
                raise ValueError("RELATION_PAIRED_VIEWS")
            context, nuisance = views[0]
            other_context, other_nuisance = views[1]
            if (type(context) is not int or not 0 <= context <= 65535
                    or context != other_context):
                raise ValueError("RELATION_PUBLIC_CONTEXT")
            _bit(nuisance)
            _bit(other_nuisance)
            first = _bit(first)
            transition = _bit(transition)
            second = _bit(second)
            reward = _bit(reward)
            self._cells[context][first][transition] += 1
            canonical_rows.append((identifier, context, nuisance, other_nuisance,
                                   first, transition, second, reward))
        self.witness_count = len(canonical_rows)
        self.witness_sha256 = sha256(json.dumps(
            canonical_rows, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")).hexdigest()

    def propose(self, context, missing_action):
        """Offer a prediction only in shadow mode for an unobserved action cell.

        The other action's local successes provide a target-context estimate.
        Only *other* contexts with both interventions provide relationship
        evidence.  Equal, complementary and independent hypotheses each get an
        identical fixed prior; the independent alternative covers unrelated
        action rates **within this menu**, not unknown mechanism families.  A
        target action with zero witnesses remains non-identifiable even if the
        contrast posterior approaches 1.  No held label or family ID is consulted.
        """
        if type(context) is not int or not 0 <= context <= 65535:
            raise ValueError("RELATION_PUBLIC_CONTEXT")
        missing_action = _bit(missing_action)
        own = self._cells.get(context)
        if own is None:
            return None
        if sum(own[missing_action]) or not sum(own[1 - missing_action]):
            return None

        contrasts = [bank for key, bank in sorted(self._cells.items())
                     if key != context and sum(bank[0]) and sum(bank[1])]
        if not contrasts:
            return None
        scores = {name: 0.0 for name in HYPOTHESES}
        for bank in contrasts:
            evidence = _context_evidence(bank)
            for name in HYPOTHESES:
                scores[name] += evidence[name]
        shift = max(scores.values())
        masses = {name: exp(scores[name] - shift) for name in HYPOTHESES}
        normalizer = sum(masses.values())
        posterior = {name: masses[name] / normalizer for name in HYPOTHESES}

        zeros, ones = own[1 - missing_action]
        local = (ones + _HALF) / (ones + zeros + 1.0)
        proposed = (posterior["equal"] * local
                    + posterior["complement"] * (1.0 - local)
                    + posterior["independent"] * 0.5)
        # In two possible worlds sharing this exact public ledger, the missing
        # outcome may always be 0 or always be 1.  With no separately admitted
        # structural transfer assumption, its identified probability interval
        # is [0, 1] regardless of the posterior over this restricted menu.
        # An unknown target action must never become an actionable prediction.
        risk_zero = proposed * proposed
        risk_one = (1.0 - proposed) * (1.0 - proposed)
        return {
            "context": context,
            "unobserved_action": missing_action,
            "forecast": proposed,  # Diagnostic forecast only; never for decisions.
            "posterior": posterior,
            "identification_status": "UNIDENTIFIED_TARGET_ACTION",
            "target_action_support": 0,
            "identified_probability_interval": (0.0, 1.0),
            "decision_forecast": None,
            "decision_eligible": False,
            "minimax_brier": 0.25,
            "worst_case_brier": max(risk_zero, risk_one),
            "balanced_two_world_brier": (risk_zero + risk_one) / 2.0,
            "other_action_support": zeros + ones,
            "independent_contrast_contexts": len(contrasts),
            "witness_count": self.witness_count,
            "witness_sha256": self.witness_sha256,
            "decision_authority": "NONE_SHADOW_ONLY",
            "science_status": "UNQUALIFIED_PROPOSAL",
        }
