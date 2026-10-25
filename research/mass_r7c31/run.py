"""R7-C31 — unchanged native R12 chooses real DoorKey actions from real R11 FIT.

All actual intervention effects are returned by pinned original Farama MiniGrid.
The explicitly supplied effect objective is *not* autonomously learned.
"""
import copy,hashlib,json,math,os,random,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
P=json.loads((HERE/'PREREG.json').read_text())
owner_root=Path(os.environ['OWNER_R11_ROOT']).resolve()
assert owner_root.is_dir()
# Original owner R12 exact immutable checkout includes pinned R10 and R11.
sys.path.insert(0,str(owner_root))
from research.native.itd02.r10 import public_adapter as owner
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
from research.native.itd02.r12.outcome_choice import select_public_action
from research.mass_r7c30 import run as c30
from research.mass_r7c29 import collect as collector
control=c30.control

def independent_choice(model,public,objective):
    bit={'carrying_changed':2,'visible_door_state_changed':1,'positive_reward':4}[objective]
    poss=[]
    for a in range(7):
        key=control.context(public,a)
        row=model.counts.get(key)
        if not row:continue
        n=sum(row.values())
        wins=sum(v for k,v in row.items() if int(k)&(1<<bit))
        probability=wins/n
        if probability>0:poss.append((-probability,a,n))
    if not poss:return {'status':'ABSTAIN_NO_LEARNED_POSITIVE_ACTION','action':None,
                         'samples':0,'probability':0.}
    highest=sorted(poss)[0]
    return {'status':'SELECT_LEARNED_PUBLIC_ACTION','action':highest[1],
            'samples':highest[2],'probability':-highest[0]}

def explicit_objective(cues):
    front,carried=cues['front'],cues['carried']
    if front[0]==5 and carried is None:return 'carrying_changed'
    if front[0]==4 and carried is not None and front[2] in (1,2):
        return 'visible_door_state_changed'
    return None

def physical_source_fork(wrapped_env, raw,public,action,objective):
    if action is None:
        return {'executed':False,'public_action':None,
             'learned_objective_realized':False,'source_reward':None}
    assert type(action)is int and 0<=action<7
    simulator=copy.deepcopy(wrapped_env)
    adapter=owner.DoorKeyPublicAdapter()
    adapter.reset_public(collector.normalized_original_public(raw))
    assert adapter.submit(action)==action
    nxt,reward,done,trunc,_=simulator.step(action)
    event=adapter.complete(collector.normalized_original_public(nxt),
                           float(reward),bool(done),bool(trunc))
    simulator.close()
    success=(event['visible_key_pickup'] if objective=='carrying_changed'
             else event['visible_door_opened'])
    return {'executed':True,'public_action':action,'learned_objective_realized':bool(success),
            'source_reward':float(reward),'source_terminated':bool(done),
            'source_truncated':bool(trunc),
            'source_before_sha256':event['before_public_sha256'],
            'source_after_sha256':event['after_public_sha256'],
            'actual_source_event_sha256':hashlib.sha256(owner.canonical(event)).hexdigest()}

def os_restore_action(nblob,cblob,public,objective,expected_native,expected_conventional):
    program="""import json,os,sys,importlib.util
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
from research.native.itd02.r12.outcome_choice import select_public_action
payload=json.loads(sys.stdin.buffer.read())
native=PublicAffordanceCells.restore(payload['native'].encode())
out=select_public_action(native,payload['public'],payload['objective'])
assert out['action']==payload['expected_native']
spec=importlib.util.spec_from_file_location('independent',payload['independent_file'])
control=importlib.util.module_from_spec(spec);spec.loader.exec_module(control)
conv=control.Control.restore(payload['conventional'].encode())
bit={'carrying_changed':2,'visible_door_state_changed':1,'positive_reward':4}[payload['objective']]
choices=[]
for a in range(7):
 row=conv.counts.get(control.context(payload['public'],a))
 if not row:continue
 n=sum(row.values());w=sum(v for k,v in row.items() if int(k)&(1<<bit))
 if w>0:choices.append((-w/n,a))
result=min(choices)[1] if choices else None
assert result==payload['expected_conventional']
print('R7C31_NATIVE_R12_AND_INDEPENDENT_CONVENTIONAL_COLD_CHOICES=PASS')
"""
    payload={'native':nblob.decode(),'conventional':cblob.decode(),
      'public':public,'objective':objective,
      'expected_native':expected_native,'expected_conventional':expected_conventional,
      'independent_file':str(ROOT/'research/mass_r7c30/control.py')}
    run=subprocess.run([sys.executable,'-B','-c',program],
      input=owner.canonical(payload),cwd=owner_root,
      capture_output=True,timeout=30,
      env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    assert run.returncode==0,('R7C31_OS_COLD_FAIL',run.stderr.decode())
    assert 'R7C31_NATIVE_R12_AND_INDEPENDENT_CONVENTIONAL_COLD_CHOICES=PASS' in run.stdout.decode()

def main():
    import gymnasium as gym,minigrid
    assert owner.UPSTREAM_MINIGRID_COMMIT==P['original_upstream'].split('@')[-1]
    t0=time.process_time()
    native=PublicAffordanceCells()
    conv=control.Control()
    trained,extra,last=c30.run_source_fit(
      native,conv,'training',P['original_FIT_training_seeds'],list(range(8)))
    assert not extra and trained['actual_selected_actions']==P['expected_original_FIT_training_events']
    assert trained['real_pickups']==trained['real_opened_doors']==8
    assert native.samples==conv.samples==1664
    native_blob=native.checkpoint()
    conv_blob=conv.checkpoint()
    assert len(native.counts)>0 and len(conv.counts)>0
    c30.cold_verify(native_blob,conv_blob,last)
    t1=time.process_time()
    episodes=[];all_forks=[];counts={'key':0,'door':0}
    for i,seed in enumerate(P['fresh_original_public_FIT_test_seeds']):
        rng=random.Random(93617+7919*i)
        env=gym.make('MiniGrid-DoorKey-8x8-v0')
        adapter=owner.DoorKeyPublicAdapter()
        try:
            raw,_=env.reset(seed=seed)
            adapter.reset_public(collector.normalized_original_public(raw))
            events=[];forks=[]
            for step in range(P['max_original_steps_per_test_seed']):
                public=owner.public_observation(collector.normalized_original_public(raw))
                cues=owner.public_cues(public)
                independent=collector.independent_cues(collector.normalized_original_public(raw))
                assert independent['front']==cues['front'] and independent['carried']==cues['carried']
                action=collector.policy({'image':public['image'],'cues':cues},rng,step,{})
                objective=explicit_objective(cues)
                if objective:
                    n=select_public_action(native,public,objective,min_samples=1)
                    c=independent_choice(conv,public,objective)
                    nf=physical_source_fork(env,raw,public,n['action'],objective)
                    cf=physical_source_fork(env,raw,public,c['action'],objective)
                    bf=physical_source_fork(env,raw,public,action,objective)
                    # Event included unselected or abstained predictions, never impute
                    # their source action or corresponding success.
                    pair={'fit_seed':seed,'step':step,'objective':objective,
                       'actual_public_context_sha256':owner.public_cues(public)['observation_sha256'],
                       'native_selection':{'status':n['status'],'action':n['action'],
                        'expected_benefit':n['expected_benefit'],'samples':n['training_samples']},
                       'conventional_selection':c,
                       'source_native_fork':nf,'source_conventional_fork':cf,
                       'source_collector_fork':bf}
                    os_restore_action(native_blob,conv_blob,public,objective,n['action'],c['action'])
                    forks.append(pair);all_forks.append(pair)
                    counts['key' if objective=='carrying_changed' else 'door']+=1
                assert adapter.submit(action)==action
                nxt,reward,done,trunc,_=env.step(action)
                outcome=adapter.complete(collector.normalized_original_public(nxt),
                   float(reward),bool(done),bool(trunc))
                events.append([step,action,outcome['before_public_sha256'],outcome['after_public_sha256'],
                  float(reward),bool(done),bool(trunc),int(outcome['visible_key_pickup']),
                  int(outcome['visible_door_opened'])])
                raw=nxt
                if done or trunc:break
            episodes.append({'seed':seed,'source_actions':len(events),
                'source_goals':sum(x[4]>0 for x in events),
                'source_public_events_sha256':hashlib.sha256(owner.canonical(events)).hexdigest(),
                'source_observation_forks':forks})
        finally:env.close()
    assert counts['key']>0 and counts['door']>0,('NO_REAL_PICKUP_DOOR_TEST_EXPOSURE',counts)
    assert native.checkpoint()==native_blob and conv.checkpoint()==conv_blob, 'TEST_LEARNING_LEAK'
    def stats(name):
        selected=[f for f in all_forks if f['source_'+name+'_fork']['executed']]
        return {'selected':len(selected),
          'abstained':len(all_forks)-len(selected),
          'real_source_objective_success':sum(f['source_'+name+'_fork']['learned_objective_realized'] for f in selected),
          'original_public_action_counts':{str(a):sum(f['source_'+name+'_fork']['public_action']==a for f in selected) for a in range(7)}}
    native_stats=stats('native');conv_stats=stats('conventional');collector_stats=stats('collector')
    output={'schema':P['schema'],'source_original':P['original_upstream'],
      'owner_R12_source_head':P['owner_R12_source_commit'],
      'protocol_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
      'training_real_source_selected_actions':1664,
      'test_original_FIT_episodes':len(episodes),
      'test_original_FIT_objective_trigger_counts':counts,
      'real_native_R12':native_stats,
      'independent_conventional':conv_stats,
      'original_public_collector':collector_stats,
      'native_conventional_choice_disagreements':sum(f['native_selection']['action']!=
         f['conventional_selection']['action'] for f in all_forks),
      'source_native_vs_conventional_real_effect_disagreements':sum(
         f['source_native_fork']['learned_objective_realized']!=
         f['source_conventional_fork']['learned_objective_realized'] for f in all_forks),
      'complete_original_source_episode_and_branch_evidence':episodes,
      'native_checkpoint_sha256':hashlib.sha256(native_blob).hexdigest(),
      'conventional_checkpoint_sha256':hashlib.sha256(conv_blob).hexdigest(),
      'native_checkpoint_bytes':len(native_blob),
      'conventional_checkpoint_bytes':len(conv_blob),
      'cpu_fit_s':round(t1-t0,6),'cpu_eval_s':round(time.process_time()-t1,6),
      'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'new_DEV_episodes_consumed':0,'protected_scientific_first_use':False,
      'original_owner_source_modified':False,
      'qualifier':'PUBLIC_FIT_ONE_STEP_EXPLICIT_OBJECTIVE_ONLY_NOT_AUTONOMOUS_GOAL_NAVIGATION'}
    out=Path(sys.argv[1]);out.write_bytes(owner.canonical(output)+b'\n')
    print('R7C31_ORIGINAL_SOURCE_R12_PHYSICAL_PUBLIC_OBJECTIVE_ACTIONS',
          json.dumps({k:v for k,v in output.items() if k!='complete_original_source_episode_and_branch_evidence'},sort_keys=True),flush=True)
if __name__=='__main__':
    main()
