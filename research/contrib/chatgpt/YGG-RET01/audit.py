"""YGG-RET01 independent source, prequential, memory and gate auditor.

Does not import campaign. Reconstructs every source witness, independently
runs the gate/controls and recomputes frozen outcomes, including negative old
history, rather than trusting repository result metrics or checkpoint hashes.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_readout_retention import (
    ArchivedEvidenceReadout,brier,_forecast,
)

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"YGG-JEPA2-03"
LIVE=HERE.parent/"YGG-JEPA2-04"
PAIRS=((14071,97241),(14072,97259))
PINS={
    14071:("958cc6050d167355af43b12f10ddd85542033319",
           "752b53d424dda55c0d18eb42bedef752e5492594"),
    14072:("08d8b357a3baa290e5a4c6773160aab6765b9fb5",
           "2e7ed2218d8b88f47a463d752fb9e304f2535940")
}
PREG="91100fa70086e5c1b2bc604da07c98dbe70af9e4"
PARENT="65a69d2733c18910178e1b7443332fddfd6bab89"
NEW_ARMS=("archive","live","gate","fixed_half","mispaired_gate","chance",
          "beta_full","beta_window24","beta_window32","beta_discount95")
OLD_ARMS=NEW_ARMS[:6]
PHASES=("warm_A","stable_A","early_B","late_B","early_return_A","late_return_A")


def check(c,tag):
    if not c:raise RuntimeError("YGG_RET01_AUDIT_"+tag)


def gitblob(path):
    return subprocess.check_output([
        "git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()
    ],cwd=ROOT,text=True,timeout=20).strip()


def source():
    spec=importlib.util.spec_from_file_location("ret01_independent_original_source",HERE/"source.py")
    s=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s)
    return s


def orig(old):
    a=OLD/f"seed-{old}-state.json"
    b=LIVE/f"seed-{old}-state.json"
    check((gitblob(a),gitblob(b))==PINS[old],"ORIGINAL_GIT_BLOB_CUSTODY")
    x,y=json.loads(a.read_bytes()),json.loads(b.read_bytes())
    ar=x["state_ascii"].encode("ascii")
    lr=y["checkpoint_ascii"].encode("ascii")
    check(digest(ar)==x["state_sha256"]
          and digest(lr)==y["checkpoint_sha256"],"ORIGINAL_SHA_CUSTODY")
    return ar,lr


def score(rows,arms):
    check(bool(rows),"SCORE_GROUP")
    return {arm:{"events":len(rows),
                 "brier":sum(x["losses"][arm] for x in rows)/len(rows)}
            for arm in arms}


def beta(ledger,views,row,arm):
    ctx=views[0]
    subset=ledger if arm in ("beta_full","beta_discount95") else (
        ledger[-24:] if arm=="beta_window24" else ledger[-32:])
    t,tn=1.,2.
    y,yn=1.,2.
    for i,item in enumerate(subset):
        _,old,x1,s2,x2,r=item
        factor=0.95**(len(subset)-i-1) if arm=="beta_discount95" else 1.
        if old[0]==ctx and x1==row["x1"]:
            t+=factor*s2;tn+=factor
            if x2==row["x2"] and s2==row["s2"]:
                y+=factor*r;yn+=factor
    return t/tn,y/yn


def near(a,b,reason):
    check(abs(a-b)<=1e-12,reason)


def audit(folder):
    data=json.loads((folder/"result.json").read_bytes())
    check(data["schema"]=="yggdrasil.ret01.actual-native-readout-development.v1"
          and data["prereg_sha"]==PREG and data["parent_sha"]==PARENT
          and data["science_pass"] is False
          and data["accepted_native"] is False
          and data["owner_first_use"] is False
          and data["deployment"]=="NONE"
          and len(data["replicas"])==2
          and data["source_blob"]==gitblob(HERE/"source.py"),
          "RESULT_SOURCE_SCHEMA")
    check(gitblob(HERE/"prereg.json")==subprocess.check_output(
        ["git","rev-parse",
         f"{PREG}:research/contrib/chatgpt/YGG-RET01/prereg.json"],
        cwd=ROOT,text=True).strip(),"FROZEN_PREREG")
    src=source()
    results=[]
    for oldseed,newseed in PAIRS:
        recorded=next(x for x in data["replicas"] if x["old_seed"]==oldseed)
        check(recorded["new_dev_seed"]==newseed,"DEVELOPMENT_SEEDS")
        ar,lr=orig(oldseed)
        actual=ArchivedEvidenceReadout(ar,lr)
        original=tuple(actual.current.original.base.native._ledger)
        old_original=tuple(actual.archived.base.native._ledger)
        beta_source=list(original)
        rows=json.loads((folder/f"seed-{oldseed}-trace.json").read_bytes())
        old_rows=json.loads((folder/f"seed-{oldseed}-old-probe.json").read_bytes())
        state=json.loads((folder/f"seed-{oldseed}-state.json").read_bytes())
        check(len(rows)==64 and len(old_rows)==32,
              "PREQUENTIAL_WITNESS_COUNTS")
        i=0
        for world in src.WORLDS:
            witness=src.generate(newseed,world)
            for t,entry in enumerate(witness):
                x=rows[i];i+=1
                check(x["old_seed"]==oldseed and x["seed"]==newseed
                      and x["world"]==world and x["index"]==t
                      and x["phase"]==entry["phase"]
                      and x["source_id"]==entry["source_id"]
                      and x["public_views"]==[list(v) for v in entry["views"]]
                      and x["row"]==entry["row"],
                      "PUBLIC_ORIGINAL_WITNESS_PARITY")
                predicted=actual.forecast(entry["views"],entry["row"])
                for arm in NEW_ARMS[6:]:
                    predicted[arm]=beta(beta_source,entry["views"],entry["row"],arm)
                for arm in NEW_ARMS:
                    for p,q in zip(predicted[arm],x["forecasts"][arm]):
                        near(p,q,"FULL_PUBLIC_PREQUENTIAL_FORECAST")
                    near(brier(predicted[arm],entry["row"]),
                         x["losses"][arm],"PREQUENTIAL_BRIER")
                near(actual.posterior,x["posterior_before"],
                     "EVIDENCE_POSTERIOR_BEFORE")
                actual.observe(entry["source_id"],entry["views"],entry["row"])
                near(actual.posterior,x["posterior_after"],
                     "EVIDENCE_POSTERIOR_AFTER")
                beta_source.append((
                    entry["source_id"],entry["views"],entry["row"]["x1"],
                    entry["row"]["s2"],entry["row"]["x2"],entry["row"]["y"]))
        check(i==64 and tuple(actual.current.original.base.native._ledger[:len(original)])
              ==original,"RETAIN_ORIGINAL_WITNESS_PREFIX")
        model_before_return=actual.current.checkpoint()
        for i,(historical,old_record) in enumerate(zip(old_rows,old_original[-32:])):
            identifier,views,first,state,second,reward=old_record
            row={"s1":views[0][0],"x1":first,"s2":state,"x2":second,"y":reward}
            check(historical["order"]==i
                  and historical["old_seed"]==oldseed
                  and historical["source_id"]==identifier
                  and historical["row"]==row
                  and historical["public_views"]==[list(v) for v in views]
                  and historical["already_consumed_diagnostic"] is True,
                  "HISTORICAL_OLD_SOURCE_ONLY")
            pred=actual.forecast(views,row)
            for arm in OLD_ARMS:
                for p,q in zip(pred[arm],historical["forecasts"][arm]):
                    near(p,q,"HISTORICAL_PREQUENTIAL_PREDICTIONS")
                near(brier(pred[arm],row),historical["losses"][arm],
                     "HISTORICAL_SCORE")
            actual.observe(identifier,views,row,historical=True)
            near(actual.posterior,historical["posterior_after"],
                 "HISTORICAL_EVIDENCE_POSTERIOR")
        check(actual.current.checkpoint()==model_before_return
              and len(actual.old_probe_events)==32,
              "HISTORICAL_NO_WEIGHT_UPDATES")
        raw=state["reader_ascii"].encode("ascii")
        check(digest(raw)==state["reader_sha256"]
              and state["archive_source_sha256"]==digest(ar)
              and state["initial_live_sha256"]==digest(lr),
              "IMMUTABLE_ORIGINAL_BOTH_MODELS")
        check(actual.checkpoint()==raw,"INDEPENDENT_FULL_REPLAY")
        cold=ArchivedEvidenceReadout.restore(raw,digest(raw),ar,lr)
        check(cold.checkpoint()==raw,"INDEPENDENT_COLD_RESTORATION")
        actual_score={p:score([x for x in rows if x["phase"]==p],NEW_ARMS)
                      for p in PHASES}
        actual_score["pooled_late"]=score(
            [x for x in rows if x["phase"] in ("late_B","late_return_A")],
            NEW_ARMS)
        historical_score=score(old_rows,OLD_ARMS)
        for key,v in actual_score.items():
            for arm,m in v.items():
                expected=recorded["new_metrics"][key][arm]
                check(expected["events"]==m["events"],"AGGREGATE_EVENT_COUNT")
                near(expected["brier"],m["brier"],"AGGREGATE_NEW_METRIC")
        for arm,m in historical_score.items():
            expected=recorded["old_historical_metrics"][arm]
            near(expected["brier"],m["brier"],"AGGREGATE_OLD_METRIC")
        pooled=actual_score["pooled_late"]
        strong=min(pooled[arm]["brier"] for arm in NEW_ARMS[6:])
        old=historical_score
        decisions={
            "new_vs_live":pooled["gate"]["brier"]<=pooled["live"]["brier"]-0.005,
            "new_vs_best_beta":pooled["gate"]["brier"]<=strong-0.005,
            "new_safety_vs_chance":pooled["gate"]["brier"]<=0.27,
            "historical_return_vs_live":old["gate"]["brier"]<=
                                         old["live"]["brier"]-0.010,
            "historical_return_near_archived":old["gate"]["brier"]<=
                                              old["archive"]["brier"]+0.03,
            "historic_frozen_exact":abs(recorded["old_archived_brier_before"]-
                                       recorded["old_archived_brier_after"])<1e-15,
            "original_native_ledger_retained":True,
            "cold_replay":cold.checkpoint()==raw,
        }
        check(decisions==recorded["predicates"]
              and recorded["development_go"]==all(decisions.values())
              and recorded["science_pass"] is False
              and recorded["new_witnesses"]==64
              and recorded["historical_probe_count"]==32
              and recorded["strongest_new_beta"]==strong,
              "FROZEN_DEVELOPMENT_QUALIFIER")
        results.append(recorded["development_go"])
    check(data["development_go"]==all(results),"REPLICA_GATE")
    print("YGG_RET01_INDEPENDENT_SOURCE_RETRIEVAL_COLD_AUDIT_PASS",
          "DEVELOPMENT_GO" if data["development_go"] else "DEVELOPMENT_NO_GO",
          "SCIENCE_NOT_PASS",flush=True)
    return data


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    args=p.parse_args()
    audit(args.directory)

