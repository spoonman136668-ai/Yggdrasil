#!/usr/bin/env python3
import hashlib,bz2,tarfile,json,io
from pathlib import Path
P=Path(__file__).resolve().parent
h=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((P/'result.json').read_text());checks=0
for name,info in r['source_custody'].items():
    if name in ('experiment.py','audit.py'): continue
    b=(P/name).read_bytes()
    assert len(b)==info['bytes'] and h(b)==info['sha256'],name
    checks+=1
with tarfile.open(P/'source.tar.bz2','r:bz2') as f:
    for fn in ('experiment.py','audit.py'):
        b=f.extractfile(fn).read();i=r['source_custody'][fn]
        assert len(b)==i['bytes'] and h(b)==i['sha256']
        checks+=1
for key in ('smoke','smoke2'):
    raw=bz2.decompress((P/(key+'.json.bz2')).read_bytes())
    assert h(raw)==r['source_custody'][key+'.json']['sha256'];a=json.loads(raw)
    assert len(a['cases'])==r['screen'][key]['worlds'] and a['seeds']==[r['screen'][key]['seed']]
    assert a['summary']['gates_passed']==2 and a['summary']['gates_total']==9
    assert a['summary']['gates']==r['screen'][key]['gates']
    assert set(a['cases'][0]['selected'])==set(['contradiction_energy','contradiction_dense','committee','diverse','random','shuffled_contradiction','fixed'])
    for c in a['cases']:
        for sel in c['selected'].values(): assert len(sel)==24 and len(set(sel))==24
    aud=json.loads(bz2.decompress((P/(key+'_audit.json.bz2')).read_bytes()))
    assert aud['status']=='PASS' and aud['cases']==len(a['cases'])
    assert aud['checks']==r['screen'][key]['audit']['checks']
    checks+=len(a['cases'])*7+7
assert r['primary_scored'] is False and r['classification']=='DEVELOPMENT_SCREEN_NO_GO'
assert sum(r['screen'][k]['audit']['checks'] for k in ('smoke','smoke2'))==949
print('ENERGY48_SCREEN_ARCHIVE_PASS:',checks,'integrity checks; 949 independently refitted scientific checks; PRIMARY NOT RUN')
