#!/usr/bin/env python3
"""Read-only ENERGY-40 original primary custody, 27 receipts and audit verification.
This is not a native Yggdrasil regression, production action, or re-scoring.
"""
from pathlib import Path
from hashlib import sha256, sha1
import bz2
import csv
import json

P=Path(__file__).resolve().parent
CHECKS={
 'experiment.py.bz2':('bc941f29ec35103727d8d1c3aed70942bbf087179e24b7ac7f1d5be8612ae8df','0b0f432189d0bd41008bfe3bc90a97ccc5f3a4931d512bdbd600f53c071b4f49','9e7255354ae45cd103a634dd3b3e684781ce2e97'),
 'audit.py.bz2':('f500629d84f503fed22787ae471f268fcd6ace9be6900b6a0a49475270192146','9c2d2bb0e779d2b3e70e1e6cd8aca5413b8027a1c203d93a62589c081c1ae780','aa93fc03007d865e9b6c8ed02f8faf995d1bee71'),
 'scored.json.bz2':('36a28a4538ef18a391913f42df7dab29929a59119defcda9dc60a831cb24264f','3710d5c7c2fc4f4b62eae7b4a6d62042da84060205025d79ef184ab4480ea2e1','f0cff8b5a3ae9aacd0abd71626149444d3802c42'),
 'audit_result.json.bz2':('f2b4939843a5c825893a20ccbf72d6d63daa01266d99e2720ca846ea053724f8','ab9a5aa94bc864fcea727a5bcb8943e915bab18c94e62d7ede3cad692d08eb90','a8f068abacb1c89a80abab48a6bb7c78527d2c59')
}

def git_sha(data):
    return sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()

def sha(data):
    return sha256(data).hexdigest()

for name,(packed_hash,raw_hash,blob_hash) in CHECKS.items():
    packed=(P/name).read_bytes()
    assert sha(packed)==packed_hash,(name,'packed SHA256')
    assert git_sha(packed)==blob_hash,(name,'Git object SHA')
    assert sha(bz2.decompress(packed))==raw_hash,(name,'unpacked SHA256')

original=json.loads(bz2.decompress((P/'scored.json.bz2').read_bytes()))
result=json.loads((P/'result.json').read_text())
aud=json.loads(bz2.decompress((P/'audit_result.json.bz2').read_bytes()))
replay=json.loads((P/'replay_diagnostics.json').read_text())
assert original['mode']=='primary' and original['schema']=='yggdrasil.energy40.score.v1'
assert original['seeds']==[8303,8311,8329] and len(original['cases'])==27
assert original['summary']==result['primary_summary']
assert aud['status']=='PASS' and aud['checks']==14283
assert aud['scored_sha256']==CHECKS['scored.json.bz2'][1]
assert result['classification']=='DEVELOPMENT_NO_GO' and sum(result['primary_summary']['gates'].values())==5
assert original['scientific_pass'] is False and original['native_yggdrasil_training'] is False
assert replay['primary_and_replay_same_gates'] and replay['primary_and_replay_same_development_classification']
assert all(replay['exact_heuristic_replay'].values()) and len(replay['highs_changed_cases'])==3
csvbytes=(P/'case_receipts.csv').read_bytes()
assert len(csvbytes)==23006 and sha(csvbytes)=='3984d09bcaffdff5c6c15df045a1ca4d613635643f28bca794f6e6b3456c5f6c'
assert git_sha(csvbytes)=='b03b2239642ca28e10dc22339e3138c0c3d3d432'
rows=list(csv.DictReader(csvbytes.decode().splitlines()))
assert len(rows)==len(original['cases'])
for case,row in zip(original['cases'],rows):
    for k in ('seed','family','n'):
        assert str(case[k])==row[k],('case identity',k)
    assert row['edge_sha256']==sha(json.dumps(case['edges'],sort_keys=True,separators=(',',':')).encode())
    assert int(row['best_feasible'])==case['best_observed_cost']
    assert row['certified_optimum']==('' if case['certified_optimum'] is None else str(case['certified_optimum']))
    sol=case['solvers']
    for m in ['anneal','ils','greedy','random','highs']:
        assert row[m+'_cost']==('' if sol[m]['cost'] is None else str(sol[m]['cost'])),(m,'cost')
        assert row[m+'_bits_hex']==(sol[m]['bits_hex'] or ''),(m,'assignment')
        if sol[m]['bits_hex'] is not None:
            bits=bytes.fromhex(sol[m]['bits_hex'])
            assert len(bits)==case['n'] and all(b in (0,1) for b in bits)
            cost=sum(e[3] for e in case['edges'] if (bits[e[0]]^bits[e[1]])!=e[2])
            assert cost==sol[m]['cost'],(m,'independent feasible cost')
    h=sol['highs']
    assert int(row['highs_certified'])==int(h['certified'])
    assert int(row['highs_status'])==h['status']
    if h['certified']:
        assert abs(h['cost']-h['dual_bound'])<1e-5 and h['cost']==case['best_observed_cost']
    for m in ['anneal','ils','greedy','random','highs']:
        assert abs(float(row[m+'_s'])-sol[m]['elapsed_s'])<6e-13
    assert abs(float(row['gen_s'])-case['generation_s'])<6e-13
print('ENERGY40_ARCHIVE_PASS: 27 exact-original receipt rows, 5 solver outputs each; independent local audit 14283 PASS; native acceptance UNVERIFIED')
