"""Frozen known-workload comparison. Capacity witnesses stay evaluator-only."""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from two_row import TwoRow,PlasticNand,ARMS,SEEDS,PUBLIC,context,TRIALS20

ROOT=Path(__file__).resolve().parent
OPKEYS=('proposals','accepted','gate_evaluations','noise_draws','proposed_row_writes','changed_coordinates','accepted_coordinates')

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def deep_size(value,seen=None):
    seen=set() if seen is None else seen
    if id(value) in seen:return 0
    seen.add(id(value));n=sys.getsizeof(value)
    if isinstance(value,dict):n+=sum(deep_size(k,seen)+deep_size(v,seen) for k,v in value.items())
    elif isinstance(value,(tuple,list)):n+=sum(deep_size(v,seen) for v in value)
    return n

def run():
    start=time.perf_counter();ceiling_trace=json.loads((ROOT.parent/'WSP-23/workload-trace.json').read_text())
    scores={a:{k:0 for k in ('observed_correct','witness_correct','old_valid_lost','exact_tasks','hidden_correct','at_task_ceiling','cold_restores','replays')} for a in ARMS}
    ops={a:{k:0 for k in OPKEYS} for a in ARMS};timings={a:0. for a in ARMS};initial_time=0.;initial_valid=0
    states={a:[] for a in ARMS};traces=[];memory={a:0 for a in ARMS};checkpoint_sizes={a:set() for a in ARMS};maxreplay=0
    for seed in SEEDS:
        for sig in range(32):
            original=tuple((context(i),(sig>>j)&1) for j,i in enumerate(PUBLIC))
            tick=time.perf_counter();initial=PlasticNand().learn(original,seed);initial_time+=time.perf_counter()-tick
            initial_pred=tuple(initial.predict(context(i)) for i in range(8))
            obs=original+((context(3),1-initial_pred[3]),);maxreplay=max(maxreplay,deep_size(obs))
            valid=[initial_pred[i]==y for i,(_x,y) in zip(PUBLIC,original)];initial_valid+=sum(valid)
            case={'seed':seed,'signature':sig,'initial_checkpoint_sha256':hashlib.sha256(initial.snapshot()).hexdigest(),'arms':{}}
            for arm in ARMS:
                tick=time.perf_counter();m=TwoRow(initial.snapshot(),arm).adapt(obs,seed);timings[arm]+=time.perf_counter()-tick
                pred=tuple(m.predict(context(i)) for i in range(8));r=scores[arm]
                fit=sum(pred[i]==y for i,(_x,y) in zip(PUBLIC+(3,),obs));lost=sum(ok and pred[i]!=y for ok,i,(_x,y) in zip(valid,PUBLIC,original))
                r['observed_correct']+=fit;r['witness_correct']+=pred[3]==obs[-1][1];r['old_valid_lost']+=lost;r['exact_tasks']+=fit==6
                for assignment in range(4):r['hidden_correct']+=sum(pred[i]==((assignment>>j)&1) for j,i in enumerate((5,6)))
                # Truth/capacity metadata is checked AFTER candidate learning.
                cert=ceiling_trace[len(traces)]
                if cert['seed']!=seed or cert['original_signature']!=sig or cert['observed_target']!=sig+(obs[-1][1]<<5) or cert['protected_mask']!=sum(int(v)<<j for j,v in enumerate(valid)):raise AssertionError('WSP26_CAPACITY_WORKLOAD_DRIFT')
                if fit>cert['ceiling']:raise AssertionError('WSP26_CAPACITY_EXCEEDED')
                r['at_task_ceiling']+=fit==cert['ceiling']
                for k in OPKEYS:ops[arm][k]+=getattr(m,k)
                if arm=='disabled' and m.rows!=initial.rows:raise AssertionError('WSP26_DISABLED_MUTATION')
                raw=m.snapshot();cold=TwoRow.restore(raw)
                if cold.snapshot()!=raw or pred!=tuple(cold.predict(context(i)) for i in range(8)):raise AssertionError('WSP26_COLD_MISMATCH')
                r['cold_restores']+=1;states[arm].append(raw);checkpoint_sizes[arm].add(len(raw))
                if sig==19:
                    replay=TwoRow(initial.snapshot(),arm).adapt(obs,seed).snapshot()
                    if replay!=raw:raise AssertionError('WSP26_REPLAY_MISMATCH')
                    r['replays']+=1
                memory[arm]=max(memory[arm],sys.getsizeof(m)+deep_size(m.__dict__))
                case['arms'][arm]={'observed_correct':fit,'old_valid_lost':lost,'predictions':pred,'checkpoint_sha256':hashlib.sha256(raw).hexdigest()}
            traces.append(case)
            print(f'WSP26_PROGRESS seed={seed} signature={sig}',file=sys.stderr,flush=True)
    required=(initial_valid==472 and scores['single_protected']['observed_correct']==742 and scores['disabled']['observed_correct']==472
              and all(r['old_valid_lost']==0 and r['cold_restores']==128 and r['replays']==4 and r['hidden_correct']==512 for r in scores.values())
              and all(o['proposals']==128*TRIALS20 and o['gate_evaluations']==128*TRIALS20*72 and o['noise_draws']==128*TRIALS20*5 for o in ops.values()))
    mixed=scores['mixed_protected'];gain=mixed['observed_correct']-742
    supported=mixed['observed_correct']==752 and gain==10 and mixed['old_valid_lost']==0 and mixed['at_task_ceiling']==128
    report={'schema':'wsp26.protected-two-row-credit.v1','engineering':'PASS' if required else 'FAIL','frozen_hypothesis':'DEV_SUPPORTED' if supported else 'SCIENTIFIC_NEGATIVE','scientific_superiority':'UNVERIFIED: authored existing public finite workload, hand-designed numerical search, unmatched larger conventional references','scores':scores,'mixed_minus_single_gain':gain,'remaining_gap_to_certified_ceiling':752-mixed['observed_correct'],'operations':ops,'initial_valid':initial_valid,'inference_synaptic_binary_coordinates':75,'protection_bits':5,'external_replay_binary_values':24,'candidate_gradient_steps':0,'times_seconds':timings,'initial_acquisition_seconds':initial_time,'total_seconds':time.perf_counter()-start,'state_digest_sha256':{a:hashlib.sha256(b''.join(v)).hexdigest() for a,v in states.items()},'trace_sha256':hashlib.sha256(canonical(traces)).hexdigest(),'checkpoint_bytes':{a:sorted(v) for a,v in checkpoint_sizes.items()},'python_model_retained_bytes_including_counters':memory,'replay_python_bytes':maxreplay,'workspace_bounds':'13 current+13 trial packed row words; up to9 packed six-lane activations per forward call; RNG/control/error scalars. Python retained-object sizes measured above; process peak RSS/energy not measured. Six-example replay supplied externally and charged; no persistent replay claim.','diagnostic_replay_trials_separate_from_primary':4*4*TRIALS20,'frozen_capacity_larger_symbolic_trained_reference_correct':768,'environment':{'python':sys.version,'platform':platform.platform()},'traces':traces,'limits':'Same forward budget, unequal row writes. Vectorization preserves exact dynamics and benefits every arm; do not attribute runtime savings to a better update policy. Fully trained larger references/solver remain stronger but capacity-unmatched. No unseen-label generalization or complete training claim. Prior WSP20 negative and WSP23 proof unchanged.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report
if __name__=='__main__':run()
