"""ENERGY-65 original evidence integrity verifier; run from archive directory.
Does not rerun experiments or substitute for independent refit/audit.
"""
import hashlib,io,json,tarfile
from pathlib import Path
root=Path(__file__).parent;m=json.loads((root/'archive_manifest.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
parts=[]
for p in m['archive_split_parts']:
 data=(root/p['filename']).read_bytes();assert len(data)==p['bytes'] and sha(data)==p['sha256'],p['filename'];parts.append(data)
archive=b''.join(parts)
assert len(archive)==m['archive_bytes'] and sha(archive)==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(archive),mode='r:bz2') as tar:
 for name,h in m['evidence_members'].items():
  data=tar.extractfile(name).read();assert sha(data)==h,name
  if (root/name).exists():assert sha((root/name).read_bytes())==h,name
assert sha((root/'source.tar.bz2').read_bytes())==m['source_sha256']
res=json.loads((root/'result.json').read_text());assert res['classification']==m['classification']=='SCREEN_NO_GO'
assert res['audit']['checks']==m['auditor_checks']==42078
print('ENERGY-65 PASS',len(parts),'archive parts',len(m['evidence_members']),'original members; 24 worlds; SCREEN_NO_GO')
