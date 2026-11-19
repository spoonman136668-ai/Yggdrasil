"""Infer an outcome relation before borrowing FIT evidence across cells."""

from fractions import Fraction
from math import comb


def count_transitions(rows, cell):
    counts = [0, 0]
    for _, views, row in rows:
        if (views[0][0], row["x1"]) == cell:
            counts[row["s2"]] += 1
    return tuple(counts)


def marginal(counts):
    zeros, ones = counts
    total = zeros + ones
    return Fraction(1, (total + 1) * comb(total, ones))


def relation_posterior(left, right):
    """Equal, complemented, and independent Beta(1,1) relation weights."""
    az, ao = left
    bz, bo = right
    terms = (marginal((az + bz, ao + bo)), marginal((az + bo, ao + bz)),
             marginal(left) * marginal(right))
    return tuple(mass / sum(terms) for mass in terms)


def transfer_priors(familiar, shifted, target, peer, confidence):
    """Create predictive priors from FIT only. Priors are never witness rows."""
    left = count_transitions(familiar, target)
    right = count_transitions(familiar, peer)
    donor = count_transitions(shifted, peer)
    if not min(sum(left), sum(right), sum(donor)):
        return {}, {}, None
    if sum(count_transitions(shifted, target)):
        raise ValueError("Target unexpectedly observed in shifted FIT")
    equal, complement, independent = relation_posterior(left, right)
    raw = donor[0] + 1, donor[1] + 1
    hard = {}
    if equal >= confidence:
        hard[target] = raw
    elif complement >= confidence:
        hard[target] = raw[::-1]
    # Normalizing to a common pseudo-sample size keeps the exact predictive mean
    # of all three hypotheses. These endpoints are frozen during evaluation.
    total = sum(raw)
    probability = (equal * raw[1] + complement * raw[0]) / total + independent / 2
    soft = {target: ((1 - probability) * total, probability * total)}
    return hard, soft, (equal, complement, independent)
