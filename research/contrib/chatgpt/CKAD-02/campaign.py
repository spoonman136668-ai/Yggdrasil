"""Frozen CKAD02–04 native-module qualification; not external causal science."""
from __future__ import annotations
import argparse
from functools import lru_cache
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import NativeContextBasis, canonical, digest, SOURCE_KIND
from yggdrasil.native_factual_weights import NativeFactualWeights
from yggdrasil.native_knowledge_activation import PINNED_MANIFEST_SHA, _check_pinned

SEEDS = (101, 202, 303)
DEGREES = (11, 5, 3, 2, 1)
INPUTS = 2048
TRAIN = 512


def need(ok, reason):
    if not ok:
        raise ValueError("CKAD_CAMPAIGN_" + reason)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def address(slot):
    return (slot, False) if slot < 7 else (slot - 7, True)


def fit(model, slot, rows, degree):
    local, retained = address(slot)
    return model.stage_fit(local, rows, digest(canonical(rows)),
                           max_degree=degree, retained=retained)


def predict(model, slot, masks):
    local, retained = address(slot)
    return [model.predict(local, x & 1023, x >> 10, retained=retained) for x in masks]


def score(predictions, outcomes):
    return {"correct": sum(p == y for p, y in zip(predictions, outcomes)),
            "incorrect": sum(p is not None and p != y for p, y in zip(predictions, outcomes)),
            "abstained": sum(p is None for p in predictions), "questions": len(outcomes),
            "prediction_sha256": digest(canonical(predictions))}


@lru_cache(maxsize=16384)
def independent_features(mask, degree):
    # Independently constructed feature SETS; never calls the native feature row.
    active = [i for i in range(11) if mask & (1 << i)]
    return frozenset(sum(1 << i for i in combination)
        for width in range(min(degree, len(active)) + 1)
        for combination in itertools.combinations(active, width))


class ExactSymbolic:
    """Independent lowest-pivot set-XOR fitter and query elimination."""
    def __init__(self, rows, degree):
        self.degree = degree
        self.equations = {}
        self.consistent = True
        for context, action, label in rows:
            variables = set(independent_features(context | (action << 10), degree))
            value = label
            while variables:
                pivot = min(variables)
                old = self.equations.get(pivot)
                if old is None:
                    self.equations[pivot] = (frozenset(variables), value)
                    break
                variables.symmetric_difference_update(old[0]); value ^= old[1]
            else:
                if value:
                    self.consistent = False
                    return

    def predict(self, mask):
        if not self.consistent:
            return None
        variables = set(independent_features(mask, self.degree)); value = 0
        while variables:
            old = self.equations.get(min(variables))
            if old is None:
                return None
            variables.symmetric_difference_update(old[0]); value ^= old[1]
        return value


def dataset(seed, slot):
    selected = sorted(range(INPUTS), key=lambda x:digest(canonical([seed, "train", x])))[:TRAIN]
    selected = sorted(selected)
    training_inputs = set(selected)
    held = [x for x in range(INPUTS) if x not in training_inputs]
    degree = (1, 2, 3, 5)[slot // 4]
    high = [m for m in range(1, INPUTS) if m.bit_count() == degree]
    low = [m for m in range(INPUTS) if m.bit_count() < degree]
    key = lambda m:digest(canonical([seed, slot, m]))
    coefficients = sorted(sorted(high, key=key)[:3] + sorted(low, key=key)[:2])
    def outcome(mask):
        return sum((mask & term) == term for term in coefficients) & 1
    rows = [[x & 1023, x >> 10, outcome(x)] for x in selected]
    truth = [outcome(x) for x in held]
    return rows, held, truth, degree


def cart_fit(rows, held, seed):
    import numpy as np
    from sklearn.tree import DecisionTreeClassifier
    x = np.array([[((c | (a << 10)) >> i) & 1 for i in range(11)] for c,a,y in rows], dtype=np.uint8)
    y = np.array([r[2] for r in rows], dtype=np.uint8)
    query = np.array([[(v >> i) & 1 for i in range(11)] for v in held], dtype=np.uint8)
    model = DecisionTreeClassifier(criterion="gini", max_depth=None,
        min_samples_split=2, min_samples_leaf=1, ccp_alpha=0.0, random_state=seed)
    started = time.monotonic(); model.fit(x, y); training = time.monotonic() - started
    need((model.predict(x) == y).all(), "CART_NOT_FULLY_FITTED")
    started = time.monotonic(); answers = model.predict(query).astype(int).tolist()
    return answers, {"training_seconds": training, "inference_seconds":time.monotonic()-started,
                     "nodes": int(model.tree_.node_count), "training_accuracy": 1.0}


def representation_audit():
    sources = {}
    cart = {}
    for seed in SEEDS:
        for slot in range(16):
            data = dataset(seed, slot); sources[seed,slot] = data
            answers, timing = cart_fit(data[0], data[1], seed)
            cart[seed,slot] = {"score": score(answers, data[2]), **timing}
    cases = []
    for degree in DEGREES:  # Complete declared basis FIRST.
        for seed in SEEDS:
            for slot in range(16):
                rows, held, truth, true_degree = sources[seed,slot]
                model = NativeContextBasis()
                started = time.monotonic()
                try:
                    learned = fit(model, slot, rows, degree)
                    fitted = True
                except ValueError as exc:
                    need(str(exc) == "CKAD_NATIVE_MODEL_CLASS_INADEQUATE", "UNEXPECTED_NATIVE_FAILURE")
                    learned = model; fitted = False
                native_fit = time.monotonic() - started
                started = time.monotonic(); answers = predict(learned, slot, held)
                native_infer = time.monotonic() - started
                started = time.monotonic(); control = ExactSymbolic(rows, degree)
                control_fit = time.monotonic() - started
                started = time.monotonic(); independent = [control.predict(x) for x in held]
                control_infer = time.monotonic() - started
                need(fitted == control.consistent and answers == independent, "INDEPENDENT_SYMBOLIC_DRIFT")
                local, retained = address(slot)
                info = learned.profile_info(local, retained=retained)
                result = {"seed":seed,"address":slot,"true_fixture_degree":true_degree,
                    "declared_basis_degree":degree,"source_sha256":digest(canonical(rows)),
                    "native_fitted":fitted,"rank":info["rank"],
                    "feature_count":sum(__import__("math").comb(11,k) for k in range(degree+1)),
                    "native":score(answers,truth),"exact_symbolic":score(independent,truth),
                    "retrieval_only":score([None]*len(held),truth),"fully_trained_cart":cart[seed,slot],
                    "native_training_seconds":native_fit,"native_inference_seconds":native_infer,
                    "symbolic_training_seconds":control_fit,"symbolic_inference_seconds":control_infer}
                if degree == 11:
                    need(fitted and result["native"]["abstained"] == len(held), "COMPLETE_BASIS_EXTRAPOLATED")
                if degree == 3 and true_degree <= 3:
                    need(fitted and info["rank"] == info["feature_count"]
                         and result["native"]["correct"] == len(held), "DECLARED_CUBIC_QUALIFICATION")
                cases.append(result)
    return cases, sources


def cold_process(checkpoint, pin, queries):
    code = '''import json,sys
from yggdrasil.native_context_basis import NativeContextBasis,canonical,digest
p=json.load(sys.stdin)
b=open(p["path"],"rb").read()
m=NativeContextBasis.restore(b,p["sha"])
answers=[m.predict(a,c,x,retained=r) for a,c,x,r in p["queries"]]
print(json.dumps({"checkpoint_sha":digest(m.checkpoint()),"answers_sha":digest(canonical(answers)),"count":len(answers)}))
'''
    payload={"path":str(checkpoint),"sha":pin,"queries":queries}
    result=subprocess.run([sys.executable,"-B","-c",code],input=canonical(payload),capture_output=True,
        check=True,timeout=90,cwd=checkpoint.parent,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1"))
    return json.loads(result.stdout)


def persistence_and_repair(sources, out):
    persistence=[]; repairs=[]
    for seed in SEEDS:
        model=NativeContextBasis()
        for slot in range(8): model=fit(model,slot,sources[seed,slot][0],3)
        frozen=model.checkpoint()
        old=[predict(model,slot,range(INPUTS)) for slot in range(8)]
        failure=None
        try: fit(model,8,sources[seed,8][0],2)
        except ValueError as exc: failure=str(exc)
        need(failure=="CKAD_NATIVE_MODEL_CLASS_INADEQUATE" and model.checkpoint()==frozen,
             "EXPECTED_REPRESENTATION_FAILURE_NOT_PRESERVED")
        repaired=fit(model,8,sources[seed,8][0],3)
        repaired_answers=predict(repaired,8,sources[seed,8][1])
        need(repaired_answers==sources[seed,8][2],"BOUNDED_REPRESENTATION_REPAIR")
        need(old==[predict(repaired,slot,range(INPUTS)) for slot in range(8)],"REPAIR_INTERFERENCE")
        repair_file=out/f"seed-{seed}-repaired.json";repair_file.write_bytes(repaired.checkpoint())
        fail_file=out/f"seed-{seed}-frozen-before-repair.json";fail_file.write_bytes(frozen)
        repairs.append({"seed":seed,"original_failure":failure,"changed_addresses":1,
            "same_source_sha256":digest(canonical(sources[seed,8][0])),
            "original_checkpoint_sha256":digest(frozen),"repaired_checkpoint_sha256":repaired.checkpoint_sha256,
            "correct_unseen":len(repaired_answers),"incorrect_unseen":0,"earlier_outputs_unchanged":True})
        for slot in range(8,12): model=fit(model,slot,sources[seed,slot][0],3)
        need(old==[predict(model,slot,range(INPUTS)) for slot in range(8)],"SEQUENTIAL_INTERFERENCE")
        raw=model.checkpoint();cold=NativeContextBasis.restore(raw,digest(raw))
        need(cold.checkpoint()==raw,"COLD_BYTES")
        path=out/f"seed-{seed}-learned.json";path.write_bytes(raw)
        queries=[];expected=[]
        for slot in range(12):
            local,retained=address(slot)
            for x in sources[seed,slot][1][:128]:
                queries.append([local,x&1023,x>>10,retained])
                expected.append(model.predict(local,x&1023,x>>10,retained=retained))
        fresh=cold_process(path,digest(raw),queries)
        need(fresh["checkpoint_sha"]==digest(raw) and fresh["answers_sha"]==digest(canonical(expected)),
             "FRESH_PROCESS_INFERENCE_DRIFT")
        persistence.append({"seed":seed,"retained_old_queries":8*INPUTS,"old_outputs_unchanged":True,
            "cold_process_queries":fresh["count"],"cold_process_answers_sha256":fresh["answers_sha"],
            "checkpoint_bytes":len(raw),"checkpoint_sha256":digest(raw),"contains_event_lookup_table":False})
    return persistence,repairs


def archive_regression():
    path=HERE/"reference-ckad01/CKAD-01-experiment.py"
    need(digest(path.read_bytes())=="768922dc0500e94454cc4d6cb16b5556978551214acd3186b47fb326a3f9441d",
         "ORIGINAL_CKAD01_SOURCE_HASH")
    original=load_module("ckad01_frozen_reference",path)
    from sklearn.tree import DecisionTreeClassifier
    cases=[]
    for seed in SEEDS:
        properties,train_ids,fact_sha=original.make_world(seed)
        x=properties[train_ids]; y=original.effect(x,"C")
        rows=[[sum(int(v)<<i for i,v in enumerate(features)),1,int(label)] for features,label in zip(x,y)]
        model=fit(NativeContextBasis(),0,rows,2)
        held=properties[original.TEST_IDS]; truth=original.effect(held,"C").astype(int).tolist()
        masks=[sum(int(v)<<i for i,v in enumerate(features)) for features in held]
        answers=[model.predict(0,mask,1) for mask in masks]
        old_rules=original.fit_pair_native(x,y)
        old=original.predict_pair_native(old_rules,held).astype(int).tolist()
        symbolic=original.fit_exact_symbolic_independent(x,y)
        need(old==original.predict_exact_independent(symbolic,held).astype(int).tolist(),"OLD_SYMBOLIC_DRIFT")
        cart=DecisionTreeClassifier(max_depth=None,random_state=seed).fit(x,y)
        need((cart.predict(x)==y).all(),"REGRESSION_CART_UNTRAINED")
        trained={r[0] for r in rows}
        new_indices=[i for i,m in enumerate(masks) if m not in trained]
        need(answers==truth,"ARCHIVED_MAJORlTY_NATIVE_REGRESSION")
        cases.append({"seed":seed,"synthetic_source_facts":100000,"fact_source_sha256":fact_sha,
            "public_training_events":512,"unique_training_contexts":len(trained),
            "previous_pair_learner_covered":sum(v>=0 for v in old),"native":score(answers,truth),
            "native_unseen_contexts":score([answers[i] for i in new_indices],[truth[i] for i in new_indices]),
            "fully_trained_cart":score(cart.predict(held).astype(int).tolist(),truth),
            "native_rank":model.profile_info(0)["rank"],"action_zero_claim":False,
            "post_CKAD01_exploratory_regression_only":True})
    return cases


def historical_audit(zip_path):
    cache=load_module("ckad_compiled_cache",HERE.parent/"NKR-25/campaign.py")
    with tempfile.TemporaryDirectory(prefix="ckad-history-") as temp:
        directory=cache.unpack_cache(zip_path,Path(temp)/"image")
        with NativeFactualWeights(directory/"facts.uint32le",directory/"manifest.json",PINNED_MANIFEST_SHA) as source:
            _check_pinned(source)
            model=NativeContextBasis();frozen=model.checkpoint();h=hashlib.sha256()
            rejected=0
            for i in range(100000):
                triple=source.row_at((i*(len(source)-1))//99999)
                h.update(__import__("struct").pack("<III",*triple))
                try: model.stage_fit(0,[list(triple)],"0"*64,source_kind="historical_train_QPQ")
                except ValueError as exc:
                    need(str(exc)=="CKAD_NATIVE_CAUSAL_GROUNDING_OR_SOURCE_AUTHORITY_ABSENT","GROUNDING_REFUSAL")
                    rejected+=1
                else: raise AssertionError("HISTORICAL_FACT_FALSE_CAUSAL_ADMISSION")
            need(model.checkpoint()==frozen,"HISTORICAL_FACTS_MUTATED_CAUSAL_MODEL")
            return {"full_image_rows":len(source),"relations":source.manifest["distinct_relation_types"],
                "image_sha256":source.manifest["packed_sha256"],"indexed_historical_witnesses":100000,
                "witness_digest":h.hexdigest(),"causal_labels_admitted":0,"typed_rejections":rejected,
                "grounding_join_verified":False,"stored_facts_are_understanding":False}


def stable(result):
    def clean(value):
        if isinstance(value,dict):
            return {k:clean(v) for k,v in value.items()
                    if not k.endswith("seconds") and k not in ("environment","source_candidate_sha")}
        if isinstance(value,list):return [clean(x) for x in value]
        return value
    return clean(result)


def compact_receipt(result):
    summary=[]
    for degree in DEGREES:
        cases=[c for c in result["CKAD02_cases"] if c["declared_basis_degree"]==degree]
        summary.append({"degree":degree,"datasets":len(cases),
            "fitted":sum(c["native_fitted"] for c in cases),
            "correct":sum(c["native"]["correct"] for c in cases),
            "incorrect":sum(c["native"]["incorrect"] for c in cases),
            "abstained":sum(c["native"]["abstained"] for c in cases)})
    return {"source_candidate_sha":result["source_candidate_sha"],
            "stable_sha256":result["stable_sha256"],"classification":result["classification"],
            "wall_seconds":result["wall_seconds"],"degree_summary":summary,
            "archive_regression_correct":sum(c["native"]["correct"] for c in result["targeted_ckad01_regression"]),
            "archive_regression_questions":sum(c["native"]["questions"] for c in result["targeted_ckad01_regression"])}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--compiled-image-zip",required=True)
    parser.add_argument("--output-directory",required=True);parser.add_argument("--verify-env",action="store_true")
    args=parser.parse_args();out=Path(args.output_directory);out.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();historical=historical_audit(args.compiled_image_zip)
    cases,sources=representation_audit();persistence,repairs=persistence_and_repair(sources,out)
    regression=archive_regression()
    result={"schema":"yggdrasil.ckad02-04.native-context-qualification.result.v1",
        "classification":"NATIVE_DECLARED_BASIS_QUALIFICATION_SUPPORTED",
        "scientific_pass":False,"accepted_native":False,"new_original_source_actions":0,
        "historical_resource":historical,"CKAD02_cases":cases,"CKAD03":persistence,"CKAD04":repairs,
        "targeted_ckad01_regression":regression,"original_ckad01_failure_rewritten":False,
        "new_unfamiliar_relationship_family_discovered":False,
        "source_candidate_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "environment":{"python":sys.version,"platform":platform.platform(),
                       "numpy":__import__("numpy").__version__,"sklearn":__import__("sklearn").__version__},
        "wall_seconds":time.monotonic()-start}
    need(result["wall_seconds"]<=900,"PRIMARY_TIME_BUDGET")
    result["stable_sha256"]=digest(canonical(stable(result)))
    if args.verify_env:
        expected=json.loads(os.environ["CKAD02_EXPECTED_RESULT"])
        need(result["stable_sha256"]==expected["stable_sha256"],"WINDOWS_REPRODUCTION_DRIFT")
    (out/"campaign-result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("result="+json.dumps(compact_receipt(result),separators=(",",":"),sort_keys=True)+"\n")
    print("CKAD02_04_RESULT="+json.dumps(compact_receipt(result),sort_keys=True),flush=True)


if __name__=="__main__":main()
