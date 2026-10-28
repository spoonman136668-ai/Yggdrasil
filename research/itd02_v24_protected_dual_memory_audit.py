"""V24 source-only protected memory versus V23 destructive forgetting.

Target laws remain immutable in V23's EXTERNAL audit only. There is no
original-world training or independent unfamiliar-environment evidence.
"""
import hashlib
import itertools
import json
import math
import subprocess
import time
import tracemalloc
from pathlib import Path

from research.itd02_v18_intermediate_plasticity_audit import target as source_target
from research.itd02_v23_unfamiliar_mapping_audit import (
    ACTIONS, PUBLIC_CUES, CONTEXTS, FAMILIES, new_target, target_split,
    train_source, conventional_weights, ridge_predict, evaluate, episode,
)
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev, canonical
from yggdrasil.itd02_v24_protected_dual_memory_dev import (
    ProtectedDualMemoryRingDev, CHECKPOINT_BOUND, STORED_SCALARS,
)

PARENT = "e5bf689f213a72d9f572320fc14ab2eeb05cc0ff"
PREREG = "230bc53bdce762e36907df645c957ae043f075be"
BLOBS = {
    "yggdrasil/itd02_native_task_bridge_dev.py": "71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
    "yggdrasil/itd02_local_ring_memory_dev.py": "1db0835d5c99456bcf99a013d4836f49314a9d39",
    "yggdrasil/itd02_v22_shared_context_ring_dev.py": "73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
    "research/itd02_v23_unfamiliar_mapping_audit.py": "72281fcfb849d96c6ef3b9740c24508dbaa5edfd",
}


def verify():
    root = Path(__file__).resolve().parents[1]
    def git(*args):
        return subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
    for ancestor in (PARENT, PREREG):
        assert git("merge-base","--is-ancestor",ancestor,"HEAD") == ""
    for path,sha in BLOBS.items():
        assert git("hash-object",path)==sha,("PROTECTED_ORIGINAL_BLOB_DRIFT",path)
    assert len(CONTEXTS)==36 and FAMILIES==("cue_second","triple_parity")
    assert STORED_SCALARS==326


def dual_predictions(model, contexts, *, bank="active"):
    original=model.checkpoint()
    frozen=ProtectedDualMemoryRingDev.restore(original)
    assert frozen.checkpoint()==original
    frozen.start_frozen_evaluation()
    identity=frozen.parameters_sha256()
    out=[]
    for cue,first,second in contexts:
        frozen.start_observation(cue)
        frozen.accept_first(first)
        if bank=="active":
            pred=frozen.score(second)
        elif bank=="source":
            pred=frozen.source_score(second)
        elif bank=="fast":
            pred=frozen.fast_score(second)
        else:
            raise ValueError("INVALID_V24_EVALUATION_BANK")
        frozen.accept_second(second,0.0,learning=False)
        out.append(pred)
    assert frozen.parameters_sha256()==identity
    assert frozen.source_sha==model.source_sha
    return out


def policy(model, family, *, bank):
    clone=ProtectedDualMemoryRingDev.restore(model.checkpoint())
    clone.start_frozen_evaluation()
    regret=0.0
    perfect=0
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        clone.start_observation(cue)
        clone.accept_first(first)
        if bank=="active":
            scores=clone.scores()
        elif bank=="source":
            scores=[clone.source_score(a) for a in ACTIONS]
        elif bank=="fast":
            scores=[clone.fast_score(a) for a in ACTIONS]
        else:
            raise ValueError("INVALID_POLICY_BANK")
        chosen=max(range(3),key=lambda i:scores[i])
        values=[new_target(family,cue,first,a) for a in ACTIONS]
        delta=max(values)-values[chosen]
        assert delta>=-1e-12
        regret+=delta
        perfect+=int(delta<=1e-12)
        clone.accept_second(ACTIONS[chosen],0.0,learning=False)
    return {"sum_regret":regret,"optimal_count":perfect}


def errors(predictions, contexts, family):
    return sum(abs(p-new_target(family,*c))
               for p,c in zip(predictions,contexts))


def run_family(family, source_blob, observed, withheld):
    clock=time.perf_counter()
    model=ProtectedDualMemoryRingDev(source_blob)
    original_sha=model.source_sha
    source_pre=evaluate(SharedContextRingDev.restore(source_blob),CONTEXTS,
                        lambda *c:source_target(*c,nonlinear=True))
    source_pre_error=sum(abs(p-source_target(*c,nonlinear=True))
                         for p,c in zip(source_pre,CONTEXTS))
    assert source_pre_error>0
    assert model.target_updates==0 and not model.gate_fast
    zero_shot=dual_predictions(model,withheld,bank="active")
    saved_before=model.checkpoint()
    assert ProtectedDualMemoryRingDev.restore(saved_before).checkpoint()==saved_before

    original=SharedContextRingDev.restore(source_blob)
    scratch=SharedContextRingDev(mode="shared")
    switch_trace=[]
    for context in observed:
        reward=new_target(family,*context)
        model.start_observation(context[0])
        model.accept_first(context[1])
        previous=model.gate_fast
        model.accept_second(context[2],reward)
        episode(original,context,reward,fit=True)
        episode(scratch,context,reward,fit=True)
        assert model.source_sha==original_sha
        assert model.slow.parameters_sha256()==original_sha
        assert model.fast.parameters_sha256()==scratch.parameters_sha256(), (
            "FAST_BANK_IS_NOT_IDENTICAL_SCRATCH")
        switch_trace.append({
            "actual_public_selected_action":context[2],
            "fast_active_after_observation":model.gate_fast,
            "did_switch":model.gate_fast!=previous,
            "seen_public_rewards":model.target_updates,
        })
    assert model.target_updates==12
    assert original.updates==588 and scratch.updates==12
    assert model.slow.parameters_sha256()==original_sha
    assert model.fast.parameters_sha256()==scratch.parameters_sha256()
    model_saved=model.checkpoint()
    assert len(model_saved)<=CHECKPOINT_BOUND
    assert ProtectedDualMemoryRingDev.restore(model_saved).checkpoint()==model_saved

    banks={kind:dual_predictions(model,withheld,bank=kind)
           for kind in ("active","source","fast")}
    source_old=evaluate(original,withheld,
                        lambda *c:new_target(family,*c))
    scratch_p=evaluate(scratch,withheld,
                       lambda *c:new_target(family,*c))
    assert all(abs(a-b)<1e-10 for a,b in zip(banks["fast"],scratch_p))
    weights=conventional_weights(
        observed,lambda *c:new_target(family,*c))
    ridge=[ridge_predict(weights,c) for c in withheld]
    mean=sum(new_target(family,*c) for c in observed)/12
    target_zeros=[0.0]*len(withheld)
    target_means=[mean]*len(withheld)
    all_predictions={
        "v24_online_selected":banks["active"],
        "v24_protected_source_bank":banks["source"],
        "v24_fast_bank":banks["fast"],
        "v23_pretrained_destructive":source_old,
        "v23_scratch_shared":scratch_p,
        "target_only_80_feature_ridge":ridge,
        "zero":target_zeros,
        "observed_label_mean":target_means,
    }
    scores={k:errors(v,withheld,family) for k,v in all_predictions.items()}
    active_source=dual_predictions(model,CONTEXTS,bank="active")
    protected_source=dual_predictions(model,CONTEXTS,bank="source")
    original_after=evaluate(original,CONTEXTS,
                            lambda *c:source_target(*c,nonlinear=True))
    source_post_error=sum(abs(p-source_target(*c,nonlinear=True))
                          for p,c in zip(protected_source,CONTEXTS))
    source_active_error=sum(abs(p-source_target(*c,nonlinear=True))
                            for p,c in zip(active_source,CONTEXTS))
    source_destructive_error=sum(abs(p-source_target(*c,nonlinear=True))
                                 for p,c in zip(original_after,CONTEXTS))
    assert abs(source_post_error-source_pre_error)<=1e-10, (
        "PROTECTED_MEMORY_SOURCE_RETENTION_MISMATCH")
    regrets={kind:policy(model,family,bank=kind)
             for kind in ("active","source","fast")}
    checkpoint_bytes={
        "v24_dual":len(model_saved),
        "v23_original_destructive":len(original.checkpoint()),
        "v23_scratch":len(scratch.checkpoint()),
    }
    messages={
        "slow":{
            "input":model.slow.forward_input_messages,
            "output":model.slow.forward_output_messages,
            "reverse":model.slow.reverse_credit_messages,
        },
        "fast":{
            "input":model.fast.forward_input_messages,
            "output":model.fast.forward_output_messages,
            "reverse":model.fast.reverse_credit_messages,
        },
    }
    records=[{
        "family":family,
        "cue":case[0],"actual_first":case[1],"heldout_second":case[2],
        "toy_target":round(new_target(family,*case),12),
        "v24_zero_shot_before_any_target_reward":round(zero_shot[i],12),
        "predictions_after_12_observed":{
            k:round(values[i],12) for k,values in all_predictions.items()
        },
    } for i,case in enumerate(withheld)]
    return {
        "family":family,"errors":scores,
        "source_retention":{
            "protected_before":source_pre_error,
            "protected_after":source_post_error,
            "active_selected_source_after":source_active_error,
            "v23_destructive_source_after":source_destructive_error,
        },
        "selector":{
            "fast_active_after_12_observations":model.gate_fast,
            "flips":model.gate_flips,
            "cumulative_source_prediction_absolute_error":model.slow_loss,
            "cumulative_fast_prediction_absolute_error":model.fast_loss,
            "trace":switch_trace,
        },
        "regrets":regrets,
        "checkpoint_bytes":checkpoint_bytes,
        "edge_messages":messages,
        "protected_source_sha_unchanged":model.slow.parameters_sha256()==original_sha,
        "fast_equals_scratch_24_predictions":True,
        "source_only_cases":records,
        "resource_wall_seconds":time.perf_counter()-clock,
    }


def main():
    verify()
    tracemalloc.start()
    start=time.perf_counter()
    source=train_source()["pretrained_shared"]
    observed,withheld=target_split()
    assert len(observed)==12 and len(withheld)==24
    results={family:run_family(family,source,observed,withheld)
             for family in FAMILIES}
    parity={}
    gains={}
    vs_ridge={}
    for family in FAMILIES:
        e=results[family]["errors"]
        selected=e["v24_online_selected"]
        scratch=e["v23_scratch_shared"]
        parity[family]=selected<=1.1*scratch
        gains[family]=selected<=0.9*scratch
        vs_ridge[family]=selected<e["target_only_80_feature_ridge"]
    if not all(parity.values()):
        classification="V24_PROTECTED_SOURCE_RETENTION_BUT_ACTIVE_TARGET_ADAPTATION_NO_GO__NO_SCIENCE"
    elif not all(gains.values()):
        classification="V24_SOURCE_MEMORY_PRESERVED_TARGET_PARITY_ONLY__NO_SCIENCE"
    elif all(vs_ridge.values()):
        classification="V24_PROTECTED_MEMORY_AND_TARGET_TOY_GAIN__NO_SCIENCE"
    else:
        classification="V24_SOURCE_MEMORY_PRESERVED_TARGET_PARITY_ONLY__NO_SCIENCE"
    all_cases=[case for family in FAMILIES for case in results[family]["source_only_cases"]]
    assert len(all_cases)==48
    current,peak=tracemalloc.get_traced_memory()
    receipt={
        "schema":"ygg.itd02.v24.protected_slow_and_evidence_selected_fast.source_only.v1",
        "classification":classification,"source_only":True,
        "scientific_first_use":False,"original_world_training":False,
        "original_native_unchanged":True,
        "physical_native_ring_cells_per_bank":8,
        "stored_learned_scalars":STORED_SCALARS,
        "target_trainable_scalars":STORED_SCALARS//2,
        "explicit_external_source_target_boundary":True,
        "uses_centralized_two_loss_selector":True,
        "independent_unfamiliar_world_transfer_proven":False,
        "source_pretraining_episodes":576,
        "target_label_count_per_family":12,
        "target_heldout_outcome_count_per_family":24,
        "source_bank_checkpoint_bytes":len(source),
        "retention_and_target_metrics":{
            f:{k:v for k,v in result.items()
               if k not in ("source_only_cases","resource_wall_seconds")}
            for f,result in results.items()
        },
        "within_ten_pct_scratch_on_both":parity,
        "target_gain_ten_pct_over_scratch":gains,
        "beats_target_only_ridge":vs_ridge,
        "canonical_48_case_sha256":hashlib.sha256(canonical(all_cases)).hexdigest(),
        "host_specific_resources":{
            "wall_seconds":time.perf_counter()-start,
            "python_tracemalloc_peak_bytes":peak,
            "python_tracemalloc_current_bytes":current,
            "per_family_wall_seconds":{
                f:result["resource_wall_seconds"] for f,result in results.items()},
            "scope":"GitHub Python3.12 test-harness not retail PC benchmark",
        },
        "qualifier":"BOUNDED_MEMORY_ISOLATION_NOT_AUTONOMOUS_CONSOLIDATION_OR_SCIENCE",
    }
    print(json.dumps(receipt,sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()
