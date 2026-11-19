#!/usr/bin/env python3
"""Read-only ENERGY-46 byte custody & per-case score verification."""
import bz2,csv,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
H=lambda x:hashlib.sha256(x).hexdigest()
result=json.loads((P/'result.json').read_text())
for k in ('primary_original','auditor_original'):
 rec=result[k];packed=(P/rec['path']).read_bytes();raw=bz2.decompress(packed)
 assert len(raw)==rec['bytes'] and len(packed)==rec['packed_bytes']
 assert H(raw)==rec['sha256'] and H(packed)==rec['packed_sha256']
assert H((P/'source.tar.bz2').read_bytes())=='2f3b1ac3e65340c6d3555ace51d6870f169dd72a01fa2917d2d7fd317855b8c9'
raw=bz2.decompress((P/'scored.json.bz2').read_bytes());P0=json.loads(raw)
with (P/'case_receipts.csv').open(newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==36 and len(P0['cases'])==36 and H((P/'case_receipts.csv').read_bytes())==result['case_receipts']['sha256']
for a,b in zip(P0['cases'],rows):
 assert (str(a['seed']),str(a['idx']),a['family'])==(b['seed'],b['idx'],b['family'])
 assert str(int(a['changed']))==b['changed']
 assert ';'.join(map(str,a['true_factors']))==b['true_factors']
 c=a['scores']['replay_gated']
 for x,y in [('cold_gated',c['cold_held']),('old_gated',c['old_held']),('new_gated',c['new_held']),('cold_elasticnet',a['scores']['elasticnet']['cold_held']),('old_elasticnet',a['scores']['elasticnet']['old_held']),('cold_unconditional',a['scores']['unconditional_replay']['cold_held']),('cold_hybrid',a['scores']['hybrid_validation']['cold_held']),('cold_stagewise',a['scores']['stagewise_omp4']['cold_held']),('old_stagewise',a['scores']['stagewise_omp4']['old_held']),('cold_omp_memory',a['scores']['omp_structural_memory']['cold_held'])]:
  assert float(b[x])==y,(x,a['seed'])
 assert int(b['gated'])==c['trigger'] and int(b['correct_truth'])==c['true_support_correct']
 assert int(b['drop'])==c['drop'] and int(b['add'])==c['add']
assert P0['decision']==result['decision'] and P0['aggregate']==result['aggregate']
assert sum(P0['decision']['gates'].values())==5 and result['classification']=='DEVELOPMENT_NO_GO'
assert result['independent_audit']['status']=='PASS' and result['independent_audit']['checks']==153215
assert result['canonical_semantic_replay']['status']=='PASS'
assert result['native_yggdrasil_training']==False and result['scientific_pass']==False and result['deployment']=='NONE'
print('ENERGY46_ARCHIVE_PASS: exact primary, independent audit, 36 per-world original scores and 5/9 frozen gates. Native acceptance NOT RUN')
