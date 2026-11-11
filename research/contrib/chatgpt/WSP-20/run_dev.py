"""WSP20 frozen protected/coherent-update mechanism falsification."""
import hashlib
import json
import platform
import sys
import time
from joint_credit import JointNand,PlasticNand,context,SEEDS,PUBLIC,ARMS,TRIALS20


def run():
    start=time.perf_counter();scores={a:{'observed_correct':0,'witness_correct':0,'old_valid_lost':0,'exact_tasks':0,'hidden_correct':0} for a in ARMS}
    ops={a:{k:0 for k in ('proposals','gate_evaluations','noise_draws','accepted','proposed_row_writes','changed_coordinates','accepted_coordinates')} for a in ARMS}
    times={a:0. for a in ARMS};initial_time=0.;initial_old=restores=replays=0;states=[]
    for seed in SEEDS:
        for sig in range(32):
            original=tuple((context(i),(sig>>j)&1) for j,i in enumerate(PUBLIC))
            tick=time.perf_counter();initial=PlasticNand().learn(original,seed);initial_time+=time.perf_counter()-tick
            initial_pred=tuple(initial.predict(context(i)) for i in range(8))
            obs=original+((context(3),1-initial_pred[3]),)
            valid=[initial_pred[i]==y for i,(_x,y) in zip(PUBLIC,original)];initial_old+=sum(valid)
            for arm in ARMS:
                tick=time.perf_counter();model=JointNand(initial.snapshot()).adapt(obs,seed,arm);times[arm]+=time.perf_counter()-tick
                pred=tuple(model.predict(context(i)) for i in range(8));r=scores[arm]
                fit=sum(pred[i]==y for i,(_x,y) in zip(PUBLIC+(3,),obs))
                r['observed_correct']+=fit;r['exact_tasks']+=fit==6;r['witness_correct']+=pred[3]==obs[-1][1]
                r['old_valid_lost']+=sum(ok and pred[i]!=y for ok,i,(_x,y) in zip(valid,PUBLIC,original))
                for assignment in range(4):r['hidden_correct']+=sum(pred[i]==((assignment>>j)&1) for j,i in enumerate((5,6)))
                for k in ops[arm]:ops[arm][k]+=getattr(model,k)
                if arm=='disabled' and model.rows!=initial.rows:raise AssertionError('WSP20_DISABLED_MUTATION')
                if arm=='joint_protected':
                    raw=model.snapshot();cold=JointNand.restore(raw)
                    if cold.snapshot()!=raw or pred!=tuple(cold.predict(context(i)) for i in range(8)):raise AssertionError('WSP20_COLD_MISMATCH')
                    restores+=1;states.append(raw)
                    if sig==19:replays+=JointNand(initial.snapshot()).adapt(obs,seed,arm).snapshot()==raw
            print(f'WSP20_PROGRESS seed={seed} signature={sig}',file=sys.stderr,flush=True)
    gain=scores['joint_protected']['observed_correct']-scores['single_protected']['observed_correct']
    supported=(scores['joint_protected']['observed_correct']>=730 and scores['joint_protected']['witness_correct']>=122 and scores['joint_protected']['old_valid_lost']==0 and gain>=16)
    required=(restores==128 and replays==4 and initial_old==472 and all(r['hidden_correct']==512 for r in scores.values())
              and all(ops[a]['proposals']==128*TRIALS20 for a in ARMS)
              and scores['single_protected']['old_valid_lost']==scores['joint_protected']['old_valid_lost']==0)
    report={'schema':'wsp20.protected-joint-dev.v1','engineering':'PASS' if required else 'FAIL',
            'frozen_mechanism_hypothesis':'DEV_SUPPORTED' if supported else 'SCIENTIFIC_NEGATIVE',
            'scientific_superiority':'UNVERIFIED; preprogrammed stochastic search and symbolic control remains perfect',
            'scores':scores,'joint_minus_single_protected_correct':gain,'operations':ops,'cold_restores':restores,'seed_replays':replays,
            'state_digest_sha256':hashlib.sha256(b''.join(states)).hexdigest(),'initial_old_correct':initial_old,'checkpoint_bytes':len(states[0]),
            'resident_binary_synapses':75,'additional_protection_activity_bits':5,'external_replay_examples':6,'candidate_gradient_steps':0,
            'seconds':times,'initial_acquisition_seconds':initial_time,'total_seconds':time.perf_counter()-start,
            'frozen_symbolic_and_trained_observed_correct_of768':768,'comparison_source':'unchanged WSP16 identical signatures/seeds/witness generation; not a new independent scientific replication',
            'environment':{'python':sys.version,'platform':platform.platform()},
            'limits':'Eightfold WSP16 adaptation budget. Joint writes up to3rows per proposal vs1; same forward-evaluation budget is NOT equal parameter-update cost. Initial five protected activity bits and six external examples counted. Hand-designed proposal and protection policy, not primitive invention or unfamiliar-world transfer.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report


if __name__=='__main__':run()
