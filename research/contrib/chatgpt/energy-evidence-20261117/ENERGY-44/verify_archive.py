#!/usr/bin/env python3
"""ENERGY44 original archive integrity; read-only, no primary execution."""
from pathlib import Path
import hashlib,bz2,csv,json,math
P=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x).hexdigest()
EXPECTED={
 'experiment.py.bz2':('82159c625e2cb272587e5e51dab22a7025840b47978091054b0fe9efbe32e96f','6882e7e4f202de660b90b9a0d08d20eb4ccfe67a8d143105a6c7390d5ea8ba30'),
 'audit.py.bz2':('7a2e16c6285ce53a0da16753d31b1872243c2e15c2f651f1dbd1381990803a00','64743cf9ab2ec23475519ce12ec1cd566f09c4ee00fc5a9e1108871486f9ad90'),
 'scored.json.bz2':('722896e5ed4bcaffa7e5730c1fe9ae7d0b84f9f8e894d7816ee5a95faf7bb7de','9661b101fb9289de14c0a41184cbdd19e7b81c8a1f1fe5c6f8fe75d29e935e74'),
 'audit_result.json.bz2':('e7b763118e265e40bdb9d75f46ebdfd4ed2158f287707ba7b8eded0d09773da7','b3d00c31d7eda929a54326b3f87b21bdf0432625fab8b2bfd866af669fb2018e')}
for name,(packed,raw) in EXPECTED.items():
 b=(P/name).read_bytes()
 assert sha(b)==packed,('pack hash',name)
 assert sha(bz2.decompress(b))==raw,('unpacked hash',name)
scored=json.loads(bz2.decompress((P/'scored.json.bz2').read_bytes()))
aud=json.loads(bz2.decompress((P/'audit_result.json.bz2').read_bytes()))
summary=json.loads((P/'result.json').read_text())
assert scored['schema']=='energy44.primary.v1' and scored['mode']=='primary'
assert scored['seeds']==[8713,8731,8741] and len(scored['cases'])==36
assert scored['aggregate']==summary['scores']
assert scored['decision']['gates']==summary['frozen_gates'] and scored['decision']['classification']==summary['class']=='DEVELOPMENT_NO_GO'
assert aud['status']=='PASS' and aud['checked']==138666 and aud['worlds']==36
assert aud['errors']==[] and aud['all_ten_arms_refit'] and aud['all_held_predictions_compared']
raw=(P/'case_receipts.csv').read_bytes()
assert len(raw)==6013 and sha(raw)=='8531518844d4874bf882636a7435582c7e24c426253390eb92521121b078314e'
rows=list(csv.DictReader(raw.decode().splitlines()))
assert len(rows)==36
mapping=[('selective_old','selective_repair','old_held'),('selective_new','selective_repair','new_held'),('selective_cold','selective_repair','cold_held'),('omp_delta_cold','omp_delta2','cold_held'),('omp_structural_old','omp_structural_memory','old_held'),('omp_structural_cold','omp_structural_memory','cold_held'),('elasticnet_cold','elasticnet','cold_held'),('no_repair_cold','no_repair','cold_held'),('shuffled_delta_cold','shuffled_delta','cold_held')]
for row,c in zip(rows,scored['cases']):
 assert int(row['seed'])==c['seed'] and int(row['world'])==c['world'] and row['family']==c['family']
 assert [int(x) for x in row['true_support'].split('|')]==c['truth']
 assert [int(x) for x in row['old_support'].split('|')]==c['scores']['selective_repair']['old_terms']
 assert [int(x) for x in row['delta_support'].split('|')]==c['scores']['selective_repair']['repair_terms']
 for col,arm,env in mapping:
  assert abs(float(row[col])-c['scores'][arm][env])<5.1e-10,(c['seed'],col)
assert summary['passed']==4 and summary['failed']==4 and summary['native_model_trained'] is False
print('ENERGY44_ARCHIVE_PASS: immutable primary, all 36 cases, ten-model aggregates, independent audit, negative classification; native qualification not run')
