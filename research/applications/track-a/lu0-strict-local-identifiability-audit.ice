TITLE: LU-0 — Strict-Local Identifiability Audit for Developmental Substrate V0.1
DATE: 2026-09-23
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

QUESTION

Can the exact Developmental Substrate V0.1
one-cell transition distribution
be determined from the cell's bounded local neighborhood alone?

Or does the inherited organism-wide C/S pool:

pc;
ps;

create a nonlocal information dependency
that a strictly local shared neural updater
cannot reproduce without receiving a broadcast signal?

WHY THIS MUST PRECEDE LEARNED-UPDATER TRAINING

The next planned model substrate is
one small shared neural update rule
executed by every cell.

Current NCA practice commonly uses
one shared learned local update rule
fed by bounded local perception.

Before training such a student,
Yggdrasil must establish whether
the frozen V0.1 teacher is actually identifiable
from the proposed local information boundary.

Training first would confound:

model-capacity failure

with

missing-input impossibility.

PARENT SUBSTRATE

Developmental Substrate V0.1:
4d3887fba0478bc1ef3bc4bea44f8e08582f5803.

V0.1 architecture record:
research/architecture/developmental-substrate-v0.1.ice.

V0 historical baseline:
92654adf407310a01e368e2c53934beae749482c.

Task-1H strong confirmation:
1b848079ae0d54dd9e7b01c8d004a93b16aeb62d.

AUDIT SCOPE

LU-0 changes no developmental dynamics.

LU-0 trains no neural network.

LU-0 runs no Task-1 qualification.

It performs a constructive causal identifiability test
on the exact V0.1 U-cell recruitment law.

WHY U RECRUITMENT

After LOCAL_HEDGE promotion:

H formation is local;

H release is local;

C/S challenge persistence is local;

ECHO_PHASE is local.

However U recruitment still contains:

sup_C = W_POOL * pc + W_LOCAL * L_C3;

sup_S = W_POOL * ps + W_LOCAL * L_S3;

opp_C = W_POOL * ps + W_LOCAL * L_S3;

opp_S = W_POOL * pc + W_LOCAL * L_C3.

Therefore U recruitment is the remaining
explicit organism-wide pool consumer
inside the developmental cell transition.

LU-0 tests that seam directly.

FROZEN CONSTANTS

N = 64.

D = 2.

R_TASK = 2.

LOCAL_R = 12.

RECRUIT_R = 3.

ETA = 1/2.

POOL_NORM = 160.

W_POOL = 3/4.

W_LOCAL = 1/4.

K_SUPP = 1/2.

N_SUPP = 3.

Probe cell:
i = 1.

The probe is U
under the inherited initial-state pattern.

BASE CELLULAR STATE

Use the exact inherited Task-1 initial state pattern:

i mod 4 = 0 -> C;

i mod 4 = 2 -> S;

otherwise U.

All timers:
0.

All B:
0.

All Q_prev:
0.

All Q_prev_side:
None.

Prior global pools:

C_pool = 0;

S_pool = 0.

No H cells exist in the fixture.

REQUEST OBJECTS

All audit requests are valid unfinished RAW requests.

Their input bits/programs are irrelevant to demand_adapter
and remain fixed deterministic placeholders.

The request identity affects no demand value.

LOCAL REQUEST TEMPLATES

Exactly four local templates:

L0:
no local request.

L1:
one C request at probe position 1.

L2:
one S request at probe position 1.

L3:
one C request
and one S request
at probe position 1.

DISTANT LOAD POSITIONS

Exactly seven positions,
expressed as clockwise offsets from probe:

15;
20;
25;
30;
35;
40;
45.

Modulo 64.

These positions are far enough
that their R_TASK = 2 demand footprints
do not enter the probe's radius-12 demand neighborhood.

DISTANT LOAD TYPES

D0:
no distant requests.

DC:
one C request at each
of the seven distant positions.

DS:
one S request at each
of the seven distant positions.

PAIR FAMILY

For each local template L0..L3,
evaluate exactly three counterfactual pairs:

DC versus DS;

DC versus D0;

DS versus D0.

Total pairs:

12.

No pair may be added,
removed,
or replaced after LU0F1.

LOCAL SIGNATURE

For each member of a pair,
construct an exact probe-local signature containing
for offsets -12..+12 around probe:

cell state;

timer;

B;

Q_prev;

Q_prev_side;

d_C;

d_S.

Also include the probe's:

L_C12;

L_S12;

L_C3;

L_S3;

local H density;

C support-margin field;

S support-margin field;

C cooperative field;

S cooperative field.

The pair is valid only if
the two local signatures are byte-identical.

Thus a bounded radius-12 observer
receives exactly the same input
in both worlds.

GLOBAL POOL UPDATE

Use the exact inherited pool update:

C_pool'
=
0.75 * C_pool
+
sum_j d_C(j)
+
fb_C;

S_pool'
=
0.75 * S_pool
+
sum_j d_S(j)
+
fb_S.

Where inherited committed-side feedback is:

fb_C =
count of C cells j
with d_C(j) >= d_S(j);

fb_S =
count of S cells j
with d_S(j) >= d_C(j).

Then:

pc = min(1, C_pool' / 160);

ps = min(1, S_pool' / 160).

No alternate pool definition is allowed.

V0.1 LOCAL H TERM

For probe U recruitment,
use the promoted V0.1 H hazard:

lambda_H
=
ETA
*
L_C3
*
L_S3
*
(1 + local_H_density_snapshot).

The fixture contains no H,
so the density term is zero.

This term is intentionally pool-free.

C/S RECRUITMENT HAZARDS

Use the exact inherited equations:

g_C
=
1 / [1 + (opp_C / K_SUPP)^N_SUPP];

g_S
=
1 / [1 + (opp_S / K_SUPP)^N_SUPP];

lambda_C
=
ETA * sup_C * g_C
+
ETA * support_margin_C;

lambda_S
=
ETA * sup_S * g_S
+
ETA * support_margin_S.

Total:

lambda
=
lambda_C + lambda_S + lambda_H.

Event probability:

P_event
=
1 - exp(-lambda).

If lambda > 0:

P(C)
=
P_event * lambda_C / lambda;

P(S)
=
P_event * lambda_S / lambda;

P(H)
=
P_event * lambda_H / lambda;

P(U)
=
1 - P_event.

If lambda = 0:

P(U) = 1
and all other probabilities = 0.

No stateless random draw is sampled.

LU-0 compares the exact transition DISTRIBUTION,
not one realized stochastic outcome.

PRIMARY METRIC

For each pair,
compute total-variation distance:

TV
=
1/2
*
sum over {C,S,H,U}
|P_A - P_B|.

Also report:

pc_A;
ps_A;
pc_B;
ps_B;

argmax non-U recruited side
among C and S;

absolute C-probability shift;

absolute S-probability shift.

STRICT-LOCAL IDENTIFIABILITY

LU0_STRICT_LOCAL_IDENTIFIABLE = TRUE iff:

1. all 12 pair local signatures
   are byte-identical within pair;

2. and max TV across all 12 pairs
   <= 1e-12.

If any valid local-identical pair
has TV > 1e-12:

LU0_STRICT_LOCAL_IDENTIFIABLE = FALSE.

This is a constructive identifiability criterion.

MATERIAL NONLOCAL DEPENDENCE

LU0_MATERIAL_POOL_DEPENDENCE = TRUE iff:

1. all 12 pair local signatures
   are byte-identical within pair;

2. median TV across 12 pairs
   >= 0.05;

3. max TV
   >= 0.10;

4. at least 4 of the 4
   DC-versus-DS pairs
   change the higher-probability C/S recruitment side.

The 0.05 median threshold means
at least five percentage points
of transition probability mass
moves solely because of information
outside the declared local observation radius.

The 0.10 max threshold
requires at least one substantial case.

INTERPRETATION RULES

If:

STRICT_LOCAL_IDENTIFIABLE = TRUE

then the existing V0.1 teacher
is compatible with exact strict-local distillation
under this audited U-recruitment seam.

Proceed to a learned-updater feasibility experiment.

If:

STRICT_LOCAL_IDENTIFIABLE = FALSE

and:

MATERIAL_POOL_DEPENDENCE = TRUE

then strict-local exact distillation
of V0.1 is architecturally impossible
without changing the information contract.

Do NOT respond by
making the neural network larger.

The next experiment must choose between:

A.
explicitly permitting pc/ps
as a bounded organism-wide broadcast input;

or

B.
testing a local replacement
for the global recruitment pool.

Because Yggdrasil's North Star
prefers developmental behavior
from bounded local cell interactions,
option B should be tested
before permanently admitting
a global broadcast into the learned updater.

If:

STRICT_LOCAL_IDENTIFIABLE = FALSE

but:

MATERIAL_POOL_DEPENDENCE = FALSE

then the dependency exists
but is small in this constructed envelope.

Proceed to a fresh-trajectory prevalence audit
before changing architecture.

MECHANICAL GATE

Before LU0F1:

prove exactly 12 pairs;

prove probe = 1 and U;

prove distant positions
have no demand footprint
inside probe radius 12;

prove all pair signatures
are identical within pair;

prove exact inherited constants;

prove exact inherited demand_adapter;

prove exact inherited pool update;

prove exact V0.1 local H hazard;

prove probability vector sums to 1
within 1e-12;

prove two complete audits
byte-identically.

FREEZE DISCIPLINE

Freeze implementation as LU0F1.

Then run exactly one
duplicate deterministic primary audit.

Interpret only after duplicate identity.

NO POST-RESULT TUNING

Do not change:

probe;

radius;

local templates;

distant positions;

pair family;

pool prior;

cell-state pattern;

pool equation;

hazard equations;

TV definition;

1e-12 identifiability threshold;

0.05 median materiality threshold;

0.10 maximum materiality threshold;

or side-flip criterion

after execution.

PLAIN-SPEAK QUESTION

Before we teach a tiny neural network
to become the cell's brain,
we need to know whether
we are giving it enough information.

Imagine two cells
whose entire visible neighborhoods
are exactly identical.

If the hand-written V0.1 organism
tells those two cells
to behave differently
only because work exists
far across the organism,
then a truly local neural cell
could never copy that rule exactly.

That would not be
a bad neural network.

It would be
missing information.

LU-0 checks that
before we waste time training.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
