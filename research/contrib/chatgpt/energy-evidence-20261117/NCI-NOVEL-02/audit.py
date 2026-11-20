"""NCI-NOVEL-02 independent report-only audit; never imports source world or learner.

This post-result verifier is not a new primary scorer and does not consume seeds.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

SEEDS=(592113,592127,592139,592157)
FAMILIES=('novel_toggle','novel_guard','novel_cross','novel_parity4',
          'unchanged','irrelevant_x3','unidentifiable_x3','outside_grammar')
NOVELS=FAMILIES[:4]
CONTROLS=('BMA','FULL','BACKOFF','RECURRENT')


def require(condition, label):
    if not condition: raise ValueError('AUDIT_FAILED_'+label)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).parent)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=args.root
    manifest=json.loads((root/'source_manifest.json').read_text('utf-8'))
    require(manifest['primary_scored'] is False,'UNFROZEN_ORIGINAL_MANIFEST')
    require(manifest['primary_seeds_reserved_untouched']==list(SEEDS),'ORIGINAL_PRIMARY_IDS')
    source_proof={}
    for name,receipt in manifest['code_and_pilot'].items():
        b=(root/name).read_bytes()
        require(hashlib.sha256(b).hexdigest()==receipt['sha256'],'SOURCE_'+name)
        require(len(b)==receipt['bytes'],'SIZE_'+name)
        source_proof[name]=receipt['sha256']
    raw=(root/'primary_result.json').read_bytes()
    d=json.loads(raw)
    require(d['pilot'] is False and d['source_free'] is True,'SOURCE_MODE')
    require(d['native_accepted'] is False and d['scientific_pass'] is False and d['protected_source_first_use'] is False,'AUTHORITY')
    require(d['seeds']==list(SEEDS) and d['families']==list(FAMILIES),'COHORT')
    require(len(d['worlds'])==32,'WORLD_COUNT')
    require(set((x['seed'],x['family']) for x in d['worlds'])==set((s,f) for s in SEEDS for f in FAMILIES),'DUPLICATE_WORLD_OR_FAMILY')
    require(all(x['evaluation_actions_per_arm']==640 for x in d['worlds']),'ACTION_BUDGET')
    require(all(x['original_source_first_use'] is False and x['native_canonical_checkpoint'] is False for x in d['worlds']),'OWNER_SCOPE')
    require(all(x['new_episode_records_per_model']['GATED_MAP']==448 for x in d['worlds']),'ADMITTED_WITNESS_COUNT')
    require(all(x['new_episode_records_per_model']['BMA']==448 for x in d['worlds']),'CONTROL_WITNESS_COUNT')
    require(all(x['checkpoint_bytes']['GATED_MAP']<=65536 for x in d['worlds']),'CANDIDATE_CHECKPOINT_CAP')
    independent={}
    for fam in NOVELS:
        rows=[x for x in d['worlds'] if x['family']==fam]
        require(len(rows)==4,'NOVEL_WORLD_MISSING')
        cand=sum(x['held_shared_brier']['GATED_MAP'] for x in rows)/4
        nofourth=sum(x['held_shared_brier']['NO_X3'] for x in rows)/4
        strong=sum(x['held_shared_brier'][x['valid_selected_fitted_control']] for x in rows)/4
        reward=sum(x['policy_reward']['GATED_MAP'] for x in rows)/4
        control_reward=sum(x['policy_reward'][x['valid_selected_fitted_control']] for x in rows)/4
        identified=sum(x['candidate_evidence']['t']['identified'] and x['candidate_evidence']['y']['identified'] for x in rows)
        for x in rows:
            correct_control=min(CONTROLS,key=lambda c:(x['valid_brier'][c],c))
            require(x['valid_selected_fitted_control']==correct_control,'CONTROL_SELECTION_LEAK')
        independent[fam]={
            'identified_both_stages_seed_count':identified,'candidate_brier':cand,
            'no_fourth_brier':nofourth,'valid_control_brier':strong,
            'candidate_reward':reward,'valid_control_reward':control_reward,
            'representation_pass':identified>=3 and cand<=.90*nofourth,
            'superiority_pass':cand<=.95*strong and reward>control_reward,
            'relative_ablation_gain':1-cand/nofourth,
            'relative_control_gain':1-cand/strong,
        }
        original=d['aggregate']['novel_family'][fam]
        require(original['representation_pass']==independent[fam]['representation_pass'],'ORIGINAL_REP_GATE')
        require(original['superiority_pass']==independent[fam]['superiority_pass'],'ORIGINAL_SCIENCE_GATE')
        require(abs(original['candidate_brier']-cand)<1e-12,'ORIGINAL_SCORE_DRIFT')
    negatives=[x for x in d['worlds'] if x['family'] in ('unidentifiable_x3','outside_grammar')]
    unknown=sum(not(x['candidate_evidence']['t']['identified'] or x['candidate_evidence']['y']['identified']) for x in negatives)
    incorrect=[{'seed':x['seed'],'family':x['family'],
                'identified_stages':[k for k,y in x['candidate_evidence'].items() if y['identified']]}
               for x in negatives if x['candidate_evidence']['t']['identified'] or x['candidate_evidence']['y']['identified']]
    rep=sum(x['representation_pass'] for x in independent.values())
    sci=sum(x['superiority_pass'] for x in independent.values())
    require(rep==d['aggregate']['representation_families_passed'] and sci==d['aggregate']['strong_control_superiority_families_passed'],'FAMILY_AGGREGATE')
    require(unknown==d['aggregate']['negative_unknown_count'],'NEGATIVE_AGGREGATE')
    audit={'schema':'nci-novel02.independent-read-only-results-audit.v1',
           'original_report_sha256':hashlib.sha256(raw).hexdigest(),
           'original_report_bytes':len(raw),'original_source_sha256':source_proof,
           'primary_seed_ids':list(SEEDS),'worlds':len(d['worlds']),
           'families':independent,'representation_families_passed':rep,
           'scientific_superiority_families_passed':sci,
           'negative_unknown':unknown,'negative_total':len(negatives),
           'negative_false_identification_cases':incorrect,
           'max_candidate_checkpoint_bytes':max(x['checkpoint_bytes']['GATED_MAP'] for x in d['worlds']),
           'total_candidate_cpu_seconds':sum(x['cpu_seconds']['GATED_MAP'] for x in d['worlds']),
           'total_exact_bma_cpu_seconds':sum(x['cpu_seconds']['BMA'] for x in d['worlds']),
           'method':'POSTHOC_REPORT_ONLY_NO_NEW_SOURCE_GENERATION',
           'engineering':'REPORT_AND_SOURCE_CUSTODY_PASS',
           'development_representation':'PASS_4_OF_4',
           'development_science':'NO_GO_0_OF_4',
           'original_world_scientific_pass':False,
           'new_source_actions_or_trials':0,
           'native_owner_mutation':False}
    args.output.write_text(json.dumps(audit,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:audit[k] for k in ('worlds','representation_families_passed','scientific_superiority_families_passed','negative_unknown','negative_total','negative_false_identification_cases','max_candidate_checkpoint_bytes','original_report_sha256')},indent=2))

if __name__=='__main__':main()
