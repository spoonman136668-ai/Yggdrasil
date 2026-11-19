#!/usr/bin/env python3
"""ENERGY-57 original custody integrity + decision receipt verifier (stdlib only)."""
from pathlib import Path
import bz2,hashlib,io,json,tarfile
P=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    m=json.loads((P/'archive_manifest.json').read_text())
    out=b''
    for part in m['parts']:
        b=(P/part['name']).read_bytes()
        assert len(b)==part['bytes'] and sha(b)==part['sha256'],('part corruption',part['name'])
        out+=b
    assert len(out)==m['evidence_archive_bytes'] and sha(out)==m['evidence_archive_sha256']
    with tarfile.open(fileobj=io.BytesIO(out),mode='r:bz2') as tf:
        names=tf.getnames(); assert set(names)==set(m['files']),(names,list(m['files']))
        content={name:tf.extractfile(name).read() for name in names}
    for name,ident in m['files'].items():
        assert len(content[name])==ident['bytes'] and sha(content[name])==ident['sha256'],name
    source_tar=content['source.tar.bz2'];assert sha(source_tar)=='9a854558df61ff23f48befe229747e49e208f7c55ee7b91c38280f2253dada41'
    with tarfile.open(fileobj=io.BytesIO(source_tar),mode='r:bz2') as tf:
        assert sha(tf.extractfile('experiment.py').read())=='d6584ea41afaaf2f86bdf5ab5d6b26f6872223ff16c7d0481a385a51b21d2b40'
        assert sha(tf.extractfile('audit.py').read())=='2650ee998ffb7938c2ab9b91aaeac319cf58458e835c08e909418925f9dbd1b5'
    result=json.loads(content['result.json']);audit=json.loads(content['screen_audit.json']);replay=json.loads(content['replay_receipt.json'])
    assert result['classification']=='SCREEN_NO_GO' and result['frozen_gates_passed']==10 and result['frozen_gates_total']==11
    assert result['critical_failed']==['cold_vs_separate_relations_3pct']
    assert result['no_primary'] and result['reserved_primary_seeds_untouched']==[100019,100043,100057]
    assert audit['status']=='PASS' and audit['error_count']==0 and audit['checks']==57779
    assert json.loads(content['screen_replay_audit.json'])['status']=='PASS'
    assert len(json.loads(content['screen.json'])['cases'])==24 and replay['status']=='PASS'
    assert len(content['case_receipts.csv'].splitlines())==25
    a=json.loads(content['screen.json']);b=json.loads(content['screen_replay.json'])
    for x in (a,b):
        x.pop('elapsed_total_seconds',None)
        for item in x['cases']:item['info'].pop('timings_control',None)
    fmt=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
    assert fmt(a)==fmt(b) and sha(fmt(a))==replay['timing_free_semantic_sha256']
    print(json.dumps({'status':'PASS','experiment':'ENERGY-57','archive_bytes':len(out),'archive_sha256':sha(out),'part_count':len(m['parts']),'source_sha_verified':True,'original_worlds':24,'auditor_checks':57779,'gate_results':'10/11 SCREEN_NO_GO','primary_seed_consumption':0},indent=2))
if __name__=='__main__':main()
