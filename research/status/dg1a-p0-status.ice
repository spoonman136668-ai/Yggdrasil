TITLE: DG-1A-P0 Current Status
DATE: 2026-09-17
STATUS: ACTIVE — STAB-04 CLOSED NEGATIVE / STAB-05 DESIGN NOT YET PREREGISTERED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
e0dffe919ebf4f6c62117b7c87384e2ef56c379b

CURRENT PURPOSE
Establish a trustworthy canonical developmental NCA control with bounded growth, persistence, meaningful damage, and stable regeneration before DG-1B functional computation or later Yggdrasil mechanisms are opened.

IMPLEMENTED SURFACE
- fixed-grid shared-rule NCA substrate;
- deterministic seed and repository-native target generation;
- state-pool persistence/regeneration curricula;
- maturity-gated training damage;
- independent training/evaluation lesion geometry;
- global and stable recovery metrics;
- persistence telemetry;
- resource accounting;
- resumable deterministic training sessions;
- machine-readable evidence writer and runner;
- explicit global_mse, balanced_fg_bg, and global_plus_foreground training loss modes;
- foreground/background balanced morphology helper;
- target-foreground morphology helper;
- fail-closed empty-foreground behavior;
- fail-closed config validation.

LATEST TEST STATUS
STAB-04 reconstructed sandbox regression:
61 passed
0 failed
Environment: Python 3.13.5 / PyTorch 2.10.0+cpu

The sandbox source was semantically reconstructed from connected GitHub readbacks of implementation/test revision:
c90809c9b0c793f003e398731e931aa6a7058f5e

This was not a native commit checkout and byte identity was not established. Treat the test and scientific result as sandbox evidence, not authoritative hardware or commit-bound acceptance.

SCIENTIFIC / EXPERIMENTAL FRONTIER
Small-grid P0 work established a replicated exploratory pattern in which maturity-gated regeneration differs strongly from growth-only post-lesion collapse, but confirmatory support remains blocked by commit-bound provenance requirements.

Full-grid 40 x 40 stabilization remains unresolved.

STAB-01 — CLOSED NEGATIVE
Increasing fixed maturity threshold to M32/M64 did not provide a valid monotonic stabilization mechanism.

STAB-02 — CLOSED NEGATIVE
Extending training development horizon to 64..128 produced an all-dead phenotype.
Key diagnostic: global unweighted morphology MSE allowed the sparse-target dead state to achieve approximately 0.0295742 loss.

STAB-03 — CLOSED NEGATIVE
BAL-50 foreground/background-balanced training avoided the all-dead attractor but produced an overgrown poor-morphology phenotype.
Measured seed-0 sandbox result:
- pre-damage active cells: 1579 / 1600;
- pre-lesion global morphology MSE: 0.1411564797;
- 0.60 lesion removed 36.48% of active cells;
- DamageEffect: -0.0361511707;
- lesion invalid for regeneration inference;
- final active cells: 1164 / 1600;
- improvement rule: FAIL.

STAB-04 — CLOSED NEGATIVE
Candidate: FG+1
TrainingMorphologyLoss = GlobalVisibleMSE + 1.0 * ForegroundVisibleMSE

Exactly one fresh seed-0 candidate was executed through a single-writer resumable checkpoint path.
Measured sandbox result:
- training iterations: 200 / 200;
- minimum recorded loss: 0.0645382553;
- final recorded loss: 0.0687634796;
- pre-damage active cells: 1578 / 1600;
- pre-lesion global morphology MSE: 0.1845480204;
- post-lesion global morphology MSE: 0.1184445843;
- DamageEffect: -0.0661034361;
- RelativeDamageEffect: -0.3581909788;
- active-cell removal: 36.50%;
- final active cells: 1073 / 1600;
- stable T50/T90: not attained / undefined;
- bounded RecoveryFraction: undefined;
- improvement rule: FAIL;
- candidate worth widening: NO.

STAB-04 FAILURE MODE
OVERGROWN / POOR-MORPHOLOGY PHENOTYPE WITH INVALID LESION.

The 0.60 evaluation lesion removed more than one-third of active cells yet improved the unchanged global morphology MSE. Therefore no valid morphology loss existed from which to infer regeneration.

CURRENT OBJECTIVE DIAGNOSIS
The P0 objective problem is now repeatedly bracketed by two opposite degeneracies:
- global occupancy-weighted MSE alone can make sparse-target death competitive;
- strong explicit foreground pressure can preserve viability while allowing excessive active/foreground structure and poor global morphology.

STAB-03 and STAB-04 independently produced the latter class under different foreground-emphasis formulations.

DURABLE EVIDENCE
research/experiments/dg1a/dg1a-p0-stab03-result.ice
evidence/dg1a/p0_stab03_sandbox.json
research/experiments/dg1a/dg1a-p0-stab04-spec.ice
research/experiments/dg1a/dg1a-p0-stab04-result.ice
evidence/dg1a/p0_stab04_sandbox.json

CURRENT DECISIONS
- close STAB-04 as negative;
- do not widen FG+1 to additional seeds;
- do not tune the FG coefficient inside STAB-04;
- preserve global morphology MSE as the common evaluation metric;
- preserve global_mse, balanced_fg_bg, and global_plus_foreground for historical reproducibility;
- do not reopen STAB-01 through STAB-04 with post-result threshold or parameter inserts;
- do not begin DG-1B yet;
- do not introduce Fibonacci scheduling into canonical P0 yet;
- retain Fibonacci as the separate DG-1A-FIB1 follow-on ablation;
- retain negative results as first-class research knowledge.

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-05, DESIGN / PREREGISTRATION ONLY.

STAB-05 must target the repeated occupancy/overgrowth failure directly. Do not convert it into an after-the-fact sweep of the STAB-04 foreground coefficient.

Before execution, the packet must preregister:
- one explicit mechanism;
- one fixed parameterization;
- why it addresses occupancy/overgrowth rather than merely shifting foreground weight;
- the unchanged global evaluation metric;
- the canonical H96/M16 envelope unless a separately justified single-factor change is the experiment;
- explicit viability, lesion-validity, morphology, active-cell, recovery, and finite-state gates.

No STAB-05 mechanism is selected by this status record.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
No claim of cognition, functional specialization, continual learning, ancestor inheritance, or general intelligence is authorized.

NEXT ACTION
Design and preregister STAB-05. Do not execute it until its single factor and gates exist in .ice. Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling.
