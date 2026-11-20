#!/usr/bin/env python3
"""Read-only ENERGY-53 archive verifier: checks exact source and frozen screening result.
Does not run primary seeds, requires only Python standard library.
"""
import hashlib, json, tarfile, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(data):return hashlib.sha256(data).hexdigest()

def load(name):return json.loads((ROOT/name).read_text())
p=load('provenance.json');result=load('result.json')
for name,expected in p['files_sha256'].items():
    got=sha((ROOT/name).read_bytes())
    assert got==expected,(name,expected,got)
assert sha((ROOT/'source.tar.bz2').read_bytes())=='bd1df60e730c72928e1b0aa1c7831f995eb1b84e43bc8bdda6269219ec941661'
with tarfile.open(ROOT/'source.tar.bz2','r:bz2') as t:
    assert sorted(t.getnames())==['audit.py','experiment.py']
    assert sha(t.extractfile('experiment.py').read())=='c1566f297a01c774d5b50b787f297cd7df31be6a4b51eb3876b603c4626f4851'
    assert sha(t.extractfile('audit.py').read())=='24f59a552448ae9a67810a7d8fdd8d181a429a40e64516fe98e0eddb70e8fb48'
with tarfile.open(ROOT/'EVIDENCE.tar.bz2','r:bz2') as t:
    names=sorted(t.getnames())
    assert names==['case_receipts.csv','replay_result.json','screen_audit.json','screen_replay.json','screen_scored.json']
    data={name:t.extractfile(name).read() for name in names}
orig=json.loads(data['screen_scored.json']);replayed=json.loads(data['screen_replay.json']);audit=json.loads(data['screen_audit.json'])
assert orig['seeds']==replayed['seeds']==[99721,99733]
assert len(orig['worlds'])==24 and len(set((w['seed'],w['family'],w['world']) for w in orig['worlds']))==24
assert audit['status']=='PASS' and audit['checks']==2399
# Semantic replay excludes non-deterministic timing measurements only.
exclude={'selection_seconds','fit_predict_seconds','wall_seconds','selection_seconds_total'}
def canonical(z):
    if isinstance(z,dict):return {k:canonical(v) for k,v in z.items() if k not in exclude}
    if isinstance(z,list):return [canonical(a) for a in z]
    return z
assert canonical(orig)==canonical(replayed)
semantic=json.dumps(canonical(orig),sort_keys=True,separators=(',',':')).encode()
assert sha(semantic)=='57c31d594f4e328dc80d8c1950873374e5de5913629786f4deaaf1b2ce67f99b'
assert result['classification']=='SCREEN_NO_GO' and result['passed']==7 and result['total_gates']==8
assert not result['frozen_screen_gates']['per_seed_positive_both']
assert result['primary_seeds_reserved_unrun']==[9511,9523,9547]
assert [s['passed'] for s in result['per_seed']]==[True,False]
assert result['audit']['checks']==2399 and result['native_training'] is False and result['scientific_pass'] is False
# Confirm aggregate exact means of each policy/learner on original per-world data.
checks=0
for policy in orig['policies']:
 for learner in orig['learners']:
    v=statistics.mean(w['policies'][policy]['learners'][learner]['cold_mse'] for w in orig['worlds'])
    assert abs(v-result['aggregate_cold_mse_by_policy_learner'][policy][learner])<1e-12
    checks+=1
print('ENERGY53_ARCHIVE_PASS',json.dumps({'evidence_members':len(names),'worlds':24,'methods':15,'aggregate_checks':checks,'audit_checks':2399,'screen':'SCREEN_NO_GO','primary_consumed':False}))
