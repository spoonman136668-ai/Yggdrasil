TITLE: LU-0C LU0CF1 PRIMARY CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / NO_POOL SIMPLIFICATION VIABLE / LOCAL POOL NOT PRESERVED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
408368910033ac2ad0fe4f65ded5a796030e296d

MECHANICAL GATE:
c1147ecb79de2c7f6bfee95f34d32d3301880b7d

LU0CF1:
872509a6da0935e791f458eca42d0d8741c9e200

FIVE-MANIFEST BINDING:
d255ddb976f359e74a3f9e5572c9c9b8fe8b4854

PARENT V0.1:
4d3887fba0478bc1ef3bc4bea44f8e08582f5803

LU-0 CLOSURE:
074513c64a64318053fcbfcabdc9207202849063

LU-0B CLOSURE:
c974b4def2973e72feec8b6be078c9255a0070d0

FROZEN SOURCE

bytes:
28556

SHA256:
57476bf302ad3117a496b5ffabb33f69d3a99d1d89eb683be2d6073c662d45ae

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

PRIMARY DUPLICATE GATE

runs:
2.

worlds per sweep:
5.

arms per world:
3.

raw bytes per sweep:
218803.

raw SHA256:
dcd4fffb1da170ddf96dd03b02b7d954939cb6b73f9a1065b052aaad37a3b46b.

byte identical:
TRUE.

external open bytes:
224197.

external open SHA256:
1bf66130e1097e58181cdefcd5b6b94d290d7e45b601ed238e3d46dd00876583.

manifest file bytes:
112193.

manifest SHA256:
23a8aed3ea7b9af564e158c9ebba1da4cd09aa384392fede4be516bb51cd2dee.

All five manifest identities match the pre-primary binding.

All runtime integrity probes:
PASS.

SCIENTIFIC STATUS

LU0C_LOCAL_POOL_PRESERVES_V01:
FALSE.

LU0C_NO_POOL_SIMPLIFICATION_VIABLE:
TRUE.

LU0C_LOCAL_POOL_ADDS_VALUE_OVER_NO_POOL:
FALSE.

GLOBAL QUESTION

LU-0 and LU-0B showed that the inherited recruitment pool
is a real organism-wide dependency in the V0.1 equations
and is materially present during ordinary Task-1 trajectories.

LU-0C asked whether that dependency must be replaced
with a local recurrent pool,
or whether the pool term can simply be removed.

The result is unambiguous under the frozen gates:

NO_POOL preserves the V0.1 task envelope.

The first density-preserving local recurrent pool does not satisfy
its own preservation gate.

The local recurrent pool also does not add value over NO_POOL.

NO_POOL PRESERVATION

All preregistered NO_POOL preservation checks:
PASS.

Phase-0 >=95% of GLOBAL_POOL_PARENT:
5 / 5.

Observed:
100% in every paired arm.

Phase-4 final-window completion >=85%:
5 / 5.

Median NO_POOL Phase-4 completion:
115.625%.

The frozen completion metric may exceed 100%
when the final window drains backlog created before that window.

NO_POOL Phase-4 within 10 percentage points
of GLOBAL_POOL_PARENT:
5 / 5.

Median paired Phase-4 delta
NO_POOL minus GLOBAL:
+3.125 percentage points.

Correct-completion area Phases 1-4
>=90% of GLOBAL:
5 / 5.

Median paired area ratio:
100.404858%.

Median area ratio >=95%:
PASS.

Final-16 backlog <=125% of GLOBAL:
5 / 5.

Median backlog ratio:
98.715596%.

Anchor-rotation recovery <=8 epochs:
5 / 5.

NO_POOL anchor recovery:
R1 0;
R2 0;
R3 2;
R4 1;
R5 0.

Demand-reversal recovery <=8 epochs:
5 / 5.

NO_POOL demand-reversal recovery:
R1 6;
R2 1;
R3 1;
R4 0;
R5 6.

Lesion criterion:
5 / 5.

NO_POOL lesion recovery:
R1 0;
R2 0;
R3 0;
R4 0;
R5 0.

Incorrect DONE:
0 in all five worlds.

Operation cost <=125% of GLOBAL:
5 / 5.

Observed NO_POOL operations per correct completion:
R1 9.979452;
R2 9.924138;
R3 9.993080;
R4 10.263345;
R5 10.003472.

GLOBAL_POOL_PARENT:
R1 10.010417;
R2 9.979239;
R3 9.955326;
R4 10.266904;
R5 9.986111.

Thus NO_POOL does not preserve the benchmark
by purchasing success with excess work.

LOCAL_POOL_R12 PRESERVATION

The local mechanism was active in all five worlds.

Its recurrent state was spatially non-uniform in all 160 epochs
of every world.

Its 25-cell local window and 62.5 normalization
were mechanically exact.

It passed every preservation check except one:

median paired Phase-4 delta
LOCAL_POOL_R12 minus GLOBAL_POOL_PARENT
must be at least -5 percentage points.

Observed median:
-6.25 percentage points.

Therefore:

LU0C_LOCAL_POOL_PRESERVES_V01 = FALSE.

Do not relax the -5 point gate.

Other LOCAL_POOL_R12 medians:

Phase-4 completion:
118.75%.

Phases-1-4 area ratio:
98.780488%.

final-16 backlog ratio:
99.816514%.

The mechanism is functional and close,
but under the frozen rule it does not preserve V0.1 sufficiently.

LOCAL POOL TELEMETRY

R1
mean pc_i:
0.650602.

mean ps_i:
0.664783.

mean spatial std pc_i:
0.379472.

mean spatial std ps_i:
0.370786.

pc_i saturation:
46.6504%.

ps_i saturation:
47.9199%.

nonzero spatial-variance epochs:
160 / 160.

U recruitment evaluations:
396.

R2
mean pc_i:
0.667889.

mean ps_i:
0.649928.

mean spatial std pc_i:
0.370202.

mean spatial std ps_i:
0.381273.

pc_i saturation:
47.8711%.

ps_i saturation:
46.9238%.

nonzero spatial-variance epochs:
160 / 160.

U recruitment evaluations:
302.

R3
mean pc_i:
0.655070.

mean ps_i:
0.658829.

mean spatial std pc_i:
0.384094.

mean spatial std ps_i:
0.378168.

pc_i saturation:
47.4805%.

ps_i saturation:
47.7051%.

nonzero spatial-variance epochs:
160 / 160.

U recruitment evaluations:
352.

R4
mean pc_i:
0.633812.

mean ps_i:
0.673688.

mean spatial std pc_i:
0.390701.

mean spatial std ps_i:
0.371627.

pc_i saturation:
45.6348%.

ps_i saturation:
48.5254%.

nonzero spatial-variance epochs:
160 / 160.

U recruitment evaluations:
366.

R5
mean pc_i:
0.625758.

mean ps_i:
0.687768.

mean spatial std pc_i:
0.397129.

mean spatial std ps_i:
0.361205.

pc_i saturation:
45.5273%.

ps_i saturation:
49.4043%.

nonzero spatial-variance epochs:
160 / 160.

U recruitment evaluations:
345.

The local recurrent state is therefore not inert.

Its negative result is not caused by zero activity.

LOCAL POOL VALUE OVER NO_POOL

All four preregistered value conditions:
FAIL.

LOCAL_POOL_R12 Phase-4 >= NO_POOL
in at least 4 / 5:
FAIL.

Observed:
2 / 5.

Median paired Phase-4 delta
LOCAL minus NO_POOL:
-3.125 percentage points.

Required:
+5 points.

FAIL.

LOCAL_POOL_R12 final-16 backlog lower than NO_POOL
in at least 4 / 5:
FAIL.

Observed:
1 / 5.

Median paired backlog reduction versus NO_POOL:
-1.209677%.

Required:
+10%.

FAIL.

Therefore:

LU0C_LOCAL_POOL_ADDS_VALUE_OVER_NO_POOL = FALSE.

PER-WORLD PHASE-4 RESULT

R1
GLOBAL:
131.25%.

LOCAL_POOL_R12:
125.0%.

NO_POOL:
128.125%.

LOCAL minus GLOBAL:
-6.25 points.

LOCAL minus NO_POOL:
-3.125 points.

final-16 backlog:
GLOBAL 538;
LOCAL 491;
NO_POOL 484.

R2
GLOBAL:
125.0%.

LOCAL_POOL_R12:
118.75%.

NO_POOL:
128.125%.

LOCAL minus GLOBAL:
-6.25 points.

LOCAL minus NO_POOL:
-9.375 points.

final-16 backlog:
GLOBAL 503;
LOCAL 502;
NO_POOL 496.

R3
GLOBAL:
125.0%.

LOCAL_POOL_R12:
125.0%.

NO_POOL:
115.625%.

LOCAL minus GLOBAL:
0 points.

LOCAL minus NO_POOL:
+9.375 points.

final-16 backlog:
GLOBAL 517;
LOCAL 524;
NO_POOL 533.

R4
GLOBAL:
103.125%.

LOCAL_POOL_R12:
96.875%.

NO_POOL:
106.25%.

LOCAL minus GLOBAL:
-6.25 points.

LOCAL minus NO_POOL:
-9.375 points.

final-16 backlog:
GLOBAL 568;
LOCAL 581;
NO_POOL 570.

R5
GLOBAL:
112.5%.

LOCAL_POOL_R12:
118.75%.

NO_POOL:
115.625%.

LOCAL minus GLOBAL:
+6.25 points.

LOCAL minus NO_POOL:
+3.125 points.

final-16 backlog:
GLOBAL 545;
LOCAL 544;
NO_POOL 538.

CAUSAL INTERPRETATION

The V0.1 global recruitment pool is present
and changes exact per-cell recruitment probabilities.

But under the tested Task-1 developmental workload,
removing that pool contribution entirely
preserves the preregistered functional envelope.

Therefore the historical global-pool dependency
is not currently justified as a necessary developmental primitive.

This does NOT prove
that a recruitment-pool signal is never useful.

It does show
that this benchmark does not require it
to preserve the validated V0.1 behavior.

The first literal local recurrent replacement
also does not earn retention.

It adds state,
saturates heavily,
and provides no preregistered benefit
over simple deletion.

PREREGISTERED CASE

LU-0C CASE B applies:

NO_POOL_SIMPLIFICATION_VIABLE = TRUE.

Therefore:

do not retain LOCAL_POOL_R12
merely because it is biologically attractive;

do not promote NO_POOL immediately;

run one fresh independent confirmation
of NO_POOL before any V0.2 architecture change.

NEXT AUTHORIZED STEP

Preregister an independent five-world confirmation:

GLOBAL_POOL_PARENT
versus
NO_POOL.

No local-pool treatment is needed in that confirmation.

Use fresh worlds derived only after the confirmation implementation freezes.

Preserve exactly:

Developmental Substrate V0.1;

LOCAL_HEDGE;

ECHO_PHASE;

D2;

G5_FULL OFF;

Task-1 load;

request-bound handoff;

neutral sensing;

scheduler;

expiry;

phase schedule;

anchor relocation;

lesion;

common randomness;

and all safety/integrity probes.

If NO_POOL independently satisfies
the same preservation envelope,
a separate architecture decision may remove
the global recruitment-pool contribution
from the next substrate revision.

PLAIN-SPEAK INTERPRETATION

We found something simpler than expected.

The old organism has a global recruitment signal.

We proved earlier
that the signal really is present
and really changes cell probabilities.

So we tried to replace it
with a local memory
that each cell could maintain itself.

That local memory worked,
but it did not quite preserve
the old system well enough
under the rule we froze in advance.

More importantly,
it did not beat the simplest option:

remove the global signal completely.

When we deleted that signal,
the organism still handled
the original workload,
the moved workplace,
the demand reversal,
and the lesion.

It stayed safe.

It did not use extra work.

Across these five new worlds,
the simpler organism passed every frozen preservation test.

So the current evidence says:

DO NOT BUILD A LOCAL SUBSTITUTE
FOR A SIGNAL WE MAY NOT NEED.

The next step is to give simple deletion
five completely new worlds
and make it prove itself again.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
