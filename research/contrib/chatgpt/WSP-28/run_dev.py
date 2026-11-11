"""Disjoint public DEV replication using completely unchanged WSP27 policies."""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.append(str(ROOT.parent/'WSP-27'))
from routed import Routed,PlasticNand,ARMS,SEEDS,PUBLIC,context,TRIALS20
sys.path.append(str(ROOT.parent/'WSP-23'))
from capacity_proof import verify
from cases import load_manifest,MANIFEST_SHA
OPKEYS=('proposals','accepted','gate_evaluations','noise_draws','proposed_row_writes','changed_coordinates','accepted_coordinates','reverse_steps','eligibility_tests','auxiliary_draws','routed_row_changes')

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def deep_size(value,seen=None):
    seen=set() if seen is None else seen
    if id(value) in seen:return 0
    seen.add(id(value));n=sys.getsizeof(value)
    if isinstance(value,dict):n+=sum(deep_size(k,seen)+deep_size(v,seen) for k,v in value.items())
    elif isinstance(value,(tuple,list)):n+=sum(deep_size(v,seen) for v in value)
    return n

def protected_ceiling(reachable,target,mask):
    eligible=[v for v in reachable if ((v^target)&mask)==0]
    if not eligible:raise ValueError('WSP28_NO_PROTECTED_RESPONSE')
    return max(6-(v^target).bit_count() for v in eligible)

def run():
    start=time.perf_counter();manifest=load_manifest();proof=json.loads((ROOT.parent/'WSP-23/proof-allow_disconnected.json').read_text())
    proof_start=time.perf_counter();checked=verify(proof);proof_seconds=time.perf_counter()-proof_start;reachable=set(proof['outputs'][-1])
    parent=json.loads((ROOT.parent/'WSP-27/result.json').read_text());old={(c['seed'],c['signature']):c for c in parent['traces']}
    scores={a:{k:0 for k in ('observed_correct','new_context_correct','old_valid_lost','exact_tasks','hidden_correct','at_task_ceiling','cold_restores','replays')} for a in ARMS}
    ops={a:{k:0 for k in OPKEYS} for a in ARMS};timings={a:0. for a in ARMS};initial_time=0.;initial_valid=0;ceiling_total=0;infeasible=0
    states={a:[] for a in ARMS};traces=[];memory={a:0 for a in ARMS};sizes={a:set() for a in ARMS};maxreplay=0
    for c in manifest['cases']:
        seed=c['seed'];sig=c['signature'];target=c['target'];protection=c['protected_mask']
        original=tuple((context(i),(sig>>j)&1) for j,i in enumerate(PUBLIC))
        tick=time.perf_counter();initial=PlasticNand().learn(original,seed);initial_time+=time.perf_counter()-tick
        initial_pred=tuple(initial.predict(context(i)) for i in range(8));initial_raw=initial.snapshot()
        if hashlib.sha256(initial_raw).hexdigest()!=old[seed,sig]['initial_checkpoint_sha256']:raise AssertionError('WSP28_PREFIX_COLD_CUSTODY')
        if (target>>5)!=initial_pred[3] or target^c['old_target']!=32:raise AssertionError('WSP28_COMPLEMENT_CUSTODY')
        obs=original+((context(3),target>>5),);maxreplay=max(maxreplay,deep_size(obs))
        valid=[initial_pred[i]==y for i,(_x,y) in zip(PUBLIC,original)];initial_valid+=sum(valid)
        if sum(int(v)<<j for j,v in enumerate(valid))!=protection:raise AssertionError('WSP28_PREFIX_PROTECTION_DRIFT')
        ceiling=protected_ceiling(reachable,target,protection);ceiling_total+=ceiling;infeasible+=target not in reachable
        case={'seed':seed,'signature':sig,'target':target,'ceiling':ceiling,'initial_checkpoint_sha256':hashlib.sha256(initial_raw).hexdigest(),'arms':{}}
        for arm in ARMS:
            tick=time.perf_counter();m=Routed(initial_raw,arm).adapt(obs,seed);timings[arm]+=time.perf_counter()-tick
            pred=tuple(m.predict(context(i)) for i in range(8));r=scores[arm]
            fit=sum(pred[i]==y for i,(_x,y) in zip(PUBLIC+(3,),obs));lost=sum(ok and pred[i]!=y for ok,i,(_x,y) in zip(valid,PUBLIC,original))
            if fit>ceiling:raise AssertionError('WSP28_CAPACITY_EXCEEDED')
            r['observed_correct']+=fit;r['new_context_correct']+=pred[3]==obs[-1][1];r['old_valid_lost']+=lost;r['exact_tasks']+=fit==6;r['at_task_ceiling']+=fit==ceiling
            for assignment in range(4):r['hidden_correct']+=sum(pred[i]==((assignment>>j)&1) for j,i in enumerate((5,6)))
            for key in OPKEYS:ops[arm][key]+=getattr(m,key)
            if arm=='disabled' and m.rows!=initial.rows:raise AssertionError('WSP28_DISABLED_MUTATION')
            raw=m.snapshot();cold=Routed.restore(raw)
            if cold.snapshot()!=raw or pred!=tuple(cold.predict(context(i)) for i in range(8)):raise AssertionError('WSP28_COLD_MISMATCH')
            r['cold_restores']+=1;states[arm].append(raw);sizes[arm].add(len(raw))
            if sig==19:
                if Routed(initial_raw,arm).adapt(obs,seed).snapshot()!=raw:raise AssertionError('WSP28_REPLAY_MISMATCH')
                r['replays']+=1
            memory[arm]=max(memory[arm],sys.getsizeof(m)+deep_size(m.__dict__))
            case['arms'][arm]={'observed_correct':fit,'old_valid_lost':lost,'predictions':pred,'checkpoint_sha256':hashlib.sha256(raw).hexdigest()}
        traces.append(case);print(f'WSP28_PROGRESS seed={seed} signature={sig}',file=sys.stderr,flush=True)
    required=(len(traces)==120 and initial_valid==444 and scores['disabled']['observed_correct']==564 and checked['verified']
              and all(r['old_valid_lost']==0 and r['cold_restores']==120 and r['replays']==4 and r['hidden_correct']==480 for r in scores.values())
              and all(o['proposals']==983040 and o['proposed_row_writes']==983040 and o['gate_evaluations']==70778880 and o['noise_draws']==4915200 and o['reverse_steps']==5898240 and o['eligibility_tests']==12779520 and o['auxiliary_draws']==983040 for o in ops.values()))
    candidate=scores['error_routed'];comparators=('original_single','uniform_matched','correct_routed');gains={a:candidate['observed_correct']-scores[a]['observed_correct'] for a in comparators}
    supported=candidate['observed_correct']>=684 and all(v>=4 for v in gains.values()) and candidate['old_valid_lost']==0
    report={'schema':'wsp28.disjoint-credit-replication.v1','engineering':'PASS' if required else 'FAIL','frozen_hypothesis':'DEV_SUPPORTED' if supported else 'SCIENTIFIC_NEGATIVE','scientific_superiority':'UNVERIFIED; public synthetic finite family,shared prefixes,unchanged supplied learning rule','manifest_sha256':MANIFEST_SHA,'cases':120,'new_unique_label_signatures':30,'old_unique_label_signatures':34,'global_observed_signature_overlap':0,'consistent_sixth_observation_cases':120,'initial_prefix_valid':initial_valid,'scores':scores,'gains_vs_controls':gains,'protected_capacity_ceiling':ceiling_total,'infeasible_target_cases':infeasible,'search_gap_to_capacity':{a:ceiling_total-r['observed_correct'] for a,r in scores.items()},'proof_checker':checked,'proof_checker_seconds':proof_seconds,'operations':ops,'times_seconds':timings,'initial_acquisition_seconds':initial_time,'total_seconds':time.perf_counter()-start,'state_digest_sha256':{a:hashlib.sha256(b''.join(v)).hexdigest() for a,v in states.items()},'trace_sha256':hashlib.sha256(canonical(traces)).hexdigest(),'checkpoint_bytes':{a:sorted(v) for a,v in sizes.items()},'python_model_retained_bytes_including_counters':memory,'replay_python_bytes':maxreplay,'inference_synaptic_binary_coordinates':75,'protection_bits':5,'external_replay_binary_values':24,'candidate_gradient_steps':0,'diagnostic_replay_trials_separate_from_primary':len(ARMS)*4*TRIALS20,'environment':{'python':sys.version,'platform':platform.platform()},'traces':traces,'limits':'Globally new six-label signatures,shared five-label prefixes and same3bit/NAND family. Fresh model per case,no learned-weight transfer or unfamiliar-world claim. Same five policies byte-identical to WSP27,including approximate Boolean credit and auxiliary-source controls. Same budgets/capacity,reverse-credit work charged equally,external replay and transient memory counted as before. No independent SCIENTIFIC_PASS,complete training,deployment or cost superiority.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report
if __name__=='__main__':run()
