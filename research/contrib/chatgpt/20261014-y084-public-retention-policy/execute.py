"""Y084: bounded learned causal retention preference from public early state.

Train tiny (<9 bucket) decision tables only on development cohorts; freeze
a model selected on a separate development-validation cohort before heldout.
The candidate sees exclusively public probe episodes 0/1 to choose one of
three existing retention preference modes. No future truth or extra reads.
"""
import importlib.util,json
from pathlib import Path
p=Path(__file__).resolve().parent.parent/"20261014-y083-retention-selection"/"execute.py"
spec=importlib.util.spec_from_file_location("y083_pinned",p)
assert spec and spec.loader
y083=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y083)
m=y083.m
y082=y083.y082
PAIRS=y083.PAIRS
FAMILIES=y083.FAMILIES
REGIMES=y083.REGIMES
POLICIES=y083.POLICIES
TRAIN=tuple(range(17344,17352))
VALID=tuple(range(17376,17384))
SEALED=tuple(range(17408,17424))
MODES=("static","affine_bucket","drift_bucket","joint_bucket")
def observation_and_context(seed,family):
    public=y082.new_public_samples(seed,family)
    assert sum(len(v) for v in public.values())==10
    b0=public[0]["0"]
    a=(public[0]["1"]-b0)%16
    d=(public[1]["0"]-b0)%16
    assert a%2==1 and public[1]["1"]==(b0+d+a)%16
    return public,{"a_mod4":a%4,"d_mod4":d%4}
def bucket(context,mode):
    a,d=context["a_mod4"],context["d_mod4"]
    if mode=="static":return "all"
    if mode=="affine_bucket":return str(a)
    if mode=="drift_bucket":return str(d)
    if mode=="joint_bucket":return f"{a}:{d}"
    raise ValueError("UNKNOWN_MODE")
def candidate_cached(seed,family,policy,public):
    prior_sampler=m.y64.dual_public_samples
    prior_decoder=m.y61.y60.public_decoder
    try:
        m.y64.dual_public_samples=lambda s,f: public
        m.y61.y60.public_decoder=y082.public_decoder_any_pinned_public_address
        run=m.candidate(seed,family,policy,"dual_sentinel_decoder_corrected")
    finally:
        m.y61.y60.public_decoder=prior_decoder
        m.y64.dual_public_samples=prior_sampler
    assert run["public_scalar_reads"]==10
    return run
def score(truth,run):
    mismatch=churn=calls=writes=illegal=0
    first=None
    for ref,row in zip(truth["rows"],run["rows"]):
        assert ref["episode"]==row["episode"]
        assert len(row["physical_assignment_evaluator_only"])==7
        assert row["candidate_retained_cache_occupancy"]<=9
        mismatch+=int(any(ref["physical_assignment"][k]!=row[
            "physical_assignment_evaluator_only"][k] for k in ref["physical_assignment"]))
        churn+=row["physical_churn_evaluator_only"]
        calls+=row["matching_search_calls"]
        writes+=row["candidate_retained_writes"]
        illegal+=row["illegal_physical_assignments"]
        if row["public_detected_swap_first_episode"] is not None:
            first=row["public_detected_swap_first_episode"]
    assert illegal==0
    return {"mismatch_episodes":mismatch,"physical_churn":churn,
            "search_calls":calls,"retained_writes":writes,"illegal":illegal,
            "public_reads":10,"first_detection":first}
def collect(seeds):
    records=[]
    try:
        for pair in PAIRS:
            for regime,onset in REGIMES:
                m.y58.install_transposition(onset,pair,{"anchor_pair_checks":0})
                for family in FAMILIES:
                    for seed in seeds:
                        public,ctx=observation_and_context(seed,family)
                        cases={}
                        for policy in POLICIES:
                            truth=m.y50.evaluate(seed,policy,"canonical","continue",family)
                            run=candidate_cached(seed,family,policy,public)
                            cases[policy]=score(truth,run)
                        records.append({"pair":pair,"regime":regime,"family":family,
                                        "seed":seed,"early_public_bucket":ctx,"arms":cases})
                m.y49.restore_environment()
    finally:m.y49.restore_environment()
    assert len(records)==2*3*4*len(seeds)
    return records
def objective(x):
    return 100*x["mismatch_episodes"]+x["physical_churn"]+.01*x["search_calls"]
def fit_tables(records):
    tables={}
    for mode in MODES:
        sums={}
        for r in records:
            b=bucket(r["early_public_bucket"],mode)
            entry=sums.setdefault(b,{p:{"mismatch_episodes":0,"physical_churn":0,"search_calls":0} for p in POLICIES})
            for policy,v in r["arms"].items():
                for metric in entry[policy]:entry[policy][metric]+=v[metric]
        tables[mode]={b:min(POLICIES,key=lambda p:(objective(v[p]),p))
                      for b,v in sums.items()}
        assert len(tables[mode])<=8
    return tables
def choose(context,mode,table):
    return table.get(bucket(context,mode),"quorum2")
def sum_trial(rows,mode,table):
    q={"mismatch_episodes":0,"physical_churn":0,"search_calls":0}
    for r in rows:
        policy=choose(r["early_public_bucket"],mode,table)
        a=r["arms"][policy]
        for key in q:q[key]+=a[key]
    return q
def train_and_select():
    development=collect(TRAIN)
    tables=fit_tables(development)
    validation=collect(VALID)
    scoreboard={mode:sum_trial(validation,mode,tables[mode]) for mode in MODES}
    chosen=min(MODES,key=lambda mode:(objective(scoreboard[mode]),mode))
    return chosen,tables,scoreboard
def run():
    selected,tables,validation=train_and_select()
    records=collect(SEALED)
    group_sums={}
    observed={"selected":{"mismatch_episodes":0,"physical_churn":0,"search_calls":0,
                         "retained_writes":0,"illegal":0,"public_reads":0,"detections":0},
              "quorum2":{"mismatch_episodes":0,"physical_churn":0,"search_calls":0,
                         "retained_writes":0,"illegal":0,"public_reads":0,"detections":0}}
    for r in records:
        key=f"{r['pair'][0]}_{r['pair'][1]}:{r['regime']}"
        g=group_sums.setdefault(key,{name:{field:0 for field in observed[name]}
                                      for name in observed})
        selected_policy=choose(r["early_public_bucket"],selected,tables[selected])
        r["selected_policy"]=selected_policy
        for name,p in (("selected",selected_policy),("quorum2","quorum2")):
            vals=r["arms"][p]
            for target in (observed[name],g[name]):
                for k in vals:
                    if k!="first_detection":target[k]+=vals[k]
                target["detections"]+=int(vals["first_detection"] is not None)
    assert len(records)==2*3*4*16==384
    for group in group_sums.values():
        assert all(v["public_reads"]==4*16*10 and v["illegal"]==0 for v in group.values())
    steady=all(group_sums[f"{a}_{b}:steady"][label]["mismatch_episodes"]==0 and
               group_sums[f"{a}_{b}:steady"][label]["detections"]==0
               for a,b in PAIRS for label in observed)
    origin=observed["quorum2"]
    trial=observed["selected"]
    improvement=(origin["mismatch_episodes"]-trial["mismatch_episodes"])/max(1,origin["mismatch_episodes"])
    churn_ok=trial["physical_churn"]<=1.05*max(1,origin["physical_churn"])
    calls_ok=trial["search_calls"]<=1.10*max(1,origin["search_calls"])
    local_safe=all(g["selected"]["mismatch_episodes"]<=g["quorum2"]["mismatch_episodes"]
                   for g in group_sums.values())
    if not steady: classification="CONDITIONAL_POLICY_STEADY_FAILURE"
    elif improvement>=.10 and churn_ok and calls_ok and local_safe:
        classification="DEVELOPMENT_LEARNED_PUBLIC_MEMORY_POLICY_GAIN"
    elif improvement>=.05:
        classification="PARTIAL_CONDITIONAL_MEMORY_GAIN_OR_COST"
    else:classification="NO_CONDITIONAL_MEMORY_POLICY_GAIN"
    return {"schema":"yggdrasil.y084-bounded-public-state-policy.v1",
            "parent_head":"2fd733b3c543324c6d42cc07c8b286ed5d9ec8d3",
            "classification":classification,
            "development_seeds":TRAIN,"validation_seeds":VALID,
            "sealed_heldout_seeds":SEALED,"pairs":PAIRS,"regimes":REGIMES,
            "candidate_modes":MODES,"chosen_mode":selected,"frozen_policy_table":tables[selected],
            "validation_scores":validation,"heldout_group_totals":group_sums,
            "heldout_totals":observed,"improvement_vs_quorum2":improvement,
            "churn_ok":churn_ok,"matching_cost_ok":calls_ok,"local_safe":local_safe,
            "steady_safe":steady,"sealed_records":records,
            "policy_table_entries":len(tables[selected]),"active":7,"retained_limit":9,
            "public_read_budget":10,"model_calls":0,"accepted_ref_mutation":False,
            "claim_limit":"Development-learned bounded public-context table selecting existing retained-preference policies. Only episodes0/1 visible for decision. Not neural cognitive memory, broad cognition or RSI."}
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))
