"""Frozen complete hidden vector-map study, sparse and cancellation boundaries."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
from model import NumericModel,SymbolicExecution,KernelRegression,acquire


def rng_for(tag):return random.Random(int.from_bytes(hashlib.sha256(tag.encode()).digest(),'big'))


class World:
    def __init__(self,width,family,tag):
        self.width=width
        rng=rng_for(tag)
        self.rows=[];self.biases=[];self.nonlinear=[];self.groups=[]
        for action in range(2):
            rows=tuple(tuple(rng.sample(range(width),4)) for _ in range(width))
            bias=rng.getrandbits(width)
            nonlinear=[];used=set()
            count={'affine':0,'four_nonlinear':4,'eight_nonlinear':8}[family]
            while len(used)<count:
                indices=tuple(sorted(rng.sample(range(width),rng.randint(2,4))))
                if indices in used:continue
                used.add(indices)
                nonlinear.append((indices,rng.randrange(1,1<<width)))
            self.rows.append(rows);self.biases.append(bias);self.nonlinear.append(tuple(nonlinear))
            coefficients={0:bias} if bias else {}
            for output,inputs in enumerate(rows):
                for index in inputs:coefficients[1<<index]=coefficients.get(1<<index,0)^(1<<output)
            for indices,coefficient in nonlinear:coefficients[sum(1<<i for i in indices)]=coefficient
            self.groups.append(tuple(sorted((m,c) for m,c in coefficients.items() if c)))

    def apply(self,action,state):
        # Teacher evaluates independent output equations, never numerical model.
        result=self.biases[action]
        for bit,inputs in enumerate(self.rows[action]):
            parity=0
            for i in inputs:parity^=state>>i&1
            result^=parity<<bit
        for inputs,coefficient in self.nonlinear[action]:
            if all(state>>i&1 for i in inputs):result^=coefficient
        return result

    rollout=NumericModel.rollout


def run(cohort):
    pre=Path(__file__).with_name('prereg.json');p=json.loads(pre.read_text())
    started=time.perf_counter();trace=hashlib.sha256()
    result={'schema':'wsp42.result.v1','cohort':cohort,'episodes':[],'timings':{}}
    for width,family,budget,seed in itertools.product(p['dimensions_max_first'],p['families'],p['budgets_per_action'],p['split'][cohort]):
        tag=f'WSP42|{cohort}|{seed}|{width}|{family}'
        world=World(width,family,tag)
        t=time.perf_counter()
        model,basis,transcript,stats=acquire(width,world.apply,budget)
        costs={'direct_construct_s':time.perf_counter()-t}
        t=time.perf_counter();fitted=KernelRegression(width,transcript)
        costs['trained_kernel_fit_s']=time.perf_counter()-t
        arms={'direct':model,'basis_only':basis,'trained':fitted,'symbolic_execution':SymbolicExecution(model),'zero':NumericModel(width,((),()))}
        seen={(a,x) for a,x,y in transcript};rng=rng_for(tag+'|evaluation')
        probes=[]
        while len(probes)<64:
            pair=(rng.randrange(2),rng.randrange(1<<width))
            if pair not in seen:probes.append(pair)
        sequences=[(rng.randrange(1<<width),tuple(rng.randrange(2) for _ in range((2,3,4)[i%3]))) for i in range(24)]
        goals=[]
        for _ in range(4):
            x=rng.randrange(1<<width);aa=tuple(rng.randrange(2) for _ in range(3))
            goals.append((x,world.rollout(x,aa)))
        scores={}
        for name,arm in arms.items():
            t=time.perf_counter()
            predictions=[arm.apply(a,x) for a,x in probes]
            composed=[arm.rollout(x,aa) for x,aa in sequences]
            plans=[arm.plan(x,goal) for x,goal in goals]
            scores[name]={'heldout':sum(y==world.apply(a,x) for y,(a,x) in zip(predictions,probes)),
                          'composed':sum(y==world.rollout(x,aa) for y,(x,aa) in zip(composed,sequences)),
                          'plans':sum(aa is not None and world.rollout(x,aa)==goal for aa,(x,goal) in zip(plans,goals))}
            costs[name+'_infer_plan_s']=time.perf_counter()-t
            if name=='direct':direct_predictions,direct_composed=predictions,composed
            if name=='symbolic_execution':assert predictions==direct_predictions and composed==direct_composed
        snap=model.snapshot();restored=NumericModel.restore(snap)
        assert [restored.apply(a,x) for a,x in probes]==direct_predictions
        t=time.perf_counter();second=World(width,family,tag+'|second')
        other,_,other_transcript,_=acquire(width,second.apply,budget)
        assert model.snapshot()==snap and NumericModel.restore(other.snapshot()).snapshot()==other.snapshot()
        costs['secondary_retention_construct_s']=time.perf_counter()-t
        try:NumericModel.restore(snap[:-1]+(b'0' if snap[-1:]!=b'0' else b'1'))
        except ValueError:pass
        else:raise AssertionError('tamper accepted')
        e={'width':width,'family':family,'budget':budget,'seed':seed,'scores':scores,'stats':stats,
           'exact_maps':sum(g==truth for g,truth in zip(model.groups,world.groups)),
           'trained_converged':max(fitted.max_errors)<=1e-7,'snapshot_bytes':len(snap),
           'resident_binary_coefficients':sum(len(g)*(2*width+1) for g in model.groups),
           'cache_payload_bits':len(transcript)*2*width,'kernel_float_coefficients':len(transcript)*width,
           'secondary_queries':len(other_transcript),'cold':True}
        trace.update(json.dumps([e,transcript],sort_keys=True,separators=(',',':')).encode())
        result['episodes'].append(e)
        for name,value in costs.items():result['timings'][name]=result['timings'].get(name,0)+value
    result['trace_sha256']=trace.hexdigest();result['total_seconds']=time.perf_counter()-started
    result['source']={'python':sys.version,'platform':platform.platform(),'prereg_sha256':hashlib.sha256(pre.read_bytes()).hexdigest()}
    try:result['source'].update(sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip())
    except subprocess.CalledProcessError:result['source']['sha']='LOCAL_DEV'
    metrics={}
    for family in p['families']:
        es=[e for e in result['episodes'] if e['family']==family and e['budget']==128]
        m={key:sum(e['scores']['direct'][key] for e in es)/(len(es)*n) for key,n in (('heldout',64),('composed',24),('plans',4))}
        m['exact_map_fraction']=sum(e['exact_maps'] for e in es)/(2*len(es))
        m['gain_over_basis']=m['heldout']-sum(e['scores']['basis_only']['heldout'] for e in es)/(len(es)*64)
        metrics[family]=m
    result['bounded_metrics']=metrics
    a=metrics['affine'];n=metrics['four_nonlinear']
    affine_ok=all(a[k]==1 for k in ('heldout','composed','plans','exact_map_fraction'))
    nonlinear_ok=n['heldout']>=.95 and n['composed']>=.90 and n['plans']>=.90 and n['exact_map_fraction']>=.90 and n['gain_over_basis']>=.10
    result['classification']='DEV_SUPPORTED_BOUNDED_FULLMAP' if affine_ok and nonlinear_ok else 'MIXED_FULLMAP_NONLINEAR_BOUNDARY' if affine_ok else 'SCIENTIFIC_NEGATIVE_FROZEN_BOUNDS_MISSED'
    result['independent_scientific_pass']=False
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cohort',choices=('DEV','PRIMARY'),default='DEV')
    print('WSP42_RESULT '+json.dumps(run(parser.parse_args().cohort),sort_keys=True))
