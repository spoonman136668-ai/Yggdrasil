"""Seal original qualified JEPA2-04 Linux/Windows native future-state evidence.

Only downloaded source-locked original CI artifacts; no source-generation/
training rerun after seeing negative result. Preserve negative outcomes.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest

HERE=Path(__file__).resolve().parent
ARTIFACTS=("result.json","seed-14071-state.json","seed-14071-trace.json",
           "seed-14072-state.json","seed-14072-trace.json")
TOL=1e-7


def check(c,tag):
    if not c:raise RuntimeError("YGG_JEPA2_04_SEAL_"+tag)


def numeric_match(a,b,tag="result"):
    if type(a) is float and type(b) in (float,int):
        check(np.isfinite(a) and np.isfinite(b) and abs(a-b)<=TOL,
              "FLOAT_"+tag)
    elif type(a) is list:
        check(type(b) is list and len(a)==len(b),"LIST_"+tag)
        for i,(x,y) in enumerate(zip(a,b)):
            numeric_match(x,y,tag+"/"+str(i))
    elif type(a) is dict:
        check(type(b) is dict and set(a)==set(b),"KEY_"+tag)
        for k in a:
            numeric_match(a[k],b[k],tag+"/"+str(k))
    else:
        check(a==b,"VALUE_"+tag)


def without_timing_and_bytes(result):
    obj=json.loads(json.dumps(result))
    for seed in obj["replicas"]:
        seed.pop("cpu_seconds")
        seed.pop("wall_seconds")
        for world in seed["world_receipts"]:
            for key in ("post_native_sha256","post_five_component_sha256",
                        "post_full_future_checkpoint_sha256",
                        "post_full_future_checkpoint_bytes"):
                world.pop(key)
    return obj


def compare_state(w1,w2,seed):
    check(w1["old_seed"]==w2["old_seed"]==seed and
          w1["new_seed"]==w2["new_seed"],"STATE_ID")
    d1=json.loads(w1["checkpoint_ascii"])
    d2=json.loads(w2["checkpoint_ascii"])
    for k in ("sensory","reward"):
        a,b=d1[k],d2[k]
        numeric_match(a,b,k)
    # The original native and prior four heads must agree in public witness
    # sequence and original anchored source, not bit-identical platform libm.
    check(d1["schema"]==d2["schema"]
          and d1["native_ascii"] and d2["native_ascii"],"NATIVE_PARENT_SCHEMA")
    n1=json.loads(d1["native_ascii"])
    n2=json.loads(d2["native_ascii"])
    check(n1["schema"]==n2["schema"] and
          n1["source_count"]==n2["source_count"],"PARENT_SOURCE_CUSTODY")
    b1=json.loads(n1["base_ascii"])
    b2=json.loads(n2["base_ascii"])
    check(b1["schema"]==b2["schema"],"OLD_JEPA_COLD_SCHEMA")
    # The entire numeric checkpoint may differ by last ULP. Its original
    # native evidence events are independently verified by each OS audit.
    for name in ("direct","negative","no_history","no_action","beta_windows"):
        numeric_match(w1[name],w2[name],name)


def main():
    linux=Path(os.environ["YGG_JEPA4_LINUX"])
    windows=Path(os.environ["YGG_JEPA4_WINDOWS"])
    run=os.environ["YGG_JEPA4_RUN_ID"]
    source=os.environ["YGG_JEPA4_SOURCE_SHA"]
    for name in ARTIFACTS:
        check((linux/name).is_file() and (windows/name).is_file(),
              "EVIDENCE_MISSING_"+name)
    lr=json.loads((linux/"result.json").read_bytes())
    wr=json.loads((windows/"result.json").read_bytes())
    check(len(lr["replicas"])==len(wr["replicas"])==2
          and lr["science_pass"] is False
          and wr["science_pass"] is False
          and lr["owner_first_use"] is False
          and wr["owner_first_use"] is False
          and lr["development_go"]==wr["development_go"],
          "RESULT_AUTHORITY_OR_VERDICT")
    numeric_match(without_timing_and_bytes(lr),
                  without_timing_and_bytes(wr),"main_result")
    for oldseed in (14071,14072):
        a=json.loads((linux/f"seed-{oldseed}-state.json").read_bytes())
        b=json.loads((windows/f"seed-{oldseed}-state.json").read_bytes())
        compare_state(a,b,oldseed)
        at=json.loads((linux/f"seed-{oldseed}-trace.json").read_bytes())
        bt=json.loads((windows/f"seed-{oldseed}-trace.json").read_bytes())
        numeric_match(at,bt,"witnessed_prequential_trace")
    for filename in ARTIFACTS:
        shutil.copyfile(linux/filename,HERE/filename)
    receipt={
        "schema":"yggdrasil.jepa2-04.windows-independent-replication.v1",
        "source_sha":source,"original_run":run,
        "original_linux_sha256":{n:digest((linux/n).read_bytes()) for n in ARTIFACTS},
        "original_windows_sha256":{n:digest((windows/n).read_bytes()) for n in ARTIFACTS},
        "numeric_tolerance":TOL,"matched_development_go":lr["development_go"],
        "science_pass":False,
        "original_source_replayed_as_new_first_use":False,
    }
    (HERE/"windows-replication.json").write_bytes(canonical(receipt))
    provenance={
        "schema":"yggdrasil.jepa2-04.source-provenance.v1",
        "prereg_first_sha":"6d113f776697a3709b46f1c616d2eb66c6e0e857",
        "parent_sha":"eee9ab7719f52c1c67ce30b142e8f07f36454dd1",
        "source_commit":source,"original_training_run":run,
        "new_world_family":"disjoint synthetic causal development, NOT independent original science",
        "original_training_repeated":False,"real_native_model_continued":True,
        "science_pass":False,"deployment":"NONE","development_go":lr["development_go"],
    }
    (HERE/"provenance.json").write_bytes(canonical(provenance))
    readme=[
        "# YGG-JEPA2-04 — Native cumulative three-step JEPA-style future states",
        "",
        "**ACTUAL training**, preserving original native causal knowledge and",
        "all 4 previously learned JEPA-style experts, plus two new separate",
        "trainable three-step future state latent experts. A trainable future",
        "observation encoder, decoder, and EMA stop-gradient target teach",
        "each action-conditioned predictor a **multi-variable future representation**.",
        "",
        "This is NOT Meta's pretrained V-JEPA2 video model. All new source",
        "episodes are disjoint synthetic Yggdrasil DEVELOPMENT worlds, not",
        "an independent real-world scientific test or protected first-use.",
        "",
        "Preregistered before source/training: 6d113f776697a3709b46f1c616d2eb66c6e0e857",
        "Previous five-component source: eee9ab7719f52c1c67ce30b142e8f07f36454dd1",
        "Frozen source execution commit: "+source,
        "Dual-platform original source training/audit: "+run,
        "",
        "## Late B and A-return 3-horizon six-outcome Brier (lower better)",
        "",
        "| Old seed → new dev seed | Native | Future JEPA | Fully fitted direct | Best conventional | Mispaired | Verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in lr["replicas"]:
        p=item["metrics"]["pooled_late"]
        readme.append(
            f"| {item['old_seed']} → {item['new_seed']} | "
            f"{p['native']['brier']:.9f} | {p['future']['brier']:.9f} | "
            f"{p['direct']['brier']:.9f} | {item['strongest_control']:.9f} | "
            f"{p['mispaired']['brier']:.9f} | "
            f"{'DEVELOPMENT_GO' if item['development_go'] else 'DEVELOPMENT_NO_GO'} |"
        )
    readme.extend([
        "",
        "Frozen development verdict: "+("GO" if lr["development_go"] else "NO_GO"),
        "SCIENTIFIC_PASS=false. ACCEPTED_NATIVE=false. DEPLOYMENT=NONE.",
        "",
        "Only actually revealed public future states/outcomes enter gradient",
        "updates, at least three action-consequence observations later.",
        "Three future intervention actions are announced BEFORE their",
        "outcomes. Strong direct logistic/online Beta, no-history, no-action",
        "and matched-update mismatched-target controls were trained too.",
        "",
        "Cumulative native source prefix, original four trained heads,",
        "full 12-bit future observation forecasts, source IDs, numeric",
        "EMA teacher weights, exact source-code pins, and two-seed",
        "unambiguous negative/positive receipts are saved in this folder.",
        "",
        "Original Linux and Windows artifacts were audited separately and",
        "then compared without a fresh repeat of scored development data.",
        "Exact final full Linux/Windows native regressions and G29 run on",
        "the post-evidence Atlas SHA.",
        "",
        "**DRAFT/UNMERGED.** No accepted main/controller modifications,",
        "owner first-use, additional scheduled task, external deployment,",
        "paid API, or scientifically proven transfer claims.",
    ])
    (HERE/"README.md").write_text("\n".join(readme)+"\n",encoding="utf8")
    print("YGG_JEPA2_04_ORIGINAL_EVIDENCE_DUAL_OS_SEAL_PASS",
          "DEVELOPMENT_GO" if lr["development_go"] else "DEVELOPMENT_NO_GO",
          flush=True)


if __name__=="__main__":
    main()

