#!/usr/bin/env python3
"""ENERGY-61 original-evidence byte custody verifier (does not train any model)."""
import bz2,hashlib,io,json,sys,tarfile
from pathlib import Path

root=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((root/'archive_manifest.json').read_text())
source=json.loads((root/'source_manifest.json').read_text())
scored=json.loads((root/'result.json').read_text())
provenance=json.loads((root/'provenance.json').read_text())
assert manifest['schema']=='yggdrasil.energy61.archive_manifest.v1'
assert scored['classification']=='SCREEN_NO_GO'
assert scored['gates_passed']==6 and scored['gates_total']==10 and len(scored['gates'])==10
assert scored['reserved_primary_unrun']==[103401,103419,103433]
assert provenance['source_commit']=='378a5445b59fbc46290c91f12c930ea2b1858555'
assert provenance['prereg_commit']=='83111478f22479062b1758a763e59885d567cc7c'
assert source['files']['source.tar.bz2']['sha256']==sha((root/'source.tar.bz2').read_bytes())
blob=b''.join((root/p['filename']).read_bytes() for p in manifest['parts'])
assert len(blob)==manifest['archive_bytes'] and sha(blob)==manifest['archive_sha256']
for part in manifest['parts']:
    b=(root/part['filename']).read_bytes()
    assert len(b)==part['bytes'] and sha(b)==part['sha256']
with tarfile.open(fileobj=io.BytesIO(bz2.decompress(blob)),mode='r:') as tf:
    found={f.name:tf.extractfile(f).read() for f in tf.getmembers()}
assert set(found)==set(manifest['originals'])
for name,entry in manifest['originals'].items():
    assert len(found[name])==entry['bytes'] and sha(found[name])==entry['sha256'],name
    if (root/name).exists(): assert (root/name).read_bytes()==found[name],name
primary=json.loads(found['screen_primary.json'])
audit=json.loads(found['screen_audit.json'])
replay=json.loads(found['replay.json'])
rep_audit=json.loads(found['replay_audit.json'])
assert primary['seeds']==[103301,103319] and primary['world_ids']==[0,1]
assert primary['n_worlds']==12 and len(primary['cases'])==12
assert audit['status']==rep_audit['status']=='PASS' and audit['checks']==rep_audit['checks']==86313
assert len(primary['arms'])==11 and primary['bank_features']==12012
assert primary['summary']['mean_mse']==scored['mean_mse']
assert set(c['seed'] for c in primary['cases'])=={103301,103319}
for case in primary['cases']:
    assert len(set(case['data']['ids']))==352
    assert case['data']['predictions']['program_memory']['old']==case['data']['predictions']['old_no_update']['old']
    assert set(case['data']['predictions'])==set(primary['arms'])
receipt=json.loads(found['replay_receipt.json'])
def canon(x):
    x=json.loads(json.dumps(x));x.pop('elapsed_seconds',None)
    for case in x['cases']:case.pop('run_cost_seconds',None)
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
assert canon(primary)==canon(replay)
assert sha(canon(primary))==receipt['canonical_semantic_sha256']
assert sha(found['screen_primary.json'])==receipt['primary_sha256']
print(json.dumps({'status':'PASS','source_sha256':source['files']['source.tar.bz2']['sha256'],'archive_sha256':sha(blob),'archive_bytes':len(blob),'parts':len(manifest['parts']),'worlds':12,'arms':11,'independent_audit_checks':audit['checks'],'replay':'PASS','decision':scored['classification']},sort_keys=True))
