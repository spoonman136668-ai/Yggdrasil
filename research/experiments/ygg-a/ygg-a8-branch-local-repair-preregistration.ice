TITLE: YGG-A8 Branch-Local Damage and Pre-Join Repair Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: 422fddf4c7f6b0d463b7dd0688a8e26cef731380
PARENT_EXPERIMENT: YGG-A7
INTEGRITY_PARENT: YGG-A6
MECHANISM_PARENT: YGG-A4
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Can the fork/join system detect and repair bounded internal damage to one completed sibling computation before D executes, while preserving the accepted horizon-aware terminal integrity contract under both U_A0 and learned U_A25 developmental dynamics?

NORTH-STAR TARGET
This moves repair from the terminal output boundary into an internal specialized branch.
It tests local reorganization/recomputation of damaged intermediate capability without extending the horizon, adding global authority, or changing the task graph.

FROZEN
- exact ten A1/A4/A6/A7 primary manifests;
- exact 160-epoch horizon;
- exact A -> {B,C} -> D fork/join task;
- exact programs, arrivals, lesions, anchors, terminal corruption schedule, expiry, routing, local matching, and service capacity;
- exact A4 atomic egress integrity handoff;
- exact A6 prospective horizon-aware terminal contract;
- exact U_A0 and U_A25 developmental modes;
- deterministic execution;
- no online adaptation.

BRANCH-DAMAGE SCHEDULE
For each manifest independently:
- exclude request IDs already in the frozen terminal-corruption schedule;
- rank remaining request IDs by
  h64("YGG-A8-BRANCH-DAMAGE", seed, rid), then rid;
- select the first eight ranked IDs;
- the first four selected IDs receive B-branch damage;
- the next four receive C-branch damage.

Thus every world has exactly:
- 8 branch-damaged requests;
- 4 B damages;
- 4 C damages;
- zero overlap with the inherited terminal-corruption IDs.

DAMAGE EVENT
After both sibling values exist and the request first enters PROCESSED_BC, flip exactly one bit of the preregistered damaged sibling value.
No other field, program, request state, or output is changed.

REPAIR MECHANISM
When a PROCESS operation is matched to a PROCESSED_BC request:
- compare B and C against their exact local deterministic sibling computations from A and the request bits;
- if one preregistered sibling is damaged, recompute only that sibling;
- consume exactly that one matched PROCESS operation;
- remain in PROCESSED_BC;
- do not compute D in the same operation;
- mark the branch repair and repair epoch.
A later separately matched PROCESS may compute D only after both siblings are correct.

The mechanism may inspect only the current request's local A/B/C values, bits, and programs.
It may not inspect future state, terminal output, evaluator data, or global queue state.

EXPERIMENTAL CONDITIONS
For every manifest run four matched conditions:
1. U_A0, damage OFF
2. U_A0, damage ON
3. U_A25, damage OFF
4. U_A25, damage ON

Damage-OFF conditions must reproduce the accepted A7 paired semantics.
Damage-ON differs only by the preregistered branch-damage schedule and pre-join repair mechanism.

MECHANICAL GATE
Demonstrate before primary interpretation:
- exactly one B-damage fixture and one C-damage fixture;
- damage occurs only after both siblings exist;
- D remains blocked while either sibling is wrong;
- branch repair consumes exactly one separate PROCESS operation;
- repair restores only the damaged sibling;
- D executes only on a later matched PROCESS;
- both B-first and C-first sibling orders remain valid;
- A4 atomic egress behavior remains exact;
- horizon-aware terminal fixture remains exact;
- duplicate execution deterministic;
- zero incorrect DONE.

PRIMARY BRANCH-REPAIR GATES
For both damaged arms:
- exactly 8 branch damage events per world;
- exactly 4 B and 4 C damages per world;
- every branch damage repaired before D;
- no D execution while either sibling is incorrect;
- no branch damage reaches terminal output unrepaired;
- zero incorrect DONE;
- matching integrity exact;
- maturity.pass true;
- horizon-aware terminal integrity true.

CAPABILITY GATES
For U_A25 damage ON relative to matched U_A25 damage OFF:
- aggregate correct_done ratio >= 0.95;
- every-world correct_done ratio >= 0.90.

For U_A0 damage ON relative to matched U_A0 damage OFF:
- report the same ratios descriptively;
- do not require U_A0 to outperform or match U_A25.

LEARNED-ARM EXERCISE
U_A25 must differ in state_sha256 from U_A0 in at least one matched damaged world.

DUPLICATION
Repeat the complete four-condition primary execution.
Canonical outputs must be byte-identical.

SUCCESS
YGG_A8_BRANCH_LOCAL_REPAIR=true iff all mechanical, branch-repair, U_A25 capability, learned-arm exercise, terminal-integrity, and duplicate gates pass.

FAILURE
Any unmet frozen gate is a scientific negative unless an independently demonstrated infrastructure/evidence defect explains it.
Do not change damage count, damaged sibling assignment, thresholds, manifests, horizon, scheduler, repair semantics, or service capacity after observing results.

INTERPRETATION
Positive:
Bounded internal specialist damage can be locally repaired before join completion while preserving learned developmental dynamics and terminal integrity.

Negative:
Internal branch repair/reorganization is a capability boundary even though terminal repair and learned-arm compatibility already pass.

BOUNDARY
No shared-baseline promotion from A8 alone.
No online adaptation.
No recursive self-modification.
No external runtime modification.
