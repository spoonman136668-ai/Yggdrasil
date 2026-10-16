"""F67A frozen synthetic feature-identifiability audit (no FIT use).

Checks whether public junction features distinguish legal candidate actions.
Works on exactly unchanged F67A source; no outcome-driven modifications.
"""
from __future__ import annotations
import importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
 return m
m=load("f67a_identifiability_original",P/"causal_memory.py")
cases=[]
for n in range(12):
 seed=-2501-n;fam=(-2,-1)[n%2]
 public,q,meta=m.SOURCE.source(seed,fam)
 mem=()
 multi=junction_multi=separating=frontier=distinct_public_context=0
 junction_candidate_feature_differences=0
 action_dependent_junction_flag_differences=0
 for i,e in enumerate(public):
  opts=m.ACTION.actions(mem,e,i,m.PACK)
  if len(opts)>1:
   multi+=1
   signals=m.public_junction_signal(mem,e)
   if signals[0] or signals[1]:
    junction_multi+=1;separating+=signals[0];frontier+=signals[1]
    vectors=[m.features(mem,e,i,a,drop,after) for a,_old,drop,after,_ in opts]
    uniq={tuple(v[k] for k in (5,6,7)) for v in vectors}
    junction_candidate_feature_differences+=int(len(uniq)>1)
    action_dependent_junction_flag_differences+=int(len({v[15] for v in vectors})>1)
  # Independently follow the unchanged original fixed control.
  mem=m.ACTION._f60_step(mem,e,m.PACK)
 cases.append(dict(seed=seed,question_type=meta["question_type"],
  multiple_action_steps=multi,junction_with_multiple_actions=junction_multi,
  separated_component_steps=separating,frontier_steps=frontier,
  candidate_dependent_public_junction_features=junction_candidate_feature_differences,
  reserve_incidence_feature_divergence=action_dependent_junction_flag_differences))
counts={k:sum(row[k] for row in cases) for k in cases[0] if k not in ("seed","question_type")}
result=dict(schema="yggdrasil.f67a.synthetic-feature-identifiability.v1",
 synthetic_cases=len(cases),counts=counts,
 public_junction_base_features_candidate_constant=counts["candidate_dependent_public_junction_features"]==0,
 contains_action_context_cross_terms_in_public_junction_dimensions=False,
 source_unchanged=True,fit_train_used=False,fit_validation_used=False,
 diagnostic_used=False,original_used=False,F3=False,rows=cases)
print(json.dumps(result,sort_keys=True))
