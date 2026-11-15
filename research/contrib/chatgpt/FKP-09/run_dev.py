"""FKP09: original DEV experiment. Strong Bayesian/sparse controls, no protected first use.

Seals candidate & all conventional predictions before reading source DEV held
consequences. All models receive identical genuine action/consequence evidence.
"""
from __future__ import annotations
import hashlib
import json
import random
import statistics
import time

from source import Source,CONTEXTS,BITS,CONTEXT_PAID,parity
from model import SharedCausalCore,PAIR_INDEXES

def conventional_exact_posterior(base:int,history:tuple[tuple[int,int],...],
                                 held:tuple[int,...])->dict:
    """Independent exact Bayesian 2-bit edit solver on same public observations."""
    target=tuple(y^parity(x&base) for x,y in history)
    consistent=[]
    for a in range(BITS):
        for b in range(a+1,BITS):
            if all(((x>>a)&1)^((x>>b)&1)==v for (x,_),v in zip(history,target)):
                consistent.append((a,b))
    if not consistent:
        raise AssertionError("FKP09_STRONG_CONTROL_NO_CANDIDATES")
    pair=consistent[0]
    full_law=base^(1<<pair[0])^(1<<pair[1])
    direct=tuple(parity(x&full_law) for x in held)
    bayes=[]
    for action in held:
        ones=sum(parity(action&(base^(1<<a)^(1<<b))) for a,b in consistent)
        bayes.append(int(ones*2>len(consistent)))
    return {"lex_pair":pair,"lex_exact_prediction":direct,
            "bayes_prediction":tuple(bayes),"candidate_count":len(consistent),
            "baseline_law":full_law,"hypotheses_evaluated":len(PAIR_INDEXES)*len(history)}

def paired_ci(pairs:list[float])->list[float]:
    rng=random.Random(9090)
    n=len(pairs)
    samples=sorted(sum(pairs[rng.randrange(n)] for _ in range(n))/n for _ in range(10000))
    return [samples[249],samples[9749]]

def run_dev()->dict:
    started=time.perf_counter()
    cpu_started=time.process_time()
    owner=Source()
    model=SharedCausalCore()
    foundation_history=tuple((i,owner.observe_core(0,i)) for i in range(BITS))
    assert owner.core_charged(0)==BITS
    model.learn_initial_core(foundation_history)
    learned_core=model.base
    source_history_sha=hashlib.sha256()
    for bit,y in foundation_history:
        source_history_sha.update(bytes((0,bit,y)))
    original={}
    action_receipts=[]
    frozen_pred_sha=hashlib.sha256()
    for context in CONTEXTS:
        public=owner.public_view(context)
        assert len(public.choices)==len(public.held_masks)==128
        assert not set(public.choices)&set(public.held_masks)
        feedback=tuple((a,owner.observe_context(context,a)) for a in public.choices[:CONTEXT_PAID])
        assert owner.context_charged(context)==CONTEXT_PAID
        for a,y in feedback:
            source_history_sha.update(context.to_bytes(2,"big")+a.to_bytes(16,"big")+bytes((y,)))
        fitted=model.learn_context(context,feedback)
        candidate=model.predict(context,public.held_masks)
        conventional=conventional_exact_posterior(learned_core,feedback,public.held_masks)
        reference12=conventional_exact_posterior(learned_core,feedback[:12],public.held_masks)
        prior=tuple(parity(action&learned_core) for action in public.held_masks)
        # A conventional independently fitted *full 128-bit context code* is
        # reconstructed from identical publicly learned data, not source rule.
        fullmask=conventional["baseline_law"]
        independent_full=tuple(parity(action&fullmask) for action in public.held_masks)
        # A conventional same-data sparse delta has exactly the inferred 2
        # flip indices, and will have the same fixed 8-index rebase capacity.
        assert candidate==independent_full==conventional["lex_exact_prediction"]
        assert fitted["chosen_index_pair"]==conventional["lex_pair"]
        predictions={"candidate":candidate,"independent_bayesian32":conventional["bayes_prediction"],
                     "reference_bayesian12":reference12["bayes_prediction"],
                     "independent_full128":independent_full,
                     "same_data_sparse_delta":independent_full,
                     "naive_shared_only":prior}
        for name in sorted(predictions):
            frozen_pred_sha.update(bytes(predictions[name]))
        original[context]={"held":public.held_masks,"predictions":predictions,
            "original_consistent32":conventional["candidate_count"],
            "original_consistent12":reference12["candidate_count"],
            "first32_paid":len(feedback)}
        action_receipts.append({"context":context,"paid_actions":len(feedback),
          "consistent_12":reference12["candidate_count"],
          "consistent_32":conventional["candidate_count"],
          "search_space":fitted["pair_candidates"]})

    # ALL arms have frozen held predictions. Only NOW may source owner reveal
    # public DEV held-out consequences to this evaluator (never to fitting).
    for context in CONTEXTS:
        row=original[context]
        truth=owner.held_dev(context,row["held"])
        row["held_metrics"]={name:sum(a==b for a,b in zip(pred,truth))/len(truth)
                            for name,pred in row["predictions"].items()}
    initial_snapshot=model.snapshot()
    assert len(model.raw_weights())==144 and len(initial_snapshot)==180

    # Real shared-core changes. Each new core is learned from 128 paid source
    # onehot consequences. No additional context queries or old held labels
    # enter the model, and no per-context complete law is stored in its state.
    rebase_records=[]
    retained=[0,0,0]
    for stage in (1,2,3):
        observations=tuple((bit,owner.observe_core(stage,bit)) for bit in range(BITS))
        assert owner.core_charged(stage)==BITS
        for bit,y in observations:
            source_history_sha.update(bytes((stage,bit,y)))
        prev_core=model.base
        record=model.rebase(observations)
        assert prev_core!=model.base and record["shared_synapse_flips"]==2
        assert record["max_adapter_indices"]<=8
        for context in CONTEXTS:
            row=original[context]
            same=model.predict(context,row["held"])==row["predictions"]["candidate"]
            retained[stage-1]+=int(same)
            if not same:raise AssertionError("FKP09_COLLATERAL_CONTEXT_FORGETTING")
        rebase_records.append(dict(stage=stage,**record))
    cold=model.snapshot()
    restored=SharedCausalCore.restore(cold)
    assert restored.snapshot()==cold
    assert all(restored.predict(ctx,original[ctx]["held"])==original[ctx]["predictions"]["candidate"]
               for ctx in CONTEXTS)
    tampered=bytearray(cold);tampered[8]^=1
    try:SharedCausalCore.restore(bytes(tampered))
    except ValueError:pass
    else:raise AssertionError("FKP09_TAMPER_ACCEPTED")

    # Stage4 is a public FIXTURE-ONLY destructive shift: prove the bounded
    # learner rejects global over-capacity update atomically, never corrupts.
    fixture_owner=Source()
    stage4=tuple((bit,fixture_owner.observe_core(4,bit,fixture_shock=True))
                 for bit in range(BITS))
    before_shock=model.snapshot()
    try:model.rebase(stage4)
    except ValueError as e:
        if "CAPACITY_OVERFLOW" not in str(e):raise
        rejected=True
    else:rejected=False
    assert rejected and model.snapshot()==before_shock

    arms=sorted(next(iter(original.values()))["held_metrics"])
    means={name:statistics.mean(original[ctx]["held_metrics"][name] for ctx in CONTEXTS)
           for name in arms}
    diffs={b:means["candidate"]-means[b] for b in arms if b!="candidate"}
    ci={b:paired_ci([original[ctx]["held_metrics"]["candidate"]-
                     original[ctx]["held_metrics"][b] for ctx in CONTEXTS])
        for b in diffs}
    # The frozen 32-action estimator should be better than 12-action on real
    # unseen predictions. Even when the source passes, the fully informed
    # conventional sparse representation can tie this mechanism exactly.
    headroom=means["independent_bayesian32"]-means["reference_bayesian12"]
    source_gate=(means["independent_bayesian32"]>=0.98 and headroom>=0.05)
    engineering_gate=(all(n==len(CONTEXTS) for n in retained) and
        model.base!=learned_core and len(model.raw_weights())==144 and rejected)
    unique_benefit=(all(diffs[b]>=0.05 and ci[b][0]>0
        for b in ("independent_bayesian32","independent_full128","same_data_sparse_delta")))
    return {
        "schema":"fkp09-original-public-dev-shared-weight-repair.v1",
        "protected_primary_opened":False,"protected_negative_opened":False,
        "dev_contexts_consumed":len(CONTEXTS),
        "original_true_source_consequences":128*4+len(CONTEXTS)*CONTEXT_PAID,
        "held_outcomes_read_after_all_arms_sealed":True,
        "original_held_predictions_per_arm":len(CONTEXTS)*128,
        "total_retention_checks":len(CONTEXTS)*128*4,
        "original_predictions_sha256":frozen_pred_sha.hexdigest(),
        "source_history_sha256":source_history_sha.hexdigest(),
        "means_held_accuracy":means,"paired_context_ci95":ci,
        "candidate_minus_controls":diffs,
        "source_headroom_delta_12_to_32":headroom,
        "source_identifiability_gate_pass":source_gate,
        "retention_by_global_rebase":retained,
        "real_changed_shared_synapses":rebase_records,
        "engineered_memory_gate_pass":engineering_gate,
        "catastrophic_outside_capacity_rejected_atomically":rejected,
        "raw_direct_causal_weights_bytes":len(model.raw_weights()),
        "full_integrity_checkpoint_bytes":len(cold),
        "cold_checkpoint_sha256":hashlib.sha256(cold).hexdigest(),
        "full_conventional_16_independent_models_bytes":len(CONTEXTS)*16,
        "same_information_sparse_delta_bytes":len(model.raw_weights()),
        "original_source_core_actions":owner.core_charged(0),
        "revision_source_core_actions":[owner.core_charged(s) for s in (1,2,3)],
        "context_source_actions":[owner.context_charged(c) for c in CONTEXTS],
        "total_process_wall_dev_seconds":time.perf_counter()-started,
        "total_process_cpu_dev_seconds":time.process_time()-cpu_started,
        "whole_process_matched_conventional_cost":"UNVERIFIED",
        "independent_out_of_family_science":"UNVERIFIED",
        "scientific_superiority_pass":False,
        "science_unique_accuracy_gate_pass":unique_benefit,
        "classification":("DEV_NO_GO_EQUAL_INFORMATION_CONVENTIONAL_TIE"
            if source_gate and engineering_gate and not unique_benefit
            else "SOURCE_NO_HEADROOM" if not source_gate
            else "ENGINEERING_INVALID" if not engineering_gate
            else "DEV_SIGNAL_ONLY_NOT_INDEPENDENT_SCIENCE"),
        "context_receipts":action_receipts
    }

if __name__=="__main__":
    print(json.dumps(run_dev(),sort_keys=True,indent=2))
