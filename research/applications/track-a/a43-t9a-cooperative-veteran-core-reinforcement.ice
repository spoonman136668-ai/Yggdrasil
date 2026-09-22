TITLE: YGGDRASIL A43 / T9A — Cooperative Veteran-Core Reinforcement
DATE: 2026-09-22
STATUS: PREREGISTERED CORE-COOPERATION EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T9A / APPLICATION-A
PARENT: A42 Active Veteran Recruitment and Push-Pull Turnover
MECHANISM PARENT: A40 Subtractive Support-Credit Pressure
BRANCH: dg1a-ar

A42 CLOSURE

a866e13826525b034eb19c10e54eb801c9ede6f6.

A42 RESULT

A42 established that active core recruitment
is mechanistically real.

Near-core favored recruitment
roughly doubled under ACTIVE_OCCUPANCY,
and MARGIN recruitment showed
a strong evidence-depth gradient.

But biased-periodic oscillation remained
87.50% to 100%
across active and push-pull arms.

Even the strongest refill arms
left favored commitment
at only about 29%
by adverse-burst end.

A41 exclusion,
A42 active recruitment,
and their direct push-pull composition
are therefore insufficient.

A43 QUESTION

Can committed veterans
reinforce one another locally
so that a dense same-side core
survives a short counter-pulse
as a cooperative unit?

A43 changes:

committed-state persistence only.

A43 does not change:

U recruitment;
H recruitment;
A35/A36 H behavior;
pool dynamics;
environment;
or topology.

F43 FREEZE

Let the exact A43 implementation freeze commit be:

F43.

No real A43 world,
population outcome,
or scientific result
may be derived before F43 exists.

WORLD SHAPE

384 fresh post-F43 trials.

48 contexts x 8 replicas.

48 cells.
48 epochs.

Environmental families remain structurally identical
to A42.

PARENT ORGANISM

Use the full A36 organism unchanged:

A29 pulse ecology;
A30 local nonlinear cross-inhibition;
A31 refractory memory;
A34 contradiction-suppressed independent recruitment;
A35 protected H uncertainty phenotype;
A36 spatial H niche entry/release cooperation.

No A37 lineage state exists.

SIGNED STATE

Preserve A40-A42 exactly.

rho = 3/4.

At epoch start:

B_pre(i,t)
=
the signed state carried from epoch t-1.

For C:

M_i
=
max(0,B_pre_i).

For S:

M_i
=
max(0,-B_pre_i).

Current local opposing evidence:

for C:
L_op = L_S.

for S:
L_op = L_C.

BASE SUBTRACTIVE PRESSURE

PRESSURE_BASE
=
max(0,L_op-M_i).

p_stay
=
1/(1+(PRESSURE/(1/2))^3).

K = 1/2.
n = 3.

COOPERATIVE SNAPSHOT TIMING

At epoch t:

1. capture B_pre;
2. update signed B as already frozen;
3. execute H release;
4. freeze the identities
   of cells currently committed C or S
   before any committed-cell defection;
5. compute same-side cooperative fields
   from that frozen snapshot
   using beginning-of-epoch M_i;
6. make all committed-cell defection decisions;
7. execute ordinary A34/A36 U recruitment
   with no A41 or A42 field.

Therefore:

a cell cannot reinforce another
because it survived the same epoch's decision.

The cooperative signal is synchronous,
order-independent,
and based only on state
that existed before the defection decisions.

COOPERATIVE RADIUS

Use exactly:

R_core = 3.

This is the existing recruitment radius.

No new radius exists.

The cell itself is excluded.

The neighborhood therefore contains
exactly six ring positions.

OCCUPANCY REINFORCEMENT FIELD

For committed cell i
with current side X:

Q_occ_same(i)
=
(1/6)
*
sum over 0 < ring_distance(i,j) <= 3
of
1[state_j = X].

Thus:

0 <= Q_occ_same <= 1.

MARGIN REINFORCEMENT FIELD

For C-committed i:

Q_margin_same(i)
=
(1/6)
*
sum over neighbors
1[state_j = C]
*
max(0,B_pre_j).

For S-committed i:

Q_margin_same(i)
=
(1/6)
*
sum over neighbors
1[state_j = S]
*
max(0,-B_pre_j).

Thus:

0 <= Q_margin_same <= 1.

No gain,
scale,
offset,
distance kernel,
or fitted threshold exists.

COOPERATIVE PRESSURE LAW

BASE:

PRESSURE
=
max(0,L_op-M_i).

OCCUPANCY_REINFORCE:

PRESSURE
=
max(
0,
L_op
-
M_i
-
Q_occ_same
).

MARGIN_REINFORCE:

PRESSURE
=
max(
0,
L_op
-
M_i
-
Q_margin_same
).

All arms then use exactly:

p_stay
=
1/(1+(PRESSURE/(1/2))^3).

This keeps p_stay intrinsically bounded in [0,1].

No additive probability bonus exists.

No clipping-based reinforcement exists.

INTERPRETATION

A43 does not make
a veteran stronger merely because
the global population agrees.

Only nearby same-side committed cells
can reinforce it.

A lone commitment receives
little or no cooperative protection.

A dense same-side core
receives stronger protection.

If neighboring veterans defect,
the cooperative field drops
on the next epoch.

Thus the mechanism can produce
a density-dependent stability boundary
without a central controller.

ARMS

Exactly six arms.

D2:

D2_BASE_SUBTRACTIVE_SLOW;
D2_OCCUPANCY_REINFORCE;
D2_MARGIN_REINFORCE.

D3:

D3_BASE_SUBTRACTIVE_SLOW;
D3_OCCUPANCY_REINFORCE;
D3_MARGIN_REINFORCE.

No A41 exclusion.

No A42 active recruitment.

No push-pull arm.

No MEDIUM arm.

All arms use rho = 3/4.

BASE RECRUITMENT

Use ordinary frozen A34/A36 recruitment
in every arm.

lambda_C;
lambda_S;
lambda_H

are unchanged.

No recruitment rate reads
Q_occ_same
or Q_margin_same.

PRIMARY TARGET

Biased-periodic contexts:

44;
45;
46;
47.

Report oscillation separately
for every context.

BALANCED CONTROL

Contexts:

40;
41;
42;
43.

Report:

oscillation;
final majority;
false-majority rate;
no-majority occupancy.

A43 must not stop oscillation
by freezing an arbitrary historical majority
under genuinely balanced evidence.

COOPERATIVE MECHANISM MEASUREMENTS

At every biased-periodic adverse-pulse onset,
for every favored-side committed cell,
record:

M_i;
same-side committed-neighbor count 0 through 6;
Q_occ_same;
Q_margin_same;
L_op;
PRESSURE_BASE;
PRESSURE_ARM;
commitment age.

For each arm report:

mean and median same-side neighbor count;
mean Q_occ_same;
mean Q_margin_same;
fraction PRESSURE_ARM = 0;
mean pressure reduction versus BASE.

DEFECT-LATENCY ORDERING

Freeze favored-side committed identities
at each adverse-pulse onset.

For every captured cell report:

same-side neighbor count;
Q field;
first defection epoch within the burst;
or NEVER.

Report Spearman correlation between:

Q field

and

defection latency.

Expected direction:

positive.

Also report defection rate
for each exact same-side neighbor count:

0;
1;
2;
3;
4;
5;
6.

This directly tests
the critical-density hypothesis
without inventing a post-result threshold.

CORE PERSISTENCE

Preserve A40-A42 reporting:

fraction of pulse-onset committed cells
still committed after adverse epoch:

1;
2;
3.

Additionally stratify by:

same-side neighbor count <= 2;

same-side neighbor count 3-4;

same-side neighbor count >= 5.

The dense cohort
should outlast the sparse cohort
if cooperative stabilization is real.

CLUSTER SURVIVAL

At pulse onset identify
contiguous favored-side committed domains
on the 48-cell ring.

For every domain record:

initial size;

mean member M;

mean member Q;

surviving member fraction
after adverse epochs 1, 2, 3;

whether the domain remains contiguous;

whether it vanishes.

Report survival by initial domain-size bins:

1-2;
3-4;
5-8;
9+.

This tests whether
cooperative protection is a cluster property
rather than only a cell-level correlation.

COUNTER-PULSE TRAJECTORY

Preserve:

favored committed fraction at pulse onset;

minimum favored committed fraction;

favored committed fraction at burst end;

recovery latency to pre-pulse fraction,
or NEVER.

A43 succeeds mechanistically
only if reinforcement preserves
more favored commitment through the burst,
not merely delays individual defections
without changing population retention.

TRUE REVERSAL COST

Preserve:

reversal acquisition;

old-majority loss latency;

new-majority acquisition;

old-side M at reversal onset;

M-to-zero latency;

signed-B zero-cross latency.

Additionally,
for the frozen old-side reversal cohort report:

same-side neighbor count at reversal onset;

Q reinforcement field at reversal onset;

median first defection latency
by neighbor-count bin:

<=2;
3-4;
>=5.

This is the rigidity check.

If dense old-side cores
cannot dissolve under true reversal,
cooperative reinforcement is too strong.

PRIMARY POPULATION METRICS

For every arm report:

aggregate service;
harm rate;
overall oscillation;
biased-periodic oscillation;
balanced false-majority;
false C dominance;
false S dominance;
contradiction no-majority;
reversal acquisition;
median old-majority loss;
directional coordination;
H occupancy;
niche prevalence;
recruitment activity.

MARGIN-VS-OCCUPANCY CAUSAL INTERPRETATION

Pointwise:

Q_occ_same >= Q_margin_same.

Therefore OCCUPANCY_REINFORCE
is generally the stronger-amplitude field.

If MARGIN_REINFORCE outperforms OCCUPANCY,
that is strong evidence
that evidence-depth selectivity matters.

If OCCUPANCY outperforms MARGIN,
A43 may conclude only
that the frozen occupancy field
was more effective.

It may not conclude
that evidence depth is intrinsically redundant.

A43 MARGIN INFORMATION GAIN

TRUE iff at least one MARGIN_REINFORCE arm:

reduces biased-periodic oscillation
versus paired BASE;

breaks at least 25%
of paired BASE biased oscillators;

raises mean adverse-epoch-3
favored core persistence
versus paired BASE;

shows positive Q_margin / defection-latency correlation;

shows greater epoch-3 persistence
for neighbor count >=5
than neighbor count <=2;

retains reversal acquisition >=80%;

retains aggregate service >=90%
of paired BASE;

and balanced false-majority <=10%.

A43 QUALIFICATION

D2_MARGIN_REINFORCE
or
D3_MARGIN_REINFORCE

is A43-QUALIFIED iff all are true:

1. overall oscillation <=5%;

2. biased-periodic oscillation <=10%;

3. breaks at least 50%
   of paired BASE biased oscillators;

4. biased-periodic oscillation
   is lower than paired OCCUPANCY_REINFORCE;

5. balanced false-majority <=10%;

6. false C dominance
   does not exceed paired BASE;

7. false S dominance
   does not exceed paired BASE;

8. reversal acquisition >=80%;

9. median old-majority loss <=4 epochs;

10. aggregate service >=90%
    of paired BASE;

11. recruitment remains nondegenerate;

12. mean adverse-epoch-3
    core persistence
    exceeds paired BASE;

13. dense-core epoch-3 persistence
    exceeds sparse-core epoch-3 persistence;

14. all integrity probes pass.

A43 COOPERATIVE INFORMATION GAIN

Because OCCUPANCY is also
a preregistered causal control,
report a broader descriptive result:

A43_COOPERATIVE_INFORMATION_GAIN

TRUE iff at least one cooperative arm
of either type:

reduces biased-periodic oscillation
versus paired BASE;

breaks at least 25%
of paired BASE biased oscillators;

raises adverse-epoch-3 core persistence;

shows positive cooperative-field
versus defection-latency ordering;

retains reversal acquisition >=80%;

retains >=90% paired BASE service;

and balanced false-majority <=10%.

This broader flag does not replace
the stricter MARGIN qualification.

FAILURE ATTRIBUTION

If cooperative Q strongly predicts survival
but macro oscillation remains:

core self-reinforcement is real
but still not the main oscillator bottleneck.

If OCCUPANCY succeeds
and MARGIN does not:

dense same-side topology matters,
but the frozen margin-weighted amplitude
is insufficient.

If MARGIN succeeds despite lower amplitude:

evidence depth has a genuine
cooperative signaling role.

If reinforcement stops oscillation
but reversal acquisition falls below80%
or old-majority loss exceeds4 epochs:

the core has become pathologically rigid.

If large domains survive
but isolated cells do not,
with oscillator reduction:

a critical cooperative core density
is supported.

If all domain sizes erode similarly:

the cooperative mechanism
does not create meaningful collective stability.

INTEGRITY PROBES

P1:
384 trials.

P2:
48 contexts x 8 replicas.

P3:
48 cells.

P4:
48 epochs.

P5:
initial C/S/U = 12/12/24.

P6:
A36 pulse ecology unchanged.

P7:
pool decay = 3/4.

P8:
local evidence radius = 12.

P9:
Hill n = 3.

P10:
Hill K = 1/2.

P11:
cooperative radius = 3.

P12:
exactly six ring-neighbor positions
enter Q.

P13:
self excluded from Q.

P14:
A34 recruitment unchanged.

P15:
A35 H hazards unchanged.

P16:
A36 niche mechanics unchanged.

P17:
D2 refractory = 2.

P18:
D3 refractory = 3.

P19:
rho exactly 3/4.

P20:
B starts at zero.

P21:
B updates every epoch for every cell.

P22:
BASE SUBTRACTIVE pressure
reads own M_pre exactly as A40.

P23:
cooperative snapshot occurs
before committed defection.

P24:
Q uses pre-defection committed identity.

P25:
MARGIN Q uses neighbors' M_pre.

P26:
OCCUPANCY pressure
subtracts exactly Q_occ_same.

P27:
MARGIN pressure
subtracts exactly Q_margin_same.

P28:
all arms use unchanged Hill law afterward.

P29:
no additive p_stay bonus exists.

P30:
no clipping-based reinforcement exists.

P31:
no new gain exists.

P32:
no new radius exists.

P33:
no distance kernel exists.

P34:
no new threshold exists.

P35:
no A41 exclusion exists.

P36:
no A42 active recruitment exists.

P37:
no A37 lineage state exists.

P38:
no future environment enters B or Q.

P39:
no centralized confidence scalar exists.

P40:
two complete primary sweeps byte-identical.

RESEARCH DISCIPLINE

Mechanical fake-world validation
must pass twice byte-identically
before F43.

F43 must exist
before fresh A43 worlds are derived.

The 384-world primary manifest
must be bound after F43
and before primary arm execution.

No post-result
rho,
radius,
gain,
kernel,
threshold,
arm,
qualification,
or world-family tuning.

PLAIN-SPEAK QUESTION

A41 taught the core
to keep some attackers out.

A42 taught the core
to call some allies back.

Both behaviors worked locally.

Neither stopped the whole organism
from flipping.

A43 moves inside the core itself.

A veteran now asks:

am I standing alone?

or am I surrounded
by other veterans
that have also earned this commitment?

If it is alone,
it gets little help.

If it is part of a dense,
well-supported cluster,
its neighbors help absorb
the short contradictory pulse.

The goal is not
to make the old decision permanent.

A real reversal still has to
tear the old core down.

The question is:

CAN A DENSE CORE
HOLD ITSELF TOGETHER
THROUGH A SHORT ATTACK,

WHILE STILL DISSOLVING
WHEN THE WORLD REALLY CHANGES?

A41:
hold the line.

A42:
bring reinforcements.

A43:
keep the core together.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
