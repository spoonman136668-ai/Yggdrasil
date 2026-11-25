"""UJ05B B0: fresh matched stable-schedule transfer; reuse A0 implementation."""
import argparse
import re
import time
from pathlib import Path
import torch
import uj05a_stability_pilot as a
import uj04y_intervention_pilot as y
from uj03a_pilot import canonical,digest,check_deadline

CORE=('dense_decay_full','dense_decay_curriculum','relational_decay_full',
      'relational_decay_curriculum','dense_teacher','relational_teacher')
ARMS=CORE+('relational_jepa','relational_shuffled_aux','relational_shuffled_result')
CANDIDATE='relational_decay_curriculum'
CONTROLS=tuple(k for k in CORE if k!=CANDIDATE)
SEEDS=(3201,3202,3203)
FIT_SEED=321100
FAMILIAR_SEED=321200
TRANSFER_SEED=321300
EPOCHS=a.EPOCHS
BATCH=a.BATCH
HORIZON=a.HORIZON
TOTAL_SECONDS=10800
cases=a.cases
prepare=a.prepare
datahash=a.datahash
schedule=a.schedule
train=a.train
evaluate=a.evaluate

def emit(event,**fields):
    print('UJ05B '+canonical(dict(event=event,**fields)).decode(),flush=True)

def assert_disjoint_seeds():
    ranges=[set(range(start,start+n)) for start,n in ((FIT_SEED,6),(FAMILIAR_SEED,6),(TRANSFER_SEED,16))]
    historical=set()
    for bases in ((301100,301200,301300),(311100,311200,311300)):
        for start,n in zip(bases,(6,6,16)):
            historical.update(range(start,start+n))
    if any(r & historical for r in ranges) or any(r & s for i,r in enumerate(ranges) for s in ranges[i+1:]):
        raise RuntimeError('split seed overlap')
    if len(set(SEEDS))!=3 or set(SEEDS)&set(a.SEEDS) or set(SEEDS)&{3001,3002,3003}:
        raise RuntimeError('training seed overlap')

def eligibility(rows,seeds=SEEDS):
    if len(rows)!=len(seeds)*len(ARMS) or len({(r['seed'],r['arm']) for r in rows})!=len(rows):
        raise RuntimeError('incomplete or duplicate arms')
    checks=[]
    for seed in seeds:
        by={r['arm']:r for r in rows if r['seed']==seed}
        if set(by)!=set(ARMS):raise RuntimeError('unexpected arms')
        def ok(k):
            return by[k]['adequate'] and 0<=by[k]['after']['familiar']['rollout']<=.15
        core=all(ok(k) for k in CORE)
        checks.append(dict(seed=seed,primary=core,jepa=core and ok('relational_jepa') and ok('relational_shuffled_aux')))
    return checks,{k:all(c[k] for c in checks) for k in ('primary','jepa')}

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
    if any(eligible.values()):
        data=prepare(cases(TRANSFER_SEED,24,True),deadline);cohort_hash=datahash(data)
        if len(data)!=16 or sum(len(r[1]) for r in data)!=384:raise RuntimeError('transfer count')
        emit('transfer_manifest',cohort_sha256=cohort_hash,strata=len(data),paired_scenarios=24*len(data))
        for seed in SEEDS:
            results={}
            for arm in ARMS:
                results[arm]=evaluate(models[seed,arm],data,deadline)
                row=dict(seed=seed,arm=arm,score=results[arm]);scores.append(row);emit('transfer_score',**row)
            controls=tuple(results[k] for k in CONTROLS)
            rr=results[CANDIDATE];j=results['relational_jepa'];sh=results['relational_shuffled_aux'];neg=results['relational_shuffled_result']
            gates.append(dict(seed=seed,primary=eligible['primary'] and y.screen(rr,controls,neg),
                              jepa=eligible['jepa'] and y.screen(j,controls+(rr,sh),neg)))
    if len(rows)!=27 or sum(r['steps'] for r in rows)!=77760 or sum(r['endpoint_steps_exposed'] for r in rows)!=19906560:
        raise RuntimeError('aggregate exposure mismatch')
    final=dict(arms_fitted=len(rows),updates=sum(r['steps'] for r in rows),
               endpoint_steps_exposed=sum(r['endpoint_steps_exposed'] for r in rows),
               mastery_checks=checks,eligible=eligible,transfer_executed=bool(scores),transfer_checks=gates,
               **{k+'_screen':bool(gates) and all(g[k] for g in gates) for k in ('primary','jepa')},
               scientific_gain_verified=False,compute_parity_verified=False,cold_retention_verified=False,
               protected_evaluation_accessed=False)
    check_deadline(deadline)
    payload=canonical(dict(manifest=manifest,arms=rows,cohort_sha256=cohort_hash,scores=scores,result=final))
    with a.receipt.open('xb') as f:f.write(payload)
    if digest(a.receipt.read_bytes())!=digest(payload):raise RuntimeError('receipt readback')
    emit('complete',receipt_sha256=digest(payload),**final)

if __name__=='__main__':
    main()
