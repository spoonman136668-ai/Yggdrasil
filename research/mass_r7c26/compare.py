"""R7-C26 fail-closed science: equal-cost original-source action forks + sensor blind."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PREREG.json').read_text())
D=Path(sys.argv[1]);data={}
for kind in ('native','conventional'):
    rs=[json.loads((D/f'{kind}-{i}.json').read_text()) for i in (1,2)]
    for r in rs:
        assert r['schema']==P['schema'] and r['kind']==kind
        assert r['source']==P['source']['upstream'] and r['owner_R3_head']==P['source']['owner_r3_head']
        assert r['protocol_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
        assert r['fit_sha256']==P['fit']['expected_sha256'] and r['fit_examples']==12
        assert len(r['traces'])==sum(len(x) for x in P['fresh_public_dev'].values())
        for fam,seeds in P['fresh_public_dev'].items():
            assert r['summary'][fam]['episodes']==len(seeds)
        for e in r['traces']:
            assert e['family'] in P['fresh_public_dev'] and e['seed'] in P['fresh_public_dev'][e['family']]
            if e['fork_step'] is None:
                assert 'fork_branches' not in e
                continue
            assert e['fork_step']>=0
            a=e['fork_branches']
            assert set(a)==({'information','sham','information_blind'} if kind=='native'
                            else {'information','sham'})
            assert a['information']['first_action'] in (0,1)
            assert a['sham']['first_action']==1-a['information']['first_action']
            for b in a.values():
                assert b['actions']>e['fork_step'] and b['checkpoint_bytes']>0
                assert b['actions']==len(b['trace'])
                assert hashlib.sha256(json.dumps(b['trace'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==b['trace_sha256']
                assert b['trace_sha256'] and b['checkpoint_sha256']
                assert len(b['first_after_turn_source_row'])==16
            if kind=='native':
                assert a['information']['first_after_turn_source_row']==a['information_blind']['first_after_turn_source_row']
                assert a['information']['first_revealed_public_front_blocked']==a['information_blind']['first_revealed_public_front_blocked']
                if a['information_blind']['actions']>e['fork_step']+1:
                    assert a['information_blind']['blind_actions']==1
    for field in ('fit_sha256','fit_counts','summary','traces'):
        assert rs[0][field]==rs[1][field],('NONDETERMINISTIC_SOURCE_REPLAY',kind,field)
    data[kind]=rs[0]

def pair_stats(kind, fam):
    rows=[e for e in data[kind]['traces'] if e['family']==fam and e['fork_step'] is not None]
    def d(a,b,field):
        return sum((e['fork_branches'][a][field]-e['fork_branches'][b][field]) for e in rows)
    o={'forked_seeds':len(rows),'source_episodes':len(P['fresh_public_dev'][fam]),
       'info_minus_sham_goals':d('information','sham','success'),
       'info_minus_sham_actions':d('information','sham','actions'),
       'info_minus_sham_rewards':round(d('information','sham','reward'),8),
       'same_one_turn_cost_for_both':all(e['fork_branches']['information']['first_action'] in (0,1)
                                        and e['fork_branches']['sham']['first_action'] in (0,1)
                                        for e in rows)}
    if kind=='native':
        o.update({'info_minus_blind_goals':d('information','information_blind','success'),
          'info_minus_blind_actions':d('information','information_blind','actions'),
          'info_minus_blind_rewards':round(d('information','information_blind','reward'),8),
          'postturn_first_choice_differences':sum(
             e['fork_branches']['information']['first_postturn_action']!=
             e['fork_branches']['information_blind']['first_postturn_action'] for e in rows),
          'newly_revealed_blocked_fronts':sum(
             e['fork_branches']['information']['first_revealed_public_front_blocked'] for e in rows),
          'same_physical_information_probe_source_outcome':all(
             e['fork_branches']['information']['first_after_turn_source_row']==
             e['fork_branches']['information_blind']['first_after_turn_source_row'] for e in rows)})
    return o

paired={k:{fam:pair_stats(k,fam) for fam in P['fresh_public_dev']} for k in data}
native=list(paired['native'].values())
total_forks=sum(x['forked_seeds'] for x in native)
actions_used=sum(x['postturn_first_choice_differences'] for x in native)
if total_forks==0:
    verdict='NO_GO_NO_GENUINE_ORIGINAL_SOURCE_FORK'
elif actions_used==0:
    verdict='NO_GO_REVEALED_SENSOR_DID_NOT_CHANGE_IMMEDIATE_NEXT_DECISION'
elif sum(x['info_minus_blind_goals'] for x in native)<=0 and sum(x['info_minus_blind_rewards'] for x in native)<=0:
    verdict='NO_GO_INFORMATION_NO_POSITIVE_CAUSAL_UTILITY_ON_PUBLIC_DEV'
else:
    verdict='PUBLIC_DEV_SENSOR_INFORMATION_CAUSAL_SIGNAL_NO_NATIVE_SUPERIORITY'
result={'schema':'mass.r7c26.reconciled-original-source-evaluator-forks.v1',
        'source':P['source']['upstream'],
        'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'fit_sha256':P['fit']['expected_sha256'],
        'two_independent_full_original_executions_identical':True,
        'owner_original_R3_unchanged':True,'protected_scientific_first_use':False,
        'evaluator_cloning_only_no_hidden_policy_inputs':True,
        'first_turn_cost_equal_but_heading_route_confounded':True,
        'native_matched_forks':total_forks,'native_immediate_next_choice_changes_due_to_sensor':actions_used,
        'paired':paired,
        'scientific_decision':verdict,
        'resource_usage':{kind:{key:data[kind][key] for key in ('cpu_fit_s','cpu_dev_s','peak_rss_kib')}
                          for kind in data}}
blob=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
(D/'comparison.json').write_bytes(blob+b'\n')
print('R7C26_TWO_INDEPENDENT_ORIGINAL_SOURCE_PROCESSES=PASS')
print('R7C26_REPORT_SHA256='+hashlib.sha256(blob).hexdigest())
print('R7C26_NATIVE_PAIRED_FORKS='+str(total_forks))
print('R7C26_NATIVE_SENSOR_CHANGED_NEXT_ACTION='+str(actions_used))
print('R7C26_SCIENTIFIC_DECISION='+verdict)
for kind in paired:
    for family,row in paired[kind].items():
        print('R7C26_PAIRED '+kind+' '+family+' '+json.dumps(row,sort_keys=True))
