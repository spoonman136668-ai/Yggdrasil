"""CAID-05 read-only ORIGINAL-ARCHIVE audit. No original-world actor or native learner.

Exploratory/retrospective only; no first-use, held evaluation or scientific gain.
Usage: python archived_beta_audit.py github-actions-artifact-14517860401.zip
"""
from collections import defaultdict
from fractions import Fraction
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from pathlib import Path
import sys
from zipfile import ZipFile

RUN_ID = 44499793023
ARTIFACT_ID = 14517860401
ZIP_SHA = 'b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d'
JOINT_SHA = '576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8'
NATIVE_SHA = '5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d'
EXPERIENCE_SHA = '9158254b80f147d7eb7516d630f6003441df4b8373375b994d864ee1d55568f4'
LEDGER_SHA = '55697acbbe953b5cf6878cecfd3286b068f665fc3c6f78334d241466c4beb274'
SCALE = 1_000_000
WINDOWS = {'earliest':[0,32], 'midpoint':[496,528], 'latest':[992,1024]}


def digest(raw):
    return sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')


def brier(counts, y):
    failures, successes = counts
    q = round(Fraction(successes + 1, failures + successes + 2) * SCALE)
    return (q - y * SCALE) ** 2


def metrics(archive):
    archive = Path(archive)
    zipbytes = archive.read_bytes()
    assert digest(zipbytes) == ZIP_SHA, 'ARCHIVE_SHA_MISMATCH'
    with ZipFile(archive) as z:
        jointbytes = z.read('amalgam-joint-state.json')
    assert digest(jointbytes) == JOINT_SHA, 'JOINT_SHA_MISMATCH'
    joint = json.loads(jointbytes)
    nativebytes = joint['native_ascii'].encode('ascii')
    assert digest(nativebytes) == NATIVE_SHA, 'NATIVE_SHA_MISMATCH'
    native = json.loads(nativebytes)
    ebytes = native['experience_ascii'].encode('ascii')
    assert digest(ebytes) == EXPERIENCE_SHA, 'EXPERIENCE_SHA_MISMATCH'
    experience = json.loads(ebytes)
    assert experience['schema'] == 'yggdrasil.ckad.native-episode-experience.v6'
    raw = experience['episodes']
    assert digest(canonical(raw)) == LEDGER_SHA, 'LEDGER_SHA_MISMATCH'
    assert len(raw) == len({x[0] for x in raw}) == 1025, 'REPLAY_OR_WRONG_COUNT'
    mismatch = [sum(x[1][0][a] != x[1][1][a] for x in raw[:8]) for a in (0,1)]
    assert mismatch[0] != mismatch[1], 'PROJECTION_NOT_LEARNED'
    selected = int(mismatch[1] < mismatch[0])
    pair_conflicts = sum(x[1][0][selected] != x[1][1][selected] for x in raw)
    assert pair_conflicts == 0, 'INCONSISTENT_PAIRED_CONTEXT'
    rows = []
    for identifier, views, x1, s2, x2, y in raw:
        for bit in (*views[0],*views[1],x1,s2,x2,y):
            assert type(bit) is int and bit in (0,1), 'NONBINARY_PUBLIC_EVENT'
        rows.append(((views[0][selected],x1,s2,x2), y))

    counts = defaultdict(lambda:[0,0])
    preq = []
    for key,y in rows:
        preq.append(brier(counts[key],y))  # predict BEFORE witnessing this reward
        counts[key][y] += 1
    assert len(counts) == 16, 'ORIGINAL_PUBLIC_CELL_COVERAGE'

    # Retrospective control only. Even LOO sees events later in time, so it is
    # NOT a prospective predictor or a performance win.
    loo = []
    for key,y in rows:
        f,s = counts[key]
        loo.append(brier([f-(1-y),s-y],y))

    fixed_fit = defaultdict(lambda:[0,0])
    for key,y in rows[:512]:
        fixed_fit[key][y] += 1
    fixed_eval = [brier(fixed_fit[key],y) for key,y in rows[512:]]

    def mean(scores):
        with localcontext() as ctx:
            ctx.prec = 40
            return format(Decimal(sum(scores)) / Decimal(len(scores) * SCALE * SCALE), '.15f')
    return {
      'schema':'yggdrasil.caid05.original-archive-conventional-baselines.v1',
      'classification':'EXPLORATORY_UNPREREGISTERED_RETROSPECTIVE_NOT_HELD',
      'original_run_id':RUN_ID,'original_artifact_id':ARTIFACT_ID,
      'original_ci_head_sha':'e9aa921c57dca836c06c7125e52229cce728620a',
      'zip_sha256':ZIP_SHA,'joint_sha256':JOINT_SHA,'native_sha256':NATIVE_SHA,
      'experience_sha256':EXPERIENCE_SHA,'source_ledger_sha256':LEDGER_SHA,
      'episode_count':len(rows),'projection':selected,
      'first_8_mismatch_counts':mismatch,'paired_context_conflicts':pair_conflicts,
      'reward_public_cells_observed':len(counts),'reward_public_cells_possible':16,
      'reward_cell_support_range':[min(sum(z) for z in counts.values()),max(sum(z) for z in counts.values())],
      'prequential_reward_brier_all_1025':mean(preq),
      'prequential_reward_brier_windows':{k:mean(preq[a:b]) for k,(a,b) in WINDOWS.items()},
      'retrospective_leave_one_out_brier_windows':{k:mean(loo[a:b]) for k,(a,b) in WINDOWS.items()},
      'fixed_first_512_beta_reward_brier_remaining_513':mean(fixed_eval),
      'held_out':False,'matched_native_head_training':False,
      'native_class_imported':False,'protected_world_stepped':False,
      'scientific_gain_verified':False,'deployed':False,
    }

if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('Usage: python archived_beta_audit.py <original-artifact-zip>')
    print(json.dumps(metrics(sys.argv[1]),indent=2,sort_keys=True))
