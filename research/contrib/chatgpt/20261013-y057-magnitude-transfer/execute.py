"""Y057: new-cohort hedged public-landmark schedule stress under novel shock offsets."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y056-mixture-regret"/"execute.py"
spec=importlib.util.spec_from_file_location("y56_pinned",SOURCE)
assert spec and spec.loader
y56=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y56)
y53=y56.y53
y49=y56.y55.y49
y46=y49.y46

DEV=tuple(range(2496,2504))
HELDOUT=tuple(range(2504,2520))
FAMILIES=((3,7,13),(5,9,5),(7,1,15),(11,3,1))
MAGNITUDES=(3,7)
ONSET_NAMES=("onset4","onset5","onset6","onset7")
ARMS=("fixed_A","fixed_B","hedged_50_50")
INITIAL=y49.ORIGINAL

def install_custom(onset,magnitude):
    # Identical original deterministic source and inverse, with ONLY new
    # exogenous post-onset additive displacement, unknown to the reader.
    base_coord,base_phys,_=INITIAL
    def jump(episode):
        return magnitude if onset is not None and episode>=onset else 0
    def coordinate(cell,seed,episode,family,regime):
        return (base_coord(cell,seed,episode,family,"steady")+jump(episode))%16
    def physical_coordinate(observed,seed,episode,family,regime):
        return base_phys((observed-jump(episode))%16,seed,episode,family,"steady")
    def public_landmarks(seed,episode,family,regime):
        return (coordinate(0,seed,episode,family,regime),
                coordinate(1,seed,episode,family,regime))
    y46.coordinate=coordinate
    y46.physical_coordinate=physical_coordinate
    y46.observed_landmarks=public_landmarks

def run():
    old=(y53.DEV,y53.HELDOUT,y53.FAMILIES,y49.install_environment)
    studies={}
    try:
        y53.DEV=DEV
        y53.HELDOUT=HELDOUT
        y53.FAMILIES=FAMILIES
        for magnitude in MAGNITUDES:
            def custom_install(onset, fixed=magnitude):
                install_custom(onset,fixed)
            y49.install_environment=custom_install
            trial=y53.run()
            assert trial["development_seeds"]==DEV
            assert trial["sealed_heldout_seeds"]==HELDOUT
            assert trial["families"]==FAMILIES
            assert trial["hedge_balanced_schedule_counts"]=={"A":8,"B":8}
            assert len(trial["heldout_records"])==5*4*16*3
            controls=trial["risk_by_arm"]
            best_worst=min(controls[a]["worst_onset"] for a in ("fixed_A","fixed_B"))
            best_pooled=min(controls[a]["pooled_four_onsets"] for a in ("fixed_A","fixed_B"))
            hedge=controls["hedged_50_50"]
            assert best_worst>0 and best_pooled>0
            robust=(hedge["worst_onset"]<=.75*best_worst and
                    hedge["pooled_four_onsets"]<=1.10*best_pooled and
                    all(controls[a]["steady_mismatches"]==0 for a in ARMS) and
                    all(trial["aggregate_by_regime"][regime][a]["landmark_reads"]==4*16*3*10
                        for regime in ("steady",)+ONSET_NAMES for a in ARMS))
            studies[str(magnitude)]={
                "synthetic_offset":magnitude,
                "robust_transfer_gate":robust,
                "worst_error_reduction_fraction":1-hedge["worst_onset"]/best_worst,
                "pooled_loss_penalty_fraction":hedge["pooled_four_onsets"]/best_pooled-1,
                "risk_by_arm":controls,
                "aggregate_by_onset":trial["aggregate_by_regime"],
                "heldout_records":trial["heldout_records"],
                "development_source_structural_checks":trial["development_checks"]}
    finally:
        y53.DEV,y53.HELDOUT,y53.FAMILIES,y49.install_environment=old
        y49.restore_environment()
    passing=sum(studies[str(m)]["robust_transfer_gate"] for m in MAGNITUDES)
    label="MAGNITUDE_TRANSFER_ROBUST" if passing==2 else (
        "PARTIAL_MAGNITUDE_TRANSFER" if passing==1 else "NO_TRANSFER")
    return {"schema":"yggdrasil.y057-shock-magnitude-transfer.v1",
            "parent_head":"65dd5180dae2c63b765f5b78b7b86e42e61ec253",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"families":FAMILIES,
            "shock_magnitudes":MAGNITUDES,
            "magnitude_studies":studies,
            "original_reference_offset_5_not_rerun":True,
            "per_trial_landmark_scalars":10,"model_calls":0,
            "claim_limit":"Synthetic affine-frame additive magnitude shift comparison on a shared new sealed cohort; not real-world transfer or predictive within-run adaptation."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
