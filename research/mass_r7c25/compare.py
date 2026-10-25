"""R7-C24: duplicate-run original-source science, selective causal info probe."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from research.native.itd02.r1.native_policy import canonical
P=json.loads((HERE/'PREREG.json').read_text())
D=Path(sys.argv[1])
source_sha=P['source']['upstream']
saved={}
for arm in P['arms']:
    independent=[json.loads((D/f'{arm}-{i}.json').read_text()) for i in (1,2)]
    for r in independent:
        assert r['schema']==P['schema'] and r['arm']==arm
        assert r['source']==source_sha
        assert r['native_head']==P['source']['original_r3_head']
        assert r['prereg_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
        assert r['fit_sha256']==P['fit']['expected_fit_sha256'] and r['fit_rows']==12
        assert len(r['episodes'])==sum(len(s) for s in P['dev'].values())
        assert r['max_checkpoint_bytes']>0 and r['max_cold_step3_bytes']>0
        assert r['cpu_fit_s']>=0 and r['cpu_dev_s']>=0 and r['max_rss_kib']>0
        for family,seeds in P['dev'].items():
            assert r['totals'][family]['episodes']==len(seeds)
            assert r['totals'][family]['steps']<=len(seeds)*P['actions_per_episode_cap']
        for ep in r['episodes']:
            assert ep['family'] in P['dev'] and ep['seed'] in P['dev'][ep['family']]
            assert len(ep['trace'])==ep['steps']
            assert hashlib.sha256(canonical(ep['trace'])).hexdigest()==ep['trace_sha256']
            assert ep['checkpoint_bytes']>0 and ep['cold_step3_checkpoint_bytes']>0
    for k in ('fit_sha256','fit_rows','fit_counts','fit_screen_info_turns','totals','episodes',
              'max_checkpoint_bytes','max_cold_step3_bytes'):
        assert independent[0][k]==independent[1][k],('INDEPENDENT_SCIENCE_MISMATCH',arm,k)
    saved[arm]=independent[0]
assert len({saved[arm]['fit_sha256'] for arm in P['arms']})==1
families=list(P['dev'])
totals={f:{a:saved[a]['totals'][f] for a in P['arms']} for f in families}
native=totals
active=[native[f]['native_active'] for f in families]
native_control=[native[f]['native_selective'] for f in families]
best_conv={}
for f in families:
    best_conv[f]=max((native[f][a] for a in P['arms'] if a.startswith('conventional')),
        key=lambda v:(v['wins'],-v['collision_terminal'],-v['steps']))
fit_count=sum(saved['native_active']['fit_screen_info_turns'].values())
assert fit_count>0,'ZERO_FIT_INFORMATION_TURNS'
probe_count=sum(x['information_turns'] for x in active)
native_not_worse=all(x['wins']>=c['wins'] and x['collision_terminal']<=c['collision_terminal']
       for x,c in zip(active,native_control))
conventional_dominates=any(best_conv[f]['wins']>=native[f]['native_active']['wins'] and
      best_conv[f]['collision_terminal']<=native[f]['native_active']['collision_terminal'] and
      best_conv[f]['steps']<=native[f]['native_active']['steps'] for f in families)
if probe_count==0:
    verdict='NO_GO_NO_ACTUAL_INFORMATION_INTERVENTIONS'
elif not native_not_worse:
    verdict='NO_GO_INFORMATION_PROBE_NATIVE_REGRESSION'
elif conventional_dominates:
    verdict='NO_NATIVE_SUPERIORITY_STRONG_CONVENTIONAL_PARITY_OR_DOMINANCE'
else:
    verdict='PUBLIC_DEVELOPMENT_MECHANISM_PENDING_INDEPENDENT_SCIENCE'
report={
    'schema':'mass.r7c25.original-source-fit-gated-information-reconciliation.v1',
    'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
    'source':source_sha,'original_owner_native_unchanged':True,
    'protected_first_use':False,
    'fit_sha256':P['fit']['expected_fit_sha256'],
    'two_independent_process_science_exact':True,
    'complete_bayesian_conventional_cold_action_restore':True,
    'native_fit_info_turns':fit_count,
    'native_actual_info_turns':probe_count,
    'native_active_noregression':native_not_worse,
    'conventional_parity_or_dominance':conventional_dominates,
    'scientific_decision':verdict,
    'by_family':totals,
    'resources':{a:{k:saved[a][k] for k in
           ('cpu_fit_s','cpu_dev_s','max_rss_kib','max_checkpoint_bytes','max_cold_step3_bytes')}
           for a in P['arms']}
}
blob=canonical(report)
(D/'comparison.json').write_bytes(blob+b'\n')
print('R7C25_TWO_INDEPENDENT_SOURCE_PROCESSES=PASS')
print('R7C25_RESULT_SHA256='+hashlib.sha256(blob).hexdigest())
print('R7C25_FIT_INFORMATION_INTERVENTIONS='+str(fit_count))
print('R7C25_DEV_INFORMATION_INTERVENTIONS='+str(probe_count))
print('R7C25_DECISION='+verdict)
for f in families:
    print('R7C25_FAMILY='+f+' '+json.dumps(totals[f],sort_keys=True))
