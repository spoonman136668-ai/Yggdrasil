"""V26 immutable source-only return-selectivity behavioral audit.

Synthetic laws and stage IDs exist ONLY in the evaluator. Original native
V22, protected V24 and V25 negative are unchanged. No scientific first use.
"""
import copy
import hashlib
import json
import subprocess
import time
import tracemalloc
from pathlib import Path

from research.itd02_v23_unfamiliar_mapping_audit import train_source, target_split
from research.itd02_v25_return_sequence_audit import RidgeCUSUM, public_step, reward
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES, canonical
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v25_unlabeled_return_dev import UnlabeledReturnRingDev
from yggdrasil.itd02_v26_crosscue_return_dev import (
    CrossCueReturnRingDev, CHECKPOINT_BOUND, NATIVE_LEARNED_SCALARS,
)

# Exact preregistered manifest, source SHA 28075b87f76a6a03d525fcacc0eabac940915736.
STREAMS = (
 ("basic_t1",(("cue_second",12),("source",12)),1,0),
 ("basic_t2",(("triple_parity",12),("source",12)),4,3),
 ("long_t1_t2",(("cue_second",8),("triple_parity",10),("source",12)),7,6),
 ("long_t2_t1",(("triple_parity",10),("cue_second",8),("source",12)),10,9),
 ("unchanged_source",(("source",12),("source",12)),2,0),
 ("unchanged_t1",(("cue_second",12),("cue_second",12)),5,3),
 ("unchanged_t2",(("triple_parity",12),("triple_parity",12)),8,6),
 ("confusable_target_only",(("cue_second",12),("triple_parity",10),("cue_second",12)),11,9),
)
HEADS=("candidate","ablation","v25","fast","source","destructive",
       "rls_cusum","rls_two_expert","rls_direct","zero","mean","stage_oracle")

def event(i,shift,offset):
    k=(5*i+shift)%12
    j=k+offset
    return (PUBLIC_CUES[j%4],ACTIONS[(2*j+1)%3],ACTIONS[(j+j//4)%3])

def begin(m,case):
    m.start_observation(case[0])
    m.accept_first(case[1])

def predict_case(m,case):
    begin(m,case)
    p=m.score(case[2])
    m.accept_second(case[2],0.0,learning=False)
    return p

def readonly_snapshot(model,ablation,v25,fast,destructive,rls,law,mean):
    """36 counterfactual choices; frozen clones, NO reward feedback to learners."""
    a=CrossCueReturnRingDev.restore(model.checkpoint())
    b=CrossCueReturnRingDev.restore(ablation.checkpoint())
    c=UnlabeledReturnRingDev.restore(v25.checkpoint())
    f=SharedContextRingDev.restore(fast.checkpoint())
    d=SharedContextRingDev.restore(destructive.checkpoint())
    q=copy.deepcopy(rls)
    for m in (a,b,c,f,d):
        m.start_frozen_evaluation()
    regrets={n:0.0 for n in HEADS}
    errors={n:0.0 for n in HEADS}
    for cue in PUBLIC_CUES:
        for first in ACTIONS:
            scores={n:[] for n in HEADS}
            outcomes=[]
            for action in ACTIONS:
                case=(cue,first,action)
                for m in (a,b,c):
                    begin(m,case)
                a_score=a.score(action)
                b_score=b.score(action)
                c_score=c.score(action)
                source_score=a.bank.source_score(action)
                fast_score=a.bank.fast_score(action)
                scores["candidate"].append(a_score)
                scores["ablation"].append(b_score)
                scores["v25"].append(c_score)
                scores["source"].append(source_score)
                scores["stage_oracle"].append(source_score if law=="source" else fast_score)
                for m in (a,b,c):
                    m.accept_second(action,0.0,learning=False)
                scores["fast"].append(predict_case(f,case))
                scores["destructive"].append(predict_case(d,case))
                _,ridge,cs,two=q.predictions(case)
                scores["rls_cusum"].append(cs)
                scores["rls_two_expert"].append(two)
                scores["rls_direct"].append(ridge)
                scores["zero"].append(0.0)
                scores["mean"].append(mean)
                outcomes.append(reward(law,case))
            optimal=max(outcomes)
            for name,preds in scores.items():
                chosen=max(range(3),key=lambda i:preds[i])
                regrets[name]+=optimal-outcomes[chosen]
                errors[name]+=sum(abs(p-y) for p,y in zip(preds,outcomes))
    return {"regret":{k:round(v,10) for k,v in regrets.items()},
            "abs_error_36":{k:round(v,10) for k,v in errors.items()}}

def heldout_target(model,fast,law):
    if law=="source":
        return None
    _,heldout=target_split()
    a=CrossCueReturnRingDev.restore(model.checkpoint())
    b=SharedContextRingDev.restore(fast.checkpoint())
    a.start_frozen_evaluation()
    b.start_frozen_evaluation()
    ea=eb=0.0
    for case in heldout:
        truth=reward(law,case)
        ea+=abs(predict_case(a,case)-truth)
        eb+=abs(predict_case(b,case)-truth)
    return {"candidate":round(ea,10),"always_fast":round(eb,10),"count":len(heldout)}

def run(name,stages,shift,offset,source):
    start=time.perf_counter()
    m=CrossCueReturnRingDev(source)
    a=CrossCueReturnRingDev(source,require_diversity=False)
    v=UnlabeledReturnRingDev(source)
    f=SharedContextRingDev(mode="shared")
    d=SharedContextRingDev.restore(source)
    q=RidgeCUSUM(source)  # existing full 80x80 online recursive least squares + CUSUM
    sha=m.bank.source_sha
    assert m.bank.slow.updates==576
    records=[];snapshots=[];stages_out=[]
    mean=0.0;seen=0;max_bytes=0
    for si,(law,length) in enumerate(stages):
        is_return=si>0 and law=="source" and stages[si-1][0]!="source"
        ret_err={k:0.0 for k in HEADS}
        latency=None;reactivations=0;false=0;slow_occupancy=0
        windows={}
        for i in range(length):
            case=event(i,shift,offset)
            truth=reward(law,case)  # evaluator-side ONLY
            for x in (m,a,v):
                begin(x,case)
            previously_fast=m.use_fast
            active=m.score(case[2])
            alt=a.score(case[2])
            vp=v.score(case[2])
            old=m.bank.source_score(case[2])
            fp=public_step(f,case,truth)
            dp=public_step(d,case,truth)
            sp,rp,cs,tp=q.predictions(case)
            preds=dict(candidate=active,ablation=alt,v25=vp,fast=fp,
                       source=old,destructive=dp,rls_cusum=cs,
                       rls_two_expert=tp,rls_direct=rp,zero=0.0,mean=mean,
                       stage_oracle=(old if law=="source" else fp))
            for x in (m,a,v):
                x.accept_second(case[2],truth)
            q.observe(case,truth,sp,rp)
            seen+=1
            mean+=(truth-mean)/seen
            assert m.bank.slow.parameters_sha256()==sha
            assert a.bank.slow.parameters_sha256()==sha
            assert m.bank.fast.parameters_sha256()==f.parameters_sha256()
            assert a.bank.fast.parameters_sha256()==f.parameters_sha256()
            returned_to_slow=previously_fast and not m.use_fast
            reactivations+=int(returned_to_slow)
            if is_return and returned_to_slow and latency is None:
                latency=i+1
            if si>0 and law!="source" and i>=4:
                false+=int(returned_to_slow)
                slow_occupancy+=int(not m.use_fast)
            if is_return:
                for k,p in preds.items():
                    ret_err[k]+=abs(p-truth)
                if i+1 in (1,4,8,12):
                    windows[str(i+1)]={k:round(v,10) for k,v in ret_err.items()}
            records.append({"name":name,"stage":si,"index":i+1,"actual_selected":case,
                "reward_observed":round(truth,12),
                "pre_feedback":{k:round(x,12) for k,x in preds.items()},
                "used_fast_before":previously_fast,
                "used_fast_after":m.use_fast,
                "v25_fast_after":v.use_fast,
                "ablation_fast_after":a.use_fast,
                "public_residual_window":[[round(r,12),g] for r,g in m.recent]})
            cp=m.checkpoint()
            max_bytes=max(max_bytes,len(cp))
            assert CrossCueReturnRingDev.restore(cp).checkpoint()==cp
            assert len(cp)<=CHECKPOINT_BOUND
            if i+1 in (1,4,8,12):
                snapshots.append({"name":name,"stage":si,"event":i+1,
                    "law_evaluator_only":law,
                    **readonly_snapshot(m,a,v,f,d,q,law,mean)})
        end_snap=[s for s in snapshots if s["stage"]==si][-1]
        stages_out.append({"index":si,"law_evaluator_only":law,"events":length,
            "return":is_return,"return_latency":latency,
            "return_error":{k:round(v,10) for k,v in ret_err.items()} if is_return else None,
            "return_window_error":windows,
            "reactivations":reactivations,
            "false_reactivations_postwarmup":false,
            "slow_occupancy_postwarmup":slow_occupancy,
            "last_snapshot":end_snap,
            "target_heldout":heldout_target(m,f,law)})
    messages={
      "source":{"input":m.bank.slow.forward_input_messages,
                "output":m.bank.slow.forward_output_messages,
                "reverse":m.bank.slow.reverse_credit_messages},
      "fast":{"input":m.bank.fast.forward_input_messages,
              "output":m.bank.fast.forward_output_messages,
              "reverse":m.bank.fast.reverse_credit_messages}}
    assert m.bank.slow.parameters_sha256()==sha
    assert CrossCueReturnRingDev.restore(m.checkpoint()).checkpoint()==m.checkpoint()
    return {"name":name,"stages":stages_out,"records":records,"snapshots":snapshots,
       "source_sha":sha,"source_sha_unchanged":True,"max_checkpoint_bytes":max_bytes,
       "stored_learned_scalars":NATIVE_LEARNED_SCALARS,
       "fast_updates":m.bank.fast.updates,"original_source_updates":m.bank.slow.updates,
       "edge_messages":messages,"wall_seconds":time.perf_counter()-start}

def decision(results):
    basics=[x["stages"][-1] for x in results[:2]]
    controls=[results[i]["stages"][-1] for i in (5,6,7)]
    detection=all(s["return_latency"] is not None and s["return_latency"]<=4
                  for s in basics)
    no_false=all(s["false_reactivations_postwarmup"]==0 and
                 s["slow_occupancy_postwarmup"]==0 for s in controls)
    gain=all(s["return_error"]["candidate"]<=.90*s["return_error"]["fast"]
             and s["return_error"]["candidate"]<=.90*s["return_error"]["rls_cusum"]
             and s["last_snapshot"]["regret"]["candidate"]<
                 s["last_snapshot"]["regret"]["fast"]
             and s["last_snapshot"]["regret"]["candidate"]<
                 s["last_snapshot"]["regret"]["rls_cusum"] for s in basics)
    extended=all(x["stages"][-1]["return_latency"] is not None and
                 x["stages"][-1]["return_latency"]<=4 for x in results[2:4])
    adaptation=all(x["stages"][0]["target_heldout"]["candidate"]<=
                   1.10*x["stages"][0]["target_heldout"]["always_fast"]
                   for x in results[:2])
    if not detection or not no_false:
        klass="V26_SOURCE_RETURN_SELECTIVITY_NOT_ESTABLISHED__NO_SCIENCE"
    elif not gain:
        klass="V26_REACTIVATION_WITHOUT_STRONG_CONTROL_GAIN__NO_SCIENCE"
    elif not extended or not adaptation:
        klass="V26_RETURN_GAIN_NOT_ROBUST__NO_SCIENCE"
    else:
        klass="V26_BOUNDED_SYNTHETIC_RETURN_SELECTIVITY_ENGINEERING_POSITIVE__NO_SCIENCE"
    return klass,dict(basic_latency_pass=detection,false_activations_zero=no_false,
                      strong_prediction_and_regret_gain=gain,
                      extended_reactivation=extended,target_adaptation_preserved=adaptation)

def verify():
    root=Path(__file__).resolve().parents[1]
    def git(*args):
        return subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
    for sha in ("7f3d16b542e83c87abdacdf8e8988ca20c1e215e",
                "9eb4e7305cbd55e146ff64c8f82f06edb87a5350",
                "28075b87f76a6a03d525fcacc0eabac940915736",
                "19ec2bcd6c3529fbc5c17d8c47afdf9490402bbe"):
        assert git("merge-base","--is-ancestor",sha,"HEAD")==""
    pins={
      "yggdrasil/itd02_native_task_bridge_dev.py":"71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
      "yggdrasil/itd02_local_ring_memory_dev.py":"1db0835d5c99456bcf99a013d4836f49314a9d39",
      "yggdrasil/itd02_v22_shared_context_ring_dev.py":"73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
      "yggdrasil/itd02_v24_protected_dual_memory_dev.py":"9ef95a28e9060dd79105f51122d527351756a1e0",
      "yggdrasil/itd02_v25_unlabeled_return_dev.py":"f90e5029b121cbfc2e361f9e0941985eb1e69e3d",
      "research/itd02_v25_return_sequence_audit.py":"6bd7b9ffc92b8b4739f7d2c7f73d4e7cdbd2b0a5",
      "research/itd02_v26_return_selectivity_preregistration.md":"6e672b6a2d20b372e8ff0d1bb2f05c15697c84b4",
      "research/itd02_v26_frozen_source_only_schedule.md":"052e3cba3f059c3430df461299c81155a0eb85ce",
    }
    for path,sha in pins.items():
        assert git("hash-object",path)==sha,("SOURCE_ID_DRIFT",path)
    assert len(STREAMS)==8 and NATIVE_LEARNED_SCALARS==326

def main():
    verify()
    tracemalloc.start()
    start=time.perf_counter()
    cpu=time.process_time()
    source=train_source()["pretrained_shared"]
    outcomes=[run(*s,source) for s in STREAMS]
    klass,gates=decision(outcomes)
    evidence=[{"name":x["name"],"records":x["records"],"snapshots":x["snapshots"]}
              for x in outcomes]
    digest=hashlib.sha256(canonical(evidence)).hexdigest()
    peak=tracemalloc.get_traced_memory()[1]
    out={"schema":"ygg.itd02.v26.return_selectivity.source_only.v1",
         "source_only":True,"scientific_first_use":False,
         "independent_unfamiliar_world_transfer_proven":False,
         "original_world_training":False,"original_native_unchanged":True,
         "candidate_scalars":NATIVE_LEARNED_SCALARS,
         "classification":klass,"gates":gates,"streams_count":len(outcomes),
         "full_matrix_rls_conventional_control":True,
         "v25_control_unchanged":True,
         "canonical_case_regret_sha256":digest,
         "streams":[{k:v for k,v in x.items()
                    if k not in ("records","snapshots","wall_seconds")} for x in outcomes],
         "host_specific_resources":{
            "wall_seconds":time.perf_counter()-start,
            "cpu_seconds":time.process_time()-cpu,
            "python_tracemalloc_peak_bytes":peak,
            "per_stream_wall_seconds":{x["name"]:x["wall_seconds"] for x in outcomes},
            "not_retail_windows_benchmark":True}}
    print(json.dumps(out,sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
