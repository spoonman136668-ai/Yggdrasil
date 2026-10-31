"""Eight-fold leave-one-metadata-profile-out retention generalization check.

Each fold withholds one of eight combinations of evidence/error/contradiction
during FIT. Learned weights transfer into a fresh store. The withheld profile
appears only in TRANSFER; no transfer labels are fed back.
"""
from __future__ import annotations
import json
from learned_memory_allocator import LearnedMemoryAllocator, ACTIVE
from learned_retention_eval import PROFILES, representation


def run():
    folds=[]
    for heldout_index, heldout_profile in enumerate(PROFILES):
        fit=LearnedMemoryAllocator()
        fit_profiles=[(i,p) for i,p in enumerate(PROFILES) if i!=heldout_index]
        for epoch in range(30):
            for i,(evidence,error,contradiction,label) in fit_profiles:
                key=f"fit-{i}"
                if not any(m.occupied and m.key==key for m in fit.memories):
                    fit.insert(key,representation(i),evidence_count=evidence,
                               prediction_error=error,contradiction_rate=contradiction)
                fit.mark_use(key)
                fit.observe_task_outcome(key,float(label))
        transfer=LearnedMemoryAllocator()
        transfer.weights=list(fit.weights)
        cohort=[]
        for repeat in range(2):
            for i,(evidence,error,contradiction,label) in enumerate(PROFILES):
                key=f"fold-{heldout_index}-eval-{repeat}-{i}"
                transfer.insert(key,representation(200+repeat*8+i),
                                 evidence_count=evidence,prediction_error=error,
                                 contradiction_rate=contradiction)
                cohort.append({"key":key,"label":label,"evidence":evidence,"profile":i})
        by_key={m.key:m for m in transfer.memories if m.occupied}
        learned={m.key for m in transfer.memories if m.occupied and m.active}
        recency={r["key"] for r in sorted(cohort,key=lambda r:by_key[r["key"]].last_used,reverse=True)[:ACTIVE]}
        evidence={r["key"] for r in sorted(cohort,key=lambda r:(-r["evidence"],r["key"]))[:ACTIVE]}
        def score(keys):
            hits=sum(r["label"] for r in cohort if r["key"] in keys)
            return {"hits":hits,"precision_at_7":hits/ACTIVE}
        heldout=next(r for r in cohort if r["profile"]==heldout_index)
        folds.append({
            "heldout_profile_index":heldout_index,
            "heldout_label":heldout_profile[3],
            "fit_profiles":len(fit_profiles),
            "transfer_feedback_events":transfer.feedback_count,
            "learned":score(learned),
            "fixed_recency":score(recency),
            "evidence_only":score(evidence),
            "heldout_profile_selected":heldout["key"] in learned,
        })
    return {
        "schema":"yggdrasil.mr32.leave-one-profile-out.v1",
        "classification":"SYNTHETIC_PROFILE_HOLDOUT_MECHANISM_DIAGNOSTIC_NOT_SCIENTIFIC_EFFICACY",
        "folds":folds,
        "summary":{
            "folds":len(folds),
            "learned_mean_precision_at_7":sum(f["learned"]["precision_at_7"] for f in folds)/len(folds),
            "recency_mean_precision_at_7":sum(f["fixed_recency"]["precision_at_7"] for f in folds)/len(folds),
            "evidence_mean_precision_at_7":sum(f["evidence_only"]["precision_at_7"] for f in folds)/len(folds),
            "heldout_profile_selected_count":sum(f["heldout_profile_selected"] for f in folds),
            "transfer_feedback_events":sum(f["transfer_feedback_events"] for f in folds),
        },
        "limits":[
            "All folds use the same known synthetic majority-rule generator.",
            "The withheld combination is novel only as a metadata profile, not as a new task family or causal mechanism.",
            "One deterministic order per fold; no confidence interval or broad population claim.",
            "Scorer metadata and linear function class are hand-designed.",
            "No authentic task reward, causal decisions, cold-restart interference, or unfamiliar environment.",
        ],
    }


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2,allow_nan=False))
