"""CKAD25 opt-in source-witnessed latent single-fault risk calculation.

Pure exact arithmetic; posterior is recomputed from the native three-world
source ledger after cold restoration, and never reads generator/world labels.
This fixed *hypothesis class* is conventional; its q value is not supplied.

Integer likelihoods share denominator 60. The 3-world posterior has a
common denominator 60**3, and predicted risks have denominator 60*sum(weights).
No approximation, prefetch or evaluator labels are used.
"""
from fractions import Fraction

Q_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(9, 10))
MAX_HISTORICAL_WORLDS = 3
_SCALE = 60
_Q_SCALED = (15, 30, 45, 54)
_OTHER_SCALED = (15, 10, 5, 2)
if any(Fraction(_Q_SCALED[i], _SCALE) != q or
       Fraction(_OTHER_SCALED[i], _SCALE) != (1-q)/3
       for i, q in enumerate(Q_GRID)):
    raise RuntimeError("CKAD_SHARED_RISK_COMPILED_MODEL_DRIFT")

# Hypothesis-only compilation: no source-specific observations or checkpoints
# live in this table. For each pair of public *positions* and its observed
# 00/10/01 outcome, precompute P(observed | unknown hot position, unknown q)
# multiplied by the common exact denominator 60. 6 pairs * 3 outcomes = 18.
# All table entries are nonnegative integers; no rounding or object cache.
def _likelihood_table():
    table = {}
    for i in range(4):
        for j in range(i + 1, 4):
            for signal in range(3):
                row = []
                for hot in range(4):
                    for q_index in range(len(Q_GRID)):
                        at_i = _Q_SCALED[q_index] if hot == i else _OTHER_SCALED[q_index]
                        at_j = _Q_SCALED[q_index] if hot == j else _OTHER_SCALED[q_index]
                        value = (60 - at_i - at_j if signal == 0
                                 else at_i if signal == 1 else at_j)
                        if value < 0:
                            raise RuntimeError('INVALID_FINITE_MODEL_LIKELIHOOD')
                        row.append(value)
                table[i, j, signal] = tuple(row)
    return table

_LIKELIHOOD_TABLE = _likelihood_table()


def _require(cond, message):
    if not cond:
        raise ValueError("CKAD_SHARED_RISK_" + message)


def _bit(value):
    _require(type(value) is int and value in (0, 1), "OBSERVED_BIT")
    return value


class NativeSharedFaultRisk:
    """Finite evidence-fitted posterior on (unknown hot site, unknown q)."""

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

        # Candidate IDs are not meaning-bearing; map each public address
        # to its source-visible position and select a compiled exact likelihood
        # for its *observed* action/outcome witness pair. Never read hidden hot.
        positions = {mask:i for i,mask in enumerate(self.masks)}
        event_likelihoods = []
        for world in self.worlds:
            left, right = world
            signal = 1 if left[1] else 2 if right[1] else 0
            event_likelihoods.append(_LIKELIHOOD_TABLE[
                positions[left[0]], positions[right[0]], signal])
        e0, e1, e2 = event_likelihoods

        weighted = []
        all_other_numerator = 0
        hot_delta_numerators = [0,0,0,0]
        for hot_index, hot in enumerate(self.masks):
            for i,q in enumerate(Q_GRID):
                index = hot_index * len(Q_GRID) + i
                weight = e0[index] * e1[index] * e2[index]
                weighted.append((hot, q, i, weight))
                all_other_numerator += weight * _OTHER_SCALED[i]
                hot_delta_numerators[hot_index] += weight * (
                    _Q_SCALED[i] - _OTHER_SCALED[i])

        total = sum(weight for _,_,_,weight in weighted)
        _require(total > 0, "ZERO_EVIDENCE")
        self._weighted = tuple(weighted)
        self._total = total
        self._risk_numerators = tuple(
            all_other_numerator + hot_delta_numerators[i]
            for i in range(4))
        _require(sum(self._risk_numerators) == _SCALE * total
                 and all(0 <= v <= _SCALE * total
                         for v in self._risk_numerators),
                 "NORMALIZED_PREDICTION")
        self._posterior_cache = None
        self._risks_cache = None

    @property
    def evidence(self):
        return Fraction(self._total,
                        16 * _SCALE ** MAX_HISTORICAL_WORLDS)

    @property
    def posterior(self):
        if self._posterior_cache is None:
            self._posterior_cache = tuple(
                (hot, q, Fraction(weight, self._total))
                for hot, q, i, weight in self._weighted)
        return self._posterior_cache

    @property
    def risks(self):
        if self._risks_cache is None:
            self._risks_cache = tuple(
                Fraction(v, _SCALE * self._total)
                for v in self._risk_numerators)
        return self._risks_cache

    def risk(self, mask):
        _require(type(mask) is int and mask in self.masks, "FORECAST_MASK")
        return Fraction(self._risk_numerators[self.masks.index(mask)],
                        _SCALE * self._total)

    def select(self):
        # All addresses share one positive denominator, so ranking exact
        # integer numerators is identical to ranking Fraction risks.
        return tuple(a for a, numerator in sorted(
            zip(self.masks, self._risk_numerators),
            key=lambda pair: (-pair[1], pair[0]))[:2])

    def checkpoint_fingerprint(self):
        return (self.masks, self.worlds, self.posterior, self.risks)


def independent_beta_risks(masks, worlds, *, trailing_worlds=None):
    """Exact existing CKAD25 mean-risk formula; no supplied hazard prior."""
    data = worlds[-trailing_worlds:] if trailing_worlds else worlds
    result = {}
    for mask in masks:
        outcomes = [value for world in data for address, value in world
                    if address == mask]
        result[mask] = Fraction(1 + sum(outcomes), 2 + len(outcomes))
    return result
