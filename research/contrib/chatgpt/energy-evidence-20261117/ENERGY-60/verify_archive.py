#!/usr/bin/env python3
"""ENERGY-60 read-only exact-evidence integrity, source and frozen-gate checker."""
import hashlib,io,json,tarfile
from pathlib import Path

P=Path(__file__).resolve().parent
H=lambda data:hashlib.sha256(data).hexdigest()
manifest=json.loads((P/'archive_manifest.json').read_text())
for name,expected in manifest['files'].items():
 data=(P/name).read_bytes();assert H(data)==expected,(name,'bad sha')
parts=manifest['parts']
raw=b''.join(((P/name).read_bytes() for name in parts))
assert len(raw)==manifest['archive_bytes'] and H(raw)==manifest['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:bz2') as tf:
 assert sorted(tf.getnames())==sorted(manifest['archive_members'])
 for member in tf.getmembers():
  contents=tf.extractfile(member).read()
  assert H(contents)==manifest['archive_member_sha256'][member.name],member.name
  if (P/member.name).exists(): assert (P/member.name).read_bytes()==contents,member.name
score=json.loads((P/'result.json').read_text());prereg=json.loads((P/'prereg.json').read_text())
assert score['classification']=='SCREEN_NO_GO' and score['primary_scored'] is False
assert score['seeds']==prereg['design']['screen_seeds'] and score['reserved_primary_seeds']==prereg['design']['primary_seeds_reserved_unconsumed']
assert score['worlds']==24 and score['gates_total']==10 and score['gates_passed']==4
assert score['auditor']['status']=='PASS' and score['auditor']['checks']==286552
assert score['replay']['status']=='PASS'
assert prereg['source_commit']=='dff08e665d4851128e9e5bb0846dc1179ca196d1'
assert H((P/'source.tar.bz2').read_bytes())==prereg['source_archive_sha256']
with tarfile.open(P/'source.tar.bz2',mode='r:bz2') as t:
 assert H(t.extractfile('experiment.py').read())==prereg['scorer_sha256']
 assert H(t.extractfile('audit.py').read())==prereg['auditor_sha256']
metrics=score['pooled_mse'];a=score['by_phase_mse'];by=score['by_seed_mse'];families=score['by_family_mse']
exercised=score['temporal_prior_exercised_fraction']
expected={
'pooled_gain5_vs_softmax':metrics['state_filter']<=.95*metrics['softmax_memory'],
'pooled_gain5_vs_prototype':metrics['state_filter']<=.95*metrics['prototype_softmax'],
'cold_C_gain5_vs_softmax':a['state_filter']['C']<=.95*a['softmax_memory']['C'],
'both_seed_positive_vs_softmax':all(v['state_filter']<v['softmax_memory'] for v in by.values()),
'all_families_noninferior_10pct':all(v['state_filter']<=1.10*v['softmax_memory'] for v in families.values()),
'historical_A_noninferior_5pct':a['state_filter']['A']<=1.05*a['softmax_memory']['A'],
'negative_shuffled_20pct':metrics['state_filter']<=.80*metrics['shuffled_probes'],
'last_snapshot_gain20pct':metrics['state_filter']<=.80*metrics['last_snapshot'],
'temporal_prior_exercised':exercised>=.10,
'independent_audit':True
}
assert set(expected)==set(prereg['frozen_screen_gates'])==set(score['gates'])
for name,value in expected.items(): assert score['gates'][name]['pass'] is bool(value),name
print(json.dumps({'status':'PASS','archive_parts':len(parts),'archive_bytes':len(raw),'archive_members':len(manifest['archive_members']),
                  'worlds':score['worlds'],'gates_passed':score['gates_passed'],'audit_checks':score['auditor']['checks'],
                  'source_commit':prereg['source_commit'],'prereg_commit':score['prereg_commit']},sort_keys=True))
