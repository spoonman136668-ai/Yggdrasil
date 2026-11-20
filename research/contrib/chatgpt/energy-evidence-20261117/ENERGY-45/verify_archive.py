#!/usr/bin/env python3
"""Read-only ENERGY-45 full original evidence integrity; no model training or network."""
import hashlib,bz2,csv,json
from pathlib import Path
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
assert H((P/'source.tar.br').read_bytes())=='0951c0cb804c3f4bdd1ecf910926bb0b59d59007c9615e35c5aefd0cbb7f13e7'
r=json.loads((P/'result.json').read_text());raw=(P/'scored.json.bz2').read_bytes()
assert H(raw)==r['primary_original']['packed_sha256']
original=bz2.decompress(raw)
assert len(original)==r['primary_original']['bytes'] and H(original)==r['primary_original']['sha256']
p=json.loads(original)
assert p['seeds']==[8803,8819,8831] and len(p['cases'])==36
assert p['decision']==r['decision'] and p['aggregate']==r['aggregate']
assert r['classification']=='DEVELOPMENT_NO_GO' and sum(r['decision']['gates'].values())==7
assert r['independent_audit']['status']=='PASS' and r['independent_audit']['checks']==154113
assert r['replay']['status']=='PASS' and r['replay']['canonical_sha256']=='84e55203bf407496011257ad0acdc4dedb38373f49d693ca5b3d5412bbf52236'
b=(P/'case_receipts.csv').read_bytes()
assert H(b)==r['case_receipts']['sha256']
rows=list(csv.DictReader(b.decode().splitlines()))
assert len(rows)==36
for original,receipt in zip(p['cases'],rows):
    assert str(original['seed'])==receipt['seed'] and str(original['world'])==receipt['world'] and original['family']==receipt['family']
    assert bool(original['changed'])==bool(int(receipt['changed']))
    assert original['scores']['gated_replace']['trigger']==bool(int(receipt['trigger']))
    assert original['scores']['gated_replace']['drop']==int(receipt['drop'])
    assert original['scores']['gated_replace']['add']==int(receipt['add'])
    assert original['scores']['gated_replace']['true_replacement_support']==bool(int(receipt['true_replacement']))
    for arm in r['arms']:
      for env in ('old_held','new_held','cold_held'):
        assert original['scores'][arm][env]==float(receipt[arm+'_'+env])
assert r['native_model_training'] is False and r['scientific_pass'] is False and r['deployment']=='NONE'
print('ENERGY45_ARCHIVE_PASS: full original, 36 × 11 outcome receipts and frozen 7/9 classification verified; native acceptance not run')
