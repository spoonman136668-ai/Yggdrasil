TITLE: YGG-A24 L12 Marginal-Cell Attribution Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: bdd206305eeacd120e8d151184a9a1ad7c371859
PARENT_EXPERIMENT: YGG-A23

QUESTION
Is the A-context L12 service-quality failure caused by one specific marginal lesion cell, by several individual cells, or only by cumulative interaction?

NORTH-STAR TARGET
Localize the developmental substrate's pressure failure to a concrete cell-level mechanism before attempting any repair.

FROZEN FROM A23
- exact A23/A22 task, ten manifests, scheduler, horizon, service capacity, maturity, matching, and terminal-integrity rules;
- alpha=.25;
- repair OFF;
- exact learned weights;
- deterministic execution;
- U_A0 and U_A25;
- exact A23 stream-noncollapse threshold and aggregate >=.90 integrity threshold;
- no retraining or online adaptation.

ANCHOR
Exact A23 L11 lesion for each seed.

CANDIDATE ARMS
For each rank K in 12,13,14,15,16:
- derive the single cell added by A23 when moving from L(K-1) to LK;
- construct a constant-cardinality lesion consisting of the exact L11 lesion plus only that one rank-K marginal cell;
- lesion cardinality is therefore exactly 12 in every candidate arm.

REPORT
For each mode and candidate rank:
- exact marginal cell identity per replicate;
- stream-noncollapse versus the same-mode L11 anchor;
- exact failure replicate/phase/stream cells;
- aggregate correct_done ratio versus L11;
- matching, maturity, terminal-integrity, and zero-branch-damage checks.

CLASSIFICATION
SINGLE_CELL_SPECIFIC:
exactly one candidate rank causes stream collapse in both modes and all others pass.

MULTI_CELL_SENSITIVE:
two or more candidate ranks individually cause stream collapse in either mode.

CUMULATIVE_ONLY:
no single candidate rank causes stream collapse in either mode.

CROSS_MODE_DIFFERENCE:
the candidate pass/fail maps differ between U_A0 and U_A25.

SUCCESS
YGG_A24_L12_MARGINAL_CELL_ATTRIBUTION=true iff all evidence is valid and exactly one preregistered classification is produced.

FAILURE
Do not change candidate set, thresholds, anchor, alpha, repair state, task, scheduler, horizon, or service capacity after observing results.

BOUNDARY
Diagnostic only.
No accepted baseline mutation.
No online adaptation.
No recursive self-modification.
