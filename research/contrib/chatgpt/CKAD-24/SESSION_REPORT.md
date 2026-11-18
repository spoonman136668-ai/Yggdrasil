# CKAD24 — Blind phase-permutation causal change detection

**DEVELOPMENT_NO_GO** — frozen synthetic development gate.
The learner did not receive source phase names or true change times.
It reused the exact CKAD23 native algorithm and three independently
saved 448-public-episode checkpoints, with two new source permutation
schedules and disjoint exogenous draw namespaces.

True evaluator-side boundaries: 48, 96, 144. A detection counts only
once per true boundary and only within 16 observed public consequences.
All duplicate alarms count as false positives. This is stricter than
the CKAD23 reward-only development gate.

| Schedule | Change 48 (seeds/3) | Change 96 | Change 144 | False alarm counts | Development |
|---|---:|---:|---:|---|---|
| middle_swap | 3 | 1 | 1 | [1, 1, 1] | DEVELOPMENT_NO_GO |
| double_flip | 0 | 1 | 0 | [1, 1, 1] | DEVELOPMENT_NO_GO |

## Frozen per-schedule metrics and gates

### middle_swap
- all_boundaries_detected_in_2_of_3: FAIL
- max_three_false_alarms_each: PASS
- held_plus_five_points_vs_no_reset: FAIL
- held_at_least_periodic32: FAIL
- held_at_least_trailing64_mle: PASS
- return_to_invariant_above_80pct: FAIL
- target_held_reward: 305/432
- gain_vs_no_reset: 13/288
- gain_vs_periodic32: -5/864
- gain_vs_trailing64_mle: 73/864
- final_return_reward: 113/144
- Seed 101: detections [50, 101, 124], false alarms 1; checkpoint d6421c4afbe4550553e6d1057ce96b170ccc18b143a86ee9e95495779023971e
- Seed 202: detections [50, 82], false alarms 1; checkpoint 00c1ec454803b35742e739e525f0f50a0e45dad766e1b780db0d2358fc6829b6
- Seed 303: detections [51, 133, 152], false alarms 1; checkpoint 31487b3ca9ee34230b08ac27043d8d631b3024ed82592bd8c2f3d92b72800f09
### double_flip
- all_boundaries_detected_in_2_of_3: FAIL
- max_three_false_alarms_each: PASS
- held_plus_five_points_vs_no_reset: FAIL
- held_at_least_periodic32: FAIL
- held_at_least_trailing64_mle: PASS
- return_to_invariant_above_80pct: PASS
- target_held_reward: 641/864
- gain_vs_no_reset: 0/1
- gain_vs_periodic32: -17/288
- gain_vs_trailing64_mle: 0/1
- final_return_reward: 43/48
- Seed 101: detections [98, 168], false alarms 1; checkpoint c3bb61f3547150fcf46f9506e5aa7c168eff311e35cf80707b2774e82fb44fe7
- Seed 202: detections [180], false alarms 1; checkpoint 4367e5e38c8649612cf4395c6139264cbfe74242d03ae990ac32f1c5d8fc9ff6
- Seed 303: detections [74], false alarms 1; checkpoint 25e926351f93b3a326bb0b51d3b02d624fd85e9e4a24f21232920b243f702e67

## Evidence custody and limits

Six exact native checkpoints and the complete six per-case source
proofs are stored in this folder with deterministic gzip compression;
all were re-executed on Linux and Windows with byte-exact checkpoint
and semantic evidence parity. Every case retains the complete original
448-episode prefix and 192 new public action-consequence witnesses.

New source namespaces do not imply independently pretrained additional
models: only three original CKAD22 seed groups were independently fitted.
This study uses known synthetic families, and cannot establish scientific
novel-world transfer or autonomous intelligence.

Result semantic SHA256: a2bd99b1c3637688b2383595864b8f38c3b859120153704b47e352dc09e4b2f7

**ENGINEERING:** pending final exact-candidate Linux/Windows regression and atlas.
**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**
