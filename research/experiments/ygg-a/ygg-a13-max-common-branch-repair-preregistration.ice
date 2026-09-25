TITLE: YGG-A13 Maximum Common-Pool Branch-Repair Load Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: 6d547932682313f3c2728f7440153ddc07922a75
PARENT_EXPERIMENT: YGG-A12

QUESTION
Does the frozen branch-local repair mechanism remain capability-preserving at the maximum fixed damage count that is valid across every one of the ten frozen worlds?

NORTH-STAR TARGET
Close the fixed-pool repair-capacity boundary before moving A into integration work.

FROZEN
All A12 task, developmental-arm, horizon, scheduler, service-capacity, terminal-integrity, maturity, repair, threshold, seed, and deterministic-execution semantics remain exact.

MAXIMUM COMMON FIXED LOAD
The frozen worlds contain 58..63 eligible request IDs in 0..63 after excluding inherited terminal-corruption IDs.
Therefore 58 is the largest single fixed damage count valid in every world.

NESTED DAMAGE SCHEDULE
Use the exact inherited A8 ranking:
h64("YGG-A8-BRANCH-DAMAGE", seed, rid), then rid,
over request IDs 0..63 excluding inherited terminal-corruption IDs.

Select the first 58 ranked IDs.
- first 56 assignments reproduce A12 exactly;
- assignment 57 targets B;
- assignment 58 targets C.

Thus:
- exactly 58 damaged requests per world;
- exactly 29 B and 29 C damages;
- first 8/16/32/48/56 assignments reproduce A8/A9/A10/A11/A12;
- zero terminal-corruption overlap.

DAMAGE / REPAIR
Unchanged from A8-A12:
- damage only after both sibling values exist at PROCESSED_BC;
- exactly one scheduled sibling value is flipped;
- one separately matched PROCESS recomputes that sibling;
- D may execute only later after both siblings are correct.

EXPERIMENTAL CONDITIONS
Per manifest:
1. U_A0 damage OFF
2. U_A0 damage ON at 58-load
3. U_A25 damage OFF
4. U_A25 damage ON at 58-load

INTEGRITY GATES
For both damaged arms in every world:
- scheduled=58
- scheduled_b=29
- scheduled_c=29
- applied=58
- repaired=58
- all repaired before D
- unrepaired_terminal=0
- d_while_branch_incorrect=0
- incorrect_done=0
- matching duplicate cell/request violations=0
- maturity.pass=true
- horizon-aware terminal integrity=true

CAPABILITY GATES
For U_A25 damage ON relative to matched U_A25 damage OFF:
- aggregate correct_done ratio >=0.95
- every-world correct_done ratio >=0.90

LINEAGE / EXERCISE
- inherited mechanical gate exact;
- first 56 assignments reproduce A12 exactly;
- minimum eligible pool >=58;
- damage-OFF aggregates reproduce U_A0=1438 and U_A25=1443;
- at least one damaged world has U_A25 state_sha256 different from U_A0;
- duplicate complete execution byte-identical.

SUCCESS
YGG_A13_MAX_COMMON_BRANCH_REPAIR=true iff every frozen gate passes.

INTERPRETATION
Positive:
The tested fixed-pool line is saturated without finding a repair-capacity failure. Close this incremental stress family and advance A to integration rather than inventing larger non-comparable damage pools.

Negative:
The repair boundary lies between 56 and 58 under the frozen common-pool design.

FAILURE
Do not change count, assignments, thresholds, service capacity, horizon, scheduler, or repair semantics after observing results.

BOUNDARY
No shared-baseline promotion from A13 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
