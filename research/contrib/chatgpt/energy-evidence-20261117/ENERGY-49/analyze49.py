#!/usr/bin/env python3
"""Prospective ENERGY-49 analysis of *separately* frozen ENERGY-48 experiment.py.
This file MUST be committed to the existing research branch together with the
prospective ENERGY-49 prereg, before scoring any of [9109,9127,9137].
Never modify thresholds or model selection based on those primary seeds.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
EXPECTED=(9109,9127,9137)
POLICIES=('diverse','random','fixed','committee','contradiction_dense','shuffled_contradiction','contradiction_energy')
BASELINES=tuple(x for x in POLICIES if x!='diverse')
CRITICAL=('cold_gain_5pct_vs_random','seed_wins_2of3_vs_random','old_loss_at_most_2pct_vs_best','compute_at_most_1_3x_random','nochange_cold_at_most_10pct_vs_random')
SUPPORTING=('cold_gain_3pct_vs_best_other','changed_cold_gain_5pct_vs_random','shuffled_negative_gain_5pct','omp7_cold_no_worse_than_random')

def summarize(result):
    assert result['schema']=='yggdrasil.energy48.v1' and result['mode']=='primary'
    assert tuple(result['seeds'])==EXPECTED and tuple(result['ids'])==(0,1,2,3)
    assert tuple(result['families'])==('parity2','parity3','mixed') and len(result['cases'])==36
    cases=result['cases']
    assert sum(c['changed'] for c in cases)==27 and sum(not c['changed'] for c in cases)==9
    assert len({c['case'] for c in cases})==36
    for c in cases:
        for pol in POLICIES:
            ix=c['selected'][pol]
            assert len(ix)==24 and len(set(ix))==24 and all(0<=i<192 for i in ix)
        assert len(c['arms'])==14
    def avg(pol,key,subset=cases,learner='elasticnet'):
        return float(np.mean([c['arms'][f'{pol}:{learner}'][key] for c in subset]))
    score={pol:{key:avg(pol,key) for key in ('mse_old','mse_new','mse_cold')} for pol in POLICIES}
    def cost(pol):return float(sum(c['selection_sec'][pol]+c['arms'][pol+':elasticnet']['fit_predict_sec'] for c in cases))
    for pol in POLICIES:
        score[pol]['selection_fit_predict_sec']=cost(pol)
        for mark,subset in [('changed',[c for c in cases if c['changed']]),('nochange',[c for c in cases if not c['changed']])]:
            score[pol][mark+'_cold']=avg(pol,'mse_cold',subset)
        score[pol]['omp7_cold']=avg(pol,'mse_cold',learner='omp7')
    cand=score['diverse'];rnd=score['random'];sham=score['shuffled_contradiction']
    best=min(BASELINES,key=lambda pol:score[pol]['mse_cold'])
    seed_detail=[]
    for seed in EXPECTED:
        sub=[c for c in cases if c['seed']==seed]
        v=avg('diverse','mse_cold',sub);r=avg('random','mse_cold',sub)
        seed_detail.append({'seed':seed,'diverse_cold':v,'random_cold':r,'diverse_better':bool(v<r)})
    gates={
        'cold_gain_5pct_vs_random':cand['mse_cold']<=.95*rnd['mse_cold'],
        'seed_wins_2of3_vs_random':sum(p['diverse_better'] for p in seed_detail)>=2,
        'old_loss_at_most_2pct_vs_best':cand['mse_old']<=1.02*min(score[p]['mse_old'] for p in BASELINES),
        'compute_at_most_1_3x_random':cand['selection_fit_predict_sec']<=1.3*rnd['selection_fit_predict_sec'],
        'nochange_cold_at_most_10pct_vs_random':cand['nochange_cold']<=1.1*rnd['nochange_cold'],
        'cold_gain_3pct_vs_best_other':cand['mse_cold']<=.97*score[best]['mse_cold'],
        'changed_cold_gain_5pct_vs_random':cand['changed_cold']<=.95*rnd['changed_cold'],
        'shuffled_negative_gain_5pct':cand['mse_cold']<=.95*sham['mse_cold'],
        'omp7_cold_no_worse_than_random':cand['omp7_cold']<=rnd['omp7_cold']
    }
    core=all(gates[k] for k in CRITICAL)
    extra=sum(gates[k] for k in SUPPORTING)
    if core and extra>=2:label='DEVELOPMENT_PROVISIONAL_GO'
    elif core:label='DEVELOPMENT_MIXED'
    else:label='DEVELOPMENT_NO_GO'
    return {'schema':'yggdrasil.energy49.primary-analysis.v1', 'classification':label,
            'primary_seed_list':list(EXPECTED),'worlds':36,'changed':27,'nochange':9,
            'candidate':'diverse:elasticnet','strongest_alternative':best+':elasticnet',
            'score':score,'per_seed':seed_detail,'frozen_gates':gates,
            'critical_passed':sum(gates[k] for k in CRITICAL),'critical_total':len(CRITICAL),
            'supporting_passed':extra,'supporting_total':len(SUPPORTING),
            'research_only':True,'native_scientific_pass':False,'native_model_training':False,
            'interpretation':'One synthetic case study; even provisional development go is not SCIENTIFIC_PASS.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('raw');p.add_argument('--out',required=True);a=p.parse_args()
    r=json.loads(Path(a.raw).read_text());out=summarize(r)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'class':out['classification'],'score':out['score'],'gates':out['frozen_gates'],'per_seed':out['per_seed']},sort_keys=True))
