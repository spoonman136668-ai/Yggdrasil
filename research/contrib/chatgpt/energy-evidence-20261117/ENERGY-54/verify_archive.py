#!/usr/bin/env python3
"""ENERGY-54 standalone read-only archive verifier; no native Yggdrasil writes."""
import bz2,csv,hashlib,io,json,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent
D=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((P/'result.json').read_text())
p=json.loads((P/'provenance.json').read_text())
a=(P/'EVIDENCE.tar.bz2').read_bytes();s=(P/'source.tar.bz2').read_bytes()
assert D(a)==r['evidence_archive_sha256']==p['evidence_archive_sha256']=='b22f6b81a5c9fbbb1fb6bed56f2da2f55f23135f712084ef40d70d05da841ef3'
assert D(s)==p['source_archive_sha256']=='e9bbeb9dd4fa1517b47a1f7dbf5b0b5605e02a22094cfc1a5c22163f2c86918e'
with tarfile.open(fileobj=io.BytesIO(s),mode='r:bz2') as f:
 files={x.name:f.extractfile(x).read() for x in f.getmembers()}
assert set(files)==set(p['source_file_sha256'])
for name,digest in p['source_file_sha256'].items():assert D(files[name])==digest
with tarfile.open(fileobj=io.BytesIO(a),mode='r:bz2') as f:
 originals={x.name:f.extractfile(x).read() for x in f.getmembers()}
assert set(originals)==set(r['evidence_file_sha256'])==set(p['evidence_file_sha256'])
for name,digest in r['evidence_file_sha256'].items():assert D(originals[name])==digest==p['evidence_file_sha256'][name]
scored=json.loads(originals['screen_scored.json']);audit=json.loads(originals['screen_audit.json']);replay=json.loads(originals['replay_result.json'])
assert scored['seeds']==r['screen_seeds']==[99851,99863]
assert scored['world_count']==len(scored['cases'])==24
assert audit['checks']==r['independent_audit']['checks']==2934 and audit['status']=='PASS'
assert replay['status']=='PASS' and replay['semantic_sha256']==r['replay']['semantic_sha256']
assert r['classification']=='SCREEN_NO_GO' and r['gates_passed']==sum(r['gates'].values())==2 and len(r['gates'])==9
assert r['reserved_primary_seeds_unscored']==[9719,9733,9749] and not r['primary_scored'] and not r['native_training']
expected=24*6*3
rows=list(csv.DictReader(io.StringIO(originals['case_receipts.csv'].decode())))
assert len(rows)==expected
for w in scored['cases']:
 matching=[row for row in rows if int(row['seed'])==w['seed'] and int(row['world_id'])==w['world'] and row['family']==w['family']]
 assert len(matching)==18
 for row in matching:
  a=w['arms'][row['policy']];metrics=a['learners'][row['learner']]
  assert list(map(int,row['selected_pool_ids'].split(';')))==a['indices']
  assert row['source_assignment_sha256']==w['sections_sha256']
  for key in ('old_mse','new_mse','cold_mse'):
   assert float(row[key])==metrics[key]
  assert row['cold_prediction_sha256']==metrics['cold_sha256']
  assert row['new_prediction_sha256']==metrics['new_sha256']
print('ENERGY54_ARCHIVE_PASS: source SHA, complete original screen, replay, full 432 case-arm receipts, independent audit, nine frozen gates; no native acceptance')
