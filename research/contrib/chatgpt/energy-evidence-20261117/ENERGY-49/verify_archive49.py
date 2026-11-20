#!/usr/bin/env python3
import json,hashlib,bz2,csv
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((P/'result49_archive.json').read_text());p=r['provenance_files']
for name,info in p.items():
    if name in ('primary49.json','experiment.py','audit.py','analyze49.py','audit49.py'):continue
    file={'result49.json':'result49.json','audit49_result.json':'audit49_result.json','case_receipts49.csv':'case_receipts49.csv','primary49.json.bz2':'primary49.json.bz2'}.get(name)
    if not file:continue
    b=(P/file).read_bytes();assert len(b)==info['bytes'] and sha(b)==info['sha256'],file
raw=bz2.decompress((P/'primary49.json.bz2').read_bytes())
assert len(raw)==p['primary49.json']['bytes'] and sha(raw)==p['primary49.json']['sha256']
data=json.loads(raw)
assert data['mode']=='primary' and data['seeds']==[9109,9127,9137]
assert len(data['cases'])==36 and r['case_count']==36
m=json.loads((P/'result49.json').read_text());a=json.loads((P/'audit49_result.json').read_text())
assert m['classification']==r['classification']=='DEVELOPMENT_PROVISIONAL_GO'
assert m['frozen_gates']==r['frozen_gates']
assert m['critical_passed']==5 and m['supporting_passed']==4
assert a['status']=='PASS' and a['checks']==3782 and a['cases']==36
rows=list(csv.DictReader((P/'case_receipts49.csv').read_text().splitlines()))
assert len(rows)==36
for row,c in zip(rows,data['cases']):
    assert row['case']==c['case'] and row['truth_sha256']==c['truth_sha256']
    assert row['pool_x_sha256']==c['pool_x_sha256']
    assert [int(x) for x in row['selected_diverse'].split('|')]==c['selected']['diverse']
    assert [int(x) for x in row['selected_random'].split('|')]==c['selected']['random']
    for source_name,header in [('diverse','diverse_cold_mse'),('random','random_cold_mse'),('contradiction_dense','dense_cold_mse'),('committee','committee_cold_mse')]:
        assert float(row[header])==c['arms'][source_name+':elasticnet']['mse_cold']
assert r['scientific_pass'] is False and r['native_model_training'] is False
print('ENERGY49_ARCHIVE_PASS: 36 full original primary worlds, hashes, audit, frozen gates, per-world receipts; no native qualification')
