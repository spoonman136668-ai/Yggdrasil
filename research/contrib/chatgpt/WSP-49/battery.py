"""Broad frozen-learner representation boundary; no result-driven adaptation."""
import argparse,hashlib,itertools,json,platform,subprocess,sys,time
from collections import deque
from pathlib import Path
from domains import LatentWorld,Encoding,EncodedSource,rng_for
from observer import Observer
from equations import EquationBank

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
    pre=Path(__file__).with_name('prereg.json');p=json.loads(pre.read_text());start=time.perf_counter();trace=hashlib.sha256();result=dict(schema='wsp49.result.v1',cohort=cohort,episodes=[],timings={},latent_equivalence_checks=0)
    for width,family,seed in itertools.product(p['widths'],p['families'],p['split'][cohort]):
        tag=f'WSP49|{cohort}|{seed}|{width}|{family}';world=LatentWorld(width,family,tag);states=admissible(world);rpairs=[(a,x) for a in range(2) for x in states];allpairs=[(a,x) for a in range(2) for x in range(1<<width)]
        encs={k:Encoding(width,k,tag) for k in p['encodings']};agents={k:Observer(width) for k in encs};sources={k:EncodedSource(world,e) for k,e in encs.items()};previous=0
        for budget in p['budgets']:
            t=time.perf_counter()
            for _ in range(previous,budget):
                rows=[]
                for k,agent in agents.items():
                    a,x,y=agent.transition(sources[k].apply);e=encs[k];rows.append((a,e.decode(x),e.decode(y)))
                assert rows==[rows[0]]*len(rows),'LATENT_ACTION_INFORMATION_MISMATCH';assert rows[0][1] in states,'SOURCE_RESET_ADMISSIBILITY';result['latent_equivalence_checks']+=1
            result['timings']['all_encodings_source_and_fit_s']=result['timings'].get('all_encodings_source_and_fit_s',0)+time.perf_counter()-t;previous=budget
            seen={(a,x) for a,x,y in agents['identity'].rows};unseen=[pair for pair in rpairs if pair not in seen];rng=rng_for(tag+'|'+str(budget));probes=[rng.choice(unseen) for _ in range(64)] if unseen else []
            seq=[(rng.choice(states),tuple(rng.randrange(2) for _ in range((2,3,4)[i%3]))) for i in range(24)];goals=[]
            for _ in range(4):
                x=rng.choice(states);aa=tuple(rng.randrange(2) for _ in range(3));goals.append((x,world.rollout(x,aa)))
            t=time.perf_counter()
            for k,agent in agents.items():
                enc=encs[k];source=sources[k];facts={(a,x):y for a,x,y in agent.rows};assert len(agent.rows)==budget;assert sum(map(sum,agent.visits))==budget;assert agent.resets==(budget-1)//64
                for model in agent.models:
                    for b in model.banks:
                        snap=b.snapshot();restored=EquationBank.restore(snap);assert restored.snapshot()==snap
                        for x in range(agent.size):assert restored.predict(x)==b.predict(x)
                        try:EquationBank.restore(snap+b'x')
                        except ValueError:pass
                        else:raise AssertionError('tamper accepted')
                arms={str(d):m for d,m in zip((1,2,3,'full'),agent.models)};arms['adaptive']=agent;scores={}
                for name,model in arms.items():
                    pred=[model.apply(a,enc.encode(x)) for a,x in allpairs];plans=[model.plan(enc.encode(x),enc.encode(g)) for x,g in goals]
                    score=dict(unseen=sum(model.apply(a,enc.encode(x))==enc.encode(world.apply(a,x)) for a,x in probes),admissible_replay=sum(model.apply(a,enc.encode(x))==enc.encode(world.apply(a,x)) for a,x in rpairs),
                        observed_recall=sum(model.apply(a,x)==y for (a,x),y in facts.items()),composed=sum(model.rollout(enc.encode(x),aa)==enc.encode(world.rollout(x,aa)) for x,aa in seq),
                        plans=sum(aa is not None and world.rollout(x,aa)==g for aa,(x,g) in zip(plans,goals)),known=sum(y is not None for y in pred),
                        wrong_known=sum(y is not None and y!=enc.encode(world.apply(a,x)) for y,(a,x) in zip(pred,allpairs)),wrong_known_inadmissible=sum(y is not None and y!=enc.encode(world.apply(a,x)) and x not in states for y,(a,x) in zip(pred,allpairs)))
                    assert score['observed_recall']==len(facts),'FACT_RECALL';scores[name]=score
                scores['onehot']=dict(unseen=0,admissible_replay=len(facts),observed_recall=len(facts))
                not_seen=[pair for pair in allpairs if pair not in seen];counter=None
                if not_seen:
                    a,x=not_seen[0];counter=dict(action=a,encoded_state=enc.encode(x),prediction=agent.apply(a,enc.encode(x)),original=enc.encode(world.apply(a,x)),alternate=enc.encode(world.apply(a,x))^1,same_observations=True)
                e=dict(width=width,family=family,seed=seed,encoding=k,budget=budget,source_actions=budget,source_resets=agent.resets,admissible_pairs=len(rpairs),all_pairs=len(allpairs),unique_observed=len(facts),unseen_total=len(probes),unseen_available=len(unseen),scores=scores,cold=True,latent_trajectory_equivalent=True,counterworld=counter,
                    selected_bank_indices=[sum(w*i for i,w in enumerate(agent.selected(a))) for a in range(2)],fixed_bit_register_payload_excluding_counters=sum(b.M*(b.M+width+1)+agent.size*(width+1)+1 for m in agent.models for b in m.banks))
                trace.update(json.dumps([e,agent.rows],sort_keys=True,separators=(',',':')).encode());result['episodes'].append(e)
            result['timings']['cold_and_evaluation_s']=result['timings'].get('cold_and_evaluation_s',0)+time.perf_counter()-t
    positive=[e for e in result['episodes'] if e['budget']==1024 and e['family'] not in ('affine_bits','random_map')];metrics={}
    for k in p['encodings']:
        es=[e for e in positive if e['encoding']==k];n=sum(e['unseen_total'] for e in es)
        metrics[k]=dict(unseen_correct=sum(e['scores']['adaptive']['unseen'] for e in es),unseen_total=n,unseen_accuracy=sum(e['scores']['adaptive']['unseen'] for e in es)/n if n else None,worlds_without_unseen=sum(e['unseen_total']==0 for e in es),admissible_replay=sum(e['scores']['adaptive']['admissible_replay'] for e in es)/sum(e['admissible_pairs'] for e in es))
    evaluable=all(m['unseen_total']>0 for m in metrics.values());passed=evaluable and all(m['unseen_accuracy']>=.90 for m in metrics.values()) and metrics['identity']['unseen_accuracy']-metrics['random_permutation']['unseen_accuracy']<=.05
    result.update(bounded_metrics=metrics,threshold_pass=passed,classification='DEV_SUPPORTED_FROZEN_REPRESENTATION_TRANSFER' if passed else ('MIXED_FROZEN_REPRESENTATION_BOUNDARY' if evaluable else 'UNVERIFIED_NO_UNSEEN_REPRESENTATION_CASES'),independent_scientific_pass=False,trace_sha256=trace.hexdigest(),total_seconds=time.perf_counter()-start,source=dict(python=sys.version,platform=platform.platform(),prereg_sha256=hashlib.sha256(pre.read_bytes()).hexdigest()))
    try:result['source'].update(sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip())
    except subprocess.CalledProcessError:result['source']['sha']='LOCAL_DEV'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cohort',choices=('DEV','PRIMARY'),default='DEV');print('WSP49_RESULT '+json.dumps(run(p.parse_args().cohort),sort_keys=True))
