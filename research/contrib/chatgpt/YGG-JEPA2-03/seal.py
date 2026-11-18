"""Seal only immutable original YGG-JEPA2-03 dual-OS training artifacts.

No retest/rerun of scored development worlds on source repair; compare
independent original Linux/Windows outputs, recompute source arithmetic, and
archive exact provenance and frozen negative/positive classification in Git.
"""
import json
import os
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical, digest

HERE=Path(__file__).resolve().parent
FILES=("result.json","seed-14071-state.json","seed-14071-trace.json",
       "seed-14072-state.json","seed-14072-trace.json")


def check(cond,name):
    if not cond:raise RuntimeError("YGG_JEPA2_03_SEAL_"+name)


def nearly(a,b,where=""):
    if type(a) is float and type(b) in (float,int):
        check(abs(a-b) <= 1e-9,"NUMERIC_CROSSOS:"+where)
    elif type(a) is list:
        check(type(b) is list and len(a)==len(b),"LIST_CROSSOS:"+where)
        for i,(x,y) in enumerate(zip(a,b)):
            nearly(x,y,where+"/"+str(i))
    elif type(a) is dict:
        check(type(b) is dict and set(a)==set(b),"KEYS_CROSSOS:"+where)
        for key in a:
            nearly(a[key],b[key],where+"/"+str(key))
    else:
        check(a==b,"VALUE_CROSSOS:"+where)


def stable(result):
    out=json.loads(json.dumps(result))
    for r in out["replicas"]:
        r.pop("wall_seconds",None)
        r.pop("cpu_seconds",None)
        for w in r["world_receipts"]:
            w.pop("cold_multi_learner_sha256",None)
            w.pop("cold_multi_learner_bytes",None)
            w.pop("world_start_sha256",None)
    return out


def state_check(a,b):
    check(a["old_seed"]==b["old_seed"] and
          a["new_dev_seed"]==b["new_dev_seed"] and
          a["old_original_model_sha256"]==b["old_original_model_sha256"],
          "OLD_SOURCE_REPLICA")
    d1=json.loads(a["state_ascii"]); d2=json.loads(b["state_ascii"])
    check(d1["schema"]==d2["schema"] and
          d1["base_sha256"]==d2["base_sha256"] and
          d1["source_count"]==d2["source_count"],
          "MODEL_RESTORED_SOURCE_ID")
    base1,base2=json.loads(d1["base_ascii"]),json.loads(d2["base_ascii"])
    check(base1["native_ascii"]==base2["native_ascii"] and
          base1["native_sha256"]==base2["native_sha256"],
          "EXACT_NATIVE_SOURCE_LEDGER")
    for expert in ("transition","reward"):
        nearly(base1[expert],base2[expert],"old-expert/"+expert)
    for expert in ("temporal_transition","temporal_reward"):
        nearly(d1[expert],d2[expert],"new-expert/"+expert)
    for expert in ("sham_transition","sham_reward"):
        nearly(a[expert],b[expert],"negative-expert/"+expert)


def main():
    linux=Path(os.environ["YGG_JEPA3_LINUX"])
    windows=Path(os.environ["YGG_JEPA3_WINDOWS"])
    run=os.environ["YGG_JEPA3_RUN_ID"]
    source=os.environ["YGG_JEPA3_SOURCE_SHA"]
    for name in FILES:
        check((linux/name).is_file() and (windows/name).is_file(),
              "MISSING_ORIGINAL_ARTIFACT:"+name)
    a=json.loads((linux/"result.json").read_bytes())
    b=json.loads((windows/"result.json").read_bytes())
    nearly(stable(a),stable(b),"original-results")
    for seed in (14071,14072):
        pa,pb=f"seed-{seed}-state.json",f"seed-{seed}-trace.json"
        state_check(json.loads((linux/pa).read_bytes()),
                    json.loads((windows/pa).read_bytes()))
        nearly(json.loads((linux/pb).read_bytes()),
               json.loads((windows/pb).read_bytes()),"original-traces")
    check(a["science_pass"] is False and a["deployment"]=="NONE" and
          a["development_go"]==b["development_go"],
          "NO_FALSE_SCIENCE")
    for file in FILES:
        shutil.copyfile(linux/file,HERE/file)
    (HERE/"windows-replication.json").write_bytes(canonical({
        "schema":"yggdrasil.jepa2-03.cross-os-original.v1",
        "original_run":run,"original_source_commit":source,
        "linux_sha256":{f:digest((linux/f).read_bytes()) for f in FILES},
        "windows_sha256":{f:digest((windows/f).read_bytes()) for f in FILES},
        "windows_result":b,"native_source_bit_exact":True,
        "specialist_weights_tolerance":1e-9,
        "development_go":a["development_go"],"science_pass":False,
    }))
    (HERE/"provenance.json").write_bytes(canonical({
        "schema":"yggdrasil.jepa2-03.original-provenance.v1",
        "frozen_prereg_commit":"475649fc5eb44b0ecddd41b705a31c02a81661c2",
        "old_qualified_source_parent":"f21b16c3823e5353caae6d76a4051909bf87d944",
        "original_run":run,"source_commit":source,
        "new_dev_seeds":[88901,88917],
        "development_go":a["development_go"],"science_pass":False,
        "deployment":"NONE","owner_first_use":False,
    }))
    text=[
        "# YGG-JEPA2-03 — Native cumulative temporal JEPA-style training",
        "",
        "The original source-authenticated NativeEpisodeExperience and both earlier",
        "trained JEPA2-02 specialists are NOT reset; a new transition and reward",
        "temporal-history latent specialist each fits from preceding 8 witnessed",
        "real public interventions. After old source bootstrap, the SAME model",
        "continues through 2 unfamiliar (development-only) A->B->A source worlds",
        "per replica, preserving old source IDs and source-conditioned weights.",
        "",
        "This is an opt-in native Yggdrasil module, not Meta video V-JEPA 2,",
        "not real-world external transfer, not owner first-use, and not a",
        "production-model or controller mutation.",
        "",
        "Frozen prereg before changes: 475649fc5eb44b0ecddd41b705a31c02a81661c2",
        "Prior qualified source: f21b16c3823e5353caae6d76a4051909bf87d944",
        "Source-locked Linux/Windows training run: "+run,
        "Original campaign source SHA: "+source,
        "",
        "## Frozen development prequential pooled late-B and A-return Brier",
        "",
        "| Prior seed | New dev seed | Native | Previous one-step | New temporal-only | Fixed native/temporal blend | Best fitted conventional | Mispaired temporal | Verdict |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in a["replicas"]:
        p=r["metrics"]["pooled_late"]
        text.append(
            f"| {r['old_seed']} | {r['new_dev_seed']} | "
            f"{p['native']['brier']:.9f} | "
            f"{p['one_step']['brier']:.9f} | "
            f"{p['temporal']['brier']:.9f} | "
            f"{p['blend']['brier']:.9f} | "
            f"{r['strongest_conventional_brier']:.9f} | "
            f"{p['mispaired']['brier']:.9f} | "
            f"{'DEVELOPMENT_GO' if r['development_go'] else 'DEVELOPMENT_NO_GO'} |"
        )
    text.extend([
        "",
        "**Frozen result:** "+("DEVELOPMENT_GO" if a["development_go"] else "DEVELOPMENT_NO_GO"),
        "",
        "**SCIENTIFIC_PASS=false. ACCEPTED_NATIVE=false. DEPLOYMENT=NONE.**",
        "New dev seeds are synthetic and generated by an existing source; even",
        "positive development would not qualify scientific transfer.",
        "",
        "The saved state files include the complete cumulative native memory,",
        "both old expert weights and both temporal expert weights. An independent",
        "restore re-fits the temporal weights from the source witness history,",
        "rejecting changed weights even with recomputed checkpoint hashes.",
        "",
        "## Source custody and audit",
        "",
        "Original Linux and Windows training artifacts were independently",
        "compared: native source ledger exact, old/new/negative weights numeric",
        "within 1e-9. Prequential causal source rows and strong controls were",
        "audited against unchanged CKAD37 development generator, not fabricated",
        "toy rows. Full original regression is a separate post-evidence gate.",
        "",
        "Files: prereg.json, campaign.py, audit.py, seal.py, full result,",
        "two original source-linked models, two all-episode traces,",
        "provenance.json and windows-replication.json.",
        "",
        "No post-result retuning/replay of these scored seeds; no merge,",
        "promotion, deployment, new runtime, scheduler, paid API or owner",
        "first-use authority.",
    ])
    (HERE/"README.md").write_text("\n".join(text)+"\n",encoding="utf8")
    print("YGG_JEPA2_03_ORIGINAL_EVIDENCE_SEAL_PASS",
          "DEVELOPMENT_GO" if a["development_go"] else "DEVELOPMENT_NO_GO",
          "SCIENTIFIC_NOT_PASS",flush=True)


if __name__=="__main__":
    main()

