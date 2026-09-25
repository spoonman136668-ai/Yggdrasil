TITLE: YGG-A14 Maximum-Repair Learned-Blend Integration Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: 93d5b08fd6e89b745105f76ec3ab958aa07bb8c6
PARENT_EXPERIMENT: YGG-A13
CROSS_MECHANISM_EVIDENCE: YGG-C8 BLEND_REQUIRED_STABLE

QUESTION
Does the fully stressed A13 branch-local repair mechanism remain capability-preserving when the frozen learned developmental-control blend is increased from alpha=0.25 to alpha=0.50?

NORTH-STAR TARGET
Begin mechanism integration after the A8-A13 repair-capacity boundary is closed.

FROZEN FROM YGG-A13
- exact ten primary manifests;
- exact 58-damage nested branch schedule;
- exactly 29 B and 29 C branch damages per world;
- exact branch damage and repair semantics;
- exact A4/A6 terminal-integrity contract;
- exact task, programs, arrivals, lesions, anchors, terminal corruptions, horizon, scheduler, service capacity, maturity rules, and capability thresholds;
- exact learned weights;
- no retraining or online adaptation;
- deterministic duplicate execution.

SCIENTIFIC CHANGE
Vary only the runtime learned-control blend coefficient for the U_A25 arm.

Test exactly:
alpha=0.25
alpha=0.50

The U_A0 arm is unchanged by alpha and remains descriptive inside the inherited A13 execution.

ALPHA=0.25 ANCHOR
The complete A13 one-pass canonical evidence hash at alpha=0.25 must equal:
ac93fda604f8da8aa3149c0251d74470ec65e052cfbeb1c685446491cb1c636c

This anchors the integration harness to the accepted A13 result.

ALPHA=0.50 INTEGRATION GATES
Under alpha=0.50:
- inherited mechanical gate passes;
- minimum eligible pool >=58;
- first 56 A12 assignments remain exact;
- scheduled=58, scheduled_b=29, scheduled_c=29;
- applied=58 and repaired=58 in every damaged world;
- all repaired before D;
- unrepaired_terminal=0;
- d_while_branch_incorrect=0;
- incorrect_done=0;
- matching duplicate cell/request violations=0;
- maturity.pass=true;
- horizon-aware terminal integrity=true;
- U_A25 damage-ON aggregate correct_done ratio relative to same-alpha damage-OFF >=0.95;
- every-world U_A25 damage ratio >=0.90;
- learned arm is materially exercised in at least one damaged world.

DUPLICATION
For each alpha, execute the complete A13 one-pass twice.
Canonical duplicate evidence must be byte-identical.

RUNTIME RESTORATION
The inherited alpha value must be exactly restored after every alpha condition and at experiment end.

SUCCESS
YGG_A14_MAX_REPAIR_BLEND_INTEGRATION=true iff:
- alpha levels are exact;
- alpha=0.25 A13 anchor hash is exact;
- alpha=0.50 integration gates all pass;
- duplicate execution is exact at both alpha values;
- runtime alpha restoration is exact.

INTERPRETATION
Positive:
The maximum tested local branch-repair workload is compatible with the stronger learned-control regime. This supports integration of repair and learned developmental control.

Negative:
The repair mechanism and stronger learned-control blend interact adversely despite each being separately viable.

FAILURE
Do not alter alpha values, damage count, repair semantics, task, thresholds, scheduler, horizon, service capacity, or weights after observing results.

BOUNDARY
No accepted baseline mutation.
No learned-weight update.
No online adaptation.
No shared-baseline promotion from A14 alone.
No recursive self-modification.
No external runtime modification.
