"""Verify ENERGY-63 exact original evidence and semantic replay without scorer imports."""
from pathlib import Path
import hashlib, io, json, sys, tarfile

P=Path(__file__).resolve().parent
manifest=json.loads((P/'archive_manifest.json').read_text())

def h(blob):return hashlib.sha256(blob).hexdigest()

chunks=[]
for part in manifest['parts']:
    raw=(P/part['name']).read_bytes()
    assert len(raw)==part['bytes'] and h(raw)==part['sha256'],part['name']
    chunks.append(raw)
whole=b''.join(chunks)
assert len(whole)==manifest['archive_bytes']
assert h(whole)==manifest['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(whole),mode='r:bz2') as archive:
    names=archive.getnames()
    assert set(names)==set(manifest['members']),(names,manifest['members'].keys())
    records={}
    for name,expected in manifest['members'].items():
        raw=archive.extractfile(name).read()
        assert len(raw)==expected['bytes'] and h(raw)==expected['sha256'],name
        records[name]=raw
    original=json.loads(records['screen_scored.json']);replay=json.loads(records['screen_replay.json'])
    assert original['summary']['classification']=='SCREEN_NO_GO'
    assert len(original['cases'])==24
    assert json.loads(records['screen_audit.json'])['independent_checks']==116562
    assert json.loads(records['replay_audit.json'])['result']=='PASS'
    original.pop('runtime_seconds');replay.pop('runtime_seconds')
    a=json.dumps(original,sort_keys=True,separators=(',',':')).encode()
    b=json.dumps(replay,sort_keys=True,separators=(',',':')).encode()
    assert a==b
    assert h(a)==json.loads(records['replay_receipt.json'])['semantic_sha256']
    assert json.loads(records['result.json'])['primary_run'] is False
print(json.dumps({'status':'PASS','parts':len(chunks),'original_members':len(records),
    'archive_bytes':len(whole),'archive_sha256':h(whole),
    'semantic_replay_sha256':h(a),'independent_checks':116562,'worlds':len(original['cases'])},indent=2))
