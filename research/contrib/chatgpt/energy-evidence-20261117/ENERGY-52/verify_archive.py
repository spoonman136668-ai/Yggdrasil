#!/usr/bin/env python3
"""ENERGY-52 read-only archive integrity verifier; not a scientific regression."""
import hashlib, io, json, tarfile
from pathlib import Path
P=Path(__file__).resolve().parent
name=P/'EVIDENCE.tar.bz2'
data=name.read_bytes()
assert hashlib.sha256(data).hexdigest()=='251415f777128c0b63b7602dc5f49a0b4fc64de130ff8c3c13506bb224f8a530'
assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()=='6e7c575a931d97f6c5360fd19773b123abbf3575'
with tarfile.open(fileobj=io.BytesIO(data),mode='r:bz2') as archive:
    members=archive.getmembers()
    assert all(m.isfile() and '..' not in m.name and m.name==Path(m.name).name for m in members)
    content={m.name:archive.extractfile(m).read() for m in members}
hashes=json.loads(content['contents_sha256.json'])
assert set(content)==set(hashes)|{'contents_sha256.json'}
for file,hexdigest in hashes.items():
    assert hashlib.sha256(content[file]).hexdigest()==hexdigest,file
assert hashlib.sha256(content['experiment.py']).hexdigest()=='1e80168f86d65e2ccd250e6975ed5df414653f064812007e723109d3178348c9'
assert hashlib.sha256(content['audit.py']).hexdigest()=='1ac95760f049a04ddc745491857ced76404dea9bc45a454170214054ffe8fbe7'
result=json.loads(content['result.json'])
assert result['classification']=='SCREEN_NO_GO' and result['prospective_seed_list']==[99973,99979]
assert result['primary_seed_list_reserved_unrun']==[9419,9431,9449]
assert result['gates_total']==8 and result['gates_passed']==5
receipt=json.loads(content['prospective_screen.json'])
assert receipt['worlds']==24 and len(receipt['cases'])==24
assert {c['seed'] for c in receipt['cases']}=={99973,99979}
assert receipt['gate_acceptance']==13
assert len({(c['seed'],c['family'],c['id']) for c in receipt['cases']})==24
assert sum(c['energy_gate'] for c in receipt['cases'])==13
audit=json.loads(content['prospective_audit.json'])
assert audit['checks']==45480 and audit['status']=='PASS' and not audit['auditor_is_source_independent']
assert 'whitelist' in audit['exception']
print('ENERGY52_ARCHIVE_PASS | 24 prospective worlds | 45,480 refit checks | audit allowlist exception disclosed | primary unrun')
