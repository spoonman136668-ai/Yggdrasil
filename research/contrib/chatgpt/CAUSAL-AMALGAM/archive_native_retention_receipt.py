"""Read-only original CKAD25 native/control checkpoint comparison.

Historical receipts are already-consumed synthetic development evidence;
never call an original source, restore a model, or re-label this as held science.
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ZIP_SHA = '64bc0a5970c50e1187d9d6225ed4eed2705504801f1c35f5ec5d8460a354d6ce'
SOURCE_SHA = '20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef'
SCHEMA = 'yggdrasil.ckad25.remote-retention-capacity.result.v1'
SEEDS = (101, 202, 303)
CHECKPOINTS = (0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192)
ARMS = ('coverage_active', 'original_active', 'uniform_random', 'coverage_random',
        'exact_mixture', 'trailing_mle', 'pooled_replay', 'frozen_ckad24')
SCORES = ('reward_sum', 'pooled_brier', 'terminal_brier', 'transition_brier')

# CKAD25 original prereg: phase lengths 48/32/64/48. Held evaluation
# uses world_at(protocol, 0 if count == 0 else count - 1), not the next episode.
SOURCE_PHASE_ENDS = (
    (48, 'context_switch_regime_0'),
    (80, 'terminal_switch_regime_0'),
    (144, 'context_switch_regime_1'),
    (192, 'invariant_regime_0'),
)


def checkpoint_source_phase(count):
    """Source phase used by the original held checkpoint readout."""
    if type(count) is not int or count not in CHECKPOINTS:
        raise ValueError('CHECKPOINT_CLOCK')
    index = 0 if count == 0 else count - 1
    for end, name in SOURCE_PHASE_ENDS:
        if index < end:
            return name
    raise ValueError('SOURCE_PHASE')

def read_archive(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ZIP_SHA:
        raise ValueError('ARCHIVE_SHA_MISMATCH')
    with zipfile.ZipFile(path) as archive:
        expected = {'campaign-result.json'} | {f'seed-{s}-capacity-native.json' for s in SEEDS}
        if set(archive.namelist()) != expected:
            raise ValueError('ARCHIVE_MEMBERS')
        # Python 3.11+ Python's digit cap should not alter validated historical
        # exact-fraction score data when parsing the original archival JSON.
        if hasattr(sys, 'set_int_max_str_digits'):
            sys.set_int_max_str_digits(0)
        report = json.loads(archive.read('campaign-result.json'))
    if (report.get('schema') != SCHEMA or report.get('source_sha256') != SOURCE_SHA
        or report.get('scientific_pass') is not False
        or report.get('accepted_native') is not False
        or report.get('deployment') != 'NONE'):
        raise ValueError('ORIGINAL_SCIENCE_BOUNDARY')
    if sorted(s.get('seed') for s in report.get('seeds', [])) != list(SEEDS):
        raise ValueError('ORIGINAL_SEED_SET')
    return report

def audit(report):
    score_parity = {k: 0 for k in SCORES}
    for seed in report['seeds']:
        if seed['source_seed'] != seed['seed'] + 56000:
            raise ValueError('SOURCE_SEED_OFFSET')
        if [p['count'] for p in seed['stream']] != list(CHECKPOINTS):
            raise ValueError('CHECKPOINT_CLOCK')
        for p in seed['stream']:
            evaluation = p['evaluation']
            if set(evaluation) != set(ARMS):
                raise ValueError('ARM_SET')
            for arm in ARMS:
                value = evaluation[arm]
                if value['episodes'] != 96 or not 0 <= value['reward_sum'] <= 96:
                    raise ValueError('HELD_RECEIPT_SCOPE')
            for k in SCORES:
                score_parity[k] += evaluation['coverage_active'][k] == evaluation['exact_mixture'][k]
    checkpoints = {}
    for count in (80, 96, 144, 160, 176, 192):
        points = [next(x for x in seed['stream'] if x['count'] == count)['evaluation']
                  for seed in report['seeds']]
        rewards = {arm: sum(x[arm]['reward_sum'] for x in points) for arm in ARMS}
        best = max(rewards[a] for a in ARMS if a != 'coverage_active')
        checkpoints[str(count)] = {
            'cohort_source_phase': checkpoint_source_phase(count),
            'held_scored_episodes': 288,
            'reward_by_arm': rewards,
            'strongest_control_reward': best,
            'candidate_minus_best_control_rewards': rewards['coverage_active'] - best,
        }
    return {'schema': 'yggdrasil.ckad25.archive-native-retention-receipt.v1',
            'original_experiment': 'CKAD25, already consumed development',
            'exact_native_vs_exact_control_parity': score_parity,
            'parity_denominator': 39,
            'checkpoints': checkpoints,
            'scientific_gain_verified': False,
            'original_world_first_use': 0,
            'native_checkpoint_updates': 0,
            'deployment': 'NONE'}

def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: archive_native_retention_receipt.py ARCHIVE.ZIP')
    print(json.dumps(audit(read_archive(sys.argv[1])), sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
