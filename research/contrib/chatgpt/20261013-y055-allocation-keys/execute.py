"""Y055: prospective assignment-key stress test of frozen 50/50 sensor portfolios."""
import importlib.util
import hashlib
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y054-portfolio-replication"/"execute.py"
spec=importlib.util.spec_from_file_location("y54_pinned",SOURCE)
assert spec and spec.loader
y54=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y54)
y53=y54.y53
y52=y53.y52
y49=y53.y49
y50=y53.y50

DEV=tuple(range(2160,2168))
HELDOUT=tuple(range(2168,2184))
FAMILIES=((3,1,13),(5,13,7),(7,9,3),(11,15,5))
REGIMES=y53.REGIMES
POLICIES=y53.POLICIES
ARMS=("fixed_A","fixed_B","hedged_even","hedged_reversed","hedged_sha_rank")
HASH_TAG=b"y055-immutable-balance-v1:"

def allocation_map():
    ordered=sorted(HELDOUT,key=lambda s:hashlib.sha256(HASH_TAG+str(s).encode()).hexdigest())
    sha_a=set(ordered[:8])
    assignments={
        "hedged_even":{seed:("A" if seed%2==0 else "B") for seed in HELDOUT},
        "hedged_reversed":{seed:("B" if seed%2==0 else "A") for seed in HELDOUT},
        "hedged_sha_rank":{seed:("A" if seed in sha_a else "B") for seed in HELDOUT}}
    for name,mapping in assignments.items():
        assert sum(x=="A" for x in mapping.values())==8
        assert sum(x=="B" for x in mapping.values())==8
    assert assignments["hedged_even"]!=assignments["hedged_sha_rank"]
    return assignments

def run():
    alloc=allocation_map()
    originals=(y50.PROBES,y50.RESET_EPISODES)
    aggregate={name:{arm:{"mismatches":0,"reads":0,"quarantines":0,
                          "churn_reference":0,"churn_candidate":0}
                     for arm in ARMS} for name,_ in REGIMES}
    records=[]
    checks=0
    try:
        # Dev-only structural gate; no candidate schedule or threshold tuning.
        for name,onset in REGIMES:
            y49.install_environment(onset)
            for family in FAMILIES:
                for seed in DEV:
                    for schedule in ("A","B"):
                        result=y52.paired_evaluate(seed,family,POLICIES[0],schedule)
                        assert result["landmark_reads"]==10
                        checks+=1
        # First sealed cohort use; no repetitions or selection after outcomes.
        for name,onset in REGIMES:
            y49.install_environment(onset)
            for family in FAMILIES:
                for seed in HELDOUT:
                    for policy in POLICIES:
                        pair={s:y52.paired_evaluate(seed,family,policy,s)
                              for s in ("A","B")}
                        assert pair["A"]["landmark_reads"]==pair["B"]["landmark_reads"]==10
                        used={"fixed_A":pair["A"],"fixed_B":pair["B"]}
                        for key,assignment in alloc.items():
                            used[key]=pair[assignment[seed]]
                        for arm,row in used.items():
                            total=aggregate[name][arm]
                            total["mismatches"]+=row["errors"]
                            total["reads"]+=row["landmark_reads"]
                            total["quarantines"]+=row["quarantines"]
                            total["churn_reference"]+=row["churn_reference"]
                            total["churn_candidate"]+=row["churn_candidate"]
                        records.append({"regime":name,"family":family,"seed":seed,
                                        "policy":policy,"assignment_by_key":{
                                            key:assignment[seed] for key,assignment in alloc.items()},
                                        "paired_fixed_outcomes":pair})
    finally:
        y50.PROBES,y50.RESET_EPISODES=originals
        y49.restore_environment()
    risk={}
    for arm in ARMS:
        four=[aggregate[regime][arm]["mismatches"] for regime,_ in REGIMES
              if regime!="steady"]
        risk[arm]={"max_onset_mismatches":max(four),
                   "pooled_mismatches":sum(four),
                   "steady_mismatches":aggregate["steady"][arm]["mismatches"]}
    best_max=min(risk[arm]["max_onset_mismatches"] for arm in ("fixed_A","fixed_B"))
    best_pool=min(risk[arm]["pooled_mismatches"] for arm in ("fixed_A","fixed_B"))
    all_steady=all(risk[arm]["steady_mismatches"]==0 for arm in ARMS)
    for regime,_ in REGIMES:
        for arm in ARMS:
            assert aggregate[regime][arm]["reads"]==4*16*3*10
    gains={arm:{
        "worst_reduction_fraction":1-risk[arm]["max_onset_mismatches"]/best_max,
        "pooled_penalty_fraction":risk[arm]["pooled_mismatches"]/best_pool-1,
        "meets_frozen_gate":risk[arm]["max_onset_mismatches"]<=.75*best_max
                            and risk[arm]["pooled_mismatches"]<=1.10*best_pool}
        for arm in alloc}
    passed=sum(row["meets_frozen_gate"] for row in gains.values())
    if all_steady and passed==3: label="ASSIGNMENT_KEY_ROBUST"
    elif all_steady and passed>=2: label="PARTIAL_KEY_TRANSFER"
    else: label="OTHERWISE_NEGATIVE"
    return {"schema":"yggdrasil.y055-portfolio-assignment-robustness.v1",
            "parent_head":"c0dedfee971097e609342983b087d78de845cbff",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"families":FAMILIES,
            "balanced_assignments":alloc,"development_structural_checks":checks,
            "frozen_key_gains":gains,"risk_by_arm":risk,
            "aggregate_by_onset":aggregate,"heldout_records":records,
            "per_trial_landmark_observations":10,"model_calls":0,
            "claim_limit":"Synthetic population-level balanced-key risk sensitivity; not individual shock detection or independent real-world source transfer."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
