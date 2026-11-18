#!/usr/bin/env python3
"""Read-only ENERGY-35 archive custody verifier. No scoring or ref mutation."""
from pathlib import Path
from hashlib import sha256
import bz2
import csv
import json

HERE=Path(__file__).resolve().parent
EXPECTED={
    'experiment.py':'dde9f68ea1f86e7e09b291859adffec78d33cfb6dd1197e8fdf25e92e4bdca9c',
    'audit.py':'07b4556fc91497f10da9733aacdb32e34967cfa984e47009e9196edd441f3a1e',
    'case_receipts.csv':'c6ba7aec571c1d590121cf2fe0eaf9e4a0f1079a8a5efb19b5357c956cadcfa3',
    'scored.json.bz2':'99ec8fab9f04ab8304cdc8a322e5aa212384c3f8c9fc4bdf360154de95b1dbb1',
}
SCORER_HASH='96f1bffc8117764b1bc9fdd2110107a8f212591be80f119a1fdcded7aacba435'
SEMANTIC_SHA='ae81d9d06be1ce685f370aab4ca2d6a691ac56ba92f788c21027c74a6ac3bae8'

def main():
    for name,digest in EXPECTED.items():
        data=(HERE/name).read_bytes()
        assert sha256(data).hexdigest()==digest,(name,'SHA mismatch')
    raw=bz2.decompress((HERE/'scored.json.bz2').read_bytes())
    assert len(raw)==227730
    assert sha256(raw).hexdigest()==SCORER_HASH
    source=json.loads(raw)
    assert source['schema']=='yggdrasil.energy35.score.v1' and source['mode']=='primary'
    assert len(source['details'])==144 and source['classification']=='DEVELOPMENT_NO_GO'
    assert source['seeds']==[7307,7331,7349]
    rows=list(csv.DictReader((HERE/'case_receipts.csv').open(newline='')))
    assert len(rows)==144
    for c,r in zip(source['details'],rows):
        for key in ('seed','world','family','regime','flip_relevance'):
            assert str(c[key])==r[key], (key,c[key],r[key])
        for arm,scored in c['correct'].items():
            for context,count in scored.items():
                assert count==int(r[arm+'_'+context]),(arm,context)
    summary=json.loads((HERE/'result.json').read_text())
    assert summary['classification']=='DEVELOPMENT_NO_GO'
    assert summary['primary_full_scored_json_sha256']==SCORER_HASH
    assert summary['scores']==source['scores'] and summary['gates']==source['gates']
    print(json.dumps({'archive':'PASS','case_receipts':144,'archive_bytes':len(raw),
                      'source_hash':EXPECTED['experiment.py'],'original_score_sha256':SCORER_HASH,
                      'qualification':'Archive custody and receipt consistency only; no native acceptance.'},indent=2))

if __name__=='__main__':main()
