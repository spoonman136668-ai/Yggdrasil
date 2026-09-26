TITLE: YGG-A25 Cell-59 Portability Attribution Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: 64d1aed4e8a4a8aea41324ae3a6625c4beb4e6ee
PARENT_EXPERIMENT: YGG-A24

QUESTION
Does cell 59 independently trigger the hidden stream-collapse phenotype across seed contexts, or is the effect specific to replicate 6?

NORTH-STAR TARGET
Distinguish a globally critical developmental cell from a context-dependent local interaction before any repair mechanism is attempted.

FROZEN FROM A24
- exact A24/A23 task, ten manifests, scheduler, horizon, service capacity, maturity, matching, terminal-integrity, and stream-noncollapse rules;
- alpha=.25;
- repair OFF;
- exact learned weights;
- deterministic execution;
- U_A0 and U_A25;
- exact L11 anchor construction;
- no retraining or online adaptation.

TARGET CELL
59.

ELIGIBILITY
A replicate is eligible iff cell 59 is not already present in its exact frozen L11 lesion.

TEST ARM
For every eligible replicate:
- exact L11 lesion plus cell 59;
- cardinality exactly 12;
- all non-lesion manifest fields frozen.

REFERENCE
The exact same eligible replicate under its L11 anchor.

REPORT
For each mode and eligible replicate:
- stream-phase counts for C and S;
- stream-noncollapse versus its own L11 reference;
- aggregate correct_done;
- maturity, matching, terminal-integrity, and zero-branch-damage checks.

CLASSIFICATION
GLOBAL_CELL59_SENSITIVITY:
cell59 causes stream collapse in at least two eligible replicates and the failing replicate set is identical across U_A0 and U_A25.

REPLICATE6_CONTEXT_SPECIFIC:
replicate6 fails in both modes and no other eligible replicate fails.

CROSS_MODE_DIFFERENCE:
the failing eligible replicate sets differ between U_A0 and U_A25.

NO_REPRODUCED_CELL59_EFFECT:
no eligible replicate fails in either mode.

OTHER_CONTEXT_PATTERN:
a valid pattern occurs that matches none of the above.

SUCCESS
YGG_A25_CELL59_PORTABILITY_ATTRIBUTION=true iff all evidence is valid and exactly one preregistered classification is produced.

FAILURE
Do not change target cell, eligibility, thresholds, task, alpha, repair state, scheduler, horizon, or service capacity after results.

BOUNDARY
Diagnostic only.
No accepted baseline mutation.
No online adaptation.
No recursive self-modification.
