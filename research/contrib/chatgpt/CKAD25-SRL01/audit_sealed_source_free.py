"""Independent read-only integrity audit of the ONE frozen SRL01 source-free trial.

Does not import the model/scorer, regenerate outcomes, execute interventions, or
promote the synthetic result as an original-world or scientific pass.
"""
from __future__ import annotations
import hashlib
import json
import lzma
from pathlib import Path
import sys

ARCHIVE_SHA256 = '088deac2fe3421e92b75d6df95ae2080b0840e1edd2397a69488c7973b7b018e'
RAW_SHA256 = 'e15d86a168d3a788c6a7d9e9adbcac3d46db75da7075cae4f61715280aa04b5f'
ARCHIVE_BYTES = 18972
RAW_BYTES = 299869
ARMS = ('native_beta','conventional_beta','learned_shared_risk',
        'independent_exact_joint_bayes','dirichlet_positives','beta_trailing_2','fixed','random')
PRIMARY_SOURCE_COMMIT = '7b513cc388406bdd7ba47234ca90a887dc7c6648'


def require(value, name):
    if not value:
        raise ValueError('SRL01_SEALED_' + name)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def verify(path):
    zipped = Path(path).read_bytes()
    require(len(zipped)==ARCHIVE_BYTES and digest(zipped)==ARCHIVE_SHA256,
            'ORIGINAL_ARCHIVE_PIN')
    raw = lzma.decompress(zipped, format=lzma.FORMAT_XZ,
                          memlimit=256*1024*1024)
    require(len(raw)==RAW_BYTES and digest(raw)==RAW_SHA256,
            'ORIGINAL_RAW_BYTES_PIN')
    data=json.loads(raw)
    require(data['schema']=='yggdrasil.ckad25.srl01.dev-result.v1', 'SCHEMA')
    require(data['parent']=='655f13033c7ce8e9699af697437fcb9bd5a06f1e',
            'EXACT_PARENT')
    require(data['classification']=='DEV_GO_FOCUSED_ONLY' and
            data['source_free_dev'] is True and
            data['scientific_gain_verified'] is False and
            data['source_first_use']=='NONE' and
            data['controls_fully_matched'] is True and
            data['consumed_primary_trials']==1 and
            data['native_true_checkpoint']=='NOT_RUN' and
            data['full_linux_windows_regression']=='NOT_RUN', 'HONEST_DISPOSITION')
    station=[530001+37*i for i in range(48)]
    negative=[540001+41*i for i in range(24)]
    require(data['stationary_seeds']==station and
            data['negative_seeds']==negative and
            len(set(station+negative))==72, 'FROZEN_SEEDS')
    require(len(data['per_seed_stationary'])==48 and
            len(data['per_seed_negative'])==24 and
            data['witnessed_train_actions']==432 and
            data['evaluated_target_action_budget_per_arm']==4608, 'ACTION_BUDGET')
    require(len(data['gates'])==6 and all(v is True for v in data['gates'].values()),
            'FROZEN_DEV_GATES')
    assert all(data['stationary'][a]==data['stationary'][b] for a,b in
               [('native_beta','conventional_beta'),
                ('learned_shared_risk','independent_exact_joint_bayes')])
    assert all(data['negative_no_stable_mapping'][a]==data['negative_no_stable_mapping'][b]
               for a,b in [('native_beta','conventional_beta'),
                           ('learned_shared_risk','independent_exact_joint_bayes')])
    require(data['stationary']['native_beta']['detected']==1157 and
            data['stationary']['learned_shared_risk']['detected']==1202 and
            data['negative_no_stable_mapping']['native_beta']['detected']==396 and
            data['negative_no_stable_mapping']['learned_shared_risk']['detected']==387,
            'REFERENCE_DETECTION_COUNTS')
    for rows, seeds, negative_condition in ((data['per_seed_stationary'],station,False),
                                            (data['per_seed_negative'],negative,True)):
        for row,seed in zip(rows,seeds):
            require(row['seed']==seed and
                    row['checkpoint_cold_parity'] is True and
                    row['source_history_witness_actions']==6 and
                    row['synthetic_negative_no_stable_role'] is negative_condition,
                    'EVIDENCE_AND_READBACK')
            history=row['source_history']
            require(len(history)==3 and all(len(v)==2 for v in history)
                    and all(len(w)==2 and type(w[0]) is int and type(w[1]) is int
                            and 0<=w[0]<4 and w[1] in (0,1)
                            for world in history for w in world),
                    'SOURCE_OBSERVATION_SHAPE')
            require(digest(canonical(history))==row['source_history_sha256'],
                    'HISTORICAL_OBSERVATION_HASH')
            require(set(row['score'])==set(ARMS) and set(row['forecast'])==set(ARMS)
                    and set(row['selected'])==set(ARMS), 'COMPLETE_MATCHED_ARMS')
            for name in ARMS:
                require(len(row['selected'][name])==2 and
                        len(set(row['selected'][name]))==2 and
                        set(row['selected'][name]).issubset({0,1,2,3}) and
                        row['score'][name]['charged_target_actions']==64 and
                        len(row['forecast'][name])==4,
                        'EQUAL_ACTION_AND_FORECAST_BUDGET')
            require(row['forecast']['learned_shared_risk']==
                    row['forecast']['independent_exact_joint_bayes'] and
                    row['selected']['learned_shared_risk']==
                    row['selected']['independent_exact_joint_bayes'],
                    'STRONG_CONVENTIONAL_PARITY')
    return {
        'schema':'yggdrasil.ckad25.srl01.sealed-original-read-only-audit.v1',
        'source_free_original_raw_sha256':RAW_SHA256,
        'source_free_original_raw_bytes':RAW_BYTES,
        'compressed_archive_sha256':ARCHIVE_SHA256,
        'compressed_archive_bytes':ARCHIVE_BYTES,
        'original_source_frozen_commit':PRIMARY_SOURCE_COMMIT,
        'cohorts_checked':72,
        'public_training_witnesses':432,
        'full_equal_budget_policy_worlds':72*32,
        'arms_checked':len(ARMS),
        'conventional_exact_tie_verified':True,
        'preserves_negative_no_mapping':True,
        'frozen_dev_disposition':'DEV_GO_FOCUSED_ONLY',
        'new_source_episodes':0,'new_primary_trials':0,
        'native_checkpoint_test_executed':False,
        'scientific_gain_verified':False,
        'deployment':'NONE',
        'result':'SEALED_SOURCE_FREE_ORIGINAL_INTEGRITY_PASS',
    }


def selftest(archive):
    import tempfile
    valid=verify(archive)
    require(valid['result']=='SEALED_SOURCE_FREE_ORIGINAL_INTEGRITY_PASS',
            'SELFTEST_VALID_RECEIPT')
    original=bytearray(Path(archive).read_bytes())
    with tempfile.TemporaryDirectory() as folder:
        target=Path(folder)/'corrupt-original.json.xz'
        tampered=original.copy();tampered[len(tampered)//2] ^= 1
        target.write_bytes(tampered)
        try:
            verify(target)
        except ValueError as e:
            require(str(e)=='SRL01_SEALED_ORIGINAL_ARCHIVE_PIN',
                    'WRONG_TAMPER_REJECTION')
        else:
            raise ValueError('TAMPERED_ARCHIVE_ACCEPTED')
        target.write_bytes(original[:-1])
        try:
            verify(target)
        except ValueError as e:
            require(str(e)=='SRL01_SEALED_ORIGINAL_ARCHIVE_PIN',
                    'WRONG_TRUNCATION_REJECTION')
        else:
            raise ValueError('TRUNCATED_ARCHIVE_ACCEPTED')
    return {'test_count':3,'passed':3,'original_sha256':RAW_SHA256,
            'archive_sha256':ARCHIVE_SHA256,'source_free':True,
            'new_primary_trial':False,'native_test_executed':False}


if __name__=='__main__':
    is_test='--selftest' in sys.argv
    paths=[x for x in sys.argv[1:] if x!='--selftest']
    source = (Path(paths[0]) if paths else
              Path(__file__).resolve().parent/'original-source-free-result.json.xz')
    print(json.dumps(selftest(source) if is_test else verify(source),
                     sort_keys=True, indent=2))
