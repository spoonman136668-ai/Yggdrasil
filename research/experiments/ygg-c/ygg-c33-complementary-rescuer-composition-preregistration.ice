YGG-C33 PREREGISTRATION — COMPLEMENTARY RESCUER COMPOSITION ACROSS PRESSURE
Parent C32 run36346247216 valid PARTIAL_CROSS_BASIN_PORTABILITY.
Governance:
- exact near-onset alpha=0.134765625 is explicitly authorized for this descendant by research/decisions/ygg-c-near-onset-alpha-authority-20260927.ice;
- runtime parent.ALPHA and parent.g.ALPHA must be frozen exactly to0.134765625 for every arm and restored afterward;
- no other authority boundary changes.

QUESTION
Do the complementary C32 single-cell rescuers compose into a pressure-portable two-cell repair of the original replicate8 failure basin?

FROZEN SUBSTRATE
- exact corrected C32/C25 substrate;
- replicate8 original lesion;
- alpha=0.134765625;
- levels8..16;
- exact manifests, weights, task, scheduler, retention, maturity, deterministic execution;
- no retraining, online adaptation, learned C/S authority, or threshold change.

INHERITED SINGLE-ADDITION ANCHORS
ADD41 rescues exactly levels8..9.
ADD40 rescues exactly levels10..16.
ADD45 rescues exactly levels10..16.
ADD47 rescues no levels.
ADD10 rescues no levels.
These anchors must reproduce exactly.

COMPOSITION ARMS
1. ADD41_40 = add cells41 and40 to ORIGINAL_R8.
2. ADD41_45 = add cells41 and45 to ORIGINAL_R8.

MATCHED CONTROLS
3. ADD41_47 = low-pressure rescuer41 plus inherited nonrescuer47.
4. ADD40_47 = high-pressure rescuer40 plus nonrescuer47.
5. ADD10_47 = two inherited nonrescuers.

Each arm changes exactly the registered two memberships and nothing else.

PRIMARY
Report maturity rescue at every level8..16 for all five double-addition arms.

CLASSIFICATION
COMPLEMENTARY_COMPOSITION_UNIVERSAL if ADD41_40 and ADD41_45 both rescue every level8..16 while ADD10_47 does not rescue every level.
ONE_COMPLEMENTARY_PAIR_UNIVERSAL if exactly one of ADD41_40 / ADD41_45 rescues all levels.
COMPOSITION_PRESSURE_GAPS_REMAIN if neither complementary pair rescues all levels but at least one rescues more levels than both constituent singles' individual overlap alone would predict.
COMPOSITION_INTERFERENCE if adding41 causes either40 or45 to lose rescue at any level10..16, or adding40/45 causes the pair to lose the inherited41 rescue at level8 or9.
GENERIC_TWO_ADDITION_RESCUE if ADD10_47 rescues all levels8..16.
ANCHOR_NOT_REPRODUCED if any inherited C32 single-addition anchor fails.
OTHER_VALID_PATTERN otherwise.

VALIDITY
- exact levels8..16;
- alpha exact and runtime-proven;
- original replicate8 lesion exact;
- inherited single anchors exact;
- exactly five registered double-addition arms;
- exactly two membership changes per double arm;
- no unregistered lesion changes;
- duplicate analysis byte-identical;
- alpha/dose/pressure globals restored.

Scientific negatives are valid. No post-result tuning.
