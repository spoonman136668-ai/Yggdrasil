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


PRE-RUN IMPLEMENTATION FREEZE 01 — YGG-A01-FIXA

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST CORRECTIVE PRIMARY FRAME.

HARNESS

research/applications/track-a/ygga01_telemetry_organism_fixa.py

Harness source commit:

b3d11a6a789989676c553f28a87fae1f2e708cf9.

Git blob SHA:

7db60f02e9d7eb50e75800c082585a511af44e4f.

Source SHA-256:

0bdd414b57c708abb41786a35296bc907b99234bf8430a273acb7c1617548cbb.

Source bytes:

28411.

PRE-FREEZE VALIDATION — NON-EVIDENCE

Exact committed GitHub bytes reconstructed in sandbox:

PASS.

Python syntax:

PASS.

Mechanical validate():

PASS.

Allowed delta from frozen R1 source:

one metric-selection block only.

Raw recovery telemetry remains part of output.

No task logic or organism transition changed.

REPRODUCIBILITY

Execute two complete deterministic trials from these exact bytes.

Serialized output SHA-256 must match exactly.

EQUIVALENCE GUARDS

records_sha256 must remain:

a41a6bf75d1632b5d27b9b1a6d1fb67feb41f1f411c749ecd986d57a9b2c6b4e.

final_state_sha256 must remain:

f304152651384c8176860b988045424ced9283549a962e4d798d12798efe735e.

No post-result tuning.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — YGG-A01-FIXA

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST FIXA PRIMARY FRAME.

HARNESS

research/applications/track-a/ygga01_telemetry_organism_fixa.py

Implementation commit:

b3d11a6a789989676c553f28a87fae1f2e708cf9.

Git blob SHA:

7db60f02e9d7eb50e75800c082585a511af44e4f.

Source SHA-256:

0bdd414b57c708abb41786a35296bc907b99234bf8430a273acb7c1617548cbb.

Source bytes:

28411.

PRE-FREEZE EQUIVALENCE AUDIT

Compared line-for-line against frozen V1.

Only three scoring-line changes exist.

Removed:
- initialization of fault_ok before iterating every recovery event;
- failure assignment for a missing arbitrary recovery event;
- latency >2 failure assignment for every recovery event.

Added:
- m4_keys = ("96","480");
- fault_ok = all(F96 and F480 are present and <=2).

No organism behavior code changed.

No task code changed.

No schedules changed.

No authority code changed.

No partition code changed.

No restart code changed.

No controls changed.

EQUIVALENCE GUARDS

FIXA must preserve:

records SHA-256 =
a41a6bf75d1632b5d27b9b1a6d1fb67feb41f1f411c749ecd986d57a9b2c6b4e.

final-state SHA-256 =
f304152651384c8176860b988045424ced9283549a962e4d798d12798efe735e.

raw fault latencies =
F96 0,
F204 20,
F480 1.

Two complete deterministic FIXA trials must be byte-identical.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — YGG-A01-FIXA

DATE:
2026-09-20.

STATUS:
CLOSED / POSITIVE CORRECTIVE PRIMARY / REPRODUCIBLE / METRIC ALIGNMENT VALID.

FROZEN HARNESS EXECUTED

research/applications/track-a/ygga01_telemetry_organism_fixa.py

Frozen Git blob:

7db60f02e9d7eb50e75800c082585a511af44e4f.

Frozen source SHA-256:

0bdd414b57c708abb41786a35296bc907b99234bf8430a273acb7c1617548cbb.

Source bytes:

28411.

REPRODUCIBILITY

Two complete deterministic 512-frame trials.

Sweep 1 serialized output SHA-256:

3765ed15d66e066f9f31ad9b3953aa8fa29debb594a7daa2aa36823f02b7e598.

Sweep 2 serialized output SHA-256:

3765ed15d66e066f9f31ad9b3953aa8fa29debb594a7daa2aa36823f02b7e598.

Byte-identical:

TRUE.

EQUIVALENCE GUARDS

Records SHA-256:

a41a6bf75d1632b5d27b9b1a6d1fb67feb41f1f411c749ecd986d57a9b2c6b4e.

Matches frozen R1:

TRUE.

Final-state SHA-256:

f304152651384c8176860b988045424ced9283549a962e4d798d12798efe735e.

Matches frozen R1:

TRUE.

Therefore the organism behavior,
frame decisions,
and final authoritative state
did not change.

RAW RECOVERY TELEMETRY

F96:

0 frames.

F204:

20 frames.

F480:

1 frame.

Raw telemetry unchanged from R1:

TRUE.

CORRECTED PREREGISTERED M4

M4 event set:

F96.
F480.

Both <=2:

TRUE.

fault_recovery_within_2:

TRUE.

PRIMARY APPLICATION SIGNAL

FIRST_PERSISTENT_ORGANISM_USEFUL:

TRUE.

APPLICATION METRICS

Authoritative false outputs:

0.

Connected availability:

0.9978448275862069.

Budget-8 steady availability:

1.0.

Budget-8 steady accuracy:

1.0.

Role-shortage recovery latency:

0 frames.

Partition false promotions:

0.

Dormant votes:

0.

Stale witness reclaims:

0.

Hereditary rewrite contested:

TRUE.

Hereditary evolution preserved:

TRUE.

All capsules valid:

TRUE.

Provenance multiplication:

0.

Restart suffix identical:

TRUE.

Restart final state identical:

TRUE.

Observed organism actions:

role migrations = 1.
hibernations = 12.
reactivations = 8.
repairs = 3.
same-target conflict rollbacks = 1.

NEGATIVE CONTROLS

Headcount quorum failure exposed:

TRUE.

Auto-wake stale-authority failure exposed:

TRUE.

Partition-majority unsafe selection exposed:

TRUE.

Archived-role veto failure exposed:

TRUE.

TECHNICAL INTERPRETATION

YGG-A01 now has one preserved invalid frozen measurement run
and one preregistered corrective rerun.

The corrective rerun did not improve organism behavior.

It changed only the implementation of the already-written M4 event scope.

The equivalence guards prove:

- identical frame record stream;
- identical final authoritative state;
- identical raw recovery observations.

Therefore the corrected positive primary is attributable to metric alignment,
not post-result task tuning.

Under the preregistered application criteria,
the first persistent telemetry-integrity organism:

- produced zero false authoritative outputs;
- maintained >99.7% connected availability;
- maintained 100% steady availability and accuracy at the eight-cell budget;
- recovered the two preregistered ordinary faults within two frames;
- recovered role shortage immediately;
- preserved partition safety;
- preserved hibernation authority expiry;
- preserved hereditary continuity;
- preserved provenance non-multiplication;
- restarted deterministically.

PLAIN-SPEAK INTERPRETATION

This is the first actual Yggdrasil application pass.

The artificial population had a job:

keep producing the right telemetry integrity byte.

We then made its life difficult.

We cut it from twelve active cells to eight.

We damaged cells.

We created a missing-role problem.

We split the organism in half.

We put voting cells to sleep.

We woke them back up.

We challenged its historical memory.

And we restarted it from a saved state.

It never produced a wrong authoritative answer.

When it had enough healthy evidence,
it kept working.

When the rules said it should not trust the situation,
it did not manufacture authority.

The original failed score is still preserved.

The correction did not make the organism behave better.

It made the scoreboard count the two fault-recovery tests that the experiment said it would count.

So the useful milestone is now justified:

YGGDRASIL HAS MOVED FROM
A COLLECTION OF WORKING MECHANISMS

TO

A PERSISTENT SYNTHETIC ORGANISM
THAT USED THOSE MECHANISMS
TO KEEP A REAL COMPUTATIONAL SERVICE RUNNING UNDER PRESSURE.

This is not production readiness.

It is the first application proof.

NEXT JUSTIFIED STEP

Application Track A already contains the separately preregistered:

A02 — Adaptive Transform Service Organism.

A02 should raise task complexity above the checksum service
while preserving the same constitutional boundaries.

It should test whether the organism can maintain a changing transform objective
rather than a fixed deterministic integrity function.

YGG-A01 accepted application frontier:

POSITIVE via preregistered FIXA metric alignment.

Original frozen R1:

preserved as measurement-semantic defect.

canonical_scientific_execution = false.
stab18_r1_touched = false.
