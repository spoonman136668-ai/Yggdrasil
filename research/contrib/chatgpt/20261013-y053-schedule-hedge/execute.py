"""Y053: precommitted balanced diversification across fixed landmark schedules."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y052-learned-probe"/"execute.py"
spec=importlib.util.spec_from_file_location("y52_pinned",SOURCE)
assert spec and spec.loader
y52=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y52)
y50=y52.y50
y49=y52.y49

DEV=tuple(range(1984,1992))
HELDOUT=tuple(range(1992,2008))
FAMILIES=((3,9,1),(5,3,11),(7,1,7),(11,5,9))
REGIMES=(("steady",None),("onset4",4),("onset5",5),
         ("onset6",6),("onset7",7))
POLICIES=y52.POLICIES
SCHEDULES=y52.SCHEDULES
ARMS=("fixed_A","fixed_B","hedged_50_50")


def selected_schedule(seed):
    # This is an exogenous schedule lottery: neither a learned selector nor
    # an observed-future-shock predictor. No hidden onset controls selection.
    return "A" if seed%2==0 else "B"


def run():
    original_probes=y50.PROBES
    original_resets=y50.RESET_EPISODES
    aggregate={name:{arm:{"mismatches":0,"landmark_reads":0,
                          "quarantines":0,"churn_reference":0,
                          "churn_candidate":0}
                     for arm in ARMS} for name,_ in REGIMES}
    records=[]
    development_invariant_checks=0
    try:
        # Structural controls evaluated prospectively on separate development
        # seeds; no tuning/selection uses their outcomes.
        for name,onset in REGIMES:
            y49.install_environment(onset)
            for family in FAMILIES:
                for seed in DEV:
                    policy=POLICIES[0]
                    a=y52.paired_evaluate(seed,family,policy,"A")
                    b=y52.paired_evaluate(seed,family,policy,"B")
                    assert a["landmark_reads"]==b["landmark_reads"]==10
                    development_invariant_checks+=1

        # Single heldout first use with exact matched control/sensor budget.
        for name,onset in REGIMES:
            y49.install_environment(onset)
            for family in FAMILIES:
                for seed in HELDOUT:
                    chosen=selected_schedule(seed)
                    for policy in POLICIES:
                        fixed={s:y52.paired_evaluate(seed,family,policy,s) for s in SCHEDULES}
                        used={"fixed_A":fixed["A"],"fixed_B":fixed["B"],
                              "hedged_50_50":fixed[chosen]}
                        for arm,row in used.items():
                            a=aggregate[name][arm]
                            a["mismatches"]+=row["errors"]
                            a["landmark_reads"]+=row["landmark_reads"]
                            a["quarantines"]+=row["quarantines"]
                            a["churn_reference"]+=row["churn_reference"]
                            a["churn_candidate"]+=row["churn_candidate"]
                        records.append({
                            "regime":name,"family":family,"seed":seed,
                            "policy":policy,"hedge_schedule":chosen,
                            "paired_fixed_results":fixed})
    finally:
        y50.PROBES=original_probes
        y50.RESET_EPISODES=original_resets
        y49.restore_environment()
    counts={s:sum(int(selected_schedule(seed)==s) for seed in HELDOUT)
            for s in SCHEDULES}
    assert counts=={"A":8,"B":8}
    for regime,_ in REGIMES:
        for arm in ARMS:
            assert aggregate[regime][arm]["landmark_reads"]==4*16*3*10
    baseline={}
    for arm in ARMS:
        losses=[aggregate[name][arm]["mismatches"] for name,_ in REGIMES if name!="steady"]
        baseline[arm]={"worst_onset":max(losses),
                       "pooled_four_onsets":sum(losses),
                       "steady_mismatches":aggregate["steady"][arm]["mismatches"]}
    hedge=baseline["hedged_50_50"]
    minworst=min(baseline[a]["worst_onset"] for a in ("fixed_A","fixed_B"))
    minpooled=min(baseline[a]["pooled_four_onsets"] for a in ("fixed_A","fixed_B"))
    steady_zero=all(baseline[a]["steady_mismatches"]==0 for a in ARMS)
    if (steady_zero and hedge["worst_onset"]<=.75*minworst and
        hedge["pooled_four_onsets"]<=1.10*minpooled):
        label="PORTFOLIO_WORST_CASE_GAIN"
    elif (steady_zero and hedge["worst_onset"]<=.90*minworst and
          hedge["pooled_four_onsets"]<=1.20*minpooled):
        label="PARETO_PARTIAL"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y053-frozen-probe-diversification.v1",
            "parent_head":"7338fee28e11ee2d2a5c3487ad9f21ccd94b3d21",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"families":FAMILIES,
            "onset_regimes":[name for name,_ in REGIMES],
            "hedge_balanced_schedule_counts":counts,
            "development_checks":development_invariant_checks,
            "landmark_observations_per_trial":10,"randomization_control_bits":1,
            "risk_by_arm":baseline,"aggregate_by_regime":aggregate,
            "heldout_records":records,"model_calls":0,
            "claim_limit":"Exogenous trial-population mixing over two fixed schedules is not within-run adaptation or next-shock prediction."}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
