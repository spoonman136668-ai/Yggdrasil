#!/usr/bin/env python3
"""Read-only ENERGY-38 artifact custody: no training, mutation or networking."""
from pathlib import Path
import bz2,csv,hashlib,json
HERE=Path(__file__).resolve().parent
SHA=lambda b:hashlib.sha256(b).hexdigest()
sources={
'experiment.py.bz2':('1d0df093a4f269d380c5bc25567fbc622a8235823aabba5c39b52ccb5b163794','879be3760bb28d34bacf03f7dc9603556d9adcc58b0f517cdc4c75d5a2418026'),
'audit.py.bz2':('f057fbaa2f03d38eb40a4b7fb62b74f019205ba4e862018d68589552a91c2df6','d477c790bdec0c646d86017190cd92eafdd1b95888206213f57b3e9374448e25'),
'semantic.json.bz2':('a145d2084dbed2281a8e77865990c9a57a0f05b1fe434c0f67400eb1435603f0','2000f13a214e4503f3a6d9d62fe8449d6d4591015c77c575ebf699a930155f18')
}
for name,(compressed,raw_sha) in sources.items():
    raw=(HERE/name).read_bytes()
    assert SHA(raw)==compressed,(name,'compressed hash')
    assert SHA(bz2.decompress(raw))==raw_sha,(name,'decompressed hash')
semantic=json.loads(bz2.decompress((HERE/'semantic.json.bz2').read_bytes()))
summary=json.loads((HERE/'result.json').read_text())
audit=json.loads((HERE/'audit_receipt.json').read_text())
assert semantic['schema']=='yggdrasil.energy38.semantic.v1'
assert len(semantic['cases'])==54 and semantic['seeds']==[7807,7829,7841]
assert semantic['score']==summary['score'] and semantic['gates']==summary['frozen_gates']
assert summary['classification']=='DEVELOPMENT_NO_GO' and audit['status']=='PASS'
assert sum(bool(v) for v in semantic['gates'].values())==2
csvb=(HERE/'world_receipts.csv').read_bytes()
assert len(csvb)==2446 and SHA(csvb)=='856a3d4bb5c085748058ae82e5839ceeb65d4be95fc42055d50145b1ea8a3dd8'
rows=list(csv.DictReader(csvb.decode().splitlines()))
assert len(rows)==54
for case,receipt in zip(semantic['cases'],rows):
    assert int(receipt['seed'])==case['seed'] and int(receipt['instance'])==case['instance']
    assert receipt['family']==case['family']
    assert case['policies']['onepass_energy']['arms']['energy']['causal_effect_correct']==int(receipt['onepass_effect'])
    assert case['policies']['omp_uncertainty']['arms']['energy']['causal_effect_correct']==int(receipt['best_omp_uncertainty_energy_effect'])
assert summary['native_checkpoint_run'] is False and summary['scientific_pass'] is False
print('ENERGY38_ARCHIVE_PASS: 54 source worlds and complete semantic receipts verified; native qualification not run')
