"""Y051: frozen equal-budget landmark probe placement; exact pinned Y050 evaluator."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y050-residual-quarantine"/"execute.py"
spec=importlib.util.spec_from_file_location("y50_pinned",SOURCE)
assert spec and spec.loader
y50=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y50)
y49=y50.y49

DEV=tuple(range(1800,1808))
HELDOUT=tuple(range(1808,1824))
FAMILIES=((3,7,1),(5,11,3),(7,9,5),(11,5,7))
REGIMES=(("steady",None),("onset4",4),("onset5",5),
         ("onset6",6),("onset7",7))
SCHEDULES={
    "A":((0,1,3,5,7),(5,7)),
    "B":((0,1,3,4,6),(4,6))}
INTERVENTIONS=("continue","trigger")
POLICIES=y50.POLICIES

def run():
    old_probes=y50.PROBES
    old_reset=y50.RESET_EPISODES
    aggregate={name:{schedule:{action:{"total":0,"episode6":0,"episode7":0,
                                      "quarantines":0,"landmark_reads":0}
                              for action in INTERVENTIONS}
                     for schedule in SCHEDULES}
               for name,_ in REGIMES}
    records=[]
    try:
        for name,onset in REGIMES:
            y49.install_environment(onset)
            for family in FAMILIES:
                for seed in DEV+HELDOUT:
                    for policy in POLICIES:
                        comparisons={}
                        for schedule,(probes,resets) in SCHEDULES.items():
                            assert len(probes)==5 and len(resets)==2
                            y50.PROBES=probes
                            y50.RESET_EPISODES=resets
                            schedule_results={}
                            for action in INTERVENTIONS:
                                control=y50.evaluate(seed,policy,"canonical",action,family)
                                candidate=y50.evaluate(seed,policy,"periodic",action,family)
                                episode_rows=[]
                                for a,b in zip(control["rows"],candidate["rows"]):
                                    assert a["episode"]==b["episode"]
                                    assert a["cache_writes"]==b["cache_writes"]
                                    assert a["cache_occupancy"]==b["cache_occupancy"]
                                    assert a["skipped_departures"]==b["skipped_departures"]
                                    assert a["flush"]==b["flush"]
                                    assert a["residual"]==b["residual"]
                                    assert a["landmark_reads"]==b["landmark_reads"]
                                    assert a["matched"]==b["matched"]==7
                                    mismatch=a["physical_assignment"]!=b["physical_assignment"]
                                    episode_rows.append({
                                        "episode":a["episode"],"mismatch":mismatch,
                                        "quarantine":a["flush"],"residual":a["residual"],
                                        "landmark_reads":a["landmark_reads"],
                                        "cache_writes":a["cache_writes"],
                                        "physical_churn_reference":a["physical_churn"],
                                        "physical_churn_candidate":b["physical_churn"],
                                        "physical_assignment_reference":a["physical_assignment"],
                                        "physical_assignment_candidate":b["physical_assignment"]})
                                assert sum(row["landmark_reads"] for row in episode_rows)==10
                                if seed in HELDOUT:
                                    totals=aggregate[name][schedule][action]
                                    totals["total"]+=sum(row["mismatch"] for row in episode_rows)
                                    totals["episode6"]+=int(episode_rows[6]["mismatch"])
                                    totals["episode7"]+=int(episode_rows[7]["mismatch"])
                                    totals["quarantines"]+=sum(row["quarantine"] for row in episode_rows)
                                    totals["landmark_reads"]+=10
                                schedule_results[action]={
                                    "episodes":episode_rows,
                                    "mismatch_count":sum(row["mismatch"] for row in episode_rows)}
                            comparisons[schedule]=schedule_results
                        records.append({"regime":name,"family":family,"seed":seed,
                                        "cohort":"heldout" if seed in HELDOUT else "development",
                                        "policy":policy,"schedules":comparisons})
    finally:
        y50.PROBES=old_probes
        y50.RESET_EPISODES=old_reset
        y49.restore_environment()
    on6=aggregate["onset6"]
    on7=aggregate["onset7"]
    steady=aggregate["steady"]
    gain6=on6["A"]["trigger"]["total"]-on6["B"]["trigger"]["total"]
    gain7=on7["B"]["trigger"]["total"]-on7["A"]["trigger"]["total"]
    controls=(all(steady[s]["trigger"]["total"]==0 and
                  steady[s]["trigger"]["quarantines"]==0 for s in SCHEDULES) and
              all(aggregate[r][s]["trigger"]["landmark_reads"]==4*16*3*10
                  for r,_ in REGIMES for s in SCHEDULES))
    if gain6>0 and gain7>0 and controls:
        classification="SCHEDULE_TRADEOFF"
    elif gain6>0 or gain7>0:
        classification="PARTIAL_TIMING_GAIN"
    else:
        classification="NO_TIMING_GAIN"
    return {"schema":"yggdrasil.y051-equal-probe-timing.v1",
            "parent_head":"ce6bbc9e2e13aac9e3a7d33e57aff6fb63b931a0",
            "classification":classification,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"schedules":SCHEDULES,
            "observation_scalars_per_eight_episodes":10,
            "aggregate_by_onset_schedule_intervention":aggregate,
            "records":records,"model_calls":0,
            "claim_limit":"Frozen synthetic equal-budget public landmark schedule tradeoff; not event-adaptive sensing."}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
