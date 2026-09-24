TITLE: LU-2H — TASK-2 EXACT-PARENT SERVICE-ENVELOPE DIAGNOSIS
DATE: 2026-09-24
STATUS: PREREGISTERED / OBSERVATION-ONLY / NOT EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT CLOSURE:
1fcfef885ca9bd8c3219333965d90cc9cc4a60e9

LU2GF1:
e9a01aa97587fc97dde073cb2a6a35ad141006cd

TEN-MANIFEST BINDING:
84c5e2f408629740c3016c7b3aad37522c5c8a7e

PRIMARY SWEEP SHA256:
cf33e4bbced5c02f577ed195acd8af4f197742897a1e2f9eab4b926aba2fa09f

QUESTION

Which component of the frozen Task-2 service envelope makes the exact U_A0
parent fail baseline feasibility in 6 of 10 worlds and produce null
recovery values even in the four baseline-feasible worlds?

OBSERVATION BOUNDARY

Use exactly the ten already-bound LU-2G manifests.

Observe only U_A0.

No U_A25 execution is required for this diagnosis.

No new world.

No manifest replacement.

No rejection sampling.

No dynamics change.

No scheduler change.

No expiry change.

No load change.

No corruption change.

No recovery-threshold change.

No learned-model change.

MEASURE

For every request that enters the pipeline, record:

creation epoch;
first SENSE epoch;
PROCESS_A epoch;
PROCESS_B epoch;
all ROUTE epochs;
first VERIFY epoch;
first failed VERIFY epoch if corrupted;
REPAIR epoch;
post-repair VERIFY epoch if observed;
DONE epoch;
EXPIRED epoch.

Derive:

pre-SENSE wait;

SENSE -> PROCESS_A extra wait beyond the next epoch;

PROCESS_A -> PROCESS_B extra wait;

PROCESS_B -> first ROUTE extra wait;

between-route-hop extra wait;

last ROUTE -> first VERIFY extra wait;

age at first VERIFY;

remaining lifetime at first VERIFY;

remaining lifetime at failed first VERIFY;

count of corruptions first reaching egress with no epoch available for
initial VERIFY before expiry;

count of detected corruptions with no epoch available for REPAIR before expiry;

count of repaired requests censored before mandatory re-VERIFY;

finite-horizon censoring.

RECOVERY DIAGNOSIS

For demand reversal at epoch 64,
lesion onset at epoch 96,
and anchor rotation at epoch 128:

retain the exact frozen recovery target used by LU-2G;

report the maximum achieved four-epoch completion rate
within the frozen +8 epoch search window;

report the target rate;

report whether the target is mathematically observed as reachable
in that window for U_A0.

Do not change the target.

SERVICE CAPACITY

Report phase-specific:

correct DONE;
expiry;
unfinished;
mean backlog;
maximum local backlog;
operations per correct completion.

DIAGNOSTIC DECISION

Classify the dominant exact-parent failure as one or more of:

PRE_SENSE_CONGESTION

TWO_PROCESS_STAGE_SERVICE_COST

ROUTE_OR_VERIFY_CONGESTION

EXPIRY_ENVELOPE_MISMATCH

RECOVERY_TARGET_MISMATCH

FINITE_HORIZON_CENSORING

or

UNRESOLVED

This is diagnosis only.

It cannot retroactively change LU-2G.

NEXT USE

Use the sealed diagnosis to preregister a new Task-2 environment contract
that is baseline-feasible for the exact parent before learned-U transfer is
tested again.

No parameter may be selected by looking for learned-U advantage.

PLAIN-SPEAK QUESTION

The neural cell was not the thing that broke LU-2G.

The exact parent could not reliably satisfy the new benchmark.

This audit asks where the benchmark is spending the time:

before work starts,
inside the extra processing stage,
while routing,
while verifying and repairing,
or inside a recovery target that Task-2 cannot physically hit.

We measure first.

We do not tune yet.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
