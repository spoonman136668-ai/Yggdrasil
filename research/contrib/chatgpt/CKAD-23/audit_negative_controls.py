"""Reject altered CKAD23 evidence even when its semantic hash is recomputed."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import time

HERE = Path(__file__).resolve().parent
AUDITOR = HERE / 'independent_audit.py'
if (HERE / 'independent_audit_enhanced.py').is_file():
    AUDITOR = HERE / 'independent_audit_enhanced.py'
spec = importlib.util.spec_from_file_location('ckad23_negative_reference', AUDITOR)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def verify(root=HERE):
    start = time.monotonic()
    result = json.loads((root / 'campaign-result.json').read_bytes())
    tests = [
        ('gate', 'CKAD23_ALL_ARM_FROZEN_METRICS_GATES',
         lambda r: r['development_gates'].__setitem__('held_gain_vs_no_reset',
                    not r['development_gates']['held_gain_vs_no_reset'])),
        ('comparator', 'CKAD23_ALL_ARM_HELD_101_0_no_reset',
         lambda r: r['seeds'][0]['stream'][0]['evaluation']['no_reset'].__setitem__(
             'reward_sum', r['seeds'][0]['stream'][0]['evaluation']['no_reset']['reward_sum'] + 1)),
        ('random_monitor', 'CKAD23_ALL_ARM_MONITOR_TRACE',
         lambda r: r['seeds'][0]['stream'][0].__setitem__('random_score', [2,1])),
        ('state', 'CKAD23_ALL_ARM_CHECKPOINT_REPLAY_101_0',
         lambda r: r['seeds'][0]['stream'][0].__setitem__('checkpoint_sha256', '0'*64)),
    ]
    rejections = {}
    for name, label, mutate in tests:
        damaged = copy.deepcopy(result)
        mutate(damaged)
        damaged['stable_sha256'] = audit.sha(audit.canonical(audit.reference.stable(damaged)))
        try:
            if name == 'gate':
                audit.verify_gates(damaged)
            else:
                with tempfile.TemporaryDirectory(prefix='ckad23-audit-negative-') as temporary:
                    output = Path(temporary)
                    (output / 'campaign-result.json').write_text(json.dumps(damaged), encoding='ascii')
                    # Copy retained byte streams for portability on Windows;
                    # never execute code from an artifact directory.
                    for item in root.glob('seed-*-stream-native.json'):
                        (output / item.name).write_bytes(item.read_bytes())
                    audit.audit(output)
        except RuntimeError as exc:
            if str(exc) != label:
                raise AssertionError(f'{name}: expected {label}, received {exc}') from exc
            rejections[name] = label
        else:
            raise AssertionError(f'Altered evidence accepted: {name}')
    return {'negative_controls':'PASS', 'rejections':rejections,
            'semantic_hash_recomputed':True, 'native_imports':0,
            'new_primary_observations':0, 'wall_seconds':time.monotonic()-start}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', type=Path, default=HERE)
    arguments = parser.parse_args()
    print(json.dumps(verify(arguments.directory), sort_keys=True))
