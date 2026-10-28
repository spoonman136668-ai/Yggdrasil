"""Corroboration gate for empirical memory transfer, including its limits.

A prediction is withheld until K DISTINCT target keys have yielded public
feedback. This only verifies observed examples, not unseen relationships.
All 16 Boolean target worlds and 4 learned source episodes are measured
against the identical-information conventional learner. All scores use
still-unobserved keys; no target identity is visible to the learners.
"""
import json
from time import process_time_ns
from empirical_probe_audit import SOURCE_WORLD_FIXTURE,truth
from empirical_local_probe import EmpiricalLocalProbe
from conventional_empirical_probe import ConventionalEmpiricalProbe
from unrestricted_operation_cells import INPUTS

def score(agent, target, minimum):
    if type(minimum) is not int or minimum not in (1,2,3):
        raise ValueError("CORROBORATION_REQUIRED")
    keys=[key for key in INPUTS if key not in agent.observed]
    predictions=[agent.predict(key) if len(agent.observed)>=minimum else None for key in keys]
    labels=[truth(target,key) for key in keys]
    return {
        "correct":sum(p is not None and p==y for p,y in zip(predictions,labels)),
        "wrong":sum(p is not None and p!=y for p,y in zip(predictions,labels)),
        "abstentions":sum(p is None for p in predictions),
    }

def trial(target):
    if type(target) is not int or not 0<=target<16:
        raise ValueError("PUBLIC_TARGET_FIXTURE_INVALID")
    models={"local":EmpiricalLocalProbe(),"conventional":ConventionalEmpiricalProbe()}
    cpu={name:0 for name in models}
    for source in SOURCE_WORLD_FIXTURE:
        for key in INPUTS:
            for _ in range(2):
                for name,model in models.items():
                    start=process_time_ns()
                    model.observe_source(key,truth(source,key))
                    cpu[name]+=process_time_ns()-start
        for model in models.values():model.close_source()
    for model in models.values():model.begin_target()
    stages=[]
    for round_number in (1,2,3):
        key=models["local"].select_probe()
        if key is None:
            key=next((k for k in INPUTS if k not in models["local"].observed),None)
        if key is not None:
            for name,model in models.items():
                start=process_time_ns()
                model.observe_target(key,truth(target,key))
                cpu[name]+=process_time_ns()-start
        stages.append({
            "round":round_number,
            "probe":list(key) if key is not None else None,
            "actions":{name:model.target_actions for name,model in models.items()},
            "remaining":{name:model.remaining() for name,model in models.items()},
            "scores":{name:{str(k):score(model,target,k) for k in (1,2,3)}
                      for name,model in models.items()},
        })
    return {"target_fixture_only":target,
            "familiar_diagnostic":target in SOURCE_WORLD_FIXTURE,
            "source_actions_per_model":32,
            "stages":stages,"cpu_ns":cpu}

def run():
    return {"cases":[trial(mask) for mask in range(16)],
            "scope":"Source episodes: four x eight completed feedback. Distinct public target probes: up to three. Corroboration thresholds 1, 2, 3; native candidate versus equally informed conventional control.",
            "limits":"Corroboration cannot prove unseen bits; unknown target worlds can retain plausible but wrong remembered explanations. No native R7 integration or retail hardware claim."}
if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
