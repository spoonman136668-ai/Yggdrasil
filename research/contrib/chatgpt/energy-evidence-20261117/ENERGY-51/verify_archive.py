#!/usr/bin/env python3
"""ENERGY-51 read-only repo archive integrity verification (standard library only)."""
from pathlib import Path
import bz2,hashlib,json,math
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
expected={
'experiment.py.bz2':('25499ac492c10bacc9392eb97588cb862e1493f1d36293440184fd2c032a51d5','76427457e5452585d07fc23b05e5a0812717d1e3d6a4ee2848cf982cde6b9c20'),
'audit.py.bz2':('1871246adadcfc4d2410adecdd132b12922c1a604a76929f721fb900b57c91ae','73e27052ac44025dbf6deb509df623008c0c3dc055ec99756d640196e2f97483'),
'scored.json.bz2':('1eff4e4cd0e429d19d1de1395522cda9480d595d3dc10cfd62aed601a4359254','acac0a6e9813b7d01436314593edec949673059165a6683b61c6e2698b3af741'),
'world_scores.json.bz2':('e4d1ff47bb87cc5a5f4c10d782fe660459f97381c1c27b5c0c3a727d91c34ad8',None)
}
for filename,(packed,raw) in expected.items():
    data=(P/filename).read_bytes()
    assert H(data)==packed,('compressed SHA mismatch',filename)
    unpacked=bz2.decompress(data)
    if raw:assert H(unpacked)==raw,('decompressed SHA mismatch',filename)
primary=json.loads(bz2.decompress((P/'scored.json.bz2').read_bytes()))
receipts=json.loads(bz2.decompress((P/'world_scores.json.bz2').read_bytes()))
result=json.loads((P/'result.json').read_text())
prereg=json.loads((P/'prereg.json').read_text())
audit=json.loads((P/'audit_result.json').read_text())
assert prereg['source_commit_sha']=='9be7cfcbcdcc740abffa272220b2ba16a83cf371'
assert result['prereg_commit']=='b2b9743778f8cbd0bddf2ba03bfe1c8469bb631e'
assert primary['seeds']==prereg['data']['primary_seeds']==[9311,9323,9341]
assert len(primary['rows'])==len(receipts['rows'])==result['worlds']==36
assert result['audit_checks']==audit['checks']==465468 and audit['status']=='PASS'
assert result['classification']==primary['classification']=='DEVELOPMENT_NO_GO'
assert result['gates']==primary['gates'] and result['gate_passed']==primary['gate_passed']==4
assert len(primary['gates'])==len(prereg['frozen_gates'])==9
assert set(primary['gates'])==set(prereg['frozen_gates'])
assert math.isclose(primary['higher_order_parity_recall'],result['higher_order_parity_recall'],abs_tol=1e-13)
assert len({(v['seed'],v['wid'],v['family']) for v in primary['rows']})==36
for a,b in zip(primary['rows'],receipts['rows']):
    assert b['i']==[a['seed'],a['wid'],a['family']]
    assert b['h']==[a['source_hash'],a['observed_train_hash']]
    for arm,v in a['models'].items():
        s=b['m'][arm]
        for i,tag in enumerate(('test_old','test_new','test_cold')):
            assert math.isclose(s[i],v['mse'][tag],abs_tol=1e-9)
    predicted=a['models']['structural_energy']
    assert b['selected']==predicted['old_supports']+predicted['correction_supports']
for arm,v in primary['aggregate'].items():
    for tag in ('test_old','test_new','test_cold'):
        values=[r['models'][arm]['mse'][tag] for r in primary['rows']]
        assert math.isclose(sum(values)/36,v['mse'][tag],abs_tol=1e-12)
print('ENERGY51_ARCHIVE_PASS: frozen source, prereg, exact full primary, world receipts, 9 gates and independent 465468-check audit')
print('NATIVE_ACCEPTANCE_NOT_RUN / SCIENTIFIC_PASS_NOT_ESTABLISHED')
