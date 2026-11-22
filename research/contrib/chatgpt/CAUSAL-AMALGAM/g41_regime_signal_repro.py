"""P0 old-query surprise: read-only, already-consumed source, NOT native training."""
import hashlib
import json
import sys
import zipfile
from fractions import Fraction

ZIPS = (
    'b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d',
    'bb2b689f84caf939b76bea669eff7efb26506b602eed81ac79a81b42efb0a5a6',
)
NATIVE = '5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d'
EPISODE = '9158254b80f147d7eb7516d630f6003441df4b8373375b994d864ee1d55568f4'
JOINT = '576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8'

def load(path, expected):
    data = open(path, 'rb').read()
    assert hashlib.sha256(data).hexdigest() == expected, 'BAD_ARCHIVE'
    with zipfile.ZipFile(path) as z:
        raw = z.read('amalgam-joint-state.json')
    outer = json.loads(raw)
    native = outer['native_ascii'].encode('ascii')
    assert hashlib.sha256(native).hexdigest() == NATIVE, 'BAD_NATIVE'
    model = json.loads(native)
    assert (model['accepted_native'], model['scientific_pass'], model['source_mode']) == (False, False, 'engineering_fixture_only'), 'BAD_STATUS'
    episode = model['experience_ascii'].encode('ascii')
    assert hashlib.sha256(episode).hexdigest() == EPISODE, 'BAD_EPISODE'
    rows = json.loads(episode)['episodes']
    assert len(rows) == 1025, 'BAD_COUNT'
    return hashlib.sha256(raw).hexdigest(), rows

def analyze(paths):
    a, b = (load(p, h) for p, h in zip(paths, ZIPS))
    assert a[0] == JOINT and a[1] == b[1], 'PLATFORM_MISMATCH'
    values = [r[5] for r in a[1] if r[1][0] == [0, 0] and r[2:5] == [0, 0, 0]]
    assert len(values) == 67 and values.count(1) == 61 and values.count(0) == 6, 'BAD_COLLISION'
    zero_run = max_run = 0
    for value in values:
        zero_run = zero_run + 1 if value == 0 else 0
        max_run = max(max_run, zero_run)
    assert max_run == 2, 'BAD_OLD_SEQUENCE'
    tail = Fraction(1, 1)
    for k in range(4):
        tail *= Fraction(7 + k, 69 + k)
    assert tail == Fraction(1, 4899), 'BAD_BETA_MATH'
    return {
        'original_episodes': len(a[1]), 'query_count': len(values),
        'reward_ones': values.count(1), 'reward_zeros': values.count(0),
        'old_max_zero_run': max_run, 'beta_next_four_zero_probability': float(tail),
        'beta_next_four_zero_fraction': str(tail),
        'g41_synthetic_continuation_first_four_end_episode': 1029,
        'g41_native_context_reset_observed_episode': 1035,
        'scientific_gain_verified': False, 'native_training': False, 'source_first_use_actions': 0,
    }

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('usage: python g41_regime_signal_repro.py LINUX_ZIP WINDOWS_ZIP')
    print(json.dumps(analyze(sys.argv[1:]), sort_keys=True, indent=2))
