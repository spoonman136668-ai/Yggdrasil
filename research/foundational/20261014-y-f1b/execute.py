"""Y-F1B DEV-only near-collision falsification of frozen F1 binding models.

A precommitted fixed sinusoid dictionary chooses distinct public sink entities
whose features are most similar to the actual but MISSING link destination.
Models and decision thresholds are frozen from the original F1 development
archive, with no refit, no sealed cohort, and no future-query input to memory.
"""
from __future__ import annotations
import importlib.util,json,hashlib,time
from pathlib import Path
import torch

HERE=Path(__file__).resolve().parent
p=HERE.parent/"20261014-y-f1-binding"/"execute.py"
spec=importlib.util.spec_from_file_location("f1_original",p)
assert spec and spec.loader
f1=importlib.util.module_from_spec(spec);spec.loader.exec_module(f1)
torch.set_num_threads(1)
SEEDS=tuple(range(39024,39048))
FAMILIES=(4,5,6,7)
FROZEN={
 "exact_binding":(7.637099266052246,0.,-3.4067234992980957),
 "identity_similarity":(6.943840980529785,0.,-4.052923202514648),
 "hybrid":(5.795569896697998,3.1492998600006104,-4.036557197570801)}
def hash_public_feature_dictionary():
    with torch.no_grad():
        return f1.old.feature(torch.arange(60000,dtype=torch.long))
def nearest_distinct(table,expected,forbidden):
    with torch.no_grad():
        needle=table[expected]
        scores=table@needle
        scores[expected]=-100.
        for item in forbidden:scores[item]=-100.
        idx=int(torch.argmax(scores))
        sim=float(scores[idx])
    assert idx not in forbidden and idx!=expected and 0<=idx<60000
    return idx,sim
def probe(seed,family,ca,cb,variant,table):
    edges,qs,truth=f1.fixture(seed,family,ca,cb,variant)
    original,_,_,full=f1.old.fixture(seed,family,ca,cb)
    assert len(edges)==12 and len(full)==12
    used=set(x for edge in edges for x in edge)
    stress=[tuple(pair) for pair in edges]
    matches=[]
    for cut,left,next_step in ((ca,2,3),(cb,6,7)):
        if not cut:continue
        broken=(f1.relabel(full[left][0],seed,variant),
                f1.relabel(full[left][1],seed,variant))
        intended=f1.relabel(full[next_step][0],seed,variant)
        assert broken in stress and intended in used
        candidate,cos=nearest_distinct(table,intended,used)
        at=stress.index(broken)
        stress[at]=(broken[0],candidate)
        matches.append({"intended":intended,"alias":candidate,"cosine":cos})
        used.add(candidate)
    assert len(stress)==12
    assert len(set(stress))==12
    exact=[f1.old.exact_reach(stress,*pair,4) for pair in qs]
    assert exact==truth, "ALIASED_GRAMMAR_ORACLE_CHANGED"
    return edges,stress,qs,truth,matches
def evaluate():
    table=hash_public_feature_dictionary()
    models={}
    for name,weights in FROZEN.items():
        model=f1.Gate(name)
        with torch.no_grad():model.weights.copy_(torch.tensor(weights,dtype=torch.float32))
        models[name]=model
    rows=[]
    per={name:{"base_correct":0,"stress_correct":0,
        "base_wrong_positive":0,"stress_wrong_positive":0}
      for name in models}
    cosine=[]
    for seed in SEEDS:
      for fam in FAMILIES:
       for ca in (False,True):
        for cb in (False,True):
          base,stress,qs,truth,aliases=probe(seed,fam,ca,cb,1,table)
          cosine.extend([r["cosine"] for r in aliases])
          x=torch.tensor([base],dtype=torch.int32)
          y=torch.tensor([stress],dtype=torch.int32)
          questions=torch.tensor([qs],dtype=torch.int32)
          record={"seed":seed,"family":fam,"cut_a":ca,"cut_b":cb,
                 "truth":[bool(y) for y in truth],"alias_count":len(aliases),
                 "aliases":aliases,"models":{}}
          for name,m in models.items():
           with torch.no_grad():
            base_answer=(f1.answer(m.make_state(x),questions)>=.5)[0].tolist()
            stress_answer=(f1.answer(m.make_state(y),questions)>=.5)[0].tolist()
           record["models"][name]={"base":[bool(v) for v in base_answer],
             "stress":[bool(v) for v in stress_answer]}
           for label,before,after in zip(truth,base_answer,stress_answer):
            per[name]["base_correct"]+=int(label==before)
            per[name]["stress_correct"]+=int(label==after)
            if not label:
             per[name]["base_wrong_positive"]+=int(before)
             per[name]["stress_wrong_positive"]+=int(after)
          rows.append(record)
    assert len(rows)==384 and len(cosine)==384
    n=len(rows)*2
    negative=sum(int(not v) for row in rows for v in row["truth"])
    assert n==768 and negative==384
    scores={name:{
      **c,
      "base_accuracy":c["base_correct"]/n,
      "stress_accuracy":c["stress_correct"]/n,
      "false_positive_rate_negative":c["stress_wrong_positive"]/negative,
      "baseline_false_positive_rate":c["base_wrong_positive"]/negative}
      for name,c in per.items()}
    eq=scores["exact_binding"]
    sim=scores["identity_similarity"]
    verdict="NEAR_COLLISION_DIAGNOSTIC_INCONCLUSIVE"
    if (eq["stress_accuracy"]>=.9 and
        eq["stress_accuracy"]-sim["stress_accuracy"]>=.10 and
        sim["false_positive_rate_negative"]-eq["false_positive_rate_negative"]>=.10):
        verdict="CODED_EQUALITY_RESISTS_ADVERSARIAL_ID_COLLISIONS"
    return {
      "schema":"yggdrasil.foundation.f1b-adversarial-alias-development.v1",
      "stage":"DEVELOPMENT_ONLY",
      "source_parent":"e3ec4c056c787fcc921baebeea1440ae7034ae77",
      "trained_model_origin_artifact_id":11924759881,
      "model_weights_fixed":{k:list(v) for k,v in FROZEN.items()},
      "source_f1_original_blob":"00831191b4d736cb8c8ce05b2bedda188656fc62",
      "seed_bounds":[39024,39048],
      "family_ids":list(FAMILIES),
      "permutation_variant":1,
      "records":rows,"raw_question_count":n,
      "negative_question_count":negative,
      "mean_near_collision_similarity":sum(cosine)/len(cosine),
      "minimum_near_collision_similarity":min(cosine),
      "candidate_scores":scores,
      "frozen_success_margins":{"min_eq_accuracy":.9,
         "min_eq_minus_sim_accuracy":.10,"min_negative_fp_gap":.10},
      "verdict":verdict,
      "reference_exact_oracle_correct":n,
      "native_state_bytes":576,"model_weight_bytes_float32":12,
      "fixed_coded_exact_equality":True,"fixed_coded_four_hop_search":True,
      "adversarial_aliases_chosen_by_public_similarity":True,
      "learned_entity_binding":False,
      "external_llm_calls":0,"accepted_ref_mutation":False,
      "sealed_cohort_reserved":False,"sealed_first_use":False,
      "full_nci01_acceptance":False}
if __name__=="__main__":print(json.dumps(evaluate(),indent=2,sort_keys=True))
