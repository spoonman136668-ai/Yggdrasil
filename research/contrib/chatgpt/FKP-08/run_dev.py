"""FKP-08 precommitted development assay (paid causal evidence; no protected first-use).

DO NOT rerun the original development cohort as fresh scientific evidence.
All predicted 128-state vectors are sealed before invoking DEV-only scorer.
"""
from __future__ import annotations
import hashlib
import json
import random
import statistics
import time
from source import Source,CONTEXTS,STATES,PAID,MOTIF_MASKS
from model import Memory,CANDIDATES,CANDIDATE_DIFF,standard_baseline_sizes

def independent_exact_marginal(previous:int,paid:tuple[tuple[int,int],...],
                               held:tuple[int,...])->tuple[int,...]:
    """Strong conventional posterior voting on all minimum-error motif pairs.

    Given exactly the same parent predictions and public paid outcomes; no
    source-private pair identity or held true labels.
    """
    evidence_mask=sum(1<<x for x,y in paid)
    change_mask=sum((((previous>>x)&1)^y)<<x for x,y in paid)
    best=17
    posterior=[]
    for pair,change in zip(CANDIDATES,CANDIDATE_DIFF):
        missing=((change^change_mask)&evidence_mask).bit_count()
        if missing<best:best=missing;posterior=[change]
        elif missing==best:posterior.append(change)
    if not posterior:raise AssertionError("FKP08_CONVENTIONAL_NO_HYPOTHESES")
    output=[]
    for x in held:
        ones=sum(((previous^v)>>x)&1 for v in posterior)
        output.append(int(ones*2>len(posterior)))
    return tuple(output)

def paired_ci(d:list[float])->list[float]:
    rnd=random.Random(9090)
    n=len(d)
    points=sorted(sum(d[rnd.randrange(n)] for _ in range(n))/n for _ in range(10000))
    return [points[249],points[9749]]

def run()->dict:
    t0=time.perf_counter()
    owner=Source()
    native=Memory()
    acquired=0
    source_digest=hashlib.sha256()
    for context in CONTEXTS:
        view=owner.view(context,0)
        paid=tuple((x,owner.observe(context,0,x)) for x in view.choices)
        assert len(paid)==STATES and owner.charged(context,0)==STATES
        for x,y in paid:source_digest.update(context.to_bytes(2,"big")+bytes((x,y)))
        native.set_base(context,paid)
        acquired+=len(paid)

    base_elapsed=time.perf_counter()-t0
    predicted=[]
    receipts=[]
    before={}
    for version in (1,2,3):
        for context in CONTEXTS:
            view=owner.view(context,version)
            assert not set(view.choices)&set(view.held)
            assert len(view.choices)==len(view.held)==128
            # All methods see the SAME 16 original paid outcomes.
            previous=native.rule(context,version-1)
            actions=view.choices[:PAID]
            paid=tuple((x,owner.observe(context,version,x)) for x in actions)
            assert owner.charged(context,version)==PAID
            fit=native.fit(context,version,paid)
            direct=native.predict(context,version,view.held)
            marginal=independent_exact_marginal(previous,paid,view.held)
            carry=tuple((previous>>x)&1 for x in view.held)
            # The strong same-informed conventional delta table has EXACTLY
            # the same information/operations and must tie native direct model.
            conventional_delta=direct
            predicted.append((context,version,view.held,direct,marginal,carry,
                              conventional_delta))
            receipts.append({"context":context,"version":version,
                "paid_actions":len(paid),
                "fit_mismatches":fit["best_mismatches"],
                "compatible_patches":fit["consistent_hypotheses"]})
            for old_v in range(version):
                old_key=(context,old_v)
                if old_key not in before:
                    old_view=owner.view(context,0 if old_v==0 else old_v)
                    states=tuple(range(256)) if old_v==0 else old_view.held
                    before[old_key]=(states,native.predict(context,old_v,states))
        # All previous versions remain recoverable after adding new evidence.
        for (context,v),(states,old_pred) in before.items():
            if native.predict(context,v,states)!=old_pred:
                raise AssertionError("FKP08_COLLATERAL_FORGETTING")

    # ALL candidate and conventional predictions are now sealed.
    pred_hash=hashlib.sha256()
    for _,_,_,direct,marginal,carry,delta in predicted:
        for values in (direct,marginal,carry,delta):
            pred_hash.update(bytes(values))
    outcome_rows=[]
    for context,version,held,direct,marginal,carry,delta in predicted:
        truth=Source().held_dev(context,version,held)
        outcome_rows.append({"context":context,"version":version,
            "candidate":sum(a==b for a,b in zip(direct,truth))/128,
            "exact_marginal":sum(a==b for a,b in zip(marginal,truth))/128,
            "carry_forward":sum(a==b for a,b in zip(carry,truth))/128,
            "same_information_delta":sum(a==b for a,b in zip(delta,truth))/128})

    snapshot=native.snapshot()
    cold=Memory.restore(snapshot)
    assert cold.snapshot()==snapshot
    for (context,v),(states,old_pred) in before.items():
        assert cold.predict(context,v,states)==old_pred
    broken=bytearray(snapshot)
    broken[4]^=1
    try:Memory.restore(bytes(broken))
    except ValueError:pass
    else:raise AssertionError("FKP08_TAMPER_ACCEPTED")
    strong_baseline_sizes=standard_baseline_sizes(native)
    totals={arm:statistics.mean(r[arm] for r in outcome_rows)
            for arm in ("candidate","exact_marginal","carry_forward","same_information_delta")}
    grouped={}
    for context in CONTEXTS:
        rows=[r for r in outcome_rows if r["context"]==context]
        grouped[context]={arm:statistics.mean(r[arm] for r in rows) for arm in totals}
    diffs={against:statistics.mean(r["candidate"]-r[against] for r in outcome_rows)
           for against in ("exact_marginal","carry_forward","same_information_delta")}
    ci={against:paired_ci([grouped[context]["candidate"]-grouped[context][against]
                           for context in CONTEXTS])
        for against in diffs}
    # Scientific precommitted condition also requires whole-process 2x cost,
    # which a same-info conventional delta scheme ties by construction.
    science_gain=(diffs["exact_marginal"]>=0.05 and ci["exact_marginal"][0]>0
                  and diffs["same_information_delta"]>=0.05
                  and ci["same_information_delta"][0]>0)
    return {"schema":"fkp08.source-dev-shared-memory-result.v1",
        "protected_primary_opened":False,"protected_negative_opened":False,
        "original_dev_cohort_consumed":True,"baseline_original_observations":acquired,
        "genuine_revision_interventions":32*3*PAID,
        "revisions_scored":len(outcome_rows),"held_per_revision":128,
        "actual_held_predictions_per_arm":len(outcome_rows)*128,
        "source_history_digest":source_digest.hexdigest(),
        "prediction_commitment_sha256":pred_hash.hexdigest(),
        "mean_exact_held_accuracy":totals,
        "paired_context_bootstrap_ci95":ci,
        "candidate_accuracy_differences":diffs,
        "all_previous_versions_bit_exact_after_updates":True,
        "cold_restore_bit_exact":True,"snapshot_tamper_rejected":True,
        "raw_direct_weights_bytes":len(native.raw_weights()),
        "full_checkpoint_bytes":len(snapshot),
        "compressed_strong_conventional_controls":strong_baseline_sizes,
        "original_base_acquisition_wall_seconds_dev":base_elapsed,
        "total_pipeline_wall_seconds_dev":time.perf_counter()-t0,
        "fully_trained_independent_native_control":"UNVERIFIED",
        "whole_process_matched_cost":"UNVERIFIED",
        "preset_unique_science_accuracy_gate_pass":science_gain,
        "classification":"DEV_NO_GO_EQUAL_INFORMATION_CONVENTIONAL_TIE" if not science_gain else "DEV_SIGNAL_ONLY_NOT_SCIENCE",
        "science_pass":False,
        "records":receipts,
        "per_context_revision_accuracy":outcome_rows}
if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
