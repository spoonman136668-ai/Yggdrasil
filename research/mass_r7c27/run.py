"""R7-C27: source-authentic, FIT-gated surprising-public-obstacle causal use.

All cloned world/RNG data is evaluation-only. Learners see ONLY public
(x,y,direction,goal,front_blocked) and their own source action consequences.
"""
import argparse,copy,hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from research.mass_r7c25 import run as c25
from research.mass_r7c24 import run as c24
from research.mass_r7c23 import run as c23
from research.mass_r7c22 import run as c22
from research.mass_r7c20 import run as c20
from research.native.itd02.r1.native_policy import PublicGrid,canonical
P=json.loads((HERE/'PREREG.json').read_text())

def observe(kind,model,b,a,n,reward,term):
    if kind=='conventional':
        model.observe(b,a,n,float(reward),bool(term))
    else:
        model.observe(b,a,n,float(reward),bool(term),False)

def no_probe_choose(kind,model,public):
    return (c23.NativeSelective.choose(model,public) if kind=='native' else
            c25.ConventionalFull.choose(model,public))

def model_bytes(kind,m):
    return c25.snapshot('native_active' if kind=='native' else 'conventional_active',m)

def cold_choice(kind,model,next_public):
    clone=copy.deepcopy(model)
    expected=no_probe_choose(kind,clone,next_public)
    payload=canonical({'arm':'native_active' if kind=='native' else 'conventional_active',
      'checkpoint':model_bytes(kind,model).decode(),'public':next_public.__dict__,
      'expected':expected,'kind':kind})
    program="""import json,sys
from research.mass_r7c25.run import restored_model, ConventionalFull
from research.mass_r7c23.run import NativeSelective
from research.native.itd02.r1.native_policy import PublicGrid
p=json.loads(sys.stdin.buffer.read())
m=restored_model(p['arm'],p['checkpoint'].encode())
st=PublicGrid(**p['public'])
got=(NativeSelective.choose(m,st) if p['kind']=='native' else ConventionalFull.choose(m,st))
assert got==p['expected'],('COLD_LEARNED_NEXT_ACTION_MISMATCH',got,p['expected'])
print('R7C27_COLD_BELIEF_CHOICE=PASS')
"""
    r=subprocess.run([sys.executable,'-B','-c',program],input=payload,
        capture_output=True,timeout=35,cwd=ROOT,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode==0,('COLD_RESTORE_FAIL',r.stderr.decode())
    return len(model_bytes(kind,model))

def public(o,goal):
    return c22.public_dynamic(o,goal)

def row(b,a,n,r,t,tr,ablation):
    return [b.x,b.y,b.direction,b.goal_x,b.goal_y,int(b.front_blocked),a,
            n.x,n.y,n.direction,int(n.front_blocked),float(r),
            int(bool(t)),int(bool(tr)),int(bool(ablation))]

def fork(kind,model,env,ob,goal,first_action,prefix,blind):
    steps=list(prefix)
    initial_probe=None
    postturn_choice=None
    revealed=None
    afterturn_original=None
    blind_count=0
    visited_revealed=0
    exposed_edge=None
    done=False;truncated=False
    for idx in range(len(steps),P['max_source_episode_actions']):
        before=public(ob,goal)
        if initial_probe is None:
            action=first_action
        elif blind and postturn_choice is None:
            # The physical information-facing turn and its actual source
            # outcome are the same. Suppress only ONE newly revealed public
            # front-reading before the next real source action.
            exposed_edge=(before.x,before.y,before.direction)
            sanitized=PublicGrid(before.x,before.y,before.goal_x,
                      before.goal_y,before.direction,False)
            action=no_probe_choose(kind,model,sanitized)
            if kind=='native':
                model.evidence.pop(exposed_edge,None)
                model.blocked.discard(exposed_edge)
                model.open_edges.discard(exposed_edge)
            else:
                model.posterior.pop(exposed_edge,None)
                model.blocked.discard(exposed_edge)
                model.open.discard(exposed_edge)
            postturn_choice=action
            blind_count+=1
        else:
            action=no_probe_choose(kind,model,before)
            if postturn_choice is None:postturn_choice=action
        assert type(action) is int and action in (0,1,2)
        nobs,reward,done,truncated,_=env.step(action)
        after=public(nobs,goal)
        observe(kind,model,before,action,after,reward,done)
        steps.append(row(before,action,after,reward,done,truncated,blind and blind_count==1 and postturn_choice==action and len(steps)==len(prefix)+1))
        if initial_probe is None:
            initial_probe=steps[-1]
            afterturn_original=after.__dict__.copy()
            revealed=int(after.front_blocked)
            exposed_edge=(after.x,after.y,after.direction)
        elif (before.x,before.y,before.direction)==exposed_edge:
            visited_revealed+=1
        ob=nobs
        if done or truncated:break
    if postturn_choice is None:
        postturn_choice=-1
    final_public=public(ob,goal)
    checkpoint_bytes=cold_choice(kind,model,final_public)
    blob=model_bytes(kind,model)
    reward_sum=round(sum(x[11] for x in steps),9)
    return {'success':bool(done and steps and steps[-1][11]>0),
       'collision_terminal':bool(done and steps and steps[-1][11]<0),
       'source_horizon':bool(truncated),'actions':len(steps),
       'reward':reward_sum,'one_turn_cost':1,
       'first_action':first_action,'first_source_row':initial_probe,
       'first_revealed_observation':afterturn_original,
       'new_obstacle_blocked':revealed,
       'postturn_next_choice':postturn_choice,
       'newly_revealed_edge_revisited':visited_revealed,
       'blinded_readings':blind_count,
       'checkpoint_bytes':checkpoint_bytes,
       'checkpoint_sha256':hashlib.sha256(blob).hexdigest(),
       'trace_sha256':hashlib.sha256(canonical(steps)).hexdigest(),
       'trace':steps}

def fitted_original_screen(fit):
    # Before any fresh DEV reset, qualify that original FIT-only real source
    # shows both kinds of next-front reading after a true information turn.
    model=c25.make('native_active',fit)
    kinds=P['fit']['original_dynamic_probe_seeds']
    summary={}
    for fam in ('MiniGrid-FourRooms-v0','MiniGrid-Dynamic-Obstacles-8x8-v0'):
        seeds=(P['fit']['original_static_probe_seeds'] if fam=='MiniGrid-FourRooms-v0'
               else P['fit']['original_dynamic_probe_seeds'])
        count,_=c25.run_family('native_active',model,fam,seeds)
        # Run again? Avoid: c25.run_family records traces in its second return;
        # this screen uses exactly these already qualified original source runs.
        summary[fam]={'actions':count['steps'],'info_turns':count['information_turns']}
    return summary

def fit_block_check(fit):
    m=c25.make('native_active',fit)
    screen={}
    for family in ('MiniGrid-FourRooms-v0','MiniGrid-Dynamic-Obstacles-8x8-v0'):
        seeds=P['fit']['original_static_probe_seeds'] if family=='MiniGrid-FourRooms-v0' else P['fit']['original_dynamic_probe_seeds']
        totals,episodes=c25.run_family('native_active',m,family,seeds)
        nprobe=sum(1 for ep in episodes for step in ep['trace'] if step[7])
        blocked=sum(1 for ep in episodes for step in ep['trace'] if step[7] and step[11]==1)
        clear=nprobe-blocked
        assert nprobe==totals['information_turns']
        screen[family]={'episodes':len(episodes),'information_turns':nprobe,
            'revealed_blocked':blocked,'revealed_clear':clear}
    return screen

def source_episodes(kind,model,family,seeds):
    episodes=[]
    for seed in seeds:
        env=c20.env_make(family)
        try:
            ob,_=env.reset(seed=seed)
            goal=c20.goal_from(ob)
            dims=tuple(int(z) for z in ob['image'].shape[:2])
            model.reset_episode(*dims)
            prefix=[]
            forks=[]
            for step in range(P['max_source_episode_actions']):
                b=public(ob,goal)
                action=model.choose(b)
                is_probe=bool(model.last_information_probe)
                if is_probe and len(forks)<12:
                    assert action in (0,1)
                    live_snap=hashlib.sha256(model_bytes(kind,model)).hexdigest()
                    configs=[('information',action,False),('information_blind',action,True),('known_side_sham',1-action,False)]
                    branch_result={}
                    for name,a,blind in configs:
                        source_copy=copy.deepcopy(env)
                        policy_copy=copy.deepcopy(model)
                        branch_result[name]=fork(kind,policy_copy,source_copy,ob,goal,a,prefix,blind)
                        source_copy.close()
                    info=branch_result['information']
                    blind=branch_result['information_blind']
                    assert info['first_source_row']==blind['first_source_row']
                    assert info['first_revealed_observation']==blind['first_revealed_observation']
                    assert info['new_obstacle_blocked']==blind['new_obstacle_blocked']
                    if info['actions']>step+1:
                        assert blind['blinded_readings']==1
                    assert all(r['one_turn_cost']==1 for r in branch_result.values())
                    forks.append({'fork_step':step,'public_before':b.__dict__,
                       'preaction_model_sha256':live_snap,
                       'prefix_sha256':hashlib.sha256(canonical(prefix)).hexdigest(),
                       'branches':branch_result})
                nobs,reward,term,trunc,_=env.step(action)
                n=public(nobs,goal)
                observe(kind,model,b,action,n,reward,term)
                prefix.append(row(b,action,n,reward,term,trunc,False))
                ob=nobs
                if term or trunc:break
            episodes.append({'family':family,'seed':seed,'parent_actions':len(prefix),
                'parent_success':bool(prefix and prefix[-1][11]>0),
                'parent_trace_sha256':hashlib.sha256(canonical(prefix)).hexdigest(),
                'forks':forks})
        finally:env.close()
    return episodes

def main():
    import gymnasium,minigrid
    ap=argparse.ArgumentParser()
    ap.add_argument('--kind',choices=('native','conventional'),required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    c20.check_source()
    t0=time.process_time()
    fit,sha,counts=c20.fit_data()
    assert len(fit)==12 and sha==P['fit']['public_actions_sha256']
    model=c25.make('native_active' if args.kind=='native' else 'conventional_active',fit)
    source_screen=fit_block_check(fit)
    print('R7C27_FIT_ONLY_SOURCE_BLOCKED_INFORMATION',json.dumps(source_screen,sort_keys=True),flush=True)
    gate=sum(z['revealed_blocked'] for z in source_screen.values())>0
    if not gate and args.kind=='native':
        status={'schema':'mass.r7c27.fit-only-original-source-gate-fail.v1',
          'source_original_pin':P['source']['upstream'],'kind':args.kind,
          'fit_info_screen':source_screen,'no_new_dev_source_episodes_consumed':True}
        Path(args.out).write_bytes(canonical(status)+b'\n')
        raise SystemExit('R7C27_FIT_UNEXPECTED_OBSTRUCTION_SOURCE_GATE_FAILED_NO_DEV')
    fit_cpu=time.process_time()-t0
    results=[]
    for family,seeds in P['new_public_dev'].items():
        results+=source_episodes(args.kind,model,family,seeds)
    summaries={}
    for family,seeds in P['new_public_dev'].items():
        sub=[e for e in results if e['family']==family]
        forks=[f for e in sub for f in e['forks']]
        blocked=[f for f in forks if f['branches']['information']['new_obstacle_blocked']==1]
        clear=[f for f in forks if f['branches']['information']['new_obstacle_blocked']==0]
        total={'episodes':len(sub),'parent_goals':sum(x['parent_success'] for x in sub),
            'forks':len(forks),'revealed_blocked_forks':len(blocked),
            'revealed_clear_forks':len(clear)}
        for name,cohort in [('blocked',blocked),('clear',clear),('all',forks)]:
            info=[e['branches']['information'] for e in cohort]
            blind=[e['branches']['information_blind'] for e in cohort]
            sham=[e['branches']['known_side_sham'] for e in cohort]
            total[name]={'forks':len(cohort),
                'info_goals':sum(e['success'] for e in info),
                'blind_goals':sum(e['success'] for e in blind),
                'sham_goals':sum(e['success'] for e in sham),
                'info_steps':sum(e['actions'] for e in info),
                'blind_steps':sum(e['actions'] for e in blind),
                'sham_steps':sum(e['actions'] for e in sham),
                'info_minus_blind_reward':round(sum(a['reward']-b['reward'] for a,b in zip(info,blind)),8),
                'info_vs_blind_postturn_choice_diff':sum(a['postturn_next_choice']!=b['postturn_next_choice'] for a,b in zip(info,blind)),
                'info_vs_blind_full_path_diff':sum(
                    [[*r[:14]] for r in a['trace']] != [[*r[:14]] for r in b['trace']]
                    for a,b in zip(info,blind))}
        summaries[family]=total
    out={'schema':P['schema'],'kind':args.kind,
        'source':P['source']['upstream'],'native_owner_head':P['source']['native_owner_head'],
        'protocol_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'fit_sha256':sha,'fit_rows':len(fit),'fit_counts':counts,
        'FIT_original_qualification':source_screen,'summary':summaries,'episodes':results,
        'fit_cpu_s':round(fit_cpu,6),'dev_cpu_s':round(time.process_time()-t0-fit_cpu,6),
        'whole_process_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    Path(args.out).write_bytes(canonical(out)+b'\n')
    print('R7C27_SOURCE_ORIGINAL_CAUSAL_USE',args.kind,json.dumps(summaries,sort_keys=True),flush=True)
if __name__=='__main__':main()
