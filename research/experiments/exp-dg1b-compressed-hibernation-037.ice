{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-COMPRESSED-HIBERNATION-037",
  "question": "Do the independently supported 64-byte persistent-state compression and 1024-step hibernation capabilities compose without a hidden interaction penalty?",
  "hypothesis": "After interval 1024, the 64-byte state has median wake-cost inflation <=25% versus the 256-byte state, retains median specificity >=0.05, supporting-seed fraction >=0.75, and unrelated collateral <=0.03 while active and physical-container resources remain matched.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": [
    {
      "experiment": "EXP-DG1B-PERSISTENT-STATE-FLOOR-032",
      "result_sha256": "3ae09eb175609c7c83e3e39ed12804aa572f8adde2c8fc6929ccfbe9ec018cff"
    },
    {
      "experiment": "EXP-DG1B-HIBERNATION-HORIZON-033",
      "result_sha256": "4f404f3ca6d95dc32d1e37c6748f3a36394a2a01c69c5d4b55214510670b47bf"
    }
  ],
  "changed_dimension": "persistent-state size only after fixed 1024-step inactivity: 256 bytes versus 64 bytes; wake dynamics and resources otherwise matched",
  "seeds": [
    165857,
    166861,
    167873,
    168887,
    169891,
    170899,
    171907,
    172933
  ],
  "inactive_interval": 1024,
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "max_wake_updates": 128
  },
  "thresholds": {
    "median_64_vs256_wake_cost_inflation_lte": 0.25,
    "median_64_specificity_gte": 0.05,
    "supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
