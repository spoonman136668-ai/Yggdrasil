"""Probe utility learned from public source worlds, with held-out targets.

Fixture source worlds are never passed as candidate masks. Each learner
observes 32 public source outcomes, grouped as four sequential episodes,
then independently constructs its memory. All sixteen target functions
are evaluated, including twelve not represented in source history.
Public target queries and outcomes are identical within matched arms.
"""
import json
from time import process_time_ns
from unrestricted_operation_cells import INPUTS
from empirical_local_probe import EmpiricalLocalProbe
from conventional_empirical_probe import ConventionalEmpiricalProbe

SOURCE_WORLD_FIXTURE=(0,1,3,7)

def truth(mask,key):
    return bool(mask>>INPUTS.index(key)&1)

def grade(model,target):
    unknown=[key for key in INPUTS if key not in model.observed]
    predictions=[model.predict(key) for key in unknown]
    labels=[truth(target,key) for key in unknown]
    return {"correct":sum(p is not None and p==y for p,y in zip(predictions,labels)),
            "wrong":sum(p is not None and p!=y for p,y in zip(predictions,labels)),
            "abstentions":sum(p is None for p in predictions),
            "unseen":len(unknown)}

def trial(target):
    if type(target) is not int or not 0<=target<16:
        raise ValueError("INVALID_PUBLIC_FIXTURE")
    arms={"local_active":EmpiricalLocalProbe(),
          "control_active":ConventionalEmpiricalProbe(),
          "local_fixed":EmpiricalLocalProbe(),
          "control_fixed":ConventionalEmpiricalProbe()}
    cpu={name:0 for name in arms}
    for source in SOURCE_WORLD_FIXTURE:
        for key in INPUTS:
            for _ in range(2):
                for name,agent in arms.items():
                    started=process_time_ns()
                    agent.observe_source(key,truth(source,key))
                    cpu[name]+=process_time_ns()-started
        for agent in arms.values():agent.close_source()
    for agent in arms.values():agent.begin_target()
    stages=[]
    for round_number in (1,2):
        for name,agent in arms.items():
            started=process_time_ns()
            key=agent.select_probe() if name.endswith("active") else INPUTS[round_number-1]
            if key is not None:
                agent.observe_target(key,truth(target,key))
            cpu[name]+=process_time_ns()-started
        stages.append({
            "round":round_number,
            "scores":{name:grade(agent,target) for name,agent in arms.items()},
            "candidate_counts":{name:agent.remaining() for name,agent in arms.items()},
            "public_probe_paths":{name:[list(key) for key in agent.observed]
                                  for name,agent in arms.items()},
            "target_actions":{name:agent.target_actions for name,agent in arms.items()},
        })
    return {
        "target_fixture_only":target,
        "source_member_diagnostic":target in SOURCE_WORLD_FIXTURE,
        "source_public_observations_per_arm":32,
        "stages":stages,
        "cpu_ns":cpu,
    }

def run():
    return {
        "cases":[trial(target) for target in range(16)],
        "scope":"Four observed public source-world episodes, four empirically learned candidate functions; all sixteen target operations, 2 public target probes",
        "limits":"Memory holds only four complete source tables; target outside memory can invalidate all candidates, and a nonempty but incorrect retained set can still predict wrongly. Not native R7 cells or autonomous structural discovery.",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
