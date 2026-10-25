"""Mass R7-C20 fail-closed cross-arm, independent-process original-source evaluator."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'PREREG.json').read_text())
arms=('original','patched','conventional')
recs={}
for arm in arms:
    runs=[]
    for rep in (1,2):
        path=Path(sys.argv[1])/f'{arm}-{rep}.json'
        w=json.loads(path.read_text())
        assert w['arm']==arm
        assert w['upstream']==p['source_original']['commit']
        assert w['original_head']==p['yggdrasil']['r3_head']
        assert w['prereg_sha256']==hashlib.sha256((ROOT/'PREREG.json').read_bytes()).hexdigest()
        assert w['fit_rows']==12
        assert set(w['totals'])==set(p['source_original']['gym_ids'])
        assert len(w['episodes'])==len(p['source_original']['gym_ids'])*len(p['roles']['dev_seeds'])
        assert all(x['checkpoint_bytes']>0 for x in w['episodes'])
        assert w['cpu_fit_seconds']>=0 and w['cpu_dev_seconds']>=0
        assert w['peak_process_rss_kib']>0
        runs.append(w)
    for f in ('fit_sha256','fit_total','totals','episodes','max_checkpoint_bytes'):
        assert runs[0][f]==runs[1][f],('REPEAT_NONDETERMINISTIC',arm,f)
    recs[arm]=runs[0]
assert len({recs[a]['fit_sha256'] for a in arms})==1,'FIT_SOURCE_NOT_IDENTICAL_ACROSS_ARMS'
families=p['source_original']['gym_ids']
for f in families:
    for arm in arms:
        assert recs[arm]['totals'][f]['episodes']==len(p['roles']['dev_seeds'])
        assert recs[arm]['totals'][f]['actions']<=len(p['roles']['dev_seeds'])*p['roles']['dev_cap_steps']
decisions={}
for fam in families:
    a,b,c=(recs[x]['totals'][fam] for x in arms)
    decisions[fam]={
      'original':a,'corrected':b,'conventional':c,
      'corrected_reduces_blocked_attempts':b['blocked_forward']<a['blocked_forward'],
      'corrected_goal_nonregression':b['wins']>=a['wins'],
      'corrected_beats_conventional_goal':b['wins']>c['wins']
    }
stop='DEVELOPMENT_MECHANISM_NO_NATIVE_SUPERIORITY'
if all(v['corrected_reduces_blocked_attempts'] and v['corrected_goal_nonregression'] for v in decisions.values()):
    stop='DEVELOPMENT_SENSOR_FIX_GO_PENDING_EXTERNAL_AND_FULL_RESOURCE_ADMISSION'
if any(not v['corrected_goal_nonregression'] for v in decisions.values()):
    stop='FAIL_CORRECTED_GOAL_REGRESSION'
status={'schema':'mass.r7c20.authenticated-original-source-result.v1','source':p['source_original']['commit'],
        'fit_sha256':recs['original']['fit_sha256'],'scientific_status':stop,
        'protected_first_use':False,'original_owner_source_modified':False,
        'qualification': 'FOCUSED_SOURCE_ONLY_NOT_FULL_G29',
        'by_family':decisions,
        'resources':{k:{field:recs[k][field] for field in ('cpu_fit_seconds','cpu_dev_seconds','peak_process_rss_kib','max_checkpoint_bytes')} for k in arms}}
encoded=json.dumps(status,sort_keys=True,separators=(',',':')).encode()
(Path(sys.argv[1])/'comparison.json').write_bytes(encoded+b'\n')
print('R7C20_REPEATED_PUBLIC_ORIGINAL_SOURCE=PASS')
print('R7C20_RESULT_SHA256='+hashlib.sha256(encoded).hexdigest())
print('R7C20_DECISION='+stop)
for fam,row in decisions.items():
    print(fam,json.dumps({arm:row['corrected' if arm=='patched' else arm] for arm in arms},sort_keys=True))
