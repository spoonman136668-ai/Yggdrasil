"""R7-C26: fork the ORIGINAL MiniGrid environment at the first eligible public probe.

Environment deepcopy is evaluation-only; no cloned state, wall/ball identity or
underlying grid is exposed to a learner. Every branch then obtains true Farama
MiniGrid actions, rewards and public observations.
"""
import argparse,copy,hashlib,json,os,resource,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from research.mass_r7c25 import run as c25
from research.mass_r7c24 import run as c24
from research.mass_r7c23 import run as c23
from research.mass_r7c22 import run as c22
from research.mass_r7c20 import run as c20
from research.native.itd02.r1.native_policy import PublicGrid,canonical
P=json.loads((HERE/'PREREG.json').read_text())

def public(obs,goal):
    return c22.public_dynamic(obs,goal)

def trace_row(before,action,after,reward,done,truncated,is_probe=False,is_blind=False):
    return [before.x,before.y,before.direction,before.goal_x,before.goal_y,
       int(before.front_blocked),action,int(bool(is_probe)),int(bool(is_blind)),
       after.x,after.y,after.direction,int(after.front_blocked),
       float(reward),int(bool(done)),int(bool(truncated))]

def observe(kind,model,before,action,after,reward,done):
    if kind=='conventional':
        model.observe(before,action,after,float(reward),bool(done))
    else:
        model.observe(before,action,after,float(reward),bool(done),False)

def no_probe_choose(kind,model,state):
    # Explicitly call pre-registered non-probing source methods. Neither branch
    # may trigger another active turn after its matched first-turn intervention.
    if kind=='native':
        return c23.NativeSelective.choose(model,state)
    return c25.ConventionalFull.choose(model,state)

def simple_blind(state):
    return PublicGrid(state.x,state.y,state.goal_x,state.goal_y,
                      state.direction,False)

def branch(kind,model,env,obs,goal,first_action,full_prefix,blind):
    rows=list(full_prefix)
    actual_first=None
    revealed=None
    first_next_choice=None
    post_probe_choice_different=None
    first_action_reward=None
    original_reveal_edge=None
    done=False;truncated=False
    total_rewards=sum(r[13] for r in rows)
    source_step_limit=P['max_episode_actions']
    max_mem=0;seq=0;blind_applied=0;revisited_new_edge=0
    for idx in range(len(rows),source_step_limit):
        before=public(obs,goal)
        is_blind=False
        if seq==0:
            act=first_action
        else:
            if blind and seq==1:
                # Information-content ablation. The physical probe action and
                # its original outcome match informative branch; only the new
                # public front observation is deliberately withheld for ONE
                # decision and from its long-term edge memory. True previous
                # and subsequent public consequences remain unmodified.
                assert kind=='native'
                edge=(before.x,before.y,before.direction)
                assert edge==original_reveal_edge
                assert edge not in model.evidence,('NOT_NOVEL_EDGE',edge)
                act=no_probe_choose(kind,model,simple_blind(before))
                model.evidence.pop(edge,None)
                model.blocked.discard(edge)
                model.open_edges.discard(edge)
                is_blind=True;blind_applied+=1
            else:
                act=no_probe_choose(kind,model,before)
            if seq==1:first_next_choice=act
        assert type(act) is int and act in (0,1,2)
        if seq>1 and original_reveal_edge==(before.x,before.y,before.direction):
            revisited_new_edge+=1
        next_obs,reward,done,truncated,_=env.step(act)
        after=public(next_obs,goal)
        observe(kind,model,before,act,after,reward,done)
        row=trace_row(before,act,after,reward,done,truncated,
                      is_probe=(seq==0),is_blind=is_blind)
        rows.append(row);total_rewards+=float(reward)
        if seq==0:
            actual_first=row
            first_action_reward=float(reward)
            revealed=int(after.front_blocked)
            original_reveal_edge=(after.x,after.y,after.direction)
            # Same physical action in info and blind MUST expose the same real
            # MiniGrid obstacle reading before any model-level ablation.
        obs=next_obs;seq+=1
        if done or truncated:break
    end_public=public(obs,goal)
    # The state has to cold-restore in a separate actual Python process
    # and choose exactly the same next public action as an in-process clone.
    c25.cold_compare('native_active' if kind=='native' else 'conventional_active',
                     model,end_public)
    checkpoint=c25.snapshot('native_active' if kind=='native' else 'conventional_active',model)
    max_mem=len(checkpoint)
    return {'success':bool(done and rows[-1][13]>0),'collision':bool(done and rows[-1][13]<0),
        'horizon':bool(truncated),'actions':len(rows),
        'reward':round(total_rewards,9),'first_action':first_action,
        'first_postturn_action':first_next_choice,'first_revealed_public_front_blocked':revealed,
        'first_after_turn_source_row':actual_first,
        'new_edge_revisit_actions':revisited_new_edge,'blind_actions':blind_applied,
        'trace_sha256':hashlib.sha256(canonical(rows)).hexdigest(),
        'trace':rows,'checkpoint_sha256':hashlib.sha256(checkpoint).hexdigest(),
        'checkpoint_bytes':max_mem}

def original_family(kind,model,family,seeds):
    results=[]
    for seed in seeds:
        env=c20.env_make(family)
        try:
            obs,_=env.reset(seed=seed)
            goal=c20.goal_from(obs)
            dimensions=tuple(map(int,obs['image'].shape[:2]))
            model.reset_episode(*dimensions)
            prefix=[]
            first_trigger=False
            for step in range(P['max_episode_actions']):
                current=public(obs,goal)
                # This choice updates only public learner belief.
                a=model.choose(current)
                is_probe=bool(model.last_information_probe)
                if is_probe:
                    assert a in (0,1),'PROBE_NOT_TURN'
                    assert step+1<=P['max_episode_actions']
                    # Freeze source source-evaluator + fully FIT-trained learner
                    # at the exact shared BEFORE-action state.
                    pre_digest=hashlib.sha256(c25.snapshot('native_active' if kind=='native'
                                                          else 'conventional_active',model)).hexdigest()
                    branches={}
                    source_clone=[copy.deepcopy(env) for _ in range(3 if kind=='native' else 2)]
                    model_clone=[copy.deepcopy(model) for _ in source_clone]
                    setups=[('information',a,False),('sham',1-a,False)]
                    if kind=='native':setups.append(('information_blind',a,True))
                    for (name,action,blind),src,m in zip(setups,source_clone,model_clone):
                        branches[name]=branch(kind,m,src,obs,goal,action,prefix,blind)
                        src.close()
                    assert branches['information']['first_after_turn_source_row']==(
                           branches['information_blind']['first_after_turn_source_row']) if kind=='native' else True
                    if kind=='native':
                        assert branches['information_blind']['blind_actions']==1 or (
                            branches['information_blind']['actions']==step+1)
                        assert branches['information']['first_revealed_public_front_blocked']==(
                            branches['information_blind']['first_revealed_public_front_blocked'])
                    assert branches['information']['first_action'] in (0,1)
                    assert branches['sham']['first_action']==1-branches['information']['first_action']
                    result={'family':family,'seed':seed,'fork_step':step,
                       'preaction_public':current.__dict__,
                       'preaction_model_sha256':pre_digest,
                       'preaction_prefix_sha256':hashlib.sha256(canonical(prefix)).hexdigest(),
                       'fork_branches':branches}
                    results.append(result)
                    first_trigger=True
                    break
                # Before first probe all policies follow authentic own historical
                # actions and observed consequences. No other intervention.
                next_obs,reward,done,truncated,_=env.step(a)
                after=public(next_obs,goal)
                observe(kind,model,current,a,after,reward,done)
                prefix.append(trace_row(current,a,after,reward,done,truncated))
                obs=next_obs
                if done or truncated:break
            if not first_trigger:
                results.append({'family':family,'seed':seed,'fork_step':None,
                    'nonforked_prefix_trace_sha256':hashlib.sha256(canonical(prefix)).hexdigest(),
                    'nonforked_actions':len(prefix),'nonforked_success':bool(prefix and prefix[-1][13]>0)})
        finally:env.close()
    return results

def main():
    import gymnasium,minigrid
    ap=argparse.ArgumentParser()
    ap.add_argument('--kind',choices=('native','conventional'),required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    c20.check_source()
    assert P['source']['upstream'].split('@')[-1]=='7f5853792ea7f04f75614661006d87fcf949f26d'
    t0=time.process_time()
    fit,fit_sha,fitcounts=c20.fit_data()
    assert fit_sha==P['fit']['expected_sha256'] and len(fit)==12
    model=c25.make('native_active' if args.kind=='native' else 'conventional_active',fit)
    t1=time.process_time()
    results=[]
    for family,seeds in P['fresh_public_dev'].items():
        results+=original_family(args.kind,model,family,seeds)
    t2=time.process_time()
    summary={}
    for f,seeds in P['fresh_public_dev'].items():
        target=[x for x in results if x['family']==f]
        forks=[x for x in target if x['fork_step'] is not None]
        stats={'episodes':len(target),'forked':len(forks),'not_forked':len(target)-len(forks)}
        for arm in ('information','sham','information_blind'):
            eligible=[x['fork_branches'][arm] for x in forks if arm in x['fork_branches']]
            if eligible:
                stats[arm]={'forks':len(eligible),
                    'goals':sum(x['success'] for x in eligible),
                    'collisions':sum(x['collision'] for x in eligible),
                    'actions':sum(x['actions'] for x in eligible),
                    'sum_reward':round(sum(x['reward'] for x in eligible),9),
                    'cold_full_checkpoints':len(eligible)}
        if args.kind=='native' and forks:
            stats['information_vs_blind_next_choice_divergences']=sum(
               x['fork_branches']['information']['first_postturn_action']!=
               x['fork_branches']['information_blind']['first_postturn_action'] for x in forks)
            stats['total_information_postturn_known_blocked']=sum(
               x['fork_branches']['information']['first_revealed_public_front_blocked'] for x in forks)
        summary[f]=stats
    out={'schema':P['schema'],'kind':args.kind,'protocol_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
         'source':P['source']['upstream'],'owner_R3_head':P['source']['owner_r3_head'],
         'fit_sha256':fit_sha,'fit_counts':fitcounts,'fit_examples':len(fit),
         'summary':summary,'traces':results,
         'cpu_fit_s':round(t1-t0,6),'cpu_dev_s':round(t2-t1,6),
         'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    Path(args.out).write_bytes(canonical(out)+b'\n')
    print('R7C26_ORIGINAL_SOURCE_FORK',args.kind,json.dumps(summary,sort_keys=True),flush=True)
if __name__=='__main__':main()
