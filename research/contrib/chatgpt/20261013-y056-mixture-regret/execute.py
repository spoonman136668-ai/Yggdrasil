"""Y056: fixed shock-onset distribution shift regret of exogenous schedule hedge."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y055-allocation-keys"/"execute.py"
spec=importlib.util.spec_from_file_location("y55_pinned",SOURCE)
assert spec and spec.loader
y55=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y55)
y54=y55.y54
y53=y54.y53

DEV=tuple(range(2256,2264))
HELDOUT=tuple(range(2264,2280))
FAMILIES=((3,5,15),(5,1,11),(7,13,9),(11,7,3))
ONSET_NAMES=("onset4","onset5","onset6","onset7")
MIXTURES={
    "dominant4":(.7,.1,.1,.1),
    "dominant5":(.1,.7,.1,.1),
    "dominant6":(.1,.1,.7,.1),
    "dominant7":(.1,.1,.1,.7)}
ARMS=("fixed_A","fixed_B","hedged_50_50")


def run():
    previous=(y53.DEV,y53.HELDOUT,y53.FAMILIES)
    try:
        y53.DEV=DEV
        y53.HELDOUT=HELDOUT
        y53.FAMILIES=FAMILIES
        data=y53.run()
    finally:
        y53.DEV,y53.HELDOUT,y53.FAMILIES=previous
    assert data["development_seeds"]==DEV
    assert data["sealed_heldout_seeds"]==HELDOUT
    assert data["families"]==FAMILIES
    assert data["hedge_balanced_schedule_counts"]=={"A":8,"B":8}
    assert len(data["heldout_records"])==5*4*16*3
    by_onset={name:{arm:data["aggregate_by_regime"][name][arm]["mismatches"]
                   for arm in ARMS} for name in ONSET_NAMES}
    losses={}
    regrets={}
    for name,probabilities in MIXTURES.items():
        assert len(probabilities)==4 and abs(sum(probabilities)-1)<1e-12
        expected={arm:sum(weight*by_onset[onset][arm]
                          for onset,weight in zip(ONSET_NAMES,probabilities))
                  for arm in ARMS}
        oracle=min(expected["fixed_A"],expected["fixed_B"])
        losses[name]=expected
        regrets[name]={arm:expected[arm]-oracle for arm in ARMS}
        assert all(x>=-1e-8 for x in regrets[name].values())
    max_regret={arm:max(regrets[m][arm] for m in MIXTURES)
                for arm in ARMS}
    uniform={arm:sum(by_onset[m][arm] for m in ONSET_NAMES)/4.0 for arm in ARMS}
    base_worst=min(max_regret["fixed_A"],max_regret["fixed_B"])
    base_uniform=min(uniform["fixed_A"],uniform["fixed_B"])
    assert base_worst>0 and base_uniform>0
    good_steady=all(data["aggregate_by_regime"]["steady"][arm]["mismatches"]==0
                    for arm in ARMS)
    equal_budget=all(data["aggregate_by_regime"][name][arm]["landmark_reads"]==
                     4*16*3*10
                     for name in ("steady",)+ONSET_NAMES for arm in ARMS)
    ratio=max_regret["hedged_50_50"]/base_worst
    mean_ratio=uniform["hedged_50_50"]/base_uniform
    if good_steady and equal_budget and ratio<=.65 and mean_ratio<=1.10:
        label="MIXTURE_MINIMAX_REGRET_GAIN"
    elif good_steady and equal_budget and ratio<=.85 and mean_ratio<=1.20:
        label="PARTIAL_REGRET_GAIN"
    else:
        label="NO_GAIN"
    data["schema"]="yggdrasil.y056-onset-mixture-regret.v1"
    data["parent_head"]="e1f3a596a1ffc7b2f8f929475e4f81b1f7d6b31e"
    data["classification"]=label
    data["distribution_weights"]=MIXTURES
    data["expected_loss_by_distribution"]=losses
    data["regret_by_distribution"]=regrets
    data["worst_mixture_regret_by_arm"]=max_regret
    data["uniform_expected_loss_by_arm"]=uniform
    data["hedge_worst_regret_ratio"]=ratio
    data["hedge_uniform_loss_ratio"]=mean_ratio
    data["claim_limit"]=("Evaluator-only synthetic exogenous shock-onset frequency mixture; "
        "distribution weights and hindsight fixed optimal choices never reach deployed per-trial schedule.")
    return data


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
