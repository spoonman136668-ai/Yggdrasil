"""Mass R7-C32: actual original DoorKey source end-to-end *engineering* delegation.

R12 remains an original unchanged FIT-learned local effect chooser. A publicly
hand-coded mission-stage selector and collector still supply high-level control
and route navigation; this NEVER certifies native autonomous mission inference.
"""
import hashlib,json,os,random,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
P=json.loads((HERE/'PREREG.json').read_text())
owner_root=Path(os.environ['OWNER_R11_ROOT']).resolve()
assert owner_root.is_dir()
sys.path.insert(0,str(owner_root))
from research.native.itd02.r10 import public_adapter as owner
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
from research.native.itd02.r12.outcome_choice import select_public_action
from research.mass_r7c31 import run as c31
from research.mass_r7c30 import run as c30
from research.mass_r7c29 import collect as collector
control=c30.control
ARMS=tuple(P['arms'])

def mission_stage(cues,mission):
    # This finite-stage program is HANDCODED, not discovered by native R12.
    assert mission==owner.MISSION
    carried=cues['carried']
    if carried is None:return 'carrying_changed'
    return 'visible_door_state_changed'

def eligible(cues,objective):
    front,carry=cues['front'],cues['carried']
    if objective=='carrying_changed':
        return front[0]==5 and carry is None
    if objective=='visible_door_state_changed':
        return front[0]==4 and front[2] in (1,2) and carry is not None
    return False

def cold_adapter(blob,event_count):
    program="""import json,sys
from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter
m=DoorKeyPublicAdapter.restore(sys.stdin.buffer.read())
assert m.events==int(sys.argv[1]) and m.pending is None
print('R7C32_REAL_SOURCE_R10_COLD_RESTORE=PASS')
"""
    x=subprocess.run([sys.executable,'-B','-c',program,str(event_count)],
        input=blob,cwd=owner_root,capture_output=True,timeout=30,
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    assert x.returncode==0,('ADAPTER_COLD_FAIL',x.stderr.decode())
    assert 'R7C32_REAL_SOURCE_R10_COLD_RESTORE=PASS' in x.stdout.decode()

def play(arm,seed,index,native,conv,native_blob,conv_blob):
    import gymnasium as gym,minigrid
    env=gym.make('MiniGrid-DoorKey-8x8-v0')
    adapter=owner.DoorKeyPublicAdapter()
    rng=random.Random(93617+7919*index)
    log=[];state={'arm':arm,'seed':seed,'source_actions':0,'goals':0,'total_reward':0.,
        'key_pickups':0,'door_openings':0,'objective_eligible':0,
        'trained_action_delegations':0,'trained_action_abstentions':0,
        'trained_action_changed_collector':0,'negative_reward_terminated':0,
        'terminated':False,'truncated':False}
    try:
        raw,_=env.reset(seed=seed)
        adapter.reset_public(collector.normalized_original_public(raw))
        for step in range(P['source_step_cap']):
            normalized=collector.normalized_original_public(raw)
            public=owner.public_observation(normalized)
            cues=owner.public_cues(public)
            assert collector.independent_cues(normalized)['front']==cues['front']
            objective=mission_stage(cues,public['mission'])
            can_learn=eligible(cues,objective)
            collector_action=collector.policy({'image':public['image'],'cues':cues},rng,step,{})
            action=collector_action
            learned=None
            if can_learn:
                state['objective_eligible']+=1
                if arm=='native_local_effect_delegation':
                    learned=select_public_action(native,public,objective,min_samples=1)
                    action=learned['action'] if learned['action'] is not None else collector_action
                elif arm=='conventional_equal_learned_effect_delegation':
                    learned=c31.independent_choice(conv,public,objective)
                    action=learned['action'] if learned['action'] is not None else collector_action
                if learned is not None:
                    if learned['action'] is None:
                        state['trained_action_abstentions']+=1
                    else:
                        state['trained_action_delegations']+=1
                        state['trained_action_changed_collector']+=int(action!=collector_action)
                        assert action in range(7)
                        if state['trained_action_delegations']==1:
                            expected_native=select_public_action(native,public,objective,min_samples=1)
                            expected_conv=c31.independent_choice(conv,public,objective)
                            c31.os_restore_action(native_blob,conv_blob,public,objective,
                                 expected_native['action'],expected_conv['action'])
            assert type(action)is int and 0<=action<7
            assert adapter.submit(action)==action
            next_obs,reward,terminated,truncated,_=env.step(action)
            event=adapter.complete(collector.normalized_original_public(next_obs),
                        float(reward),bool(terminated),bool(truncated))
            assert event['action']==action and event['ordinal']==step+1
            state['source_actions']+=1;state['total_reward']+=float(reward)
            state['key_pickups']+=int(event['visible_key_pickup'])
            state['door_openings']+=int(event['visible_door_opened'])
            state['goals']+=int(reward>0)
            state['negative_reward_terminated']+=int(terminated and reward<0)
            log.append({'t':step,'a':action,'collector_a':collector_action,
                'mission_stage':objective,'stage_eligible':can_learn,
                'learned_action':None if learned is None else learned['action'],
                'public_before_sha256':event['before_public_sha256'],
                'public_after_sha256':event['after_public_sha256'],
                'public_carry_before':event['carried_before'],
                'public_carry_after':event['carried_after'],
                'front_before':event['front_before'],'front_after':event['front_after'],
                'pickup':event['visible_key_pickup'],'opened':event['visible_door_opened'],
                'r':float(reward),'done':bool(terminated),'trunc':bool(truncated)})
            raw=next_obs
            if terminated or truncated:
                state['terminated']=bool(terminated)
                state['truncated']=bool(truncated)
                break
        snap=adapter.checkpoint()
        cold_adapter(snap,len(log))
        state['total_reward']=round(state['total_reward'],9)
        state['R10_checkpoint_bytes']=len(snap)
        state['R10_checkpoint_sha256']=hashlib.sha256(snap).hexdigest()
        state['trace_sha256']=hashlib.sha256(owner.canonical(log)).hexdigest()
        return state,log
    finally:env.close()

def main():
    import gymnasium as gym,minigrid
    assert owner.UPSTREAM_MINIGRID_COMMIT==P['original_minigrid'].split('@')[-1]
    assert P['source_owner_r12_head']=='6e2d4a219b1fb62e0124ba053b65b7e3fdd46546'
    t0=time.process_time()
    native=PublicAffordanceCells();conventional=control.Control()
    train,_,last=c30.run_source_fit(native,conventional,'training',
                 P['original_FIT_training_seeds'],list(range(8)))
    assert train['actual_selected_actions']==P['expected_selected_actual_effect_training_rows']
    assert native.samples==conventional.samples==1664
    assert train['real_pickups']==train['real_opened_doors']==8
    nblob=native.checkpoint();cblob=conventional.checkpoint()
    c30.cold_verify(nblob,cblob,last)
    fit_cpu=time.process_time()-t0
    records=[];totals={}
    for arm in ARMS:
        states=[];raw_logs=[]
        for index,seed in enumerate(P['fresh_independent_original_FIT_seeds']):
            state,log=play(arm,seed,index,native,conventional,nblob,cblob)
            states.append(state);raw_logs.append({'seed':seed,'events':log})
        totals[arm]={
            'episodes':len(states),'source_goals':sum(x['goals'] for x in states),
            'source_steps':sum(x['source_actions'] for x in states),
            'source_reward_sum':round(sum(x['total_reward'] for x in states),9),
            'actual_key_pickups':sum(x['key_pickups'] for x in states),
            'actual_door_openings':sum(x['door_openings'] for x in states),
            'public_stage_eligible':sum(x['objective_eligible'] for x in states),
            'delegated_R12_or_conventional_learner_calls':sum(x['trained_action_delegations'] for x in states),
            'learner_abstentions':sum(x['trained_action_abstentions'] for x in states),
            'learned_action_vs_collector_diff':sum(x['trained_action_changed_collector'] for x in states),
            'max_public_adapter_checkpoint_bytes':max(x['R10_checkpoint_bytes'] for x in states)}
        records.append({'arm':arm,'episodes':states,'complete_original_public_step_records':raw_logs})
    assert native.checkpoint()==nblob and conventional.checkpoint()==cblob, 'TEST_SOURCE_WEIGHT_LEAK'
    assert all(v['episodes']==len(P['fresh_independent_original_FIT_seeds']) for v in totals.values())
    # End-to-end source trace equality is an observed fact, not a fabricated
    # implication from the earlier C31 one-step equality.
    first=records[0]['complete_original_public_step_records']
    pair_agreements={}
    for rec in records[1:]:
        pair_agreements[rec['arm']]=sum(
            rec['complete_original_public_step_records'][i]['events']==first[i]['events']
            for i in range(len(first)))
    out={'schema':P['schema'],
        'source_original':P['original_minigrid'],
        'native_owner_head':P['source_owner_r12_head'],
        'protocol_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'FIT_original_selected_actions':1664,
        'original_R12_checkpoint_sha256':hashlib.sha256(nblob).hexdigest(),
        'independent_conventional_checkpoint_sha256':hashlib.sha256(cblob).hexdigest(),
        'native_checkpoint_bytes':len(nblob),'conventional_checkpoint_bytes':len(cblob),
        'manual_stage_policy_NOT_learned':True,
        'hand_written_navigation_collector_NOT_native':True,
        'per_arm_actual_source':totals,
        'native_vs_other_exact_complete_episode_counts':pair_agreements,
        'original_episode_and_step_evidence':records,
        'fit_cpu_s':round(fit_cpu,6),
        'test_cpu_s':round(time.process_time()-t0-fit_cpu,6),
        'peak_full_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'source_dev_episodes_consumed':0,'protected_first_use':False,
        'owner_source_changed':False}
    Path(sys.argv[1]).write_bytes(owner.canonical(out)+b'\n')
    print('R7C32_DOORKEY_ORIGINAL_PUBLIC_SEQUENCE',
          json.dumps({k:v for k,v in out.items() if k!='original_episode_and_step_evidence'},
          sort_keys=True),flush=True)
if __name__=='__main__':main()
