TITLE: YGG-A9 Doubled Branch-Repair Load Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: c5ee026ed7ff5ec3aa10d9d509c219bcfc37a651
PARENT_EXPERIMENT: YGG-A8

QUESTION
Does the accepted A8 branch-local repair mechanism preserve capability when the internal specialist-damage load is doubled from 8 to 16 damaged requests per world, without changing the task, horizon, repair semantics, service capacity, or developmental arms?

NORTH-STAR TARGET
Measure repair/reorganization capacity under materially higher internal damage pressure rather than introducing a new repair mechanism.

FROZEN FROM YGG-A8
- exact ten primary manifests;
- exact 160-epoch horizon;
- exact A -> {B,C} -> D fork/join task;
- exact A4 atomic egress integrity;
- exact A6 horizon-aware terminal contract;
- exact A8 local branch-damage event and pre-join repair mechanism;
- exact U_A0 and U_A25 developmental arms;
- exact task programs, arrivals, lesions, anchors, terminal corruptions, expiry, local matching, routing, and service capacity;
- exact A8 capability thresholds;
- deterministic execution and duplicate complete execution.

NESTED DAMAGE SCHEDULE
Use the exact A8 FIXA candidate pool:
request IDs 0..63 excluding inherited terminal-corruption IDs.

Use the exact A8 ranking:
h64("YGG-A8-BRANCH-DAMAGE", seed, rid), then rid.

Select the first 16 ranked IDs.
Assignments:
- ranked positions 1..4: B damage
- positions 5..8: C damage
- positions 9..12: B damage
- positions 13..16: C damage

Therefore:
- exactly 16 damaged requests per world;
- exactly 8 B and 8 C damages;
- the first 8 requests and targets exactly reproduce the accepted A8 damage schedule;
- zero overlap with inherited terminal corruptions.

DAMAGE / REPAIR
Use A8 semantics unchanged:
- damage is applied only after both sibling values exist at PROCESSED_BC;
- exactly one preregistered sibling value is flipped;
- one separately matched PROCESS recomputes only that sibling;
- request remains PROCESSED_BC after repair;
- D may execute only on a later separately matched PROCESS after both siblings are correct.

EXPERIMENTAL CONDITIONS
For every manifest:
1. U_A0 damage OFF
2. U_A0 damage ON at doubled load
3. U_A25 damage OFF
4. U_A25 damage ON at doubled load

MECHANICAL / LINEAGE GATES
- exact A8 mechanical gate passes;
- new schedule has exactly 16 IDs, 8 B and 8 C;
- first 8 ID->target assignments exactly equal accepted A8;
- zero terminal-corruption overlap;
- damage-OFF aggregates reproduce A7/A8: U_A0=1438, U_A25=1443.

DAMAGED-WORLD INTEGRITY GATES
For both damaged arms in every world:
- scheduled=16
- scheduled_b=8
- scheduled_c=8
- applied=16
- repaired=16
- all repaired before D
- unrepaired_terminal=0
- d_while_branch_incorrect=0
- incorrect_done=0
- matching duplicate cell/request violations=0
- maturity.pass=true
- horizon-aware terminal integrity=true

CAPABILITY GATES
For U_A25 damage ON relative to matched U_A25 damage OFF:
- aggregate correct_done ratio >= 0.95
- every-world correct_done ratio >= 0.90

Report U_A0 ratios descriptively.

LEARNED-ARM EXERCISE
At least one matched damaged world must have a different U_A25 state_sha256 from U_A0.

DUPLICATION
Repeat the complete paired execution.
Canonical outputs must be byte-identical.

SUCCESS
YGG_A9_DOUBLED_BRANCH_REPAIR_LOAD=true iff all lineage, mechanical, damaged-world integrity, U_A25 capability, learned-arm exercise, and duplicate gates pass.

FAILURE
Any unmet frozen gate is a scientific negative unless an independently demonstrated infrastructure/evidence defect explains it.
Do not change damage count, target assignment, thresholds, manifests, horizon, scheduler, repair semantics, or service capacity after observing results.

BOUNDARY
No shared-baseline promotion from A9 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
