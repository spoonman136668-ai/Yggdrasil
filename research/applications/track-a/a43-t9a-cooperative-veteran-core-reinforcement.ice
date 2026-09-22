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


POST-F43 PRIMARY MANIFEST BINDING

DATE:
2026-09-22.

F43:
6453348499ec860b587fb92af3471526175e4894

PRIMARY SEED:
A43-F43-6453348499ec860b587fb92af3471526175e4894-PRIMARY

WORLD COUNT:
384.

WORLD SHAPE:
48 contexts x 8 replicas.

PRIMARY WORLD MANIFEST SHA256:
3c534bcdee0e8e927735926f5260cfe959dc2d44274e7286c471340249f4a1c5

STATUS:
BOUND BEFORE ANY PRIMARY ARM EXECUTION.

The manifest was derived from the frozen F43 source
after F43 existed.

No arm outcome,
population metric,
qualification result,
or scientific comparison
was observed before this binding.

The canonical DG-1R-05 primary is not consumed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


A43 PRIMARY CLOSURE

DATE:
2026-09-22.

F43:
6453348499ec860b587fb92af3471526175e4894

MANIFEST-BINDING COMMIT:
822cc003b5f6d2fe4ac0adaf801faf3f6ea9a8bd

PRIMARY SEED:
A43-F43-6453348499ec860b587fb92af3471526175e4894-PRIMARY

PRIMARY WORLD MANIFEST SHA256:
3c534bcdee0e8e927735926f5260cfe959dc2d44274e7286c471340249f4a1c5

PRIMARY OUTPUT SHA256:
79dccdc8220fb781b7ef099f50507367963f242b5fc2b951d6cdfbc7efc853bb

PRIMARY RUNS:
2.

PRIMARY OUTPUT BYTES:
50086.

BYTE IDENTICAL:
true.

P40:
PASS.

All other executable integrity probes:
PASS.

A43_MARGIN_INFORMATION_GAIN:
TRUE.

A43_COOPERATIVE_INFORMATION_GAIN:
TRUE.

QUALIFICATION

D2_MARGIN_REINFORCE:
NOT QUALIFIED.

D3_MARGIN_REINFORCE:
NOT QUALIFIED.

TECHNICAL EVIDENCE

D2 BASE SUBTRACTIVE SLOW:
aggregate service 236006;
harm rate 16.41%;
overall oscillation 10.94%;
biased-periodic oscillation 96.88%;
balanced false-majority 0.00%;
reversal acquisition 90.62%;
median old-majority loss 2 epochs;
false C dominance 16.37%;
false S dominance 14.62%;
favored committed fraction
71.57% at adverse-pulse onset
to 25.15% at burst end;
adverse-epoch-3 core persistence 10.01%.

D2 MARGIN REINFORCE:
aggregate service 234929;
harm rate 16.41%;
overall oscillation 7.81%;
biased-periodic oscillation 53.12%;
balanced false-majority 0.00%;
reversal acquisition 89.84%;
median old-majority loss 2 epochs;
false C dominance 16.37%;
false S dominance 14.15%;
favored committed fraction
75.06% at adverse-pulse onset
to 44.63% at burst end;
adverse-epoch-3 core persistence 18.52%.

D2 OCCUPANCY REINFORCE:
aggregate service 158918;
harm rate 44.79%;
overall oscillation 0.78%;
biased-periodic oscillation 6.25%;
balanced false-majority 96.88%;
reversal acquisition 0.00%;
median old-majority loss NEVER;
false C dominance 26.90%;
false S dominance 14.15%;
favored committed fraction
79.33% at adverse-pulse onset
to 78.74% at burst end;
adverse-epoch-3 core persistence 83.50%.

D3 BASE SUBTRACTIVE SLOW:
aggregate service 230646;
harm rate 16.15%;
overall oscillation 10.42%;
biased-periodic oscillation 93.75%;
balanced false-majority 0.00%;
reversal acquisition 89.06%;
median old-majority loss 2 epochs;
false C dominance 16.37%;
false S dominance 13.68%;
favored committed fraction
66.76% at adverse-pulse onset
to 25.01% at burst end;
adverse-epoch-3 core persistence 10.86%.

D3 MARGIN REINFORCE:
aggregate service 231204;
harm rate 16.41%;
overall oscillation 6.77%;
biased-periodic oscillation 46.88%;
balanced false-majority 0.00%;
reversal acquisition 87.50%;
median old-majority loss 2 epochs;
false C dominance 15.79%;
false S dominance 13.21%;
favored committed fraction
70.10% at adverse-pulse onset
to 42.34% at burst end;
adverse-epoch-3 core persistence 15.96%.

D3 OCCUPANCY REINFORCE:
aggregate service 157832;
harm rate 45.57%;
overall oscillation 1.82%;
biased-periodic oscillation 9.38%;
balanced false-majority 93.75%;
reversal acquisition 0.00%;
median old-majority loss NEVER;
false C dominance 25.73%;
false S dominance 14.62%;
favored committed fraction
79.07% at adverse-pulse onset
to 78.72% at burst end;
adverse-epoch-3 core persistence 81.50%.

BIASED-PERIODIC CONTEXT DETAIL

D2 BASE:
44 = 7/8 oscillatory;
45 = 8/8;
46 = 8/8;
47 = 8/8.

D2 MARGIN REINFORCE:
44 = 0/8;
45 = 1/8;
46 = 8/8;
47 = 8/8.

D2 OCCUPANCY REINFORCE:
44 = 0/8;
45 = 0/8;
46 = 0/8;
47 = 2/8.

D3 BASE:
44 = 8/8;
45 = 8/8;
46 = 8/8;
47 = 6/8.

D3 MARGIN REINFORCE:
44 = 0/8;
45 = 0/8;
46 = 8/8;
47 = 7/8.

D3 OCCUPANCY REINFORCE:
44 = 0/8;
45 = 0/8;
46 = 0/8;
47 = 3/8.

PAIRED OSCILLATOR BREAKS

D2:
paired BASE biased oscillators = 31;
broken by MARGIN_REINFORCE = 14;
broken by OCCUPANCY_REINFORCE = 29.

D3:
paired BASE biased oscillators = 30;
broken by MARGIN_REINFORCE = 17;
broken by OCCUPANCY_REINFORCE = 28.

MARGIN COOPERATIVE MECHANISM

D2 MARGIN REINFORCE:
mean same-side neighbor count 4.771;
mean Q_margin 0.4193;
mean Q_occupancy 0.7951;
mean pressure reduction 0.1929;
PRESSURE = 0 fraction 82.90%;
Q_margin / defection-latency Spearman +0.1447.

Defection rate by same-side neighbor count:
0 = 72.73%;
1 = 85.59%;
2 = 82.18%;
3 = 72.67%;
4 = 63.77%;
5 = 42.20%;
6 = 19.27%.

D3 MARGIN REINFORCE:
mean same-side neighbor count 4.558;
mean Q_margin 0.4026;
mean Q_occupancy 0.7597;
mean pressure reduction 0.1861;
PRESSURE = 0 fraction 79.85%;
Q_margin / defection-latency Spearman +0.1750.

Defection rate by same-side neighbor count:
0 = 85.71%;
1 = 83.03%;
2 = 78.46%;
3 = 73.80%;
4 = 58.51%;
5 = 36.90%;
6 = 16.88%.

The low-count bins contain fewer
and more context-dependent observations,
so strict monotonicity is not claimed there.

The 3-through-6 gradient is strong
in both D2 and D3.

CORE-DENSITY PERSISTENCE

D2 MARGIN REINFORCE,
adverse epoch 3:

all = 18.52%;
neighbor count <=2 = 15.59%;
neighbor count 3-4 = 18.23%;
neighbor count >=5 = 21.21%.

D3 MARGIN REINFORCE,
adverse epoch 3:

all = 15.96%;
neighbor count <=2 = 13.86%;
neighbor count 3-4 = intermediate;
neighbor count >=5 = 16.50%.

Thus dense same-side neighborhoods
persist better than sparse neighborhoods
under MARGIN reinforcement.

CLUSTER SURVIVAL

D2 MARGIN REINFORCE,
epoch-3 surviving member fraction / domain vanish rate:

size 1-2:
17.47% / 77.68%.

size 3-4:
17.84% / 53.27%.

size 5-8:
20.69% / 26.05%.

size 9+:
20.13% / 24.32%.

D3 MARGIN REINFORCE:

size 1-2:
15.59% / 80.00%.

size 3-4:
17.15% / 56.76%.

size 5-8:
17.91% / 39.51%.

size 9+:
14.03% / 33.33%.

The D3 9+ epoch-3 bin is small,
so its surviving-member fraction
is not treated as a monotonic density law.

The robust spatial result is:

larger domains are substantially
less likely to vanish completely.

TRUE REVERSAL COST

D2 MARGIN REINFORCE:
reversal acquisition 89.84%;
median old-majority loss 2 epochs;
dense old-side cohort (neighbor count >=5):
100% eventually defected;
median first-defection latency 3 epochs.

D3 MARGIN REINFORCE:
reversal acquisition 87.50%;
median old-majority loss 2 epochs;
dense old-side cohort:
100% eventually defected;
median first-defection latency 3 epochs.

Therefore margin-weighted cooperation
does not create pathological irreversibility.

OCCUPANCY UPPER BOUND

OCCUPANCY_REINFORCE
nearly eliminates the target oscillator:

D2 biased-periodic 6.25%;
D3 biased-periodic 9.38%.

It also preserves approximately 82-84%
of the pulse-onset committed core
through adverse epoch 3.

But it does so by locking the organism.

Balanced false-majority becomes:

D2 96.88%;
D3 93.75%.

True reversal acquisition becomes:

0.00% in both.

Harm rises to roughly:

45%.

Thus OCCUPANCY_REINFORCE
is not a candidate solution.

It is an experimentally useful upper bound
showing that sufficient cooperative reinforcement
can stop the oscillator,
but excessive undifferentiated reinforcement
destroys reversibility and uncertainty.

QUALIFICATION INTERPRETATION

MARGIN_REINFORCE satisfies
the frozen information-gain requirements
in both D2 and D3.

It:

reduces biased-periodic oscillation strongly;

breaks more than 25%
of paired BASE target oscillators;

raises adverse-epoch-3 core persistence;

shows positive cooperative-field
versus defection-latency ordering;

preserves reversal acquisition above 80%;

preserves service above 90% of BASE;

and retains 0% balanced false-majority.

But it is NOT A43-QUALIFIED.

The remaining failures are substantial:

overall oscillation remains above 5%;

biased-periodic oscillation remains
53.12% in D2
and 46.88% in D3,
far above the 10% qualification limit;

and MARGIN cannot outperform
the much stronger but pathological
OCCUPANCY field on oscillator suppression.

CAUSAL INTERPRETATION

A43 is the first experiment in this sequence
to identify a cooperative core mechanism
that substantially changes the macro attractor
while preserving healthy reversal.

The effect is not merely local.

MARGIN_REINFORCE:

roughly halves the biased-periodic oscillator;

nearly doubles or materially raises
third-epoch core persistence;

raises favored commitment
at burst end from roughly 25%
to roughly 42-45%;

and retains true reversal
with a 2-epoch old-majority loss.

The positive Q_margin / defection-latency relation
and the same-side neighbor-count gradient
show that the effect is genuinely cooperative.

A veteran survives better
when embedded in a dense,
well-supported same-side core.

The occupancy arm proves
that the oscillator can be almost eliminated
by enough local cooperative reinforcement.

But occupancy also establishes
the opposite boundary:

undifferentiated cooperative support
is far too strong.

The remaining design space is therefore
not between:

no cooperation
and
cooperation.

It is between:

selective margin-weighted cooperation
that remains reversible
but is still too weak in some target contexts;

and

full occupancy cooperation
that is strong enough
but pathologically rigid.

The key unresolved structure
is context-specific.

MARGIN_REINFORCE eliminates
almost all oscillation in contexts 44 and 45,
but leaves contexts 46 and 47
largely oscillatory.

That pattern should be diagnosed mechanistically
before introducing a new strength parameter.

No post-result gain is justified.

The next experiment should determine
what distinguishes the residual 46/47 failures
from the solved 44/45 cases,
then add one causal mechanism
that changes cooperative reinforcement
without crossing into the occupancy lock-in regime.

PLAIN-SPEAK INTERPRETATION

A43 finally found something
that changes the whole organism,
not just a local symptom.

When veterans help nearby veterans,
the core really does become harder
to tear apart.

With margin-weighted cooperation,
the old side ends a bad pulse
with roughly 42-45% of the population
still committed,
instead of only about 25%.

And the flipping problem
is cut roughly in half.

Most importantly,
the organism can still change its mind
when the world truly changes.

So cooperative reinforcement is real.

But we also found the danger line.

If every nearby committed cell
gets full-strength voting power,
the oscillator almost disappears completely.

That sounds good
until we look at why.

The organism becomes nearly frozen.

Under balanced evidence
it keeps old majorities
more than 90% of the time,
and in real reversals
it fails to switch at all.

So we have now bracketed
the useful cooperative regime.

Too little cooperation:
the core falls apart.

Margin-weighted cooperation:
the core holds much better
and stays reversible,
but some periodic worlds still beat it.

Full occupancy cooperation:
the core becomes almost unbreakable,
which is worse than oscillation.

The next move should not be:

turn the cooperation knob up.

That would be tuning toward the answer.

The useful question is now:

why does the same
margin-weighted cooperative core
solve contexts 44 and 45
but still fail in 46 and 47?

That difference can tell us
what behavior is actually missing.

A41:
hold the line.

A42:
bring reinforcements.

A43:
keep the core together.

A43 WORKS MECHANISTICALLY,
but the remaining failure
is now narrow enough
to diagnose rather than guess.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
