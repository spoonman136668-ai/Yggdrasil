"""Information sufficiency of all 16 binary composition operations.

For each of four held-out intermediate-message pairs and each of sixteen
different truth tables, train on three public pairs twice each. Score the
unseen pair BEFORE any additional interaction. Then each agent proposes
an information-gaining public query and receives two identical completed
outcomes at that input. Afterwards score again, explicitly counting these
as extra observations/reacquisition, NOT zero-shot generalization.
"""
import json
from time import process_time_ns
from unrestricted_operation_cells import UnrestrictedMessageCells,INPUTS
from conventional_version_space import ConventionalVersionSpace
from multi_regime_online_comparison import deep_bytes

def outcome(mask,inputs):
    return bool(mask>>INPUTS.index(inputs)&1)

def score(prediction,target):
    return {"correct":int(prediction is not None and prediction==target),
            "wrong":int(prediction is not None and prediction!=target),
            "abstention":int(prediction is None)}

def trial(mask,heldout):
    if type(mask) is not int or not 0<=mask<16 or heldout not in INPUTS:
        raise ValueError("FIXTURE_INVALID")
    native=UnrestrictedMessageCells()
    conventional=ConventionalVersionSpace()
    elapsed={"native":0,"conventional":0}
    for pair in INPUTS:
        if pair==heldout:continue
        for _ in range(2):
            for name,model in (("native",native),("conventional",conventional)):
                started=process_time_ns()
                model.observe(pair,outcome(mask,pair))
                elapsed[name]+=process_time_ns()-started
    target=outcome(mask,heldout)
    before={name:score(model.predict(heldout),target)
            for name,model in (("native",native),("conventional",conventional))}
    probes={name:model.informative_probe()
            for name,model in (("native",native),("conventional",conventional))}
    # The sole unresolved pair is selected; it is an explicit PUBLIC probe,
    # not evidence of transfer to an unobserved successor.
    for _ in range(2):
        for name,model in (("native",native),("conventional",conventional)):
            started=process_time_ns()
            model.observe(probes[name],outcome(mask,probes[name]))
            elapsed[name]+=process_time_ns()-started
    after={name:score(model.predict(heldout),target)
           for name,model in (("native",native),("conventional",conventional))}
    return {
        "mask_fixture_only":mask, "heldout":list(heldout),
        "prior_public_observations":6,"additional_public_observations":2,
        "native_observations":native.observations,
        "conventional_observations":conventional.observations,
        "prior_hypothesis_counts":{"native":2,"conventional":2},
        "final_hypothesis_counts":{"native":len(native.possible_operations()),
                                   "conventional":len(conventional.possible_operations())},
        "public_probe":{key:list(value) for key,value in probes.items()},
        "before":before,"after_public_probe":after,"cpu_ns":elapsed,
        "native_python_bytes":deep_bytes(native.cells),
        "conventional_python_bytes":deep_bytes((conventional.remaining,conventional.counts)),
    }

def run():
    rows=[trial(mask,heldout) for mask in range(16) for heldout in INPUTS]
    return {
        "experiments":rows,
        "scope":"All 16 Boolean public-operation families x four target pairs; independent conventional version-space control and matched public probe budget",
        "finding_boundary":"Three observed two-input truth-table points cannot determine unrestricted fourth outcome; querying it is additional observation, not unfamiliar-family transfer.",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
