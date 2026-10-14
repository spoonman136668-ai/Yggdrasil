"""Y078: previously unseen source affine-family transfer of Y077 frozen public decoder."""
import importlib.util,json
from pathlib import Path
p=Path(__file__).resolve().parent.parent/"20261014-y077-address-aware-decoder"/"execute.py"
spec=importlib.util.spec_from_file_location("y077_frozen",p)
assert spec and spec.loader
y077=importlib.util.module_from_spec(spec);spec.loader.exec_module(y077)

DEV=tuple(range(9632,9640))
HELDOUT=tuple(range(9680,9696))
NEW_FAMILIES=((3,7,11),(5,9,15),(7,13,9),(11,5,3))

def run():
    old=(y077.DEV,y077.HELDOUT,y077.y076.FAMILIES)
    try:
        y077.DEV,y077.HELDOUT=DEV,HELDOUT
        y077.y076.FAMILIES=NEW_FAMILIES
        result=y077.run()
    finally:
        y077.DEV,y077.HELDOUT,y077.y076.FAMILIES=old
        y077.m.y49.restore_environment()
    assert result["sealed_heldout_seeds"]==HELDOUT
    trials=result["paired_trials"]
    assert len(trials)==1152
    assert set(tuple(r["family"]) for r in trials)==set(NEW_FAMILIES)
    assert all(len(r["arms"])==5 for r in trials)
    breakdown=[]
    for pair in ((4,11),(5,12)):
        for onset in ("onset1","onset4"):
            for family in NEW_FAMILIES:
                cohort=[r for r in trials if tuple(r["pair"])==pair and
                        r["regime"]==onset and tuple(r["family"])==family]
                assert len(cohort)==16*3
                sensed=sum(r["arms"]["new_dual_corrected"]["first_detection"] is not None
                           for r in cohort)
                baseline=sum(r["arms"]["new_dual_detect_only"]["post_detection_mismatch_episodes"]
                             for r in cohort)
                fixed=sum(r["arms"]["new_dual_corrected"]["post_detection_mismatch_episodes"]
                          for r in cohort)
                old_total=sum(r["arms"]["old_dual_corrected"]["mismatch_episodes"]
                              for r in cohort)
                new_total=sum(r["arms"]["new_dual_corrected"]["mismatch_episodes"]
                              for r in cohort)
                safe=(sensed==48 and baseline>0 and fixed<=.8*baseline and new_total<old_total)
                breakdown.append({"pair":pair,"onset":onset,"family":family,
                                  "new_detections":sensed,"baseline_post":baseline,
                                  "corrected_post":fixed,"old_total":old_total,
                                  "new_total":new_total,"safe":safe})
    assert len(breakdown)==16
    if not result["steady_zero_mismatches_and_detections"]:
        label="STEADY_SAFETY_FAILURE"
    elif all(v["safe"] for v in breakdown):
        label="ALL_NEW_AFFINE_FAMILIES_SAFE"
    elif result["classification"]=="DUAL_TOPOLOGY_SAFE_RECOVERY":
        label="AGGREGATE_ONLY_AFFINE_TRANSFER"
    else:
        label="PARTIAL_OR_FAILED_NEW_AFFINE_TRANSFER"
    return {"schema":"yggdrasil.y078-unseen-affine-transfer.v1",
            "parent_head":"1069457f6a5b301686ec0e0edf674d7970818e7c",
            "classification":label,"parent_original_classification":result["classification"],
            "sealed_heldout_seeds":HELDOUT,"development_seeds":DEV,
            "new_affine_families":NEW_FAMILIES,"breakdown":breakdown,
            "comparisons":result["comparisons"],"paired_trials":trials,
            "groups":result["groups"],
            "fixed_public_reads_per_trial":10,"active":7,"retained_limit":9,
            "steady_zero_mismatches_and_detections":result["steady_zero_mismatches_and_detections"],
            "model_calls":0,"accepted_ref_mutation":False,
            "claim_limit":"Fixed two-geometry sensor+decoder transfer to four new affine families; no unseen geometry/RSI claim."}
if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
