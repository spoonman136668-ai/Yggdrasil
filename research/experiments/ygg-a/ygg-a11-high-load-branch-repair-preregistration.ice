TITLE: YGG-A11 High-Load Branch-Repair Boundary Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: 1b909266d35c14b47904e2d4b5010a8b8f09fc0
PARENT_EXPERIMENT: YGG-A10

QUESTION
Does the accepted branch-local repair mechanism remain capability-preserving when the exact nested internal specialist-damage schedule is increased from 32 to 48 damaged requests per world?

NORTH-STAR TARGET
Locate the repair/reorganization capacity boundary before introducing any additional repair mechanism or broader capability.

FROZEN FROM YGG-A10
- exact ten primary manifests;
- exact 160-epoch horizon;
- exact A -> {B,C} -> D fork/join task;
- exact A4/A6 terminal-integrity contract;
- exact A8 branch-local damage and pre-join repair semantics;
- exact U_A0 and U_A25 developmental arms;
- exact task programs, arrivals, lesions, anchors, terminal corruptions, expiry, local matching, routing, service capacity, maturity contract, and capability thresholds;
- deterministic duplicate execution.

NESTED DAMAGE SCHEDULE
Use the exact A8 candidate pool:
request IDs 0..63 excluding inherited terminal-corruption IDs.

Use the exact A8 ranking:
h64("YGG-A8-BRANCH-DAMAGE", seed, rid), then rid.

Select the first 48 ranked IDs.
Assign frozen blocks of four, alternating B then C:
1..4 B, 5..8 C, continuing this pattern through positions 45..48.

Therefore:
- exactly 48 damaged requests per world;
- exactly 24 B and 24 C damages;
- first 8 assignments exactly reproduce accepted A8;
- first 16 assignments exactly reproduce accepted A9;
- first 32 assignments exactly reproduce accepted A10;
- zero overlap with inherited terminal corruptions.

DAMAGE / REPAIR
Unchanged from A8-A10:
- damage applies only after both sibling values exist at PROCESSED_BC;
- exactly one preregistered sibling value is flipped;
- one separately matched PROCESS recomputes only that sibling;
- the request remains PROCESSED_BC after repair;
- D may execute only later, after both siblings are correct.

EXPERIMENTAL CONDITIONS
Per manifest:
1. U_A0 damage OFF
2. U_A0 damage ON at 48-load
3. U_A25 damage OFF
4. U_A25 damage ON at 48-load

LINEAGE / MECHANICAL GATES
- exact inherited mechanical gate passes;
- schedule has exactly 48 IDs, 24 B and 24 C;
- first 8/16/32 assignments reproduce A8/A9/A10 exactly;
- zero terminal-corruption overlap;
- damage-OFF aggregates reproduce accepted U_A0=1438 and U_A25=1443.

DAMAGED-WORLD INTEGRITY
For both damaged arms in every world:
- scheduled=48
- scheduled_b=24
- scheduled_c=24
- applied=48
- repaired=48
- all repaired before D
- unrepaired_terminal=0
- d_while_branch_incorrect=0
- incorrect_done=0
- matching duplicate cell/request violations=0
- maturity.pass=true
- horizon-aware terminal integrity=true

CAPABILITY
For U_A25 damage ON relative to matched U_A25 damage OFF:
- aggregate correct_done ratio >= 0.95
- every-world correct_done ratio >= 0.90

U_A0 ratios are descriptive.

LEARNED-ARM EXERCISE
At least one damaged world must have a different U_A25 state_sha256 from U_A0.

DUPLICATION
Repeat the complete paired execution.
Canonical outputs must be byte-identical.

SUCCESS
YGG_A11_HIGH_LOAD_BRANCH_REPAIR=true iff every frozen lineage, mechanical, integrity, capability, learned-arm, and duplicate gate passes.

FAILURE
Any unmet frozen gate is a scientific negative unless an independently demonstrated infrastructure/evidence defect explains it.
Do not alter damage count, assignments, thresholds, horizon, scheduler, repair semantics, or service capacity after observing results.

BOUNDARY
No shared-baseline promotion from A11 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
