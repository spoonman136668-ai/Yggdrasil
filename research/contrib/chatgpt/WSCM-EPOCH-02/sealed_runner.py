"""WSCM-EPOCH-02: one-shot journaled NEW-seed source-free follow-up.

Reuses the exact EPOCH-01 learner and controls; changes only fixture seed allowlist.
No protected source calls, production writes, scheduler, seed replay, or tuning.
"""
from __future__ import annotations

import argparse
from hashlib import sha256, sha1
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
ORIGINAL = ROOT / 'research/contrib/chatgpt/WSCM-EPOCH-01/experiment.py'
PREREG = Path(__file__).with_name('prereg.json')
SOURCE_BLOB = 'bc91d9817d4edfcfd16b2b313782270c7ef87c14'
PREREG_BLOB = '6001dd5377e61d948d28aae8eb9e691fdfe47073'
NATIVE_BLOB = '5a18b00a4c4131526e71f51d63dfd9eb9471c81e'
ARTIFACT_SHA = '576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8'
SEEDS = {'B': (94011, 94023), 'C': (95011, 95023)}
ORDER = tuple((scenario, seed) for scenario, values in SEEDS.items() for seed in values)
CONTROLS = ('frozen','continuing','fit_full','trailing32','bocpd32','bayes2')
PER_SEED_SECONDS = 35


def git_blob(raw: bytes) -> str:
    return sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')


def atomic_write(path: Path, content: bytes) -> None:
    if path.exists():
        raise ValueError('EPOCH02_RECEIPT_ALREADY_EXISTS')
    tmp = path.with_name(path.name + '.write')
    if tmp.exists():
        raise ValueError('EPOCH02_INCOMPLETE_WRITE')
    with tmp.open('xb') as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def source_preflight(joint: Path, expected_runner_blob: str) -> dict:
    if git_blob(Path(__file__).read_bytes()) != expected_runner_blob:
        raise ValueError('EPOCH02_RUNNER_DRIFT')
    if git_blob(PREREG.read_bytes()) != PREREG_BLOB:
        raise ValueError('EPOCH02_PREREG_DRIFT')
    if git_blob(ORIGINAL.read_bytes()) != SOURCE_BLOB:
        raise ValueError('EPOCH02_EPOCH01_SOURCE_DRIFT')
    import yggdrasil.native_episode_experience as native
    if git_blob(Path(native.__file__).read_bytes()) != NATIVE_BLOB:
        raise ValueError('EPOCH02_NATIVE_SOURCE_DRIFT')
    if sha256(joint.read_bytes()).hexdigest() != ARTIFACT_SHA:
        raise ValueError('EPOCH02_CHECKPOINT_DRIFT')
    data = json.loads(PREREG.read_bytes())
    if (data['frozen_design']['seeds'] != {k:list(v) for k,v in SEEDS.items()}
            or data['frozen_design']['compute_budget'].split(' ')[0] != str(PER_SEED_SECONDS)):
        raise ValueError('EPOCH02_PREREG_CONTRACT')
    return {'runner_blob':expected_runner_blob,'prereg_blob':PREREG_BLOB,
            'epoch01_source_blob':SOURCE_BLOB,'native_source_blob':NATIVE_BLOB,
            'original_joint_sha256':ARTIFACT_SHA}


def source_model():
    spec = spec_from_file_location('wscm_epoch01_original', ORIGINAL)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.SEEDS != {'B': (92011,92023,92041),'C': (93011,93023,93041)}:
        raise ValueError('EPOCH02_ORIGINAL_SEED_MUTATION')
    # Only rebind the source-free *fixture generator's allowlist*. No model,
    # scoring, stage, control, checkpoint or policy definitions change.
    module.SEEDS = SEEDS
    return module


def classify(rows):
    if len(rows) != 4 or {(x['altered'], x['seed']) for x in rows} != set(ORDER):
        raise ValueError('EPOCH02_INCOMPLETE_COHORT')
    detail = []
    for x in rows:
        if x['episodes'] != 112 or len(x['stage_end_checkpoints']) != 3:
            raise ValueError('EPOCH02_INCOMPLETE_SEED')
        b = x['transition_brier']
        best = min(b['changed'][arm] for arm in CONTROLS)
        margin = round(b['changed']['epoch'] - best, 9)
        return_drift = round(b['A_return']['epoch'] - b['A_return']['frozen'], 9)
        detail.append({'altered':x['altered'],'seed':x['seed'],
                       'epoch_changed_brier':b['changed']['epoch'],
                       'best_control_changed_brier':best,
                       'candidate_minus_best_control':margin,
                       'return_drift_vs_frozen':return_drift,
                       'changed_pass':margin <= -0.005,
                       'return_pass':return_drift <= 0.01,
                       'no_warm_spurious':x['stage_activations']['A_warm']==0})
    all_pass = all(x['changed_pass'] and x['return_pass'] and x['no_warm_spurious'] for x in detail)
    both_fail = all(not x['changed_pass'] for x in detail)
    retention_fail = any(not x['return_pass'] for x in detail)
    result='DEV_PROMISING_ONLY' if all_pass else 'DEV_NO_GO' if both_fail or retention_fail else 'DEV_MIXED'
    return result,detail


def _read_receipt(path: Path, scenario: str, seed: int, pins):
    data = json.loads(path.read_bytes())
    if data.get('status')!='COMPLETE' or (data.get('seed'),data.get('altered'))!=(seed,scenario) or data.get('pins')!=pins:
        raise ValueError('EPOCH02_RECEIPT_MISMATCH')
    if data['result']['episodes'] != 112:
        raise ValueError('EPOCH02_CONSUMED_COUNT')
    return data['result']


def child(joint: Path, journal: Path, scenario: str, seed: int, runner_blob: str):
    pins = source_preflight(joint, runner_blob)
    if (scenario,seed) not in ORDER or journal.exists():
        raise ValueError('EPOCH02_CHILD_SCOPE')
    start = time.perf_counter()
    model = source_model()
    # Import/original checkpoint verified before scoring; no A->B->A event
    # is drawn during any parent-run preflight.
    old = model.load_original(joint)
    result = model.run_seed(old,seed,scenario)
    data = {'status':'COMPLETE','seed':seed,'altered':scenario,'pins':pins,
            'result':result,'child_wall_seconds':round(time.perf_counter()-start,6),
            'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'scientific_gain_verified':False}
    atomic_write(journal,canonical(data))
    print(json.dumps({'seed':seed,'altered':scenario,'episodes':result['episodes'],'wall':data['child_wall_seconds']}),flush=True)


def parent(joint: Path, output: Path, runner_blob: str):
    pins=source_preflight(joint, runner_blob)
    # Run can only start in an EMPTY directory, thus resumed execution cannot
    # consume a primary seed twice. Marker is fsynced BEFORE a child launches.
    if output.exists():
        if not output.is_dir() or any(output.iterdir()):
            raise ValueError('EPOCH02_PRIOR_ATTEMPT_FOUND_NO_REPLAY')
    else:
        output.mkdir(parents=True)
    started = time.perf_counter()
    rows=[]
    for scenario,seed in ORDER:
        key=f'{scenario}-{seed}'
        started_path=output / (key+'.started.json')
        receipt_path=output / (key+'.receipt.json')
        atomic_write(started_path,canonical({'status':'STARTED','altered':scenario,'seed':seed,'pins':pins}))
        command=[sys.executable,'-B',str(Path(__file__).resolve()),'child',
                 '--joint',str(joint.resolve()),'--receipt',str(receipt_path),
                 '--scenario',scenario,'--seed',str(seed),'--runner-blob',runner_blob]
        try:
            proc=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                timeout=PER_SEED_SECONDS,check=False)
        except subprocess.TimeoutExpired:
            atomic_write(output/(key+'.timeout.json'),canonical({'status':'TIMEOUT_TERMINAL','seed':seed,'altered':scenario,'cap_seconds':PER_SEED_SECONDS}))
            raise RuntimeError('EPOCH02_TIMEOUT_STOP_NO_REPLAY:'+key)
        if proc.returncode != 0 or not receipt_path.exists():
            atomic_write(output/(key+'.failure.json'),canonical({'status':'FAILED_TERMINAL', 'seed':seed,'altered':scenario,
                'returncode':proc.returncode,'stderr_excerpt':proc.stderr.decode('utf-8','replace')[-1800:]}))
            raise RuntimeError('EPOCH02_CHILD_FAILED_NO_REPLAY:'+key)
        rows.append(_read_receipt(receipt_path,scenario,seed,pins))
        print(key+' completed and sealed',flush=True)
    classification, detail=classify(rows)
    summary={'schema':'yggdrasil.wscm.epoch02.source-free-dev.v1',
             'classification':classification, 'source_parent':'86264b41a08d49f558418c0fba367f3a2636befa',
             'pins':pins,'seed_order':ORDER,'per_seed':rows,'predeclared_gates':detail,
             'new_protected_world_actions':0,'synthetic_public_observations':sum(x['episodes'] for x in rows),
             'all_controls_same_observations':True,'original_native_accepted_state_mutated':False,
             'full_repo_regression':'UNVERIFIED','scientific_gain_verified':False,
             'wall_seconds':round(time.perf_counter()-started,6)}
    atomic_write(output/'result.json',canonical(summary))
    print('SEALED '+classification+' 4/4 receipts '+str(summary['synthetic_public_observations'])+' outcomes',flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=('child','parent'))
    p.add_argument('--joint',type=Path,required=True)
    p.add_argument('--runner-blob',required=True)
    p.add_argument('--out-dir',type=Path)
    p.add_argument('--receipt',type=Path)
    p.add_argument('--scenario')
    p.add_argument('--seed',type=int)
    a=p.parse_args()
    if a.mode=='child':
        if a.receipt is None: raise ValueError('EPOCH02_NO_RECEIPT')
        child(a.joint,a.receipt,a.scenario,a.seed,a.runner_blob)
    else:
        if a.out_dir is None: raise ValueError('EPOCH02_NO_OUTPUT_DIR')
        parent(a.joint,a.out_dir,a.runner_blob)


if __name__=='__main__':
    main()
