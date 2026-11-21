"""CKAD25 opt-in source-witnessed latent single-fault risk calculation.

Pure exact arithmetic; posterior is recomputed from the native three-world
source ledger after cold restoration, and never reads generator/world labels.
This fixed *hypothesis class* is conventional; its q value is not supplied.
"""
from fractions import Fraction
from itertools import product

Q_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(9, 10))
MAX_HISTORICAL_WORLDS = 3


def _require(cond, message):
    if not cond:
        raise ValueError("CKAD_SHARED_RISK_" + message)


def _bit(value):
    _require(type(value) is int and value in (0, 1), "OBSERVED_BIT")
    return value


class NativeSharedFaultRisk:
    """Finite, evidence-fitted posterior on (unknown hot site, unknown q)."""

    def __init__(self, candidate_masks, public_worlds):
        _require(type(candidate_masks) in (list, tuple) and
                 len(candidate_masks) == 4 and
                 all(type(x) is int and 0 <= x < 16 for x in candidate_masks) and
                 len(set(candidate_masks)) == 4, "PUBLIC_CANDIDATES")
        _require(type(public_worlds) in (list, tuple) and
                 len(public_worlds) == MAX_HISTORICAL_WORLDS,
                 "EXACT_NATIVE_THREE_WORLDS")
        self.masks = tuple(sorted(candidate_masks))
        self.worlds = []
        for world in public_worlds:
            _require(type(world) in (list, tuple) and len(world) == 2,
                     "TWO_WITNESSES_PER_WORLD")
            seen = set()
            facts = []
            for row in world:
                _require(type(row) in (tuple, list) and len(row) == 2,
                         "WITNESS_SHAPE")
                mask, value = row
                _require(type(mask) is int and mask in self.masks and
                         mask not in seen, "UNIQUE_PUBLIC_WITNESSES")
                seen.add(mask)
                facts.append((mask, _bit(value)))
            _require(sum(value for _, value in facts) <= 1,
                     "SINGLE_DEFECT_HYPOTHESIS_CONFLICT")
            self.worlds.append(tuple(sorted(facts)))
        self.worlds = tuple(self.worlds)
        posterior = []
        for hot, q in product(self.masks, Q_GRID):
            mass = Fraction(1, 16)
            for world in self.worlds:
                selected = {mask: outcome for mask, outcome in world}
                if 1 in selected.values():
                    fault_mask = next(mask for mask, y in world if y)
                    likelihood = q if fault_mask == hot else (1-q)/3
                else:
                    likelihood = 1 - sum(
                        (q if mask == hot else (1-q)/3 for mask in selected),
                        Fraction(0))
                _require(likelihood >= 0, "LIKELIHOOD")
                mass *= likelihood
            posterior.append((hot, q, mass))
        evidence = sum((mass for _, _, mass in posterior), Fraction(0))
        _require(evidence > 0, "ZERO_EVIDENCE")
        self.evidence = evidence
        self.posterior = tuple((hot, q, mass/evidence)
                               for hot, q, mass in posterior)
        risks = [sum((weight*(q if hot == mask else (1-q)/3)
                      for hot, q, weight in self.posterior), Fraction(0))
                 for mask in self.masks]
        _require(sum(risks, Fraction(0)) == 1 and
                 all(Fraction(0) <= x <= Fraction(1) for x in risks),
                 "NORMALIZED_PREDICTION")
        self.risks = tuple(risks)

    def risk(self, mask):
        _require(type(mask) is int and mask in self.masks, "FORECAST_MASK")
        return self.risks[self.masks.index(mask)]

    def select(self):
        return tuple(sorted(self.masks, key=lambda a: (-self.risk(a), a))[:2])

    def checkpoint_fingerprint(self):
        # Entire posterior is deterministic from existing native source rows.
        return (self.masks, self.worlds, self.posterior, self.risks)


def independent_beta_risks(masks, worlds, *, trailing_worlds=None):
    """Exact existing CKAD25 mean-risk formula; no supplied hazard prior."""
    data = worlds[-trailing_worlds:] if trailing_worlds else worlds
    result = {}
    for mask in masks:
        outcomes = [value for world in data for address,value in world
                    if address == mask]
        result[mask] = Fraction(1+sum(outcomes), 2+len(outcomes))
    return result
