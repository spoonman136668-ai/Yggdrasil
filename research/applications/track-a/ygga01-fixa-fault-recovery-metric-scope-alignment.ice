TITLE: YGG-A01-FIXA — Fault-Recovery Metric Scope Alignment
DATE: 2026-09-20
STATUS: PREREGISTERED / CORRECTIVE APPLICATION RERUN / NON-CANONICAL
TRACK: YGGDRASIL APPLICATION TRACK A
PARENT: YGG-A01 FROZEN PRIMARY
BRANCH: dg1a-ar

PURPOSE

The first frozen YGG-A01 trial was fully reproducible
but its primary signal was FALSE because the implementation of M4
included the F204 partition-contained fault.

The preregistration defines M4 only for:

F96
and
F480.

F204 belongs to the partition scenario.

YGG-A01-FIXA asks:

WHAT IS THE PREREGISTERED APPLICATION RESULT
WHEN THE FROZEN TRIAL IS RE-EVALUATED
WITH THE M4 EVENT SET IMPLEMENTED EXACTLY AS WRITTEN?

BOUNDARY

This is not a task-logic repair.

This is not threshold tuning.

This is not schedule tuning.

The only allowed semantic change is:

fault_recovery_within_2

must be evaluated from recovery events:

96
and
480

only.

F204 must remain visible in raw recovery telemetry
but must not contribute to M4.

FROZEN R1 REFERENCE

Original frozen source SHA-256:

0101cf351b9805360e6549a9f29129f86757777fa5475c4b72bd9176b6e33e94.

Original trial output SHA-256:

e3cc4dcba7265322bb98716a4207ec2962023e55b2bc44e7f266266c36b34629.

Original records SHA-256:

a41a6bf75d1632b5d27b9b1a6d1fb67feb41f1f411c749ecd986d57a9b2c6b4e.

Original final-state SHA-256:

f304152651384c8176860b988045424ced9283549a962e4d798d12798efe735e.

ALLOWED CODE CHANGE

Inside run_trial():

retain the raw loop that reports every fault recovery latency,
including F204.

For the boolean M4 result:

fault_recovery_within_2 = TRUE

iff:

latency(F96) is not null and <=2
AND
latency(F480) is not null and <=2.

No other event contributes to that boolean.

FORBIDDEN CHANGES

Do not change:

- cell model;
- task shard function;
- frame generator;
- fault injections;
- partition windows;
- resource budgets;
- hibernation policy;
- reactivation policy;
- role migration policy;
- role donor selection;
- governance roots;
- registry roots;
- checksum authority thresholds;
- partition provisional thresholds;
- hereditary capsule logic;
- stale-history challenge;
- witness rotation;
- restart logic;
- primary signal formula except through the corrected M4 boolean;
- negative controls.

EQUIVALENCE GUARDS

Because the organism logic must be unchanged:

records_sha256 MUST equal:

a41a6bf75d1632b5d27b9b1a6d1fb67feb41f1f411c749ecd986d57a9b2c6b4e.

final_state_sha256 MUST equal:

f304152651384c8176860b988045424ced9283549a962e4d798d12798efe735e.

Raw fault recovery telemetry MUST remain:

F96 = 0.
F204 = 20.
F480 = 1.

All non-M4 application metrics must remain identical to the original frozen trial.

PRIMARY CORRECTIVE SIGNAL

FIXA_METRIC_ALIGNMENT_VALID

TRUE iff:

records_sha256 matches original R1
AND
final_state_sha256 matches original R1
AND
raw recovery latencies remain 0 / 20 / 1
AND
M4 evaluates only F96 and F480.

Then report the unchanged YGG-A01 primary formula
using the corrected M4 value.

REPRODUCIBILITY

Two complete deterministic trials.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first FIXA primary frame begins,
no further change is allowed.

PLAIN-SPEAK PREREGISTERED QUESTION

We are not giving the organism a second chance by changing the test.

We are correcting the scoreboard so it matches the test we wrote before the run.

The organism must do exactly the same thing,
frame for frame,
state for state.

If anything about its behavior changes,
the correction is invalid.

The only question is:

when we count the two recovery tests we actually preregistered,
does the application gate pass?

canonical_scientific_execution = false.
stab18_r1_touched = false.
