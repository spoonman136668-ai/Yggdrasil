"""Leave-one-target-world-out risk calibration without held-out leakage.

Four complete SOURCE worlds are learned from public feedback by each arm.
Fifteen other target-world episodes supply prior prediction/outcome history.
The held-out sixteenth world is neither used to set a risk threshold nor
included in calibration updates. Completed prior outcomes are used only
AFTER the pre-feedback prediction was captured. Scored target outcomes
remain entirely unavailable to learners until evaluation.
"""
import json
from time import process_time_ns
from empirical_probe_audit import SOURCE_WORLD_FIXTURE,truth
from empirical_local_probe import EmpiricalLocalProbe
from conventional_empirical_probe import ConventionalEmpiricalProbe
from public_error_calibrator import PublicErrorCalibrator
from unrestricted_operation_cells import INPUTS

ARMS={"local":EmpiricalLocalProbe,"conventional":ConventionalEmpiricalProbe}

def episode(model_type,world):
    model=model_type()
    for mask in SOURCE_WORLD_FIXTURE:
        for key in INPUTS:
            for repeat in range(2):
                model.observe_source(key,truth(mask,key))
        model.close_source()
    model.begin_target()
    snapshots=[]
    for stage in (1,2):
        key=model.select_probe()
        if key is None:
            key=next((x for x in INPUTS if x not in model.observed),None)
        if key is not None and model.remaining()>0:
            model.observe_target(key,truth(world,key))
        otherwise=[x for x in INPUTS if x not in model.observed]
        snapshots.append({
            "stage":stage,
            "actions":model.target_actions,
            "remaining":model.remaining(),
            "predictions":[(x,model.predict(x),truth(world,x)) for x in otherwise],
        })
    return snapshots

def grade(snapshots,calibrator,stage):
    s=snapshots[stage-1]
    result={"correct":0,"wrong":0,"abstentions":0}
    raw=dict(result)
    for _,prediction,actual in s["predictions"]:
        key=(s["actions"],s["remaining"])
        accepted=calibrator.accept(key,prediction)
        for p,bucket in ((prediction,raw),(accepted,result)):
            bucket["abstentions" if p is None else
                   "correct" if p==actual else "wrong"]+=1
    return {"raw":raw,"calibrated":result,
            "actions":s["actions"],"remaining":s["remaining"],
            "unseen":len(s["predictions"])}

def trial(heldout,max_error=0.20):
    if type(heldout) is not int or not 0<=heldout<16:
        raise ValueError("HELDOUT_WORLD_INVALID")
    records={}
    for name,model_type in ARMS.items():
        begin=process_time_ns()
        calibration=PublicErrorCalibrator(min_predictions=5,max_upper_error=max_error)
        training=[]
        for world in range(16):
            if world==heldout:continue
            evidence=episode(model_type,world)
            for stage in evidence:
                key=(stage["actions"],stage["remaining"])
                for _,prediction,truth_label in stage["predictions"]:
                    if prediction is not None:
                        calibration.record_completed(key,prediction,truth_label)
            training.append(world)
        holdout=episode(model_type,heldout)
        scores=[grade(holdout,calibration,stage) for stage in (1,2)]
        records[name]={
            "training_world_count":len(training),
            "heldout_not_in_training":heldout not in training,
            "calibration_predictions":calibration.total(),
            "calibration_bucket_counts":{
                str(key):list(count) for key,count in sorted(calibration.history.items())},
            "scores":scores,
            "cpu_ns":process_time_ns()-begin,
        }
    return {"heldout_fixture_only":heldout,
            "source_member_diagnostic":heldout in SOURCE_WORLD_FIXTURE,
            "arms":records}

def run():
    return {
        "folds":[trial(world) for world in range(16)],
        "scope":"16 leave-one-world-out held-out target folds, 15 past target episodes per fold, pre-feedback calibration labels and matched conventional memory",
        "limits":"Wilson upper risk estimation from tiny synthetic historical episodes; prediction risks are dependent by episode and not a coverage or safety guarantee. Original R7/real DoorKey not evaluated.",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
