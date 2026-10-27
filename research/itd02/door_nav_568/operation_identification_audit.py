"""Held-out operation identification with identical public action ownership.

Local and conventional operation learners use the same six-operation
hypothesis family. Native affine and conventional affine comparators retain
their narrower prior. Neither learner knows the fixture operation identity.
"""
import json
from time import process_time_ns
from public_composition_transfer_audit import PAIRS,FRAMES
from operation_learning_cells import OperationLearningCells,OperationMessageCell
from conventional_operation_control import ConventionalOperationControl
from compositional_local_cells import CompositionalLocalCells
from conventional_composition_controls import ConventionalFactorized,ConventionalExactTable

MESSAGES=((False,False),(False,True),(True,False),(True,True))

def trial(heldout,rule_id):
    if type(rule_id) is not int or not 0<=rule_id<6 or heldout not in MESSAGES:
        raise ValueError("EXPERIMENT_INPUT_INVALID")
    local=OperationLearningCells()
    conventional=ConventionalOperationControl()
    affine=CompositionalLocalCells()
    affine_control=ConventionalFactorized()
    exact=ConventionalExactTable()
    models={"local":local,"conventional":conventional,
            "affine":affine,"affine_control":affine_control}
    cpu={k:0 for k in models}
    cpu["exact"]=0
    for index in range(2):
        for pair in PAIRS:
            result=pair[0]^pair[1]
            for _ in range(2):
                for name,learner in models.items():
                    start=process_time_ns()
                    learner.observe_pair(index,pair,result)
                    cpu[name]+=process_time_ns()-start
    for messages in MESSAGES:
        if messages==heldout:continue
        frame=FRAMES[messages[0]]+FRAMES[messages[1]]
        result=OperationMessageCell.operations(*messages)[rule_id]
        for _ in range(2):
            for name,learner in models.items():
                start=process_time_ns()
                learner.observe_final(frame,result)
                cpu[name]+=process_time_ns()-start
            start=process_time_ns()
            exact.observe_final(frame,result)
            cpu["exact"]+=process_time_ns()-start
    final_frame=FRAMES[heldout[0]]+FRAMES[heldout[1]]
    truth=OperationMessageCell.operations(*heldout)[rule_id]
    results={}
    for name,agent in tuple(models.items())+(("exact",exact),):
        prediction=agent.predict(final_frame)
        results[name]={
            "correct":int(prediction is not None and prediction==truth),
            "wrong":int(prediction is not None and prediction!=truth),
            "abstention":int(prediction is None)}
    return {
        "heldout":list(heldout),"operation_id_fixture_only":rule_id,
        "pair_actions":16,"final_actions":6,"total_actions":22,
        "native_observations":local.observations(),
        "conventional_observations":conventional.observations,
        "operation_candidates_remaining":len(local.exchange.survivors()),
        "results":results,"cpu_ns":cpu,
    }

def run():
    rows=[trial(heldout,rule_id) for heldout in MESSAGES for rule_id in range(6)]
    return {"experiments":rows,
            "scope":"Six operation families x four unseen combinations, matched pair/terminal public feedback and independent same-family control",
            "limits":"Predeclared six-operation hypothesis family, synthetic two-stage binary causality, no actual R7 cell checkpoint or original DoorKey acceptance."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
