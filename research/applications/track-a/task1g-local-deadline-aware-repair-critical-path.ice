TITLE: TASK-1G — Local Deadline-Aware Repair Critical-Path Scheduling
DATE: 2026-09-23
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / TASK-1
PARENT: TASK-1F T1FF1-R1 PRIMARY CLOSURE
PARENT CLOSURE: fda86a2fee99fb948524b53b0eb0652011d655f6

QUESTION

Task-1F established robust information gain
from LOCAL_HEDGE across five fresh manifests,
but formal qualification failed because one correctly repaired request
expired before mandatory post-repair verification.

Can a purely local deadline-aware service rule
protect the already-detected repair critical path
without extending request lifetime,
changing correctness,
or changing ordinary task scheduling?

SCIENTIFIC MOTIVATION

Task-1F R2 request 219:

stream:
S.

created:
epoch 109.

corruption:
applied.

corruption detected:
TRUE.

repair:
performed at epoch 140.

repaired output:
correct.

expiry:
epoch 141.

mandatory post-repair verification:
not reached.

Thus the failure is not:

repair computation;

corruption detection;

LOCAL_HEDGE semantics;

wrong-side execution;

or loss of task correctness.

It is a service-ordering failure
on a request with very little remaining lifetime.

EXTERNAL DESIGN PRINCIPLE

Earliest-deadline-first scheduling
prioritizes ready work by the nearest deadline.

Task-1G imports only the narrow principle:

WHEN ALREADY-DETECTED REPAIR WORK
IS LOCALLY READY,

the request with the least remaining lifetime
may receive local proposal priority
for the repair critical path.

Task-1G does not claim EDF optimality.

FROZEN PARENTS

Developmental Substrate V0:
92654adf407310a01e368e2c53934beae749482c.

Task-1E T1EF1:
04872029aeb773b3e98ccb71537c18ff965487e1.

Task-1F T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063.

Task-1F five-manifest binding:
49b12cbb00a75e4949b14866f81bc9e5a8002baa.

Task-1F primary closure:
fda86a2fee99fb948524b53b0eb0652011d655f6.

NO SUBSTRATE CHANGE

Preserve exactly:

LOCAL_HEDGE H formation;

LOCAL_HEDGE H release;

all C/S commitment equations;

B update;

rho = 3/4;

ECHO_PHASE;

D2;

G5_FULL OFF;

refractory semantics;

recruitment law;

fixed 64-cell ring;

R_TASK = 2;

neutral sensing;

request-bound handoff;

task programs;

arrival load;

corruption rate;

distributed lesion;

anchor rotation;

phase lengths;

32-epoch expiry;

verification computation;

repair computation;

mandatory post-repair verification;

one-operation-per-cell-per-epoch;

one-operation-per-request-per-epoch.

PRIMARY ARMS

Exactly two:

LOCAL_HEDGE_PARENT

Exact Task-1F LOCAL_HEDGE parent scheduling.

LOCAL_HEDGE_REPAIR_EDF

Exact LOCAL_HEDGE_PARENT
except the local proposal order
for requests already inside the detected repair critical path.

REPAIR CRITICAL PATH

A request enters the repair critical path only after
a VERIFY operation has detected an incorrect processed output.

Critical-path stages are:

REPAIR_PENDING;

and

AT_EGRESS after a successful repair
while mandatory post-repair verification remains outstanding.

Ordinary uncorrupted AT_EGRESS work
is not part of this priority class.

No RAW, SENSED, PROCESSED, or ROUTING request
receives Task-1G deadline priority.

DEADLINE VALUE

Request expiry remains exactly the frozen parent expiry.

For request r at epoch t:

remaining_lifetime(r,t)
=
expiry_epoch(r) - t.

No expiry extension.

No grace period.

No deadline rewrite.

No tunable urgency threshold.

LOCAL PROPOSAL RULE

For each cell,
construct the exact inherited LOCAL_HEDGE eligible request set.

Partition eligible requests into:

A.
repair-critical requests;

B.
all other requests.

If A is nonempty:

order A first by:

1. smallest remaining_lifetime;
2. oldest request creation epoch;
3. request id;
4. inherited stateless tie key.

Then append B
in the exact inherited parent order.

If A is empty:

proposal order is bit-for-bit parent order.

The request-side deferred-acceptance preference remains unchanged.

Thus Task-1G changes only
which locally eligible request a cell proposes first.

NO GLOBAL INFORMATION

The treatment may read only:

current epoch;

local eligible request state;

request creation / expiry metadata;

whether the request has entered
the already-detected repair critical path.

It may not read:

global backlog;

global throughput;

future arrivals;

phase identity;

future corruption;

future lesion;

majority state;

or any centralized scheduler output.

NO NEW RANDOMNESS

No new RNG namespace.

No random priority.

No probability.

No stochastic grace policy.

The treatment is deterministic.

MECHANISM TELEMETRY

For LOCAL_HEDGE_REPAIR_EDF report:

repair_critical_opportunities;

repair_critical_matches;

repair_critical_preemptions;

mean remaining lifetime
at REPAIR_PENDING service;

mean remaining lifetime
at post-repair VERIFY service;

minimum remaining lifetime
at each critical stage;

number of repaired requests
that expire before re-verification;

number of correctly repaired requests
successfully re-verified;

ordinary task completion / backlog metrics;

all Task-1F LOCAL_HEDGE mechanism telemetry.

CROSS-MANIFEST DESIGN

Use exactly five fresh primary manifests.

Do not reuse Task-1F result manifests
as Task-1G primaries.

After T1GF1 exists,
derive replicates k=1..5 from:

T1GF1;

literal TASK1G-REPLICATE;

k.

Each manifest independently derives:

four balanced nonconstant nonaffine truth tables;

task seed;

320 arrivals;

corruption schedule;

lesion offset;

anchors.

Bind all five manifests
before any primary arm execution.

Two complete five-replicate sweeps
must be byte-identical
before scientific interpretation.

MECHANICAL GATE

Before T1GF1 prove:

1. LOCAL_HEDGE_PARENT exact behavioral parity
   with frozen Task-1F LOCAL_HEDGE
   on the mechanical manifest.

2. With no repair-critical request locally eligible,
   LOCAL_HEDGE_REPAIR_EDF proposal order
   equals parent order exactly.

3. Only already-detected repair-critical work
   may move ahead of parent order.

4. Expiry remains 32 epochs.

5. Repair computation unchanged.

6. Verification computation unchanged.

7. Mandatory post-repair verification unchanged.

8. No request may be marked DONE by repair alone.

9. No new RNG namespace.

10. All LOCAL_HEDGE dynamics exact parent parity.

11. One-operation cell/request invariants pass.

12. Two complete mechanical sweeps
    are byte-identical.

PRIMARY INFORMATION GAIN

For each replicate k define:

repair_success_gain_k
=
LOCAL_HEDGE_REPAIR_EDF
correctly-completed-after-detected-repair fraction
-
LOCAL_HEDGE_PARENT paired value.

Define:

expiry_after_correct_repair_k
=
count of correctly repaired requests
that expire before mandatory re-verification.

TASK1G_REPAIR_SERVICE_INFORMATION_GAIN = TRUE iff all are true:

1. mechanism active
   in at least 3 of 5 replicates;

2. no LOCAL_HEDGE_REPAIR_EDF replicate
   has lower repair-detection fraction
   than its parent;

3. no LOCAL_HEDGE_REPAIR_EDF replicate
   has lower correctly-completed-after-detected-repair fraction
   than its parent;

4. total expiry-after-correct-repair count
   across five treatment replicates
   is strictly lower than paired parent total;

5. Phase-0 completion
   >=95% of paired parent
   in every replicate;

6. Phase-4 final-window completion
   is no worse than parent by more than 5 percentage points
   in any replicate;

7. incorrect DONE = 0
   in all five treatment replicates;

8. operations per correct completion
   <=125% of paired parent
   in every replicate;

9. all integrity probes pass.

PRIMARY QUALIFICATION

TASK1G_QUALIFIED = TRUE iff
TASK1G_REPAIR_SERVICE_INFORMATION_GAIN = TRUE
and all are true:

1. repair detection >=95%
   in every applicable treatment replicate;

2. repair success >=90%
   in every applicable treatment replicate;

3. zero correctly repaired requests
   expire before mandatory re-verification
   across all five treatment replicates;

4. median LOCAL_HEDGE_REPAIR_EDF
   Phase-4 final-window completion >=85%;

5. at least 4 of 5 treatment replicates
   achieve Phase-4 final-window completion >=85%;

6. anchor-rotation recovery <=8 epochs
   in at least 4 of 5 replicates;

7. demand-reversal recovery <=8 epochs
   in all five replicates;

8. lesion criterion passes
   in all five replicates.

FAILURE ATTRIBUTION

If repair EDF removes
expiry-after-correct-repair events
without throughput regression:

the Task-1F formal miss
was a separable repair-service scheduling seam.

If repair EDF is active
but the same expiry failure remains:

local service ordering alone
cannot guarantee the two-step repair / reverify path
within the unchanged lifetime.

Do not extend expiry inside Task-1G.

If repair EDF improves repair success
but materially harms ordinary throughput:

repair urgency competes too strongly
with general service capacity.

Do not add a tuned urgency weight inside Task-1G.

If Task-1G qualifies:

Task-1F LOCAL_HEDGE remains
a candidate V0.1 substrate change,
now with its repair lifecycle independently closed.

A separate frozen confirmation
is still required before modifying V0 itself.

NO POST-RESULT TUNING

Do not change:

deadline definition;

critical-path stages;

priority threshold;

expiry;

repair;

verification;

number of manifests;

manifest selection;

task load;

anchor shift;

scheduler outside the repair critical path;

D family;

G5;

LOCAL_HEDGE equations;

or qualification after results.

PLAIN-SPEAK QUESTION

One job in Task-1F was fixed correctly
but died while waiting to be checked.

Task-1G does not give it more lifetime.

It does not weaken the final check.

It asks only:

if a nearby cell can work on
an already-detected broken job
that is about to expire,

should that job go first?

That is the whole experiment.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
