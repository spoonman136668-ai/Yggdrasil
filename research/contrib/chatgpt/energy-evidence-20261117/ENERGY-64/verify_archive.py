"""ENERGY-64 byte-level archive and pre-registered score integrity verifier."""
from pathlib import Path
import hashlib,tarfile,json,io
p=Path(__file__).parent
h=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((p/'archive_manifest.json').read_text())
chunks=[]
for part in m['parts']:
 b=(p/part['name']).read_bytes()
 assert len(b)==part['size'] and h(b)==part['sha256'],part['name']
 chunks.append(b)
full=b''.join(chunks)
assert len(full)==m['archive_size_bytes'] and h(full)==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(full),mode='r:bz2') as z:
 manifest=json.loads(z.extractfile('contents_sha256.json').read())
 assert len(manifest)+1==m['file_count']
 for name,digest in manifest.items():
  assert h(z.extractfile(name).read())==digest,name
 scr=json.loads(z.extractfile('screen_scored.json').read());audit=json.loads(z.extractfile('screen_audit.json').read());replay=json.loads(z.extractfile('screen_replay.json').read());reg=json.loads(z.extractfile('prereg.json').read());result=json.loads(z.extractfile('result.json').read())
 assert reg['source_commit']=='3b940e60e02171b3f1edd73034e140ecab53e393'
 assert reg['seeds']['fresh_screen']==scr['seeds']==[998331,998347]
 assert reg['seeds']['reserved_primary']==[106101,106117,106137]
 assert len(scr['cases'])==24 and audit['checks']==108401 and audit['verdict']=='PASS'
 assert result['classification']=='SCREEN_NO_GO' and scr['summary']['decision']=='SCREEN_NO_GO' and scr['summary']['pass_count']==5
 assert h(json.dumps({k:v for k,v in scr.items() if k!='elapsed_seconds'},sort_keys=True,separators=(',',':')).encode())==h(json.dumps({k:v for k,v in replay.items() if k!='elapsed_seconds'},sort_keys=True,separators=(',',':')).encode())
print(json.dumps({'verdict':'PASS','parts':len(chunks),'archive_sha256':m['archive_sha256'],'files_verified':len(manifest),'worlds':24,'auditor_checks':audit['checks'],'screen_decision':'SCREEN_NO_GO'},indent=2))
