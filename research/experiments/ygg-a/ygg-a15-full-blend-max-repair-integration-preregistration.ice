TITLE: YGG-A15 Full-Blend Maximum-Repair Integration Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: ee3e1710939fed04c51dc4602adec963d1ed5799
PARENT_EXPERIMENT: YGG-A14

QUESTION
Does the maximum 58-event branch-repair workload remain capability-preserving under the full learned developmental-control blend alpha=1.0?

NORTH-STAR TARGET
Close the repair-plus-learned-control integration boundary before moving A to a different integration dimension.

FROZEN FROM YGG-A14
- exact ten manifests;
- exact 58-damage branch schedule;
- exact 29 B / 29 C damages;
- exact branch-repair semantics;
- exact terminal-integrity contract;
- exact task, programs, arrivals, lesions, anchors, corruptions, horizon, scheduler, service capacity, maturity rules, and thresholds;
- exact learned weights;
- deterministic duplicate execution.

SCIENTIFIC CHANGE
Test exactly:
alpha=0.50
alpha=1.00

alpha=0.50 is the accepted A14 integration anchor.
alpha=1.00 is the full learned-control regime.

ANCHOR
At alpha=0.50 the complete A13-derived one-pass evidence hash must equal:
5b8cc8a5c6c2732000fee3efe0bf6ee01fa7b86484d927e92234e977bd95ab9f

FULL-BLEND GATES
At alpha=1.00:
- inherited mechanical gate passes;
- minimum eligible pool >=58;
- first 56 A12 assignments exact;
- scheduled/applied/repaired=58 in every damaged world;
- scheduled_b=29 and scheduled_c=29;
- all repairs precede D;
- unrepaired_terminal=0;
- d_while_branch_incorrect=0;
- incorrect_done=0;
- matching duplicate violations=0;
- maturity.pass=true;
- horizon-aware terminal integrity=true;
- U_A25 damage-ON aggregate correct_done ratio vs same-alpha OFF >=0.95;
- every-world damage ratio >=0.90;
- learned arm materially exercised.

DUPLICATION / RESTORATION
Each alpha executes twice and must be byte-identical.
Runtime alpha must be exactly restored after every condition and at experiment end.

SUCCESS
YGG_A15_FULL_BLEND_MAX_REPAIR_INTEGRATION=true iff the alpha=.50 anchor is exact, alpha=1.0 passes all integration gates, duplicates are exact, and runtime restoration is exact.

INTERPRETATION
Positive: repair and learned developmental control remain compatible across the entire supported blend range; close this integration boundary.
Negative: full learned control crosses an interaction boundary despite alpha=.50 compatibility.

FAILURE
Do not alter alpha, damage schedule, repair semantics, thresholds, weights, horizon, scheduler, or service capacity after results.

BOUNDARY
No accepted baseline mutation.
No learned-weight update.
No online adaptation.
No shared-baseline promotion from A15 alone.
No recursive self-modification.
