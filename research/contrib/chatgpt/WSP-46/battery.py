"""WSP46 information-access boundary: real trajectories versus injected states."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from frozen_numeric import NumericLearner,ActionModel
from agent import TrajectoryAgent,MembershipAgent,TrainedOneHot
from world import World,rng_for


def reachable_states(world,width):
    reached={0};frontier=[0]
    while frontier:
        state=frontier.pop()
        for action in range(2):
            nxt=world.apply(action,state)
            if nxt not in reached:reached.add(nxt);frontier.append(nxt)
    return tuple(sorted(reached))


def run(cohort):
    pre=Path(__file__).with_name('prereg.json');p=json.loads(pre.read_text());started=time.perf_counter()
    result=dict(schema='wsp46.result.v1',cohort=cohort,episodes=[],timings={});trace=hashlib.sha256()
    for width,family,seed in itertools.product(p['widths_max_first'],p['families'],p['split'][cohort]):
        tag=f'WSP46|{cohort}|{seed}|{width}|{family}';world=World(width,family,tag);size=1<<width
        reachable=reachable_states(world,width);reachable_set=set(reachable)
        active=TrajectoryAgent(width);random=TrajectoryAgent(width,'random');member=MembershipAgent(width)
        previous=0;costs={}
        for budget in p['budgets']:
            for name,agent in (('numeric',active),('random',random),('membership',member)):
                t=time.perf_counter()
                for _ in range(previous,budget):agent.transition(world.apply)
                costs[name+'_acquisition_s']=costs.get(name+'_acquisition_s',0)+time.perf_counter()-t
            previous=budget
            for agent in (active,random):
                for t,(a,x,y) in enumerate(agent.rows):
                    expected=0 if t%64==0 else agent.rows[t-1][2]
                    assert x==expected and x in reachable_set and y==world.apply(a,x)
            trained=TrainedOneHot(active.rows);assert trained.training_errors==0
            seen={(a,x) for a,x,y in active.rows};rseen={(a,x) for a,x,y in random.rows}
            allpairs=[(a,x) for a in range(2) for x in range(size)]
            rpairs=[(a,x) for a in range(2) for x in reachable]
            runseen=[pair for pair in rpairs if pair not in seen];unseen=[pair for pair in allpairs if pair not in seen]
            rng=rng_for(tag+'|'+str(budget));rprobes=[rng.choice(runseen) for _ in range(64)] if runseen else []
            uprobes=[rng.choice(unseen) for _ in range(64)] if unseen else []
            sequences=[(rng.choice(reachable),tuple(rng.randrange(2) for _ in range((2,3,4)[i%3]))) for i in range(24)]
            goals=[]
            for _ in range(4):
                x=rng.choice(reachable);aa=tuple(rng.randrange(2) for _ in range(3));goals.append((x,world.rollout(x,aa)))
            arms={'numeric':active,'random':random,'membership':member,'trained_onehot':trained,'zero':ActionModel([NumericLearner(width) for _ in range(2)])};scores={}
            t=time.perf_counter()
            for name,model in arms.items():
                plans=[model.plan(x,g) for x,g in goals]
                scores[name]=dict(reachable_unseen=sum(model.apply(a,x)==world.apply(a,x) for a,x in rprobes),
                    all_unseen=sum(model.apply(a,x)==world.apply(a,x) for a,x in uprobes),
                    reachable_replay=sum(model.apply(a,x)==world.apply(a,x) for a,x in rpairs),
                    full_replay=sum(model.apply(a,x)==world.apply(a,x) for a,x in allpairs),
                    observed_recall=sum(model.apply(a,x)==world.apply(a,x) for a,x in sorted(seen)),
                    composed=sum(model.rollout(x,aa)==world.rollout(x,aa) for x,aa in sequences),
                    plans=sum(aa is not None and world.rollout(x,aa)==g for aa,(x,g) in zip(plans,goals)))
            costs['evaluation_s']=costs.get('evaluation_s',0)+time.perf_counter()-t
            t=time.perf_counter()
            for agent in (active,random,member):
                for m in agent.learners:
                    snap=m.snapshot();restored=NumericLearner.restore(snap);assert restored.snapshot()==snap
                    try:NumericLearner.restore(snap+b'x')
                    except ValueError:pass
                    else:raise AssertionError('tamper accepted')
            costs['cold_integrity_s']=costs.get('cold_integrity_s',0)+time.perf_counter()-t
            counterworld=None
            if unseen:
                a,x=unseen[0];original=world.apply(a,x);alternate=original^1;prediction=active.apply(a,x)
                assert original!=alternate
                assert all((alternate if aa==a and xx==x else world.apply(aa,xx))==yy for aa,xx,yy in active.rows)
                counterworld=dict(unobserved_action=a,unobserved_state=x,prediction=prediction,original=original,alternate=alternate,compatible_observations=True,both_correct=False)
            e=dict(width=width,family=family,seed=seed,budget=budget,reachable_states=len(reachable),reachable_pairs=len(rpairs),all_pairs=len(allpairs),
                unique_active=len(seen),unique_random=len(rseen),unique_membership=len({(a,x) for a,x,y in member.rows}),resets_active=active.resets,resets_random=random.resets,
                reachable_unseen_total=len(rprobes),reachable_unseen_available=len(runseen),all_unseen_total=len(uprobes),all_unseen_available=len(unseen),
                evaluation_kind='UNSEEN_REACHABLE' if runseen else 'NO_UNSEEN_REACHABLE_CASES',random_seen_common_unseen=sum(pair in rseen for pair in rprobes),
                scores=scores,counterworld=counterworld,cold=True,trained_converged=True,
                snapshot_bytes=sum(len(m.snapshot()) for m in active.learners),policy_thresholds=active.policy_thresholds)
            trace.update(json.dumps([e,active.rows,random.rows,member.rows],sort_keys=True,separators=(',',':')).encode());result['episodes'].append(e)
        for key,value in costs.items():result['timings'][key]=result['timings'].get(key,0)+value
    es=[e for e in result['episodes'] if e['budget']==1024];unseen_total=sum(e['reachable_unseen_total'] for e in es)
    active_unseen=sum(e['scores']['numeric']['reachable_unseen'] for e in es)/unseen_total if unseen_total else None
    random_unseen=sum(e['scores']['random']['reachable_unseen'] for e in es)/unseen_total if unseen_total else None
    replay=sum(e['scores']['numeric']['reachable_replay'] for e in es)/sum(e['reachable_pairs'] for e in es)
    member_ok=all(e['scores']['membership']['full_replay']==e['all_pairs'] for e in result['episodes'])
    trajectory_ok=unseen_total>0 and active_unseen>=.95 and replay>=.90 and active_unseen-random_unseen>=.05
    result.update(bounded_metrics=dict(membership_full_pass=member_ok,trajectory_bound_pass=trajectory_ok,reachable_unseen_accuracy=active_unseen,random_common_unseen_accuracy=random_unseen,
        reachable_replay_accuracy=replay,unseen_reachable_evaluated=unseen_total,unseen_unavailable_worlds=sum(e['reachable_unseen_total']==0 for e in es)),
        classification='DEV_SUPPORTED_TRAJECTORY_ACQUISITION' if member_ok and trajectory_ok else 'MIXED_MEMBERSHIP_TRAJECTORY_GAP' if member_ok else 'SCIENTIFIC_NEGATIVE_NUMERIC_MEMBERSHIP_BOUND_MISSED',
        independent_scientific_pass=False,trace_sha256=trace.hexdigest(),total_seconds=time.perf_counter()-started,
        source=dict(python=sys.version,platform=platform.platform(),prereg_sha256=hashlib.sha256(pre.read_bytes()).hexdigest(),frozen_numeric_sha256=hashlib.sha256(Path(__file__).with_name('frozen_numeric.py').read_bytes()).hexdigest()))
    try:result['source'].update(sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip())
    except subprocess.CalledProcessError:result['source']['sha']='LOCAL_DEV'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cohort',choices=('DEV','PRIMARY'),default='DEV')
    print('WSP46_RESULT '+json.dumps(run(parser.parse_args().cohort),sort_keys=True))
