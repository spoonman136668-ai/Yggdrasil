"""Verify exact ENERGY-55 external research archive; never runs native Yggdrasil."""
import argparse, hashlib, io, json, tarfile
from pathlib import Path


def sha(b):return hashlib.sha256(b).hexdigest()
def verify(root):
    root=Path(root);p=json.loads((root/'provenance.json').read_text())
    for archive_name,members in p['archives'].items():
        blob=(root/archive_name).read_bytes()
        if sha(blob)!=p['archives_sha256'][archive_name]:raise AssertionError('archive byte mismatch '+archive_name)
        with tarfile.open(fileobj=io.BytesIO(blob),mode='r:bz2') as tar:
            names=tar.getnames()
            if sorted(names)!=sorted(members):raise AssertionError('file list mismatch '+archive_name)
            for name,want in members.items():
                got=tar.extractfile(name).read()
                if sha(got)!=want:raise AssertionError('entry hash mismatch '+name)
    for name,expected in p['top_level_sha256'].items():
        if sha((root/name).read_bytes())!=expected:raise AssertionError('top file SHA mismatch '+name)
    records={}
    with tarfile.open(root/'EVIDENCE.tar.bz2','r:bz2') as tar:
        for name in ('smoke.json','smoke2.json','audit_smoke.json','audit_smoke2.json','replay_receipt.json'):
            records[name]=json.load(tar.extractfile(name))
    s1,s2=records['smoke.json'],records['smoke2.json']
    assert s1['seeds']==[99983] and s2['seeds']==[99989]
    assert s1['worlds']==12 and s2['worlds']==12
    assert records['audit_smoke.json']['status']==records['audit_smoke2.json']['status']=='PASS'
    assert records['audit_smoke.json']['checks']+records['audit_smoke2.json']['checks']==72568
    assert records['replay_receipt.json']['status']=='PASS'
    r=json.loads((root/'result.json').read_text())
    assert r['classification']=='UNPREREGISTERED' and r['primary_not_run']
    assert r['audit_checks']==72568 and r['cases']==24
    for a in r['mean_mse']:
        for k in ('old','new','cold'):
            v=(s1['pooled'][a][k]+s2['pooled'][a][k])/2
            assert abs(v-r['mean_mse'][a][k])<1e-10
    return {'status':'PASS','archives':list(p['archives']),'cases':24,'arms':10,'audit_checks':72568,'primary_consumed':False}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.');args=parser.parse_args()
    print(json.dumps(verify(args.root),sort_keys=True))
