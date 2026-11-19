"""CKAD49 frozen two-seed scientific development first-use, no pilot/primary."""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad49_source_screen",HERE/"campaign.py")
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

def main():
    cases=[M.run(seed) for seed in M.DEV]
    decision=M.classify(cases)
    if decision=="SOURCE_INVALID":raise AssertionError("CKAD49_SOURCE_OR_CHECKPOINT_CUSTODY_INVALID")
    report={
      "schema":"yggdrasil.ckad49.original-development-screen.v1",
      "prereg_committed_before_source":"63d9ff3b5cabbe932f70ad5452c86d24cfb74c7f",
      "predecessor":"5949204f743f113891efe18d0ba81c690151acce",
      "dev_decision":decision,"scientific_pass":False,
      "dev_seeds_consumed":list(M.DEV),
      "pilot_reserved_untouched":list(M.PILOT),
      "primary_reserved_untouched":list(M.PRIMARY),
      "candidate_family":"Learn state singleton exception from source evidence; choose XOR/additive primitive effect composition, preserve old native source and reward relationships.",
      "frozen_thresholds":{
        "pooled_max_Brier":.19,"gain_vs_unrestricted_tabular_min":.010,
        "gain_vs_old_XOR_restricted_min":.025,
        "max_gap_over_16_hypothesis_exact_BMA":.004,
        "max_early_novel_gap_vs_BMA":.015,
        "max_cold_return_gap_vs_BMA":.008,
        "correct_operator_and_exception_by_last_scored_probe":True,
        "two_OS_exact_score_and_full_checkpoint_sha_parity":True},
      "cases":cases,
      "known_limits":"A NEW finite 16-hypothesis operator/partition family contains true novel worlds, unlike CKAD48; not open-ended state-feature invention or general physics. Source-trained isolated research model, not accepted binary native Yggdrasil. Equal source rows and intervention budgets but unmatched compute. No independent held first-use, full regression, owner integration, merge or deployment."
    }
    print("CKAD49_DEV_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")))
    return report

if __name__=="__main__":main()
