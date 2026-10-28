"""V21 locked V20 source-only paired same-head relay gain ablation."""
import itertools,json,os,statistics
from research.itd02_v18_intermediate_plasticity_audit import target,train_candidate,ridge_predict
from research.itd02_v20_responsibility_gated_audit import read_v20
from yggdrasil.itd02_v20_causal_credit_dev import ResponsibilityGatedRingDev
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES
from yggdrasil.itd02_v18_intermediate_plasticity_dev import INITIAL_GAIN
cases=list(itertools.product(PUBLIC_CUES,ACTIONS,ACTIONS))
assert len(cases)==36
output={}
for nonlinear in (False,True):
    records=[]
    for heldout in cases:
        m=ResponsibilityGatedRingDev()
        training=[c for c in cases if c!=heldout]
        for _ in range(16):
            for cue,first,second in training:
                train_candidate(m,cue,first,second,target(cue,first,second,nonlinear=nonlinear))
        learned,reset,size=read_v20(m,heldout)
        truth=target(*heldout,nonlinear=nonlinear)
        changed=sum(abs(g-INITIAL_GAIN) for row in m.gains for g in row)
        records.append({"case":list(heldout),"truth":truth,
            "learned_error":abs(learned-truth),"reset_error":abs(reset-truth),
            "gain_displacement_l1":changed,"checkpoint_bytes":size})
    output["nonlinear" if nonlinear else "additive"]={
      "folds":len(records),
      "mean_error_learned":statistics.mean(x["learned_error"] for x in records),
      "mean_error_reset":statistics.mean(x["reset_error"] for x in records),
      "reset_better":sum(x["reset_error"]+1e-10<x["learned_error"] for x in records),
      "reset_worse":sum(x["reset_error"]>x["learned_error"]+1e-10 for x in records),
      "near_tie":sum(abs(x["reset_error"]-x["learned_error"])<=1e-10 for x in records),
      "mean_gain_displacement_l1":statistics.mean(x["gain_displacement_l1"] for x in records),
      "max_checkpoint_bytes":max(x["checkpoint_bytes"] for x in records),
      "per_case":records}
receipt={"schema":"itd02.v21.same-head-gain-ablation.source-only.v1",
"source_sha":os.environ["PARENT_SHA"],"family_count":2,"total_folds":72,
"fitted_head_weights_identical":True,"original_native_training":False,
"scientific_first_use":False,"results":output}
assert all(v["reset_better"]+v["reset_worse"]+v["near_tie"]==36 for v in output.values())
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_v21_ablation.json"),"w") as f:json.dump(receipt,f,sort_keys=True,indent=2)
print("ITD02_V21_ABLATION="+json.dumps({k:{a:b for a,b in v.items() if a!="per_case"} for k,v in output.items()},sort_keys=True))
