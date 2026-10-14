"""Y-F1C: frozen transition-identity ablation, development only.

Only the link-to-link *transition signal* is ablated; packed public endpoint
identity, coded query anchor matching, and 4-hop traversal remain programmed.
Consequently no outcome here is evidence of learned variable identity.
"""
from __future__ import annotations
import importlib.util,json,time
from pathlib import Path
import torch
HERE=Path(__file__).resolve().parent
src=HERE.parent/"20261014-y-f1b"/"execute.py"
spec=importlib.util.spec_from_file_location("yf1b_frozen",src)
assert spec and spec.loader
f1b=importlib.util.module_from_spec(spec);spec.loader.exec_module(f1b)
f1=f1b.f1
torch.set_num_threads(1)
SEEDS=range(39720,39744)
FAMILIES=(4,5,6,7)
ARMS=("frozen_exact_binding","frozen_hybrid","frozen_similarity",
      "hybrid_without_transition_identity","hybrid_misplaced_transition_identity")
def native_state(facts,form):
    if form in ("frozen_exact_binding","frozen_hybrid","frozen_similarity"):
        name={"frozen_exact_binding":"exact_binding","frozen_hybrid":"hybrid",
              "frozen_similarity":"identity_similarity"}[form]
        m=f1.Gate(name)
        with torch.no_grad():
            m.weights.copy_(torch.tensor(f1b.FROZEN[name],dtype=torch.float32))
            return m.make_state(facts)
    with torch.no_grad():
        w=f1b.FROZEN["hybrid"]
        eq,sim=f1.signals(facts)
        if form=="hybrid_without_transition_identity":
            eq=torch.zeros_like(eq)
        else:
            eq=eq.roll(shifts=1,dims=2)
        p=torch.sigmoid(w[0]*eq+w[1]*sim+w[2])
        p=p*(~torch.eye(12,dtype=torch.bool)).to(p)
        packed=((facts[:,:,0]<<16)|facts[:,:,1]).to(torch.int32).view(torch.float32)
        state=torch.cat((packed,p[:,f1.MASK]),dim=-1)
        assert state.shape[-1]==144 and state.element_size()==4
        return state
def evaluate():
    started=time.perf_counter()
    table=f1b.hash_public_feature_dictionary()
    rows=[]
    score={m:{"base_correct":0,"stress_correct":0,"stress_wrong_positive":0,
             "base_wrong_positive":0,"prediction_flips":0} for m in ARMS}
    alias_count=0
    for seed in SEEDS:
      for family in FAMILIES:
       for ca in (False,True):
        for cb in (False,True):
         base,stress,qs,truth,aliases=f1b.probe(seed,family,ca,cb,1,table)
         alias_count+=len(aliases)
         bx=torch.tensor([base],dtype=torch.int32)
         sx=torch.tensor([stress],dtype=torch.int32)
         questions=torch.tensor([qs],dtype=torch.int32)
         row={"seed":seed,"family":family,"cut_a":ca,"cut_b":cb,
              "truth":[bool(v) for v in truth],"models":{}}
         for arm in ARMS:
          with torch.no_grad():
           ba=(f1.answer(native_state(bx,arm),questions)>=.5)[0].tolist()
           sa=(f1.answer(native_state(sx,arm),questions)>=.5)[0].tolist()
          row["models"][arm]={"base":[bool(v) for v in ba],
                              "stress":[bool(v) for v in sa]}
          for t,a,b in zip(truth,ba,sa):
           z=score[arm]
           z["base_correct"]+=int(a==t)
           z["stress_correct"]+=int(b==t)
           z["base_wrong_positive"]+=int((not t) and a)
           z["stress_wrong_positive"]+=int((not t) and b)
           z["prediction_flips"]+=int(a!=b)
         rows.append(row)
    neg=sum(int(not t) for row in rows for t in row["truth"])
    assert len(rows)==384 and neg==384 and alias_count==384
    out={name:{**s,
      "base_accuracy":s["base_correct"]/768,
      "stress_accuracy":s["stress_correct"]/768,
      "base_false_positive_rate":s["base_wrong_positive"]/384,
      "stress_false_positive_rate":s["stress_wrong_positive"]/384}
      for name,s in score.items()}
    intact=out["frozen_hybrid"]["stress_accuracy"]
    removed=out["hybrid_without_transition_identity"]["stress_accuracy"]
    verdict="TRANSITION_IDENTITY_DEPENDENCE_UNRESOLVED"
    if intact>=.95 and removed<=.75 and intact-removed>=.20:
      verdict="CODED_TRANSITION_IDENTITY_REQUIRED_IN_THIS_HYBRID"
    return {"schema":"yggdrasil.foundation.f1c.transition-identity-dev.v1",
     "stage":"DEVELOPMENT_ONLY","parent_commit":"5399db8cba82e4e322b44e0646e056cffd1da864",
     "parent_artifact_id":11925094585,"new_dev_seed_bounds":[39720,39744],
     "families":list(FAMILIES),"rows":rows,"candidate_scores":out,
     "registered_verdict":verdict,"states":384,"questions":768,
     "negative_questions":neg,"alias_count":alias_count,
     "resident_state_bytes":576,"frozen_model_weights":f1b.FROZEN,
     "learned_identity":False,"fixed_coded_query_anchors":True,
     "fixed_coded_four_hop_search":True,"fixed_public_id_packing":True,
     "model_retrained":False,"sealed_first_use":False,"accepted_ref_mutation":False,
     "external_llm_calls":0,"wall_ms":round((time.perf_counter()-started)*1000)}
if __name__=="__main__":
 print(json.dumps(evaluate(),sort_keys=True,indent=2))
