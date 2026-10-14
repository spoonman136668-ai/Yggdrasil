"""Y086: cost-constrained development-learned public conditional retention.

Learn a four-key policy map from a public affine observation. Optimize among
81 mappings with deterministic grouped error/churn/search constraints during
development; validate and freeze before sealed first use. No evaluator truth
enters the deployed public-key policy function.
"""
import importlib.util,itertools,json
from pathlib import Path
p=Path(__file__).resolve().parent.parent/"20261014-y085-public-affine-drift"/"execute.py"
spec=importlib.util.spec_from_file_location("y085_frozen",p)
assert spec and spec.loader
prior=importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
POLICIES=prior.POLICIES
TRAIN=tuple(range(18816,18824))
VALID=tuple(range(18848,18856))
SEALED=tuple(range(18880,18896))
PAIRS=prior.PAIRS
REGIMES=prior.REGIMES
BUCKETS=("3","7","11","15")
def bucket(row):
    return str(row["early_public_bucket"]["a_mod16"])
def evaluate(records,policy_table):
    sums={k:{"mismatch_episodes":0,"physical_churn":0,"search_calls":0,
             "public_reads":0,"illegal":0,"detections":0} for k in ("learned","quorum2")}
    by_group={}
    counts={p:0 for p in POLICIES}
    for r in records:
        choice=policy_table.get(bucket(r),"quorum2")
        assert choice in POLICIES
        counts[choice]+=1
        k=f"{r['pair'][0]}_{r['pair'][1]}:{r['regime']}"
        group=by_group.setdefault(k,{name:{x:0 for x in sums[name]} for name in sums})
        for name,arm in (("learned",choice),("quorum2","quorum2")):
            stats=r["arms"][arm]
            for target in (sums[name],group[name]):
                for field in ("mismatch_episodes","physical_churn","search_calls",
                              "public_reads","illegal"):
                    target[field]+=stats[field]
                target["detections"]+=int(stats["first_detection"] is not None)
    return sums,by_group,counts
def safe(stats,groups):
    learned,base=stats["learned"],stats["quorum2"]
    return (learned["physical_churn"]<=1.05*max(1,base["physical_churn"])
            and learned["search_calls"]<=1.10*max(1,base["search_calls"])
            and all(group["learned"]["mismatch_episodes"]<=
                    group["quorum2"]["mismatch_episodes"] for group in groups.values())
            and all(group[n]["illegal"]==0 for group in groups.values() for n in group))
def learn():
    development=prior.collect(TRAIN)
    assert set(bucket(r) for r in development)==set(BUCKETS)
    proposed=[]
    for combo in itertools.product(POLICIES,repeat=len(BUCKETS)):
        table=dict(zip(BUCKETS,combo))
        totals,groups,counts=evaluate(development,table)
        if safe(totals,groups):
            proposed.append((totals["learned"]["mismatch_episodes"],totals["learned"]["physical_churn"],
                             totals["learned"]["search_calls"],combo))
    # Quorum2 is always feasible: bounded no-op fallback.
    baseline=("quorum2",)*len(BUCKETS)
    assert any(v[3]==baseline for v in proposed)
    proposed.sort()
    shortlisted=[p[3] for p in proposed[:8]]
    if baseline not in shortlisted:shortlisted.append(baseline)
    validation=prior.collect(VALID)
    best=None
    for combo in shortlisted:
        table=dict(zip(BUCKETS,combo))
        totals,groups,_=evaluate(validation,table)
        if not safe(totals,groups):continue
        row=(totals["learned"]["mismatch_episodes"],totals["learned"]["physical_churn"],
             totals["learned"]["search_calls"],combo)
        if best is None or row<best:best=row
    frozen=baseline if best is None else best[-1]
    return dict(zip(BUCKETS,frozen)),len(proposed),len(shortlisted),best
def run():
    table,eligible,considered,development_best=learn()
    original=prior.collect(SEALED)
    summary,groups,counts=evaluate(original,table)
    assert len(original)==384 and all(x in BUCKETS for x in (bucket(r) for r in original))
    selected=summary["learned"];baseline=summary["quorum2"]
    improvement=(baseline["mismatch_episodes"]-selected["mismatch_episodes"])/max(1,baseline["mismatch_episodes"])
    group_safe=safe(summary,groups)
    diverse=sum(v>0 for v in counts.values())>=2
    steady=all(groups[f"{a}_{b}:steady"][n]["mismatch_episodes"]==0
               and groups[f"{a}_{b}:steady"][n]["detections"]==0
               for a,b in PAIRS for n in ("learned","quorum2"))
    if not steady:label="CONSTRAINED_RETENTION_STEADY_FAILURE"
    elif not diverse:label="CONSTRAINED_RETENTION_POLICY_COLLAPSED"
    elif improvement>=.10 and group_safe:label="SAFE_CONDITIONAL_RETENTION_GAIN"
    elif improvement>=.05:label="PARTIAL_CONDITIONAL_RETENTION_COST"
    else:label="NO_CONSTRAINED_RETENTION_GAIN"
    for r in original:r["learned_policy"]=table[bucket(r)]
    return {"schema":"yggdrasil.y086-cost-constrained-public-retention.v1",
            "parent_head":"72c95e1e43ffa690071fef3f6cae053f7e7baac8",
            "classification":label,"training_seeds":TRAIN,"validation_seeds":VALID,
            "sealed_heldout_seeds":SEALED,"public_buckets":BUCKETS,
            "frozen_mapping":table,"development_feasible_mappings":eligible,
            "development_shortlist_count":considered,"development_best":development_best,
            "selected_policy_counts":counts,"selection_diverse":diverse,
            "group_safe":group_safe,"steady_safe":steady,"improvement_vs_quorum2":improvement,
            "heldout_totals":summary,"heldout_groups":groups,
            "heldout_records":original,"table_entries":len(table),
            "public_reads_per_trial":10,"active":7,"retained_limit":9,
            "model_calls":0,"accepted_ref_mutation":False,
            "claim_limit":"Four public affine-key conditional policy choices optimized with dev-only physical ground truth; bounded static controller memory and unchanged 7-active/9-retained task memory. Not learned recurrent cognition or RSI."}
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))
