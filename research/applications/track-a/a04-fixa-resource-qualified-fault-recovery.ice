TITLE: YGG-A04-FIXA — Resource-Qualified Fault-Recovery Metric Alignment
DATE: 2026-09-20
STATUS: PREREGISTERED / CORRECTIVE APPLICATION REPLICATION / NON-CANONICAL
TRACK: YGGDRASIL APPLICATION TRACK A
PARENT: A04 Fixed-Seed Environment Generalization R1
BRANCH: dg1a-ar

PURPOSE

A04 R1 was reproducible and passed every primary signal except the M6 fault-recovery aggregate.

Two outside-partition fault targets were repaired into healthy DORMANT state
because the active-cell resource budget had no spare slot at the repair-due epoch.

The A04 preregistration limits M6 to faults:

outside partition
AND
when sufficient recoverable resources exist.

R1 implemented only the outside-partition half.

A04-FIXA asks:

WHAT IS THE PREREGISTERED A04 RESULT
WHEN M6 RESOURCE QUALIFICATION IS IMPLEMENTED EXPLICITLY
WITHOUT CHANGING ORGANISM BEHAVIOR?

BOUNDARY

Synthetic software only.
No production mutation.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

R1 PRESERVED RESULT

Frozen A04 source SHA-256:

d40fd3ac9b9b792df62e5e40b1b83627a24eac3ee906d8a1519ae74c8cf07122.

R1 serialized output SHA-256:

4eba15119bad474d097a8c0a9fcc67aa4ff783533918bcfd1c7cb6c307646cf8.

R1 fixed-seed schedule manifest:

24cfb3a9fa92b1013948739b7a9f022e0457bd550c91cc591fbbb9f7fbd9df43.

R1 aggregate candidate task-output stream SHA-256:

81805844f6eb663d73774e1b6eaf689747c04207570dae089b3fded5ae9539b5.

R1 task observations:

total requests = 55296;
candidate served = 51537;
candidate correct = 51537;
candidate incorrect = 0;
static served = 38682;
oracle served = 51981;
candidate coverage = 0.9320203993055556;
static coverage = 0.6995442708333334;
static gain = 0.2324761284722222;
oracle efficiency = 0.9914584174987014;
maximum non-partition reallocation = 3;
median non-partition reallocation = 1.0;
scenarios beating static = 12.

ALLOWED CHANGE

A04-FIXA may change only M6 fault-event qualification / reporting.

For every generated damage event:

raw fault telemetry remains recorded.

A fault is M6 ordinary-recovery eligible iff:

1. the fault epoch is outside an active communication partition;

AND

2. at the repair-due epoch:

repair_due = fault_epoch + 1,

immediately BEFORE the repair action is processed,

the current number of cells whose state consumes an active resource slot
is strictly less than the environment's current active-cell budget.

Frozen active-resource-slot states:

ACTIVE;
REACTIVATING.

QUARANTINED fault targets do not count as active service slots.

DORMANT cells do not count.

Thus:

resource_qualified =
pre_repair_active_or_reactivating_count < active_budget(repair_due).

This rule must be evaluated before the target repair result is known.

It may not depend on:

- whether the target eventually becomes active;
- whether the target eventually becomes dormant;
- observed recovery latency;
- task accuracy;
- candidate coverage.

Therefore qualification is not outcome-selected.

EXPECTED R1 DIAGNOSTIC CASES

S08 fault epoch 334:

repair_due = 335;
pre-repair active / reactivating count = 10;
active budget = 10;

resource_qualified = FALSE.

S10 fault epoch 40:

repair_due = 41;
pre-repair active / reactivating count = 11;
active budget = 10;

resource_qualified = FALSE.

These exact classifications are preregistered from the preserved R1 diagnosis.

All other fault events must be classified mechanically by the same rule.

FORBIDDEN CHANGES

Do not change:

- fixed 12 seeds;
- environment generator;
- demand vectors;
- cap windows;
- damage times;
- damage target selection;
- partition windows;
- restart epoch;
- transform task;
- A02 organism policy;
- migration policy / ordering;
- hibernation policy;
- reactivation policy;
- repair timing;
- governance / registry thresholds;
- re-merge semantics;
- static baseline;
- oracle calculation;
- reallocation scoring;
- task metrics;
- primary thresholds.

EQUIVALENCE GUARDS

Because organism behavior must remain unchanged:

aggregate candidate task-output SHA-256 MUST equal:

81805844f6eb663d73774e1b6eaf689747c04207570dae089b3fded5ae9539b5.

The following R1 aggregate observations MUST remain exactly:

candidate served = 51537;
candidate correct = 51537;
candidate incorrect = 0;
static served = 38682;
oracle served = 51981;
coverage = 0.9320203993055556;
static gain = 0.2324761284722222;
oracle efficiency = 0.9914584174987014;
maximum reallocation = 3;
median reallocation = 1.0;
scenarios beating static = 12.

All partition,
restart,
and safety observations must remain unchanged.

RAW FAULT TELEMETRY

FIXA must report every fault,
including resource-unqualified faults.

For every fault report:

scenario;
fault epoch;
target;
inside_partition;
repair_due_epoch;
pre_repair_active_slot_count;
repair_due_budget;
resource_qualified;
raw restored service-active epoch if any;
raw latency if any;
final healthy / state outcome.

Unqualified faults do not disappear.

They are excluded only from the M6 ordinary-recovery maximum.

PRIMARY CORRECTIVE SIGNAL

A04_FIXA_RESOURCE_QUALIFICATION_VALID

TRUE iff:

fixed-seed schedule manifest unchanged
AND
aggregate task-output SHA matches R1
AND
all task / adaptation aggregates match R1
AND
S08/F334 is resource-unqualified by the frozen rule
AND
S10/F40 is resource-unqualified by the frozen rule
AND
all raw fault events remain present
AND
every M6-qualified outside-partition fault has a restored service-active latency <= 2
AND
no M6-qualified fault remains unrestored
AND
all restart / partition / safety observations match R1.

CORRECTED APPLICATION SIGNAL

A04_FIXED_SEED_GENERALIZATION_ACCEPTED

TRUE iff:

A04_FIXA_RESOURCE_QUALIFICATION_VALID
AND
all original A04 primary thresholds,
evaluated with corrected M6 eligibility,
are TRUE.

REPRODUCIBILITY

Two complete deterministic 12-seed FIXA sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After first FIXA primary request begins,
no further semantic or scoring change is allowed.

PLAIN-SPEAK PREREGISTERED QUESTION

We are not changing how the cells behave.

We are fixing what counts as a fair two-frame recovery test.

If a repaired cell is healthy
but every allowed active slot is already occupied,
then it cannot legally become active without breaking the resource budget.

That is not the same situation as:

"the cell had room to return and failed to recover."

So FIXA checks whether there was actually an empty active slot
before the repair happened.

It makes that decision before seeing what the repaired cell does.

The two constrained faults stay in the record.

They simply stop being scored as ordinary fast-recovery tests
if the preregistered resource condition was not satisfied.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A04-FIXA RESOURCE-QUALIFIED FAULT RECOVERY

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST FIXA PRIMARY REQUEST.

IMPLEMENTATION COMMIT

afdb95c5b23f59a39996417f01c1b8b3e6534615.

SOURCE BUNDLE

Loader:

research/applications/track-a/a04_fixa_resource_qualified_v1.py

Loader Git blob:

77f49d896f49169cab1878f1cddf0a28c03da567.

Payload:

research/applications/track-a/a04_fixa_resource_qualified_v1.py.gz

Payload Git blob:

5393447b9e4cc00e0367424fd96104f3f7f713e5.

Compressed payload SHA-256:

5d440c661b34a61bea8c5a716a4c68cd933710a89e17459788c1aca4402081f3.

Compressed payload bytes:

8307.

Decompressed source SHA-256:

0b0f1a47e109ee8f218c664c568dd981c97bfb382c54ec30d035e6c8cf4e4f1a.

Decompressed source bytes:

29602.

SEMANTIC DIFF FROM A04 R1

Allowed scoring instrumentation only:

- capture pre-repair active / reactivating count;
- capture repair-due active budget;
- compute resource_qualified before repair outcome;
- exclude outside-partition faults from ordinary M6 only when no active resource slot exists;
- report every raw fault and FIXA equivalence evidence.

No organism action path changed.

The frozen diff does NOT alter:

damage;
repair;
role migration;
hibernation;
reactivation;
partition operation;
dynamic re-merge;
restart;
task output;
static baseline;
oracle behavior.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

A02 dependency source SHA-256:

b2eeb1e589a029f16b0437ce1f3dd05826b81a91ab6c6d91ce25bb28b96db60b.

A04 fixed-seed manifest:

24cfb3a9fa92b1013948739b7a9f022e0457bd550c91cc591fbbb9f7fbd9df43.

Environment diversity:

PASS.

Non-primary mechanical-seed R1 / FIXA equivalence:

TRUE

for candidate behavior,
static baseline,
oracle result,
reallocation,
restart,
partition re-merge,
resource-budget behavior,
and task-service observations.

The mechanical probe changed only fault-qualification telemetry as permitted.

No A04-FIXA primary request was executed before this freeze.

R1 EQUIVALENCE ANCHORS

A04 R1 task-output stream SHA-256:

81805844f6eb663d73774e1b6eaf689747c04207570dae089b3fded5ae9539b5.

R1 aggregate observations remain the exact required FIXA targets specified above.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
