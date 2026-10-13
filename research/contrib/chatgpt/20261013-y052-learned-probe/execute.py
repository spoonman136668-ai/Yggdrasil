"""Y052: development-trained four-parameter probe-schedule selection; sealed evaluation."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y051-probe-timing"/"execute.py"
spec=importlib.util.spec_from_file_location("y51_pinned",SOURCE)
assert spec and spec.loader
y51=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y51)
y50=y51.y50
y49=y51.y49
y46=y50.y46

TRAIN=tuple(range(1888,1896))
HELDOUT=tuple(range(1896,1912))
FAMILIES=((3,3,7),(5,9,1),(7,5,11),(13,1,5))
REGIMES=(("steady",None),("onset4",4),("onset5",5),
         ("onset6",6),("onset7",7))
POLICIES=y51.POLICIES
SCHEDULES={"A":((0,1,3,5,7),(5,7)),
           "B":((0,1,3,4,6),(4,6))}
ARMS=("fixed_A","fixed_B","learned_AB")
PERCEPT_EPOCHS=16
LEARNING_RATE=0.1


def observable_pre_episode4(seed,family):
    # Episode 0/1/3 anchor observations are in both schedules' fixed sensor
    # budgets. Calling this pure deterministic simulator read does not grant
    # candidate access to future events or to additional unique episode probes.
    b0,cell1_0=y46.observed_landmarks(seed,0,family,"late_shock")
    b1,cell1_1=y46.observed_landmarks(seed,1,family,"late_shock")
    b3,cell1_3=y46.observed_landmarks(seed,3,family,"late_shock")
    a=(cell1_3-b3)%16
    d=(b1-b0)%16
    assert a%2==1 and (cell1_0-b0)%16==a and (cell1_1-b1)%16==a
    assert b3==(b1+2*d)%16
    return (1.0,(a-8)/8.0,(d-8)/8.0,(b3-8)/8.0)


def paired_evaluate(seed,family,policy,schedule):
    probes,resets=SCHEDULES[schedule]
    y50.PROBES=probes
    y50.RESET_EPISODES=resets
    control=y50.evaluate(seed,policy,"canonical","trigger",family)
    candidate=y50.evaluate(seed,policy,"periodic","trigger",family)
    diffs=[]
    quenches=0
    reads=0
    churn_control=churn_candidate=0
    by_episode=[]
    for a,b in zip(control["rows"],candidate["rows"]):
        assert a["episode"]==b["episode"]
        for k in ("cache_writes","cache_occupancy","skipped_departures","flush","residual","landmark_reads","matched"):
            assert a[k]==b[k],k
        assert a["matched"]==7
        mismatch=a["physical_assignment"]!=b["physical_assignment"]
        diffs.append(int(mismatch))
        quenches+=int(a["flush"])
        reads+=a["landmark_reads"]
        churn_control+=a["physical_churn"]
        churn_candidate+=b["physical_churn"]
        by_episode.append({"episode":a["episode"],"mismatch":mismatch,
                           "landmark_reads":a["landmark_reads"],
                           "quarantine":a["flush"],
                           "churn_reference":a["physical_churn"],
                           "churn_candidate":b["physical_churn"],
                           "writes":a["cache_writes"]})
    assert len(diffs)==8 and reads==10
    return {"errors":sum(diffs),"quarantines":quenches,
            "landmark_reads":reads,"churn_reference":churn_control,
            "churn_candidate":churn_candidate,"by_episode":by_episode}


def fit(examples):
    assert len(examples)==8*4*5*3
    weights=[0.0]*4
    updates=0
    ties=0
    for features,decision,is_tie in examples:
        ties+=int(is_tie)
    for epoch in range(PERCEPT_EPOCHS):
        for features,label,is_tie in examples:
            score=sum(a*b for a,b in zip(weights,features))
            if label*score<=0:
                weights=[w+LEARNING_RATE*label*x for w,x in zip(weights,features)]
                updates+=1
    return weights,updates,ties


def selection(weights,features):
    return "B" if sum(w*x for w,x in zip(weights,features))>0 else "A"


def run():
    orig_probes=y50.PROBES
    orig_resets=y50.RESET_EPISODES
    examples=[]
    train_summary={"B_better":0,"A_better":0,"ties":0,
                   "features_with_opposed_targets":0}
    by_feature={}
    heldout_records=[]
    aggregate={regime:{arm:{"errors":0,"quarantines":0,"landmark_reads":0}
                       for arm in ARMS} for regime,_ in REGIMES}
    oracle_errors=0
    try:
        # All development outcome labels are confined to a distinct source
        # population and are NEVER forwarded to heldout schedule selection.
        for regime,onset in REGIMES:
            y49.install_environment(onset)
            for family in FAMILIES:
                for seed in TRAIN:
                    feature=observable_pre_episode4(seed,family)
                    for policy in POLICIES:
                        arms={s:paired_evaluate(seed,family,policy,s) for s in SCHEDULES}
                        ea,eb=arms["A"]["errors"],arms["B"]["errors"]
                        target=1 if eb<ea else -1
                        is_tie=ea==eb
                        if is_tie:train_summary["ties"]+=1
                        elif target==1:train_summary["B_better"]+=1
                        else:train_summary["A_better"]+=1
                        examples.append((feature,target,is_tie))
                        by_feature.setdefault(feature,set()).add(target)
        weights,updates,ties=fit(examples)
        assert ties==train_summary["ties"]
        train_summary["features_with_opposed_targets"]=sum(len(v)>1 for v in by_feature.values())
        assert len(weights)==4 and all(abs(w)<1e6 for w in weights)

        # First use of new sealed records begins only after fixed training.
        prehistories={}
        for regime,onset in REGIMES:
            y49.install_environment(onset)
            for family in FAMILIES:
                for seed in HELDOUT:
                    feature=observable_pre_episode4(seed,family)
                    key=(family,seed)
                    if key in prehistories:
                        assert feature==prehistories[key], "FUTURE_EVENT_LEAK"
                    else:
                        prehistories[key]=feature
                    chosen=selection(weights,feature)
                    assert chosen in SCHEDULES
                    for policy in POLICIES:
                        source={s:paired_evaluate(seed,family,policy,s) for s in SCHEDULES}
                        oracle_errors+=min(source["A"]["errors"],source["B"]["errors"])
                        used={"fixed_A":source["A"],"fixed_B":source["B"],
                              "learned_AB":source[chosen]}
                        for name,row in used.items():
                            aggregate[regime][name]["errors"]+=row["errors"]
                            aggregate[regime][name]["quarantines"]+=row["quarantines"]
                            aggregate[regime][name]["landmark_reads"]+=row["landmark_reads"]
                        heldout_records.append({
                            "regime":regime,"family":family,"seed":seed,"policy":policy,
                            "pre_episode4_public_features":feature,
                            "learned_selection":chosen,
                            "paired_fixed_outcomes":source})
    finally:
        y50.PROBES=orig_probes
        y50.RESET_EPISODES=orig_resets
        y49.restore_environment()
    for regime,_ in REGIMES:
        for arm in ARMS:
            assert aggregate[regime][arm]["landmark_reads"]==4*16*3*10
    pooled={arm:sum(aggregate[r][arm]["errors"] for r,_ in REGIMES) for arm in ARMS}
    steady=aggregate["steady"]["learned_AB"]
    baseline=min(pooled["fixed_A"],pooled["fixed_B"])
    if (pooled["learned_AB"]<.95*baseline and
        steady["errors"]==0 and steady["quarantines"]==0):
        classification="LEARNED_SELECTION_GAIN"
    elif (pooled["learned_AB"]<.99*baseline and
          steady["errors"]==0 and steady["quarantines"]==0):
        classification="PARTIAL_SELECTION_GAIN"
    else:
        classification="NO_GAIN"
    return {"schema":"yggdrasil.y052-learned-four-parameter-probe-selector.v1",
            "parent_head":"157905e34bf50af3528c4a0b39cbd2d6715a54bf",
            "classification":classification,
            "development_seeds":TRAIN,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"regimes":[name for name,_ in REGIMES],
            "train_examples":len(examples),"training_epochs":PERCEPT_EPOCHS,
            "learned_four_weights":weights,"training_updates":updates,
            "development_summary":train_summary,
            "causal_pre_shock_feature_equivalence":True,
            "pooled_errors_by_arm":pooled,
            "paired_world_oracle_diagnostic_not_deployable":oracle_errors,
            "aggregate_by_regime":aggregate,
            "heldout_records":heldout_records,"model_calls":0,
            "claim_limit":"Synthetic training of four scalar schedule weights on development outcomes; no knowledge of future independent shock onsets, with extra metadata capacity accounted."}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
