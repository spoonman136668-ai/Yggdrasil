TITLE: DG-1 Current Research Status
DATE: 2026-09-17
STATUS: ACTIVE — DG-1A P0 OBJECTIVE / VIABILITY STABILIZATION
TRACK: DG-1
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE; EXPLORATORY FOR SANDBOX RESULTS

PURPOSE
Maintain an operator-readable durable research status ledger. This record summarizes the live DG-1 frontier and points to experiment-specific evidence. It is not an execution authority.

CURRENT OBJECTIVE
Establish a viable canonical DG-1A developmental substrate that can grow a target morphology, remain stable, suffer meaningful damage, and exhibit measurable stable repair before opening DG-1B functional computation.

RESEARCH FOUNDATION
YG-R1 through YG-R8 research records exist.
YG-R8 Pass 1 is closed and reconciled into the DG-1 implementation gate.
Functional-regeneration, structural-plasticity, resource-pressure, and measurement contracts remain adopted for early DG-1 work.

ACTIVE BRANCH
dg1a-p0

LATEST VERIFIED REPOSITORY FRONTIER BEFORE THIS STATUS UPDATE
a0026df2561487a62061aa364208341777e623be

P0 IMPLEMENTATION STATUS
The bounded P0 substrate, training curricula, recovery/persistence telemetry, resource accounting, resumable training, explicit evidence, and three explicit training-loss modes are implemented:
- global_mse;
- balanced_fg_bg;
- global_plus_foreground.

Latest reconstructed sandbox regression:
61 passed
0 failed
Python 3.13.5 / PyTorch 2.10.0+cpu

The execution source was semantically reconstructed from connected GitHub readbacks of implementation/test revision c90809c9b0c793f003e398731e931aa6a7058f5e because the sandbox could not obtain a native checkout. Byte identity was not established. Treat this as sandbox evidence, not authoritative hardware or commit-bound scientific acceptance.

CURRENT FULL-GRID FINDINGS
STAB-01: NEGATIVE
Fixed maturity-threshold increases did not provide a valid monotonic stabilization mechanism.

STAB-02: NEGATIVE
Longer 64..128 developmental training horizons converged to an all-dead phenotype, exposing sparse-target degeneracy in global unweighted morphology MSE.

STAB-03: NEGATIVE
Equal 0.5/0.5 foreground/background balanced training loss prevented the all-dead solution but overcorrected toward an overgrown phenotype.
Measured seed-0 sandbox result:
- pre-damage active cells: 1579 / 1600;
- pre-lesion global morphology MSE: 0.1411564797;
- 0.60 center lesion removed 36.48% of active cells;
- post-lesion global MSE improved to 0.1050053090;
- DamageEffect: -0.0361511707;
- lesion invalid for regeneration inference;
- final active cells: 1164 / 1600;
- improvement rule failed.

STAB-04: NEGATIVE
Candidate FG+1 retained the global training loss and added one full foreground-visible MSE term.
Exactly one fresh seed-0 candidate was executed with single-writer resumable checkpoints.
Measured sandbox result:
- 200 / 200 training iterations;
- minimum recorded loss: 0.0645382553;
- final recorded loss: 0.0687634796;
- pre-damage active cells: 1578 / 1600;
- pre-lesion global morphology MSE: 0.1845480204;
- 0.60 center lesion removed 36.50% of active cells;
- post-lesion global MSE improved to 0.1184445843;
- DamageEffect: -0.0661034361;
- RelativeDamageEffect: -0.3581909788;
- final active cells: 1073 / 1600;
- stable T50/T90 undefined/not attained;
- candidate worth widening: NO.

CURRENT INTERPRETATION
The immediate P0 problem remains objective balancing, now with repeated evidence on both sides:
- global occupancy-weighted MSE can make sparse-target death competitive;
- strong foreground emphasis can avoid death while making excessive active structure competitive.

STAB-03 and STAB-04 reached the latter class through different objective formulations. In both, removing more than one-third of active cells improved the common global morphology metric, so regeneration inference was invalid.

This narrows the next research question from generic regeneration failure to explicit occupancy/structure control during morphology learning.

DURABLE STAB-04 RECORDS
research/experiments/dg1a/dg1a-p0-stab04-spec.ice
research/experiments/dg1a/dg1a-p0-stab04-result.ice
evidence/dg1a/p0_stab04_sandbox.json
research/status/dg1a-p0-status.ice

NEXT BOUNDED PACKET
Provisionally DG-1A-P0-STAB-05 — DESIGN / PREREGISTRATION ONLY.

No STAB-05 mechanism is selected by this status record.

The next mechanism must directly target occupancy/overgrowth rather than becoming a coefficient sweep of STAB-03 or STAB-04. Before execution it must define one fixed intervention, preserve the common global evaluation metric, retain the H96/M16 envelope unless that envelope is itself the preregistered single factor, and freeze viability, lesion-validity, morphology, active-cell, recovery, and finite-state gates.

FIBONACCI TRACK
DG-1A-FIB1 remains preserved and separate.
Planned later questions include Fibonacci repair budgets, capacity ceilings, golden-angle topology priors, module-size vocabularies, and emergence tests.
Do not introduce these into canonical P0 while the basic objective/viability problem remains unresolved.

LARGER DG-1 TRAJECTORY
stable local development
-> functional computation
-> specialization
-> functional regeneration
-> continual development
-> developmental neural modules
-> frozen intelligent seed
-> developmental adapters
-> ancestor inheritance
-> resource-constrained organism
-> regenerable capability

ANCESTOR INHERITANCE
Remains a first-class future direction. The goal is to test whether useful capability from previous models can be transformed into compact persistent developmental information that can regenerate task-relevant phenotype without retaining every donor checkpoint.

BOUNDARIES
Do not modify Wingless, ckb-plane, or Mind-Palace without explicit authorization.
Do not activate CKB runtime, Coinbase/live broker systems, TradeGuard, deployment/promotion, or external execution authority.
P0 remains morphology/developmental-substrate research and does not establish cognition or general intelligence.

NEXT ACTION
Design and preregister STAB-05. Do not execute it until its exact single factor and gates exist in .ice. Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling until canonical P0 viability/stability is adequately characterized.
