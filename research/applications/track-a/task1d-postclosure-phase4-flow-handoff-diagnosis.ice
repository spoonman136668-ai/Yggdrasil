TITLE: TASK-1D POST-CLOSURE PHASE-4 FLOW-HANDOFF DIAGNOSIS
DATE: 2026-09-22
STATUS: OBSERVATION-ONLY / EXACT FROZEN-T1DF1 REPLAY
TRACK: DG-1 / TASK-1D
PARENT CLOSURE: 08179f03b4e20ab1c8f66f32f69b68b68706f83d

PURPOSE

Localize the downstream spatial service deficit
that remained after local admission backpressure failed.

This diagnostic changes no Task-1D dynamics.

SOURCE / MANIFEST

T1DF1:
4f57b9adfdaa8041757ca02e15dcf70a1429f9ad

T1DF1 source bytes:
15217

T1DF1 source SHA256:
eca65242ea0b83a3448dcc28bf360141e819286000dfdb747c5c34969d18fd57

Primary manifest SHA256:
80da942fecf911f3e4e11a16347e7241a61e11bc8834a2eb7c4fefde84121566

The replay resolves through the exact T1F1 parent loader:
source bytes 37394;
SHA256 567c37e3e2171bc3cfc15b996c447e87b7ac5cdafb7bc299ba104284ae826e12.

REPLAY PARITY

The observation-only replay reproduces the frozen PRESSURE_ADMISSION
public result exactly.

Full public-result parity:
TRUE.

Key reproduced values:

correct DONE:
238.

Phase-4 final-16 correct completion:
28.125%.

final-16 RAW backlog area:
343.

final-16 non-RAW backlog area:
553.

final-16 total backlog area:
896.

pressure SENSE preemptions:
206.

Therefore the diagnostic telemetry is attached to the exact
authoritative Task-1D trajectory.

CENTRAL FINDING

The dominant Phase-4 downstream deficit is not ordinary local
service unavailability.

It is FLOW-HANDOFF DEBT created by the anchor-rotation semantics.

At epoch 128,
the environment rotates all ingress and egress anchors by +16.

The frozen Task-1 semantics then use the CURRENT anchors
for every unfinished request,
including requests created before the rotation.

This has two consequences.

1. OLD RAW REQUESTS BECOME ORPHANED.

At epoch 128,
8 legacy RAW requests are still waiting:

C:
2.

S:
6.

They remain physically located at the old ingress.

After rotation,
SENSE requires the request position to equal the CURRENT ingress.

Therefore these old RAW requests have zero eligible sensing cells.

Across Phase 4,
legacy RAW request-epoch observations:

C:
61.

S:
171.

Zero-eligible observations:

C:
61 / 61.

S:
171 / 171.

These requests cannot re-enter the pipeline.
They age to expiry while continuing to exist as local demand state.

2. IN-FLIGHT ROUTING REQUESTS ARE RETARGETED.

At epoch 128,
17 legacy requests are already PROCESSED or ROUTING:

C:
8.

S:
9.

Their destination is not frozen per request.

The next ROUTE operation tests arrival against the NEW egress.

Thus a packet already near its old egress is suddenly required
to reach a different spatial endpoint.

The effect is directionally asymmetric because route direction remains fixed.

TASK-1D primary anchors:

Phase 0-3:

C_IN = 4.
C_OUT = 10.
S_IN = 44.
S_OUT = 38.

Phase 4:

C_IN = 20.
C_OUT = 26.
S_IN = 60.
S_OUT = 54.

For C traffic,
which routes clockwise,
the moved egress creates approximately
16 additional hops for old near-egress work.

For S traffic,
which routes counterclockwise,
moving S_OUT from 38 to 54 places the new egress
48 counterclockwise hops beyond the old one.

At epoch 128,
legacy S in-flight requests require:

49;
50;
51;
52;
54;
53;
55;
51;
56

remaining route hops
for the observed legacy S PROCESSED / ROUTING cohort.

These requests have only a 32-epoch total lifetime.

They are therefore structurally unable
to finish the newly rebound route before expiry
unless already extraordinarily young and exceptionally serviced.

PHASE-4 ROUTE DEBT

Across Phase 4,
ROUTE matches are:

legacy C:
175.

legacy S:
194.

new Phase-4 C:
83.

new Phase-4 S:
66.

Total legacy ROUTE operations:
369.

Total new-request ROUTE operations:
149.

Legacy share of all Phase-4 ROUTE service:
71.24%.

Thus most Phase-4 routing capacity is spent
on work that predates the spatial relocation.

LEGACY REMAINING-DISTANCE TELEMETRY

Legacy C PROCESSED / ROUTING request-epoch observations:

n:
224.

mean remaining hops to current egress:
9.14.

median:
8.

p90:
18.

max:
23.

Legacy S:

n:
236.

mean:
45.59.

median:
45.

p90:
52.

max:
56.

New Phase-4 C requests:

mean remaining:
4.13.

median:
4.

p90:
7.

max:
8.

New Phase-4 S requests:

mean remaining:
4.08.

median:
4.

p90:
7.

max:
8.

The route explosion is therefore specific
to legacy work crossing the anchor-change boundary.

EPOCH-128 LEGACY COHORT OUTCOME

Unfinished legacy requests at the moment of relocation:
33.

Final outcomes:

C DONE:
1.

C EXPIRED:
11.

S DONE:
2.

S EXPIRED:
19.

Total DONE:
3 / 33.

Total EXPIRED:
30 / 33.

Therefore 90.91% of the outstanding legacy cohort expires.

Yet this cohort consumes the majority of Phase-4 route service before doing so.

NEW PHASE-4 WORK

New Phase-4 requests are created directly against the new anchors.

Their route distances remain the intended short pipeline geometry.

However they compete for local service
with the large legacy route debt
and with demand state left behind at the old locations.

This explains why:

neutral sensing helps only partially;

unconditional ingress priority shifts congestion downstream;

local admission backpressure moderates the queue split
but cannot improve total throughput.

Those mechanisms operate after the environment has already created
a pathological in-flight migration problem.

CAUSAL RECLASSIFICATION

The Task-1 / 1B / 1C / 1D failures should not be interpreted as evidence
that the V0 cells cannot spatially redeploy service.

The current Task-1 anchor-shift environment conflates:

SPATIAL REDEPLOYMENT OF NEW DEMAND

with

RETROACTIVE MIGRATION OF ALREADY-ADMITTED WORK.

The second behavior was never the intended developmental claim.

The task interface silently changes the destination semantics
of outstanding work when the anchors move.

That creates doomed queue debt
which dominates the exact failure window.

NEXT JUSTIFIED CAUSAL QUESTION

Test a request-bound handoff contract.

Each request should use the ingress / egress anchor generation
that existed when the request was created.

When the environment moves:

new requests use the new anchors;

already-created requests continue to drain through their original
ingress / egress pair;

no request teleports;

no request is dropped;

no route direction changes;

no topology changes;

no V0 state rule changes.

This is analogous to preserving in-flight flow/session continuity
during endpoint migration rather than rebinding every outstanding unit
to the new destination.

The experiment must isolate this task-interface seam.

Do not retune:

V0;

D2;

G5;

R_TASK;

arrival load;

expiry;

phase lengths;

anchor displacement;

truth tables;

corruption;

lesion;

or downstream correctness.

PLAIN-SPEAK INTERPRETATION

We found the traffic jam.

When the work locations moved,
the experiment also told old jobs
that their destination had moved.

That was especially brutal for S jobs.

A job that was almost finished
could suddenly be nearly a full lap away
from its new finish line.

At the same time,
jobs still waiting at the old entrance
were no longer allowed to be picked up at all.

Those old jobs then spent most of Phase 4
burning routing capacity until they expired.

So the organism was not merely being asked:

"Can you reorganize around a new workplace?"

It was also being asked:

"Can you rescue a pile of old jobs
whose doors and destinations changed underneath them?"

That is a different problem.

The next test should let old work finish where it started
while new work begins at the new location.

Then we can measure spatial redeployment cleanly.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
