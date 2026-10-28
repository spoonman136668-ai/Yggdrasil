"""Source-memory contradiction with matched target probes and new learning.

All 16 target functions evaluated after four public source-world episodes.
At each of three probe steps, both learners receive two completed target
outcomes at the selected input. Original source-only learner is a negative
control; recovering learners abandon their inherited explanation after
contradiction, abstaining on unseen inputs until public evidence suffices.
"""
import json
from time import process_time_ns
from unrestricted_operation_cells import INPUTS
from empirical_probe_audit import SOURCE_WORLD_FIXTURE,truth
from empirical_local_probe import EmpiricalLocalProbe
from recovering_local_probe import RecoveringLocalProbe
from recovering_conventional_probe import RecoveringConventionalProbe

def evaluate(model,target):
    keys=[key for key in INPUTS if key not in model.observed]
    preds=[model.predict(key) for key in keys]
    actual=[truth(target,key) for key in keys]
    return {"correct":sum(x is not None and x==y for x,y in zip(preds,actual)),
            "wrong":sum(x is not None and x!=y for x,y in zip(preds,actual)),
            "abstentions":sum(x is None for x in preds),
            "unseen":len(keys)}

def trial(target):
    if type(target) is not int or not 0<=target<16:
        raise ValueError("INVALID_TARGET_FIXTURE")
    agents={"local_recovery":RecoveringLocalProbe(),
            "conventional_recovery":RecoveringConventionalProbe(),
            "source_only":EmpiricalLocalProbe()}
    cpu={name:0 for name in agents}
    for source in SOURCE_WORLD_FIXTURE:
        for key in INPUTS:
            for repeat in range(2):
                for name,agent in agents.items():
                    start=process_time_ns()
                    agent.observe_source(key,truth(source,key))
                    cpu[name]+=process_time_ns()-start
        for agent in agents.values():agent.close_source()
    for agent in agents.values():agent.begin_target()
    stages=[]
    for step in range(1,4):
        key=agents["local_recovery"].select_probe()
        # Compare at the same public input, not only the same budget.
        if key is None:key=next((k for k in INPUTS if k not in agents["local_recovery"].observed),None)
        for name,agent in agents.items():
            if key is None:continue
            repetitions=2 if name!="source_only" else 1
            for _ in range(repetitions):
                start=process_time_ns()
                if (key not in agent.observed or name!="source_only") and (name!="source_only" or agent.remaining()>0):
                    agent.observe_target(key,truth(target,key))
                cpu[name]+=process_time_ns()-start
        stages.append({
            "step":step,
            "public_unique_target_inputs":len(agents["local_recovery"].observed),
            "public_target_feedback":2*step,
            "probe":list(key) if key is not None else None,
            "scores":{name:evaluate(agent,target) for name,agent in agents.items()},
            "fallback":{name:getattr(agent,"fallback",False) for name,agent in agents},
            "remaining_source":{name:agent.remaining() for name,agent in agents.items()},
            "candidate_target_feedback":agents["local_recovery"].public_feedback,
            "conventional_target_feedback":agents["conventional_recovery"].public_feedback,
        })
    return {"target_fixture_only":target,"in_memory_diagnostic":target in SOURCE_WORLD_FIXTURE,
            "public_source_feedback_per_arm":32,"stages":stages,"cpu_ns":cpu}

def run():
    return {"cases":[trial(mask) for mask in range(16)],
            "scope":"Four fully observed source worlds; sixteen target operations; three target probe inputs, two public outcomes each; recovery versus conventional and source-only",
            "limits":"Recovery detects only exhausted source hypotheses, not plausible-but-wrong surviving memories. Unknown targets still need direct public evidence. Prototype Python truth slots, not R7 native cells."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
