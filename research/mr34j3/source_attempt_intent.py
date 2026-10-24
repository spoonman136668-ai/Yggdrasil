"""MR34J3J prospective source-attempt inventory; entirely SOURCE-FREE.

Never reserves a source, imports gymnasium/minigrid, dispatches work, or changes
external state. Exact evaluator commit and platform instance remain unbound until
CKB-plane source custodian issues an authoritative signed lease.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter

SOURCE_SHA = '7f5853792ea7f04f75614661006d87fcf949f26d'
ENV = 'MiniGrid-MemoryS7-v0'
HOSTS = ('ubuntu-24.04', 'windows-2025')
PHASE_ARMS = {
    'PREFLIGHT': ('public_rule',),
    'FIT': ('learned_trace17', 'conventional_rnn57', 'observation_only3'),
    'DEV': ('learned_trace17', 'conventional_rnn57', 'observation_only3', 'public_rule', 'fit_donor_ablation'),
    'HELD': ('learned_trace17', 'conventional_rnn57', 'observation_only3', 'public_rule', 'fit_donor_ablation'),
}
SEED_TOTALS = {'PREFLIGHT': 16, 'FIT': 768, 'DEV': 128, 'HELD': 256}


def seeds(phase: str) -> tuple[int, ...]:
    if phase == 'PREFLIGHT':
        return tuple(3_000_000 + e for e in range(16))
    if phase == 'FIT':
        return tuple(sorted(3_100_000+100*c+e for c in range(1, 25) for e in range(32)))
    if phase == 'DEV':
        return tuple(sorted(3_200_000+100*c+e for c in range(1, 9) for e in range(16)))
    if phase == 'HELD':
        return tuple(sorted(3_300_000+100*c+e for c in range(1, 17) for e in range(16)))
    raise ValueError('UNKNOWN_PHASE')


def attempts():
    """Each host/phase/seed/arm is a separate physical-source intent."""
    for host in HOSTS:
        for phase, arms in PHASE_ARMS.items():
            for seed in seeds(phase):
                for arm in arms:
                    attempt_id = f'MR34J3J|{host}|{phase}|{seed}|{arm}'
                    yield {
                        'scheduled_attempt_id': attempt_id,
                        'source_commit': SOURCE_SHA,
                        'environment_id': ENV,
                        'host_role': host,
                        'phase': phase,
                        'seed': seed,
                        'arm_id': arm,
                        'reservation': 'PROPOSED_NOT_RESERVED',
                        'consumed': 'UNVERIFIED',
                    }


def verified_intent() -> dict:
    phase_seeds = {p: set(seeds(p)) for p in PHASE_ARMS}
    assert all(len(s) == SEED_TOTALS[p] for p, s in phase_seeds.items())
    assert sum(map(len, phase_seeds.values())) == len(set.union(*phase_seeds.values())) == 1168
    counts = Counter()
    ids = set()
    digest = hashlib.sha256()
    for row in attempts():
        assert row['reservation'] == 'PROPOSED_NOT_RESERVED'
        assert row['consumed'] == 'UNVERIFIED'
        assert row['scheduled_attempt_id'] not in ids, 'REPEATED_ATTEMPT_ID'
        ids.add(row['scheduled_attempt_id'])
        counts[(row['host_role'], row['phase'], row['arm_id'])] += 1
        payload = json.dumps(row, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode('ascii')
        digest.update(payload + b'\n')
    assert len(ids) == 8480
    for host in HOSTS:
        for phase, arms in PHASE_ARMS.items():
            for arm in arms:
                assert counts[(host, phase, arm)] == SEED_TOTALS[phase]
        assert sum(c for (h, _, _), c in counts.items() if h == host) == 4240
    return {
        'schema': 'mr34j3j.prospective-attempt-intent.v1',
        'admission': 'NO', 'execution_authority': False,
        'scientific_first_use': 'NOT_CLAIMED',
        'original_source_resets': 0,
        'source_sha': SOURCE_SHA, 'environment': ENV,
        'hosts': list(HOSTS),
        'distinct_seed_values': 1168,
        'proposed_physical_attempts_per_host': 4240,
        'proposed_total_physical_attempts': 8480,
        'attempt_id_set_sha256': digest.hexdigest(),
        'required_at_execution': ['actual_runner_identity', 'frozen_evaluator_commit',
                                  'independently_verified_source_lease',
                                  'immutable_actual_source_attempt_and_consumption_receipts'],
        'counts_by_host_phase': {
            host: {phase: len(PHASE_ARMS[phase]) * SEED_TOTALS[phase] for phase in PHASE_ARMS}
            for host in HOSTS
        },
        'phase_arm_budget': {p: {'seed_values': SEED_TOTALS[p], 'arms': list(arms)}
                             for p, arms in PHASE_ARMS.items()},
    }


FIT_DONOR_SALT = 341303


def fit_only_donor_index(evaluation_seed: int, *, salt: int = FIT_DONOR_SALT) -> int:
    """Frozen FIT-only donor index for a registered DEV or HELD source attempt.

    No cue, reward, or target observation is consulted. The caller must
    separately supply the 768 public FIT cues sealed before DEV/HELD use.
    PREFLIGHT, FIT, arbitrary/OOV seeds and alternate salts fail closed.
    """
    if type(evaluation_seed) is not int or (evaluation_seed not in seeds('DEV')
                                            and evaluation_seed not in seeds('HELD')):
        raise ValueError('DONOR_INDEX_REQUIRES_REGISTERED_DEV_OR_HELD_SEED')
    if type(salt) is not int or salt != FIT_DONOR_SALT:
        raise ValueError('FIT_DONOR_SALT_DRIFT')
    h = hashlib.sha256(f'{FIT_DONOR_SALT}:{evaluation_seed}'.encode('ascii')).digest()
    return int.from_bytes(h[:8], 'big') % 768


if __name__ == '__main__':
    print(json.dumps(verified_intent(), sort_keys=True, indent=2))
