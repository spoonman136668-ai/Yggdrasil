"""Sequential public drift observations versus equal-memory conventional control."""
import json
from retained_transfer_audit import truth
from retained_cell_transfer import RetainedCellTransfer
from conventional_retained_transfer import ConventionalRetainedTransfer,ScratchConventional
from unrestricted_operation_cells import INPUTS

def trial(source,target):
    local=RetainedCellTransfer()
    table=ConventionalRetainedTransfer()
    scratch=ScratchConventional()
    for key in INPUTS:
        for repeat in range(2):
            for learner in (local,table):
                learner.train_source(key,truth(source,key))
    local=RetainedCellTransfer.restore(local.checkpoint())
    stages=[]
    for observed,key in enumerate(INPUTS[:3],1):
        for learner in (local,table,scratch):
            learner.observe_new(key,truth(target,key))
        remaining=INPUTS[observed:]
        scores={}
        for name,learner in (("local",local),("table",table),("scratch",scratch)):
            preds=[learner.predict(key) for key in remaining]
            labels=[truth(target,key) for key in remaining]
            scores[name]={
                "correct":sum(p is not None and p==y for p,y in zip(preds,labels)),
                "wrong":sum(p is not None and p!=y for p,y in zip(preds,labels)),
                "abstentions":sum(p is None for p in preds),
            }
        restored=RetainedCellTransfer.restore(local.checkpoint())
        stages.append({
            "target_observations":observed,
            "unseen_inputs":len(remaining),
            "scores":scores,
            "drift_detected":local.contradiction,
            "cold_restore_exact":all(restored.predict(k)==local.predict(k) for k in INPUTS),
            "checkpoint_bytes":len(local.checkpoint()),
        })
    return {
        "source":source,"target":target,
        "relationship":("same" if source==target else
                       "complement" if source^target==15 else "unrelated"),
        "source_observations":8,
        "target_observations":3,
        "updates":(local.new_observations,table.new_observations,scratch.new_observations),
        "stages":stages,
    }

def run():
    return {
        "runs":[trial(i,j) for i in range(16) for j in range(16)],
        "scope":"256 source-target worlds; sequential target observations, held-out scoring and equal-information conventional memory",
        "limitation":"Undetected drift remains unsafe. Local and conventional learners use the same prior, not autonomous rule discovery.",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
