"""UJ06B D0: fresh local consistency transfer; unchanged C0 learner."""
import argparse
import math
import re
import time
from pathlib import Path
import torch
import uj06a_local_pilot as c
import uj04y_intervention_pilot as y
from uj03a_pilot import canonical,digest,check_deadline

ARMS=c.ARMS
CANDIDATE=c.CANDIDATE
NEGATIVE=c.NEGATIVE
CORRUPTED=('relational_local_shuffled',NEGATIVE)
POSITIVE=tuple(k for k in ARMS if k not in CORRUPTED)
CONTROLS=c.CONTROLS
SEEDS=(3401,3402,3403)
FIT_SEED=341100
FAMILIAR_SEED=341200
TRANSFER_SEED=341300
EPOCHS=c.EPOCHS
BATCH=c.BATCH
HORIZON=c.HORIZON
TOTAL_SECONDS=c.TOTAL_SECONDS
cases=c.cases
prepare=c.prepare
datahash=c.datahash
schedule=c.schedule
train=c.train
evaluate=c.evaluate

def emit(event,**fields):
    print('UJ06B '+canonical(dict(event=event,**fields)).decode(),flush=True)

def assert_disjoint_seeds():
    ranges=[set(range(start,start+n)) for start,n in ((FIT_SEED,6),(FAMILIAR_SEED,6),(TRANSFER_SEED,16))]
    historical=set()
    for bases in ((301100,301200,301300),(311100,311200,311300),(321100,321200,321300),(331100,331200,331300)):
        for start,n in zip(bases,(6,6,16)):historical.update(range(start,start+n))
    if any(r & historical for r in ranges) or any(r & s for i,r in enumerate(ranges) for s in ranges[i+1:]):
        raise RuntimeError('split seed overlap')
    if len(set(SEEDS))!=3 or set(SEEDS)&{3001,3002,3003,3101,3102,3103,3201,3202,3203,3301,3302,3303}:
        raise RuntimeError('training seed overlap')

def valid_number(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>=0

def valid_training(r):
    ratios=r['shuffle_ratios']
    hist=r['fit_history']
    return (r['steps']==24*EPOCHS and r['endpoint_steps_exposed']==2*384*HORIZON*EPOCHS
        and len(hist)==5 and all(valid_number(v) for v in hist)
        and len(ratios)==(2 if r['arm'] in c.CORE else 3)
        and all(valid_number(v) and v>=.5 for v in ratios)
        and all(valid_number(r['after'][split][metric]) for split in ('fit','familiar') for metric in ('rollout','effect'))
        and bool(re.fullmatch('[0-9a-f]{64}',r['checkpoint_sha256'])) and r['checkpoint_bytes']>0
        and valid_number(r['wall_seconds']) and valid_number(r['cpu_seconds']))

def eligibility(rows,seeds=SEEDS):
    if len(rows)!=len(seeds)*len(ARMS) or len({(r['seed'],r['arm']) for r in rows})!=len(rows):
        raise RuntimeError('incomplete or duplicate arms')
    checks=[]
    for seed in seeds:
        by={r['arm']:r for r in rows if r['seed']==seed}
        if set(by)!=set(ARMS):raise RuntimeError('unexpected arms')
        custody=all(valid_training(r) for r in by.values())
        positive=all(by[k]['adequate'] and by[k]['after']['familiar']['rollout']<=.15 for k in POSITIVE)
        # Shuffled auxiliary still must learn the uncorrupted prediction task to bounded error.
        sh=by[CORRUPTED[0]]
        aux=sh['after']['fit']['rollout']<=.10 and sh['after']['familiar']['rollout']<=.15
        checks.append(dict(seed=seed,matched_training=custody,positive_mastery=positive,
            corrupted_aux_prediction_bound=aux,corrupted_outcome_valid=valid_training(by[NEGATIVE]),
            primary=custody and positive and aux))
    return checks,all(r['primary'] for r in checks)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-sha',required=True);parser.add_argument('--receipt',type=Path,required=True)
    a=parser.parse_args();root=a.receipt.parent
    if not re.fullmatch('[0-9a-f]{40}',a.source_sha) or not root.is_dir() or any(root.iterdir()):
        raise ValueError('source or exclusive trial directory')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    deadline=time.monotonic()+TOTAL_SECONDS
    assert_disjoint_seeds()
    fit=prepare(cases(FIT_SEED,64),deadline);familiar=prepare(cases(FAMILIAR_SEED,16),deadline)
    if sum(len(r[1]) for r in fit)!=384 or sum(len(r[1]) for r in familiar)!=96:
        raise RuntimeError('dataset count')
    manifest=dict(source_sha=a.source_sha,fit_sha256=datahash(fit),familiar_sha256=datahash(familiar),
                  seeds=SEEDS,data_seed_bases=(FIT_SEED,FAMILIAR_SEED,TRANSFER_SEED),arms=ARMS,epochs=EPOCHS,batch=BATCH,horizon=HORIZON,schedules={a:[schedule(a,e) for e in (0,15,30,45,59,119)] for a in ARMS},torch=str(torch.__version__),
                  protected_evaluation_accessed=False)
    emit('manifest',**manifest)
    rows=[];models={}
    for seed in SEEDS:
        for arm in ARMS:
            emit('arm_started',arm=arm,seed=seed)
            row,model=train(arm,seed,fit,familiar,root,deadline)
            rows.append(row);models[seed,arm]=model;emit('arm_completed',**row)
    checks,eligible=eligibility(rows);emit('mastery_gate',checks=checks,eligible=eligible)
    scores=[];gates=[];cohort_hash=None
    if eligible:
        data=prepare(cases(TRANSFER_SEED,24,True),deadline);cohort_hash=datahash(data)
        if len(data)!=16 or sum(len(r[1]) for r in data)!=384:raise RuntimeError('transfer count')
        emit('transfer_manifest',cohort_sha256=cohort_hash,strata=len(data),paired_scenarios=24*len(data))
        for seed in SEEDS:
            results={}
            for arm in ARMS:
                results[arm]=evaluate(models[seed,arm],data,deadline)
                row=dict(seed=seed,arm=arm,score=results[arm]);scores.append(row);emit('transfer_score',**row)
            controls=tuple(results[k] for k in CONTROLS)
            rr=results[CANDIDATE];neg=results[NEGATIVE]
            gates.append(dict(seed=seed,primary=eligible and y.screen(rr,controls,neg)))
    if len(rows)!=30 or sum(r['steps'] for r in rows)!=86400 or sum(r['endpoint_steps_exposed'] for r in rows)!=22118400:
        raise RuntimeError('aggregate exposure mismatch')
    final=dict(arms_fitted=len(rows),updates=sum(r['steps'] for r in rows),
               endpoint_steps_exposed=sum(r['endpoint_steps_exposed'] for r in rows),
               mastery_checks=checks,eligible=eligible,transfer_executed=bool(scores),transfer_checks=gates,
               primary_screen=bool(gates) and all(g['primary'] for g in gates),
               scientific_gain_verified=False,compute_parity_verified=False,cold_retention_verified=False,
               protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,arms=rows,cohort_sha256=cohort_hash,scores=scores,result=final))
    with a.receipt.open('xb') as f:f.write(payload)
    if digest(a.receipt.read_bytes())!=digest(payload):raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
