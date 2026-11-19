"""Seal original independent Linux/Windows readout retention evidence to GitHub.

Never retrain scored development sources merely to repair an evidence step.
Each OS must pass independent full source/weights/readout audit BEFORE seal.
"""
import json
import os
from pathlib import Path
import shutil
import sys
from math import isfinite

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest

HERE=Path(__file__).resolve().parent
FILES=("result.json","seed-14071-state.json","seed-14071-trace.json",
       "seed-14071-old-probe.json","seed-14072-state.json",
       "seed-14072-trace.json","seed-14072-old-probe.json")
TOL=1e-7


def check(c,name):
    if not c:raise RuntimeError("YGG_RET01_SEAL_"+name)


def equiv(a,b,label="root"):
    if type(a) is float and type(b) in (float,int):
        check(isfinite(a) and isfinite(b) and abs(a-b)<=TOL,
              "FLOAT_"+label)
    elif type(a) is list:
        check(type(b) is list and len(a)==len(b),"LIST_"+label)
        for i,(x,y) in enumerate(zip(a,b)):
            equiv(x,y,label+"/"+str(i))
    elif type(a) is dict:
        check(type(b) is dict and set(a)==set(b),"KEYS_"+label)
        for k in a:
            equiv(a[k],b[k],label+"/"+str(k))
    else:
        check(a==b,"VALUE_"+label)


def normal_result(d):
    v=json.loads(json.dumps(d))
    for seed in v["replicas"]:
        seed.pop("cpu_seconds")
        seed.pop("wall_seconds")
        for receipt in seed["world_receipts"]:
            receipt.pop("begin_reader_sha256")
            receipt.pop("final_reader_sha256")
            receipt.pop("final_cumulative_native_sha256")
    return v


def main():
    linux=Path(os.environ["YGG_RET01_LINUX"])
    windows=Path(os.environ["YGG_RET01_WINDOWS"])
    run=os.environ["YGG_RET01_RUN"]
    source=os.environ["YGG_RET01_SOURCE"]
    for name in FILES:
        check((linux/name).is_file() and (windows/name).is_file(),
              "MISSING_ORIGINAL_"+name)
    lr=json.loads((linux/"result.json").read_bytes())
    wr=json.loads((windows/"result.json").read_bytes())
    check(lr["science_pass"] is False and wr["science_pass"] is False
          and lr["development_go"]==wr["development_go"]
          and lr["owner_first_use"] is False and wr["owner_first_use"] is False,
          "FROZEN_SCIENCE_AND_RESULT")
    equiv(normal_result(lr),normal_result(wr),"frozen_results")
    for seed in (14071,14072):
        a=json.loads((linux/f"seed-{seed}-state.json").read_bytes())
        b=json.loads((windows/f"seed-{seed}-state.json").read_bytes())
        for k in ("old_seed","new_dev_seed","archive_source_sha256",
                  "initial_live_sha256","frozen_future_heads_sha256",
                  "beta_ledger_count"):
            check(a[k]==b[k],"STATE_PROVENANCE_"+k)
        # Cold native source/weights are independently replayed and checked
        # in both OS audit jobs; compare the gate probabilities numerically.
        inner_a=json.loads(a["reader_ascii"])
        inner_b=json.loads(b["reader_ascii"])
        for k in ("schema","archive_sha256","initial_live_sha256"):
            check(inner_a[k]==inner_b[k],"READER_PRIOR_"+k)
        for k in ("posterior","negative_posterior"):
            equiv(inner_a[k],inner_b[k],"selector_"+k)
        equiv(inner_a["new_events"],inner_b["new_events"],"source_events")
        equiv(inner_a["old_probe_events"],inner_b["old_probe_events"],
              "old_probe_events")
        for suffix in ("trace","old-probe"):
            trace_a=json.loads((linux/f"seed-{seed}-{suffix}.json").read_bytes())
            trace_b=json.loads((windows/f"seed-{seed}-{suffix}.json").read_bytes())
            equiv(trace_a,trace_b,"prequential_"+suffix)
    for file in FILES:
        shutil.copyfile(linux/file,HERE/file)
    (HERE/"windows-replication.json").write_bytes(canonical({
        "schema":"yggdrasil.ret01.windows-source-replication.v1",
        "source_sha":source,"original_run":run,
        "linux_artifact_sha256":{f:digest((linux/f).read_bytes()) for f in FILES},
        "windows_artifact_sha256":{f:digest((windows/f).read_bytes()) for f in FILES},
        "independent_full_native_replay_audit":True,
        "comparison_numeric_tolerance":TOL,
        "science_pass":False,
    }))
    (HERE/"provenance.json").write_bytes(canonical({
        "schema":"yggdrasil.ret01.evidence-provenance.v1",
        "prereg_first_sha":"91100fa70086e5c1b2bc604da07c98dbe70af9e4",
        "parent_sha":"65a69d2733c18910178e1b7443332fddfd6bab89",
        "source_sha":source,"training_run":run,
        "scored_original_rerun":False,
        "development_go":lr["development_go"],
        "science_pass":False,"deployment":"NONE",
    }))
    report=[
        "# YGG-RET01 — Pinned native causal readout + evidence-only retrieval",
        "",
        "Engineering: two-platform source-bound training, frozen original readout,",
        "independent exact public outcome replay, independent original-state",
        "cold continuation and evidence selector qualification.",
        "",
        "This development candidate stores an immutable archived context readout",
        "from an original native checkpoint while the existing, fully trained",
        "seven-component native+six-head model continues to observe witnessed",
        "public events (four earlier heads update, two future heads persist).",
        "A prior-1/8 evidence-only Bayesian selection weights the archived",
        "and live context readouts without hidden domain labels.",
        "",
        "Frozen prereg FIRST: 91100fa70086e5c1b2bc604da07c98dbe70af9e4",
        "Qualified old source: 65a69d2733c18910178e1b7443332fddfd6bab89",
        "Frozen first training source: "+source,
        "Original independent two-OS audit run: "+run,
        "",
        "## New domain public evidence Brier (lower better)",
        "",
        "| Seed | Live native | Pinned archive | Evidence gate | Best fitted Beta | Mispaired gate | Verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for seed in lr["replicas"]:
        pool=seed["new_metrics"]["pooled_late"]
        report.append(
            f"| {seed['new_dev_seed']} | {pool['live']['brier']:.9f} | "
            f"{pool['archive']['brier']:.9f} | {pool['gate']['brier']:.9f} | "
            f"{seed['strongest_new_beta']:.9f} | "
            f"{pool['mispaired_gate']['brier']:.9f} | "
            f"{'DEVELOPMENT_GO' if seed['development_go'] else 'DEVELOPMENT_NO_GO'} |")
    report.extend([
        "",
        "## Previously consumed historical return diagnostic (NOT fresh science)",
        "",
        "| Original seed | Pinned old readout before | Pinned old readout after | Live readout | Evidence gate | Frozen qualifiers |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ])
    for seed in lr["replicas"]:
        old=seed["old_historical_metrics"]
        failed=", ".join(k for k,v in seed["predicates"].items() if not v)
        report.append(
            f"| {seed['old_seed']} | "
            f"{seed['old_archived_brier_before']:.9f} | "
            f"{seed['old_archived_brier_after']:.9f} | "
            f"{old['live']['brier']:.9f} | "
            f"{old['gate']['brier']:.9f} | "
            f"{'PASS' if not failed else 'FAIL: '+failed} |")
    report.extend([
        "",
        "**Overall verdict: "+("DEVELOPMENT_GO" if lr["development_go"]
                              else "DEVELOPMENT_NO_GO")+"**.",
        "",
        "Historical return examples were ALREADY consumed in original native",
        "training. Evaluating their known outcomes is a read-only diagnostic",
        "and proves neither truly held transfer nor scientific advantage.",
        "Even DEVELOPMENT_GO would not be SCIENTIFIC_PASS.",
        "",
        "Full 64 new source events/replica and 32 old witness diagnostic events",
        "are rederived, with prequential forecasts, numeric probabilities,",
        "retained original ledgers and exact final cold checkpoint SHA.",
        "",
        "**SCIENTIFIC_PASS=false. DEPLOYMENT=NONE. DRAFT/UNMERGED.**",
        "No accepted main, Forge controller, owner first-use, model promotion,",
        "extra scheduler, paid API or external trading effects.",
    ])
    (HERE/"README.md").write_text("\n".join(report)+"\n",encoding="utf8")
    print("YGG_RET01_SOURCE_EVIDENCE_SEAL_PASS",
          "DEVELOPMENT_GO" if lr["development_go"] else "DEVELOPMENT_NO_GO",
          "SCIENTIFIC_NOT_PASS",flush=True)


if __name__=="__main__":
    main()

