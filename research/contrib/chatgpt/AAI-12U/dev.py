"""AAI-12U frozen source-only evaluation. Learners cannot import source generator."""
from __future__ import annotations
import argparse
import hashlib
import json
import time
import learners
import source_world as hidden


def score():
    assert len(hidden.GROUPS)==8 and len(hidden.FIXTURES)==2
    totals={arm:{group:[] for group in ('reuse','changed','familiar')} for arm in learners.ARMS}
    time_used={arm:0. for arm in learners.ARMS}
    source_digest=[];predictions=[]; cold=0; accepted={'reuse':0,'changed':0,'familiar':0}
    for fixture in hidden.FIXTURES:
        for idx,record in enumerate(hidden.GROUPS):
            group=record[0]
            donor=hidden.source_rows(fixture,idx,'donor')
            interference=hidden.source_rows(fixture,idx,'interference')
            receiver=hidden.source_rows(fixture,idx,'recipient')
            heldout=hidden.withheld(fixture,idx)
            assert len(heldout)==60
            assert not set(tuple(r['x']) for r in receiver)&set(x for x,y in heldout)
            source_digest.append([fixture,idx,[[r['x'],r['y']] for r in (*donor,*interference,*receiver)]])
            for arm in learners.ARMS:
                tic=time.perf_counter()
                m=learners.Memory(arm,donor,interference,receiver)
                snapshot=m.checkpoint()
                m=learners.Memory.restore(snapshot)
                guess=[m.prediction(x) for x,y in heldout]
                time_used[arm]+=time.perf_counter()-tic
                cold+=1
                totals[arm][group].extend(int(p==y) for p,(_,y) in zip(guess,heldout))
                if arm=='uncertainty_gated' and m.selected is not None:accepted[group]+=1
                predictions.append([fixture,idx,arm,m.selected,guess])
    scores={arm:{k:round(sum(v)/len(v),9) for k,v in groups.items()} for arm,groups in totals.items()}
    for arm in learners.ARMS:
        scores[arm]['all']=round(sum(map(sum,totals[arm].values()))/960,9)
    cand=scores['uncertainty_gated']; comparator=max((scores[a]['all'] for a in learners.ARMS if a!='uncertainty_gated'))
    local=scores['local_only_beta'];times=min(time_used[a] for a in learners.ARMS if a!='uncertainty_gated')
    checks={
      'overall_gain_vs_strongest_nonoracle_0_02':cand['all']>=comparator+.02-1e-10,
      'reuse_gain_vs_local_0_15':cand['reuse']>=local['reuse']+.15-1e-10,
      'reuse_accuracy_min_0_85':cand['reuse']>=.85-1e-10,
      'changed_nondegradation_0_03':cand['changed']>=local['changed']-.03-1e-10,
      'familiar_nondegradation_0_03':cand['familiar']>=local['familiar']-.03-1e-10,
      'reuse_detected_6_of_8':accepted['reuse']>=6,
      'false_accept_changed_at_most_one':accepted['changed']<=1,
      'all_process_wall_ratio_at_most_10':time_used['uncertainty_gated']<=10*times,
    }
    return {'schema':'yggdrasil.aai12u.source-development.v1',
      'classification':'DEV_ADMITTED_SCIENCE_UNVERIFIED' if all(checks.values()) else 'DEV_NO_GO_NO_SCIENCE',
      'scores':scores,'frozen_checks':checks,'selected_prior_slot_by_class':accepted,
      'whole_source_model_seconds':{k:round(v,6) for k,v in time_used.items()},
      'source_public_sha256':hashlib.sha256(json.dumps(source_digest,separators=(',',':')).encode()).hexdigest(),
      'cold_checkpoint_count':cold,
      'prediction_trace_sha256':hashlib.sha256(json.dumps(predictions,separators=(',',':')).encode()).hexdigest(),
      'counts':{'all_per_arm':960,'reuse':480,'changed':240,'familiar':240},
      'scientific_cohorts_consumed':0,'native_model_modified':False,'source_only':True}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-dev',action='store_true');p.add_argument('--primary',action='store_true')
    args=p.parse_args()
    if args.primary:p.error('AAI12U SCIENTIFIC FIRST USE DISARMED')
    if not args.source_dev:p.error('source-only mechanical mode --source-dev required')
    print('AAI12U_DEV='+json.dumps(score(),sort_keys=True),flush=True)

if __name__=='__main__':main()
