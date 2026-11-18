#!/usr/bin/env python3
"""ENERGY-39 byte-exact original primary and per-case audit, read-only."""
from pathlib import Path
import bz2,csv,hashlib,json
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
archives={
'experiment.py.bz2':('933cfaf724d88c09b9d72e5773347d2399896d218c99192049e87f143198757a','7e95b250d63911d4b47c55ab62d67ed2acd06509fd2571095e9c91568e0bf1d8'),
'audit.py.bz2':('a4d21a367ef0dad897d0c42364e42fb88c67a6f4a9ac98d4d131a970b57a9da7','61e66de9e444af7c991cb3800b20657e732b064aef35038e58689fc224cd03ec'),
'scored.json.bz2':('b3a1429f63ef8a10ffd78d6fe537693f5b904aeab037d2832e953255cf65d704','a49f7a7b5d2fa2a25336b2e8a02c66080d34e260ef2b7e9fffcda72dceec4aa5')
}
for name,(packed,original) in archives.items():
    b=(P/name).read_bytes()
    assert H(b)==packed,('compressed hash mismatch',name)
    assert H(bz2.decompress(b))==original,('decompressed hash mismatch',name)
raw=bz2.decompress((P/'scored.json.bz2').read_bytes())
assert len(raw)==151913
primary=json.loads(raw)
summary=json.loads((P/'result.json').read_text())
aud=json.loads((P/'audit_receipt.json').read_text())
assert primary['mode']=='primary' and primary['schema']=='yggdrasil.energy39.result.v1'
assert len(primary['cases'])==36 and primary['seeds']==[8209,8221,8231]
assert primary['summary']['classification']==summary['status']=='DEVELOPMENT_NO_GO'
assert primary['summary']['gates']==summary['gates']==aud['gates']
assert primary['summary']['optimal_count']==summary['exact_optimal_count']
assert summary['highs_exact_certified']==36 and aud['checks']==623
assert primary['scientific_pass'] is False and primary['native_checkpoint_run'] is False and primary['deployment']=='NONE'
csv_b=(P/'case_receipts.csv').read_bytes()
assert len(csv_b)==7033 and H(csv_b)=='9b377d86b833311687495a1850379fd46e64d691896209813c888e8cadc83653'
records=list(csv.DictReader(csv_b.decode().splitlines()))
assert len(records)==36
for world,row in zip(primary['cases'],records):
    for key in ('seed','family','n','world'):
        assert str(world[key])==row[key],('case ID',key)
    assert int(row['optimum'])==world['exact_optimum']
    assert H(json.dumps(world['edges'],separators=(',',':')).encode())==row['graph_sha256']
    for key in ('anneal','greedy','random','highs'):
        assert int(row[key])==world['costs'][key],('solver score',key)
    assert bool(int(row['highs_certified']))==world['highs_certificate']['certified']
    for key in ('generation','anneal','greedy','random','highs','enumerate'):
        assert row[key+'_seconds']==f"{world['seconds'][key]:.12f}"
print('ENERGY39_ARCHIVE_PASS: 36 original exact graph+score+timing receipts, source/audit hashes intact; native Yggdrasil acceptance not run')
