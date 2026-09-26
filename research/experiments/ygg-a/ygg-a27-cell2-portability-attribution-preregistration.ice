TITLE: YGG-A27 Cell-2 Portability Attribution Preregistration
DATE: 2026-09-26
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_RESULT: YGG-A26 INPUT_DIVERGENCE
PARENT_CLOSURE: 2a5fe763cf2d20f369eaadd622650bdc7ff84c6a

QUESTION
Does the true A24 failing marginal cell, cell 2, independently trigger the hidden stream-collapse phenotype across frozen seed contexts, or is the effect specific to actual manifest replicate 6?

NORTH-STAR TARGET
Distinguish a globally critical developmental component from a context-dependent local interaction before designing any repair mechanism.

FROZEN
- exact A24/A25 task, ten manifests, scheduler, horizon, service capacity, maturity, matching, terminal-integrity, and stream-noncollapse rules;
- alpha=.25;
- repair OFF;
- exact learned weights;
- deterministic execution;
- U_A0 and U_A25;
- exact frozen L11 anchor construction;
- no retraining or online adaptation.

TARGET CELL
2.

ELIGIBILITY
A manifest is eligible iff cell 2 is not already present in its exact frozen L11 lesion.

TEST ARM
For every eligible manifest:
- exact L11 lesion plus cell 2;
- cardinality exactly 12;
- all non-lesion manifest fields frozen.
All reporting MUST use the manifest's actual replicate field, never list position or enumerate index.

REFERENCE
The exact same eligible manifest under its L11 anchor.

REPORT
For each mode and eligible actual replicate:
- stream-phase counts for C and S;
- stream-noncollapse versus its own L11 reference;
- aggregate correct_done;
- maturity, matching, terminal-integrity, and zero-branch-damage checks.

CLASSIFICATION
GLOBAL_CELL2_SENSITIVITY:
cell 2 causes stream collapse in at least two eligible actual replicates and the failing replicate set is identical across U_A0 and U_A25.

REPLICATE6_CONTEXT_SPECIFIC:
actual manifest replicate 6 fails in both modes and no other eligible actual replicate fails.

CROSS_MODE_DIFFERENCE:
the failing eligible actual replicate sets differ between U_A0 and U_A25.

NO_REPRODUCED_CELL2_EFFECT:
no eligible actual replicate fails in either mode.

OTHER_CONTEXT_PATTERN:
a valid pattern occurs that matches none of the above.

SUCCESS
YGG_A27_CELL2_PORTABILITY_ATTRIBUTION=true iff all evidence is valid, duplicate execution is byte-identical, actual replicate IDs are verified against the manifests, and exactly one preregistered classification is produced.

FAILURE
Do not change target cell, eligibility, thresholds, task, alpha, repair state, scheduler, horizon, service capacity, or replicate interpretation after results.

BOUNDARY
Diagnostic only.
No accepted baseline mutation.
No online adaptation.
No recursive self-modification.
