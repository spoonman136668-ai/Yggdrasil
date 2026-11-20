#!/usr/bin/env python3
"""Read-only GitHub archived ENERGY-43 source/receipt/invariant verifier. No training."""
import bz2,hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
h=lambda b:hashlib.sha256(b).hexdigest()
source={'experiment.py.bz2':('c44dc6d77a57453e90da4858835f949d73713f1035abe674156f0f2df42530fe','48a798f75c1afc9701158edb4131d076dbe07f9dd3ad9374b9095ad2b47fe79f'),
'audit.py.bz2':('f6e56bcbbe55a1a00ee386ef08a9a6a7896307006eb51d62d22b3fb720abacb0','b838cf23568016d97c068c8ea0e1e818b9355ab3a28992d602d1cb4f4d775e61'),
'case_receipts.json.bz2':('d3250a6b936200e4a412a6d4d59329f82e3d3c699f2d896125e7134f99299d13','2fcac188fd971a5d06ec55c44a8153876291d2c682d7c485f3643ee512e6db99')}
for name,(packed,rawsha) in source.items():
    b=(p/name).read_bytes(); assert h(b)==packed,(name,'packed')
    assert h(bz2.decompress(b))==rawsha,(name,'raw')
r=json.loads((p/'result.json').read_text());a=json.loads((p/'audit_receipt.json').read_text())
c=json.loads(bz2.decompress((p/'case_receipts.json.bz2').read_bytes()))
assert c['source_commit']==r['source_commit'] and c['prereg_commit']==r['prereg_commit']
assert len(c['cases'])==r['worlds']==36 and r['primary_seeds']==[8617,8629,8651]
assert r['classification']=='DEVELOPMENT_NO_GO' and sum(r['gates'].values())==r['gates_passed']==3
assert a['status']=='PASS' and a['checks']==116772
assert r['native_yggdrasil_model_trained'] is False and r['scientific_pass'] is False
for method in r['arms']:
    for split in ('old_held','new_held','cold_held'):
        avg=sum(cz['test_mse_by_arm'][method][split] for cz in c['cases'])/36
        assert abs(avg-r['aggregate'][method][split])<1e-9,(method,split)
K=r['model_grammar_size']
for case in c['cases']:
    truth=set(case['truth_support_indices']);sel=set(j if j<K else j-K for j in case['energy_selected_indices'])
    assert abs(case['factor_recall']-len(truth & sel)/5)<1e-12
print('ENERGY43_ARCHIVE_PASS: 36 cases, 8 arms, exact support recall and source hashes verified; native qualification NOT RUN')
