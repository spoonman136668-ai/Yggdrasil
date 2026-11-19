#!/usr/bin/env python3
"""Check all byte hashes and immutable scientific receipts from ENERGY-58 archive."""
import hashlib,io,json,tarfile
from pathlib import Path
R=Path(__file__).parent
SHA=lambda data:hashlib.sha256(data).hexdigest()
m=json.loads((R/'archive_manifest.json').read_text());r=json.loads((R/'result.json').read_text());s=json.loads((R/'source_manifest.json').read_text())
parts=[]
for p in m['parts']:
    payload=(R/p['name']).read_bytes();assert len(payload)==p['bytes'] and SHA(payload)==p['sha256'],p['name'];parts.append(payload)
source=(R/'source.tar.bz2').read_bytes();assert SHA(source)==s['source_tar_sha256']==m['source_archive_sha256']
archive=b''.join(parts)
assert SHA(archive)==m['archive_sha256'] and len(archive)==m['archive_bytes']
with tarfile.open(fileobj=io.BytesIO(archive),mode='r:bz2') as obj:
    members={x.name:obj.extractfile(x).read() for x in obj.getmembers() if x.isfile()}
assert set(members)==set(m['archive_files'])
for name,spec in m['archive_files'].items():
    assert len(members[name])==spec['bytes'] and SHA(members[name])==spec['sha256'],name
score=json.loads(members['primary.json']); audit=json.loads(members['audit_result.json']);replay=json.loads(members['replay.json'])
old=json.loads(members['cold_restart_result.json']);again=json.loads(members['replay_restart.json']);
assert score['seeds']==r['seeds']==[100181,100193,100207] and len(score['cases'])==r['cases']==36
assert r['classification']=='DEVELOPMENT_NO_GO' and r['gates_passed']==9 and r['gates_total']==11
assert set(k for k,v in r['gates'].items() if not v['pass'])=={'cold_gain_5pct_vs_matched','cold_gain_5pct_vs_rehearsal'}
assert audit['status']==json.loads(members['replay_audit.json'])['status']=='PASS' and audit['checks']==r['independent_audit']['checks']==93968
assert old['status']==again['status']=='PASS' and old['readouts']==again['readouts']==9216
assert json.loads(members['replay_receipt.json'])['semantic_replay_exact']
for model,details in r['aggregate'].items():
    for phase,val in details.items():assert abs(val-score['aggregate'][model][phase])<1e-11
assert SHA((R/'case_receipts.csv').read_bytes())==m['case_receipts_sha256']
assert m['classification']==r['classification']
print(json.dumps({'status':'PASS','parts':len(parts),'original_primary_bytes':len(members['primary.json']),
                  'worlds':len(score['cases']),'methods':len(r['aggregate']),'audit_checks':audit['checks'],'fresh_processes':old['processes'],
                  'frozen_gates':r['gates_total'],'gates_passed':r['gates_passed']}))
