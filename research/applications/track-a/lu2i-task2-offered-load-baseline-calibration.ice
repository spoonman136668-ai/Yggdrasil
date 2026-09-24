TITLE: LU-2I — TASK-2 OFFERED-LOAD BASELINE CALIBRATION
DATE: 2026-09-24
STATUS: PREREGISTERED / EXACT-PARENT ONLY / NO LEARNED ARM
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT DIAGNOSIS:
dba00160c1e783af47c6d43b8d695b608c171736

LU-2G CLOSURE:
1fcfef885ca9bd8c3219333965d90cc9cc4a60e9

LU2GF1:
e9a01aa97587fc97dde073cb2a6a35ad141006cd

SCIENTIFIC QUESTION

Did LU-2G fail exact-parent baseline feasibility primarily because three
two-stage Task-2 requests per epoch overload the whole service pipeline,
even though that load was chosen to normalize PROCESS-operation demand?

HYPOTHESIS

If offered-load mismatch is the dominant cause identified by LU-2H,
then reducing Task-2 arrivals from exactly three to exactly two requests
per epoch while retaining the inherited 32-epoch expiry and all organism
dynamics should materially reduce pre-SENSE congestion and restore exact-parent
baseline feasibility in fresh worlds.

AUTHORITY

Exact V0.2 parent only.

U recruitment:
exact teacher.

H release:
exact teacher.

C/S stay-defect:
exact teacher.

FC/FS lifecycle:
exact teacher.

No learned inference is required.

No LU-1E weight is needed for scientific execution.

This is environment calibration, not a learned-authority comparison.

TASK-2 COMPUTATION

Retain LU-2G Task-2 exactly:

two causally ordered PROCESS operations;

immutable x0, PA, PB;

Stage A yA = PA(x0);

Stage B replaces x0 bit 0 with yA and computes PB;

verification from immutable provenance;

verification failure -> REPAIR_PENDING;

repair recomputes both stages;

mandatory independent re-verification;

no stage skipping.

ONLY PRIMARY ENVIRONMENT CHANGE

Requests per epoch:

LU-2G:
3

LU-2I:
2

Everything else remains inherited unless explicitly described below.

PHASE SCHEDULE

160 epochs.

Five 32-epoch phases.

Phase 0 balanced:
1 C + 1 S every epoch.

Phase 1 C-heavy:
two-epoch deterministic cycle:

epoch even within phase:
2 C + 0 S

epoch odd within phase:
1 C + 1 S

Thus every two epochs:
3 C + 1 S
=
3:1.

Phase 2 S-heavy:
mirror of Phase 1.

Phase 3 balanced:
1 C + 1 S every epoch,
with the exact inherited distributed lesion timing and geometry.

Phase 4 balanced:
1 C + 1 S every epoch,
with the exact inherited anchor relocation timing and geometry.

No phase id is exposed to developmental policy.

SERVICE ENVELOPE

Expiry:
32 epochs, unchanged.

Experiment horizon:
160 epochs, unchanged.

Scheduler:
unchanged.

Cellular operation selection:
unchanged.

Corruption semantics:
unchanged.

Repair / verification math:
unchanged.

Lesion:
unchanged.

Anchor relocation:
unchanged.

D2 / LOCAL_HEDGE / ECHO_PHASE / NO_POOL / G5_FULL OFF:
unchanged.

PROGRAM DERIVATION

Implementation must freeze before fresh LU-2I programs/worlds exist.

Let the implementation freeze identity be LU2IF1.

For replicate 1..10 derive fresh Task-2 programs from:

LU2I-TASK2-L2|LU2IF1|replicate|stream|stage|counter

Programs remain balanced, nonconstant, nonaffine, deterministic, and
distinct within replicate using deterministic duplicate resolution only.

No difficulty filtering.

No world replacement.

No rejection sampling.

PRIMARY WORLDS

Exactly 10 fresh exact-parent worlds.

Derive only after LU2IF1 exists.

Namespace:

LU2I-TASK2-L2|LU2IF1|replicate

replicate 1..10.

Bind all ten complete manifests before any scientific world executes.

Do not reuse LU-2G manifest identities.

BASELINE FEASIBILITY

Use the exact LU-2G baseline-feasibility contract:

- at least one correct DONE in every phase;
- zero incorrect DONE;
- both C and S streams produce correct DONE;
- verification / repair integrity pass;
- finite operations per correct completion;
- no impossible manifest or scheduler condition.

Primary calibration success requires:

at least 8 / 10 exact-parent worlds baseline-feasible.

This threshold is fixed before execution.

DIAGNOSTIC MEASURES

Observation-only instrumentation shall report:

pre-SENSE wait distribution;

SENSE -> PROCESS_A extra wait;

PROCESS_A -> PROCESS_B extra wait;

PROCESS_B -> first ROUTE extra wait;

between-route-hop extra wait;

last ROUTE -> first VERIFY extra wait;

age and remaining lifetime at first VERIFY;

deadline-impossible corruption counts;

repair completion / censoring;

phase-specific correct DONE, expiry, unfinished, backlog, and
operations per correct completion.

RECOVERY TARGET

Retain the frozen LU-2G recovery target only as a diagnostic.

It is NOT a LU-2I success gate.

Report for demand reversal, lesion onset, and anchor relocation:

target rate;

maximum achieved four-epoch rate within +8 epochs;

whether the old target is reached.

Do not redefine the recovery target inside LU-2I after observing results.

DECISION

LU2I_L2_BASELINE_CALIBRATED = TRUE iff:

- duplicate ten-world exact-parent sweeps are byte-identical;
- at least 8 / 10 worlds satisfy exact LU-2G baseline feasibility;
- zero incorrect DONE occurs in all ten worlds;
- exact parent / substrate identities are preserved;
- the only task-environment change from LU-2G is the preregistered arrival schedule.

If fewer than 8 / 10 worlds are baseline-feasible:

LU2I_L2_BASELINE_CALIBRATED = FALSE.

Interpret that as evidence that reducing offered load to two requests per
epoch is insufficient to make Task-2 a valid transfer benchmark under the
inherited 32-epoch envelope.

No learned-authority conclusion may be drawn.

CAUSAL INTERPRETATION

If LU2I_L2_BASELINE_CALIBRATED = TRUE and pre-SENSE congestion falls
substantially relative to the sealed LU-2H observation, the offered-load
mismatch hypothesis is supported.

This does not itself establish learned-U transfer.

It only establishes a baseline-feasible Task-2 environment candidate that
may later receive a fresh learned-authority transfer preregistration.

NO POST-RESULT TUNING

After LU2IF1:

do not change load;
expiry;
phase schedule;
program derivation;
corruption;
scheduler;
repair;
verification;
manifest count;
baseline bars;
or exact-parent dynamics.

PLAIN-SPEAK QUESTION

LU-2H showed that Task-2 jobs are not spending most of their time on the
second calculation, routing, or verification.

They are waiting to start.

The typical job spends 26 of its 32 lifetime epochs waiting before SENSE.

So this experiment changes one thing only:

instead of offering three two-stage jobs every epoch, offer two.

The hand-written parent gets tested by itself on ten fresh worlds.

If at least eight worlds now satisfy the exact same baseline integrity rules,
we have strong evidence that the old Task-2 benchmark simply asked the
service pipeline to admit work faster than it could sustainably process it.

If it still fails, we keep looking at the environment boundary rather than
blaming the neural recruiter.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
