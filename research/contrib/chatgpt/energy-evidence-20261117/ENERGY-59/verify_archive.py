#!/usr/bin/env python3
"""ENERGY-59 GitHub archive verifier. Does not train or call the official Yggdrasil runtime."""
import csv,hashlib,io,json,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent
S=lambda name:hashlib.sha256((P/name).read_bytes()).hexdigest()
info=json.loads((P/'source_manifest.json').read_text());manifest=json.loads((P/'archive_manifest.json').read_text());result=json.loads((P/'result.json').read_text())
assert info['source_parent']=='99756a3550f7cdcc0f34e982bfc7750b2d15d178'
assert result['source_freeze_commit']=='7563eb7471f97a0da2bbff4d1302905c8985fa8b'
assert result['prereg_before_primary_commit']=='fa6fb59fc796a6bc3a151165f5338e5b0dc2e019'
assert result['gates_total']==10 and result['gates_passed']==6 and result['classification']=='DEVELOPMENT_NO_GO'
assert result['independent_audit_status']=='PASS' and result['independent_audit_checks']==369674
assert result['fresh_process_restore']['status']=='PASS' and result['fresh_process_restore']['predictions_checked']==6912
assert result['deterministic_semantic_replay']['status']=='PASS'
for f,meta in info['files'].items():assert S(f)==meta['sha256'] and (P/f).stat().st_size==meta['bytes'],('source',f)
assert S('EVIDENCE.tar.bz2')==manifest['evidence_tar_sha256']
assert (P/'EVIDENCE.tar.bz2').stat().st_size==manifest['evidence_tar_bytes']
parts=sorted(manifest['parts'])
assert b''.join((P/n).read_bytes() for n in parts)==(P/'EVIDENCE.tar.bz2').read_bytes()
for n,meta in manifest['parts'].items():assert S(n)==meta['sha256'] and (P/n).stat().st_size==meta['bytes'],('part',n)
with tarfile.open(P/'EVIDENCE.tar.bz2','r:bz2') as t:
 assert set(t.getnames())==set(manifest['members'])
 for n,meta in manifest['members'].items():
  content=t.extractfile(n).read()
  assert len(content)==meta['bytes'] and hashlib.sha256(content).hexdigest()==meta['sha256']
  assert content==(P/n).read_bytes()
with (P/'case_receipts.csv').open() as f:
 rows=list(csv.DictReader(f))
assert len(rows)==108 and len({(r['seed'],r['world_id'],r['family'],r['phase']) for r in rows})==108
primary=json.loads((P/'primary.json').read_text());assert len(primary['cases'])==36
assert len({(c['world']['seed'],c['world']['family'],c['world']['world_id']) for c in primary['cases']})==36
assert primary['seeds']==[101101,101119,101141]
assert abs(primary['pooled']['energy_consensus']-result['pooled_mean_held_mse']['energy_consensus'])<1e-14
print(json.dumps({'status':'PASS','result':result['classification'],'worlds':36,'case_receipt_rows':len(rows),'archive_parts':len(parts),'evidence_bytes':(P/'EVIDENCE.tar.bz2').stat().st_size,'all_part_sha256':'PASS','source_sha256':'PASS','prereg_sha':'fa6fb59fc796a6bc3a151165f5338e5b0dc2e019'}))
