"""Actual action-cycle coordinate acquisition with two-point operator fit."""
import argparse,hashlib,itertools,json,platform,subprocess,sys,time
from pathlib import Path
from coordinates import CycleModel
from domains import LatentWorld,Encoding,EncodedSource,rng_for
from raw_equations import EquationBank,BankModel,AdaptiveModel

def bitreverse(x,w):return sum(((x>>i)&1)<<(w-1-i) for i in range(w))

def evaluate(model,raw,world,enc,rows,phase,tag):
    n=model.size;facts={(a,x):y for a,x,y in rows};unseen=[x for x in range(n) if (1,enc.encode(x)) not in facts];rng=rng_for(tag+'|'+phase)
    probes=[rng.choice(unseen) for _ in range(64)] if unseen else [];allpairs=[(a,x) for a in range(2) for x in range(n)]
    seq=[(rng.randrange(n),tuple(rng.randrange(2) for _ in range((2,3,4)[i%3]))) for i in range(24)];goals=[]
    for _ in range(4):
        x=rng.randrange(n);aa=tuple(rng.randrange(2) for _ in range(3));goals.append((x,world.rollout(x,aa)))
    snap=model.snapshot();restored=CycleModel.restore(snap);assert restored.snapshot()==snap
    try:CycleModel.restore(snap+b'x')
    except ValueError:pass
    else:raise AssertionError('tamper accepted')
    assert all(restored.apply(a,x)==model.apply(a,x) for a,x in allpairs),'COLD_REPLAY'
    for rm in raw.models:
        for b in rm.banks:
            s=b.snapshot();assert EquationBank.restore(s).snapshot()==s
    scores={}
    for name,arm in [('acquired_coordinates',model),('frozen_raw',raw)]:
        pred=[arm.apply(a,enc.encode(x)) for a,x in allpairs];plans=[arm.plan(enc.encode(x),enc.encode(g)) for x,g in goals]
        score=dict(unseen_action1=sum(arm.apply(1,enc.encode(x))==enc.encode(world.apply(1,x)) for x in probes),full_replay=sum(y==enc.encode(world.apply(a,x)) for y,(a,x) in zip(pred,allpairs)),known=sum(y is not None for y in pred),wrong_known=sum(y is not None and y!=enc.encode(world.apply(a,x)) for y,(a,x) in zip(pred,allpairs)),
                   observed_recall=sum(arm.apply(a,x)==y for (a,x),y in facts.items()),composed=sum(arm.rollout(enc.encode(x),aa)==enc.encode(world.rollout(x,aa)) for x,aa in seq),plans=sum(aa is not None and world.rollout(x,aa)==g for aa,(x,g) in zip(plans,goals)))
        assert score['observed_recall']==len(facts),'FACT_RECALL';scores[name]=score
    scores['onehot']=dict(unseen_action1=0,observed_recall=len(facts),full_replay=len(facts))
    return dict(phase=phase,source_actions=len(rows),unique_observed=len(facts),observed_action1=sum(a==1 for a,x in facts),unseen_total=len(probes),unseen_available=len(unseen),all_pairs=2*n,cycle_valid=model.valid,prior_fitted=model.fitted,prior_rejected=model.rejected,parameters=dict(m=model.m,b=model.b),scores=scores,cold=True,
                coordinate_register_payload_bits=2*n*model.width+n+2*n*(model.width+1)+2*model.width+3,raw_equation_register_payload_bits=sum(b.M*(b.M+model.width+1)+n*(model.width+1)+1 for m in raw.models for b in m.banks),counterworld_possible=bool(unseen))

def run(cohort):
    pre=Path(__file__).with_name('prereg.json');p=json.loads(pre.read_text());start=time.perf_counter();trace=hashlib.sha256();result=dict(schema='wsp50.result.v1',cohort=cohort,episodes=[],timings={},latent_equivalent_conditions=0)
    for width,family,seed in itertools.product(p['widths'],p['families'],p['split'][cohort]):
        tag=f'WSP50|{cohort}|{seed}|{width}|{family}';world=LatentWorld(width,family,tag);latent_rows=None
        for kind in p['encodings']:
            enc=Encoding(width,kind,tag);source=EncodedSource(world,enc);model=CycleModel(width);raw=AdaptiveModel([BankModel([EquationBank(width,d) for _ in range(2)]) for d in (1,2,3,'full')]);state=0;rows=[];visits=[[0]*model.size for _ in range(2)];n=model.size
            def take(a):
                nonlocal state
                x=state;y=source.apply(a,x);model.observe(a,x,y)
                for rm in raw.models:rm.banks[a].observe(x,y)
                rows.append((a,x,y));visits[a][x]+=1;state=y
                assert len(rows)<=8192,'SOURCE_BUDGET'
                return x,y
            t=time.perf_counter()
            for index in range(n):model.record_cycle(state,index);take(0)
            model.certify(state);cycle_rows=rows[:];reference={x:i for i,(a,x,y) in enumerate(cycle_rows)};valid=int(len(reference)==n and state==0)
            assert model.valid==valid,'CYCLE_CERTIFICATE'
            if valid:
                assert all(model.coord(x)==i and model.decode(i)==x for x,i in reference.items()),'EXPERIENCE_COORDINATE_PARITY'
                _,first_y=take(1);model.fit_first(first_y)
                if not model.coord(state)&1:take(0)
                second_x,second_y=take(1);model.fit_second(second_x,second_y)
                ref_b=reference[first_y];ref_m=((reference[second_y]-ref_b)*pow(reference[second_x],-1,n))%n
                assert (model.b,model.m)==(ref_b,ref_m),'CONVENTIONAL_AFFINE_FIT_PARITY'
            result['timings']['acquire_and_fit_s']=result['timings'].get('acquire_and_fit_s',0)+time.perf_counter()-t
            t=time.perf_counter();e=evaluate(model,raw,world,enc,rows,'post_fit',tag);e.update(width=width,family=family,seed=seed,encoding=kind,reference_fit_parity=bool(valid));result['episodes'].append(e);trace.update(json.dumps([e,rows],sort_keys=True,separators=(',',':')).encode());result['timings']['evaluation_s']=result['timings'].get('evaluation_s',0)+time.perf_counter()-t
            t=time.perf_counter()
            if valid:
                targets=[bitreverse(i,width) for i in range(n) if not model.fact(1,model.decode(bitreverse(i,width)))[1]][:16]
                for target in targets:
                    count=0
                    while model.coord(state)!=target:
                        take(0);count+=1;assert count<=n,'NAVIGATION'
                    take(1)
            else:
                for _ in range(16):take(int(visits[0][state]>visits[1][state]))
            result['timings']['validation_source_and_update_s']=result['timings'].get('validation_source_and_update_s',0)+time.perf_counter()-t
            decoded=[(a,enc.decode(x),enc.decode(y)) for a,x,y in rows]
            if latent_rows is None:latent_rows=decoded
            else:assert decoded==latent_rows,'ENCODING_TRAJECTORY_INFORMATION_MISMATCH'
            result['latent_equivalent_conditions']+=1
            t=time.perf_counter();e=evaluate(model,raw,world,enc,rows,'post_validation',tag);e.update(width=width,family=family,seed=seed,encoding=kind,reference_fit_parity=bool(valid));result['episodes'].append(e);trace.update(json.dumps([e,rows],sort_keys=True,separators=(',',':')).encode());result['timings']['evaluation_s']+=time.perf_counter()-t
    positive=[e for e in result['episodes'] if e['family']=='affine' and e['phase']=='post_fit'];metrics={}
    for k in p['encodings']:
        es=[e for e in positive if e['encoding']==k];total=sum(e['unseen_total'] for e in es)
        metrics[k]=dict(correct=sum(e['scores']['acquired_coordinates']['unseen_action1'] for e in es),total=total,accuracy=sum(e['scores']['acquired_coordinates']['unseen_action1'] for e in es)/total if total else None,raw_correct=sum(e['scores']['frozen_raw']['unseen_action1'] for e in es),worlds_without_unseen=sum(e['unseen_total']==0 for e in es))
    neg=[e for e in result['episodes'] if e['phase']=='post_validation' and e['family'] in ('quadratic_second','random_second')];reject=sum(e['prior_rejected'] for e in neg)/len(neg)
    reject_by_family={f:sum(e['prior_rejected'] for e in neg if e['family']==f)/sum(e['family']==f for e in neg) for f in ('quadratic_second','random_second')}
    passed=all(m['total'] and m['accuracy']>=.99 for m in metrics.values()) and metrics['identity']['accuracy']-metrics['random_permutation']['accuracy']<=.01 and all(v>=.90 for v in reject_by_family.values())
    result.update(bounded_metrics=dict(affine_post_fit_unseen=metrics,negative_rejection_rate=reject,negative_rejection_by_family=reject_by_family,threshold_pass=passed),classification='DEV_SUPPORTED_ACQUIRED_CYCLE_COORDINATES' if passed else 'MIXED_ACQUIRED_CYCLE_BOUNDARY',independent_scientific_pass=False,trace_sha256=trace.hexdigest(),total_seconds=time.perf_counter()-start,source=dict(python=sys.version,platform=platform.platform(),prereg_sha256=hashlib.sha256(pre.read_bytes()).hexdigest()))
    try:result['source'].update(sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip())
    except subprocess.CalledProcessError:result['source']['sha']='LOCAL_DEV'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cohort',choices=('DEV','PRIMARY'),default='DEV');print('WSP50_RESULT '+json.dumps(run(p.parse_args().cohort),sort_keys=True))
