"""WSP43 maximum-first exact-coefficient and recovery boundary assay."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from model import NumericModel,GF2Regression,acquire
from heuristic import acquire as heuristic_acquire
from world import World,rng_for


def run(cohort):
    pre=Path(__file__).with_name('prereg.json');p=json.loads(pre.read_text())
    started=time.perf_counter();trace=hashlib.sha256()
    result={'schema':'wsp43.result.v1','cohort':cohort,'episodes':[],'screens':[],'timings':{}}
    for width,family,ceiling,seed in itertools.product(p['dimensions_max_first'],p['families'],p['budgets_max_first'],p['split'][cohort]):
        budget=min(ceiling,(1<<width)-32)
        if budget<width+1:
            screen=dict(width=width,family=family,budget=ceiling,seed=seed,reason='basis_exceeds_budget',executed=False)
            result['screens'].append(screen);trace.update(json.dumps(screen,sort_keys=True).encode());continue
        tag=f'WSP43|{cohort}|{seed}|{width}|{family}'
        world=World(width,family,tag)
        t=time.perf_counter();model,basis,transcript,stats=acquire(width,world.apply,budget)
        costs={'exact_construct_s':time.perf_counter()-t}
        t=time.perf_counter();heuristic,_,hrows,hstats=heuristic_acquire(width,world.apply,budget)
        costs['heuristic_construct_s']=time.perf_counter()-t
        t=time.perf_counter();fitted=GF2Regression(width,transcript,model)
        costs['gf2_fit_s']=time.perf_counter()-t
        arms={'direct':model,'heuristic':heuristic,'fitted_same_features':fitted,'basis_only':basis,'zero':NumericModel(width,((),()))}
        seen={(a,x) for a,x,y in transcript};hseen={(a,x) for a,x,y in hrows}
        rng=rng_for(tag+'|evaluation');probes=[]
        while len(probes)<64:
            pair=(rng.randrange(2),rng.randrange(1<<width))
            if pair not in seen:probes.append(pair)
        sequences=[(rng.randrange(1<<width),tuple(rng.randrange(2) for _ in range((2,3,4)[i%3]))) for i in range(24)]
        goals=[]
        for _ in range(4):
            x=rng.randrange(1<<width);aa=tuple(rng.randrange(2) for _ in range(3));goals.append((x,world.rollout(x,aa)))
        scores={}
        for name,arm in arms.items():
            t=time.perf_counter();predictions=[arm.apply(a,x) for a,x in probes]
            composed=[arm.rollout(x,aa) for x,aa in sequences];plans=[arm.plan(x,g) for x,g in goals]
            scores[name]={'heldout':sum(y==world.apply(a,x) for y,(a,x) in zip(predictions,probes)),
                          'composed':sum(y==world.rollout(x,aa) for y,(x,aa) in zip(composed,sequences)),
                          'plans':sum(aa is not None and world.rollout(x,aa)==g for aa,(x,g) in zip(plans,goals))}
            costs[name+'_infer_plan_s']=time.perf_counter()-t
            if name=='direct':direct_predictions=predictions
        false={}
        exact={}
        for name,arm in (('direct',model),('heuristic',heuristic)):
            false[name]=sum(c!=dict(truth).get(m,0) for group,truth in zip(arm.groups,world.groups) for m,c in group)
            exact[name]=sum(group==truth for group,truth in zip(arm.groups,world.groups))
        assert false['direct']==0,'WRONG_EXACT_COEFFICIENT'
        snap=model.snapshot();restored=NumericModel.restore(snap)
        assert [restored.apply(a,x) for a,x in probes]==direct_predictions
        t=time.perf_counter();second=World(width,family,tag+'|second')
        other,_,secondary_rows,_=acquire(width,second.apply,budget)
        assert model.snapshot()==snap and NumericModel.restore(other.snapshot()).snapshot()==other.snapshot()
        costs['secondary_retention_construct_s']=time.perf_counter()-t
        try:NumericModel.restore(snap[:-1]+(b'0' if snap[-1:]!=b'0' else b'1'))
        except ValueError:pass
        else:raise AssertionError('tamper accepted')
        e=dict(width=width,family=family,budget=ceiling,effective_budget=budget,seed=seed,scores=scores,exact_maps=exact,
               false_coefficients=false,stats=stats,heuristic_stats=hstats,heuristic_seen_eval=sum(pair in hseen for pair in probes),
               gf2_ranks=fitted.ranks,gf2_inconsistent=fitted.inconsistent,gf2_training_errors=fitted.training_errors,
               snapshot_bytes=len(snap),resident_binary_coefficients=sum(len(g)*(2*width+1) for g in model.groups),
               cache_payload_bits=len(transcript)*2*width,secondary_queries=len(secondary_rows),cold=True)
        trace.update(json.dumps([e,transcript,hrows],sort_keys=True,separators=(',',':')).encode())
        result['episodes'].append(e)
        for name,value in costs.items():result['timings'][name]=result['timings'].get(name,0)+value
    result['trace_sha256']=trace.hexdigest();result['total_seconds']=time.perf_counter()-started
    result['source']={'python':sys.version,'platform':platform.platform(),'prereg_sha256':hashlib.sha256(pre.read_bytes()).hexdigest()}
    try:result['source'].update(sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip())
    except subprocess.CalledProcessError:result['source']['sha']='LOCAL_DEV'
    subset=[e for e in result['episodes'] if e['width']<=32 and e['family'] in ('eight_nonlinear','sixteen_nonlinear') and e['budget']==1024]
    m={key:sum(e['scores']['direct'][key] for e in subset)/(len(subset)*n) for key,n in (('heldout',64),('composed',24),('plans',4))}
    m['exact_map_fraction']=sum(e['exact_maps']['direct'] for e in subset)/(2*len(subset))
    m['gain_over_heuristic']=m['heldout']-sum(e['scores']['heuristic']['heldout'] for e in subset)/(len(subset)*64)
    result['bounded_metrics']=m
    gain=m['heldout']>=.95 and m['composed']>=.90 and m['plans']>=.90 and m['exact_map_fraction']>=.90 and m['gain_over_heuristic']>=.05
    result['classification']='DEV_SUPPORTED_EXACT_COEFFICIENT_GAIN' if gain else 'MIXED_EXACT_INVARIANT_GAIN_THRESHOLD_MISSED'
    result['independent_scientific_pass']=False
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cohort',choices=('DEV','PRIMARY'),default='DEV')
    print('WSP43_RESULT '+json.dumps(run(parser.parse_args().cohort),sort_keys=True))
