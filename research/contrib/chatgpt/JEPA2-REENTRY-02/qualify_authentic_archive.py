"""Read-only parity on existing archived JEPA2-05 trained checkpoint and traces.

No source generator, no new training, no score retuning, no production learner.
"""
import hashlib
import json
import sys
import zipfile
from copy import deepcopy
from pathlib import Path

import numpy as np
from frozen_readout import FrozenHorizonReadout

ARTIFACT = Path(sys.argv[1]) if len(sys.argv) >= 2 else None
MEMBER_SHA = {
    'seed-14071-state.json': '00bd2f7377a6b039e46a28552e689a439f579155355b5c65540c821494b168da',
    'seed-14072-state.json': 'd698fb5050f401ca3481fa37ceb8c33c430497b3a97e82caadff69b270441be0',
    'seed-14071-trace.json': 'b141ee7d3f6328e232da2bc053052f55d8f475e017c895fc34a59750f3d625cf',
    'seed-14072-trace.json': '7e72e0882909d27688190b709a998279168164da198509a95e2ba139da8702e8',
}
EXPECTED_FINAL_SHA = {14071: '646058e49adf75d2cf74b16b901e801b24ea38f017a717d68fe65a93ab4cad9e',
                      14072: 'ef8e1b6daa9b0349d675aee6c30a79d759d6e21c460b5fc900461417c1970609'}
EXPECTED_OLD_SHA = {14071: 'c9bd78d4636d9b71e5bca42a3cf52afcfb9a58267d83c3e7727deceab667e690',
                    14072: '724cc155863d2ac88265ddb3006a90702049ed54a53e52881939f063c002a31b'}
OLD_COUNT = {14071: 1006, 14072: 981}

def read(z, name):
    raw = z.read(name)
    assert len(raw) and hashlib.sha256(raw).hexdigest() == MEMBER_SHA[name], name
    return json.loads(raw)

def episodes(model):
    o = json.loads(model['native_ascii'])
    for _ in range(5):
        if 'episodes' in o:
            return tuple((e[0], tuple(tuple(v) for v in e[1]), *e[2:]) for e in o['episodes'])
        key = next((x for x in ('base_ascii', 'native_ascii') if isinstance(o.get(x), str)), None)
        assert key, 'ledger not found'
        o = json.loads(o[key])
    assert False, 'ledger nesting'


def canonical(model):
    return json.dumps(model, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')

if ARTIFACT is None or not ARTIFACT.is_file():
    raise SystemExit('usage: qualify_authentic_archive.py PATH_TO_ORIGINAL_ARCHIVE.zip [OUTPUT_REPORT.json]')

with zipfile.ZipFile(ARTIFACT) as z:
    report = {'workflow_run': 44492525160, 'artifact_id': 14513033616,
              'original_source': '7b0d9fd8c16b8e0433a632666cec88d8d008c19f',
              'candidate_adapter_blob': '5611f656a91e45eaeed46022e41d1050d5ff87a0',
              'runs': [], 'basis': 'original consumed development archive, read-only'}
    for seed in (14071, 14072):
        state = read(z, f'seed-{seed}-state.json')
        trace = read(z, f'seed-{seed}-trace.json')
        raw_checkpoint = state['model_ascii'].encode('ascii')
        assert hashlib.sha256(raw_checkpoint).hexdigest() == state['model_sha256'] == EXPECTED_FINAL_SHA[seed]
        assert state['old_model_sha256'] == EXPECTED_OLD_SHA[seed]
        model = json.loads(state['model_ascii'])
        history = episodes(model)
        assert len(history) == OLD_COUNT[seed] + 16, (len(history), seed)
        assert len(trace) == 14
        final = FrozenHorizonReadout(raw_checkpoint, state['model_sha256'])
        assert final.sha256 == EXPECTED_FINAL_SHA[seed]
        # Input heads from the *original* archived frozen weight arrays, not a newly trained head.
        # The checkpoint envelope is a test-only derived composition; the original final
        # checkpoint was already separately cold-parsed above with its exact SHA.
        test_model = deepcopy(model)
        test_model['sensory'], test_model['reward'] = state['frozen_heads']
        raw_frozen = canonical(test_model)
        frozen = FrozenHorizonReadout(raw_frozen, hashlib.sha256(raw_frozen).hexdigest())
        passed, rejected, maxerr = 0, 0, 0.0
        frozen_snapshot = raw_frozen
        final_snapshot = raw_checkpoint
        for i, t in enumerate(trace):
            assert t['start'] == i and len(t['forecasts']['frozen']) == 6
            # Each prequential forecast uses old witnessed prefix + first k new observations.
            start = OLD_COUNT[seed] + i
            public_views = history[start][1]
            old_and_seen = history[:start]
            plan = tuple(tuple(pair) for pair in t['announced_plan'])
            compatible = public_views[0][0] == public_views[1][0]
            if compatible:
                p = frozen.forecast(public_views, plan, old_and_seen)
                diff = max(abs(float(x)-float(y)) for x, y in zip(p, t['forecasts']['frozen']))
                maxerr = max(maxerr, diff)
                assert diff <= 1e-12, (seed, i, diff)
                passed += 1
            else:
                try:
                    frozen.forecast(public_views, plan, old_and_seen)
                except ValueError as e:
                    assert str(e) == 'JEPA_REENTRY_COORDINATE_INCOMPATIBLE', str(e)
                else:
                    raise AssertionError((seed, i, 'incompatible view unexpectedly admitted'))
                rejected += 1
        assert raw_frozen == frozen_snapshot and raw_checkpoint == final_snapshot
        assert passed + rejected == 14
        # Final original updated (not frozen) head must also be functional and finite
        index = next(i for i in range(14) if history[OLD_COUNT[seed]+i][1][0][0] == history[OLD_COUNT[seed]+i][1][1][0])
        t = trace[index]; start = OLD_COUNT[seed]+index
        final_prob = final.forecast(history[start][1], tuple(tuple(a) for a in t['announced_plan']), history[:start])
        assert len(final_prob) == 6 and all(0. <= p <= 1. for p in final_prob)
        # Negative custody control on the original exact archive
        try:
            FrozenHorizonReadout(raw_checkpoint + b' ', state['model_sha256'])
        except ValueError as e:
            assert str(e) == 'JEPA_REENTRY_CHECKPOINT_PIN'
        else:
            raise AssertionError('original pinned checkpoint tamper incorrectly admitted')
        report['runs'].append({'old_seed': seed, 'archived_history_count': len(history),
                               'source_checked_forecasts': 14, 'admitted_and_matched': passed,
                               'incompatible_correctly_rejected': rejected,
                               'max_abs_delta_admitted': maxerr,
                               'trained_original_final_checkpoint_loaded': True,
                               'frozen_heads_from_original_archive': True,
                               'checkpoint_sha256': state['model_sha256'],
                               'old_checkpoint_sha256': state['old_model_sha256'],
                               'native_parent_preserved': True, 'score_type': 'consumed_archive_not_new_science'})
    report['total_admitted'] = sum(r['admitted_and_matched'] for r in report['runs'])
    report['total_rejected'] = sum(r['incompatible_correctly_rejected'] for r in report['runs'])
    report['development_science_pass'] = False
    if len(sys.argv) >= 3:
        Path(sys.argv[2]).write_text(json.dumps(report, sort_keys=True, indent=2)+'\n')
    print(json.dumps(report, sort_keys=True, indent=2))
