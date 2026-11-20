"""Offline custody verifier for original ENERGY-66 evidence. Run beside split archive."""
import hashlib,io,json,tarfile
from pathlib import Path
p=Path(__file__).parent
h=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((p/'archive_manifest.json').read_text())
parts=[]
for item in m['parts']:
 b=(p/item['name']).read_bytes()
 assert len(b)==item['bytes'] and h(b)==item['sha256'],item['name']
 parts.append(b)
original=b''.join(parts)
assert len(original)==m['archive_size'] and h(original)==m['archive_sha256']
assert h((p/'source.tar.bz2').read_bytes())==m['source_sha256']
with tarfile.open(fileobj=io.BytesIO(original),mode='r:bz2') as t:
 assert set(t.getnames())==set(m['contained_files'])
 for name,digest in m['contained_files'].items():
  data=t.extractfile(name).read();assert h(data)==digest,name
 obj=json.loads(t.extractfile('screen_scored.json').read())
 replay=json.loads(t.extractfile('screen_replay.json').read())
 obj.pop('runtime_seconds');replay.pop('runtime_seconds');assert obj==replay
 semantic=h(json.dumps(obj,sort_keys=True,separators=(',',':')).encode())
 assert semantic==json.loads((p/'replay_receipt.json').read_text())['semantic_sha256']
 assert len(obj['cases'])==24 and obj['aggregate']['classification']=='SCREEN_NO_GO'
 assert json.loads(t.extractfile('screen_audit.json').read())['checks']==42366
print('PASS ENERGY-66 archive parts',len(parts),'checks',42366,'worlds',24,'archive_sha256',m['archive_sha256'])
