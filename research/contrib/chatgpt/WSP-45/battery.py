"""WSP45 fixed numerical learning, low-degree transfer and full-table bounds."""
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
from numeric import NumericLearner,ActionModel


def rng_for(tag):return random.Random(int.from_bytes(hashlib.sha256(tag.encode()).digest(),'big'))


class World:
    def __init__(self,width,family,tag):
        self.width,self.family,self.tag=width,family,tag
        rng=rng_for(tag);self.rows=[];self.bias=[];self.terms=[]
        for action in range(2):
            self.rows.append(tuple(tuple(rng.sample(range(width),4)) for _ in range(width)))
            self.bias.append(rng.randrange(1<<width));terms=[];used=set()
            degree={'linear':0,'quadratic':2,'cubic_ood':3,'arbitrary_hash':0}[family]
            while degree and len(used)<4:
                indices=tuple(sorted(rng.sample(range(width),degree)))
                if indices in used:continue
                used.add(indices);terms.append((indices,rng.randrange(1,1<<width)))
            self.terms.append(tuple(terms))

    def apply(self,action,state):
        if self.family=='arbitrary_hash':return hashlib.sha256(f'{self.tag}|{action}|{state}'.encode()).digest()[0]&((1<<self.width)-1)
        out=self.bias[action]
        for bit,inputs in enumerate(self.rows[action]):out^=(sum(state>>i&1 for i in inputs)%2)<<bit
        for inputs,c in self.terms[action]:
            if all(state>>i&1 for i in inputs):out^=c
        return out

    rollout=ActionModel.rollout


class ExternalCompiler:
    """Independent external symbolic transform, identical facts/certificate prior."""
    def __init__(self,width,rows):
        self.width=width;self.coeff=[];self.facts=[]
        for action in range(2):
            facts={x:y for a,x,y in rows if a==action};self.facts.append(facts)
            coeff=[facts.get(x,0) for x in range(1<<width)]
            for bit in range(width):
                for mask in range(1<<width):
                    if mask>>bit&1:coeff[mask]^=coeff[mask^(1<<bit)]
            self.coeff.append([c if all(t in facts for t in range(1<<width) if t&mask==t) else 0 for mask,c in enumerate(coeff)])
    def apply(self,action,state):
        out=0
        for mask,c in enumerate(self.coeff[action]):
            if state&mask==mask:out^=c
        return out
    rollout=ActionModel.rollout
    plan=ActionModel.plan


class TrainedOneHot:
    """Closed-form least-squares optimum of one-hot source-state regressors."""
    def __init__(self,width,rows):
        self.width=width;self.weights=[{} for _ in range(2)]
        for a,x,y in rows:self.weights[a][x]=y
        self.training_errors=sum(self.apply(a,x)!=y for a,x,y in rows)
    def apply(self,action,state):return self.weights[action].get(state,0)
    rollout=ActionModel.rollout
    plan=ActionModel.plan


def run(cohort):
    pre=Path(__file__).with_name('prereg.json');p=json.loads(pre.read_text());started=time.perf_counter()
    result=dict(schema='wsp45.result.v1',cohort=cohort,episodes=[],timings={});trace=hashlib.sha256()
    for width,family,seed in itertools.product(p['widths_max_first'],p['families'],p['split'][cohort]):
        tag=f'WSP45|{cohort}|{seed}|{width}|{family}';world=World(width,family,tag);size=1<<width
        learners=[NumericLearner(width) for _ in range(2)];candidate=ActionModel(learners);transcript=[];previous=0;costs={}
        teacher_coeff=[]
        for action in range(2):
            values=[world.apply(action,x) for x in range(size)]
            for bit in range(width):
                for mask in range(size):
                    if mask>>bit&1:values[mask]^=values[mask^(1<<bit)]
            teacher_coeff.append(values)
        phases=(('linear_basis',width+1),('quadratic_basis',1+width+width*(width-1)//2),('full_truth',size))
        for phase,target in phases:
            t=time.perf_counter()
            for action,m in enumerate(learners):
                for _ in range(previous,target):
                    x=m.choose()
                    if x is None:raise AssertionError('premature numeric done')
                    y=world.apply(action,x);m.observe(x,y);transcript.append((action,x,y))
            costs['numeric_acquisition_s']=costs.get('numeric_acquisition_s',0)+time.perf_counter()-t;previous=target
            t=time.perf_counter();external=ExternalCompiler(width,transcript);trained=TrainedOneHot(width,transcript)
            costs['external_compile_fit_s']=costs.get('external_compile_fit_s',0)+time.perf_counter()-t
            if phase=='full_truth':probes=[(a,x) for a in range(2) for x in range(size)];kind='EXHAUSTIVE_TRAINED_STATE_REPLAY'
            else:
                rng=rng_for(tag+'|'+phase);probes=[]
                for action,m in enumerate(learners):
                    unseen=[x for x,seen in enumerate(m.seen) if not seen]
                    probes.extend((action,rng.choice(unseen)) for _ in range(32))
                kind='UNSEEN_TO_ALL_TRANSCRIPT_ARMS_WITH_REPLACEMENT'
            rng=rng_for(tag+'|sequences|'+phase)
            sequences=[(rng.randrange(size),tuple(rng.randrange(2) for _ in range((2,3,4)[i%3]))) for i in range(24)]
            goals=[]
            for _ in range(4):
                x=rng.randrange(size);aa=tuple(rng.randrange(2) for _ in range(3));goals.append((x,world.rollout(x,aa)))
            scores={};zero=ActionModel([NumericLearner(width) for _ in range(2)])
            t=time.perf_counter()
            for name,model in (('numeric',candidate),('external',external),('trained_onehot',trained),('disabled_learning',zero)):
                values=[model.apply(a,x) for a,x in probes];composed=[model.rollout(x,aa) for x,aa in sequences];plans=[model.plan(x,g) for x,g in goals]
                scores[name]=dict(one_step=sum(y==world.apply(a,x) for y,(a,x) in zip(values,probes)),composed=sum(y==world.rollout(x,aa) for y,(x,aa) in zip(composed,sequences)),plans=sum(aa is not None and world.rollout(x,aa)==g for aa,(x,g) in zip(plans,goals)))
                if name=='numeric':direct_values=values
                if name=='external':assert direct_values==values
            costs['evaluation_s']=costs.get('evaluation_s',0)+time.perf_counter()-t
            snapshots=[];certified=0
            for action,m in enumerate(learners):
                coeff=[sum(v<<j for j,v in enumerate(row)) for row in m.coefficients()]
                assert coeff==external.coeff[action]
                for mask,c in enumerate(coeff):
                    ready=m.counts[mask]==1<<mask.bit_count()
                    assert not ready or c==teacher_coeff[action][mask]
                    certified+=ready
                snapshot=m.snapshot();restored=NumericLearner.restore(snapshot);assert restored.snapshot()==snapshot
                snapshots.append(snapshot)
            e=dict(width=width,family=family,seed=seed,phase=phase,queries=2*target,evaluation_kind=kind,one_step_total=len(probes),scores=scores,
                   certified_coefficients=certified,trained_converged=trained.training_errors==0,cold=True,snapshot_bytes=sum(map(len,snapshots)))
            result['episodes'].append(e);trace.update(json.dumps([e,transcript],sort_keys=True,separators=(',',':')).encode())
        t=time.perf_counter();frozen=[m.snapshot() for m in learners]
        other=World(width,family,tag+'|second');other_models=[NumericLearner(width) for _ in range(2)]
        for a,m in enumerate(other_models):
            for _ in range(size):
                x=m.choose();m.observe(x,other.apply(a,x))
        assert [m.snapshot() for m in learners]==frozen
        second_frozen=[m.snapshot() for m in other_models]
        edit=(seed+width)%size;replacement=world.apply(0,edit)^1
        learners[0].observe(edit,replacement)
        assert learners[0].fault==1 and learners[1].snapshot()==frozen[1]
        assert [m.snapshot() for m in other_models]==second_frozen
        repaired_rows=tuple((a,x,replacement if a==0 and x==edit else world.apply(a,x)) for a in range(2) for x in range(size))
        repaired=ExternalCompiler(width,repaired_rows)
        assert all(candidate.apply(a,x)==repaired.apply(a,x) for a in range(2) for x in range(size))
        repair=dict(width=width,family=family,seed=seed,repair=True,extra_source_replies=1,secondary_source_replies=2*size,
                    threshold_evaluations=sum(m.threshold_evaluations for m in learners),resident_task_bits=2*(2*size*width+size+1),resident_bounded_counts=2*size)
        trace.update(json.dumps(repair,sort_keys=True).encode());result.setdefault('repairs',[]).append(repair)
        costs['retention_repair_s']=time.perf_counter()-t
        for key,value in costs.items():result['timings'][key]=result['timings'].get(key,0)+value
    positives=[e for e in result['episodes'] if (e['family'],e['phase']) in (('linear','linear_basis'),('quadratic','quadratic_basis')) or e['phase']=='full_truth']
    positive=all(e['scores']['numeric']['one_step']==e['one_step_total'] and e['scores']['numeric']['composed']==24 and e['scores']['numeric']['plans']==4 for e in positives)
    negatives=[e for e in result['episodes'] if e['family'] in ('cubic_ood','arbitrary_hash') and e['phase']!='full_truth']
    negative=all(any(e['scores']['numeric']['one_step']<e['one_step_total'] for e in negatives if e['family']==family and e['phase']==phase)
                 for family in ('cubic_ood','arbitrary_hash') for phase in ('linear_basis','quadratic_basis'))
    result.update(classification='DEV_SUPPORTED_NUMERIC_ACQUISITION' if positive and negative else 'MIXED_OR_NEGATIVE_FROZEN_BOUNDS_MISSED',independent_scientific_pass=False,
                  bounded_metrics=dict(positive_pass=positive,negative_failure_preserved=negative,positive_conditions=len(positives)),trace_sha256=trace.hexdigest(),total_seconds=time.perf_counter()-started,
                  source=dict(python=sys.version,platform=platform.platform(),prereg_sha256=hashlib.sha256(pre.read_bytes()).hexdigest()))
    try:result['source'].update(sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip())
    except subprocess.CalledProcessError:result['source']['sha']='LOCAL_DEV'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cohort',choices=('DEV','PRIMARY'),default='DEV')
    print('WSP45_RESULT '+json.dumps(run(parser.parse_args().cohort),sort_keys=True))
