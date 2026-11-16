"""CB6: retrospective six-sensor identification information and cost bound.

The source state and previous outcomes were consumed in CB5. This module never
calls its generator or uses a hidden sensor label to choose an intervention.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
import math
from itertools import permutations

CANDIDATES = 6
PUBLIC_UPSTREAM_AND_BASELINE_ACTIONS = 5
CB5_ARCHIVE_BLOB = '852e75d7f84bac5f7e090514cda57b1c394327a6'


class DirectExclusion:
    """Constant-size six-bit support; probe once per channel, infer final identity."""

    def __init__(self, *, exactly_one: bool):
        if type(exactly_one) is not bool:
            raise ValueError('CB6_CARDINALITY_CONTRACT_REQUIRED')
        self.exactly_one = exactly_one
        self.support = 0b111111
        self.queried = 0
        self.resolved = None

    def next_probe(self):
        if self.resolved is not None:
            return None
        if self.exactly_one and self.support.bit_count() == 1:
            self.resolved = self.support.bit_length() - 1
            return None
        return next((i for i in range(CANDIDATES)
                     if (self.support >> i) & 1 and not (self.queried >> i) & 1), None)

    def observe(self, channel, causal_reversal):
        if type(channel) is not int or type(causal_reversal) is not bool:
            raise ValueError('CB6_PUBLIC_PROBE_SCHEMA')
        expected = self.next_probe()
        if expected is None or expected != channel:
            raise ValueError('CB6_PUBLIC_ACTION_ORDER_OR_BUDGET')
        # No state updates before all validation checks.
        self.queried |= 1 << channel
        if causal_reversal:
            self.resolved = channel
            self.support = 1 << channel
        else:
            self.support &= ~(1 << channel)
        if self.exactly_one and self.support.bit_count() == 1:
            self.resolved = self.support.bit_length() - 1

    @property
    def probes(self):
        return self.queried.bit_count()

    def raw_logical_bytes(self):
        # Support and spent-probe masks; no Python object overhead included.
        return bytes([self.support, self.queried])


def exact_bayes_optimal_cost(probabilities, prices):
    """Exact six-channel Bayesian optimal adaptive decision cost.

    One causal channel exists. An actual probe reports a deterministic yes/no.
    After a negative, probabilities of other candidates renormalize. A final
    surviving channel is identified without additional paid intervention.
    """
    if len(probabilities) != CANDIDATES or len(prices) != CANDIDATES:
        raise ValueError('CB6_SIX_CANDIDATES_REQUIRED')
    if any(type(p) not in (int,float) or not math.isfinite(p) or p <= 0 for p in probabilities):
        raise ValueError('CB6_POSITIVE_FINITE_PRIOR_REQUIRED')
    if any(type(c) not in (int,float) or not math.isfinite(c) or c < 0 for c in prices):
        raise ValueError('CB6_NONNEGATIVE_COSTS_REQUIRED')
    priors = tuple(float(p) for p in probabilities)
    costs = tuple(float(c) for c in prices)
    @lru_cache(maxsize=None)
    def solve(mask):
        if mask.bit_count() == 1:
            return 0., None
        mass = sum(priors[i] for i in range(CANDIDATES) if mask >> i & 1)
        bids = []
        for i in range(CANDIDATES):
            if (mask >> i) & 1:
                no_mask = mask & ~(1 << i)
                expected = costs[i] + (1. - priors[i] / mass) * solve(no_mask)[0]
                bids.append((expected, i))
        return min(bids)
    return solve((1 << CANDIDATES) - 1)


def exhaustive_symmetric_worlds():
    """All six source-private identities tested without choosing based on them."""
    rows = []
    for hidden in range(CANDIDATES):
        a = DirectExclusion(exactly_one=True)
        while (ch := a.next_probe()) is not None:
            a.observe(ch, ch == hidden)
        if a.resolved != hidden:
            raise AssertionError('CB6_INFERRED_WRONG_CHANNEL')
        rows.append({'hidden_evaluator_only':hidden, 'resolved':a.resolved, 'probes':a.probes,
                     'raw_logical_bytes':len(a.raw_logical_bytes())})
    return rows


def archived_cb5_cost_reduction(record):
    """Arithmetic on CB5 frozen summary, not a re-execution of CB5 source."""
    if record.get('schema') != 'yggdrasil.cb5.blind-mechanism-result.v1':
        raise ValueError('CB6_ARCHIVE_SCHEMA_MISMATCH')
    data = record.get('per_world_receipts', {}).get('world_summary')
    if type(data) is not list or len(data) != 32:
        raise ValueError('CB6_ARCHIVE_WORLD_COUNT')
    total, removed, restored = 0, 0, []
    for idx, row in enumerate(data):
        if (type(row) is not list or len(row) != 6 or type(row[0]) is not int or
            row[0] != 82500+idx or type(row[1]) is not int or not 0 <= row[1] <= 7 or
            type(row[2]) is not int or not 6 <= row[2] <= 11 or
            type(row[5]) is not str or len(row[5]) != 64):
            raise ValueError('CB6_ARCHIVE_WORLD_INTEGRITY')
        original_paid = row[2]
        sensor_probe_rank = original_paid - PUBLIC_UPSTREAM_AND_BASELINE_ACTIONS
        # In CB5 the final candidate's sixth paid test only confirms what the
        # previous five unique negative source outcomes logically established.
        optimized_paid = original_paid - int(sensor_probe_rank == CANDIDATES)
        total += original_paid
        removed += original_paid-optimized_paid
        restored.append([row[0],original_paid,optimized_paid,int(sensor_probe_rank == CANDIDATES)])
    if total != 287 or removed != 11:
        raise ValueError('CB6_ARCHIVE_NOT_EXPECTED_PINNED_RECEIPTS')
    return {'archived_worlds':len(data),'original_total_paid':total,
            'logical_last_positive_confirmations_eliminated':removed,
            'reduced_total_paid':total-removed,'world_costs':restored}


def study(record):
    rows = exhaustive_symmetric_worlds()
    cost, first = exact_bayes_optimal_cost((1,)*6, (1,)*6)
    archive = archived_cb5_cost_reduction(record)
    result = {
        'schema':'yggdrasil.cb6.retrospective-probe-bound-result.v1',
        'classification':'RETROSPECTIVE_COST_SAVING_TIES_EXACT_BAYES__NO_SCIENTIFIC_ADVANTAGE',
        'source_first_use':False,'new_source_interventions_executed':0,
        'candidate_correct_all_six_hypotheses':all(x['resolved']==x['hidden_evaluator_only'] for x in rows),
        'new_candidate_cost_by_hidden_channel':[x['probes'] for x in rows],
        'candidate_expected_downstream_paid_uniform':sum(x['probes'] for x in rows)/6,
        'independent_optimal_exact_bayes_expected_downstream_paid_uniform':cost,
        'optimal_bayes_first_channel':first,
        'original_confirm_positive_expected_downstream_uniform':7/2,
        'original_max_paid_per_world':11,'improved_max_paid_per_world':10,
        'candidate_logical_bytes':2,
        'retroactive_cb5_original_outcomes_unchanged':True,
        'archive':archive,
        'scientific_pass':False,'native_promotion':False,
    }
    if abs(result['candidate_expected_downstream_paid_uniform']-cost) > 1e-12:
        raise AssertionError('CB6_BAYES_DOMINATES_OR_COST_MISMATCH')
    result['untimed_receipt_sha256'] = sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result


if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:
        raise SystemExit('usage: python probe_bound.py /path/to/FKP18-CB5/result.json')
    with open(sys.argv[1],encoding='utf-8') as f:
        print(json.dumps(study(json.load(f)),sort_keys=True,indent=2))
