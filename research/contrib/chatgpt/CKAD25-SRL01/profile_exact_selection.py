"""Read-only prior-vs-optimized SRL01 selection CPU profile.

Uses exactly frozen *public training witnesses*, never original evaluator truth,
original source actor, canonical checkpoint, paid API, runner or new trial.
The previous Fraction source is obtained from a pinned prior Git blob (or a
user-provided local exact-blob file in a source-free development sandbox).
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
from time import process_time

from dev_trial import (STATIONARY_SEEDS, NEGATIVE_SEEDS, training_history)
from yggdrasil.native_shared_fault_risk import (NativeSharedFaultRisk,
                                                 independent_beta_risks)

PREVIOUS_BLOB = '6b9811f4c61ef6fba67ba9685ca14bd14d0c5f1d'
ORIGINAL_PARENT = '2da3f907b2a622b5af801d75a8b2ed46f14f1d3e'
NEW_BLOB = 'f5f98069b74a984906295256e61c6b1b97bc6b7c'
ROOT = (Path(__file__).resolve().parents[4]
        if len(Path(__file__).resolve().parents)>4 else Path.cwd())
MASKS = tuple(range(4))


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def get_prior_source():
    path = os.environ.get('SRL01_PINNED_PRIOR_SOURCE_PATH')
    if path:
        raw = Path(path).read_bytes()
    else:
        raw = subprocess.run(['git','show',ORIGINAL_PARENT+':yggdrasil/native_shared_fault_risk.py'],
                             cwd=ROOT,check=True,capture_output=True).stdout
    if git_blob(raw) != PREVIOUS_BLOB:
        raise ValueError('PREVIOUS_MODEL_BLOB_DRIFT')
    spec=importlib.util.spec_from_loader('_srl01_original_fraction_model',loader=None)
    module=importlib.util.module_from_spec(spec)
    exec(compile(raw,'_srl01_original_fraction_model.py','exec'),module.__dict__)
    return module


def run(repetitions=80,rounds=3):
    import inspect
    optimized=Path(inspect.getfile(NativeSharedFaultRisk)).read_bytes()
    if git_blob(optimized)!=NEW_BLOB:
        raise ValueError('OPTIMIZED_SOURCE_BLOB_DRIFT')
    prior=get_prior_source()
    histories=[training_history(s,negative=False) for s in STATIONARY_SEEDS]
    histories += [training_history(s,negative=True) for s in NEGATIVE_SEEDS]
    if len(histories)!=72:raise ValueError('PUBLIC_COHORT_DRIFT')
    def beta(history):
        r=independent_beta_risks(MASKS,history)
        return tuple(sorted(MASKS,key=lambda a:(-r[a],a))[:2])
    methods={
        'prior_fraction_fit_and_select':lambda h:prior.NativeSharedFaultRisk(MASKS,h).select(),
        'optimized_integer_fit_and_select':lambda h:NativeSharedFaultRisk(MASKS,h).select(),
        'prior_empirical_beta_fit_and_select':beta,
    }
    for h in histories:
        if methods['prior_fraction_fit_and_select'](h)!=methods['optimized_integer_fit_and_select'](h):
            raise ValueError('ORIGINAL_ACTION_PARITY_FAIL')
    times={name:[] for name in methods}
    for _ in range(rounds):
        for method in methods.values():
            for history in histories:method(history)
        for name,method in methods.items():
            start=process_time()
            for _ in range(repetitions):
                for history in histories:method(history)
            times[name].append(process_time()-start)
    med={name:statistics.median(t) for name,t in times.items()}
    return {
        'schema':'yggdrasil.srl01.posthoc_exact_cpu_selection.v1',
        'runtime':{'python':sys.version.split()[0],'platform':platform.platform()},
        'scope':'same 72 consumed PUBLIC source histories, post-result engineering only',
        'new_science_trials':0,'new_original_source_actions':0,
        'original_prior_git_blob':PREVIOUS_BLOB,'optimized_git_blob':NEW_BLOB,
        'original_source_sha_parent':ORIGINAL_PARENT,
        'histories':72,'rounds':rounds,'calls_per_arm_per_round':72*repetitions,
        'cpu_seconds_rounds':times,'median_cpu_seconds':med,
        'speedup_over_prior_fraction':med['prior_fraction_fit_and_select']/med['optimized_integer_fit_and_select'],
        'optimized_vs_beta_ratio':med['optimized_integer_fit_and_select']/med['prior_empirical_beta_fit_and_select'],
        'native_end_to_end_cpu':'UNVERIFIED','windows_linux_full_final':'NOT_RUN',
        'source_readout_parity':True,'scientific_gain_verified':False,
    }


if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
