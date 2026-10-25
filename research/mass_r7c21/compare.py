"""Source-first R7-C21: independent-run equality + prespecified scientific veto."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research.native.itd02.r1.native_policy import canonical
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PREREG.json').read_text())
folder=Path(sys.argv[1]);arms=P['arms'];model={}
for arm in arms:
    runs=[json.loads((folder/f"{arm}-{i}.json").read_text()) for i in (1,2)]
    for w in runs:
        assert w['schema']=='mass.r7c21.public-original-source.v1'
        assert w['arm']==arm
        assert w['source_commit']==P['original_source'].split('@')[-1]
        assert w['native_head']==P['original_r3']
        assert w['prereg_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
        assert w['fit_rows']==12
        assert len(w['episodes'])==len(P['source_types'])*len(P['dev_roles']['fresh_dev_seeds'])
        assert w['max_checkpoint_bytes']>0
        assert w['peak_process_rss_kib']>0
        assert w['cpu_fit_seconds']>=0 and w['cpu_dev_seconds']>=0
    for field in ('fit_sha256','fit_rows','fit_source_actions','totals','episodes','max_checkpoint_bytes'):
        assert runs[0][field]==runs[1][field],('R7C21_INDEPENDENT_REPRODUCTION_FAIL',arm,field)
    for e in runs[0]['episodes']:
        assert e['seed'] in P['dev_roles']['fresh_dev_seeds']
        assert e['family'] in P['source_types']
        assert e['steps']==len(e['trace'])
        assert hashlib.sha256(canonical(e['trace'])).hexdigest()==e['trace_sha256']
    model[arm]=runs[0]
assert len({model[a]['fit_sha256'] for a in arms})==1,'FIT_NOT_IDENTICAL'
decision={}
for family in P['source_types']:
    row={a:model[a]['totals'][family] for a in arms}
    expected=len(P['dev_roles']['fresh_dev_seeds'])
    assert all(x['episodes']==expected for x in row.values())
    assert all(x['actions']<=expected*P['dev_roles']['max_actions_per_episode'] for x in row.values())
    decision[family]=row
four='MiniGrid-FourRooms-v0'
o,g,m,c=[decision[four][a] for a in arms]
claim='NO_NATIVE_NAVIGATION_SUPERIORITY'
if m['wins']>=o['wins'] and m['wins']>=g['wins'] and m['blocked_forward']<=g['blocked_forward']:
    claim='DEVELOPMENT_MECHANISM_PASS_PENDING_INDEPENDENT_SCIENCE'
if m['wins']<o['wins'] or m['wins']<g['wins']:
    claim='NO_GO_GOAL_REGRESSION'
if m['wins']<c['wins']:
    claim='NO_GO_CONVENTIONAL_BEATS_NATIVE'
# All results survive a NO-GO, there is no automatic promotion.
report={'schema':'mass.r7c21.reconciled-source-results.v1','qualification':'FOCUSED_DEVELOPMENT_ONLY',
        'source_commit':P['original_source'].split('@')[-1],
        'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'fit_sha256':model[arms[0]]['fit_sha256'],
        'two_independent_executions_identical':True,
        'protected_first_use':False,
        'native_owner_source_unchanged':True,
        'by_family':decision,'scientific_decision':claim,
        'resources':{a:{k:model[a][k] for k in
                     ('cpu_fit_seconds','cpu_dev_seconds','peak_process_rss_kib','max_checkpoint_bytes')} for a in arms}}
body=canonical(report)
(folder/'comparison.json').write_bytes(body+b'\n')
print('R7C21_TWO_INDEPENDENT_EXECUTIONS=PASS')
print('R7C21_COMPARISON_SHA256='+hashlib.sha256(body).hexdigest())
print('R7C21_SCIENTIFIC_DECISION='+claim)
for f in P['source_types']:
    print('R7C21_FAMILY='+f+' '+json.dumps(decision[f],sort_keys=True))
