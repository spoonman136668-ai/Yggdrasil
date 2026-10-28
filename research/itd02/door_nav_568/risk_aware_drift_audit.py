"""Matched risk-aware versus fixed public probes over all 256 worlds.

Four arms receive identical source evidence and exactly N new target
observations: native active, conventional active, native fixed-order,
conventional fixed-order. Score only still-unseen target inputs.
The source truth table is public prior evidence; target mask is fixture only.
"""
import json
from time import process_time_ns
from unrestricted_operation_cells import INPUTS
from risk_aware_drift_probe import RiskAwareLocalProbe
from conventional_active_mutation import ConventionalActiveMutation

def outcome(mask,key):
    return bool(mask>>INPUTS.index(key)&1)

def evaluate(model,target):
    remaining=[key for key in INPUTS if key not in model.observed]
    values=[model.predict(key) for key in remaining]
    labels=[outcome(target,key) for key in remaining]
    return {"correct":sum(v is not None and v==label for v,label in zip(values,labels)),
            "wrong":sum(v is not None and v!=label for v,label in zip(values,labels)),
            "abstentions":sum(v is None for v in values),
            "unseen":len(remaining)}

def trial(source,target):
    if (type(source) is not int or type(target) is not int
        or not 0<=source<16 or not 0<=target<16):
        raise ValueError("INVALID_WORLD_FIXTURE")
    models={
        "native_active":RiskAwareLocalProbe(source),
        "conventional_active":ConventionalActiveMutation(source),
        "native_fixed":RiskAwareLocalProbe(source),
        "conventional_fixed":ConventionalActiveMutation(source),
    }
    clocks={name:0 for name in models}
    stages=[]
    for step in range(1,4):
        for name,model in models.items():
            begin=process_time_ns()
            key=model.select_probe() if name.endswith("active") else INPUTS[step-1]
            model.observe(key,outcome(target,key))
            clocks[name]+=process_time_ns()-begin
        stages.append({
            "new_public_observations":step,
            "scores":{name:evaluate(model,target) for name,model in models.items()},
            "probe_paths":{name:[list(k) for k in model.observed] for name,model in models.items()},
            "remaining_hypotheses":{
                name:len(model.possible) if hasattr(model,"possible") else model.count()
                for name,model in models.items()},
        })
    return {
        "source_fixture_only":source,"target_fixture_only":target,
        "relation":("same" if source==target else
                    "complement" if source^target==15 else "unrelated"),
        "source_observations_per_arm":8,
        "target_observations_per_arm":3,
        "stages":stages,"cpu_ns":clocks,
    }

def run():
    return {
        "runs":[trial(source,target) for source in range(16) for target in range(16)],
        "scope":"Exhaustive 256-world active versus fixed public information-gathering; independent conventional control with identical six-mutation prior",
        "limitations":"Predefined mutation family and complete source table; independent unknown deviations can remain undetectable until sampled. CPU times are Python microbenchmarks.",
    }
if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
