"""Native persistent property/relationship use on the pinned CKAD01 simulator.

Fixed-full-knowledge training, followed by observability ablation; NOT a repeat
of the old knowledge-exposure benchmark. No new external causal source action.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_property_knowledge import NativePropertyKnowledge

SEEDS=(101,202,303)
CONDITIONS={"FULL":1023,"IRRELEVANT_WITHHELD":112,"RELEVANT_WITHHELD":1023^16,"ZERO":0}


def need(ok,reason):
    if not ok:raise ValueError("CKAD05_"+reason)


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def score(predictions,truth):
    return {"questions":len(truth),"correct":sum(a==b for a,b in zip(predictions,truth)),
            "incorrect":sum(a is not None and a!=b for a,b in zip(predictions,truth)),
            "abstained":sum(a is None for a in predictions),"prediction_sha256":digest(canonical(predictions))}


def cold_process(path,pin,questions):
    code='''import json,sys
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_context_basis import canonical,digest
p=json.load(sys.stdin)
raw=open(p["path"],"rb").read()
m=NativePropertyKnowledge.restore(raw,p["sha"])
out=[m.predict_entity(a,e,x,visible_mask=v) for a,e,x,v in p["questions"]]
print(json.dumps({"answers_sha256":digest(canonical(out)),"count":len(out),"native_properties":m.property_count,"checkpoint_sha256":digest(m.checkpoint())}))
'''
    payload={"path":str(path),"sha":pin,"questions":questions}
    result=subprocess.run([sys.executable,"-B","-c",code],input=canonical(payload),capture_output=True,
        check=True,cwd=path.parent,timeout=90,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1"))
    return json.loads(result.stdout)


def run(out):
    import numpy as np
    from sklearn.tree import DecisionTreeClassifier
    start=time.monotonic()
    source_path=HERE.parent/"CKAD-02/reference-ckad01/CKAD-01-experiment.py"
    need(digest(source_path.read_bytes())=="768922dc0500e94454cc4d6cb16b5556978551214acd3186b47fb326a3f9441d",
         "SOURCE_CODE_PIN")
    source=load_module("ckad05_pinned_original",source_path)
    exact_module=load_module("ckad05_independent_control",HERE.parent/"CKAD-02/campaign.py")
    prior=json.loads((HERE.parent/"CKAD-02/result.json").read_text())
    prior_hashes={c["seed"]:c["fact_source_sha256"] for c in prior["targeted_ckad01_regression"]}
    cases=[]
    for seed in SEEDS:
        namespace=f"ckad01-synthetic:{seed}"
        properties,train_ids,fact_sha=source.make_world(seed)
        need(fact_sha==prior_hashes[seed],"SYNTHETIC_PROPERTY_SOURCE_PIN")
        property_rows=[[e,p,int(properties[e,p])] for e in range(10000) for p in range(10)]
        model=NativePropertyKnowledge(namespace)
        t=time.monotonic()
        model=model.stage_properties(property_rows,digest(canonical(property_rows)),source_namespace=namespace)
        knowledge_seconds=time.monotonic()-t
        need(model.property_count==100000,"BROAD_NATIVE_PROPERTY_COUNT")
        train_x=properties[train_ids];train_y=source.effect(train_x,"C")
        events=[[int(e),1,int(y)] for e,y in zip(train_ids,train_y)]
        t=time.monotonic()
        model=model.stage_relation(0,events,digest(canonical(events)),source_namespace=namespace)
        native_fit_seconds=time.monotonic()-t
        held_ids=source.TEST_IDS.astype(int).tolist()
        held_x=properties[source.TEST_IDS];truth=source.effect(held_x,"C").astype(int).tolist()
        before={name:[model.predict_entity(0,e,1,visible_mask=mask) for e in held_ids]
                for name,mask in CONDITIONS.items()}
        frozen=model.checkpoint();(out/f"seed-{seed}-before-trainingB.json").write_bytes(frozen)
        # Add a distinct relation without overwriting old facts or C weights.
        new_y=source.effect(train_x,"B")
        new_events=[[int(e),1,int(y)] for e,y in zip(train_ids,new_y)]
        after=model.stage_relation(1,new_events,digest(canonical(new_events)),source_namespace=namespace)
        need(model.checkpoint()==frozen,"OLD_MODEL_REWRITTEN")
        need(after._known==model._known and after._values==model._values and
             after._property_sources==model._property_sources,"PROPERTY_FORGETTING")
        need(after.property_count==100000,"PROPERTY_COUNT_AFTER_TRAINING")
        need(after._relations._profiles[0]==model._relations._profiles[0],"OLD_RELATION_WEIGHTS_CHANGED")
        cart=DecisionTreeClassifier(criterion="gini",max_depth=None,min_samples_split=2,
            min_samples_leaf=1,ccp_alpha=0.0,random_state=seed)
        t=time.monotonic();cart.fit(train_x,train_y);cart_fit_seconds=time.monotonic()-t
        need((cart.predict(train_x)==train_y).all(),"CART_NOT_FULLY_FITTED")
        symbolic_rows=[[sum(int(v)<<p for p,v in enumerate(x)),1,int(y)] for x,y in zip(train_x,train_y)]
        symbolic=exact_module.ExactSymbolic(symbolic_rows,2)
        need(symbolic.consistent,"SYMBOLIC_FIT")
        @lru_cache(maxsize=4096)
        def symbolic_partial(values,known):
            unknown=1023^known;subset=unknown;result=None
            while True:
                p=symbolic.predict((values|subset)|1024)
                if p is None or (result is not None and p!=result):return None
                result=p
                if subset==0:return result
                subset=(subset-1)&unknown
        @lru_cache(maxsize=4096)
        def cart_partial(values,known):
            pending=[0];labels=set();tree=cart.tree_
            while pending:
                node=pending.pop();feature=int(tree.feature[node])
                if feature<0:
                    labels.add(int(cart.classes_[int(np.argmax(tree.value[node][0]))]))
                    if len(labels)>1:return None
                elif known&(1<<feature):
                    value=(values>>feature)&1
                    pending.append(int(tree.children_left[node] if value<=tree.threshold[node] else tree.children_right[node]))
                else:
                    pending.extend((int(tree.children_left[node]),int(tree.children_right[node])))
            return next(iter(labels)) if len(labels)==1 else None
        conditions={};all_questions=[];all_answers=[]
        for name,mask in CONDITIONS.items():
            t=time.monotonic()
            answers=[after.predict_entity(0,e,1,visible_mask=mask) for e in held_ids]
            infer_seconds=time.monotonic()-t
            need(answers==before[name],"SEQUENTIAL_OLD_ANSWER_INTERFERENCE")
            t=time.monotonic()
            independent=[];conventional=[]
            for x in held_x:
                values=sum(int(v)<<p for p,v in enumerate(x))&mask
                independent.append(symbolic_partial(values,mask))
                conventional.append(cart_partial(values,mask))
            control_seconds=time.monotonic()-t
            need(answers==independent,"INDEPENDENT_SYMBOLIC_PARTIAL_DRIFT")
            native_score=score(answers,truth)
            need(native_score["incorrect"]==0,"FALSE_NATIVE_CERTAINTY")
            if name in ("FULL","IRRELEVANT_WITHHELD"):
                need(answers==truth,"COMPLETE_OR_IRRELEVANT_KNOWLEDGE_QUALIFICATION")
            if name=="ZERO":need(all(x is None for x in answers),"KNOWLEDGE_FREE_GUESSING")
            conditions[name]={"visible_mask":mask,"native":native_score,
                "independent_symbolic":score(independent,truth),"fully_trained_cart":score(conventional,truth),
                "retrieval_only":score([None]*len(truth),truth),"native_inference_seconds":infer_seconds,
                "control_inference_seconds":control_seconds}
            all_questions.extend([[0,e,1,mask] for e in held_ids]);all_answers.extend(answers)
        raw=after.checkpoint();path=out/f"seed-{seed}-complete-native-knowledge.json";path.write_bytes(raw)
        fresh=cold_process(path,digest(raw),all_questions)
        need(fresh["native_properties"]==100000 and fresh["count"]==len(all_questions)
             and fresh["checkpoint_sha256"]==digest(raw)
             and fresh["answers_sha256"]==digest(canonical(all_answers)),"COLD_NATIVE_KNOWLEDGE_JOIN")
        cases.append({"seed":seed,"source_namespace":namespace,"synthetic_property_source_sha256":fact_sha,
            "native_property_count":100000,"property_values_one":int(properties.sum()),
            "property_values_zero":100000-int(properties.sum()),"initial_relation_events":512,
            "subsequent_relation_events":512,"all_prior_properties_retained":True,
            "prior_relation_weights_unchanged":True,"old_consequence_answers_retained":len(all_questions),
            "cold_queries":fresh["count"],"cold_answers_sha256":fresh["answers_sha256"],
            "checkpoint_bytes":len(raw),"checkpoint_sha256":digest(raw),
            "before_trainingB_checkpoint_sha256":digest(frozen),"contains_entity_consequence_lookup":False,
            "conditions":conditions,"cart_nodes":int(cart.tree_.node_count),"cart_training_accuracy":1.0,
            "native_knowledge_install_seconds":knowledge_seconds,"native_relation_training_seconds":native_fit_seconds,
            "cart_training_seconds":cart_fit_seconds})
    return {"schema":"yggdrasil.ckad05.native-property-join.result.v1",
        "classification":"NATIVE_PERSISTENT_SYNTHETIC_KNOWLEDGE_USE_SUPPORTED",
        "scientific_pass":False,"accepted_native":False,"source_grounding":"PINNED_SYNTHETIC_SIMULATOR_ONLY",
        "historical_knowledge_causal_join_verified":False,"new_original_source_actions":0,
        "original_ckad01_result_rewritten":False,"original_exposure_benchmark_rerun":False,
        "learned_new_unrestricted_family":False,"cases":cases,"wall_seconds":time.monotonic()-start}


def stable(result):
    def clean(x):
        if isinstance(x,dict):return {k:clean(v) for k,v in x.items()
            if not k.endswith("seconds") and k not in ("environment","source_candidate_sha")}
        if isinstance(x,list):return [clean(v) for v in x]
        return x
    return clean(result)


def receipt(result):
    sums={}
    for condition in CONDITIONS:
        sums[condition]={k:sum(c["conditions"][condition]["native"][k] for c in result["cases"])
                         for k in ("questions","correct","incorrect","abstained")}
    return {"classification":result["classification"],"stable_sha256":result["stable_sha256"],
            "source_candidate_sha":result["source_candidate_sha"],"conditions":sums,
            "native_properties_per_seed":100000,"cold_questions":sum(c["cold_queries"] for c in result["cases"]),
            "wall_seconds":result["wall_seconds"]}


def main():
    p=argparse.ArgumentParser();p.add_argument("--output-directory",required=True)
    p.add_argument("--verify-env",action="store_true");args=p.parse_args()
    out=Path(args.output_directory);out.mkdir(parents=True,exist_ok=True)
    result=run(out)
    result["source_candidate_sha"]=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    result["environment"]={"python":sys.version,"platform":platform.platform(),
        "numpy":__import__("numpy").__version__,"sklearn":__import__("sklearn").__version__}
    need(result["wall_seconds"]<=300,"AUDIT_TIME_BUDGET")
    result["stable_sha256"]=digest(canonical(stable(result)))
    if args.verify_env:need(result["stable_sha256"]==json.loads(os.environ["CKAD05_EXPECTED_RESULT"])["stable_sha256"],
                           "WINDOWS_STABLE_REPRODUCTION")
    (out/"campaign-result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("result="+json.dumps(receipt(result),separators=(",",":"),sort_keys=True)+"\n")
    print("CKAD05_NATIVE_KNOWLEDGE="+json.dumps(receipt(result),sort_keys=True),flush=True)


if __name__=="__main__":main()
