#!/usr/bin/env python3
"""ENERGY-SELECT-14: post-score CSV arithmetic audit; NEVER regenerate primary worlds."""
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

POL = {'tournament':'t', 'bayesian_information_gain':'ig', 'round_robin':'rr', 'random':'rand'}
FAM = ('NULL', 'SINGLE_REWIRE', 'OUT_FAMILY_DOUBLE')
SEEDS = (97711, 97717, 97729, 97731, 97747, 97753, 97767, 97773, 97783, 97789, 97807, 97813)

def audit(csv_path, original_path=None):
    raw = Path(csv_path).read_bytes()
    rows = list(csv.DictReader(raw.decode('ascii').splitlines()))
    assert len(rows)==36, 'must contain exactly 36 original world summaries'
    assert set((int(r['seed']),r['scenario']) for r in rows) == set((seed, scenario) for seed in SEEDS for scenario in FAM)
    summary = {}
    for p, prefix in POL.items():
        vals, detection, changed = [], 0, 0
        fam = defaultdict(list)
        n_false_null = 0
        for row in rows:
            x = float(row[prefix+'_brier'])
            assert math.isfinite(x) and 0 <= x <= 2
            vals.append(x)
            fam[row['scenario']].append(x)
            c = int(row['changed'])
            tp = int(row[prefix+'_detect'])
            fp = int(row[prefix+'_false'])
            assert c == {'NULL':0,'SINGLE_REWIRE':1,'OUT_FAMILY_DOUBLE':2}[row['scenario']]
            assert 0<=tp<=c and 0<=fp<=12-c
            detection += tp
            changed += c
            if row['scenario'] == 'NULL': n_false_null += (fp>0)
        summary[p] = {'brier':statistics.fmean(vals), 'family_brier':{s:statistics.fmean(fam[s]) for s in FAM},
                      'changed_row_detection':detection/changed,'null_world_false_alert_rate':n_false_null/len(SEEDS)}
    strongest = min((summary[p]['brier'],p) for p in POL if p!='tournament')
    cand = summary['tournament']
    gain = strongest[0]-cand['brier']
    by_world = [float(r['ig_brier']) - float(r['t_brier']) for r in rows]
    se = statistics.stdev(by_world)/(len(by_world)**0.5)
    result={'schema':'yggdrasil.energy-select14-postscore-audit.v1','worlds_verified':len(rows),
            'csv_sha256':hashlib.sha256(raw).hexdigest(), 'original_primary_sha256':None,
            'scores':summary, 'strongest_conventional_control':strongest[1],
            'tournament_gain_over_strongest':gain, 'mean_paired_ig_minus_tournament':statistics.fmean(by_world),
            'exploratory_paired_95pct_normal_interval':[statistics.fmean(by_world)-1.96*se,statistics.fmean(by_world)+1.96*se],
            'test':'PASS: independent world-level arithmetic reaggregation (not independent source reexecution)',
            'science':'NEGATIVE_NO_GO' if gain < .010 or cand['changed_row_detection'] < .80 else 'UNVERIFIED',
            'source_free':True,'primary_replayed':False}
    if original_path:
        original=Path(original_path).read_bytes()
        expected=json.loads(original)
        result['original_primary_sha256']=hashlib.sha256(original).hexdigest()
        assert expected['n_worlds']==36
        for p in POL:
            for field in ('brier','changed_row_detection','null_world_false_alert_rate'):
                assert abs(summary[p][field]-expected['summary'][p][field])<1e-12, (p,field)
            for fam_name in FAM:
                assert abs(summary[p]['family_brier'][fam_name]-expected['summary'][p]['family_brier'][fam_name])<1e-12
        assert abs(gain-expected['candidate_gain'])<1e-12
        result['original_arithmetic_matched']=True
    return result

if __name__=='__main__':
    result=audit(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
    print(json.dumps(result,sort_keys=True,indent=2))
