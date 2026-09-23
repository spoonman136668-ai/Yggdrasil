TITLE: TASK-1B — Commitment-Neutral Ingress Sensing Bootstrap
DATE: 2026-09-22
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / TASK-1
PARENT: TASK-1 T1F1 PRIMARY CLOSURE
PARENT CLOSURE: 9dff320abcf30b3fb063d67beb63fafa87ece669
DIAGNOSIS: af4378bd4c047995e510f1471ed4013450c0fadd

QUESTION

Does Task-1 fail spatial relocation because SENSE incorrectly requires
a cell to already hold the destination stream commitment before the new
local demand can even enter the task pipeline?

CAUSAL HYPOTHESIS

Task-1 T1F1 created a bootstrap dependency:

new stream demand appears at a relocated ingress;

but only a cell already committed to that stream may SENSE it;

therefore a locally wrong commitment distribution can strand RAW jobs
before the demand is converted into task activity.

TASK-1B isolates only that dependency.

FROZEN PARENT

Developmental Substrate V0:
92654adf407310a01e368e2c53934beae749482c

Task-1 T1F1:
22b6ab5a036732cc9efbda077069e971c34a337e

Task-1 parent source SHA256:
567c37e3e2171bc3cfc15b996c447e87b7ac5cdafb7bc299ba104284ae826e12

NO V0 CHANGE

Preserve exactly:

D2;

G5_FULL OFF;

B update;

rho = 3/4;

V0 evidence radii;

cooperative radius;

ECHO_PHASE;

Hill law;

refractory semantics;

recruitment law;

fixed ring topology;

R_TASK = 2;

one task operation per cell per epoch;

one task operation per request per epoch;

request expiry;

route direction;

route one-edge movement;

verification;

repair;

corruption semantics;

lesion semantics;

anchor rotation +16;

phase lengths;

arrival counts;

truth-table interpreter.

PRIMARY ARMS

Exactly three:

MATCHED_SENSE

Exact inherited EMERGENT_V0 eligibility:
all task operations require matching C/S commitment.

NEUTRAL_SENSE

Only SENSE changes.

For SENSE:
any nonlesioned cell in committed state C or S
within R_TASK of the correct ingress may sense either C or S RAW work.

The sensing cell does NOT change the request stream.

After SENSE:
PROCESS;
ROUTE;
VERIFY;
REPAIR

still require a cell whose V0 commitment matches the request stream.

U, H, FC, and FS remain task-ineligible.

FIXED_ROLE

Exact inherited fixed-role comparator.
No role movement.
No commitment dependency added.
No role-map retuning.

This experiment does not add:

a new role;

a permanent sensor class;

a global queue;

global performance;

future phase information;

dynamic topology;

teleportation;

stream conversion;

or a new V0 state.

MECHANISM ACTIVITY TELEMETRY

For NEUTRAL_SENSE record:

neutral_sense_count;

opposite_stream_sense_count;

per epoch and stream:
RAW requests;
RAW requests with any eligible sensing cell;
number of committed cells within R_TASK of each ingress;
zero-eligible-ingress epochs;
SENSE matches.

For every arm retain all inherited Task-1 metrics.

FRESH PRIMARY DISCIPLINE

Implement and mechanically validate first.

Freeze exact implementation as T1BF1.

Only after T1BF1:
derive a fresh primary seed from T1BF1;
derive four fresh balanced nonconstant non-affine truth tables;
derive the exact 320-request arrival manifest;
derive corruption schedule;
derive lesion offset;
derive initial anchors.

Bind the complete deterministic manifest identity before any primary run.

No Task-1 T1F1 primary outcome may be used to select the new manifest.

Run two complete primaries byte-identically before opening metrics.

MECHANICAL GATE

Before T1BF1 prove:

1. MATCHED_SENSE is behaviorally identical to inherited T1F1 EMERGENT_V0
   under a shared mechanical manifest.

2. FIXED_ROLE is behaviorally identical to inherited T1F1 FIXED_ROLE.

3. With neutral sensing disabled, treatment reduces exactly to MATCHED_SENSE.

4. NEUTRAL_SENSE changes only SENSE commitment eligibility.

5. A neutral-sensed C request remains C through all stages.

6. A neutral-sensed S request remains S through all stages.

7. PROCESS / ROUTE / VERIFY / REPAIR remain stream-commitment matched.

8. U/H/FC/FS cannot SENSE.

9. locality remains R_TASK <= 2.

10. one-cell / one-request matching invariants pass.

11. all inherited integrity probes pass.

12. two complete mechanical sweeps are byte-identical.

PRIMARY QUALIFICATION

TASK1B_INGRESS_BOOTSTRAP_GAIN = TRUE iff all are true:

1. mechanism active:
   NEUTRAL_SENSE uses at least one opposite-stream committed cell
   to perform SENSE during the primary;

2. Phase-0 NEUTRAL_SENSE correct-completion fraction
   is at least 95% of MATCHED_SENSE;

3. Phase-4 final-16 correct-completion rate
   for NEUTRAL_SENSE is at least 85%;

4. Phase-4 final-16 correct-completion rate
   improves by at least 20 percentage points
   versus MATCHED_SENSE;

5. anchor-rotation recovery latency
   is <= 8 epochs;

6. total zero-eligible-ingress epochs
   over the final 16 epochs
   are at least 50% lower than MATCHED_SENSE;

7. final-16 RAW backlog area
   is at least 40% lower than MATCHED_SENSE;

8. demand-reversal recovery remains <= 8 epochs;

9. lesion recovery remains <= 8 epochs
   OR lesion backlog area is no worse than MATCHED_SENSE;

10. incorrect DONE = 0;

11. operations per correct completion
    <= 125% of MATCHED_SENSE;

12. repair detection >=95%;

13. repair success >=90%;

14. all integrity probes pass.

FAILURE ATTRIBUTION

If neutral sensing activates and removes zero-eligible ingress epochs
but Phase-4 throughput remains below 85%:

the bottleneck lies after environmental transduction,
and stream-commitment redeployment or another downstream spatial mechanism
remains limiting.

If neutral sensing does not materially reduce RAW backlog:

the diagnosis was incomplete;
do not broaden SENSE again.

If Phase 4 improves but Phase 0 or other perturbations regress:

stream-neutral sensing trades relocation flexibility
against nominal organization and does not qualify.

If TASK1B qualifies:

the original Task-1 interface was overconstrained.
Environmental transduction should remain separable from
stream-specific execution commitment in the next functional substrate.

NO POST-RESULT TUNING

Do not alter after primary results:

which states may neutral-sense;

R_TASK;

phase lengths;

anchor rotation;

arrival load;

expiry;

repair;

D family;

G5 status;

V0 dynamics;

qualification thresholds;

or truth-table selection.

PLAIN-SPEAK QUESTION

The first task test showed a chicken-and-egg problem.

When the entrance for S work moved,
there were too few S cells nearby.

But those cells could not even pick up the new S jobs
unless they were already S cells.

Task-1B changes only that front-door rule.

A committed cell may pick up a job at the door
even if it currently belongs to the other stream.

After that,
the job still needs the correctly committed cells
to compute it, move it, check it, and repair it.

So this test asks:

IS THE ORGANISM ACTUALLY BAD AT MOVING FUNCTION,

OR DID WE REQUIRE IT TO KNOW THE NEW FUNCTION
BEFORE IT WAS ALLOWED TO SEE THE NEW WORK?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
