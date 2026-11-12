"""WSP47 identical-trajectory equation inference and explicit prior uncertainty."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from equations import EquationBank,BankModel,AdaptiveModel
from reference import BatchBank,BatchModel,BatchAdaptive
from trajectory import TrajectoryAgent,TrainedOneHot
from world import World,rng_for


def reachable_states(world):
    reached={0};queue=[0]
    while queue:
        state=queue.pop()
        for action in range(2):
            nxt=world.apply(action,state)
            if nxt not in reached:reached.add(nxt);queue.append(nxt)
    return tuple(sorted(reached))


def run(cohort):
    pre=Path(__file__).with_name('prereg.json');p=json.loads(pre.read_text());started=time.perf_counter();trace=hashlib.sha256()
    result=dict(schema='wsp47.result.v1',cohort=cohort,episodes=[],timings={})
    degrees=(1,2,3,'full')
    for width,family,seed in itertools.product(p['widths_max_first'],p['families'],p['split'][cohort]):
        tag=f'WSP47|{cohort}|{seed}|{width}|{family}';world=World(width,family,tag);size=1<<width
        trajectory=TrajectoryAgent(width);models=[BankModel([EquationBank(width,d) for _ in range(2)]) for d in degrees];adaptive=AdaptiveModel(models)
        reached=reachable_states(world);rpairs=[(a,x) for a in range(2) for x in reached];allpairs=[(a,x) for a in range(2) for x in range(size)]
        previous=0;costs={}
        for budget in p['budgets']:
            trajectory_seconds=0.0;equation_seconds=0.0
            for _ in range(previous,budget):
                t=time.perf_counter();a,x,y=trajectory.transition(world.apply);trajectory_seconds+=time.perf_counter()-t
                t=time.perf_counter()
                for model in models:model.banks[a].observe(x,y)
                equation_seconds+=time.perf_counter()-t
            costs['frozen_source_and_learner_s']=costs.get('frozen_source_and_learner_s',0)+trajectory_seconds
            costs['numeric_equation_update_s']=costs.get('numeric_equation_update_s',0)+equation_seconds;previous=budget
            rows=trajectory.rows;seen={(a,x) for a,x,y in rows};unseen=[pair for pair in rpairs if pair not in seen];rng=rng_for(tag+'|'+str(budget))
            probes=[rng.choice(unseen) for _ in range(64)] if unseen else []
            sequences=[(rng.choice(reached),tuple(rng.randrange(2) for _ in range((2,3,4)[i%3]))) for i in range(24)]
            goals=[]
            for _ in range(4):
                x=rng.choice(reached);aa=tuple(rng.randrange(2) for _ in range(3));goals.append((x,world.rollout(x,aa)))
            t=time.perf_counter();refs=[BatchModel([BatchBank(width,d,[(x,y) for aa,x,y in rows if aa==a]) for a in range(2)]) for d in degrees]
            reference=BatchAdaptive(refs);costs['batch_reference_fit_s']=costs.get('batch_reference_fit_s',0)+time.perf_counter()-t
            for model,ref in zip(models,refs):
                assert all(model.apply(a,x)==ref.apply(a,x) for a,x in allpairs),'NUMERIC_REFERENCE_PARITY'
                for a in range(2):
                    assert model.banks[a].fault==int(ref.banks[a].fault)
                    snap=model.banks[a].snapshot();assert EquationBank.restore(snap).snapshot()==snap
                    try:EquationBank.restore(snap+b'x')
                    except ValueError:pass
                    else:raise AssertionError('tamper accepted')
            assert all(adaptive.apply(a,x)==reference.apply(a,x) for a,x in allpairs),'ADAPTIVE_REFERENCE_PARITY'
            matching={'linear':0,'quadratic':1,'cubic_ood':2,'arbitrary_hash':3}[family]
            assert all(models[matching].apply(a,x) in (None,world.apply(a,x)) for a,x in allpairs),'MATCHING_PRIOR_WRONG_KNOWN'
            trained=TrainedOneHot(rows);assert trained.training_errors==0
            arms={str(d):m for d,m in zip(degrees,models)};arms.update(adaptive=adaptive,frozen_subcube=trajectory,trained_onehot=trained,erased=BankModel([EquationBank(width,1) for _ in range(2)]))
            scores={};t=time.perf_counter()
            for name,model in arms.items():
                full=[model.apply(a,x) for a,x in allpairs];plans=[model.plan(x,g) for x,g in goals]
                scores[name]=dict(reachable_unseen=sum(model.apply(a,x)==world.apply(a,x) for a,x in probes),
                    reachable_replay=sum(model.apply(a,x)==world.apply(a,x) for a,x in rpairs),full_replay=sum(y==world.apply(a,x) for y,(a,x) in zip(full,allpairs)),
                    full_known=sum(y is not None for y in full),wrong_known=sum(y is not None and y!=world.apply(a,x) for y,(a,x) in zip(full,allpairs)),
                    wrong_known_unreachable=sum(y is not None and y!=world.apply(a,x) and x not in reached for y,(a,x) in zip(full,allpairs)),
                    wrong_known_unseen_reachable=sum(y is not None and y!=world.apply(a,x) and x in reached and (a,x) not in seen for y,(a,x) in zip(full,allpairs)),
                    observed_recall=sum(model.apply(a,x)==world.apply(a,x) for a,x in seen),
                    composed=sum(model.rollout(x,aa)==world.rollout(x,aa) for x,aa in sequences),plans=sum(aa is not None and world.rollout(x,aa)==g for aa,(x,g) in zip(plans,goals)))
            costs['evaluation_s']=costs.get('evaluation_s',0)+time.perf_counter()-t
            assert all(scores[str(d)]['observed_recall']==len(seen) for d in degrees),'OBSERVED_FACT_LOSS'
            assert scores['adaptive']['observed_recall']==len(seen)
            counterworld=None;not_seen=[pair for pair in allpairs if pair not in seen]
            if not_seen:
                a,x=not_seen[0];original=world.apply(a,x);other=original^1;prediction=adaptive.apply(a,x)
                assert all((other if aa==a and xx==x else world.apply(aa,xx))==y for aa,xx,y in rows)
                counterworld=dict(action=a,state=x,prediction=prediction,original=original,alternate=other,both_correct=False,same_observations=True)
            bank_stats={str(d):[dict(features=b.M,rank=sum(b.occupied),fault=b.fault,task_payload_bits=b.M*(b.M+width+1)+size*(width+1)+1,snapshot_bytes=len(b.snapshot())) for b in m.banks] for d,m in zip(degrees,models)}
            e=dict(width=width,family=family,seed=seed,budget=budget,source_replies=len(rows),source_resets=trajectory.resets,unique_observed=len(seen),reachable_pairs=len(rpairs),all_pairs=len(allpairs),
                   reachable_unseen_total=len(probes),unseen_available=len(unseen),evaluation_kind='UNSEEN_REACHABLE' if probes else 'NO_UNSEEN_REACHABLE_CASES',scores=scores,
                   bank_stats=bank_stats,selected_bank_indices=[sum(w*i for i,w in enumerate(adaptive.selected(a))) for a in range(2)],
                   counterworld=counterworld,cold=True,reference_parity=True,matching_prior_validity=True)
            trace.update(json.dumps([e,rows],sort_keys=True,separators=(',',':')).encode());result['episodes'].append(e)
        for key,value in costs.items():result['timings'][key]=result['timings'].get(key,0)+value
    es=[e for e in result['episodes'] if e['budget']==1024 and e['family']!='arbitrary_hash'];total=sum(e['reachable_unseen_total'] for e in es)
    accuracy=sum(e['scores']['adaptive']['reachable_unseen'] for e in es)/total if total else None
    frozen=sum(e['scores']['frozen_subcube']['reachable_unseen'] for e in es)/total if total else None
    replay=sum(e['scores']['adaptive']['reachable_replay'] for e in es)/sum(e['reachable_pairs'] for e in es)
    observed=sum(e['scores']['adaptive']['observed_recall'] for e in es)==sum(e['unique_observed'] for e in es)
    passed=total>0 and accuracy>=.95 and replay>=.90 and observed
    result.update(bounded_metrics=dict(structured_unseen_accuracy=accuracy,frozen_common_unseen_accuracy=frozen,structured_reachable_replay=replay,structured_observed_recall_exact=observed,
                  unseen_structured_evaluations=total,structured_worlds_without_unseen=sum(e['reachable_unseen_total']==0 for e in es),threshold_pass=passed),
                  classification='DEV_SUPPORTED_NUMERIC_TRAJECTORY_INFERENCE' if passed else 'MIXED_NUMERIC_TRAJECTORY_BOUNDARY',independent_scientific_pass=False,
                  trace_sha256=trace.hexdigest(),total_seconds=time.perf_counter()-started,
                  source=dict(python=sys.version,platform=platform.platform(),prereg_sha256=hashlib.sha256(pre.read_bytes()).hexdigest()))
    try:result['source'].update(sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip())
    except subprocess.CalledProcessError:result['source']['sha']='LOCAL_DEV'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cohort',choices=('DEV','PRIMARY'),default='DEV')
    print('WSP47_RESULT '+json.dumps(run(parser.parse_args().cohort),sort_keys=True))
