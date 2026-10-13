"""Y049: fixed episode5 cache quarantine under new unannounced shock timings."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y048-cache-reset"/"execute.py"
spec=importlib.util.spec_from_file_location("y48_pinned",SOURCE)
assert spec and spec.loader
y48=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y48)
y46=y48.y46

DEV=tuple(range(1584,1592))
HELDOUT=tuple(range(1592,1608))
FAMILIES=((3,1,7),(5,3,1),(7,5,9),(13,7,11))
POLICIES=y48.POLICIES
ONSET_NAMES=("steady","onset3","onset4","onset6")
INTERVENTIONS=("continue","quarantine")
ORIGINAL=(y46.coordinate,y46.physical_coordinate,y46.observed_landmarks)


def install_environment(onset):
    """Patch only the deterministic environment, never policy/scientific results."""
    orig_coordinate,orig_physical,_=ORIGINAL
    def offset(episode):
        return 5 if onset is not None and episode>=onset else 0
    def coordinate(cell,seed,episode,family,regime):
        return (orig_coordinate(cell,seed,episode,family,"steady")+offset(episode))%16
    def physical_coordinate(observed,seed,episode,family,regime):
        return orig_physical((observed-offset(episode))%16,seed,episode,family,"steady")
    def landmarks(seed,episode,family,regime):
        return (coordinate(0,seed,episode,family,regime),
                coordinate(1,seed,episode,family,regime))
    y46.coordinate=coordinate
    y46.physical_coordinate=physical_coordinate
    y46.observed_landmarks=landmarks


def restore_environment():
    y46.coordinate,y46.physical_coordinate,y46.observed_landmarks=ORIGINAL


def run():
    summaries={regime:{intervention:{"pre5":0,"post5":0,"at4":0}
                       for intervention in INTERVENTIONS}
               for regime in ONSET_NAMES}
    records=[]
    try:
        for name,onset in (("steady",None),("onset3",3),("onset4",4),("onset6",6)):
            install_environment(onset)
            for family in FAMILIES:
                for seed in DEV+HELDOUT:
                    for policy in POLICIES:
                        comparisons={}
                        for intervention in INTERVENTIONS:
                            # Evaluator sees a conventional symbolic regime only.
                            # The experimental shock timing is in the environment
                            # coordinate functions, never exposed to this reader.
                            control=y48.evaluate(seed,"late_shock",policy,"reference",intervention,family)
                            periodic=y48.evaluate(seed,"late_shock",policy,"periodic",intervention,family)
                            before=after=at4=0
                            for a,b in zip(control["rows"],periodic["rows"]):
                                assert a["episode"]==b["episode"]
                                assert a["cache_writes"]==b["cache_writes"]
                                assert a["cache_occupancy"]==b["cache_occupancy"]
                                assert a["skipped_departures"]==b["skipped_departures"]
                                assert a["flushed"]==b["flushed"]
                                assert a["matched"]==b["matched"]==7
                                if seed in HELDOUT and a["physical_assignment"]!=b["physical_assignment"]:
                                    if a["episode"]<5:
                                        before+=1
                                    else:
                                        after+=1
                                    if a["episode"]==4:
                                        at4+=1
                            if seed in HELDOUT:
                                summaries[name][intervention]["pre5"]+=before
                                summaries[name][intervention]["post5"]+=after
                                summaries[name][intervention]["at4"]+=at4
                            comparisons[intervention]={
                                "mismatches_pre5":before,"mismatches_post5":after,
                                "canonical_churn":sum(x["churn"] for x in control["rows"]),
                                "periodic_churn":sum(x["churn"] for x in periodic["rows"]),
                                "writes":sum(x["cache_writes"] for x in periodic["rows"]),
                                "suppressed_departures":sum(x["skipped_departures"] for x in periodic["rows"])}
                        records.append({"regime":name,"family":family,"seed":seed,
                                        "cohort":"heldout" if seed in HELDOUT else "development",
                                        "policy":policy,"paired_comparisons":comparisons})
    finally:
        restore_environment()
    c4=summaries["onset4"]
    c6=summaries["onset6"]
    if c4["quarantine"]["post5"]==0 and c6["quarantine"]["post5"]>0 and c4["continue"]["post5"]>0:
        classification="RESET_WINDOW_DEPENDENT"
    elif c4["quarantine"]["post5"]<c4["continue"]["post5"]:
        classification="PARTIAL_WINDOW"
    else:
        classification="NO_CONFIRMED_WINDOW"
    return {"schema":"yggdrasil.y049-fixed5-reset-window.v1",
            "parent_head":"c7f2fb3162e65ca90fb03f8fca80b9d9df5611d0",
            "classification":classification,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "onset_regimes":ONSET_NAMES,"families":FAMILIES,
            "mismatches_by_onset_and_intervention":summaries,
            "records":records,"model_calls":0,
            "claim_limit":"Synthetic shock timing and fixed scheduled cache intervention only, no event awareness."}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
