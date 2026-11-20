#!/usr/bin/env python3
"""Verify ENERGY-62 original evidence byte identities without changing files."""
import json,hashlib,tarfile
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x).hexdigest()
m=json.loads((p/'archive_manifest.json').read_text())
assert m['schema']=='yggdrasil.energy62.archive-manifest.v1'
for n,expected in m['files'].items():
 if n=='EVIDENCE.tar.bz2' and not (p/n).exists():
  blob=b''.join((p/name).read_bytes() for name in sorted(m['evidence_parts']))
 else:blob=(p/n).read_bytes()
 assert sha(blob)==expected,('file_sha256',n)
for n,expected in m.get('evidence_parts',{}).items():
 assert sha((p/n).read_bytes())==expected,('evidence_part',n)
from io import BytesIO
blob=b''.join((p/name).read_bytes() for name in sorted(m['evidence_parts']))
with tarfile.open(fileobj=BytesIO(blob),mode='r:bz2') as f:
 for n,expected in m['source_originals'].items():
  item=f.extractfile(n);assert item is not None
  assert sha(item.read())==expected,('evidence_content',n)
 d={n:json.loads(f.extractfile(n).read()) for n in ('scored.json','replay.json','audit.json','replay_audit.json')}
a=d['scored.json'];b=d['replay.json'];a.pop('elapsed_s');b.pop('elapsed_s')
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
assert canon(a)==canon(b)
r=json.loads((p/'replay_receipt.json').read_text());assert sha(canon(a))==r['semantic_sha256']
assert d['audit.json']['status']=='PASS' and d['replay_audit.json']['status']=='PASS'
assert d['audit.json']['independent_refit_checks']==m['completed_audit_checks']==50059
result=json.loads((p/'result.json').read_text())
assert result['classification']=='SCREEN_NO_GO' and result['pass']==5 and result['total']==10
assert result['primary_seeds_unrun']==[104101,104117,104129]
assert len(a['cases'])==m['candidate_worlds']==24
print(json.dumps({'result':'PASS','archive_verified':True,'worlds':24,'audit_checks':50059,'classification':'SCREEN_NO_GO'},sort_keys=True))
