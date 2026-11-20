"""NCI-NOVEL-01 source-free four-seed development screen, never owner science.
Original design/preprimary amendment are immutable on GitHub before first scored run.
"""
from __future__ import annotations
import json,sys,time,math,argparse,hashlib
from pathlib import Path
from core import NativeResearchArm, MASKS, COMPLEXITY, canonical, digest
from world import FAMILIES, PHASES, IDs, source_inputs, world_step, planned_action, event_id

SEEDS=(481223,481247,481269,481283)
EXPOSED_PREFLIGHT_SEED=481201
SIZES={'old_fit':64,'new_fit':64,'valid':32,'held_new':64,'return_old':64}
KINDS=('MAP','BMA','FULL','SUBSET','RECURRENT')


def obs(arm, seed,family,phase,index,policy='random',update=True):
    p,q,r=source_inputs(seed,family,phase,index)
    ident=IDs(phase)
    if policy=='reward':
        a1=max((0,1),key=lambda a:(expected_reward(arm,ident,p,q,r,a),-a))
    elif policy=='information':
        a1=max((0,1),key=lambda a:(uncertainty(arm.predict(ident,'t',(p,q,a),r)),-a))
    else:a1=planned_action(seed,family,phase,index,'a1')
    first=(p,q,a1)
    pred_t=arm.predict(ident,'t',first,r)
    s2=world_step(seed,family,phase,index,p,q,r,a1)
    if policy=='reward':
        a2=max((0,1),key=lambda a:(arm.predict(ident,'y',(q,s2,a),r),-a))
    elif policy=='information':
        a2=max((0,1),key=lambda a:(uncertainty(arm.predict(ident,'y',(q,s2,a),r)),-a))
    else:a2=planned_action(seed,family,phase,index,'a2')
    terminal=(q,s2,a2)
    pred_y=arm.predict(ident,'y',terminal,r)
    y=world_step(seed,family,phase,index,p,q,r,a1,a2,s2)
    if update:
        arm.update(ident,'t',first,r,s2,event_id(seed,family,phase,index,'t'))
        arm.update(ident,'y',terminal,r,y,event_id(seed,family,phase,index,'y'))
    return {'transition_brier':(pred_t-s2)**2,'reward_brier':(pred_y-y)**2,
            'reward':y,'a1':a1,'a2':a2,'p':p,'q':q,'r':r,'state':s2,
            'source_id':f'nci01/{seed}/{family}/{phase}/{index}',
            'source_public_factor_ids':ident[:3], 'public_action_roles':ident[3:],
            'source_authenticity':'SELF_AUTHORED_SYNTHETIC_ONLY'}


def uncertainty(p):
    return -p*math.log(max(p,1e-300))-(1-p)*math.log(max(1-p,1e-300))


def expected_reward(arm,source_ids,p,q,r,a1):
    chance=arm.predict(source_ids,'t',(p,q,a1),r)
    first=max(arm.predict(source_ids,'y',(q,0,a2),r) for a2 in (0,1))
    second=max(arm.predict(source_ids,'y',(q,1,a2),r) for a2 in (0,1))
    return (1-chance)*first+chance*second


def mean(xs,key):return sum(x[key] for x in xs)/len(xs) if xs else None


def single(seed,family):
    models={k:NativeResearchArm(k) for k in KINDS}
    start=time.monotonic();fit_times={k:0 for k in KINDS};full_times={k:0 for k in KINDS}
    old_ids=IDs('old_fit')
    for phase in ('old_fit','new_fit'):
        for i in range(SIZES[phase]):
            for k,m in models.items():
                st=time.process_time();obs(m,seed,family,phase,i,update=True);dt=time.process_time()-st;fit_times[k]+=dt;full_times[k]+=dt
        if phase=='old_fit':
            old_pins={k:m.old_digest(old_ids) for k,m in models.items()}
            old_snapshots={k:m.checkpoint()['sha256'] for k,m in models.items()}
        elif phase=='new_fit':
            for k,m in models.items():
                if m.old_digest(old_ids)!=old_pins[k]:raise AssertionError('OLD_WEIGHT_DRIFT_'+k)
    val={k:[] for k in KINDS}
    for i in range(SIZES['valid']):
        for k,m in models.items():
            st=time.process_time();val[k].append(obs(m,seed,family,'valid',i,update=False));full_times[k]+=time.process_time()-st
    rates={k:sum(z['transition_brier']+z['reward_brier'] for z in vs)/(2*len(vs)) for k,vs in val.items()}
    best=min((rates[k],k) for k in KINDS if k!='MAP')[1]
    all_scores={k:[] for k in KINDS}
    for i in range(SIZES['held_new']//2):
        for k,m in models.items():
            st=time.process_time();all_scores[k].append(obs(m,seed,family,'held_new',i,update=True));full_times[k]+=time.process_time()-st
    # Before the policy segment, clone the already observed new-world checkpoint.
    # All policy evaluation states start from the same public observation tape.
    held_snapshots={k:m.checkpoint() for k,m in models.items()}
    for k,snap in held_snapshots.items():
        reloaded=NativeResearchArm.restore(snap['raw'],snap['sha256'])
        if reloaded.checkpoint()['sha256']!=snap['sha256']:raise AssertionError('COLD_CHECKPOINT_DRIFT')
        models[k]=reloaded
    policy_scores={k:[] for k in ('MAP','BMA','FULL','SUBSET','RECURRENT','IG','RANDOM')}
    for k in KINDS:
        for i in range(32,64):
            st=time.process_time();policy_scores[k].append(obs(models[k],seed,family,'held_new',i,policy='reward',update=True));full_times[k]+=time.process_time()-st
    ig=NativeResearchArm.restore(held_snapshots['BMA']['raw'],held_snapshots['BMA']['sha256'])
    ran=NativeResearchArm.restore(held_snapshots['BMA']['raw'],held_snapshots['BMA']['sha256'])
    for i in range(32,64):
        policy_scores['IG'].append(obs(ig,seed,family,'held_new',i,policy='information',update=True))
        policy_scores['RANDOM'].append(obs(ran,seed,family,'held_new',i,policy='random',update=True))
    return_scores={k:[] for k in KINDS}
    for i in range(SIZES['return_old']):
        for k,m in models.items():
            if m.old_digest(old_ids)!=old_pins[k]:raise AssertionError('OLD_CUMULATIVE_RETENTION_FAILED')
            st=time.process_time();return_scores[k].append(obs(m,seed,family,'return_old',i,update=False));full_times[k]+=time.process_time()-st
    for k,m in models.items():
        if m.old_digest(old_ids)!=old_pins[k]:raise AssertionError('POST_RETURN_DRIFT')
    recognized={}
    for k in ('MAP','BMA'):
        recognized[k]={stage:models[k].component(IDs('new_fit'),stage).confidence() for stage in ('t','y')}
    # Preserve exact snapshot integrity and impose fixed-footprint cap.
    states={k:m.checkpoint() for k,m in models.items()}
    if states['MAP']['bytes']>65536:raise ValueError('MAP_SOURCE_FREE_MEMORY_CAP_BREACH')
    out={
        'seed':seed,'family':family,'selected_control_on_validation':best,
        'validation_brier':rates,
        'held_shared_brier':{k:mean([{'brier':(o['transition_brier']+o['reward_brier'])/2} for o in v],'brier') for k,v in all_scores.items()},
        'held_policy_reward':{k:mean(v,'reward') for k,v in policy_scores.items()},
        'return_old_brier':{k:mean([{'brier':(o['transition_brier']+o['reward_brier'])/2} for o in v],'brier') for k,v in return_scores.items()},
        'old_digest':old_pins,'old_checkpoint_before_new':old_snapshots,
        'last_state_sha256':{k:s['sha256'] for k,s in states.items()},
        'state_bytes':{k:s['bytes'] for k,s in states.items()},
        'source_visible_r_values':recognized['MAP']['t']['observed_r_support'],
        'candidate_relation':recognized['MAP'],
        'fully_fitted_exact_relation':recognized['BMA'],
        'fit_cpu_seconds':fit_times,'full_process_cpu_seconds':full_times,
        'action_count_per_arm':576,
        'source_exposure_conventions':'Two observed interventions per 288 episodes per family, including 32 matched held prequential and 32 separately selected real policy outcomes',
        'records':{'fit_old':64,'fit_new':64,'valid':32,'held_shared':32,'held_policy':32,'return_old':64},
        'elapsed_wall_seconds':time.monotonic()-start,
        'scientific_acceptance':False}
    return out


def aggregate(results):
    novelty=[x for x in results if x['family'].startswith('disjoint')]
    family_wins={}
    per_seed={}
    for family in sorted(set(x['family'] for x in novelty)):
        rows=[x for x in novelty if x['family']==family]
        wins=0
        for x in rows:
            cand=x['held_shared_brier']['MAP']
            selected=x['selected_control_on_validation']
            strongest=x['held_shared_brier'][selected]
            if cand<=.95*strongest and x['held_policy_reward']['MAP']>x['held_policy_reward'][selected]:
                wins+=1
        candidate_mean=sum(x['held_shared_brier']['MAP'] for x in rows)/len(rows)
        selected_mean=sum(x['held_shared_brier'][x['selected_control_on_validation']] for x in rows)/len(rows)
        c_reward=sum(x['held_policy_reward']['MAP'] for x in rows)/len(rows)
        b_reward=sum(x['held_policy_reward'][x['selected_control_on_validation']] for x in rows)/len(rows)
        family_wins[family]={'seeds_won':wins,'candidate_mean_held_brier':candidate_mean,
            'selected_control_mean_held_brier':selected_mean,
            'candidate_mean_action_reward':c_reward,'selected_control_mean_action_reward':b_reward,
            'qualified_dev_improvement':candidate_mean<=.95*selected_mean and c_reward>b_reward}
    for seed in SEEDS:
        rows=[x for x in results if x['seed']==seed]
        per_seed[str(seed)]={'MAP_mean_brier':sum(x['held_shared_brier']['MAP'] for x in rows)/len(rows),
             'VALID_selected_control_mean_brier':sum(x['held_shared_brier'][x['selected_control_on_validation']] for x in rows)/len(rows),
             'MAP_policy_reward':sum(x['held_policy_reward']['MAP'] for x in rows)/len(rows),
             'BMA_policy_reward':sum(x['held_policy_reward']['BMA'] for x in rows)/len(rows)}
    return {'family_per_seed_strong_control_wins':family_wins,
            'winning_families':sum(1 for row in family_wins.values() if row['qualified_dev_improvement']),
            'overall_held_MAP':sum(x['held_shared_brier']['MAP'] for x in results)/len(results),
            'overall_held_control_selected_validation':sum(x['held_shared_brier'][x['selected_control_on_validation']] for x in results)/len(results),
            'overall_held_control_min_posthoc_DIAGNOSTIC_ONLY':sum(min(x['held_shared_brier'][k] for k in KINDS if k!='MAP') for x in results)/len(results),
            'per_seed':per_seed,
            'NO_SCIENCE_PASS':True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preflight-only',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    t0=time.monotonic()
    results=[]
    seeds=(EXPOSED_PREFLIGHT_SEED,) if args.preflight_only else SEEDS
    families=FAMILIES[:2] if args.preflight_only else FAMILIES
    for seed in seeds:
        for family in families:
            results.append(single(seed,family))
            print('completed',seed,family,'wall',round(results[-1]['elapsed_wall_seconds'],3),flush=True)
    report={'schema':'nci-novel01.source-free-dev-report.v1',
            'preflight_only':args.preflight_only,
            'study_seeds':list(seeds),'source_free_self_authored':True,
            'candidate':'bounded_min_description_length_boolean_program_MAP',
            'controls':list(KINDS[1:])+['ACTIVE_BMA_INFO_GAIN','SEEDED_RANDOM'],
            'provenance':'no_original_yggdrasil_source_actions_no_owner_checkpoint',
        'source_first_use_classification':'SELF_AUTHORED_SYNTHETIC_DEV_ONLY',
        'preflight_exposed_seed_not_in_primary':EXPOSED_PREFLIGHT_SEED,
            'worlds':results,'aggregate':aggregate(results) if not args.preflight_only else {},
            'total_wall_seconds':time.monotonic()-t0,
            'model_installed':False,'scientific_pass':False}
    args.output.write_bytes(canonical(report)+b'\n')
    print('result',args.output,'bytes',args.output.stat().st_size)

if __name__=='__main__':main()
