#!/usr/bin/env python3
"""Read-only ENERGY-42 archive receipt integrity; does not run the frozen primary."""
import bz2,csv,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
expected={
 'experiment.py.bz2':('8ed05d3bcd05fec566e3e1a60b4158c58a675ffd3d4935d619424a01f27d64dc','0d25d1fe19f7f8f091f5d9b9014eca832a80b2d5133ce93888060c3911bf455c'),
 'audit.py.bz2':('80e9529754b1387a33d55ccbcea9799976cf5dea81c9c21016b92bdd61d46565','b7868c6e36963d1d9dd1136af66a8a28332534b38daeb11afa290334b08fdeb5'),
 'case_scores.csv.bz2':('57f02c63eab7d409f59ec7d4d6ea5734e7f6a6775abb0ebed7fa8eff0ab2e0c9','493abe98fdb9ffc14de6f4a291e9b453e89d7bd521c8e1d4aabd8a3cad31b575')}
for file,(packed,rawsha) in expected.items():
 payload=(P/file).read_bytes()
 assert H(payload)==packed,('bad packed',file)
 assert H(bz2.decompress(payload))==rawsha,('bad raw',file)
rows=list(csv.DictReader(bz2.decompress((P/'case_scores.csv.bz2').read_bytes()).decode().splitlines()))
r=json.loads((P/'result.json').read_text())
assert len(rows)==48 and r['seeds']==[8501,8521,8537]
arms=('structured_energy','bayes','logistic','uniform','shuffled_energy','oracle')
for arm in arms:
 assert sum(int(row[arm]) for row in rows if row['mode']=='novel')==r['scores'][arm]['novel_correct']
 assert sum(int(row[arm]) for row in rows if row['mode']=='old')==r['scores'][arm]['old_correct']
 assert sum(int(row[arm]) for row in rows if row['mode']=='novel' and row['family']=='lattice')==r['scores'][arm]['lattice_correct']
 assert sum(int(row[arm]) for row in rows if row['mode']=='novel' and int(row['n'])==52)==r['scores'][arm]['n52_correct']
assert sum(r['gates'].values())==4 and r['classification']=='DEVELOPMENT_NO_GO'
assert r['independent_audit']['checks']==71609
assert r['scientific_pass'] is False and r['native_training'] is False
print('ENERGY42_ARCHIVE_PASS: hashes, 48 per-world 6-arm scores, frozen classification; native acceptance NOT RUN')
