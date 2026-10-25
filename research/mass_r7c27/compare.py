"""R7-C27 fail-closed actual original-world causal information-use reconciliation."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from research.native.itd02.r1.native_policy import canonical
P=json.loads((HERE/'PREREG.json').read_text())
D=Path(sys.argv[1]);data={}
for kind in P['arms']:
    kind_name='native' if kind=='native_active' else 'conventional'
    rs=[json.loads((D/f'{kind_name}-{i}.json').read_text()) for i in (1,2)]
    for r in rs:
        assert r['schema']==P['schema'] and r['kind']==kind_name
        assert r['source']==P['source']['upstream'] and r['native_owner_head']==P['source']['native_owner_head']
        assert r['protocol_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
        assert r['fit_sha256']==P['fit']['public_actions_sha256'] and r['fit_rows']==12
        assert len(r['episodes'])==sum(len(s) for s in P['new_public_dev'].values())
        assert r['whole_process_peak_rss_kib']>0 and r['fit_cpu_s']>=0 and r['dev_cpu_s']>=0
        for family,seeds in P['new_public_dev'].items():
            assert r['summary'][family]['episodes']==len(seeds)
        for episode in r['episodes']:
            assert episode['family'] in P['new_public_dev'] and episode['seed'] in P['new_public_dev'][episode['family']]
            for fork in episode['forks']:
                assert fork['fork_step']>=0
                b=fork['branches']
                assert set(b)=={'information','information_blind','known_side_sham'}
                i,blind,sham=(b[k] for k in ('information','information_blind','known_side_sham'))
                assert i['first_action']==blind['first_action'] and i['first_action'] in (0,1)
                assert sham['first_action']==1-i['first_action']
                assert i['first_source_row']==blind['first_source_row']
                assert i['first_revealed_observation']==blind['first_revealed_observation']
                assert i['new_obstacle_blocked']==blind['new_obstacle_blocked']
                assert i['new_obstacle_blocked'] in (0,1)
                for x in b.values():
                    assert x['checkpoint_bytes']>0 and x['one_turn_cost']==1
                    assert x['actions']==len(x['trace']) and x['actions']<=P['max_source_episode_actions']
                    assert x['trace_sha256']==hashlib.sha256(canonical(x['trace'])).hexdigest()
                if i['actions']>fork['fork_step']+1:
                    assert blind['blinded_readings']==1
    for field in ('fit_sha256','fit_rows','fit_counts','FIT_original_qualification','summary','episodes'):
        assert rs[0][field]==rs[1][field],('DETERMINISTIC_DUPLICATE_FAILED',kind_name,field)
    data[kind_name]=rs[0]
native=data['native'];conventional=data['conventional']
assert sum(x['revealed_blocked'] for x in native['FIT_original_qualification'].values())>0
totals={}
for name,d in data.items():
    totals[name]={}
    for fam in P['new_public_dev']:
        x=d['summary'][fam]
        by_outcome={}
        for label in ('blocked','clear','all'):
            cohort=x[label]
            assert cohort['forks']>=0
            by_outcome[label]=cohort
        assert x['forks']==x['blocked']['forks']+x['clear']['forks']
        totals[name][fam]={'episodes':x['episodes'],'parent_goals':x['parent_goals'],
                           'forks':x['forks'],'blocked':by_outcome['blocked'],
                           'clear':by_outcome['clear'],'all':by_outcome['all']}
native_blocked=sum(totals['native'][fam]['blocked']['forks'] for fam in P['new_public_dev'])
native_clear=sum(totals['native'][fam]['clear']['forks'] for fam in P['new_public_dev'])
native_blocked_choice=sum(totals['native'][fam]['blocked']['info_vs_blind_postturn_choice_diff'] for fam in P['new_public_dev'])
native_blocked_reward=sum(totals['native'][fam]['blocked']['info_minus_blind_reward'] for fam in P['new_public_dev'])
native_blocked_goal=sum(totals['native'][fam]['blocked']['info_goals']-totals['native'][fam]['blocked']['blind_goals'] for fam in P['new_public_dev'])
if native_blocked==0:
    verdict='NO_GO_NO_UNEXPECTED_PUBLIC_BLOCKED_DISCOVERY_ON_NEW_DEV'
elif native_blocked_choice==0:
    verdict='NO_GO_OBSTACLE_DISCOVERED_BUT_NO_DIFFERENT_POSTTURN_ACTION'
elif native_blocked_goal<=0 and native_blocked_reward<=0:
    verdict='NO_GO_NEW_OBSTACLE_SENSOR_AFFECTED_ACTION_WITHOUT_POSITIVE_TASK_GAIN'
else:
    verdict='PUBLIC_DEV_NEW_OBSTACLE_INFORMATION_ACTION_EFFECT_REQUIRES_STRONGER_INDEPENDENT_SCIENCE'
out={'schema':'mass.r7c27.reconciled-original-public-surprise-information-ablation.v1',
     'source':P['source']['upstream'],
     'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
     'FIT_blocked_original_qualification':native['FIT_original_qualification'],
     'fit_sha256':P['fit']['public_actions_sha256'],
     'two_complete_original_source_processes_identical':True,
     'protected_scientific_first_use':False,'native_owner_source_unchanged':True,
     'evaluator_only_exact_source_cloning':True,
     'native_blocked_information_forks':native_blocked,
     'native_clear_information_forks':native_clear,
     'native_blocked_next_action_effects':native_blocked_choice,
     'native_blocked_goal_difference':native_blocked_goal,
     'native_blocked_reward_difference':round(native_blocked_reward,8),
     'scientific_decision':verdict,'by_family':totals,
     'resources':{name:{k:d[k] for k in
         ('fit_cpu_s','dev_cpu_s','whole_process_peak_rss_kib')} for name,d in data.items()}}
b=canonical(out);(D/'comparison.json').write_bytes(b+b'\n')
print('R7C27_ORIGINAL_SOURCE_DOUBLE_PROCESS=PASS')
print('R7C27_REPORT_SHA256='+hashlib.sha256(b).hexdigest())
print('R7C27_NATIVE_BLOCKED_FORKS='+str(native_blocked))
print('R7C27_NATIVE_BLOCKED_NEXT_ACTION_EFFECTS='+str(native_blocked_choice))
print('R7C27_SCIENTIFIC_DECISION='+verdict)
for name in totals:
    for fam,x in totals[name].items():
        print('R7C27_PAIRED '+name+' '+fam+' '+json.dumps(x,sort_keys=True))
