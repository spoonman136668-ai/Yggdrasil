"""WSP83: one-shot frozen four-world unregistered DEV compositional falsification.

Only private source context evaluator is in this harness; numeric, symbolic,
neural and legacy models are source-blind, receiving one shared continuously
charged public 384-action trajectory per world. All public model predictions
are SHA256 sealed before any evaluator-private counterfactual truth is used.
Unregistered developer evidence is NOT scientific first-use acceptance.
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
sys.path.append(str(HERE.parent/"WSP-82"))
import source
from xor_weights import PaidXorComposer
from independent_symbolic import IndependentSymbolicXorComposer
from temporal_weights import PaidTemporalFeatureEditor as FrozenWSP82SingleAtomEditor
from history_adam import EndToEndAdamControl as FrozenWSP82HistoryAdam

PRE_COMMIT="3339fdb449c37e686668b959fbb1700ffeca35fe"
PRE_PARENT="ccea1458e2328983030bb919fbd07bdfbb570730"
PINNED={
 "research/contrib/chatgpt/WSP-83/prereg.json":"0dbf536d76e9c7827faa313178daa8ae15bf6faa",
 "research/contrib/chatgpt/WSP-83/source.py":"47a9afc85dc1a4fed4900dd4bc85ad7dea4f331b",
 "research/contrib/chatgpt/WSP-83/xor_weights.py":"55f7f68ae83044345306140d0e0878ff45595178",
 "research/contrib/chatgpt/WSP-83/independent_symbolic.py":"6840d0b5ec440f5bd7b454c2017f5b3fa8cd14ac",
 "research/contrib/chatgpt/WSP-82/temporal_weights.py":"79e5fcce5df0954d1ac818cb4b2797eab6a82392",
 "research/contrib/chatgpt/WSP-82/history_adam.py":"1c5b63c69a8cc6d1b1c1cb353347f0aa40deae5c",
 "research/contrib/chatgpt/WSP-80/prereg.json":"0e96f4e0eff1ced7f87b754a2ad4fbb75c7b3d58",
 "research/contrib/chatgpt/WSP-80/source.py":"c5d0ab0dcf38b2f2dec1e60d7d8346eb2c2697d2",
}
PUBLIC=tuple((s,a,h) for h in source.CONTEXTS
             for s in source.STATES for a in source.ACTIONS)
assert len(PUBLIC)==4608


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)


def hash_json(obj):
    return sha256(canonical(obj).encode("ascii")).hexdigest()


def git(*args):
    return subprocess.run(("git",)+args,cwd=REPO,
                          check=True,text=True,capture_output=True).stdout.strip()


def readonly_source_admission():
    sha=git("rev-parse","HEAD")
    expected=os.environ.get("GITHUB_SHA")
    if os.environ.get("GITHUB_EVENT_NAME")=="pull_request":
        expected=os.environ.get("WSP83_CHECKOUT_HEAD_SHA")
        if not expected:
            raise RuntimeError("explicit PR head custody missing")
    if len(sha)!=40 or (expected and expected!=sha) or git("status","--porcelain"):
        raise RuntimeError("dirty or mismatched exact source checkout")
    if git("rev-parse",PRE_COMMIT+"^")!=PRE_PARENT:
        raise RuntimeError("prereg source baseline drift")
    first="research/contrib/chatgpt/WSP-83/prereg.json"
    if git("rev-parse",PRE_COMMIT+":"+first)!=PINNED[first]:
        raise RuntimeError("prospective prereg source did not precede first use")
    for path,blob in PINNED.items():
        if git("rev-parse","HEAD:"+path)!=blob:
            raise RuntimeError("frozen prereg or source changed: "+path)
    prereg=json.loads((HERE/"prereg.json").read_text("utf8"))
    if (prereg["schema"]!="wsp83.xor-composed-feature-development.v1"
            or prereg["state"]!="FROZEN_BEFORE_SOURCE_LEARNER_UNIT_TESTS_OR_OUTCOMES"
            or prereg["parent"]["exact_sha"]!=PRE_PARENT
            or prereg["new_unregistered_cohort"]!=[
                {"seed":s,"family":source.COHORT[s]} for s in (9901,9902,9903,9904)]
            or prereg["source_private"]["paid_actions_total"]!=1536
            or prereg["source_private"]["public_query_count_total"]!=18432
            or prereg["source_private"]["contexts"]!=[list(h) for h in source.CONTEXTS]
            or prereg["source_private"]["registered_or_protected_source_access"] is not False
            or prereg["authority"]["registered_first_use"] is not False):
        raise RuntimeError("frozen developer source contract drift")
    return sha,prereg


def collect_publicly_paid(world):
    session=world.session()
    candidate=PaidXorComposer()
    legacy=FrozenWSP82SingleAtomEditor()
    neural_paid=[]
    for step in range(384):
        history=tuple(session.action_history)
        event=session.step(source.fixed_action(world.seed,step))
        if event.action_cost!=1:
            raise AssertionError("charged source event missing")
        candidate.charge(event.before,event.action,event.after,event.action_cost)
        legacy.charge(event.before,event.action,event.after,event.action_cost)
        neural_paid.append((event.before,event.action,history,event.after))
    if len(session.ledger)!=384 or candidate.charges!=384 or legacy.charges!=384:
        raise AssertionError("paid no-reset source budget violated")
    return tuple(session.ledger),tuple(neural_paid),candidate,legacy


def memoryless(s,a,h):
    x=list(s)
    x[a]^=1
    return tuple(x)


def paid_pair_memory(ledger):
    lookup={}
    conflicts=set()
    history=[]
    for e in ledger:
        key=(e.before,e.action,tuple(history[-2:]))
        if key in lookup and lookup[key]!=e.after:
            conflicts.add(key)
        lookup[key]=e.after
        history.append(e.action)
    return lambda s,a,h: None if (s,a,tuple(h[-2:])) in conflicts else lookup.get(
        (s,a,tuple(h[-2:])))


def fit_freeze_before_private_oracle(world,ledger,neural_paid,candidate,legacy):
    t=process_time_ns()
    learned=candidate.compile()
    restored=PaidXorComposer.restore(candidate.snapshot())
    snapshot=restored.snapshot()
    symbolic=IndependentSymbolicXorComposer(ledger)
    composer_cpu=process_time_ns()-t
    legacy_refused=False
    try:
        legacy.compile()
    except ValueError:
        legacy_refused=True
    model=FrozenWSP82HistoryAdam(world.seed)
    t=process_time_ns()
    adam_receipt=model.fit(neural_paid)
    adam_cpu=process_time_ns()-t
    paid_lookup=paid_pair_memory(ledger)
    outputs={}
    methods=("numeric","symbolic","old_singleton","memoryless",
             "paid_lookup","adam_forced","adam_native")
    for name in methods:
        preds=[]
        for s,a,h in PUBLIC:
            if name=="numeric":
                p=restored.predict(s,a,h)
            elif name=="symbolic":
                p=symbolic.predict(s,a,h)
            elif name=="old_singleton":
                p=legacy.predict(s,a,h) if not legacy_refused else None
            elif name=="memoryless":
                p=memoryless(s,a,h)
            elif name=="paid_lookup":
                p=paid_lookup(s,a,h)
            elif name=="adam_forced":
                p=model.predict(s,a,h,confidence=False)
            else:
                p=model.predict(s,a,h,confidence=True)
            if p is not None and (type(p) is not tuple or len(p)!=6
                                  or any(type(v) is not int or v not in (0,1) for v in p)):
                raise ValueError("invalid public model prediction")
            preds.append(list(p) if p is not None else None)
        outputs[name]=preds
    if set(outputs)!=set(methods) or any(len(v)!=len(PUBLIC) for v in outputs.values()):
        raise AssertionError("model portfolio undercoverage")
    paid_pairs=sorted({tuple(e.before)+(e.action,) for e in ledger})
    payload={
        "schema":"wsp83.public-predictions-pretruth.v1",
        "seed":world.seed,"paid_actions":len(ledger),"query_count":len(PUBLIC),
        "paid_pairs":[list(x) for x in paid_pairs],
        "outputs":outputs,
    }
    sealed=canonical(payload)
    return {
        "seal":sealed,
        "sha256":sha256(sealed.encode("ascii")).hexdigest(),
        "learned":learned,
        "legacy_refused":legacy_refused,
        "symbolic_equal":outputs["numeric"]==outputs["symbolic"],
        "numeric_cold_equal":all(restored.predict(s,a,h)==candidate.predict(s,a,h)
                                 for s,a,h in PUBLIC),
        "cold_weight_sha256":sha256(snapshot.encode("ascii")).hexdigest(),
        "history_adam":adam_receipt,
        "composer_cpu_ns":composer_cpu,
        "adam_cpu_ns":adam_cpu,
    }


def score_after_freeze(world,frozen):
    if sha256(frozen["seal"].encode("ascii")).hexdigest()!=frozen["sha256"]:
        raise AssertionError("sealed model predictions tampered")
    payload=json.loads(frozen["seal"])
    if payload["seed"]!=world.seed or payload["paid_actions"]!=384 or payload["query_count"]!=4608:
        raise AssertionError("evaluator source/coverage changed")
    # Evaluator-private arbitrary-state/context truth is ONLY accessed here,
    # after all source-blind model predictions have been frozen.
    truth=[world.private_truth(h,s,a) for s,a,h in PUBLIC]
    paid={tuple(x) for x in payload["paid_pairs"]}
    scored={}
    for name,all_preds in payload["outputs"].items():
        result={"correct":0,"wrong_confident":0,"abstain":0,
                "genuinely_unpaid_correct":0,"genuinely_unpaid_total":0}
        for idx,p in enumerate(all_preds):
            s,a,_=PUBLIC[idx]
            category=("abstain" if p is None else
                      "correct" if tuple(p)==truth[idx] else "wrong_confident")
            result[category]+=1
            if tuple(s)+(a,) not in paid:
                result["genuinely_unpaid_total"]+=1
                if category=="correct":
                    result["genuinely_unpaid_correct"]+=1
        if sum(result[x] for x in ("correct","wrong_confident","abstain"))!=4608:
            raise AssertionError("incomplete private scoring")
        scored[name]=result
    return scored


def classify(records,prereg):
    t=prereg["thresholds"]
    novel=[r for r in records if r["family"]=="temporal_xor_new"]
    control=[r for r in records if r["family"]=="memoryless_control"]
    if len(novel)!=2 or len(control)!=2:
        raise AssertionError("invalid developer family")
    checks={
        "old_singleton_rejected_both_novel":all(x["old_WSP82_singleton_rejected"] for x in novel),
        "old_singleton_passed_controls":sum(not x["old_WSP82_singleton_rejected"] for x in control)
            >=t["controls_legacy_model_compatible_count_min"],
        "new_numerical_correct":all(x["scores"]["numeric"]["correct"]>=
            t["numeric_new_worlds_confident_correct_each_min"] for x in novel),
        "new_numerical_no_wrong":all(x["scores"]["numeric"]["wrong_confident"]<=
            t["numeric_new_worlds_confident_wrong_each_max"] for x in novel),
        "composed_necessary":sum(x["composer"]["composed_two_atom_XOR_outputs"]>0 for x in novel)
            >=t["new_worlds_learned_two_atom_XOR_count_min"],
        "new_vs_memoryless":sum(x["scores"]["numeric"]["correct"]-
            x["scores"]["memoryless"]["correct"] for x in novel)>=
            t["new_worlds_correct_gain_over_memoryless_total_min"],
        "new_never_paid":sum(x["scores"]["numeric"]["genuinely_unpaid_correct"] for x in novel)>=
            t["new_worlds_correct_genuinely_unpaid_total_min"],
        "control_correct":all(x["scores"]["numeric"]["correct"]>=
            t["control_worlds_numeric_correct_each_min"] for x in control),
        "independent_symbolic_full_parity":sum(x["symbolic_exact_parity"] for x in records)>=
            t["numeric_independent_symbolic_exact_full_parity_worlds_min"],
        "history_Adam_fully_trained":sum(x["history_Adam"]["fully_trained"] for x in records)>=
            t["real_history_Adam_95pct_converged_worlds_min"],
        "numeric_cold_restore":all(x["numeric_cold_full_parity"] for x in records),
        "paid_exact":sum(x["paid_actions"] for x in records)==t["paid_actions_total_exact"],
        "registered_protected_source_unused":True,
    }
    return {
        "classification":"DEV_XOR_COMPOSITION_DIAGNOSTICS_PASS"
           if all(checks.values()) else "DEV_XOR_COMPOSITION_DIAGNOSTICS_NEGATIVE",
        "checks":checks,"passed":sum(checks.values()),"total":len(checks)}


def main():
    if sys.argv[1:]!=["--frozen-unregistered-dev-only"]:
        raise PermissionError("only four frozen unregistered dev worlds admissible")
    exact,prereg=readonly_source_admission()
    started_cpu,started_wall=process_time_ns(),perf_counter_ns()
    records=[]
    for spec in prereg["new_unregistered_cohort"]:
        world=source.World(spec["seed"])
        if world.family!=spec["family"]:
            raise AssertionError("developer source family drift")
        t=process_time_ns()
        ledger,neural,candidate,old=collect_publicly_paid(world)
        acquisition_cpu=process_time_ns()-t
        frozen=fit_freeze_before_private_oracle(
            world,ledger,neural,candidate,old)
        score=score_after_freeze(world,frozen)
        records.append({
            "seed":world.seed,"family":world.family,
            "private_source_sha256":world.private_receipt(),
            "paid_ledger_sha256":hash_json([
                [e.before,e.action,e.after,e.action_cost] for e in ledger]),
            "paid_actions":len(ledger),
            "composer":frozen["learned"],
            "old_WSP82_singleton_rejected":frozen["legacy_refused"],
            "symbolic_exact_parity":frozen["symbolic_equal"],
            "numeric_cold_full_parity":frozen["numeric_cold_equal"],
            "numeric_cold_snapshot_sha256":frozen["cold_weight_sha256"],
            "prelabel_SHA256":frozen["sha256"],
            "history_Adam":frozen["history_adam"],
            "acquisition_cpu_ns":acquisition_cpu,
            "composer_cpu_ns":frozen["composer_cpu_ns"],
            "Adam_training_cpu_ns":frozen["adam_cpu_ns"],
            "scores":score,
        })
    result={
       "schema":"wsp83.composed-feature-developer-result.v1",
       "source_commit":exact,
       "prereg_first_commit":PRE_COMMIT,
       "prereg_blob":PINNED["research/contrib/chatgpt/WSP-83/prereg.json"],
       "registered_WSP80_sources_consumed":0,
       "unregistered_worlds":len(records),
       "paid_actions":sum(x["paid_actions"] for x in records),
       "private_queries":len(records)*len(PUBLIC),
       "cpu_all_controls_ns":process_time_ns()-started_cpu,
       "wall_all_controls_ns":perf_counter_ns()-started_wall,
       "records":records,
       "frozen_diagnostics":classify(records,prereg),
       "open_ended_feature_discovery":False,
       "scientific_acceptance":"UNVERIFIED",
       "deployment":"NONE",
    }
    print("WSP83_DEV_RESULT="+canonical(result),flush=True)


if __name__=="__main__":
    main()
