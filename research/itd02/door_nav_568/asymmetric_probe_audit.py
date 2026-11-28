"""Unequal-information public probes versus fixed-order and matched control.

All four target worlds are in the candidate set; both arms get identical
prior information, one PUBLIC observation per round, and no target identity.
Assess remaining hypotheses, mistakes and abstentions only on unprobed
target inputs. A lower uncertainty set does not necessarily improve accuracy.
"""
import json
from time import process_time_ns
from asymmetric_probe_cells import LocalAsymmetricProbe,HYPOTHESES
from conventional_asymmetric_probe import ConventionalAsymmetric
from unrestricted_operation_cells import INPUTS

def bit(mask,key):
    return bool((mask>>INPUTS.index(key))&1)

def grade(model,target):
    unknown=[key for key in INPUTS if key not in model.observed]
    guesses=[model.predict(key) for key in unknown]
    labels=[bit(target,key) for key in unknown]
    return {"correct":sum(v is not None and v==y for v,y in zip(guesses,labels)),
            "wrong":sum(v is not None and v!=y for v,y in zip(guesses,labels)),
            "abstentions":sum(v is None for v in guesses),
            "unseen":len(unknown)}

def trial(target):
    if type(target) is not int or target not in HYPOTHESES:
        raise ValueError("TARGET_OUTSIDE_STRESS_FAMILY")
    arms={"local_active":LocalAsymmetricProbe(),
          "conventional_active":ConventionalAsymmetric(),
          "local_fixed":LocalAsymmetricProbe(),
          "conventional_fixed":ConventionalAsymmetric()}
    timings={name:0 for name in arms}
    steps=[]
    for round_number in (1,2):
        for name,model in arms.items():
            begin=process_time_ns()
            key=model.choose() if name.endswith("active") else INPUTS[round_number-1]
            model.observe(key,bit(target,key))
            timings[name]+=process_time_ns()-begin
        steps.append({
            "round":round_number,
            "scores":{name:grade(model,target) for name,model in arms.items()},
            "candidate_counts":{name:model.candidate_count() for name,model in arms.items()},
            "public_probes":{name:[list(key) for key in model.observed] for name,model in arms.items()},
            "actions":{name:model.actions for name,model in arms.items()},
        })
    return {"target_fixture_only":target,"steps":steps,"cpu_ns":timings}

def run():
    cases=[trial(mask) for mask in HYPOTHESES]
    return {"cases":cases,
            "scope":"Four target operations, 2:2 versus 1:3 public probe partition, two sequential matched actions",
            "limits":"Disclosed four-function hypothesis family; local implementation uses replicated shared version space, not autonomous native R7 representation learning; synthetic microtimings only."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
