TITLE: LU-2O — LU-2N EXACT-PARENT REPAIR-TIMING AUDIT
DATE: 2026-09-24
STATUS: PREREGISTERED / DIAGNOSTIC ONLY / NO NEW WORLD
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2N CLOSURE:
096c8dee7ae368f69e322be8e1b8a5ca20feff08

PARENT LU2NF1:
a4657c94a654d2b4f83b6af0c7844b65e6999593

ACCEPTED LU-2N PRIMARY RUN:
36056265256

ACCEPTED LU-2N PRIMARY ARTIFACT:
10832413015

ACCEPTED LU-2N PRIMARY SHA256:
a742491a9282e346d848850000c0f24a3f6ea7fdf4b8c62eefa35e7f31432d77

PURPOSE

Diagnose why exact-parent U_A0 baseline feasibility failed in LU-2N
replicates 5, 8, and 10 before changing any environment, threshold, or
learned authority.

SCIENTIFIC QUESTION

Are the three LU-2N exact-parent repair-integrity failures caused by
finite-horizon truncation of an otherwise valid repair sequence, or by a
deeper repair-capacity defect under contiguous 16-cell damage?

WORLD POLICY

Use exactly the ten accepted LU-2N manifests.

Do not derive new worlds.
Do not replace worlds.
Do not rejection-sample.

PRIMARY SCIENCE STATUS

LU-2O is diagnostic only.

It does not reopen or alter the LU-2N FALSE verdict.

ARM

Replay exact U_A0 only.

No U_A25 execution is needed for the primary diagnosis.

No learned authority is introduced.

DYNAMICS

Exact LU2NF1 / V0.2 parent dynamics.

Exactly 160 epochs.

Do not extend the horizon.

Do not add drain epochs.

Do not change load, lesion, corruption, expiry, anchors, programs, arrival
schedule, task semantics, or random variates.

INSTRUMENTATION

Add observation-only per-request timestamps for every scheduled corrupted
request:

arrival_epoch;
first_at_egress_epoch;
first_verification_detection_epoch;
first_repair_epoch;
first_successful_reverify_epoch;
done_epoch;
terminal_state_at_epoch_160.

Also record:

request age at first detection;
request age at first repair;
request age at successful reverify;
epochs remaining after first detection;
epochs remaining after first repair.

Instrumentation may read state and transitions but may not affect any
decision, queue, RNG call, transition probability, request state, or cell
state.

REPLAY INTEGRITY GATE

Before interpreting timing evidence, each replayed U_A0 world must reproduce
the accepted LU-2N U_A0 aggregate outputs exactly for:

correct_done;
incorrect_done;
expired;
backlog;
operations;
operations_per_correct_completion;
phase summaries;
stream summaries;
repair summary;
event summary;
state_sha256;
trace_sha256;
matching_duplicate_cell;
matching_duplicate_request.

If any world differs, LU-2O is INVALID and no timing interpretation is made.

DIAGNOSTIC CLASSIFICATION

For each LU-2N baseline-failed world:

HORIZON_TRUNCATED_REPAIR if:

- every corruption reaching egress is detected;
- the unrepaired request has first_verification_detection_epoch near the end
  of the 160-epoch horizon;
- terminal state is REPAIR_PENDING or another in-progress repair state;
- no incorrect DONE occurs;
- no expiry occurs.

DEEPER_REPAIR_CAPACITY_DEFECT if:

- an unrepaired request is detected with enough remaining service time but
  still fails to enter/complete repair; or
- the request becomes stranded in a non-repair state; or
- instrumentation reveals persistent local service absence rather than
  simple horizon truncation.

Do not define a new numerical pass threshold from observed data.

Report exact timestamps and remaining epochs.

SECONDARY OBSERVATION

Record the accepted replicate-1 U_A25 anchor-recovery-null result from LU-2N
as a separate unresolved signal.

Do not diagnose it in LU-2O unless exact-parent repair timing is first
classified.

NO POST-RESULT TUNING

Do not change:

160-epoch horizon;
lesion geometry;
lesion size;
lesion duration;
load;
expiry;
corruption;
repair semantics;
qualification bars;
alpha;
weights;
OBS-V1;
or authority.

NEXT STEP RULE

If all three exact-parent failures are horizon-truncated repairs:

design a fresh experiment whose evaluation contract separates terminal
in-flight work from genuine repair failure without changing organism
dynamics.

If any failure is a deeper repair-capacity defect:

diagnose local service/workforce geometry under contiguous damage before
testing learned-U robustness again.

PLAIN-SPEAK QUESTION

Three hand-written-parent worlds failed because one detected bad request was
still not repaired when the test stopped.

LU-2O does not give the organism more time and does not change anything.

It simply puts timestamps on those requests.

If the missing repairs were detected right at the end and are visibly still
in the repair pipeline, we found an evaluation-horizon problem.

If they had plenty of time and still got stranded, we found a real capacity
problem caused by concentrated damage.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
