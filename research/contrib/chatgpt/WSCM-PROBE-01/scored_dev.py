"""One-shot DEV-only comparison on frozen source-free seeds.

Never provide scenario labels to WitnessCausalProbe. Seal each completed seed
before starting another; never replay a started seed on failure/timeout.
No protected-world source, controller or paid API access.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha1, sha256
from importlib.util import spec_from_file_location, module_from_spec
import json
import os
from pathlib import Path
import random
import time

from yggdrasil.native_episode_experience import NativeEpisodeExperience

ROOT = Path(__file__).resolve().parents[3] # within research/contrib/chatgpt/WSCM-PROBE-01
COORDINATOR = '86264b41a08d49f558418c0fba367f3a2636befa'
NATIVE_BLOB = '5a18b00a4c4131526e71f51d63dfd9eb9471c81e'
VERSION_BLOB = 'de9fe9a25a575379286425d81e9a490da7b913fa'
HAZARD = Fraction(1,16)
SEEDS=(96211,96221,96229,96253)
PHASES=(('B_confirm',24,0,Fraction(4,5)),
        ('A_return',24,0,Fraction(1,26)),
        ('C_unfamiliar',24,1,Fraction(9,10)))


def source_module(name,filepath):
    spec=spec_from_file_location(name,filepath)
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git_blob(data):
    return sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def seal(root,path,obj):
    data=json.dumps(obj,sort_keys=True,indent=2,allow_nan=False).encode()+b'\n'
    target=root/path
    fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644)
    with os.fdopen(fd,'wb') as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    return sha256(data).hexdigest()


def synthetic(i,context,outcome):
    identifier=sha256(f'wscm-probe01/public-fixture/{i}'.encode()).hexdigest()
    return identifier,((context,0),(context,1)),{'s1':context,'x1':0,'s2':outcome,'x2':0,'y':0}


def original_fixture(versioned):
    obj=versioned.VersionedNativeTransition(NativeEpisodeExperience())
    for i in range(48):
        obj=obj.observe(*synthetic(i,i%2,i%2))
    for i in range(48,51):
        obj=obj.observe(*synthetic(i,0,1))
    repair=obj.versions()
    if len(repair)!=1 or repair[0]['old_counts']!=[24,0] or repair[0]['reset_counts']!=[0,3]:
        raise ValueError('SCORING_SOURCE_FIXTURE_MISMATCH')
    return obj,repair[0]['version_id']


def beta_from_ledger(ledger,context,action,tail=None):
    found=[]
    for identifier,views,x1,y,x2,reward in (ledger if tail is None else ledger[-tail:]):
        if views[0][0]==context and x1==action:
            found.append(y)
    return Fraction(sum(found)+1,len(found)+2)


def independent_bayes_predict(weight,old,new):
    # Separately implemented exact two-state conventional HMM comparator.
    next_old=HAZARD+(1-2*HAZARD)*weight
    return next_old*old+(1-next_old)*new


def independent_bayes_update(weight,old,new,outcome):
    prior=HAZARD+(1-2*HAZARD)*weight
    like_old=(old if outcome==1 else (1-old))
    like_new=(new if outcome==1 else (1-new))
    return (prior*like_old)/(prior*like_old+(1-prior)*like_new)


def run_seed(seed,versioned,probe_mod):
    # No seed/phase is passed to the learner. Only source-free public witnesses.
    rng=random.Random(seed)
    ver,eid=original_fixture(versioned)
    learner=probe_mod.WitnessCausalProbe(ver,eid)
    bayes_weight=Fraction(1,2)
    ledger=list(ver.original_native._ledger)
    seen=set(x[0] for x in ledger)
    global_i=51
    by_phase=[]
    all_actions=0
    for phase,num,context,law in PHASES:
        sums={name:0.0 for name in ('candidate','two_state_bayes','frozen_old',
                                    'frozen_reset','continuing_native','fitted_beta','trailing32_beta')}
        diagnostic=0
        after8=None
        for j in range(num):
            view=(context,0)
            action,informative=learner.choose(view)
            old,new=learner.hypotheses(view,action)
            # Explicit prequential predictions before this event is generated.
            p=learner.forecast(view,action)
            if informative:
                conventional=independent_bayes_predict(bayes_weight,old,new)
            else:
                conventional=old
            if p!=conventional:
                raise ValueError('SCORED_CONVENTIONAL_BAYES_PARITY')
            predictions={
              'candidate':p,'two_state_bayes':conventional,
              'frozen_old':old,'frozen_reset':new,
              'continuing_native':learner.original_native.forecast(view,action,full=True),
              'fitted_beta':beta_from_ledger(ledger,context,action),
              'trailing32_beta':beta_from_ledger(ledger,context,action,32),
            }
            # The deterministic synthetic simulator draws ONE action-consequence
            # outcome shared with all controls, never more for the candidate.
            y=int(rng.randrange(law.denominator)<law.numerator)
            witness_id=sha256(f'wscm-probe01/{seed}/{global_i}'.encode()).hexdigest()
            if witness_id in seen:
                raise ValueError('SCORED_DUPLICATE_WITNESS')
            seen.add(witness_id)
            views=((context,0),(context,1))
            row={'s1':context,'x1':action,'s2':y,'x2':0,'y':0}
            for name,val in predictions.items():
                sums[name]+=(float(val)-y)**2
            if informative:
                bayes_weight=independent_bayes_update(bayes_weight,old,new,y)
                diagnostic+=1
            learner=learner.witness(witness_id,views,row)
            if learner.posterior_old!=bayes_weight:
                raise ValueError('SCORED_CONVENTIONAL_POSTERIOR_PARITY')
            ledger.append(learner.original_native._ledger[-1])
            all_actions+=1
            global_i+=1
            if j==7:
                after8=float(learner.posterior_old)
        # Cold check after each phase, binding the exact independent state
        # digest (the checkpoint is stored separately from version sidecar).
        raw=learner.checkpoint()
        snap=sha256(raw[2]).hexdigest()
        cold=probe_mod.WitnessCausalProbe.restore(
            *raw,versioned.VersionedNativeTransition,expected_state_sha256=snap)
        if cold.checkpoint()!=raw or cold.posterior_old!=learner.posterior_old:
            raise ValueError('SCORED_COLD_REPLAY_DRIFT')
        learner=cold
        by_phase.append({'stage':phase,'count':num,
                         'mean_transition_brier':{k:round(s/num,9) for k,s in sums.items()},
                         'diagnostic_actions':diagnostic,
                         'posterior_old_after8':round(after8,9),
                         'cold_sha256':snap,'cold_parity':True,
                         'source_state_sha256':learner.original_native.info()['state_sha256']})
    if all_actions!=72 or learner.counts!=(48,24):
        raise ValueError('SCORED_ACTION_PARITY')
    return {'seed':seed,'source_free':True,'episodes':all_actions,
            'native_prefix_witnesses':51,'end_ledger_events':len(learner.original_native._ledger),
            'phases':by_phase,'diagnostic_evidence_and_abstentions':list(learner.counts),
            'live_source_state_sha256':learner.original_native.info()['state_sha256']}


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--out',required=True,type=Path)
    args=cli.parse_args()
    target=args.out
    target.mkdir(parents=True,exist_ok=True)
    # No scored seed is invoked before all source and checkpoint integrity.
    native_path=Path(__import__('yggdrasil.native_episode_experience',fromlist=['x']).__file__)
    if git_blob(native_path.read_bytes())!=NATIVE_BLOB:
        raise ValueError('SCORED_NATIVE_SOURCE_DRIFT')
    ver_path=Path(__file__).parents[1]/'WSCM-VERSIONED-02/versioned_transition.py'
    if git_blob(ver_path.read_bytes())!=VERSION_BLOB:
        raise ValueError('SCORED_VERSION_SOURCE_DRIFT')
    probe_path=Path(__file__).parents[0]/'probe.py'
    # During source-frozen execution the expected blob is pinned by caller
    # and logged, not inferred from mutable Python code at runtime.
    ver=source_module('wscm_version_for_probe_scoring',ver_path)
    probe=source_module('wscm_probe_scoring',probe_path)
    if probe.HAZARD!=HAZARD:
        raise ValueError('SCORED_HAZARD_DRIFT')
    started=time.perf_counter()
    checks=[]
    for seed in SEEDS:
        seal(target,f'{seed}.started.json',{'seed':seed,'source_free':True,'one_shot':True,
                                           'native_blob':NATIVE_BLOB,'version_blob':VERSION_BLOB})
        one=run_seed(seed,ver,probe)
        one['wall_s']=round(time.perf_counter()-started,6)
        one['receipt_sha256']=seal(target,f'{seed}.completed.json',one)
        checks.append(one)
        print('SEALED_SEED',seed,'episodes',one['episodes'],'wall_s',one['wall_s'],flush=True)
        if time.perf_counter()-started>60:
            raise TimeoutError('SCORED_60_SECOND_BUDGET')
    summary={'schema':'yggdrasil.wscm.probe01.source-free-dev.v1',
             'preregistered_seeds':list(SEEDS),'completed_seed_count':len(checks),
             'completed_public_outcomes':sum(x['episodes'] for x in checks),
             'exact_bayes_prequential_parity':True,
             'scenario_labels_not_given_to_learner':True,
             'scientific_gain_verified':False,
             'results':checks,'wall_s':round(time.perf_counter()-started,6)}
    seal(target,'result.json',summary)
    print('FINAL_SEALED_RESULT',len(checks),'wall_s',summary['wall_s'],flush=True)


if __name__=='__main__':main()
