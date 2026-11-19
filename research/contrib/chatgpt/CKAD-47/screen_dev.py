"""CKAD47 one-shot frozen DEV qualifier; no held pilot or primary mode."""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad47_source_once",HERE/"campaign.py")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def main():
    cases=[D.evaluate(seed) for seed in D.DEV]
    decision=D.classify(cases)
    if decision=="SOURCE_INVALID":
        raise AssertionError("CKAD47_SOURCE_CUSTODY_OR_COLD_FAILED")
    report={
      "schema":"yggdrasil.ckad47.dev-screen.v1",
      "prereg_commit":D.PREREG,
      "research_parent":"754e7fd1daf4e99f4949fa649eccd26863622a7b",
      "decision":decision,
      "scientific_pass":False,
      "dev_seeds_consumed":list(D.DEV),
      "reserved_pilots_untouched":list(D.PILOT),
      "reserved_primaries_untouched":list(D.PRIMARY),
      "source_specs":{"four_action_identifiers":list(range(4)),
          "four_state_identifiers":list(range(4)),
          "initial_old_action_episodes":D.OLD,
          "novel_primitive_boundary":D.OLD,
          "return_to_old_action_boundary":D.NEW_END,
          "total_episode_count_per_world":D.TOTAL,
          "expected_rewards_are_never_source_training":True,
          "true_hidden_permutation_never_given_to_models":True},
      "frozen_thresholds":{
          "max_pooled_late_and_return_Brier":.17,
          "min_gain_against_fullfit_tabular":.010,
          "max_gap_to_exact_24_permutation_Bayes":.006,
          "max_early_novel_worse_than_exact":.015,
          "max_cold_return_worse_than_exact":.008,
          "source_custody_and_2OS_checkpoint_hash_parity":True},
      "cases":cases,
      "limits":"Development-only hand-specified XOR-action causal family, with newly independent action deltas but prior known 4-state XOR group. Not proof of open-world new physics, compositional general intelligence, production Yggdrasil acceptance, or efficiency. Extra exact Bayesian compute unmatched. No held first use, no full final repo regression, no merge."
    }
    print("CKAD47_DEV_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")))
    return report


if __name__=="__main__":
    main()
