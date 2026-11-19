"""Read-only cross-CKAD41..49 qualification audit.

This script reads preserved GitHub source receipts on disk. It NEVER imports or
executes an experiment campaign and NEVER consumes new science seed data.
Cross-study Brier levels are intentionally NOT aggregated or ranked because
the worlds, observation-policy budgets and examiner types differ.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parent
STUDIES=tuple(range(41,50))
SOURCE={
41:"4458be879af0b0d2bfe068382156da837696e3dc",
42:"290b9a7f0ccd351b62e1bfb8f1de762601663bf2",
43:"e5dda4e582bc4d5d98508536748f4a8c88330442",
44:"4f8dc305f3b1aa2ee3ef2cbf36e9449eac51f10b",
45:"89081c51a101ec6537955d09f0611e65828b2b26",
46:"49f52a79405e0713b9f62eaa3882b32d70fcc0ba",
47:"dc99602f8f9665e7e2bbf40d0ba5422869c1b309",
48:"86075fb964ef2cf032c564993ca2229c6ea20aeb",
49:"2802bdad9f3f52539d8acacce1a639dd0800fc96"}
RUNS={41:44442044268,42:44445368631,43:44495061873,
44:44497581168,45:44500365682,46:44504915242,
47:44507998278,48:44510045592,49:44519725256}
THRESHOLD={41:.015,42:.010,43:.010,44:.010,45:.010,
           46:.015,47:.010,48:.010,49:.010}
NAMES={
41:"Sixteen-source native microanchor memory",
42:"Dual causal template versus discount93",
43:"Two persistent expert route and repair",
44:"Contrastive evidence-conditioned causal recall",
45:"Closed-loop causal intervention selector",
46:"Ground unknown action IDs onto binary actuator classes",
47:"Four-state and four-action XOR effect composition",
48:"State-partition-conditioned four-way effects",
49:"Singleton-exception plus XOR/mod4 causal-operator inference"}
SCOPES={
41:"observed synthetic A-B-A late-phase Brier",
42:"observed synthetic A-B-A late-phase Brier",
43:"observed synthetic A-B-A late-phase Brier",
44:"observed synthetic A-B-A late-phase Brier",
45:"common untrained two-stage intervention probe expected Brier",
46:"on-policy prequential unfamiliar-action + cold return Brier",
47:"common untrained two-action terminal probe expected Brier, XOR worlds",
48:"common untrained two-action terminal probe expected Brier, state-dependent worlds",
49:"common untrained two-action terminal probe expected Brier, mixed XOR/mod4 worlds"}
LIMITS={
41:"Archival eligibility is not good predictive recall; more source snapshots degraded relative to native stream.",
42:"Loses to pre-existing source-trained discount93 control; early return degrades; original learned checkpoint SHA drifts between Linux and Windows (engineering failure despite CI success).",
43:"Additional expert prematurely switches rules and fails retained early-return control; two trained specialists are not sufficient.",
44:"Evidence-conditioned retrieval improves weak comparators but misses strongest-control gain threshold and sustained return.",
45:"Candidate chooses meaningfully different actions but neither independent seed provides required consistent advantage against exact information gain.",
46:"Previously unseen action symbols are grounded to two familiar actuator classes; exact balanced-mapping posterior wins both seeds; no new underlying primitive mechanics.",
47:"True new four-action effects are modeled in research sidecar, but gain over independently trained conventional tabular is about 0.0018; XOR physics remains a predeclared invariant.",
48:"Correct public state partitions recovered from genuine transitions but candidate forecasts equal exact full Bayesian structure; conventional tabular nearly identical.",
49:"Previously unlisted exception and modular-add operator are found in newly extended 16-member grammar; candidate equals exact BMA and conventional tabular gains remain small."}
SPEC={
41:{"source_key":"qualified_source_sha","ci":"ci","case":"results","eng":"engineering_status","sci":"decision"},
42:{"source_key":"exact_scored_source_sha","ci":"ci","case":"research_summary","eng":"engineering_decision","sci":"scientific_decision"},
43:{"source_key":"first_scored_source_sha","ci":"ci","case":"scored_results","eng":"engineering","sci":"decision"},
44:{"source_key":"exact_scored_source_sha","ci":"ci","case":"dev_outcomes","eng":"engineering_decision","sci":"scientific_decision"},
45:{"source_key":"exact_scored_source_sha","ci":"ci","case":"results","eng":"engineering_decision","sci":"scientific_decision"},
46:{"source_key":"exact_scored_source_sha","ci":"ci","case":"results","eng":"engineering_decision","sci":"scientific_decision"},
47:{"source_key":"scored_original_source","ci":"ci","case":"measurements","eng":"engineering_qualification","sci":"scientific_qualification"},
48:{"source_key":"scored_source_sha","ci":"ci","case":"cases","eng":"engineering_qualification","sci":"scientific_qualification"},
49:{"source_key":"first_DEV_scored_sha","ci":"engineering_ci","case":"original_seed_outcomes","eng":"engineering_qualification","sci":"scientific_qualification"}}


def _require(test,message):
    if not test:raise AssertionError(message)


def _scores(n,x):
    if n==41:
        p=x["pooled_brier"]
        return p["native_micro16"],min(p["native_stream"],p["native_anchor32"],p["strongest_conventional"]),"best original native/anchored/conventional"
    if n==42:
        p=x["pooled_late_phase_brier"]
        return p["native_dual_causal"],min(p["causal_discount93"],p["native_stream"],p["strongest_conventional"]),"best native/discounted/conventional"
    if n==43:
        p=x["pooled_late_brier"]
        return p["candidate"],p["best_control"],"best source-trained causal/native control"
    if n==44:
        p=x["pooled_late_two_stage_brier"]
        return p["candidate"],p["best_control_brier"],p["best_control_name"]
    if n==45:
        return x["causal_pooled_candidate_brier"],x["pooled_best_control_brier"],x["pooled_best_control"]
    if n==46:
        p=x["primary_pool"]
        return p["candidate"],p["best_nonprivileged_control_brier"],p["best_nonprivileged_control_name"]
    if n==47:
        p=x["pooled_late_and_return_brier"]
        return p["native_fourway_effect"],p["fully_fitted_tabular"],"fully_fitted_tabular (exact Bayes also compared separately)"
    if n==48:
        p=x["pooled_late_return"]
        return p["candidate"],p["fully_trained_tabular"],"fully_fitted_tabular (exact BMA also compared separately)"
    if n==49:
        p=x["pooled_late_plus_old_return_Brier"]
        return p["discovered_feature_native"],p["unrestricted_tabular"],"unrestricted_tabular (exact BMA also compared separately)"
    raise AssertionError("AUDIT_UNREGISTERED_EXPERIMENT")


def load_archive(n):
    _require(n in STUDIES,"AUDIT_STUDY_UNREGISTERED")
    path=RESEARCH/f"CKAD-{n}"/"dev_screen_report.json"
    return json.loads(path.read_text(encoding="utf-8"))


def analyze():
    items=[]
    for n in STUDIES:
        d=load_archive(n)
        s=SPEC[n]
        _require(d[s["source_key"]]==SOURCE[n],f"CKAD{n}_EXACT_SOURCE_MISMATCH")
        _require(d[s["sci"]]=="DEV_NO_GO",f"CKAD{n}_NOT_PRESERVED_NEGATIVE")
        eng=d[s["eng"]]
        _require(("PASS" in eng) == (n!=42),f"CKAD{n}_ENGINEERING_MISCLASSIFICATION")
        ci=d[s["ci"]]
        run=ci["dev_run"] if n==49 else ci["run_id"]
        _require(run==RUNS[n],f"CKAD{n}_CI_CUSTODY_MISMATCH")
        cases=d[s["case"]]
        _require(len(cases)==2,f"CKAD{n}_DEVELOPMENT_COHORT_SIZE")
        expected_seeds=([41101,41102] if n==41 else [n*1000+111,n*1000+112])
        _require([c["seed"] for c in cases]==expected_seeds,f"CKAD{n}_DEV_SEED_REPETITION_OR_DRIFT")
        rows=[]
        for c in cases:
            candidate,control,control_name=_scores(n,c)
            _require(all(math.isfinite(q) and 0<=q<=1 for q in (candidate,control)),f"CKAD{n}_BAD_SCORE")
            gain=control-candidate
            rows.append({"seed":c["seed"],"candidate_brier":candidate,
                         "specified_comparator":control_name,
                         "comparator_brier":control,
                         "absolute_gain":gain,
                         "minimum_gain_required":THRESHOLD[n],
                         "gain_threshold_met":gain>=THRESHOLD[n]})
        _require(not all(v["gain_threshold_met"] for v in rows),f"CKAD{n}_SCIENTIFIC_NEGATIVE_CONTRADICTION")
        items.append({"study":f"CKAD{n}","mechanism":NAMES[n],
                      "scoring_scope":SCOPES[n],"same_metric_across_studies":False,
                      "engineering":eng,"scientific":"DEV_NO_GO",
                      "original_source_sha":SOURCE[n],
                      "original_ci_run":RUNS[n],"official_full_repo_regression":False,
                      "dev_rows":rows,"finding":LIMITS[n]})
    _require(sum(x["engineering"].find("PASS")>=0 for x in items)==8,
             "AUDIT_ENGINEERING_COUNT_DRIFT")
    _require(items[1]["engineering"]=="NOT_QUALIFIED_CROSS_PLATFORM_CHECKPOINT_DRIFT",
             "AUDIT_CKAD42_CROSS_OS_FAILURE_UNTRACKED")
    _require(all(x["scientific"]=="DEV_NO_GO" for x in items),"AUDIT_SCIENCE_PROMOTION_FORBIDDEN")
    return {"schema":"yggdrasil.ckad41-49.read-only-qualification-audit.v1",
            "authoritative_research_repo":"spoonman136668-ai/Yggdrasil",
            "audited_parent":"e22ec67385cc376ad4e708b19fecf8cb673d5b6c",
            "accepted_main_verified_at_audit":"5e74f8db85b2f5839c42148c0dfba69a88b1a2c9",
            "studies":len(items),"engineering_dev_passes":8,
            "engineering_dev_unqualified":1,
            "scientific_dev_passes":0,"scientific_dev_no_go":9,
            "study_results":items,
            "fatal_interpretation_boundary":"Study scopes/worlds, original actual-action policies, sample counts, and readout test distributions differ. No cross-study averaging, best-algorithm leaderboard or general-intelligence claim.",
            "what_is_missing":[
              "Direct qualified continuity of accepted Yggdrasil native training state: these stacked research files instantiate separate source-trained experimental learners; code stacking is not model-parameter continuity.",
              "An actual genuinely disjoint, unknown-physics held transfer that cannot be solved by the search model's preregistered known-true finite grammar.",
              "Strong information-equivalent fully fitted tabular and exact symbolic baselines, proper causal negative controls, action budget and process compute/bytes measured before promotion.",
              "Interference and cold retention of unrelated previously learned relationships across multiple real training phases, without resets or only task-scripted returns.",
              "Independently governed original held scientific qualification and full final required-platform repo regression on any future candidate."
            ],
            "audit_only":True,"scientific_seeds_consumed_here":[],"accepted_model_changed":False,
            "promotion_authorized":False}


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--pretty",action="store_true")
    args=ap.parse_args()
    record=analyze()
    print("CKAD41_49_AUDIT_REPORT="+json.dumps(record,sort_keys=True,
               indent=2 if args.pretty else None,
               separators=None if args.pretty else (",",":")))
