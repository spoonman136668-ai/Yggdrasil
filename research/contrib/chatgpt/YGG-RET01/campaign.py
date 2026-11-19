"""YGG-RET01 actually continue prior Yggdrasil, test readout evidence retrieval.

Frozen current JEPA2-04 7-component trained source and archived JEPA2-03
native reader are exact Git-blob pinned. Each independent cohort witnesses
64 NEW PUBLIC action/consequence episodes. Model and matched controls
predict before revelation, then update. After training, 32 already-consumed
historical episodes probe evidence-only returning readout (not new science).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_readout_retention import (
    ArchivedEvidenceReadout,brier,_forecast,
)

HERE=Path(__file__).resolve().parent
PARENT="65a69d2733c18910178e1b7443332fddfd6bab89"
PREREG="91100fa70086e5c1b2bc604da07c98dbe70af9e4"
OLD=HERE.parent/"YGG-JEPA2-03"
CURRENT=HERE.parent/"YGG-JEPA2-04"
SEEDS=((14071,97241),(14072,97259))
PINS_OLD={14071:"958cc6050d167355af43b12f10ddd85542033319",
          14072:"08d8b357a3baa290e5a4c6773160aab6765b9fb5"}
PINS_CURRENT={14071:"752b53d424dda55c0d18eb42bedef752e5492594",
              14072:"2e7ed2218d8b88f47a463d752fb9e304f2535940"}
NEW_ARMS=("archive","live","gate","fixed_half","mispaired_gate","chance",
          "beta_full","beta_window24","beta_window32","beta_discount95")
OLD_ARMS=("archive","live","gate","fixed_half","mispaired_gate","chance")
PHASES=("warm_A","stable_A","early_B","late_B","early_return_A","late_return_A")


def check(c,tag):
    if not c:raise RuntimeError("YGG_RET01_"+tag)


def git_blob(path):
    return subprocess.check_output(
        ["git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()],
        cwd=ROOT,text=True,timeout=20).strip()


def source_module():
    spec=importlib.util.spec_from_file_location(
        "ygg_ret01_original_source",HERE/"source.py")
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def inputs(oldseed):
    oldfile=OLD/f"seed-{oldseed}-state.json"
    livefile=CURRENT/f"seed-{oldseed}-state.json"
    check(git_blob(oldfile)==PINS_OLD[oldseed]
          and git_blob(livefile)==PINS_CURRENT[oldseed],
          "ORIGINAL_TRAINED_SOURCE_BLOB")
    old=json.loads(oldfile.read_bytes())
    live=json.loads(livefile.read_bytes())
    archive_raw=old["state_ascii"].encode("ascii")
    live_raw=live["checkpoint_ascii"].encode("ascii")
    check(digest(archive_raw)==old["state_sha256"]
          and digest(live_raw)==live["checkpoint_sha256"],
          "ORIGINAL_CHECKPOINT_SOURCE_SHA")
    return archive_raw,live_raw


class BayesianCounts:
    """Online fitted matched-information categorical Beta models."""
    def __init__(self,source):
        self.ledger=list(source)

    def forecast(self, views, row, arm):
        check(arm in NEW_ARMS[6:],"CONVENTIONAL_ARM")
        bank=self.ledger
        if arm=="beta_window24":bank=bank[-24:]
        if arm=="beta_window32":bank=bank[-32:]
        context=views[0]
        numer_t,denom_t=1.,2.
        numer_r,denom_r=1.,2.
        for i,(_,old_views,x1,s2,x2,y) in enumerate(bank):
            w=(0.95**(len(bank)-i-1)
               if arm=="beta_discount95" else 1.)
            if old_views[0]==context and x1==row["x1"]:
                numer_t+=w*s2
                denom_t+=w
                if s2==row["s2"] and x2==row["x2"]:
                    numer_r+=w*y
                    denom_r+=w
        return numer_t/denom_t,numer_r/denom_r

    def update(self, identifier, views, row):
        self.ledger.append((identifier,views,row["x1"],row["s2"],row["x2"],row["y"]))


def summarize(rows,arms):
    check(bool(rows),"SCORE_GROUP_EMPTY")
    return {arm:{"brier":sum(x["losses"][arm] for x in rows)/len(rows),
                 "events":len(rows)}
            for arm in arms}


def run_seed(oldseed,newseed,source):
    started=time.perf_counter()
    cpu=time.process_time()
    archive_raw,live_raw=inputs(oldseed)
    reader=ArchivedEvidenceReadout(archive_raw,live_raw)
    original_source=tuple(reader.current.original.base.native._ledger)
    archive_source=tuple(reader.archived.base.native._ledger)
    check(len(original_source) in (942,917)
          and len(archive_source) in (702,677),
          "ORIGINAL_LEDGER_COUNTS")
    controls=BayesianCounts(original_source)
    orig_future=canonical({
        "sensory":reader.current.sensory.checkpoint(),
        "reward":reader.current.reward.checkpoint()})
    old_source_fingerprint=digest(reader.archived.checkpoint())
    before_archive_probs=[]
    before_live_probs=[]
    for identifier,views,first,state,second,reward in archive_source[-32:]:
        row={"s1":views[0][0],"x1":first,"s2":state,"x2":second,"y":reward}
        before_archive_probs.append(
            brier(_forecast(reader.archived.base.native,views,row),row))
        before_live_probs.append(
            brier(_forecast(reader.current.original.base.native,views,row),row))
    old_archive_baseline=sum(before_archive_probs)/32
    old_live_baseline=sum(before_live_probs)/32

    new_trace=[]
    receipts=[]
    seen={r[0] for r in original_source}
    for world in source.WORLDS:
        events=source.generate(newseed,world)
        begin_count=reader.current.original.base.native.info()["count"]
        begin_sha=digest(reader.checkpoint())
        for t,e in enumerate(events):
            identifier,views,row=e["source_id"],e["views"],e["row"]
            check(identifier not in seen and e["seed"]==newseed
                  and e["world"]==world and e["index"]==t
                  and e["phase"] in PHASES,"NEW_SOURCE_EXACT_PUBLIC")
            seen.add(identifier)
            forecast=reader.forecast(views,row)
            for arm in NEW_ARMS[6:]:
                forecast[arm]=controls.forecast(views,row,arm)
            losses={arm:brier(forecast[arm],row) for arm in NEW_ARMS}
            posterior_before=reader.posterior
            original_observation=reader.observe(identifier,views,row)
            check(original_observation is not None
                  and original_observation["live"]==forecast["live"]
                  and original_observation["gate"]==forecast["gate"],
                  "PREQUENTIAL_READOUT_PARITY")
            controls.update(identifier,views,row)
            new_trace.append({
                "seed":newseed,"old_seed":oldseed,"world":world,
                "index":t,"phase":e["phase"],"source_id":identifier,
                "public_views":views,"row":row,
                "posterior_before":posterior_before,
                "posterior_after":reader.posterior,
                "forecasts":forecast,"losses":losses,
            })
        current_native=reader.current.original.base.native
        check(current_native.info()["count"]==begin_count+source.EVENTS,
              "ACTUAL_NATIVE_TRAINING_COUNT")
        check(tuple(current_native._ledger[:len(original_source)])==original_source,
              "OLD_NATIVE_PUBLIC_WITNESS_ERASURE")
        check(digest(reader.archived.checkpoint())==old_source_fingerprint,
              "ORIGINAL_ARCHIVE_MODEL_CHANGED")
        receipts.append({
            "world":world,"new_public_events":len(events),
            "begin_count":begin_count,
            "final_native_count":current_native.info()["count"],
            "begin_reader_sha256":begin_sha,
            "final_reader_sha256":digest(reader.checkpoint()),
            "final_cumulative_native_sha256":digest(current_native.checkpoint()),
            "archive_unchanged":True,
            "all_four_prior_specialists_update":True,
        })

    new_phase={
        phase:summarize([x for x in new_trace if x["phase"]==phase],NEW_ARMS)
        for phase in PHASES
    }
    new_pooled=summarize([x for x in new_trace
                          if x["phase"] in ("late_B","late_return_A")],NEW_ARMS)
    new_phase["pooled_late"]=new_pooled

    # Returning historic witness diagnostic: already-consumed source,
    # NOT held first-use. The old frozen model is never trained on these again.
    old_trace=[]
    weight_before_return=reader.posterior
    for i,(identifier,views,first,state,second,reward) in enumerate(
            archive_source[-32:]):
        row={"s1":views[0][0],"x1":first,"s2":state,"x2":second,"y":reward}
        predicted=reader.forecast(views,row)
        losses={arm:brier(predicted[arm],row) for arm in OLD_ARMS}
        poster_before=reader.posterior
        probe=reader.observe(identifier,views,row,historical=True)
        check(predicted==probe,"HISTORICAL_PROBE_PREQUENTIAL_PARITY")
        old_trace.append({
            "old_seed":oldseed,"source_id":identifier,
            "order":i,"public_views":views,"row":row,
            "posterior_before":poster_before,
            "posterior_after":reader.posterior,
            "forecasts":predicted,"losses":losses,
            "already_consumed_diagnostic":True
        })
    historic=summarize(old_trace,OLD_ARMS)
    after_archive=sum(
        brier(_forecast(reader.archived.base.native,views,{
            "s1":views[0][0],"x1":a,"s2":s,"x2":b,"y":r
        }),{"s1":views[0][0],"x1":a,"s2":s,"x2":b,"y":r})
        for _,views,a,s,b,r in archive_source[-32:]
    )/32
    check(abs(old_archive_baseline-after_archive)<1e-15,
          "IMMUTABLE_ORIGINAL_CONTEXT_READOUT")
    check(digest(reader.archived.checkpoint())==old_source_fingerprint,
          "ARCHIVE_CHECKPOINT_CHANGED")
    check(tuple(reader.current.original.base.native._ledger[:len(original_source)])
          ==original_source,"CUMULATIVE_ORIGINAL_NATIVE_PREFIX")
    check(canonical({
          "sensory":reader.current.sensory.checkpoint(),
          "reward":reader.current.reward.checkpoint()})==orig_future,
          "SIX_COMPONENT_FUTURE_WEIGHTS_CUSTODY")
    count=reader.current.original.base.native.info()["count"]
    check(count==len(original_source)+64 and count<=1024,
          "NATIVE_CAPACITY_CUSTODY")
    final_blob=reader.checkpoint()
    cold=ArchivedEvidenceReadout.restore(
        final_blob,digest(final_blob),archive_raw,live_raw)
    check(cold.checkpoint()==final_blob and
          cold.current.checkpoint()==reader.current.checkpoint(),
          "FULL_ORIGINAL_EVIDENCE_COLD")
    elapsed_cpu=time.process_time()-cpu
    check(elapsed_cpu<=125,"FROZEN_CPU_LIMIT")
    best_beta=min(new_pooled[a]["brier"] for a in NEW_ARMS[6:])
    checks={
        "new_vs_live":new_pooled["gate"]["brier"]<=new_pooled["live"]["brier"]-0.005,
        "new_vs_best_beta":new_pooled["gate"]["brier"]<=best_beta-0.005,
        "new_safety_vs_chance":new_pooled["gate"]["brier"]<=0.27,
        "historical_return_vs_live":historic["gate"]["brier"]<=
                                     historic["live"]["brier"]-0.010,
        "historical_return_near_archived":historic["gate"]["brier"]<=
                                          historic["archive"]["brier"]+0.03,
        "historic_frozen_exact":abs(old_archive_baseline-after_archive)<1e-15,
        "original_native_ledger_retained":True,
        "cold_replay":cold.checkpoint()==final_blob,
    }
    result={
        "old_seed":oldseed,"new_dev_seed":newseed,
        "native_retained_episodes_before":len(original_source),
        "native_retained_episodes_after":count,
        "archive_episodes":len(archive_source),
        "future_heads_unmodified":True,
        "new_witnesses":64,"historical_probe_count":32,
        "world_receipts":receipts,
        "archive_sha256":old_source_fingerprint,
        "initial_live_sha256":digest(live_raw),
        "old_archived_brier_before":old_archive_baseline,
        "old_archived_brier_after":after_archive,
        "old_live_brier_before":old_live_baseline,
        "archive_posterior_at_return":weight_before_return,
        "archive_posterior_after_return":reader.posterior,
        "new_metrics":new_phase,
        "old_historical_metrics":historic,
        "strongest_new_beta":best_beta,
        "predicates":checks,
        "development_go":all(checks.values()),
        "science_pass":False,
        "cpu_seconds":elapsed_cpu,
        "wall_seconds":time.perf_counter()-started,
    }
    state={
        "old_seed":oldseed,"new_dev_seed":newseed,
        "archive_source_sha256":digest(archive_raw),
        "initial_live_sha256":digest(live_raw),
        "reader_sha256":digest(final_blob),
        "reader_ascii":final_blob.decode("ascii"),
        "frozen_future_heads_sha256":digest(orig_future),
        "new_model_cold_sha256":digest(reader.current.checkpoint()),
        "beta_ledger_count":len(controls.ledger)
    }
    return result,state,new_trace,old_trace


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    check(git_blob(HERE/"prereg.json")==subprocess.check_output(
        ["git","rev-parse",
         f"{PREREG}:research/contrib/chatgpt/YGG-RET01/prereg.json"],
        cwd=ROOT,text=True).strip(),"PREREG_FROZEN")
    source=source_module()
    results=[]
    for oldseed,newseed in SEEDS:
        report,state,trace,oldtrace=run_seed(oldseed,newseed,source)
        results.append(report)
        for name,value in [
            (f"seed-{oldseed}-state.json",state),
            (f"seed-{oldseed}-trace.json",trace),
            (f"seed-{oldseed}-old-probe.json",oldtrace)
        ]:
            (args.output/name).write_bytes(canonical(value))
        print("YGG_RET01_REAL_NATIVE_CONTINUATION",oldseed,newseed,
              "new_public_events",report["new_witnesses"],
              "development_go",report["development_go"],flush=True)
    result={
        "schema":"yggdrasil.ret01.actual-native-readout-development.v1",
        "prereg_sha":PREREG,"parent_sha":PARENT,
        "source_blob":git_blob(HERE/"source.py"),
        "original_old_model_git_blobs":PINS_OLD,
        "original_current_model_git_blobs":PINS_CURRENT,
        "replicas":results,
        "development_go":all(x["development_go"] for x in results),
        "science_pass":False,"accepted_native":False,
        "owner_first_use":False,"deployment":"NONE",
        "caution":"Old historic return diagnostic reuses previously consumed original native witnesses and is NOT fresh held scientific transfer. New source is separate synthetic development only."
    }
    (args.output/"result.json").write_bytes(canonical(result))
    print("YGG_RET01_"+("DEVELOPMENT_GO" if result["development_go"]
                       else "DEVELOPMENT_NO_GO")+" SCIENCE_NOT_PASS",flush=True)


if __name__=="__main__":
    main()

