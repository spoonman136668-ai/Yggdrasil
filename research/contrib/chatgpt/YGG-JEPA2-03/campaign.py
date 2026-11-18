"""YGG-JEPA2-03: CONTINUE real native cumulative training; add temporal experts.

Every model starts at a fully trained, independently audited YGG-JEPA2-02
checkpoint; prior native source/weights are never reset. New development-only
CKAD37 causal-world episodes are observed sequentially by ONE learner
per replica across 2 previously unseen development seed worlds. Hidden
regime/phase labels remain evaluator-only. No independent scientific first-use.
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
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_jepa_temporal import (
    NativeTemporalMultiLearner, TemporalLatentSpecialist, _fit_history, STEPS,
)

HERE=Path(__file__).resolve().parent
PARENT="f21b16c3823e5353caae6d76a4051909bf87d944"
PREREG="475649fc5eb44b0ecddd41b705a31c02a81661c2"
OLD_DIR=HERE.parent/"YGG-JEPA2-02"
SOURCE=ROOT/"research/contrib/chatgpt/CKAD-37/campaign.py"
BASE={
 14071:{"new":88901, "blob":"563e8e562c2af5ad2d37b7d6da727252e9f27633",
        "old_native":"90f959b217e639515b642365d05a915bb6dfbcc099eafef0666f02b88496de38",
        "old_checkpoint":"021d02351e9decc4cc11b6b2a0f320ba1520ec3bd6c0b8819f07914908241295"},
 14072:{"new":88917,"blob":"1758915fd61ebad14a226acf06ac1baa04e060ce",
        "old_native":"040641dba3be3fa348cf08b02fde4be1416ad38d601a70cded7b271b02fb8011",
        "old_checkpoint":"e9c63de1dd3ed59bae3939698c53e91d8347732f935569cc32b8ee701d737f9e"},
}
ARMS=("native","one_step","temporal","blend","mispaired",
      "beta_full","beta_window24","beta_window48","beta_discount95","sham")
BETA=("beta_full","beta_window24","beta_window48","beta_discount95")
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
SCHEMA="yggdrasil.jepa2-03.real-native-temporal-continuation-dev.v1"
MAX_EPISODES=1000
MAX_CPU=120.


def check(cond, name):
    if not cond:raise RuntimeError("YGG_JEPA2_03_"+name)


def git_blob(path):
    check(path.is_file(),"SOURCE_NOT_AVAILABLE")
    return subprocess.check_output(["git","rev-parse","HEAD:"+
        path.relative_to(ROOT).as_posix()],cwd=ROOT,text=True,timeout=15).strip()


def load_ckad37():
    # Read-only import of original Yggdrasil world generator and control model.
    spec=importlib.util.spec_from_file_location("yggdrasil_ckad37_source",SOURCE)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    check(module.SCHEMA=="yggdrasil.ckad37.native-unannounced-rule-shifts.v1",
          "UNEXPECTED_WORLD_SOURCE")
    return module


def verified_old(seed):
    desc=BASE[seed]
    path=OLD_DIR/f"seed-{seed}-states.json"
    check(git_blob(path)==desc["blob"],"OLD_CHECKPOINT_GIT_BLOB")
    records=json.loads(path.read_bytes())
    check(len(records)==2 and records[0]["world"]==0,"OLD_WORLD_CUSTODY")
    record=records[0]
    raw=record["multi_learner_ascii"].encode("ascii")
    check(digest(raw)==desc["old_checkpoint"]==record["multi_learner_sha256"],
          "ORIGINAL_LEARNED_CHECKPOINT_SHA")
    model=NativeTemporalMultiLearner.bootstrap(raw,digest(raw))
    check(digest(model.base.native.checkpoint())==
          desc["old_native"]==record["native_original_sha256"],
          "ORIGINAL_NATIVE_BYTE_SHA")
    check(model.base.checkpoint()==raw,"OLD_LEARNED_WEIGHTS_CHANGED")
    return model


def old_row(event):
    _, views, first, state, second, reward=event
    return {"s1":views[0][0],"x1":first,"s2":state,"x2":second,"y":reward}


def risk(pred,row):
    p,q=pred
    check(all(isinstance(v,(float,int)) and 0<=v<=1
              for v in (p,q)),"PROBABILITY")
    return ((p-row["s2"])**2+(q-row["y"])**2)/2


def scores(rows):
    check(bool(rows),"MISSING_PHASE")
    return {arm:{"brier":sum(x["losses"][arm] for x in rows)/len(rows),
                 "episodes":len(rows)} for arm in ARMS}


def run_seed(oldseed, source):
    started=time.perf_counter()
    cpu=time.process_time()
    info=BASE[oldseed]
    newseed=info["new"]
    model=verified_old(oldseed)
    initial_count=model.source_count
    old_ledger=model.base.native._ledger
    check(initial_count==len(old_ledger) and initial_count in (226,240),
          "OLD_WITNESS_COUNT")
    # Exact reference native model; only observed source actions are admitted.
    ref=NativeEpisodeExperience.restore(
        model.base.native.checkpoint(),digest(model.base.native.checkpoint()))
    conventional=source.Conventional()
    for event in old_ledger:
        conventional.observe(old_row(event))
    sham_t,sham_r=_fit_history(old_ledger,mispair=True)
    check(sham_t.steps==model.transition.steps and
          sham_r.steps==model.reward.steps,"OLD_NEGATIVE_BUDGET")
    original_native_sha=digest(ref.checkpoint())
    original_base_sha=digest(model.base.checkpoint())
    original_ledger=old_ledger
    old_predictions=[]
    for event in old_ledger[-32:]:
        _, views, first, state, second, reward=event
        pred=model.base.predict(views,first,state,second,stream=True)
        old_predictions.append(risk(pred["native"],old_row(event)))
    old_brier_before=sum(old_predictions)/len(old_predictions)
    traces=[]
    world_receipts=[]
    snapshot_before_world=None
    all_ids=set(e[0] for e in original_ledger)
    for world in (0,1):
        # The generator returns private regime/phase labels; ONLY event views,
        # first/second actions and witnessed consequences go into any learner.
        events,priv=source.generator(newseed,world)
        check(len(events)>160 and len(events)<300,"NEW_WORLD_LENGTH")
        prior_count=model.base.native.info()["count"]
        start_sha=digest(model.checkpoint())
        previous=old_ledger[-1] if world==0 else model.base.native._ledger[-1]
        for t,(identifier,views,row,phase) in enumerate(events):
            check(identifier not in all_ids and
                  phase in ("warm",)+PHASES,"NEW_WITNESS_SHAPE")
            all_ids.add(identifier)
            before=model.base.native._ledger
            predicted=model.predict(views,row["x1"],row["s2"],row["x2"])
            negative=(sham_t.probability(views,(row["x1"],),before),
                      sham_r.probability(views,(row["x1"],row["s2"],row["x2"]),before))
            context=row["s1"]
            ctrl={}
            for arm in BETA:
                ctrl[arm]=(
                    conventional.p(arm,"transition",context,row["x1"]),
                    conventional.p(arm,"terminal",context,row["x1"],
                                    row["s2"],row["x2"])
                )
            predictions={**predicted,"mispaired":negative,
                         **ctrl,"sham":(.5,.5)}
            losses={arm:risk(predictions[arm],row) for arm in ARMS}
            traces.append({
                "seed":newseed,"world":world,"index":t,"phase":phase,
                "source_id":identifier,
                "views":views,"first":row["x1"],"next_state":row["s2"],
                "second":row["x2"],"reward":row["y"],
                "forecasts":predictions,"losses":losses,
            })
            # VERIFIED outcome revelation occurs after all predictions above.
            model=model.observe(identifier,views,row)
            ref=ref.observe(identifier,views,row)
            conventional.observe(row)
            sham_t.observe(views,(row["x1"],),before,previous[3])
            sham_r.observe(views,(row["x1"],row["s2"],row["x2"]),
                           before,previous[5])
            previous=(identifier,views,row["x1"],row["s2"],row["x2"],row["y"])
        check(model.base.native.checkpoint()==ref.checkpoint(),
              "ORIGINAL_NATIVE_REPLAY_DRIFT")
        check(model.base.native._ledger[:initial_count]==original_ledger,
              "ORIGINAL_SOURCE_PREFIX_CHANGED")
        check(model.base.native.info()["count"]==prior_count+len(events),
              "CUMULATIVE_EPISODE_COUNT")
        check(model.base.native.info()["count"]<MAX_EPISODES,
              "SOURCE_CAPACITY")
        raw=model.checkpoint()
        check(len(raw)<=1048576,"CUMULATIVE_CHECKPOINT_LIMIT")
        restored=NativeTemporalMultiLearner.restore(raw,digest(raw))
        check(restored.checkpoint()==raw,"COLD_CONTINUATION_DIVERGENCE")
        check(model.base.checkpoint()==restored.base.checkpoint(),
              "OLD_EXPERT_COLD_REPLAY")
        check(model.transition.steps==model.reward.steps==
              model.base.native.info()["count"]*STEPS,"TEMPORAL_SOURCE_PARITY")
        check(sham_t.steps==sham_r.steps==model.transition.steps,
              "NEGATIVE_TRAINING_BUDGET")
        world_receipts.append({
            "world":world,"new_source_seed":newseed,"episode_count":len(events),
            "initial_source_count":prior_count,
            "final_source_count":model.base.native.info()["count"],
            "world_start_sha256":start_sha,
            "cold_multi_learner_sha256":digest(raw),
            "cold_multi_learner_bytes":len(raw),
            "native_sha256":digest(ref.checkpoint()),
            "temporal_updates_per_expert":model.transition.steps,
            "old_learner_updates_per_expert":model.base.transition.steps,
            "original_source_prefix_retained":True,
            "private_world_boundaries_used_for_training":False
        })
    after_raw=model.checkpoint()
    identifier,views,row=events[-1]
    check(model.observe(identifier,views,row) is model,
          "CUMULATIVE_DUPLICATE_IDEMPOTENCE")
    corrupted=dict(row);corrupted["y"]^=1
    try:model.observe(identifier,views,corrupted)
    except ValueError:pass
    else:raise RuntimeError("YGG_JEPA2_03_CONTRADICTION_NOT_REJECTED")
    check(model.checkpoint()==after_raw,"CONFLICT_MUTATED_TRAINING")
    old_after=[]
    for event in original_ledger[-32:]:
        _,view,first,state,second,reward=event
        pred=model.base.predict(view,first,state,second,stream=True)
        old_after.append(risk(pred["native"],old_row(event)))
    old_brier_after=sum(old_after)/len(old_after)
    metrics={phase:scores([r for r in traces if r["phase"]==phase])
             for phase in PHASES}
    pooled=[r for r in traces if r["phase"] in ("late_B","late_return_A")]
    metrics["pooled_late"]=scores(pooled)
    primary=metrics["pooled_late"]
    strong=min(primary[a]["brier"] for a in BETA)
    early,returning=metrics["early_B"],metrics["late_return_A"]
    b=primary["blend"]["brier"]
    preds={
        "vs_native":b<=primary["native"]["brier"]-0.005,
        "vs_strongest_control":b<=strong-0.010,
        "temporal_pairing":primary["temporal"]["brier"]<=
                            primary["mispaired"]["brier"]-0.010,
        "early_shift_safety":early["blend"]["brier"]<=
                               early["native"]["brier"]+0.010,
        "old_return_safety":returning["blend"]["brier"]<=
                               returning["native"]["brier"]+0.010,
    }
    check(model.base.native._ledger[:initial_count]==original_ledger,
          "FINAL_ORIGINAL_SOURCE_ERASURE")
    spent=time.process_time()-cpu
    check(spent<=MAX_CPU,"CPU_BUDGET_EXCEEDED")
    report={
        "old_seed":oldseed,"new_dev_seed":newseed,
        "original_source_count":initial_count,
        "new_source_count":len(traces),
        "total_retained_source_count":model.base.native.info()["count"],
        "original_native_sha256":original_native_sha,
        "original_multi_learner_sha256":original_base_sha,
        "old_source_prefix_retained":True,
        "old_source_diagnostic_brier_before":old_brier_before,
        "old_source_diagnostic_brier_after":old_brier_after,
        "world_receipts":world_receipts,
        "metrics":metrics,"predicates":preds,
        "strongest_conventional_brier":strong,
        "development_go":all(preds.values()),
        "science_pass":False,
        "cpu_seconds":spent,
        "wall_seconds":time.perf_counter()-started,
    }
    return report,{"old_seed":oldseed,"new_dev_seed":newseed,
        "state_sha256":digest(after_raw),"state_ascii":after_raw.decode("ascii"),
        "sham_transition":sham_t.data(),"sham_reward":sham_r.data(),
        "old_original_model_sha256":info["old_checkpoint"]},traces


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    source=load_ckad37()
    final=[]
    for oldseed in (14071,14072):
        report,state,trace=run_seed(oldseed,source)
        final.append(report)
        for name,record in [
            (f"seed-{oldseed}-state.json",state),
            (f"seed-{oldseed}-trace.json",trace)
        ]:
            (args.output/name).write_bytes(canonical(record))
        print("YGG_JEPA2_03_COMPLETED",oldseed,
              "new_episode_count",report["new_source_count"],
              "development_go",report["development_go"],flush=True)
    result={
        "schema":SCHEMA,"prereg_first_sha":PREREG,
        "source_parent":PARENT,"source_kind":"native cumulative, prior retained plus fresh synthetic development episodes",
        "replicas":final,"development_go":all(x["development_go"] for x in final),
        "science_pass":False,"accepted_native":False,"deployment":"NONE",
        "owner_first_use":False,
        "caution":"Preconsumed synthetic parent seed/source; new dev-only Yggdrasil causal generator seeds; no protected primary or externally novel world science."
    }
    (args.output/"result.json").write_bytes(canonical(result))
    print("YGG_JEPA2_03_SOURCE_TRAINING_COMPLETE",
          "DEVELOPMENT_GO" if result["development_go"] else "DEVELOPMENT_NO_GO",
          "SCIENTIFIC_NOT_PASS",flush=True)


if __name__=="__main__":
    main()

