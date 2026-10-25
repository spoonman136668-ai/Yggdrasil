"""R7-C23 strict independent duplicate original-source evaluation and negative archive."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from research.native.itd02.r1.native_policy import canonical
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PREREG.json').read_text())
D=Path(sys.argv[1]);arm_records={}
for arm in P['arms']:
    runs=[json.loads((D/f'{arm}-{k}.json').read_text()) for k in (1,2)]
    for row in runs:
        assert row['schema']==P['schema'] and row['arm']==arm
        assert row['protocol_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
        assert row['upstream']==P['original_source'].split('@')[-1]
        assert row['owner_native_head']==P['owner_native_head']
        assert row['fit_sha256']==P['fit']['expected_fit_sha256']
        assert row['fit_rows']==P['fit']['selected_rows']
        assert len(row['episodes'])==len(P['dev']['static_seeds'])+len(P['dev']['dynamic_seeds'])
        assert row['peak_process_rss_kib']>0
        assert row['cpu_fit_seconds']>=0 and row['cpu_dev_seconds']>=0
        for fam,seeds in ((P['static_original'],P['dev']['static_seeds']),
                          (P['moving_original'],P['dev']['dynamic_seeds'])):
            assert row['totals'][fam]['episodes']==len(seeds)
            assert row['totals'][fam]['actions']<=len(seeds)*P['dev']['source_task_action_cap']
        for e in row['episodes']:
            assert (e['family']==P['static_original'] and e['seed'] in P['dev']['static_seeds'] or
                    e['family']==P['moving_original'] and e['seed'] in P['dev']['dynamic_seeds'])
            assert len(e['trace'])==e['steps'] and e['checkpoint_bytes']>0
            assert hashlib.sha256(canonical(e['trace'])).hexdigest()==e['trace_sha256']
    for field in ('fit_sha256','fit_rows','fit_counts','totals','episodes','max_checkpoint_bytes'):
        assert runs[0][field]==runs[1][field],('REPRODUCIBILITY_FAIL',arm,field)
    arm_records[arm]=runs[0]
assert len({arm_records[a]['fit_sha256'] for a in P['arms']})==1
t={fam:{a:arm_records[a]['totals'][fam] for a in P['arms']}
   for fam in (P['static_original'],P['moving_original'])}
sel={f:t[f]['native_selective'] for f in t}
persist={f:t[f]['native_persistent'] for f in t}
conv={f:[t[f][a] for a in P['arms'] if a.startswith('conventional')]
      for f in t}
native_mech_ok=all(sel[f]['wins']>=persist[f]['wins'] and
  sel[f]['collision_terminated']<=persist[f]['collision_terminated'] for f in t)
conventional_dom=any(any(k['wins']>=sel[f]['wins'] and
  k['collision_terminated']<=sel[f]['collision_terminated'] and
  k['actions']<=sel[f]['actions'] for k in conv[f]) for f in t)
if not native_mech_ok:
    verdict='NO_GO_SELECTIVE_NATIVE_REGRESSION'
elif conventional_dom:
    verdict='NO_NATIVE_SUPERIORITY_CONVENTIONAL_PARITY_OR_DOMINANCE'
else:
    verdict='PUBLIC_DEVELOPMENT_IMPROVEMENT_REQUIRES_EXTERNAL_FIRST_USE_AND_RESOURCE_QUALIFICATION'
output={'schema':'mass.r7c23.reconciled-original-source-development.v1',
        'source':P['original_source'],'source_dynamic_blob':P['source_dynamic_blob'],
        'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'fit_sha256':P['fit']['expected_fit_sha256'],
        'two_independent_process_runs_identical':True,
        'owner_R3_unchanged':True,'protected_scientific_first_use':False,
        'scientific_decision':verdict,'native_mechanism_no_regression':native_mech_ok,
        'conventional_parity_or_dominance':conventional_dom,
        'by_family':t,'resources':{a:{key:arm_records[a][key] for key in
          ('cpu_fit_seconds','cpu_dev_seconds','peak_process_rss_kib','max_checkpoint_bytes')}
          for a in P['arms']}}
blob=canonical(output)
(D/'comparison.json').write_bytes(blob+b'\n')
print('R7C23_TWO_INDEPENDENT_SOURCE_PROCESS_RUNS=PASS')
print('R7C23_REPORT_SHA256='+hashlib.sha256(blob).hexdigest())
print('R7C23_SCIENTIFIC_DECISION='+verdict)
for fam in t:
    print('R7C23_FAMILY',fam,json.dumps(t[fam],sort_keys=True))
