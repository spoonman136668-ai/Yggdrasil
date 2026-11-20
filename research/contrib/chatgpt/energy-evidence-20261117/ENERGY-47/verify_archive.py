#!/usr/bin/env python3
"""ENERGY-47 read-only custody and pre-primary negative screen verifier."""
from pathlib import Path
import bz2,tarfile,json,hashlib,io
P=Path(__file__).resolve().parent
s=json.loads((P/'result.json').read_text())
assert s['classification']=='DEVELOPMENT_SCREEN_NO_GO' and s['primary_scored'] is False
assert s['reserved_primary_seeds']==[9001,9011,9023] and s['total_independent_audit_checks']==50938
for name,item in s['source_and_evidence_custody'].items():
    data=(P/name).read_bytes()
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],name
with tarfile.open(P/'source.tar.bz2') as t:
    for n in ('experiment.py','audit.py'):
        assert t.extractfile(n).read()==(P/n).read_bytes()
for label in ('smoke','smoke2'):
    source=json.loads((P/(label+'.json')).read_text())
    packed=bz2.decompress((P/(label+'.json.bz2')).read_bytes())
    assert packed==(P/(label+'.json')).read_bytes()
    assert source['mode'].startswith('smoke') and len(source['cases'])==6
    a=json.loads((P/(label+'_audit.json')).read_text())
    assert a['status']=='PASS' and a['checks']==25469
    assert bz2.decompress((P/(label+'_audit.json.bz2')).read_bytes())==(P/(label+'_audit.json')).read_bytes()
assert s['scientific_pass'] is False and s['native_yggdrasil_training'] is False
print('ENERGY47_SCREEN_ARCHIVE_PASS: 12 worlds, 50938 independently audited checks; primary NOT RUN')
