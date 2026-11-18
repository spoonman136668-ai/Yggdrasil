"""CK20-PVA01: read-only paired delayed-reward evidence audit.

This does not execute CKAD20 environments or authorize native integration.
Accepted source receipts must be independently verified; matching hashes alone
do not prove an action actually ran.
"""
import argparse
import hashlib
import itertools
import json
from math import ceil, erf, sqrt
from pathlib import Path

SCHEMA = 'yggdrasil.ck20.paired-reward-execution-receipts.v1'
OUT_SCHEMA = 'yggdrasil.ck20.paired-policy-value-audit.v1'
SEEDS = (101, 202, 303)
EXPECTED_PER_SEED = 96
DELTA = .02
Q_VALUES = (.02, .05, .10, .25, .5)
Z975 = 1.959963984540054
Z80 = .8416212335729143


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def ensure(ok, code):
    if not ok:
        raise ValueError('CK20_PVA_' + code)


def pin(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def validate_arm(arm):
    ensure(type(arm) is dict and set(arm) ==
           {'execution', 'a1', 's2', 'a2', 'y', 'trace_sha256'}, 'ARM_SCHEMA')
    ensure(arm['execution'] == 'executed', 'NOT_EXECUTED')
    ensure(all(type(arm[k]) is int and arm[k] in (0,1)
               for k in ('a1','s2','a2','y')), 'ARM_PUBLIC_BINARY')
    ensure(pin(arm['trace_sha256']), 'ARM_TRACE_PIN')


def validate(document):
    ensure(type(document) is dict and set(document) ==
           {'schema', 'cohort', 'protocol_sha256', 'comparator', 'pairs'}, 'SCHEMA')
    ensure(document['schema'] == SCHEMA and document['cohort'] == 'eval-2'
           and pin(document['protocol_sha256']), 'PROTOCOL_PIN')
    ensure(type(document['comparator']) is str and bool(document['comparator'])
           and document['comparator'] != 'native', 'COMPARATOR_ID')
    pairs = document['pairs']
    ensure(type(pairs) is list and len(pairs) == 288, 'MATCHED_COUNT')
    seen = set()
    reward = {seed: [] for seed in SEEDS}
    for row in pairs:
        ensure(type(row) is dict and set(row) ==
               {'seed', 'episode', 'draw_sha256', 'native', 'control'}, 'PAIR_SCHEMA')
        seed, episode = row['seed'], row['episode']
        ensure(type(seed) is int and seed in SEEDS and type(episode) is int
               and 0 <= episode < EXPECTED_PER_SEED, 'PAIR_IDENTITY')
        ensure((seed, episode) not in seen, 'DUPLICATE_IDENTITY')
        seen.add((seed, episode))
        ensure(pin(row['draw_sha256']), 'DRAW_PIN')
        validate_arm(row['native'])
        validate_arm(row['control'])
        ensure(row['native']['trace_sha256'] != row['control']['trace_sha256'],
               'REUSED_TRACE')
        reward[seed].append(row['native']['y'] - row['control']['y'])
    ensure(all(len(reward[seed]) == EXPECTED_PER_SEED for seed in SEEDS),
           'MISSING_PAIRS')
    return reward


def exact_seed_signflip(deltas):
    """Two-sided nonparametric randomization for three independent seed groups."""
    ensure(type(deltas) is tuple and len(deltas) == 3
           and all(type(x) in (float,int) for x in deltas), 'DELTAS')
    observed = abs(sum(deltas))
    count = sum(abs(sum(sign * diff for sign, diff in zip(signs, deltas)))
                >= observed - 1e-12 for signs in itertools.product((-1,1),repeat=3))
    return count / 8


def sensitivity():
    data=[]
    for q in Q_VALUES:
        variance = q - DELTA*DELTA
        needed = ceil(((Z975+Z80)**2) * variance / (DELTA**2))
        se = sqrt(variance / 288)
        z = DELTA/se
        normal_cdf=lambda x: .5*(1+erf(x/sqrt(2)))
        power=normal_cdf(z-Z975)+normal_cdf(-z-Z975)
        data.append({'discordance_assumption':q,
                     'approx_n_for_80_percent_power':needed,
                     'approx_power_at_n_288':power})
    return data


def evaluate(document):
    rewards=validate(document)
    per_seed={str(seed):sum(rewards[seed])/len(rewards[seed]) for seed in SEEDS}
    changes=tuple(per_seed[str(seed)] for seed in SEEDS)
    observed=sum(changes)/len(changes)
    p=exact_seed_signflip(changes)
    return {
        'schema':OUT_SCHEMA,
        'source_protocol_sha256':document['protocol_sha256'],
        'source_comparator':document['comparator'],
        'paired_final_cohort_episodes':288,
        'seed_groups':3,
        'per_seed_difference':per_seed,
        'mean_paired_reward_difference':observed,
        'development_margin_met':observed >= DELTA,
        'two_sided_cluster_exact_p':p,
        'cluster_test_05_pass':p < .05,
        'cannot_attain_cluster_05_with_three_seeds':True,
        'sensitivity_not_observed':sensitivity(),
        'receipt_schema_validated':True,
        'receipt_execution_independently_verified':False,
        'scientific_pass':False,
        'deployment':'NONE'
    }


def synthetic_fixture():
    """Only a test fixture. Never label these synthetic rows as CKAD20 results."""
    rows=[]
    for seed in SEEDS:
        for i in range(EXPECTED_PER_SEED):
            arm0={'execution':'executed','a1':0,'s2':0,'a2':0,'y':1,
                  'trace_sha256':digest(canonical(['native',seed,i]))}
            arm1={'execution':'executed','a1':1,'s2':1,'a2':1,'y':0,
                  'trace_sha256':digest(canonical(['control',seed,i]))}
            rows.append({'seed':seed,'episode':i,
                         'draw_sha256':digest(canonical(['exogenous',seed,i])),
                         'native':arm0,'control':arm1})
    return {'schema':SCHEMA,'cohort':'eval-2',
            'protocol_sha256':digest(canonical(['CKAD20','FIXTURE_ONLY'])),
            'comparator':'matched-conventional-fixture','pairs':rows}


def self_test():
    assert all(sum(1 for x in range(16) if x&1)==8 for _ in range(1))
    assert exact_seed_signflip((1.,1.,1.))==.25
    assert exact_seed_signflip((.02,.02,.02))==.25
    assert exact_seed_signflip((0.,0.,0.))==1.0
    assert min(exact_seed_signflip(ds) for ds in
               itertools.product((-1, 0, 1), repeat=3))>=.25
    assert [r['approx_n_for_80_percent_power'] for r in sensitivity()] == [385,974,1955,4898,9804]
    sample=synthetic_fixture()
    a=evaluate(sample)
    assert a['mean_paired_reward_difference']==1.0
    assert a['two_sided_cluster_exact_p']==.25
    assert a['development_margin_met'] and not a['cluster_test_05_pass']
    bad=json.loads(canonical(sample))
    bad['pairs'][0]['control']['execution']='imputed'
    try:
        evaluate(bad)
        raise AssertionError('CK20_PVA_IMPUTED_WAS_ACCEPTED')
    except ValueError as exc:
        assert 'NOT_EXECUTED' in str(exc)
    bad=json.loads(canonical(sample))
    bad['pairs'][1]['episode']=0
    try:
        evaluate(bad)
        raise AssertionError('CK20_PVA_DUPLICATE_WAS_ACCEPTED')
    except ValueError as exc:
        assert 'DUPLICATE_IDENTITY' in str(exc)
    bad=json.loads(canonical(sample))
    bad['pairs'][0]['control']['y']=None
    try:
        evaluate(bad)
        raise AssertionError('CK20_PVA_MISSING_REWARD_WAS_ACCEPTED')
    except ValueError as exc:
        assert 'ARM_PUBLIC_BINARY' in str(exc)
    return {'status':'PASS','unit_fixture_only':True,
            'minimum_two_sided_seed_cluster_p':.25,
            'CKAD20_scientific_claim_supported':False,
            'sensitivity':sensitivity()}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--input',type=Path)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    if args.self_test:
        data=self_test()
    elif args.input:
        data=evaluate(json.loads(args.input.read_text(encoding='utf-8')))
    else:
        p.error('--input or --self-test required')
    if args.output:
        args.output.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    print(json.dumps(data,sort_keys=True))
