"""Independent, report-only auditor for NCI-NOVEL-03 sealed source-free results.
Does not import the evaluator, learner, or train/score any worlds.
"""
import argparse
import json
from pathlib import Path

SEEDS=(693101,693131,693157,693181)
FAMILIES=('novel_toggle','novel_guard','novel_parity4',
          'outside_rank2','outside_mux','outside_entangle',
          'unchanged','unidentifiable_x3')
OOD={'outside_rank2','outside_mux','outside_entangle'}
PHASE_EPISODES=64+512+128+128+64


def mean(items):
    return sum(items)/len(items)


def verify(report):
    assert report['schema']=='nci-novel03.source-free-research-result.v1'
    assert report['source_mode']=='SELF_AUTHORED_SYNTHETIC_DEV'
    assert report['owner_canonical_model_accessed'] is False
    assert report['seeds']==list(SEEDS) and report['families']==list(FAMILIES)
    worlds=report['worlds']
    assert len(worlds)==32
    assert {(w['seed'],w['family']) for w in worlds}=={(s,f) for s in SEEDS for f in FAMILIES}
    for w in worlds:
        assert w['source_actions']==2*PHASE_EPISODES
        assert w['source_episodes']==PHASE_EPISODES
        assert w['new_training_actions']==1024
        assert w['calibration_evidence_only_actions']==256
        assert w['cold_old_unchanged'] is True
        assert len(w['old_parent_sha256'])==64
        assert len(w['source_witness_root'])==64
        assert len(w['research_new_fit_sha256'])==64
        assert sum(w['public_x3_counts'])==512
        if w['alarm']:
            assert w['relation_identity']=='UNKNOWN_OUTSIDE_GRAMMAR'
        elif w['public_x3_counts'][1]==0:
            assert w['relation_identity']=='UNKNOWN_NONIDENTIFIABLE_X3'
        else:
            assert w['relation_identity'] in ('PUBLIC_FACTOR_SUPPORTED_WITHIN_GRAMMAR_NOT_CERTIFIED','UNKNOWN_OR_IRRELEVANT_X3')
        assert w['alarm']==(w['logloss_full_advantage']>=.08 and w['brier_full_advantage']>=.025)
        for k in ('BMA','FULL','BACKOFF'):
            assert 0<=w['held'][k]<=1
            for metric in ('brier','logloss'):
                assert 0<=w['calibration'][k][metric]<=10
        assert w['held']['CRITIC']==w['held']['FULL' if w['alarm'] else 'BMA']
    ood=[w for w in worlds if w['family'] in OOD]
    known=[w for w in worlds if w['family'] not in OOD]
    summary=report['summary']
    assert len(ood)==12 and len(known)==20
    assert summary['worlds']==32 and summary['ood_worlds']==12 and summary['known_worlds']==20
    assert summary['source_free_actions_per_arm']==32*2*PHASE_EPISODES
    assert summary['true_ood_alarms']==sum(w['alarm'] for w in ood)
    assert summary['false_ood_alarms']==sum(w['alarm'] for w in known)
    assert summary['old_parent_sha_stable']
    assert summary['alarm_gate_pass']==(summary['true_ood_alarms']>=10 and summary['false_ood_alarms']==0)
    metrics={kind:mean([w['held'][kind] for w in ood]) for kind in ('CRITIC','BMA','FULL','BACKOFF')}
    for k,x in metrics.items():assert abs(summary['ood_held_brier'][k]-x)<1e-12
    assert summary['forecast_gate_pass']==(metrics['CRITIC']<=min(metrics['BMA'],metrics['FULL'])+.015)
    assert summary['science_status']=='SOURCE_FREE_DEV_ONLY_NO_INDEPENDENT_SCIENTIFIC_PASS'
    assert summary['deployment'] is False
    return {'classification':'REPORT_ONLY_AUDIT_PASS',
            'worlds':32,'source_free_actual_action_reveals':32*2*PHASE_EPISODES,
            'out_of_class_alarms':summary['true_ood_alarms'],
            'in_class_false_alarms':summary['false_ood_alarms'],
            'held_brier':metrics,'owner_training':False,
            'no_new_scored_experiment':True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--result',required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(json.loads(args.result.read_text('utf-8'))),sort_keys=True,indent=2))


if __name__=='__main__':main()
