#!/usr/bin/env python3
"""Read-only ENERGY-36 evidence-integrity qualifier; no scoring or mutation."""
import bz2
import hashlib
import json
from pathlib import Path
P=Path(__file__).resolve().parent
CHECK={
  'experiment.py.bz2':'5362527acc6030ad450ac8cf8e3347b3c498220ffc269e52c22b6d6e99b1a093',
  'audit.py.bz2':'29dcd9bb408350300c976f971de6d3c70a1469bbe260b7d9eab028bda4ccfa69',
  'semantic_scored.json.bz2':'3ae450399f6af280ab9ce3133d7117ddde7698caa6080db35f187cbff0638d1d',
}
EXPECTED={
  'experiment.py.bz2':'320ffbe34409b1f9eb49219f22e0f136a933e4604480e153f3a1afaf863d7b7e',
  'audit.py.bz2':'3afa76e1ff1065ac7c5db41d616c1acf674dc2376777c13f640b5fb2db5964d9',
  'semantic_scored.json.bz2':'ff591f3f9d00c5de1b9c7323de53341c1fe17ff0506ba167d3f43219f0bd5dd2',
}
def hashbytes(b):return hashlib.sha256(b).hexdigest()
for f,hashval in CHECK.items():
    original=(P/f).read_bytes()
    assert hashbytes(original)==hashval,('compressed_sha256',f)
    decoded=bz2.decompress(original)
    assert hashbytes(decoded)==EXPECTED[f],('decoded_sha256',f)
r=json.loads(bz2.decompress((P/'semantic_scored.json.bz2').read_bytes()))
summary=json.loads((P/'result.json').read_text())
audit=json.loads((P/'audit_result.json').read_text())
assert r['schema']=='yggdrasil.energy36.score.v1' and r['classification']=='DEVELOPMENT_NO_GO'
assert len(r['details'])==r['cases']==72 and r['seeds']==[7607,7621,7643]
assert r['score']==summary['scores'] and r['gates']==summary['gates']
assert r['score']==audit['scores'] and r['gates']==audit['gates']
assert summary['classification']=='DEVELOPMENT_NO_GO' and audit['status']=='PASS'
assert sum(r['gates'].values())==3
assert r['scientific_pass'] is False and r['native_checkpoint_run'] is False and r['deployment']=='NONE'
print('ENERGY36_ARCHIVE_PASS: fixed source, independent auditor and all 72 cases intact; no native acceptance')
