TITLE: TASK-1E POST-CLOSURE RELOCATED-S-STATE DIAGNOSIS
DATE: 2026-09-22
STATUS: OBSERVATION-ONLY / EXACT FROZEN-T1EF1 REPLAY
TRACK: DG-1 / TASK-1E
PARENT CLOSURE: 532862b59937e53b37e39c5c0f25fbf259ea704e

PURPOSE

Localize the residual Phase-4 deficit
after request-bound handoff removed
the dominant in-flight migration artifact.

SOURCE / MANIFEST

T1EF1:
04872029aeb773b3e98ccb71537c18ff965487e1

source SHA256:
c1578a0d21d1125a26d81664adc0c3a78a3a23e9a4a2a4865d526e41af7d2207

primary manifest SHA256:
b759aca22f379bffa887ea820cb476a9f8a9da15bf58c78cb3f7b52455edccda

The replay uses the exact frozen REQUEST_BOUND primary.

Instrumentation is read-only.

No state transition,
request transition,
matching rule,
randomness,
anchor,
program,
arrival,
corruption,
lesion,
or qualification
is changed.

REPLAY PARITY

Full published REQUEST_BOUND result parity:
TRUE.

Reproduced:

correct DONE:
275.

Phase-4 final-16:
78.125%.

final-16 total backlog area:
638.

anchor-rotation recovery:
0 epochs.

CENTRAL FINDING

The remaining relocation deficit is almost entirely
an S-stream local-state availability failure.

It is not primarily finite-horizon censoring
and it is not lack of local S demand.

PHASE-4 NEW WORK

New Phase-4 arrivals:
64.

New Phase-4 correct DONE by horizon:
20.

Final state by stream:

C:
DONE = 20;
AT_EGRESS = 2;
PROCESSED = 2;
RAW = 3;
ROUTING = 5.

S:
DONE = 0;
PROCESSED = 1;
RAW = 22;
ROUTING = 3;
SENSED = 6.

Therefore every new Phase-4 completion
belongs to the C stream.

No new Phase-4 S request completes.

CREATION-COHORT RESULT

Epochs 128-135:
8 / 16 complete.

Epochs 136-143:
8 / 16 complete.

Epochs 144-151:
4 / 16 complete.

Epochs 152-159:
0 / 16 complete.

The theoretical minimum noncorrupt pipeline is:

SENSE;
PROCESS;
six ROUTE;
VERIFY.

Nine operations total.

Minimum possible done_epoch - created:
8.

Late-horizon censoring therefore exists
for the latest arrivals.

However it does not explain
the stream asymmetry:

new S requests fail even
when created early enough to mature.

FINAL-16 ELIGIBILITY — C STREAM

C RAW:

mean eligible cells:
5.0.

zero-eligible fraction:
0%.

C SENSED:

mean eligible:
5.0.

zero:
0%.

C PROCESSED:

mean eligible:
5.0.

zero:
0%.

C ROUTING:

mean eligible:
5.0.

zero:
0%.

C AT_EGRESS:

mean eligible:
4.0.

zero:
0%.

FINAL-16 ELIGIBILITY — S STREAM

S RAW:

observations:
232.

mean eligible cells:
0.638.

zero-eligible fraction:
36.21%.

S SENSED:

observations:
146.

mean eligible:
0.452.

zero-eligible fraction:
54.79%.

S PROCESSED:

observations:
3.

mean eligible:
1.0.

zero:
0%.

S ROUTING:

observations:
11.

mean eligible:
0.091.

zero-eligible fraction:
90.91%.

Thus the S pipeline is not merely slower.

Large portions of it have no locally eligible
S-committed executor at all.

FINAL-16 RELOCATED ANCHOR STATE

Five-cell R_TASK neighborhood
around relocated C ingress:

mean C:
5.0.

Five-cell neighborhood
around relocated S ingress:

mean H:
4.375.

mean S:
0.5.

mean U:
0.125.

mean C:
0.

Around relocated S egress:

mean S:
4.0.

mean H:
0.875.

mean U:
0.125.

Therefore the severe deficit is concentrated
at the relocated S ingress / early transport region,
not at S egress verification.

LOCAL DEMAND SIGNAL

This is not caused by missing S evidence.

Final-16 at relocated S ingress:

L_S3:
1.0.

L_C3:
0.0.

L_S12:
0.345.

L_C12:
0.0025.

Nearly all local S evidence there
comes from new Phase-4 work.

Legacy contribution to L_S12:
approximately 0.01.

Thus the new location is reporting
strong, correctly directed local S demand.

GLOBAL POOL STATE

Despite local one-sided S evidence,
the inherited population-wide support pools remain high.

Final-16 mean normalized pool values
used by the V0 step:

P_C:
approximately 0.9360.

P_S:
approximately 0.9876.

This creates an important interaction
with the inherited H-state semantics.

H RELEASE

The inherited H release law uses:

sup_C =
W_POOL * P_C
+
W_LOCAL * local_C;

sup_S =
W_POOL * P_S
+
W_LOCAL * local_S;

then suppresses release by:

1 - min(sup_C, sup_S).

Because both global pools remain high,
a locally one-sided S region
still appears globally supported
on both sides.

Final-16 relocated S-ingress neighborhood:

mean H cells before update:
4.4375 of 5.

mean exact H-release lambda:
0.03453.

mean H-release probability:
approximately 3.37% per H-cell / epoch.

Observed final-16 transitions
inside the five-cell S-ingress neighborhood:

H -> U:
2.

U -> H:
1.

U -> S:
1.

The neighborhood therefore remains H-dominated
despite persistent one-sided local S demand.

EARLY PHASE-4 CONTEXT

During epochs 128-143:

P_C:
1.0.

P_S:
1.0.

Relocated S local evidence remains strongly S-sided:

L_S3:
0.9375.

L_C3:
0.0.

Yet the new S-ingress neighborhood contains on average:

C:
2.4375;

FC:
0.9375;

H:
1.375;

U:
0.25;

S:
0.

It then transitions toward H rather than rapidly becoming S.

OLD S LOCATION

The old S-ingress five-cell neighborhood remains:

5.0 S cells on average

through both early and final Phase 4.

Thus request-bound handoff correctly preserves old service long enough
to drain legacy work,

but the frozen substrate does not rapidly establish
a second S-capable service front at the new location.

CAUSAL INTERPRETATION

Task-1E has removed the handoff artifact.

The remaining failure is now a substrate-level
LOCAL SPECIALIZATION / HEDGE interaction.

The organism receives the correct local message:

"this new region has S work."

But the H-state decision remains heavily influenced
by population-wide C and S support.

When both global task streams are busy,
that global coexistence is interpreted
as local ambiguity.

Cells near a strongly one-sided local S demand front
therefore remain H
instead of resolving into S.

This is the first Task-1 result
that directly implicates a V0 state-transition semantic
rather than task admission, scheduling, or flow handoff.

The likely seam is specifically:

HEDGE FORMATION / RELEASE
SHOULD REPRESENT LOCAL AMBIGUITY,

not merely global coexistence of both task streams.

This is a causal hypothesis,
not yet a validated mechanism.

NEXT JUSTIFIED STEP

Preregister a narrow differential
that changes only the information used
to form / release H.

Do not change:

C/S commitment support law;

B update;

ECHO_PHASE;

D2;

G5;

R_TASK;

request-bound handoff;

scheduler;

topology;

task programs;

arrival load;

phase lengths;

anchor shift;

expiry;

verification;

repair.

The treatment should test whether H ambiguity
is computed from local C/S evidence
rather than the globally mixed support pools.

Because the present failure is spatially asymmetric
on one fresh primary,
the causal test should use multiple fresh manifests
before any mechanism is promoted.

PLAIN-SPEAK INTERPRETATION

The jobs are telling the cells
exactly where the new S workplace is.

That signal is strong.

But the cells near that workplace
mostly stay undecided.

Why?

Because the organism still has lots of C work
somewhere else.

The old hedge rule sees:

"the organism has strong C support
and strong S support"

and treats that as uncertainty
even in a neighborhood
where the local evidence is almost purely S.

So a cell beside the new S entrance
can remain on the fence
because C work exists far away.

That is probably the wrong meaning of uncertainty
for spatial task organization.

The next experiment should test that one idea
across several fresh worlds
without changing anything else.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
