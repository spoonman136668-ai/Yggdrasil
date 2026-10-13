"""Y058: heldout anchor-invisible nonaffine transposition boundary for schedule diversification."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y057-magnitude-transfer"/"execute.py"
spec=importlib.util.spec_from_file_location("y57_pinned",SOURCE)
assert spec and spec.loader
y57=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y57)
y56=y57.y56
y53=y57.y53
y49=y57.y49
y46=y57.y46

DEV=tuple(range(2800,2808))
HELDOUT=tuple(range(2808,2824))
FAMILIES=((3,5,7),(5,11,9),(7,7,13),(11,9,3))
TRANSPOSE=((2,3),(4,5))
REGIMES=(("steady",None),("onset4",4),("onset6",6))
ARMS=("fixed_A","fixed_B","hedged_50_50")
ORIGINAL=y49.ORIGINAL

def install_transposition(onset,pair,checks):
    """Change only environment coordinate-label mapping, preserve public cell0/1."""
    native_coord,native_phys,native_anchors=ORIGINAL
    assert pair[0]!=pair[1] and set(pair).isdisjoint({0,1})
    def permute(cell,episode):
        if onset is None or episode<onset:
            return cell
        if cell==pair[0]:return pair[1]
        if cell==pair[1]:return pair[0]
        return cell
    def coordinate(cell,seed,episode,family,regime):
        return native_coord(permute(cell,episode),seed,episode,family,"steady")
    def physical_coordinate(observed,seed,episode,family,regime):
        native_cell=native_phys(observed,seed,episode,family,"steady")
        return permute(native_cell,episode)
    def public_landmarks(seed,episode,family,regime):
        exposed=(coordinate(0,seed,episode,family,regime),
                 coordinate(1,seed,episode,family,regime))
        unchanged=native_anchors(seed,episode,family,"steady")
        assert exposed==unchanged, "PUBLIC_ANCHOR_MODIFICATION_INVALID"
        checks["anchor_pair_checks"]+=1
        return exposed
    y46.coordinate=coordinate
    y46.physical_coordinate=physical_coordinate
    y46.observed_landmarks=public_landmarks

def run():
    original_values=(y53.DEV,y53.HELDOUT,y53.FAMILIES,y53.REGIMES,
                     y49.install_environment)
    studies={}
    try:
        y53.DEV=DEV
        y53.HELDOUT=HELDOUT
        y53.FAMILIES=FAMILIES
        y53.REGIMES=REGIMES
        for pair in TRANSPOSE:
            checks={"anchor_pair_checks":0}
            def install_onset(onset,fixed_pair=pair):
                install_transposition(onset,fixed_pair,checks)
            y49.install_environment=install_onset
            result=y53.run()
            assert result["development_seeds"]==DEV
            assert result["sealed_heldout_seeds"]==HELDOUT
            assert result["families"]==FAMILIES
            assert result["hedge_balanced_schedule_counts"]=={"A":8,"B":8}
            assert len(result["heldout_records"])==3*4*16*3
            assert checks["anchor_pair_checks"]>0

            aggregate=result["aggregate_by_regime"]
            steady_all_zero=all(result["risk_by_arm"][arm]["steady_mismatches"]==0 for arm in ARMS)
            postshock={regime:{arm:aggregate[regime][arm]["mismatches"] for arm in ARMS}
                       for regime in ("onset4","onset6")}
            any_error=any(n>0 for errors in postshock.values() for n in errors.values())
            quarantines={regime:{arm:aggregate[regime][arm]["quarantines"] for arm in ARMS}
                         for regime,_ in REGIMES}
            zero_resets=all(n==0 for row in quarantines.values() for n in row.values())
            same_sensor=all(aggregate[regime][arm]["landmark_reads"]==4*16*3*10
                            for regime,_ in REGIMES for arm in ARMS)
            assert same_sensor, "SENSOR_BUDGET_INVALID"
            studies[f"{pair[0]}_{pair[1]}"]={
                "transposed_physical_cells":pair,
                "anchors_exactly_preserved":True,
                "public_anchor_reads_checked":checks["anchor_pair_checks"],
                "steady_all_zero":steady_all_zero,
                "any_postshock_physical_assignment_mismatch":any_error,
                "zero_quarantine_actions":zero_resets,
                "reset_counts_by_regime":quarantines,
                "risk_by_arm":result["risk_by_arm"],
                "postshock_mismatches":postshock,
                "same_sensing_cost":same_sensor,
                "aggregate_by_regime":aggregate,
                "by_family_seed_policy":result["heldout_records"],
                "original_y053_rubric_label_for_this_condition":result["classification"]
            }
    finally:
        y53.DEV,y53.HELDOUT,y53.FAMILIES,y53.REGIMES,y49.install_environment=original_values
        y49.restore_environment()
    valid=all(item["anchors_exactly_preserved"] and item["steady_all_zero"] and
              item["same_sensing_cost"] for item in studies.values())
    assert valid, "NONAFFINE_SOURCE_VALIDITY_FAILURE"
    evidenced=any(item["any_postshock_physical_assignment_mismatch"]
                  for item in studies.values())
    no_reset=all(item["zero_quarantine_actions"] for item in studies.values())
    classification=("ANCHOR_INVISIBLE_LIMIT" if evidenced and no_reset
                    else "INCONCLUSIVE_LIMIT")
    return {
        "schema":"yggdrasil.y058-anchor-blind-nonlinear-coordinate.v1",
        "parent_head":"0cf8678669c6b1bcd3ae80c1c7ccf623b8835d18",
        "classification":classification,
        "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
        "source_affine_background_families":FAMILIES,
        "regimes":[name for name,_ in REGIMES],
        "transposition_arms":TRANSPOSE,"per_trial_landmark_scalars":10,
        "anchor_invisible_conditions":studies,
        "new_candidate_training_or_tuning":False,"model_calls":0,
        "claim_limit":"Prospective deterministic non-affine synthetic post-onset coordinate-label swaps invisible to two public anchor cells; no autonomous shock detection or physical-source transfer."
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
