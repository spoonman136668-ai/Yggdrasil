TITLE: LU-2K — FRESH EXACT-PARENT VALIDATION OF L1 TASK-2 ENVIRONMENT
DATE: 2026-09-24
STATUS: PREREGISTERED / NO LU-2K WORLD DERIVED OR EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2I CLOSURE:
1cfbfd3c3bfad9233bc9493b94f5b6db96f7bc9d

PARENT LU-2J CLOSURE:
9da321fbc63681acc01b8f6ed05d3b9a23d13577

LU2IF1:
326f89f940818a6abb0fcbc999595b844936dc53

PURPOSE

Validate on a completely fresh exact-parent world set whether the L1
Task-2 environment identified by LU-2I is genuinely baseline-feasible
before learned U is allowed back into Task-2.

SCIENTIFIC QUESTION

At exactly one Task-2 request per epoch, does the exact V0.2 parent satisfy
the inherited Task-2 baseline-feasibility contract in at least 8 of 10
fresh worlds while preserving both functional streams and zero incorrect
DONE?

ARMS

Exactly one arm:

U_A0 exact parent.

No learned U.
No alpha blend.
No learned H.
No optimizer.
No retraining.
No adaptation.

TASK-2 ENVIRONMENT

Retain the frozen LU-2G / LU-2I Task-2 computation exactly:

two causally ordered PROCESS stages;
immutable x0, PA, PB provenance;
Stage B input constructed from Stage A output;
mandatory verification;
corruption detection;
repair by recomputing both stages from immutable provenance;
mandatory re-verification after repair.

Retain:

64-cell ring;
C/S directional streams;
D2;
LOCAL_HEDGE;
ECHO_PHASE;
NO_POOL;
G5_FULL OFF;
request-bound handoff;
neutral sensing;
distributed lesion;
anchor relocation;
inherited 32-epoch expiry;
160-epoch horizon;
five 32-epoch phases.

OFFERED LOAD

Exactly one request per epoch.

Do not change expiry to make L1 pass.
Do not change the Task-2 service path.
Do not change corruption or verification semantics.

IMPLEMENTATION FREEZE

Create LU2KF1 before deriving any LU-2K primary world.

The implementation must bind:

L1 only;
exact parent only;
fresh-world derivation;
strict baseline-feasibility evaluation;
descriptive recovery reporting.

No world may exist before LU2KF1.

FRESH WORLDS

Exactly 10 fresh worlds.

Namespace:

LU2K-TASK2-L1-EXACT-PARENT|LU2KF1|replicate

replicate 1..10.

Do not reuse any LU-2G, LU-2H, LU-2I, or LU-2J world.

Bind all ten complete manifests before any execution.

No world replacement.
No rejection sampling.
No result-dependent manifest choice.

BASELINE-FEASIBILITY CONTRACT

For each world, strict baseline-feasible is TRUE iff exact U_A0 has:

1. at least one correct DONE request in every phase;
2. zero incorrect DONE;
3. both C and S streams produce correct DONE;
4. verification / repair integrity passes;
5. finite operations per correct completion;
6. no impossible manifest or scheduler condition.

This is the same baseline-feasibility concept used in LU-2G and LU-2I.
Do not add an absolute legacy-clearance score.

PRIMARY VALIDATION SIGNAL

LU2K_L1_EXACT_PARENT_ENVIRONMENT_VALIDATED = TRUE iff:

- duplicate complete ten-world sweeps are byte-identical;
- at least 8 / 10 worlds are strict baseline-feasible;
- all 10 worlds have zero incorrect DONE;
- all 10 worlds retain both C and S functional completion;
- no manifest or integrity identity defect occurs.

Otherwise FALSE.

If fewer than 8 / 10 worlds are baseline-feasible, L1 is not authorized
for learned-U transfer and the failure must be diagnosed before any learned
Task-2 comparison.

RECOVERY METRICS

Report the frozen demand-reversal, lesion, and anchor-relocation recovery
latencies descriptively.

Do not use them as LU-2K decision gates.

Reason:

LU-2H established that the earlier recovery target was not baseline-feasible
at L3, while LU-2I showed it becomes attainable as offered load falls.

LU-2K is specifically validating the strict baseline service/integrity
environment at L1, not retuning a recovery threshold.

EXPOSURE REPORTING

For each world and aggregate across ten worlds report:

scheduled corruptions;
corruption applied;
corruptions reaching egress;
verification detected;
repaired;
correct DONE after repair;
expired;
pre-SENSE median / mean / p90.

This is observation-only and not a tuning channel.

MECHANICAL GATE BEFORE LU2KF1

Prove:

1. exact LU2IF1 parent import / identity;
2. exact V0.2 parent authority;
3. requests_per_epoch == 1;
4. exact Task-2 two-stage computation;
5. exact corruption / repair / reverify semantics;
6. exact 32-epoch expiry;
7. exact 160-epoch horizon and phase structure;
8. no learned-model invocation;
9. fresh namespace derivation depends on LU2KF1;
10. duplicate mechanical evidence byte-identical.

NO POST-RESULT TUNING

After LU2KF1 do not change:

load;
expiry;
Task-2 computation;
corruption;
repair;
verification;
phase structure;
manifest count;
baseline-feasibility definition;
world namespace;
or exact-parent authority.

NEXT STEP RULE

If LU2K_L1_EXACT_PARENT_ENVIRONMENT_VALIDATED = TRUE:

the L1 Task-2 environment is eligible for a separately preregistered learned-U
transfer experiment.

Do not automatically increase learned authority.

Use the already accepted 25-percent U blend lineage only if the next
preregistration explicitly authorizes it.

If FALSE:

diagnose the exact-parent failure before any learned-U Task-2 experiment.

PLAIN-SPEAK QUESTION

LU-2I showed that one Task-2 job per epoch almost eliminates the waiting line
and passed the strict baseline in nine of ten calibration worlds.

LU-2J showed the strange medium-load dip was mostly an exposure/scoring effect,
not a workforce collapse.

Now we need the clean confirmation.

Give the hand-written parent ten completely new one-job-per-epoch worlds.

If at least eight of them pass the same strict baseline rules, then Task-2
finally has a fair environment in which to ask whether learned recruitment
generalizes.

If the parent cannot do that reliably, the neural controller does not get
tested yet.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
