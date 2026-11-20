"""Reconstruct byte-identical CKAD22 historical checkpoints, without executing a learner.

Run only against already-consumed original GitHub Actions artifacts. No source actors,
checkpoint mutation, new observations, inference, training, or remote execution.
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

CKAD21_SHA = '2addc338ebaba21115d5700f6a64b1612a4be7099267b7ec1df7d84d1530c293'
CKAD22_SHA = '90362c075154ab936fc2e0a82716fbe5bd875585cd89aeed0b08b32831560fc4'
CKAD22_WINDOWS_SHA = 'e4fea224001f0b850a10cd1954e85262a41364b0f09734caf07175c9e3caa6f7'
SOURCE_SHA = '20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef'
SEEDS = (101, 202, 303)
SCHEDULE = (352, 384, 416, 448)


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def open_pinned(path, expected_sha):
    raw = Path(path).read_bytes()
    if digest(raw) != expected_sha:
        raise ValueError('ARCHIVE_SHA_MISMATCH')
    return zipfile.ZipFile(path)


def load_report(z, expected_seeds=SEEDS):
    report = json.loads(z.read('campaign-result.json'))
    if sorted(s['seed'] for s in report['seeds']) != list(expected_seeds):
        raise ValueError('SEED_SET_MISMATCH')
    if report.get('source_sha256') != SOURCE_SHA:
        raise ValueError('SOURCE_SHA_MISMATCH')
    return report


def reconstruct(final, old_state, count):
    """Recover historical serialized bytes using the recorded derived-state digest.

    Does NOT independently calculate native derived model state or execute it.
    The original full-checkpoint SHA verifies final byte identity.
    """
    if old_state['experience']['count'] != count:
        raise ValueError('SESSION_COUNT')
    ctx = old_state['experience']['context']['context_start']
    if ctx != count - 32 or old_state['experience']['context']['novel_enabled'] is not True:
        raise ValueError('CONTEXT_BOUNDARY')
    if old_state['experience']['state_sha256'] != old_state['experience']['derived_state_sha256']:
        raise ValueError('DERIVED_DIGEST_DRIFT')
    exp = json.loads(final['experience_ascii'])
    if len(exp['episodes']) != 448 or exp['novel'] is not True or exp['repair'] is not True:
        raise ValueError('FINAL_LEDGER_SCHEMA')
    if exp['schema'] != 'yggdrasil.ckad.native-episode-experience.v3':
        raise ValueError('FINAL_EXPERIENCE_VERSION')
    exp.update(episodes=exp['episodes'][:count], context_start=ctx,
               state_sha256=old_state['experience']['state_sha256'])
    raw = canonical({**final, 'experience_ascii': canonical(exp).decode('ascii')})
    if len(raw) != old_state['checkpoint_bytes']:
        raise ValueError('HISTORICAL_CHECKPOINT_LENGTH')
    if digest(raw) != old_state['checkpoint_sha256']:
        raise ValueError('HISTORICAL_CHECKPOINT_SHA')
    return raw


def audit(parent_zip, child_zip, windows_zip=None):
    results = []
    with open_pinned(parent_zip, CKAD21_SHA) as zp, open_pinned(child_zip, CKAD22_SHA) as zc:
        rp, rc = load_report(zp), load_report(zc)
        if rc.get('scientific_pass') is not False or rc.get('accepted_native') is not False:
            raise ValueError('SCIENCE_BOUNDARY')
        if rc.get('deployment') != 'NONE':
            raise ValueError('DEPLOYMENT_BOUNDARY')
        if windows_zip is not None:
            with open_pinned(windows_zip, CKAD22_WINDOWS_SHA) as zw:
                rw = load_report(zw)
                if rw['stable_sha256'] != rc['stable_sha256']:
                    raise ValueError('CROSS_OS_SEMANTIC_MISMATCH')
                windows_by_seed = {s['seed']: s for s in rw['seeds']}
        else:
            windows_by_seed = None
        parents = {s['seed']: s for s in rp['seeds']}
        for s in rc['seeds']:
            seed = s['seed']
            parent = parents[seed]
            if s['parent_checkpoint_sha256'] != parent['final_checkpoint_sha256']:
                raise ValueError('PARENT_REPORT_PIN')
            prior_raw = zp.read(parent['final_checkpoint_name'])
            full_raw = zc.read(s['final_checkpoint_name'])
            if digest(prior_raw) != parent['final_checkpoint_sha256']:
                raise ValueError('PARENT_MEMBER_SHA')
            if digest(full_raw) != s['final_checkpoint_sha256']:
                raise ValueError('FINAL_MEMBER_SHA')
            original = json.loads(full_raw)
            original_prior = json.loads(prior_raw)
            if canonical(original) != full_raw or canonical(original_prior) != prior_raw:
                raise ValueError('NONCANONICAL_SOURCE')
            if any(original[k] != original_prior[k] for k in original if k != 'experience_ascii'):
                raise ValueError('NONEXPERIENCE_FIELD_DRIFT')
            first = json.loads(original_prior['experience_ascii'])['episodes']
            final = json.loads(original['experience_ascii'])['episodes']
            if len(first) != 320 or len(final) != 448 or final[:320] != first:
                raise ValueError('PARENT_WITNESS_PREFIX')
            if len(s['sessions']) != 4 or [q['session'] for q in s['sessions']] != list(range(4)):
                raise ValueError('SESSION_SCHEDULE')
            for i, count in enumerate(SCHEDULE):
                state = s['sessions'][i]['states']['novel_active']
                if windows_by_seed is not None and state != windows_by_seed[seed]['sessions'][i]['states']['novel_active']:
                    raise ValueError('CROSS_OS_SAVED_STATE')
                rec = reconstruct(original, state, count)
                results.append({'seed': seed, 'session': i, 'witnesses': count,
                                'checkpoint_sha256': digest(rec), 'checkpoint_bytes': len(rec),
                                'exact_original_sha256_match': True,
                                'pre_return_384': i == 1})
    return {'schema': 'ckad22.original-intermediate-recovery.v1', 'results': results,
            'historical_exact_checkpoints_verified': len(results),
            'pre_return_384_checkpoints_verified': sum(x['pre_return_384'] for x in results),
            'derived_state_hash_independently_recomputed': False,
            'original_native_model_executed_now': False,
            'source_first_use': 0, 'scientific_gain_verified': False, 'deployment': 'NONE'}


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit('usage: python ckad22_exact_intermediate.py ckad21.zip ckad22.zip [ckad22-windows.zip]')
    print(json.dumps(audit(*sys.argv[1:]), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
