"""V22 source-frozen equal-feedback-count local-vs-conventional readout control."""
import itertools,json,os,time
from research.itd02_v18_intermediate_plasticity_audit import target,ridge_predict
from research.itd02_v21_capacity_learning_audit import (
    CONTEXTS,PUBLIC_HISTORIES,design_features,ridge_head_predict)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS
receipt={"schema":"ygg.itd02.v22.equal_per_head_samples.v1","original_native_changed":False,
"scientific_first_use":False,"families":{}}
start=time.process_time()
for family,nonlinear in (("additive",False),("nonadditive",True)):
    total={"local_head_11":0.0,"conventional_public_11":0.0,"conventional_public_35":0.0}
    n=0
    for heldout in CONTEXTS:
        cue,first,action=heldout
        eleven=[(c,f,action) for c,f in PUBLIC_HISTORIES if (c,f)!=(cue,first)]
        assert len(eleven)==11
        full=[t for t in CONTEXTS if t!=heldout]
        assert len(full)==35
        local=ridge_head_predict(
            [design_features(*x,hops=4) for x in eleven],
            [target(*x,nonlinear=nonlinear) for x in eleven],
            design_features(*heldout,hops=4))
        conv11=ridge_predict(eleven,heldout,nonlinear=nonlinear)
        conv35=ridge_predict(full,heldout,nonlinear=nonlinear)
        truth=target(*heldout,nonlinear=nonlinear)
        total["local_head_11"]+=abs(truth-local)
        total["conventional_public_11"]+=abs(truth-conv11)
        total["conventional_public_35"]+=abs(truth-conv35)
        n+=1
    receipt["families"][family]={"folds":n,"total_absolute_error":total,
       "per_head_training_examples":11,"pooled_training_examples":35}
receipt["cpu_seconds"]=time.process_time()-start
assert receipt["families"]["additive"]["folds"]==36
print("ITD02_V22_EQUAL_SAMPLES="+json.dumps(receipt,sort_keys=True))
with open(os.path.join(os.environ["RUNNER_TEMP"],"itd02_v22.json"),"w") as f:json.dump(receipt,f,sort_keys=True,indent=2)
