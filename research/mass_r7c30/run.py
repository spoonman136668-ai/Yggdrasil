"""Train original unchanged R11 against authentic original DoorKey action outcomes.

Research code stays separate; the source-original native owner R10/R11 source
is imported from a pinned checkout and never edited. All selected actions
are replayed by truly calling original MiniGrid reset/step, not by inventing
environment outcomes or treating prior collector labels as new source events.
"""
import collections,hashlib,importlib.util,json,os,random,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
P=json.loads((HERE/'PREREG.json').read_text())
owner_root=Path(os.environ['OWNER_R11_ROOT']).resolve()
assert owner_root.is_dir()
sys.path.insert(0,str(owner_root))
from research.native.itd02.r10 import public_adapter as owner
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
def sidecar(path,module):
    spec=importlib.util.spec_from_file_location(module,str(path))
    x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
    return x
collector=sidecar(ROOT/'research/mass_r7c29/collect.py','r7c30_original_source_collector')
control=sidecar(HERE/'control.py','r7c30_independent_categorical')

def native_label(prediction):
    p=prediction['predicted']
    if p is None:return None
    names=('front_changed','visible_door_state_changed','carrying_changed',
           'heading_changed','positive_reward','terminated','truncated')
    return sum(int(p[k])<<i for i,k in enumerate(names))

def run_source_fit(model,baseline,role,seeds,episode_indices):
    import gymnasium as gym
    import minigrid  # original registered source
    recs=[];all_predictions=[];events_total=0
    n_picks=n_opens=goals=0
    if role=='validation':
        trained_count=model.samples;baseline_count=baseline.samples
    for seed,index in zip(seeds,episode_indices):
        env=gym.make("MiniGrid-DoorKey-8x8-v0")
        adapter=owner.DoorKeyPublicAdapter()
        rng=random.Random(93617+7919*index)
        try:
            raw,_=env.reset(seed=seed)
            adapter.reset_public(collector.normalized_original_public(raw))
            if role=='training':
                model.start_session(adapter,f'r7c30-source-FIT-{seed}')
            history=[]
            for step in range(P['protocol_roles']['source_episode_action_cap']):
                public=owner.public_observation(collector.normalized_original_public(raw))
                cues=owner.public_cues(public)
                independent=collector.independent_cues(collector.normalized_original_public(raw))
                assert independent['front']==cues['front']
                assert independent['carried']==cues['carried']
                assert independent['direction']==cues['direction']
                control_front,control_carried=control.cues(public)
                assert control_front==cues['front'] and control_carried==cues['carried']
                action=collector.policy({'image':public['image'],'cues':cues},rng,step,{})
                if role=='validation':
                    npred=model.predict(public,action)
                    cpred=baseline.predict(public,action)
                assert adapter.submit(action)==action
                after,reward,done,truncated,_=env.step(action)
                event=adapter.complete(collector.normalized_original_public(after),
                                       float(reward),bool(done),bool(truncated))
                assert event['action']==action and event['pose_delta'] is None
                if role=='training':
                    native_selected=model.learn_selected(adapter)
                    assert native_selected['sample_index']==model.samples
                    baseline.learn(event)
                else:
                    actual=control.label(event)
                    nlab=native_label(npred)
                    clab=cpred['modal']
                    # Evaluate each learned predictor against the same exact
                    # ORIGINAL public effect label after the chosen source step.
                    assert ((nlab is None)==(clab is None)),('COVERAGE_DRIFT',seed,step)
                    all_predictions.append({
                        'seed':seed,'step':step,'action':action,
                        'actual_outcome_bits':actual,
                        'native_outcome_bits':nlab,
                        'conventional_outcome_bits':clab,
                        'native_samples':npred['samples'],
                        'conventional_samples':cpred['samples'],
                        'carrying_changed':bool(actual&4),
                        'door_state_changed':bool(actual&2),
                        'reward_positive':bool(actual&16),
                        'front_changed':bool(actual&1)})
                history.append({'step':step,'action':action,'name':event['action_name'],
                    'before_public_sha256':event['before_public_sha256'],
                    'after_public_sha256':event['after_public_sha256'],
                    'front_before':event['front_before'],'front_after':event['front_after'],
                    'carried_before':event['carried_before'],'carried_after':event['carried_after'],
                    'visible_key_pickup':event['visible_key_pickup'],
                    'visible_door_opened':event['visible_door_opened'],
                    'source_reward':event['reward'],'terminated':event['terminated'],
                    'truncated':event['truncated']})
                n_picks+=int(event['visible_key_pickup'])
                n_opens+=int(event['visible_door_opened'])
                goals+=int(event['reward']>0)
                events_total+=1
                raw=after
                if done or truncated:break
            digest=hashlib.sha256(owner.canonical(history)).hexdigest()
            assert digest==P['expected_prior_source_prefix_hashes'][str(seed)],('SOURCE_TRACE_IDENTITY_DRIFT',seed,digest)
            recs.append({'fit_seed':seed,'role':role,'actions':len(history),
                         'actual_goals':sum(int(t['source_reward']>0) for t in history),
                         'real_pickups':sum(int(t['visible_key_pickup']) for t in history),
                         'real_doors_opened':sum(int(t['visible_door_opened']) for t in history),
                         'prior_C29_source_prefix_sha256':digest,
                         'actual_source_selected_events':history})
        finally:env.close()
    if role=='validation':
        assert model.samples==trained_count and baseline.samples==baseline_count, 'VALIDATION_LEARNED'
    return {'role':role,'episodes':recs,'actual_selected_actions':events_total,
            'real_pickups':n_picks,'real_opened_doors':n_opens,
            'source_rewarded_goals':goals},all_predictions,public

def cold_verify(native_blob,conv_blob,public):
    # No dependence on the in-process source learner's internal object identity.
    npred=[PublicAffordanceCells.restore(native_blob).predict(public,i) for i in range(7)]
    cmodel=control.Control.restore(conv_blob)
    cpred=[cmodel.predict(public,i) for i in range(7)]
    payload=owner.canonical({'native':native_blob.decode(),'control':conv_blob.decode(),
                              'public':public,'native_expected':npred,'control_expected':cpred,
                              'control_file':str(HERE/'control.py')})
    program="""import importlib.util,json,sys
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
p=json.loads(sys.stdin.buffer.read())
spec=importlib.util.spec_from_file_location('original_independent',p['control_file'])
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
m=PublicAffordanceCells.restore(p['native'].encode())
c=s.Control.restore(p['control'].encode())
assert [m.predict(p['public'],a) for a in range(7)]==p['native_expected']
assert [c.predict(p['public'],a) for a in range(7)]==p['control_expected']
def broken(s):
 x=json.loads(s); x['sha256']=('0' if x['sha256'][0]!='0' else '1')+x['sha256'][1:]
 return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
for ctor,blob in ((PublicAffordanceCells,p['native']), (s.Control,p['control'])):
 try:ctor.restore(broken(blob))
 except ValueError:pass
 else:raise AssertionError('CORRUPTED_CHECKPOINT_ACCEPTED')
print('R7C30_OWNER_NATIVE_AND_CONVENTIONAL_COLD_RESTORE=PASS')
"""
    r=subprocess.run([sys.executable,'-B','-c',program],input=payload,
                     cwd=owner_root,capture_output=True,timeout=35,
                     env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode==0,('COLD_RESTORE_FAIL',r.stderr.decode())
    assert 'R7C30_OWNER_NATIVE_AND_CONVENTIONAL_COLD_RESTORE=PASS' in r.stdout.decode()
    return {'fresh_python_next_prediction_parity':True,'tamper_rejection_both':True,
            'native_checkpoint_bytes':len(native_blob),
            'conventional_checkpoint_bytes':len(conv_blob),
            'native_checkpoint_sha256':hashlib.sha256(native_blob).hexdigest(),
            'conventional_checkpoint_sha256':hashlib.sha256(conv_blob).hexdigest()}

def main():
    import gymnasium,minigrid
    assert owner.UPSTREAM_MINIGRID_COMMIT==P['upstream'].split('@')[-1]
    assert P['owner_R11_head']=='56e0c14393b8a7ddee479dbee6779f092f33267d'
    t0=time.process_time()
    m=PublicAffordanceCells()
    c=control.Control()
    tr,selections,public_train=run_source_fit(m,c,'training',
        P['protocol_roles']['training_fit_seeds'],
        list(range(len(P['protocol_roles']['training_fit_seeds']))))
    assert not selections
    assert m.samples==c.samples==tr['actual_selected_actions']
    assert tr['real_pickups']==8 and tr['real_opened_doors']==8,('TRAIN_NO_CAUSAL_EVENTS',tr['real_pickups'],tr['real_opened_doors'])
    native_blob=m.checkpoint();conv_blob=c.checkpoint()
    assert m.samples==1664,('FIT_SELECTED_EXPOSURE_DRIFT',m.samples)
    assert len(m.counts)<=512
    cold=cold_verify(native_blob,conv_blob,public_train)
    t1=time.process_time()
    val,results,public_val=run_source_fit(m,c,'validation',
        P['protocol_roles']['validation_fit_seeds'],list(range(8,12)))
    assert val['real_pickups']==4 and val['real_opened_doors']==4,('VALIDATION_NO_CAUSAL_EVENTS',val['real_pickups'],val['real_opened_doors'])
    assert m.checkpoint()==native_blob and c.checkpoint()==conv_blob, 'VALIDATION_MODEL_CHANGED'
    t2=time.process_time()
    total=len(results);covered=[x for x in results if x['native_outcome_bits'] is not None]
    native_correct=sum(x['native_outcome_bits']==x['actual_outcome_bits'] for x in covered)
    conv_correct=sum(x['conventional_outcome_bits']==x['actual_outcome_bits'] for x in covered)
    assert all(x['native_outcome_bits']==x['conventional_outcome_bits'] for x in covered),(
        'NATIVE_VS_SAME_DATA_CONVENTIONAL_DISAGREE_MODAL',)
    def group(key):
        rows=[x for x in results if x[key]]
        return {'events':len(rows),'covered':sum(x['native_outcome_bits'] is not None for x in rows),
                'native_exact':sum(x['native_outcome_bits']==x['actual_outcome_bits'] for x in rows if x['native_outcome_bits'] is not None),
                'conventional_exact':sum(x['conventional_outcome_bits']==x['actual_outcome_bits'] for x in rows if x['conventional_outcome_bits'] is not None)}
    validation={
        'selected_events':total,'source_public_context_covered':len(covered),
        'source_public_context_abstained':total-len(covered),
        'native_exact_event_predictions':native_correct,
        'independent_conventional_exact_event_predictions':conv_correct,
        'native_conventional_prediction_disagreements':0,
        'coverage_fraction':round(len(covered)/total,9),
        'native_exact_fraction_on_covered':round(native_correct/len(covered),9) if covered else None,
        'conventional_exact_fraction_on_covered':round(conv_correct/len(covered),9) if covered else None,
        'visible_pickup_events':group('carrying_changed'),
        'visible_door_state_change_events':group('door_state_changed'),
        'source_goal_reward_events':group('reward_positive'),
        'front_changes':group('front_changed'),
        'actual_preaction_prediction_receipts':results
    }
    output={'schema':P['schema'],'original_upstream':P['upstream'],
        'original_owner_R10':P['owner_R10_head'],'original_owner_R11':P['owner_R11_head'],
        'protocol_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'training':tr,'validation_source':val,'validation_predictions':validation,
        'trained_native_samples':m.samples,'trained_native_contexts':len(m.counts),
        'trained_conventional_samples':c.samples,'trained_conventional_contexts':len(c.counts),
        'full_cold_state':cold,'native_checkpoint_sha256':cold['native_checkpoint_sha256'],
        'conventional_checkpoint_sha256':cold['conventional_checkpoint_sha256'],
        'cpu_training_s':round(t1-t0,6),'cpu_validation_s':round(t2-t1,6),
        'peak_python_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'public_DEV_episodes':0,'protected_scientific_first_use':False,
        'original_native_owner_source_modified':False,
        'scientific_decision':'ORIGINAL_SOURCE_NATIVE_R11_EMPIRICAL_EFFECT_LEARNING_QUALIFIED_NO_CONVENTIONAL_ADVANTAGE'}
    out=Path(sys.argv[1]);out.write_bytes(owner.canonical(output)+b'\n')
    (out.parent/('checkpoint-native-'+out.stem+'.json')).write_bytes(native_blob+b'\n')
    (out.parent/('checkpoint-conventional-'+out.stem+'.json')).write_bytes(conv_blob+b'\n')
    print('R7C30_NATIVE_ORIGINAL_SOURCE_REAL_FIT_SAMPLES='+str(m.samples))
    print('R7C30_ORIGINAL_SOURCE_PUBLIC_VALIDATION',json.dumps({k:v for k,v in validation.items() if k!='actual_preaction_prediction_receipts'},sort_keys=True))
    print('R7C30_NATIVE_INDEPENDENT_CONVENTIONAL_PARITY=PASS')
    print('R7C30_FULL_OS_COLD_SOURCE_MEMORY=PASS')
if __name__=='__main__':main()
