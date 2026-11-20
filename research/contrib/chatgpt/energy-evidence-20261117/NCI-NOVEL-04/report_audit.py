"""Independent post-result arithmetic/custody audit. No imports of learner, world or trial."""
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parent
SOURCE_SHA={
'learner.py':'9c89e3bc37b4ad62a135441f49581ca0021575df00d7f5ef4dc2cd4b9a28c536',
'world.py':'8bb966aa7d8dc9ba0bcdd65142048647aa9ee16e7a1abce84431322cdc3ca8b5',
'trial.py':'2597268704db1a45937dc4a49c4ffc98ddff9daade316da3406f9bddf6366e9f',
'test_contract.py':'c4f503915fab1d434b3c073b51d3e88a96043a3d200c357a614ba715a758d8b4',
}
FAMILIES=('cubic_action','cubic_coupling','paired_nonlin','switching_cubic',
          'unchanged','unidentifiable_fourth','out_of_degree_four')
SEEDS=(794011,794033,794057,794089)

def mean(v):return sum(v)/len(v)

def audit():
    for name,sha in SOURCE_SHA.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,('SOURCE_DRIFT',name)
    raw=(ROOT/'primary_result.json').read_bytes()
    doc=json.loads(raw)
    assert doc['schema']=='nci-novel04.source-free-result.v1'
    assert doc['mode']=='PRIMARY_ONCE' and doc['seeds']==list(SEEDS) and doc['families']==list(FAMILIES)
    assert doc['source_kind']=='SELF_AUTHORED_SYNTHETIC_DEV' and doc['native_accepted'] is False and doc['scientific_pass'] is False
    rows=doc['worlds']
    assert len(rows)==28
    keys=[(r['seed'],r['family']) for r in rows]
    assert len(set(keys))==28 and set(keys)=={(s,f) for s in SEEDS for f in FAMILIES}
    for r in rows:
        assert r['train_events_per_arm']==384 and r['total_actions_per_arm']==704
        assert all(r['old_stable'].values()) and all(r['cold_exact'].values())
        assert r['selected_control'] in ('BMA','FULL','BACKOFF')
        expected=min(('BMA','FULL','BACKOFF'),key=lambda k:(r['valid'][k],('BMA','FULL','BACKOFF').index(k)))
        assert r['selected_control']==expected
        assert all(0<=v<=1 for v in r['held'].values())
        assert all(0<=v<=1 for v in r['policy'].values())
        assert all(0<=v<=1 for v in r['old_return'].values())
        assert set(r['old_stable'])=={'MAP','BMA','NOX3','FULL','BACKOFF'}
    summaries=[]
    for fam in FAMILIES:
        subset=[r for r in rows if r['family']==fam]
        assert len(subset)==4
        map_brier=mean([r['held']['MAP'] for r in subset])
        control=mean([r['held'][r['selected_control']] for r in subset])
        nox3=mean([r['held']['NOX3'] for r in subset])
        map_action=mean([r['policy']['MAP'] for r in subset])
        control_action=mean([r['policy'][r['selected_control']] for r in subset])
        stored=next(x for x in doc['summary']['families'] if x['family']==fam)
        assert abs(map_brier-stored['map_brier'])<1e-13
        assert abs(control-stored['selected_brier'])<1e-13
        assert abs(nox3-stored['no_x3_brier'])<1e-13
        assert abs(map_action-stored['map_policy_reward'])<1e-13
        assert abs(control_action-stored['selected_policy_reward'])<1e-13
        assert stored['representation_10pct']==(map_brier<=.90*nox3)
        assert stored['superiority_5pct']==(map_brier<=.95*control and map_action-control_action>=.01)
        summaries.append(stored)
    assert doc['summary']['novel_representation_gates']==sum(x['representation_10pct'] for x in summaries[:4])
    assert doc['summary']['novel_superiority_gates']==sum(x['superiority_5pct'] for x in summaries[:4])
    assert doc['summary']['old_bank_stable'] and doc['summary']['cold_checkpoint_exact']
    negatives={
     'unknown_in_unidentifiable':sum(not r['candidate_evidence']['t']['identified'] and not r['candidate_evidence']['y']['identified'] for r in rows if r['family']=='unidentifiable_fourth'),
     'unknown_out_of_degree':sum(not r['candidate_evidence']['t']['identified'] and not r['candidate_evidence']['y']['identified'] for r in rows if r['family']=='out_of_degree_four'),
     'unknown_unchanged':sum(not r['candidate_evidence']['t']['identified'] and not r['candidate_evidence']['y']['identified'] for r in rows if r['family']=='unchanged')}
    assert doc['summary']['negatives']==negatives
    assert doc['summary']['total_worlds']==len(rows)
    assert doc['summary']['max_checkpoint_bytes']==max(x['max_checkpoint_bytes'] for x in rows)
    assert mean([r['held']['MAP'] for r in rows if r['family'] in FAMILIES[:4]])==doc['summary']['held_mean_map']
    assert mean([r['held'][r['selected_control']] for r in rows if r['family'] in FAMILIES[:4]])==doc['summary']['held_mean_valid_selected_control']
    return {
      'schema':'nci-novel04.independent-posthoc-report-audit.v1',
      'classification':'DEV_NO_GO_STRONG_CONTROL_TIE_AND_OUT_OF_CLASS_FALSE_ID',
      'raw_primary_sha256':hashlib.sha256(raw).hexdigest(),
      'raw_primary_bytes':len(raw),
      'worlds':len(rows),'primary_seeds':list(SEEDS),
      'source_sha256':SOURCE_SHA,
      'observed_actions_per_arm_seed':4928,
      'total_source_actions_per_arm_across_seeds':19712,
      'matched_valid_selected_control_counts':dict(Counter(r['selected_control'] for r in rows)),
      'family_results':summaries,
      'novel_representation_gates':sum(x['representation_10pct'] for x in summaries[:4]),
      'novel_scientific_superiority_gates':sum(x['superiority_5pct'] for x in summaries[:4]),
      'negative_unknown_counts':negatives,
      'all_old_digest_stable':True,'all_research_cold_byte_restore':True,
      'max_checkpoint_bytes':doc['summary']['max_checkpoint_bytes'],
      'source_kind':'SELF_AUTHORED_SYNTHETIC_DEV',
      'native_owner_restored':False,'independent_scientific_pass':False,
      'action_replay_or_model_training_performed_by_this_audit':False,
    }

if __name__=='__main__':
    result=audit()
    out=ROOT/'audit_result.json'
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('POSTHOC_REPORT_ONLY_AUDIT_PASS',result['worlds'],'worlds',result['raw_primary_sha256'])
