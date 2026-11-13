"""WSP85 prospective intervention-quality development experiment.

Six fresh UNREGISTERED developer worlds, three independently physically
paid arms/world, 144 action-identical StageA + 240 active/random/passive
StageB, original WSP84 numerical and symbolic and Adam64 controls.

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
sys.path.append(str(HERE.parent/"WSP-84"))
sys.path.append(str(HERE.parent/"WSP-83"))
sys.path.append(str(HERE.parent/"WSP-82"))

import source
from active_policy import HypothesisInterventionPolicy
from operator_weights import PaidOperatorInducer
from independent_symbolic import IndependentTruthTableControl
from xor_weights import PaidXorComposer as OldWSP83Xor
from history_adam64 import EndToEndAdamControl as FrozenAdam64

PRE_COMMIT="3683e76c5b12d3be41b96ccc5bcc5ee6950b79bf"
PRE_PARENT="f0ac74d8a83ac60fa23e7c4fd20934df50835a33"
FROZEN={
    "research/contrib/chatgpt/WSP-85/prereg.json":
        "24d2cfdbe9342168958308a2472b224f409d9003",
    "research/contrib/chatgpt/WSP-85/source.py":
        "575cb3abfcacf277de6c358df12bee159dfdebe2",
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
    "research/contrib/chatgpt/WSP-80/source.py":
        "c5d0ab0dcf38b2f2dec1e60d7d8346eb2c2697d2",
}
ARMS=("hypothesis_active","hash_random","cyclic_passive")
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
        expected=os.getenv("WSP85_CHECKOUT_HEAD_SHA")
        if not expected:
            raise RuntimeError("missing PR exact head provenance")
    if len(head)!=40 or (expected and head!=expected) or git("status","--porcelain"):
        raise RuntimeError("dirty exact-source checkout or SHA mismatch")
    if git("rev-parse",PRE_COMMIT+"^")!=PRE_PARENT:
        raise RuntimeError("prospective WSP85 freeze parent drift")
    first="research/contrib/chatgpt/WSP-85/prereg.json"
    if git("rev-parse",PRE_COMMIT+":"+first)!=FROZEN[first]:
        raise RuntimeError("scientific WSP85 prereg was not prospectively frozen")
    for file,sha in FROZEN.items():
        if git("rev-parse","HEAD:"+file)!=sha:
            raise RuntimeError("frozen source or model/control code changed: "+file)
    p=json.loads((HERE/"prereg.json").read_text("utf8"))
    specs=p["source"]["unregistered_worlds"]
    if (p["schema"]!="wsp85.discriminating-intervention-development.v1"
            or p["status"]!="FROZEN_BEFORE_SOURCE_POLICY_LEARNER_IMPLEMENTATION_OR_OUTCOMES"
            or p["parent"]["sha"]!=PRE_PARENT
            or specs!=[{"seed":s,"family":source.COHORT[s]}
                       for s in (10201,10202,10203,10204,10205,10206)]
            or p["source"]["arm_names"]!=list(ARMS)
            or p["source"]["paid_actions_per_arm"]!=384
            or p["source"]["physically_paid_actions"]!=6912
            or p["source"]["all_arm_queries"]!=297216
            or p["authority"]["registered_scientific_first_use"] is not False):
        raise RuntimeError("WSP85 frozen protocol mismatch")
    return head,p


def _public_paid_hash(rows):
    return digest([[e.before,e.action,e.after,e.action_cost] for e in rows])


def acquire_independently_paid(world,arm):
    if arm not in ARMS:
        raise PermissionError("undefined or registered arm")
    session=world.session()
    numeric=PaidOperatorInducer()
    old=OldWSP83Xor()
    active=HypothesisInterventionPolicy() if arm=="hypothesis_active" else None
    rows=[]
    charged_history=[]
    for step in range(384):
        if step<144:
            action=source.stage_a_action(world.seed,step)
        elif arm=="hypothesis_active":
            action=active.choose(step,tuple(session.ledger),
                                 tuple(session.actions))
        elif arm=="hash_random":
            action=source.random_stage_b_action(world.seed,step)
        else:
            action=source.passive_stage_b_action(world.seed,step)
        previous=tuple(session.actions)
        e=session.step(action)
        if e.action_cost!=1:
            raise AssertionError("unpaid or free source observation")
        numeric.charge(e.before,e.action,e.after,e.action_cost)
        old.charge(e.before,e.action,e.after,e.action_cost)
        rows.append((e.before,e.action,previous,e.after))
        charged_history.append(e.action)
    if (len(session.ledger)!=384 or len(rows)!=384 or
            numeric.charges!=384 or len(session.actions)!=384):
        raise AssertionError("not all 384 physical actions were paid")
    if active and active.receipt()["paid_StageB_choices"]!=240:
        raise AssertionError("intervention policy did not choose 240 actions")
    return {
        "paid":tuple(session.ledger),
        "neural_rows":tuple(rows),
        "action_history":tuple(charged_history),
        "numeric":numeric,
        "old":old,
        "policy_receipt":active.receipt() if active else None,
        "stageA_144_digest":_public_paid_hash(session.ledger[:144]),
        "full_paid_sha256":_public_paid_hash(session.ledger),
        "stageB_action_choices":tuple(charged_history[144:]),
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
        raise AssertionError("prelabel predictions mutated")
    data=json.loads(sealed)
    if (data["source_seed"]!=world.seed or data["arm"]!=arm
            or data["physically_paid_actions"]!=384
            or data["public_queries_per_model"]!=16512):
        raise AssertionError("private scoring source misbound")
    truth=[world.private_truth(history,state,action)
           for state,action,history in PUBLIC]
    charged_pairs={tuple(pair) for pair in data["charged_public_pairs"]}
    scored={}
    for model,outputs in data["outputs"].items():
        result={"correct":0,"wrong_confident":0,"abstain":0,
                "never_paid_state_action_correct":0,
                "never_paid_state_action_total":0}
        for i,pred in enumerate(outputs):
            state,action,_=PUBLIC[i]
            outcome=("abstain" if pred is None else
                     "correct" if tuple(pred)==truth[i] else "wrong_confident")
            result[outcome]+=1
            if tuple(state)+(action,) not in charged_pairs:
                result["never_paid_state_action_total"]+=1
                if outcome=="correct":
                    result["never_paid_state_action_correct"]+=1
        if sum(result[k] for k in ("correct","wrong_confident","abstain"))!=16512:
            raise AssertionError("scoring omitted frozen evaluator queries")
        scored[model]=result
    return scored


def classify(records,p):
    t=p["predeclared_dev_thresholds"]
    if len(records)!=t["unregistered_worlds_exact"]*3:
        raise AssertionError("missing source worlds/arms")
    by={}
    for row in records:
        by.setdefault(row["seed"],{})[row["arm"]]=row
    if sorted(by)!=[10201,10202,10203,10204,10205,10206] or any(
            set(v)!=set(ARMS) for v in by.values()):
        raise AssertionError("frozen arms/worlds replaced")
    novel=[by[s] for s in (10201,10202,10203,10204)]
    controls=[by[s] for s in (10205,10206)]
    for v in by.values():
        if len({x["stageA_144_digest"] for x in v.values()})!=1:
            raise AssertionError("first 144 physical charged rows differ")
    score=lambda r,k:r["scores"]["numeric"][k]
    chosen=lambda v:v["hypothesis_active"]
    random=lambda v:v["hash_random"]
    passive=lambda v:v["cyclic_passive"]
    active_random_gain=sum(score(chosen(w),"correct")-
                           score(random(w),"correct") for w in novel)
    active_passive_gain=sum(score(chosen(w),"correct")-
                            score(passive(w),"correct") for w in novel)
    alternatives=lambda r:sum(x["operator_candidates"] for x in
                              r["operator_receipt"]["learned_operator_receipts"])
    active_random_reduction=sum(alternatives(random(w))-
                                alternatives(chosen(w)) for w in novel)
    differing_actions=sum(
        sum(a!=r and a!=p for a,r,p in zip(
            w["hypothesis_active"]["stageB_action_choices"],
            w["hash_random"]["stageB_action_choices"],
            w["cyclic_passive"]["stageB_action_choices"]))
        for w in by.values())
    checks={
        "exact_18_sessions":len(records)==t["charged_arm_sessions_exact"],
        "exact_physical_paid_budget":sum(r["paid_actions"] for r in records)==
            t["paid_actions_exact"],
        "numeric_equals_symbolic_all_18":sum(r["numeric_symbolic_full_parity"]
            for r in records)>=t["numerical_symbolic_query_parity_sessions_min"],
        "active_beats_random_correct":active_random_gain>=
            t["active_novel_correct_over_random_aggregate_min"],
        "active_beats_passive_correct":active_passive_gain>=
            t["active_novel_correct_over_passive_aggregate_min"],
        "active_no_confident_wrong":sum(score(chosen(v),"wrong_confident")
            for v in novel)<=t["active_novel_confident_wrong_total_max"],
        "active_novel_16000_correct":sum(
            score(chosen(v),"correct")>=16000 for v in novel)>=
            t["active_novel_worlds_with_at_least_16000_correct_min"],
        "active_genuinely_unpaid_correct":sum(
            score(chosen(v),"never_paid_state_action_correct") for v in novel)>=
            t["active_novel_aggregate_never_paid_correct_min"],
        "active_reduced_ambiguity":active_random_reduction>=
            t["active_minimal_operator_candidate_reduction_vs_random_total_min"],
        "memoryless_controls_perfect":sum(
            score(chosen(v),"correct")==16512 for v in controls)>=
            t["control_worlds_active_perfect_correct_count_min"],
        "neural_full_training_count":sum(r["Adam64"]["fully_trained"]
            for r in records)>=t["neural_baselines_fully_trained_sessions_min"],
        "distinct_interventions":differing_actions>=
            t["active_actions_different_from_random_or_passive_stageB_min"],
        "zero_private_policy_lookup":all(
            r["policy_receipt"] is None or
            r["policy_receipt"]["any_direct_private_source_lookups"] is False
            for r in records),
        "prelabel_freeze_before_private_scoring":True,
        "all_numeric_cold_restorable":all(r["numeric_cold_exact_readout"]
            for r in records),
        "registered_source_first_use_zero":True,
    }
    return {
        "classification":("DEV_INTERVENTION_SELECTION_PASS" if all(checks.values())
                           else "DEV_INTERVENTION_SELECTION_NEGATIVE"),
        "criteria":checks,
        "passed":sum(checks.values()),
        "total":len(checks),
        "active_minus_random_correct_novel_total":active_random_gain,
        "active_minus_passive_correct_novel_total":active_passive_gain,
        "active_minus_random_alternative_models":active_random_reduction,
        "active_nonmatching_actions_vs_both_controls":differing_actions,
    }


def main():
    if sys.argv[1:]!=["--frozen-unregistered-dev-only"]:
        raise PermissionError("unregistered WSP85 developer-only source admission")
    sha,p=admit_frozen_source()
    cpu0,wall0=process_time_ns(),perf_counter_ns()
    all_frozen=[]
    for spec in p["source"]["unregistered_worlds"]:
        seed=spec["seed"]
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
    for seed in (10201,10202,10203,10204,10205,10206):
        receipts={row["private_source_sha256"] for row in records
                  if row["seed"]==seed}
        if len(receipts)!=1:
            raise AssertionError("arm-world private physics mismatch")
    decision=classify(records,p)
    report={
        "schema":"wsp85.hypothesis-intervention-frozen-development-result.v1",
        "exact_source_SHA":sha,"frozen_prereg_commit":PRE_COMMIT,
        "frozen_prereg_blob":FROZEN["research/contrib/chatgpt/WSP-85/prereg.json"],
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
    print("WSP85_DEV_RESULT="+canonical(report),flush=True)


if __name__=="__main__":
    main()
