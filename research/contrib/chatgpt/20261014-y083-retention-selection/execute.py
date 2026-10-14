"""Y083: development-selected bounded retention preference under unchanged 7/9 memory."""
import importlib.util,json
from pathlib import Path
p=Path(__file__).resolve().parent.parent/"20261014-y082-late-window"/"execute.py"
spec=importlib.util.spec_from_file_location("y082_frozen",p)
assert spec and spec.loader
y082=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y082)
m=y082.m
TRAIN=tuple(range(16128,16136))
SEALED=tuple(range(16160,16176))
PAIRS=y082.PAIRS
FAMILIES=y082.FAMILIES
REGIMES=y082.REGIMES
POLICIES=("matched_sham","full","quorum2")
assert set(POLICIES)==set(y082.POLICIES)
def trial_stats(seed,family,policy,ref):
    # Each candidate has 7 active/<=9 retained and exactly ten public reads.
    run=y082.new_candidate(seed,family,policy,True)
    assert run["public_scalar_reads"]==10 and len(run["rows"])==8
    mismatches=churn=calls=writes=illegal=0
    first=None
    for actual,row in zip(ref["rows"],run["rows"]):
        assert actual["episode"]==row["episode"]
        assert len(row["physical_assignment_evaluator_only"])==7
        assert row["candidate_retained_cache_occupancy"]<=9
        mismatches+=int(any(actual["physical_assignment"][k]!=row[
            "physical_assignment_evaluator_only"][k] for k in actual["physical_assignment"]))
        churn+=row["physical_churn_evaluator_only"]
        calls+=row["matching_search_calls"]
        writes+=row["candidate_retained_writes"]
        illegal+=row["illegal_physical_assignments"]
        observed=row["public_detected_swap_first_episode"]
        if observed is not None:first=observed
    assert illegal==0
    return {"mismatch_episodes":mismatches,"physical_churn":churn,
            "search_calls":calls,"retained_writes":writes,
            "illegal":illegal,"public_reads":10,"first_detection":first}
def train_selection():
    metrics={policy:{"mismatch_episodes":0,"physical_churn":0,
                     "search_calls":0,"retained_writes":0,
                     "public_reads":0,"trials":0} for policy in POLICIES}
    try:
        for pair in PAIRS:
            for name,onset in REGIMES:
                m.y58.install_transposition(onset,pair,{"anchor_pair_checks":0})
                for family in FAMILIES:
                    for seed in TRAIN:
                        for policy in POLICIES:
                            truth=m.y50.evaluate(seed,policy,"canonical","continue",family)
                            s=trial_stats(seed,family,policy,truth)
                            row=metrics[policy]
                            for field in ("mismatch_episodes","physical_churn",
                                          "search_calls","retained_writes","public_reads"):
                                row[field]+=s[field]
                            row["trials"]+=1
                m.y49.restore_environment()
    finally:m.y49.restore_environment()
    assert all(x["trials"]==2*3*4*8 for x in metrics.values())
    # Predetermined absolute physical-error-first objective, with bounded
    # churn/search-cost tiebreaks, then lexical tie break.
    def key(policy):
        x=metrics[policy]
        return (100*x["mismatch_episodes"]+x["physical_churn"]+
                .01*x["search_calls"],x["mismatch_episodes"],
                x["physical_churn"],policy)
    return min(POLICIES,key=key),metrics
def run():
    selected,dev=train_selection()
    records=[]
    groups={}
    totals={policy:{"mismatch_episodes":0,"physical_churn":0,
                   "search_calls":0,"retained_writes":0,
                   "public_reads":0,"detections":0,"illegal":0}
            for policy in POLICIES}
    try:
        for pair in PAIRS:
            for regime,onset in REGIMES:
                name=f"{pair[0]}_{pair[1]}:{regime}"
                m.y58.install_transposition(onset,pair,{"anchor_pair_checks":0})
                group={policy:{"mismatch_episodes":0,"physical_churn":0,
                              "search_calls":0,"retained_writes":0,
                              "public_reads":0,"detections":0,"illegal":0}
                       for policy in POLICIES}
                for family in FAMILIES:
                    for seed in SEALED:
                        row={"pair":pair,"regime":regime,"family":family,
                             "seed":seed,"arms":{},"selected_policy":selected}
                        for policy in POLICIES:
                            reference=m.y50.evaluate(seed,policy,"canonical","continue",family)
                            stats=trial_stats(seed,family,policy,reference)
                            row["arms"][policy]=stats
                            for aggregate in (group[policy],totals[policy]):
                                for key in ("mismatch_episodes","physical_churn","search_calls",
                                            "retained_writes","public_reads","illegal"):
                                    aggregate[key]+=stats[key]
                                aggregate["detections"]+=int(stats["first_detection"] is not None)
                        records.append(row)
                assert all(g["public_reads"]==4*16*10 and g["illegal"]==0
                           for g in group.values())
                groups[name]=group
                m.y49.restore_environment()
    finally:m.y49.restore_environment()
    assert len(records)==2*3*4*16==384
    steady=all(groups[f"{a}_{b}:steady"][p]["mismatch_episodes"]==0
               and groups[f"{a}_{b}:steady"][p]["detections"]==0
               for a,b in PAIRS for p in POLICIES)
    ref=totals["quorum2"]
    candidate=totals[selected]
    relative_gain=((ref["mismatch_episodes"]-candidate["mismatch_episodes"])
                   / max(1,ref["mismatch_episodes"]))
    no_group_regression=all(g[selected]["mismatch_episodes"]<=g["quorum2"]["mismatch_episodes"]
                            for g in groups.values())
    cost_ok=candidate["physical_churn"]<=1.05*max(1,ref["physical_churn"])
    if not steady:label="RETENTION_NULL_SAFETY_FAILURE"
    elif selected!="quorum2" and relative_gain>=.05 and no_group_regression and cost_ok:
        label="DEV_SELECTED_RETENTION_POLICY_GENERALIZED"
    elif relative_gain>0:
        label="PARTIAL_RETENTION_POLICY_GAIN_OR_COST"
    else:label="NO_RETENTION_POLICY_GAIN"
    return {"schema":"yggdrasil.y083-development-policy-selection.v1",
            "parent_head":"d17a95d2e7f16dc3ca8daa60e8f652267475b134",
            "classification":label,"development_seeds":TRAIN,
            "sealed_heldout_seeds":SEALED,"pairs":PAIRS,
            "regimes":REGIMES,"families":FAMILIES,
            "policies":POLICIES,"selected_policy":selected,
            "development_metrics":dev,"selected_vs_quorum2_gain":relative_gain,
            "selected_vs_quorum2_cost_ok":cost_ok,
            "no_group_regression":no_group_regression,
            "steady_null_safe":steady,"groups":groups,"aggregate":totals,
            "sealed_trial_records":records,"active":7,"retained_limit":9,
            "scalar_reads_per_trial":10,"model_calls":0,
            "accepted_ref_mutation":False,
            "claim_limit":"Development-selected one-of-three fixed memory preference policies with no extra persistent state; not learned local-to-retained transformation, autonomous memory or RSI."}
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))
