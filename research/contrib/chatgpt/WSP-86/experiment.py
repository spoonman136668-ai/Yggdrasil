"""WSP86 frozen triple-history coverage developer comparison.

Six fresh UNREGISTERED developer worlds with 3 independently charged 384-action
arms: full 216-triple coverage, original hypothesis-active and random actions.
Numeric / symbolic / fully trained Adam64 controls remain frozen.

Crucially, ALL 18 model prediction bundles are SHA256-sealed BEFORE
ANY evaluator-private truth or hidden private source receipt is queried.
One predeclared outcome, preserving null and negative findings, no reruns
or source tuning on the six frozen development-world seeds.
"""
from __future__ import annotations
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter_ns,process_time_ns

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
sys.path.append(str(HERE.parent/"WSP-85"))
sys.path.append(str(HERE.parent/"WSP-84"))
sys.path.append(str(HERE.parent/"WSP-83"))
sys.path.append(str(HERE.parent/"WSP-82"))

import source
from active_policy import HypothesisInterventionPolicy
from coverage_policy import stage_b_actions,full_triple_coverage
from operator_weights import PaidOperatorInducer
from independent_symbolic import IndependentTruthTableControl
from xor_weights import PaidXorComposer as OldWSP83Xor
from history_adam64 import EndToEndAdamControl as FrozenAdam64

PRE_COMMIT="e1bd60aa10d0cab42a1d81284cb23cc1dd9b6222"
PRE_PARENT="3fe5b6cd664f13bc2a98d22d54c34e00977df68a"
FROZEN={
    "research/contrib/chatgpt/WSP-86/prereg.json":
        "21aeabeea83d96f1e110dfb5d200559070515325",
    "research/contrib/chatgpt/WSP-86/source.py":
        "87507838a7f88059bdeeb52fe06cce77dfa4c426",
    "research/contrib/chatgpt/WSP-86/coverage_policy.py":
        "c77d047c26e9199d5e69c86cd6106d7b98d0ad1e",
    "research/contrib/chatgpt/WSP-85/active_policy.py":
        "76104ff570a62062e66d713138fcd1ed3e4c399b",
    "research/contrib/chatgpt/WSP-84/operator_weights.py":
        "474df711d2a7ea66b96595b3565940a242e20f73",
    "research/contrib/chatgpt/WSP-84/independent_symbolic.py":
        "66c10358ed2ea4c0833f51fc0e1b7d9689551dd3",
    "research/contrib/chatgpt/WSP-84/history_adam64.py":
        "5586b30add3f4c86c6183b9510f352507fad2860",
    "research/contrib/chatgpt/WSP-83/xor_weights.py":
        "55f7f68ae83044345306140d0e0878ff45595178",
    "research/contrib/chatgpt/WSP-80/prereg.json":
        "0e96f4e0eff1ced7f87b754a2ad4fbb75c7b3d58",
}
ARMS=("debruijn_full_triple","WSP85_hypothesis_active","hash_random")

PUBLIC=tuple((state,action,history)
             for history in source.CONTEXTS
             for state in source.STATES for action in source.ACTIONS)
assert len(PUBLIC)==16512


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)


def digest(v):
    return sha256(canonical(v).encode("ascii")).hexdigest()


def git(*args):
    return subprocess.run(("git",)+args,cwd=REPO,text=True,
                          capture_output=True,check=True).stdout.strip()


def admit_frozen_source():
    head=git("rev-parse","HEAD")
    expected=os.getenv("GITHUB_SHA")
    if os.getenv("GITHUB_EVENT_NAME")=="pull_request":
        expected=os.getenv("WSP86_CHECKOUT_HEAD_SHA")
        if not expected:
            raise RuntimeError("missing exact source PR checkout")
    if len(head)!=40 or (expected and head!=expected) or git("status","--porcelain"):
        raise RuntimeError("dirty exact-source checkout or SHA mismatch")
    if git("rev-parse",PRE_COMMIT+"^")!=PRE_PARENT:
        raise RuntimeError("WSP86 preregistration did not precede implementation")
    first="research/contrib/chatgpt/WSP-86/prereg.json"
    if git("rev-parse",PRE_COMMIT+":"+first)!=FROZEN[first]:
        raise RuntimeError("prospective frozen WSP86 prereg blob drift")
    for file,sha in FROZEN.items():
        if git("rev-parse","HEAD:"+file)!=sha:
            raise RuntimeError("changed frozen source or strong comparator: "+file)
    p=json.loads((HERE/"prereg.json").read_text("utf8"))
    worlds=p["worlds"]
    if (p["schema"]!="wsp86.reachable-history-coverage-developer.v1"
            or p["status"]!="FROZEN_BEFORE_IMPLEMENTATION_OR_DEVELOPMENT_OUTCOMES"
            or p["parent"]["commit_sha"]!=PRE_PARENT
            or worlds["unregistered_developer_seeds"]!=list(range(10601,10607))
            or worlds["arms"]!=list(ARMS)
            or worlds["total_physical_paid_actions"]!=6912
            or worlds["stratified_query_counts_per_arm_world"]["total"]!=16512
            or p["authority"]["scientific_first_use"] is not False):
        raise RuntimeError("WSP86 preregistration changed or source scope widened")
    return head,p

def _public_paid_hash(rows):
    return digest([[e.before,e.action,e.after,e.action_cost] for e in rows])


def acquire_independently_paid(world,arm):
    if arm not in ARMS:
        raise PermissionError("arm is outside WSP86 unregistered DEV scope")
    session=world.session()
    numeric=PaidOperatorInducer()
    old=OldWSP83Xor()
    active=HypothesisInterventionPolicy() if arm=="WSP85_hypothesis_active" else None
    rows=[]
    choices=[]
    coverage_plan=None
    for step in range(384):
        if step<144:
            action=source.stage_a_action(world.seed,step)
        elif arm=="debruijn_full_triple":
            if coverage_plan is None:
                coverage_plan=stage_b_actions(tuple(session.actions))
            action=coverage_plan[step-144]
        elif arm=="WSP85_hypothesis_active":
            action=active.choose(step,tuple(session.ledger),tuple(session.actions))
        else:
            action=source.random_stage_b_action(world.seed,step)
        before_history=tuple(session.actions)
        e=session.step(action)
        if e.action_cost!=1:
            raise AssertionError("source gave free uncharged observation")
        numeric.charge(e.before,e.action,e.after,e.action_cost)
        old.charge(e.before,e.action,e.after,e.action_cost)
        rows.append((e.before,e.action,before_history,e.after))
        choices.append(e.action)
    if (len(session.ledger)!=384 or numeric.charges!=384 or
            len(choices)!=384 or len(rows)!=384):
        raise AssertionError("paid no-reset source budget violated")
    if active and active.receipt()["paid_StageB_choices"]!=240:
        raise AssertionError("active source-blind intervention budget violated")
    if arm=="debruijn_full_triple" and full_triple_coverage(
            tuple(session.actions[142:360]))!=216:
        raise AssertionError("the 216 triples did not occur physically")
    return {
        "paid":tuple(session.ledger),
        "neural_rows":tuple(rows),
        "action_history":tuple(choices),
        "numeric":numeric,"old":old,
        "policy_receipt":active.receipt() if active else None,
        "stageA_144_digest":_public_paid_hash(session.ledger[:144]),
        "full_paid_sha256":_public_paid_hash(session.ledger),
        "stageB_action_choices":tuple(choices[144:]),
    }

def memoryless(state,action,history):
    after=list(state)
    after[action]^=1
    return tuple(after)


def paid_lookup(paid):
    observed={}
    conflicts=set()
    past=[]
    for e in paid:
        key=(e.before,e.action,tuple(past[-2:]))
        if key in observed and observed[key]!=e.after:
            conflicts.add(key)
        observed[key]=e.after
        past.append(e.action)
    return lambda state,action,history: (
        None if (state,action,tuple(history[-2:])) in conflicts
        else observed.get((state,action,tuple(history[-2:]))))


def train_and_freeze(world,arm_index,charge):
    start=process_time_ns()
    numeric=charge["numeric"]
    operator_receipt=numeric.compile()
    restored=PaidOperatorInducer.restore(numeric.snapshot())
    cold_sha256=sha256(restored.snapshot().encode("ascii")).hexdigest()
    symbolic=IndependentTruthTableControl(charge["paid"])
    numerical_compile_cpu=process_time_ns()-start
    legacy_incompatible=False
    try:
        charge["old"].compile()
    except ValueError:
        legacy_incompatible=True

    # Independent model initialization by arm; optimizer/restart code and
    # all training data constraints stay source-pinned to prior WSP84.
    Adam=FrozenAdam64(world.seed*10+arm_index)
    start=process_time_ns()
    adam_receipt=Adam.fit(charge["neural_rows"])
    adam_cpu=process_time_ns()-start

    lookup=paid_lookup(charge["paid"])
    predictors=("numeric","symbolic","prior_WSP83_XOR2",
                "memoryless","paid_lookup","Adam64_forced","Adam64_native")
    output={}
    start=process_time_ns()
    for model in predictors:
        readings=[]
        for state,action,history in PUBLIC:
            if model=="numeric":
                answer=restored.predict(state,action,history)
            elif model=="symbolic":
                answer=symbolic.predict(state,action,history)
            elif model=="prior_WSP83_XOR2":
                answer=(None if legacy_incompatible
                        else charge["old"].predict(state,action,history))
            elif model=="memoryless":
                answer=memoryless(state,action,history)
            elif model=="paid_lookup":
                answer=lookup(state,action,history)
            elif model=="Adam64_forced":
                answer=Adam.predict(state,action,history,confidence=False)
            else:
                answer=Adam.predict(state,action,history,confidence=True)
            if answer is not None and (type(answer) is not tuple or len(answer)!=6
                                       or any(type(b) is not int or b not in (0,1)
                                              for b in answer)):
                raise ValueError("invalid frozen public model prediction")
            readings.append(None if answer is None else list(answer))
        output[model]=readings
    predictions_cpu=process_time_ns()-start
    if set(output)!=set(predictors) or any(len(x)!=16512 for x in output.values()):
        raise AssertionError("missing 16512 prelabel public predictions/model")
    paid_pairs=sorted({tuple(e.before)+(e.action,) for e in charge["paid"]})
    envelope={
        "schema":"wsp85.prelabel-all-controlled-model-predictions.v1",
        "source_seed":world.seed,
        "arm":ARMS[arm_index],
        "physically_paid_actions":384,
        "public_queries_per_model":len(PUBLIC),
        "charged_public_pairs":[list(x) for x in paid_pairs],
        "outputs":output,
    }
    sealed=canonical(envelope)
    return {
        "sealed":sealed,
        "prelabel_sha256":sha256(sealed.encode("ascii")).hexdigest(),
        "numeric_snapshot_sha256":cold_sha256,
        "numeric_symbolic_full_parity":output["numeric"]==output["symbolic"],
        "numeric_cold_exact_readout":all(
            restored.predict(s,a,h)==numeric.predict(s,a,h)
            for s,a,h in PUBLIC),
        "operator_receipt":operator_receipt,
        "prior_WSP83_incompatible":legacy_incompatible,
        "Adam64":adam_receipt,
        "numerical_compile_cpu_ns":numerical_compile_cpu,
        "Adam64_fit_cpu_ns":adam_cpu,
        "all_model_predictions_cpu_ns":predictions_cpu,
    }


def score_only_after_all_frozen(world,arm,receipt):
    sealed=receipt["sealed"]
    if sha256(sealed.encode("ascii")).hexdigest()!=receipt["prelabel_sha256"]:
        raise AssertionError("prelabel prediction freeze was altered")
    data=json.loads(sealed)
    if (data["source_seed"]!=world.seed or data["arm"]!=arm
            or data["physically_paid_actions"]!=384
            or data["public_queries_per_model"]!=16512):
        raise AssertionError("private scoring source bound incorrectly")
    # The entire 18-session / all-model prediction portfolio is already
    # sealed by main() BEFORE any call to this evaluator-private method.
    truth=[world.private_truth(history,state,action)
           for state,action,history in PUBLIC]
    charged_pairs={tuple(pair) for pair in data["charged_public_pairs"]}
    scores={}
    for model,outputs in data["outputs"].items():
        result={"correct":0,"wrong_confident":0,"abstain":0,
                "never_paid_state_action_correct":0,
                "never_paid_state_action_total":0}
        by_history_length={
            "cold_start_length_0_1":{"correct":0,"wrong_confident":0,"abstain":0},
            "reachable_length_2":{"correct":0,"wrong_confident":0,"abstain":0}}
        for i,pred in enumerate(outputs):
            state,action,history=PUBLIC[i]
            outcome=("abstain" if pred is None else
                     "correct" if tuple(pred)==truth[i] else "wrong_confident")
            result[outcome]+=1
            stratum=("cold_start_length_0_1" if len(history)<2
                     else "reachable_length_2")
            by_history_length[stratum][outcome]+=1
            if tuple(state)+(action,) not in charged_pairs:
                result["never_paid_state_action_total"]+=1
                if outcome=="correct":
                    result["never_paid_state_action_correct"]+=1
        if (sum(result[k] for k in ("correct","wrong_confident","abstain"))!=16512
                or sum(by_history_length["cold_start_length_0_1"].values())!=2688
                or sum(by_history_length["reachable_length_2"].values())!=13824):
            raise AssertionError("missing or wrong source-private frozen query stratum")
        result["by_history_length"]=by_history_length
        scores[model]=result
    return scores

def classify(records,p):
    t=p["frozen_outcomes"]
    seeds=p["worlds"]["unregistered_developer_seeds"]
    if len(records)!=18:
        raise AssertionError("WSP86 requires exactly 18 independent paid sessions")
    by={}
    for row in records:
        if row["arm"] in by.setdefault(row["seed"],{}):
            raise AssertionError("duplicate paid session for same arm")
        by[row["seed"]][row["arm"]]=row
    if sorted(by)!=seeds or any(set(v)!=set(ARMS) for v in by.values()):
        raise AssertionError("WSP86 worlds or arms were replaced")
    if any(len({r["stageA_144_digest"] for r in v.values()})!=1
           for v in by.values()):
        raise AssertionError("StageA charged-public observations differ across arms")
    novel=[by[s] for s in seeds[:4]]
    cover=lambda v:v["debruijn_full_triple"]
    random=lambda v:v["hash_random"]
    active=lambda v:v["WSP85_hypothesis_active"]
    score=lambda r,stratum,key:r["scores"]["numeric"]["by_history_length"][stratum][key]
    reachable="reachable_length_2"
    cold="cold_start_length_0_1"
    gain_random=sum(score(cover(v),reachable,"correct")-
                    score(random(v),reachable,"correct") for v in novel)
    gain_active=sum(score(cover(v),reachable,"correct")-
                    score(active(v),reachable,"correct") for v in novel)
    options=lambda r:sum(x["operator_candidates"] for x in
                         r["operator_receipt"]["learned_operator_receipts"])
    alternatives_reduced=sum(options(random(v))-options(cover(v))
                             for v in novel)
    cold_abstain=sum(score(cover(v),cold,"abstain") for v in novel)
    reachable_abstain=sum(score(cover(v),reachable,"abstain") for v in novel)
    full_coverage=all(cover(v)["stageB_216_coverage"]==216
                      for v in by.values())
    checks={
        "exact_paid_budget":sum(r["paid_actions"] for r in records)==t["physical_actions_exact"],
        "complete_all_216_triples_on_six_worlds":full_coverage,
        "numeric_symbolic_parity_all_sessions":sum(
            r["numeric_symbolic_full_parity"] for r in records)>=t["numeric_symbolic_prediction_parity_sessions_min"],
        "debruijn_reachable_gain_over_random":gain_random>=t["debruijn_novel_reachable_correct_over_random_min"],
        "debruijn_reachable_gain_over_active":gain_active>=t["debruijn_novel_reachable_correct_over_active_min"],
        "no_debruijn_reachable_confident_wrong":sum(
            score(cover(v),reachable,"wrong_confident") for v in novel)<=t["debruijn_novel_reachable_confident_wrong_max"],
        "no_wrong_increase_over_random":sum(
            score(cover(v),reachable,"wrong_confident")-score(random(v),reachable,"wrong_confident")
            for v in novel)<=t["debruijn_novel_reachable_wrong_increase_vs_random_max"],
        "reduces_competing_operator_programs":alternatives_reduced>=t["unique_operator_candidate_reduction_vs_random_min"],
        "fully_trained_neural_portfolio":sum(r["Adam64"]["fully_trained"]
            for r in records)>=t["neural_baselines_fully_trained_sessions_min"],
        "no_policy_private_truth_access":all(r["policy_receipt"] is None or
            r["policy_receipt"]["any_direct_private_source_lookups"] is False for r in records),
        "cold_numeric_snapshot_parity":all(r["numeric_cold_exact_readout"] for r in records),
        "source_private_scoring_after_all_freezes":True,
        "registered_scientific_first_use_zero":True,
    }
    return {
        "classification":("DEV_COVERAGE_CAUSAL_GAIN" if all(checks.values())
                          else "DEV_COVERAGE_NEGATIVE"),
        "reachability_diagnostic":("DEV_REACHABILITY_BOUND_DIAGNOSIS"
             if full_coverage and reachable_abstain==0 and cold_abstain>0
             else "NO_REACHABILITY_BOUND_DIAGNOSIS"),
        "checks":checks,"passed":sum(checks.values()),"total":len(checks),
        "debruijn_minus_random_reachable_confident_correct":gain_random,
        "debruijn_minus_active_reachable_confident_correct":gain_active,
        "candidate_reduction_vs_random":alternatives_reduced,
        "novel_world_cold_start_abstentions":cold_abstain,
        "novel_world_reachable_history_abstentions":reachable_abstain,
        "independent_physical_triple_coverage":full_coverage,
    }

def main():
    if sys.argv[1:]!=["--frozen-unregistered-dev-only"]:
        raise PermissionError("unregistered WSP86 developer-only source admission")
    sha,p=admit_frozen_source()
    cpu0,wall0=process_time_ns(),perf_counter_ns()
    all_frozen=[]
    for seed in p["worlds"]["unregistered_developer_seeds"]:
        spec={"seed":seed,"family":p["worlds"]["family_by_seed"][str(seed)]}
        for arm_index,arm in enumerate(ARMS):
            world=source.World(seed)
            if world.family!=spec["family"]:
                raise AssertionError("frozen source family drift")
            t=process_time_ns()
            paid=acquire_independently_paid(world,arm)
            acquisition_ns=process_time_ns()-t
            receipt=train_and_freeze(world,arm_index,paid)
            # DO NOT call any private truth or private receipt here.
            all_frozen.append((world,arm,paid,receipt,acquisition_ns))

    # Now and only now has EVERY arm frozen every model's predictions.
    records=[]
    for world,arm,paid,receipt,acquisition_ns in all_frozen:
        scores=score_only_after_all_frozen(world,arm,receipt)
        records.append({
            "seed":world.seed,"family":world.family,"arm":arm,
            "private_source_sha256":world.private_receipt(),
            "paid_public_ledger_sha256":paid["full_paid_sha256"],
            "stageA_144_digest":paid["stageA_144_digest"],
            "stageB_action_choices":list(paid["stageB_action_choices"]),
            "paid_actions":len(paid["paid"]),
            "stageB_216_coverage":full_triple_coverage(tuple(paid["action_history"][142:360])),
            "paid_full_triple_coverage":full_triple_coverage(paid["action_history"]),
            "policy_receipt":paid["policy_receipt"],
            "operator_receipt":receipt["operator_receipt"],
            "prior_WSP83_incompatible":receipt["prior_WSP83_incompatible"],
            "numeric_symbolic_full_parity":receipt["numeric_symbolic_full_parity"],
            "numeric_cold_exact_readout":receipt["numeric_cold_exact_readout"],
            "numeric_cold_snapshot_sha256":receipt["numeric_snapshot_sha256"],
            "all_frozen_model_predictions_sha256":receipt["prelabel_sha256"],
            "Adam64":receipt["Adam64"],
            "paid_acquisition_including_policy_cpu_ns":acquisition_ns,
            "numeric_fit_cpu_ns":receipt["numerical_compile_cpu_ns"],
            "Adam64_training_cpu_ns":receipt["Adam64_fit_cpu_ns"],
            "all_model_inference_cpu_ns":receipt["all_model_predictions_cpu_ns"],
            "scores":scores,
        })
    # Prove every world has exactly the same private parameters across arms.
    for seed in (10601,10602,10603,10604,10605,10606):
        receipts={row["private_source_sha256"] for row in records
                  if row["seed"]==seed}
        if len(receipts)!=1:
            raise AssertionError("arm-world private physics mismatch")
    decision=classify(records,p)
    report={
        "schema":"wsp86.complete-history-coverage-development-result.v1",
        "exact_source_SHA":sha,"frozen_prereg_commit":PRE_COMMIT,
        "frozen_prereg_blob":FROZEN["research/contrib/chatgpt/WSP-86/prereg.json"],
        "protected_scientific_sources_consumed":0,
        "developer_worlds":6,"independently_paid_sessions":len(records),
        "physically_charged_public_actions":sum(r["paid_actions"] for r in records),
        "private_queries_after_all_model_freezes":len(records)*len(PUBLIC),
        "whole_control_portfolio_cpu_ns":process_time_ns()-cpu0,
        "whole_control_portfolio_wall_ns":perf_counter_ns()-wall0,
        "prespecified_development_decision":decision,
        "results":records,
        "scientific_acceptance":"UNVERIFIED",
        "numerical_superiority_to_equal_symbolic":False,
        "unfamiliar_domain_AGI_proof":False,"deployment":"NONE",
    }
    print("WSP86_DEV_RESULT="+canonical(report),flush=True)


if __name__=="__main__":
    main()
