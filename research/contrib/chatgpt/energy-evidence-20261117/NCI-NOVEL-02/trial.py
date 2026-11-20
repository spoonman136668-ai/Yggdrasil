"""Source-free only, one-way public observation tape. No native model interface."""
from __future__ import annotations
import argparse
import json
import math
import resource
import time
from pathlib import Path
from core import ResearchArm, canonical, digest
from world import (FAMILIES,SEEDS,PILOT_SEED,SIZES,OLD_IDS,NEW_IDS,
                   inputs,consequence,action,witness,identity)

ARMS=('GATED_MAP','BMA','NO_X3','FULL','BACKOFF','RECURRENT','FROZEN_OLD')
FITTED=('BMA','FULL','BACKOFF','RECURRENT')
NOVEL=FAMILIES[:4]


def episode(arm,seed,family,phase,i,policy='balanced',update=True):
    x=inputs(seed,family,phase,i)
    ids=identity(phase)
    if policy=='reward':
        a1=max((0,1),key=lambda a:(expected_reward(arm,ids,x,a),-a))
    else:
        a1=action(seed,family,phase,i,'t')
    feat_t=(*x,a1)
    p_t=arm.predict(ids,'t',feat_t)
    s2=consequence(seed,family,phase,i,'t',x,a1)
    if policy=='reward':
        a2=max((0,1),key=lambda a:(arm.predict(ids,'y',(*x,s2,a)),-a))
    else:
        a2=action(seed,family,phase,i,'y')
    feat_y=(*x,s2,a2)
    p_y=arm.predict(ids,'y',feat_y)
    y=consequence(seed,family,phase,i,'y',x,a1,s2,a2)
    if update:
        arm.admit(ids,'t',feat_t,s2,witness(seed,family,phase,i,'t'))
        arm.admit(ids,'y',feat_y,y,witness(seed,family,phase,i,'y'))
    return {'brier':((p_t-s2)**2+(p_y-y)**2)/2,'reward':y,
            'action1':a1,'action2':a2,'transition':s2,'input':x}


def expected_reward(arm,ids,x,a1):
    p=arm.predict(ids,'t',(*x,a1))
    y0=max(arm.predict(ids,'y',(*x,0,a2)) for a2 in (0,1))
    y1=max(arm.predict(ids,'y',(*x,1,a2)) for a2 in (0,1))
    return (1-p)*y0+p*y1


def mean(rows,key):
    return sum(z[key] for z in rows)/len(rows) if rows else None


def single(seed,family):
    arms={name:ResearchArm(name) for name in ARMS}
    cpu={name:0.0 for name in ARMS}
    for phase in ('old_fit','new_fit'):
        for i in range(SIZES[phase]):
            for name,arm in arms.items():
                st=time.process_time()
                episode(arm,seed,family,phase,i)
                cpu[name]+=time.process_time()-st
        if phase=='old_fit':
            before={k:v.old_digest(OLD_IDS) for k,v in arms.items()}
    after={k:v.old_digest(OLD_IDS) for k,v in arms.items()}
    if before!=after:raise AssertionError('OLD_STATE_MUTATED_ON_NEW_FIT')
    valid={name:[] for name in ARMS}
    for i in range(SIZES['valid']):
        for name,arm in arms.items():
            valid[name].append(episode(arm,seed,family,'valid',i,update=False))
    valid_loss={name:mean(data,'brier') for name,data in valid.items()}
    chosen=min(FITTED,key=lambda k:(valid_loss[k],k))
    shared={name:[] for name in ARMS}
    for i in range(SIZES['held_shared']):
        for name,arm in arms.items():
            st=time.process_time()
            shared[name].append(episode(arm,seed,family,'held_shared',i))
            cpu[name]+=time.process_time()-st
    restored={}
    for name,arm in arms.items():
        raw=arm.checkpoint()
        re=ResearchArm.restore(raw,digest(raw))
        if re.checkpoint()!=raw:raise AssertionError('COLD_CHECKPOINT_CHANGED')
        restored[name]=re
    arms=restored
    policy={name:[] for name in ARMS}
    for name,arm in arms.items():
        for i in range(SIZES['held_policy']):
            st=time.process_time()
            policy[name].append(episode(arm,seed,family,'held_policy',i,policy='reward'))
            cpu[name]+=time.process_time()-st
    returned={name:[] for name in ARMS}
    for i in range(SIZES['old_return']):
        for name,arm in arms.items():
            returned[name].append(episode(arm,seed,family,'old_return',i,update=False))
    for name,arm in arms.items():
        if arm.old_digest(OLD_IDS)!=before[name]:raise AssertionError('OLD_RETURN_READOUT_MUTATION')
    candidate_evidence={stage:arms['GATED_MAP'].component(NEW_IDS,stage).evidence() for stage in ('t','y')}
    return {
        'seed':seed,'family':family,'valid_selected_fitted_control':chosen,
        'valid_brier':valid_loss,
        'held_shared_brier':{k:mean(v,'brier') for k,v in shared.items()},
        'policy_reward':{k:mean(v,'reward') for k,v in policy.items()},
        'return_brier':{k:mean(v,'brier') for k,v in returned.items()},
        'candidate_evidence':candidate_evidence,
        'checkpoint_bytes':{k:len(v.checkpoint()) for k,v in arms.items()},
        'checkpoints_sha256':{k:digest(v.checkpoint()) for k,v in arms.items()},
        'old_digest_sha256':before,
        'new_episode_records_per_model':{k:v.event_count for k,v in arms.items()},
        'cpu_seconds':cpu,
        'evaluation_actions_per_arm':2*sum(SIZES.values()),
        'original_source_first_use':False,'native_canonical_checkpoint':False}


def aggregate(worlds):
    novels=[w for w in worlds if w['family'] in NOVEL]
    byfamily={}
    for f in NOVEL:
        arr=[z for z in novels if z['family']==f]
        cand=sum(x['held_shared_brier']['GATED_MAP'] for x in arr)/len(arr)
        nox=sum(x['held_shared_brier']['NO_X3'] for x in arr)/len(arr)
        selected=sum(x['held_shared_brier'][x['valid_selected_fitted_control']] for x in arr)/len(arr)
        reward=sum(x['policy_reward']['GATED_MAP'] for x in arr)/len(arr)
        ctrl_reward=sum(x['policy_reward'][x['valid_selected_fitted_control']] for x in arr)/len(arr)
        identified=sum(bool(x['candidate_evidence']['t']['identified'] and x['candidate_evidence']['y']['identified']) for x in arr)
        byfamily[f]={'identified_two_stage_seeds':identified,'candidate_brier':cand,
           'no_fourth_brier':nox,'selected_fitted_brier':selected,
           'candidate_reward':reward,'selected_fitted_reward':ctrl_reward,
           'ablation_gain_relative':(nox-cand)/nox,
           'superiority_vs_fitted_relative':(selected-cand)/selected,
           'representation_pass':identified>=3 and cand<=.90*nox,
           'superiority_pass':cand<=.95*selected and reward>ctrl_reward}
    nega=[w for w in worlds if w['family'] in ('unidentifiable_x3','outside_grammar')]
    return {'novel_family':byfamily,
      'representation_families_passed':sum(z['representation_pass'] for z in byfamily.values()),
      'strong_control_superiority_families_passed':sum(z['superiority_pass'] for z in byfamily.values()),
      'negative_unknown_count':sum(not(z['candidate_evidence']['t']['identified'] or z['candidate_evidence']['y']['identified']) for z in nega),
      'negative_total':len(nega),
      'max_candidate_checkpoint_bytes':max(w['checkpoint_bytes']['GATED_MAP'] for w in worlds),
      'total_candidate_CPU_seconds':sum(w['cpu_seconds']['GATED_MAP'] for w in worlds),
      'total_BMA_CPU_seconds':sum(w['cpu_seconds']['BMA'] for w in worlds),
      'scientific_pass':False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    seeds=(PILOT_SEED,) if args.pilot else SEEDS
    families=FAMILIES[:2] if args.pilot else FAMILIES
    start=time.monotonic()
    worlds=[]
    for seed in seeds:
        for family in families:
            worlds.append(single(seed,family))
            print('COMPLETED',seed,family,round(time.monotonic()-start,2),flush=True)
    obj={'schema':'nci-novel02.source-free-dev-report.v1',
        'source_free':True,'pilot':args.pilot,'seeds':list(seeds),'families':list(families),
        'worlds':worlds,'aggregate':aggregate(worlds) if not args.pilot else None,
        'elapsed_wall_seconds':time.monotonic()-start,
        'native_accepted':False,'scientific_pass':False,
        'protected_source_first_use':False}
    args.output.write_bytes(canonical(obj)+b'\n')
    print('REPORT',args.output, args.output.stat().st_size)

if __name__=='__main__':main()
