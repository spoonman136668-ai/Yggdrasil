"""Independent source/score/cold-evidence audit of YGG-JEPA2-03 candidate.

No experiment campaign module is imported; direct CKAD37 world-source
generation verifies the actual public consequences and chronological
prequential scoring. Frozen negative decision is reconstructed independently.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa_temporal import NativeTemporalMultiLearner

HERE=Path(__file__).resolve().parent
SRC=HERE.parent/"CKAD-37/campaign.py"
PAIRS=((14071,88901),(14072,88917))
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
BETA=("beta_full","beta_window24","beta_window48","beta_discount95")
ARMS=("native","one_step","temporal","blend","mispaired",*BETA,"sham")


def check(c,name):
    if not c:raise RuntimeError("YGG_JEPA2_03_AUDIT_"+name)


def original_worlds():
    spec=importlib.util.spec_from_file_location("ckad37_original_source_reconstruction",SRC)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def metrics(rows):
    check(bool(rows),"EMPTY_SCORING_GROUP")
    return {arm:{"brier":sum(r["losses"][arm] for r in rows)/len(rows),
                 "episodes":len(rows)} for arm in ARMS}


def read(out):
    result=json.loads((out/"result.json").read_bytes())
    check(result["schema"]=="yggdrasil.jepa2-03.real-native-temporal-continuation-dev.v1"
          and result["prereg_first_sha"]=="475649fc5eb44b0ecddd41b705a31c02a81661c2"
          and result["science_pass"] is False
          and result["accepted_native"] is False
          and result["owner_first_use"] is False
          and result["deployment"]=="NONE","SOURCE_CONTRACT")
    check(len(result["replicas"])==2,"REPLICA_COUNT")
    generator=original_worlds()
    verdicts=[]
    for oldseed,newseed in PAIRS:
        report=next(x for x in result["replicas"] if x["old_seed"]==oldseed)
        check(report["new_dev_seed"]==newseed,"REPLICA_SOURCE")
        state=json.loads((out/f"seed-{oldseed}-state.json").read_bytes())
        trace=json.loads((out/f"seed-{oldseed}-trace.json").read_bytes())
        check(len(trace)==report["new_source_count"] and len(trace)>400,
              "NEW_WITNESS_COUNT")
        indices=[]
        for world in (0,1):
            expected,_=generator.generator(newseed,world)
            source=[r for r in trace if r["world"]==world]
            check(len(source)==len(expected),"WORLD_EPISODE_COUNT")
            for t,(row,original) in enumerate(zip(source,expected)):
                identifier,views,observed,phase=original
                check(row["seed"]==newseed and row["index"]==t and
                      row["source_id"]==identifier and
                      row["views"]==[list(x) for x in views] and
                      row["first"]==observed["x1"] and
                      row["next_state"]==observed["s2"] and
                      row["second"]==observed["x2"] and
                      row["reward"]==observed["y"] and
                      row["phase"]==phase,"SOURCE_WITNESS_RECONSTRUCTION")
                for arm in ARMS:
                    p,q=row["forecasts"][arm]
                    b=((p-observed["s2"])**2+(q-observed["y"])**2)/2
                    check(abs(b-row["losses"][arm])<=1e-12,
                          "ACTUAL_PREQUENTIAL_ARITHMETIC")
                check(row["forecasts"]["sham"]==[.5,.5],
                      "SHAM_RESULT")
                indices.append((world,t,identifier))
        check(len(indices)==len(set(indices))==len(trace),"DUPLICATE_EVENT")
        all_metrics={phase:metrics([r for r in trace if r["phase"]==phase])
                     for phase in PHASES}
        all_metrics["pooled_late"]=metrics([
            r for r in trace if r["phase"] in ("late_B","late_return_A")
        ])
        for phase,group in all_metrics.items():
            for arm,a in group.items():
                b=report["metrics"][phase][arm]
                check(b["episodes"]==a["episodes"] and
                      abs(b["brier"]-a["brier"])<=1e-12,
                      "GROUP_BRIER_RECONSTRUCTION")
        p=all_metrics["pooled_late"]
        strong=min(p[arm]["brier"] for arm in BETA)
        q=all_metrics["early_B"]
        z=all_metrics["late_return_A"]
        decisions={
            "vs_native":p["blend"]["brier"]<=p["native"]["brier"]-0.005,
            "vs_strongest_control":p["blend"]["brier"]<=strong-0.010,
            "temporal_pairing":p["temporal"]["brier"]<=p["mispaired"]["brier"]-0.010,
            "early_shift_safety":q["blend"]["brier"]<=q["native"]["brier"]+0.010,
            "old_return_safety":z["blend"]["brier"]<=z["native"]["brier"]+0.010,
        }
        check(report["predicates"]==decisions and
              report["development_go"]==all(decisions.values()) and
              report["science_pass"] is False,
              "FROZEN_VERDICT_RECONSTRUCTION")
        raw=state["state_ascii"].encode("ascii")
        check(digest(raw)==state["state_sha256"],"MODEL_PIN")
        model=NativeTemporalMultiLearner.restore(raw,digest(raw))
        check(model.checkpoint()==raw and
              model.base.native.info()["count"]==report["total_retained_source_count"],
              "REAL_NATIVE_COLD")
        oldstate=json.loads((
           HERE.parent/"YGG-JEPA2-02"/f"seed-{oldseed}-states.json").read_bytes())[0]
        oldascii=oldstate["multi_learner_ascii"].encode("ascii")
        check(model.base.native._ledger[:report["original_source_count"]]==
              NativeTemporalMultiLearner.bootstrap(
                  oldascii,digest(oldascii)).base.native._ledger,
              "CONTINUED_OLD_SOURCE_CUSTODY")
        verdicts.append(report["development_go"])
    check(result["development_go"]==all(verdicts),"GLOBAL_VERDICT")
    print("YGG_JEPA2_03_COLD_SOURCE_AND_METRIC_AUDIT_PASS",
          "DEVELOPMENT_GO="+str(result["development_go"]),
          "SCIENCE_NOT_PASS",flush=True)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    x=p.parse_args()
    read(x.directory)


if __name__=="__main__":
    main()

