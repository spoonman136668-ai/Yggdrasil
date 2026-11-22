"""Reseal deliberately corrupted CKAD26 receipts and require semantic rejection."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ckad26_negative_reference',HERE/'independent_audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def verify(root=HERE):
    start = time.monotonic()
    result = json.loads((root/'campaign-result.json').read_bytes())
    mutations = [
        ('gate','FROZEN_METRICS_GATES',lambda r:r['development_gates'].__setitem__(
            'seed101_gain_vs_product',not r['development_gates']['seed101_gain_vs_product'])),
        ('strong_control','HELD_101_0_trailing_mle',lambda r:r['seeds'][0]['stream'][0]['evaluation']['trailing_mle'].__setitem__(
            'reward_sum',r['seeds'][0]['stream'][0]['evaluation']['trailing_mle']['reward_sum']+1)),
        ('ablation','HELD_101_0_prior_only',lambda r:r['seeds'][0]['stream'][0]['evaluation']['prior_only'].__setitem__(
            'pooled_brier',[0,1])),
        ('monitor','MONITOR_TRACE',lambda r:r['seeds'][0]['stream'][0]['monitors']['refresh_no_alarm'].__setitem__('score',[2,1])),
        ('checkpoint','CHECKPOINT_REPLAY_101_0',lambda r:r['seeds'][0]['stream'][0].__setitem__('checkpoint_sha256','0'*64)),
        ('capacity','CAPACITY_PROBE',lambda r:r['seeds'][0]['capacity_probe'].__setitem__('admitted',True)),
        ('initial','PARENT_PIN',lambda r:r['seeds'][0].__setitem__('parent_checkpoint_sha256','0'*64)),
        ('cached_receipts','RECEIPT_PIN',lambda r:r['seeds'][0].__setitem__('receipt_state_sha256','0'*64)),
    ]
    rejected = {}
    for name,label,mutate in mutations:
        changed = copy.deepcopy(result)
        mutate(changed)
        changed['stable_sha256'] = audit.sha(audit.canonical(audit.stable(changed)))
        expected = 'CKAD26_INDEPENDENT_'+label
        try:
            if name=='gate':
                audit.verify_gates(changed)
            elif name=='capacity':
                case = changed['seeds'][0]
                raw = (root/case['final_checkpoint_name']).read_bytes()
                ledger = json.loads(json.loads(raw)['experience_ascii'])['episodes']
                audit.verify_capacity(case,ledger,audit.sha(raw))
            else:
                with tempfile.TemporaryDirectory(prefix='ckad26-negative-') as temporary:
                    directory = Path(temporary)
                    (directory/'campaign-result.json').write_bytes(audit.canonical(changed))
                    for checkpoint in root.glob('seed-*-refresh-native.json'):
                        (directory/checkpoint.name).write_bytes(checkpoint.read_bytes())
                    audit.audit(directory)
        except RuntimeError as exc:
            if str(exc)!=expected:
                raise AssertionError(f'{name}: expected {expected}; received {exc}') from exc
            rejected[name] = expected
        else:
            raise AssertionError('Altered CKAD26 evidence accepted: '+name)
    return {'negative_controls':'PASS','rejections':rejected,'semantic_hash_recomputed':True,
            'native_imports':0,'new_primary_observations':0,'wall_seconds':time.monotonic()-start}


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',nargs='?',type=Path,default=HERE)
    args = parser.parse_args()
    print(json.dumps(verify(args.directory),sort_keys=True))
