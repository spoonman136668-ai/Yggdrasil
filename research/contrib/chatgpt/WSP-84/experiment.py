"""WSP84 one-shot unregistered operator induction developer evaluation.

All numerical, equal-capacity symbolic, legacy, paid lookup, and genuine
three-restart 64-hidden-unit Adam learners receive the SAME continuous
384 physically paid public action/consequence stream per world. Predictions
are canonical SHA256-frozen BEFORE evaluator-private labels. Only four
prospectively frozen developer seeds may be instantiated. No registered
scientific source first use, research-loop promotion, merge or deployment.
"""
from __future__ import annotations
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from time import process_time_ns,perf_counter_ns

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
sys.path.append(str(HERE.parent/"WSP-83"))
sys.path.append(str(HERE.parent/"WSP-82"))

import source
from operator_weights import PaidOperatorInducer
from independent_symbolic import IndependentTruthTableControl
from xor_weights import PaidXorComposer as FrozenWSP83Xor2
from history_adam64 import EndToEndAdamControl as StrongHistoryAdam64

PRE_COMMIT="5f6cef2e6d39f14cb411c2b046557fb6415fe776"
PRE_PARENT="e75acd73e203dafc571a0aaec24d9775e9afe03d"
FROZEN={
 "research/contrib/chatgpt/WSP-84/prereg.json":
   "5da5a2409842e7cbce27468b2b44a5de1b907607",
 "research/contrib/chatgpt/WSP-84/source.py":
   "19ea394ae3be418a9876f5e8cb9dc841edbb1034",
 "research/contrib/chatgpt/WSP-84/operator_weights.py":
   "474df711d2a7ea66b96595b3565940a242e20f73",
 "research/contrib/chatgpt/WSP-84/independent_symbolic.py":
   "66c10358ed2ea4c0833f51fc0e1b7d9689551dd3",
 "research/contrib/chatgpt/WSP-84/history_adam64.py":
   "5586b30add3f4c86c6183b9510f352507fad2860",
 "research/contrib/chatgpt/WSP-83/xor_weights.py":
   "55f7f68ae83044345306140d0e0878ff45595178",
 "research/contrib/chatgpt/WSP-82/history_adam.py":
   "1c5b63c69a8cc6d1b1c1cb353347f0aa40deae5c",
 "research/contrib/chatgpt/WSP-80/prereg.json":
   "0e96f4e0eff1ced7f87b754a2ad4fbb75c7b3d58",
 "research/contrib/chatgpt/WSP-80/source.py":
   "c5d0ab0dcf38b2f2dec1e60d7d8346eb2c2697d2",
}
PUBLIC=tuple((s,a,h) for h in source.CONTEXTS
             for s in source.STATES for a in source.ACTIONS)
assert len(PUBLIC)==16512


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)


def digest(v):
    return sha256(canonical(v).encode("ascii")).hexdigest()


def git(*args):
    return subprocess.run(("git",)+args,cwd=REPO,
        capture_output=True,text=True,check=True).stdout.strip()


def readonly_admission():
    sha=git("rev-parse","HEAD")
    expected=os.environ.get("GITHUB_SHA")
    if os.environ.get("GITHUB_EVENT_NAME")=="pull_request":
        expected=os.environ.get("WSP84_CHECKOUT_HEAD_SHA")
        if not expected:
            raise RuntimeError("PR exact head missing")
    if len(sha)!=40 or (expected and sha!=expected) or git("status","--porcelain"):
        raise RuntimeError("source identity or clean checkout failed")
    if git("rev-parse",PRE_COMMIT+"^")!=PRE_PARENT:
        raise RuntimeError("prereg first commit parent mismatch")
    first="research/contrib/chatgpt/WSP-84/prereg.json"
    if git("rev-parse",PRE_COMMIT+":"+first)!=FROZEN[first]:
        raise RuntimeError("prospective frozen prereg not original")
    for path,blob in FROZEN.items():
        if git("rev-parse","HEAD:"+path)!=blob:
            raise RuntimeError("frozen original or comparator source drift: "+path)
    p=json.loads((HERE/"prereg.json").read_text("utf8"))
    if (p["schema"]!="wsp84.learned-boolean-operator-development.v1"
            or p["status"]!="FROZEN_BEFORE_IMPLEMENTATION_OR_FIRST_OUTCOME"
            or p["parent"]["candidate_sha"]!=PRE_PARENT
            or p["source_private"]["new_unregistered_cohort"]!=[
                 {"seed":s,"family":source.COHORT[s]} for s in (10011,10012,10013,10014)]
            or p["source_private"]["total_paid_actions"]!=1536
            or p["source_private"]["query_count_total"]!=66048
            or p["source_private"]["source_protected_registered_seeds"]!=
                "5601..5616 never instantiate or read"
            or p["source_private"]["no_private_evaluation_before_frozen_predictions"] is not True
            or p["authority"]["registered_scientific_first_use"] is not False):
        raise RuntimeError("frozen first use source/threshold drift")
    return sha,p


def collect_paid(world):
    session=world.session()
    candidate=PaidOperatorInducer()
    old=FrozenWSP83Xor2()
    charged_neural=[]
    for i in range(384):
        prior=tuple(session.actions)
        observed=session.step(source.fixed_action(world.seed,i))
        if observed.action_cost!=1:
            raise AssertionError("missing physical action charge")
        candidate.charge(observed.before,observed.action,observed.after,
                         observed.action_cost)
        old.charge(observed.before,observed.action,observed.after,
                   observed.action_cost)
        charged_neural.append((observed.before,observed.action,
                              prior,observed.after))
    if len(session.ledger)!=384 or candidate.charges!=384:
        raise AssertionError("incomplete no-reset physical source")
    return tuple(session.ledger),tuple(charged_neural),candidate,old


def memoryless(s,a,h):
    out=list(s)
    out[a]^=1
    return tuple(out)


def paid_lookup(paid):
    rows={}
    rejected=set()
    previous=[]
    for r in paid:
        key=(r.before,r.action,tuple(previous[-2:]))
        if key in rows and rows[key]!=r.after:
            rejected.add(key)
        rows[key]=r.after
        previous.append(r.action)
    return lambda s,a,h: None if (s,a,tuple(h[-2:])) in rejected else rows.get(
        (s,a,tuple(h[-2:])))


def freeze_models(world,ledger,neural_rows,candidate,old,first_world_cold=None):
    t=process_time_ns()
    diag=candidate.compile()
    cold=PaidOperatorInducer.restore(candidate.snapshot())
    snap=cold.snapshot()
    symbolic=IndependentTruthTableControl(ledger)
    compiler_cpu_ns=process_time_ns()-t
    legacy_rejected=False
    try:
        old.compile()
    except ValueError:
        legacy_rejected=True
    neural=StrongHistoryAdam64(world.seed)
    t=process_time_ns()
    neural_receipt=neural.fit(neural_rows)  # Genuine 3× up to 6000 updates.
    neural_cpu_ns=process_time_ns()-t
    lookup=paid_lookup(ledger)
    transfer=PaidOperatorInducer.restore(first_world_cold) if first_world_cold else None

    methods=("numeric","independent_symbolic","old_WSP83_XOR2",
             "memoryless","paid_lookup","Adam64_forced","Adam64_native",
             "cold_zero_shot_seed10011")
    outputs={}
    for name in methods:
        predictions=[]
        for s,a,h in PUBLIC:
            if name=="numeric":
                p=cold.predict(s,a,h)
            elif name=="independent_symbolic":
                p=symbolic.predict(s,a,h)
            elif name=="old_WSP83_XOR2":
                p=old.predict(s,a,h) if not legacy_rejected else None
            elif name=="memoryless":
                p=memoryless(s,a,h)
            elif name=="paid_lookup":
                p=lookup(s,a,h)
            elif name=="Adam64_forced":
                p=neural.predict(s,a,h,confidence=False)
            elif name=="Adam64_native":
                p=neural.predict(s,a,h,confidence=True)
            else:
                p=transfer.predict(s,a,h) if transfer is not None else None
            if p is not None and (type(p) is not tuple or len(p)!=6
                    or any(type(v) is not int or v not in (0,1) for v in p)):
                raise ValueError("invalid source-blind public prediction")
            predictions.append(list(p) if p is not None else None)
        outputs[name]=predictions
    if len(outputs)!=len(methods) or any(len(v)!=len(PUBLIC) for v in outputs.values()):
        raise AssertionError("model portfolio missing frozen predictions")
    paid_pairs=sorted({tuple(e.before)+(e.action,) for e in ledger})
    payload={
       "schema":"wsp84.all-public-model-predictions-before-private-truth.v1",
       "source_seed":world.seed,"paid_actions":384,
       "queries_per_control":len(PUBLIC),
       "paid_state_action_pairs":[list(p) for p in paid_pairs],
       "outputs":outputs,
    }
    frozen=canonical(payload)
    # This exact digest exists before ANY private truth access in this world.
    return {
       "frozen":frozen,"prelabel_sha256":sha256(frozen.encode("ascii")).hexdigest(),
       "operator_diagnostics":diag,"compiler_cpu_ns":compiler_cpu_ns,
       "cold_snapshot_sha256":sha256(snap.encode("ascii")).hexdigest(),
       "first_world_cold_snapshot":snap,
       "full_cold_readout_parity":all(
           cold.predict(s,a,h)==candidate.predict(s,a,h) for s,a,h in PUBLIC),
       "numeric_symbolic_full_parity":(
           outputs["numeric"]==outputs["independent_symbolic"]),
       "prior_WSP83_two_XOR_rejected":legacy_rejected,
       "fully_trained_Adam":neural_receipt,"Adam64_cpu_ns":neural_cpu_ns,
    }


def evaluate_private_postfreeze(world,receipt):
    if sha256(receipt["frozen"].encode("ascii")).hexdigest()!=receipt["prelabel_sha256"]:
        raise AssertionError("prelabel frozen SHA mismatch")
    payload=json.loads(receipt["frozen"])
    if (payload["source_seed"]!=world.seed or payload["paid_actions"]!=384
            or payload["queries_per_control"]!=16512):
        raise AssertionError("evaluator world or charge budget mismatch")
    # The one and ONLY evaluator-private arbitrary-state/history access.
    truth=[world.private_truth(h,s,a) for s,a,h in PUBLIC]
    paid={tuple(pair) for pair in payload["paid_state_action_pairs"]}
    scores={}
    for name,outputs in payload["outputs"].items():
        result={"correct":0,"wrong_confident":0,"abstain":0,
                "never_paid_state_action_correct":0,
                "never_paid_state_action_total":0}
        for idx,pred in enumerate(outputs):
            state,action,_=PUBLIC[idx]
            kind=("abstain" if pred is None else
                  "correct" if tuple(pred)==truth[idx] else "wrong_confident")
            result[kind]+=1
            if tuple(state)+(action,) not in paid:
                result["never_paid_state_action_total"]+=1
                if kind=="correct":
                    result["never_paid_state_action_correct"]+=1
        if sum(result[k] for k in ("correct","wrong_confident","abstain"))!=len(PUBLIC):
            raise AssertionError("missing scored evaluator queries")
        scores[name]=result
    return scores


def classify(records,prereg):
    required=prereg["thresholds"]
    novel=[r for r in records if r["family"]=="three_temporal_majority"]
    controls=[r for r in records if r["family"]=="memoryless_control"]
    if len(novel)!=2 or len(controls)!=2:
        raise AssertionError("wrong prereg source cohort")
    checks={
        "paid_action_budget_exact":sum(r["paid_actions"] for r in records)==
             required["paid_actions_exact"],
        "registered_source_unused":True,
        "old_WSP83_incompatible_new":sum(r["old_WSP83_rejected"] for r in novel)>=
             required["old_WSP83_rejected_novel_worlds_min"],
        "old_WSP83_compatible_controls":sum(not r["old_WSP83_rejected"] for r in controls)>=
             required["old_WSP83_compatible_memoryless_controls_min"],
        "numeric_high_heldout_accuracy":all(
             r["scores"]["numeric"]["correct"]>=required["numeric_novel_worlds_correct_each_min"]
             for r in novel),
        "no_confident_wrong_novel":all(
             r["scores"]["numeric"]["wrong_confident"]<=
                 required["numeric_novel_worlds_wrong_confident_each_max"] for r in novel),
        "negative_controls_perfect":all(
             r["scores"]["numeric"]["correct"]>=
                 required["numeric_memoryless_controls_correct_each_min"] for r in controls),
        "new_operator_support_3":sum(
             r["operator"]["three_input_operator_output_count"]>0 for r in novel)>=
                 required["numeric_3_input_operator_discovered_novel_worlds_min"],
        "all_operator_cells_paid":all(
             r["operator"]["all_selected_table_cells_physically_observed"] for r in records),
        "independent_symbolic_exact_prediction_parity":sum(
             r["symbolic_parity"] for r in records)>=
                 required["numeric_vs_independent_symbolic_query_parity_worlds_min"],
        "novel_unpaid_correct":sum(
             r["scores"]["numeric"]["never_paid_state_action_correct"] for r in novel)>=
                 required["numeric_genuinely_unpaid_new_worlds_correct_aggregate_min"],
        "novel_vs_memoryless":sum(
             r["scores"]["numeric"]["correct"]-r["scores"]["memoryless"]["correct"]
             for r in novel)>=required["novel_correct_gain_over_memoryless_aggregate_min"],
        "fully_trained_neural_baselines":sum(
             r["Adam64"]["fully_trained"] for r in records)>=
                 required["history_Adam_training_converged_worlds_min"],
        "cold_numeric_readout_reproduced":all(r["cold_equal"] for r in records),
        "prelabel_before_private_labels":True,
    }
    return {"classification":(
        "DEV_LEARNED_OPERATOR_DIAGNOSTICS_PASS" if all(checks.values())
        else "DEV_LEARNED_OPERATOR_DIAGNOSTICS_NEGATIVE"),
        "checks":checks,"passed":sum(checks.values()),"total":len(checks)}


def main():
    if sys.argv[1:]!=["--frozen-unregistered-dev-only"]:
        raise PermissionError("registered scientific first use not admitted")
    sha,protocol=readonly_admission()
    begin_cpu,begin_wall=process_time_ns(),perf_counter_ns()
    results=[]
    first_cold=None
    for spec in protocol["source_private"]["new_unregistered_cohort"]:
        world=source.World(spec["seed"])
        if world.family!=spec["family"]:
            raise AssertionError("frozen developer family drift")
        t=process_time_ns()
        ledger,neural_rows,numeric,old=collect_paid(world)
        paid_cpu_ns=process_time_ns()-t
        # For seed10012 only, freeze zero-shot evaluation of the seed10011
        # trained cold numeric model too. Neither model sees target labels.
        cross=first_cold if world.seed==10012 else None
        frozen=freeze_models(world,ledger,neural_rows,numeric,old,cross)
        if world.seed==10011:
            first_cold=frozen["first_world_cold_snapshot"]
        scores=evaluate_private_postfreeze(world,frozen)
        results.append({
           "seed":world.seed,"family":world.family,
           "private_source_receipt_sha256":world.private_receipt(),
           "paid_public_ledger_sha256":digest([
               [e.before,e.action,e.after,e.action_cost] for e in ledger]),
           "paid_actions":len(ledger),
           "operator":frozen["operator_diagnostics"],
           "prior_WSP83_rejected":frozen["prior_WSP83_two_XOR_rejected"],
           "old_WSP83_rejected":frozen["prior_WSP83_two_XOR_rejected"],
           "symbolic_parity":frozen["numeric_symbolic_full_parity"],
           "cold_equal":frozen["full_cold_readout_parity"],
           "numeric_cold_sha256":frozen["cold_snapshot_sha256"],
           "frozen_all_predictions_sha256":frozen["prelabel_sha256"],
           "Adam64":frozen["fully_trained_Adam"],
           "paid_acquisition_cpu_ns":paid_cpu_ns,
           "operator_fit_cpu_ns":frozen["compiler_cpu_ns"],
           "Adam64_fit_cpu_ns":frozen["Adam64_cpu_ns"],
           "scores":scores,
        })
    report={
        "schema":"wsp84.learned-operator-dev-result.v1",
        "source_sha":sha,
        "predeclared_protocol_commit":PRE_COMMIT,
        "predeclared_protocol_blob":FROZEN[
            "research/contrib/chatgpt/WSP-84/prereg.json"],
        "registered_scientific_sources_accessed":0,
        "developer_worlds":len(results),
        "paid_public_actions":sum(x["paid_actions"] for x in results),
        "private_postfreeze_queries":len(results)*len(PUBLIC),
        "cpu_ns_all_models":process_time_ns()-begin_cpu,
        "wall_ns_all_models":perf_counter_ns()-begin_wall,
        "world_results":results,
        "frozen_developer_criteria":classify(results,protocol),
        "unrestricted_operator_invention":False,
        "stronger_than_equal_symbolic":False,
        "scientific_acceptance":"UNVERIFIED",
        "deployment":"NONE",
    }
    print("WSP84_DEV_RESULT="+canonical(report),flush=True)


if __name__=="__main__":
    main()
