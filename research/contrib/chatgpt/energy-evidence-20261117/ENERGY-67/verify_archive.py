"""Verify exact ENERGY-67 archive parts, original files and frozen source tar."""
from pathlib import Path
import hashlib,io,tarfile,json
p=Path(__file__).resolve().parent
m=json.loads((p/'archive_manifest.json').read_text());h=lambda b:hashlib.sha256(b).hexdigest()
data=b''
for part in m['parts']:
 b=(p/part['name']).read_bytes()
 assert len(b)==part['size'] and h(b)==part['sha256'],part['name']
 data+=b
assert len(data)==m['archive_size_bytes'] and h(data)==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(data),mode='r:bz2') as t:
 for name,checksum in m['original_files'].items():
  file=t.extractfile(name)
  assert file is not None,name
  assert h(file.read())==checksum,name
src=json.loads((p/'source_manifest.json').read_text())
assert h((p/'source.tar.bz2').read_bytes())==src['archive_sha256']
with tarfile.open(p/'source.tar.bz2','r:bz2') as t:
 for name,checksum in src['source_files'].items():
  assert h(t.extractfile(name).read())==checksum,name
print(json.dumps({'result':'PASS','parts':len(m['parts']),'archive_size':len(data),'original_files':len(m['original_files']),'archive_sha256':m['archive_sha256']},indent=2))
