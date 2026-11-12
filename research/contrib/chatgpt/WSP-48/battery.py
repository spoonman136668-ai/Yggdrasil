"""Frozen equal-capacity action-selection comparison; evaluator graph is private."""
import argparse,hashlib,itertools,json,platform,subprocess,sys,time
from collections import deque
from pathlib import Path
from agent import Agent
from equations import EquationBank
from world import World,rng_for

def admissible(world):
    distances={0:0};q=deque([0])
    while q:
        x=q.popleft()
        if distances[x]==63:continue
        for a in range(2):
            y=world.apply(a,x)
            if y not in distances:distances[y]=distances[x]+1;q.append(y)
    return tuple(sorted(distances))

def run(cohort):
    pre=Path(__file__).with_name('prereg.json');p=json.loads(pre.read_text());start=time.perf_counter();trace=hashlib.sha256()
    result=dict(schema='wsp48.result.v1',cohort=cohort,episodes=[],timings={},shadow_checks=0)
    for width,family,seed in itertools.product(p['widths_max_first'],p['families'],p['split'][cohort]):
        tag=f'WSP48|{cohort}|{seed}|{width}|{family}';world=World(width,family,tag);states=admissible(world);rpairs=[(a,x) for a in range(2) for x in states];allpairs=[(a,x) for a in range(2) for x in range(1<<width)]
        arms={name:Agent(width,name) for name in ('frontier','least_visit')};first_full={k:None for k in arms};elapsed={k:0.0 for k in arms};previous=0
        for budget in p['budgets']:
            for name,agent in arms.items():
                t=time.perf_counter()
                for _ in range(previous,budget):
                    a,x,y=agent.transition(world.apply);assert x in states,'SOURCE_RESET_ADMISSIBILITY'
                    if name=='frontier':result['shadow_checks']+=1
                    observed=sum(b.seen.bit_count() for b in agent.models[-1].banks)
                    if observed==len(rpairs) and first_full[name] is None:first_full[name]=agent.steps
                elapsed[name]+=time.perf_counter()-t
            previous=budget
            seen={k:{(a,x) for a,x,y in m.rows} for k,m in arms.items()};unseen=[pair for pair in rpairs if pair not in seen['frontier']|seen['least_visit']];rng=rng_for(tag+'|'+str(budget));probes=[rng.choice(unseen) for _ in range(64)] if unseen else []
            sequences=[(rng.choice(states),tuple(rng.randrange(2) for _ in range((2,3,4)[i%3]))) for i in range(24)];goals=[]
            for _ in range(4):
                x=rng.choice(states);aa=tuple(rng.randrange(2) for _ in range(3));goals.append((x,world.rollout(x,aa)))
            scores={};t=time.perf_counter()
            for name,agent in arms.items():
                facts={(a,x):y for a,x,y in agent.rows};assert len(agent.rows)==budget;assert sum(map(sum,agent.visits))==budget;assert agent.resets==(budget-1)//64
                expected=[0]*agent.size
                for (a,x),y in facts.items():expected[y]|=1<<x
                assert expected==agent.predecessors,'GRAPH_FROM_FACTS_ONLY'
                for model in agent.models:
                    for b in model.banks:
                        snap=b.snapshot();restored=EquationBank.restore(snap);assert restored.snapshot()==snap
                        for x in range(agent.size):assert restored.predict(x)==b.predict(x)
                        try:EquationBank.restore(snap+b'x')
                        except ValueError:pass
                        else:raise AssertionError('tamper accepted')
                pred=[agent.apply(a,x) for a,x in allpairs];plans=[agent.plan(x,g) for x,g in goals]
                matching={'linear':0,'quadratic':1,'cubic_ood':2,'arbitrary_hash':3}[family]
                assert all(agent.models[matching].apply(a,x) in (None,world.apply(a,x)) for a,x in allpairs)
                score=dict(unique_observed=len(facts),coverage=len(facts)/len(rpairs),first_full_coverage_step=first_full[name],admissible_replay=sum(agent.apply(a,x)==world.apply(a,x) for a,x in rpairs),
                    observed_recall=sum(agent.apply(a,x)==y for (a,x),y in facts.items()),common_unseen=sum(agent.apply(a,x)==world.apply(a,x) for a,x in probes),
                    onehot_observed_recall=sum(facts.get((a,x))==y for (a,x),y in facts.items()),onehot_admissible_replay=len(facts),onehot_common_unseen=0,
                    composed=sum(agent.rollout(x,aa)==world.rollout(x,aa) for x,aa in sequences),plans=sum(aa is not None and world.rollout(x,aa)==g for aa,(x,g) in zip(plans,goals)),
                    known=sum(y is not None for y in pred),wrong_known=sum(y is not None and y!=world.apply(a,x) for y,(a,x) in zip(pred,allpairs)),
                    wrong_known_inadmissible=sum(y is not None and y!=world.apply(a,x) and x not in states for y,(a,x) in zip(pred,allpairs)),wave_rounds=agent.wave_rounds,
                    fixed_bit_register_payload_excluding_counters=sum(b.M*(b.M+width+1)+agent.size*(width+1)+1 for m in agent.models for b in m.banks)+agent.size**2,
                    cold=True,source_consistency=True)
                assert score['observed_recall']==len(facts),'FACT_RECALL'
                not_seen=[pair for pair in allpairs if pair not in facts]
                if not_seen:
                    a,x=not_seen[0];score['counterworld']=dict(action=a,state=x,original=world.apply(a,x),alternate=world.apply(a,x)^1,prediction=agent.apply(a,x),same_observations=True)
                else:score['counterworld']=None
                scores[name]=score
            result['timings']['evaluation_s']=result['timings'].get('evaluation_s',0)+time.perf_counter()-t
            e=dict(width=width,family=family,seed=seed,budget=budget,admissible_pairs=len(rpairs),all_pairs=len(allpairs),common_unseen_total=len(probes),common_unseen_available=len(unseen),scores=scores)
            trace.update(json.dumps([e,{k:m.rows for k,m in arms.items()}],sort_keys=True,separators=(',',':')).encode());result['episodes'].append(e)
        for k,v in elapsed.items():result['timings'][k+'_including_shadow_s' if k=='frontier' else k+'_s']=result['timings'].get(k+'_including_shadow_s' if k=='frontier' else k+'_s',0)+v
    target=[e for e in result['episodes'] if e['width']==8 and e['budget']==512];final=[e for e in result['episodes'] if e['budget']==1024]
    coverage={k:sum(e['scores'][k]['coverage'] for e in target)/len(target) for k in arms};replay=sum(e['scores']['frontier']['admissible_replay']/e['admissible_pairs'] for e in final)/len(final)
    passed=coverage['frontier']>=.75 and coverage['frontier']-coverage['least_visit']>=.10 and replay>=.90
    result.update(bounded_metrics=dict(width8_512_mean_coverage=coverage,coverage_gain_pp=100*(coverage['frontier']-coverage['least_visit']),final_mean_admissible_replay=replay,threshold_pass=passed),classification='DEV_SUPPORTED_NUMERIC_FRONTIER_EXPLORATION' if passed else 'MIXED_NUMERIC_FRONTIER_BOUNDARY',independent_scientific_pass=False,
        trace_sha256=trace.hexdigest(),total_seconds=time.perf_counter()-start,source=dict(python=sys.version,platform=platform.platform(),prereg_sha256=hashlib.sha256(pre.read_bytes()).hexdigest()))
    try:result['source'].update(sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip())
    except subprocess.CalledProcessError:result['source']['sha']='LOCAL_DEV'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cohort',choices=('DEV','PRIMARY'),default='DEV');print('WSP48_RESULT '+json.dumps(run(p.parse_args().cohort),sort_keys=True))
