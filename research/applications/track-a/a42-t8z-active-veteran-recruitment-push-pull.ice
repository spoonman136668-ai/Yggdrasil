TITLE: YGGDRASIL A42 / T8Z — Active Veteran Recruitment and Push-Pull Turnover
DATE: 2026-09-22
STATUS: PREREGISTERED ACTIVE-RECRUITMENT EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8Z / APPLICATION-A
PARENT: A41 Veteran-Core Recruitment Exclusion Field
MECHANISM PARENT: A36 Spatially Cooperative Protected Hedge Niches
BRANCH: dg1a-ar

A41 CLOSURE

735af926c189a8383c9a99d1dc8227a61b60dd7e.

A41 RESULT

A41 established that local exclusion is mechanistically active.

OCCUPANCY_EXCLUSION substantially reduced
adverse recruitment near a surviving core.

But biased-periodic oscillation remained
93.75% to 100% across exclusion arms.

The key counter-pulse result was:

favored committed fraction
fell from roughly 66-72% at pulse onset
to roughly 25-26% at burst end
under every A41 arm.

Therefore A41 created a fence
but not a regenerative core.

A42 QUESTION

Can a surviving veteran core
actively recruit nearby uncertain cells
toward its own commitment?

And does positive recruitment
combine synergistically
with A41 exclusion?

A42 separates:

barrier;

magnet;

and barrier plus magnet.

F42 FREEZE

Let the exact A42 implementation freeze commit be:

F42.

No real A42 world,
population outcome,
or scientific result
may be derived before F42 exists.

WORLD SHAPE

384 fresh post-F42 trials.

48 contexts x 8 replicas.

48 cells.
48 epochs.

Environmental families remain structurally identical
to A41.

PARENT ORGANISM

Use the full A36 organism unchanged:

A29 pulse ecology;
A30 local nonlinear cross-inhibition;
A31 refractory memory;
A34 contradiction-suppressed independent recruitment;
A35 protected H uncertainty phenotype;
A36 spatial H niche entry/release cooperation.

No A37 lineage state exists.

COMMITTED-STATE LAW

All A42 arms use
A40/A41 SUBTRACTIVE_SLOW
for committed-state defection.

rho = 3/4.

For C:
M_pre = max(0,B_pre).

For S:
M_pre = max(0,-B_pre).

PRESSURE = max(0,L_op-M_pre).

p_stay = 1/(1+(PRESSURE/(1/2))^3).

No A42 arm changes
committed-state defection.

SURVIVOR-CORE TIMING

Preserve A41 timing.

At epoch t:

1. capture B_pre;
2. update signed B;
3. execute H release;
4. execute committed-state SUBTRACTIVE_SLOW defection;
5. freeze the surviving C/S core snapshot;
6. compute local recruitment fields;
7. execute U-cell recruitment.

The recruitment field reads
surviving committed identity
and beginning-of-epoch aligned M_pre.

No current evidence is counted twice
through M.

FIELD RADIUS

Use exactly:

R_core = RECRUIT_R = 3.

No new radius exists.

OCCUPANCY FIELD

For eligible U cell i:

Q_C_occ(i)
=
mean over radius 3
of 1[state_j = C].

Q_S_occ(i)
=
mean over radius 3
of 1[state_j = S].

MARGIN FIELD

Q_C_margin(i)
=
mean over radius 3
of 1[state_j = C] * max(0,B_pre_j).

Q_S_margin(i)
=
mean over radius 3
of 1[state_j = S] * max(0,-B_pre_j).

Thus all Q values remain in [0,1].

No new gain,
scale,
offset,
distance kernel,
or fitted threshold exists.

BASE RECRUITMENT

Preserve A34/A41 base recruitment:

lambda_C;
lambda_S;
lambda_H

exactly as already frozen.

H recruitment is unchanged
in every A42 arm.

ACTIVE OCCUPANCY RECRUITMENT

lambda_C'
=
lambda_C
+
ETA * Q_C_occ.

lambda_S'
=
lambda_S
+
ETA * Q_S_occ.

lambda_H'
=
lambda_H.

ACTIVE MARGIN RECRUITMENT

lambda_C'
=
lambda_C
+
ETA * Q_C_margin.

lambda_S'
=
lambda_S
+
ETA * Q_S_margin.

lambda_H'
=
lambda_H.

Frozen:

ETA = 1/2.

Therefore no new recruitment gain exists.

A41 OCCUPANCY EXCLUSION CONTROL

Preserve exactly:

lambda_C'
=
lambda_C * (1-Q_S_occ).

lambda_S'
=
lambda_S * (1-Q_C_occ).

lambda_H'
=
lambda_H.

PUSH-PULL COMPOSITION

The push-pull arm composes
the two already-defined transformations.

For C:

lambda_C'
=
(lambda_C + ETA*Q_C_margin)
*
(1-Q_S_occ).

For S:

lambda_S'
=
(lambda_S + ETA*Q_S_margin)
*
(1-Q_C_occ).

lambda_H'
=
lambda_H.

This introduces no third field
and no new parameter.

It means:

same-side veteran margin
acts as a magnet;

opposing committed occupancy
acts as a barrier.

The exclusion multiplier
applies to the complete recruitment intensity
toward that side.

ARMS

Exactly ten arms.

D2:

D2_BASE_SUBTRACTIVE_SLOW;
D2_OCCUPANCY_EXCLUSION;
D2_ACTIVE_OCCUPANCY_RECRUIT;
D2_ACTIVE_MARGIN_RECRUIT;
D2_PUSH_PULL.

D3:

D3_BASE_SUBTRACTIVE_SLOW;
D3_OCCUPANCY_EXCLUSION;
D3_ACTIVE_OCCUPANCY_RECRUIT;
D3_ACTIVE_MARGIN_RECRUIT;
D3_PUSH_PULL.

No MEDIUM arm exists.

All arms use rho = 3/4.

CAUSAL QUESTIONS

BASE vs OCCUPANCY_EXCLUSION:

barrier alone.

BASE vs ACTIVE_OCCUPANCY_RECRUIT:

plain spatial magnet alone.

BASE vs ACTIVE_MARGIN_RECRUIT:

evidence-depth-weighted magnet alone.

ACTIVE_OCCUPANCY_RECRUIT
vs
ACTIVE_MARGIN_RECRUIT:

does evidence depth improve
positive recruitment topology
under the frozen no-gain formulas?

OCCUPANCY_EXCLUSION
vs
ACTIVE_MARGIN_RECRUIT
vs
PUSH_PULL:

barrier alone;
magnet alone;
barrier plus magnet.

PRIMARY TARGET

Biased-periodic contexts:

44;
45;
46;
47.

Report oscillation separately
for all four contexts.

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

A42 must not stop pulse chasing
by manufacturing a stable majority
under balanced evidence.

ACTIVE-RECRUITMENT MEASUREMENTS

At every biased-periodic adverse-pulse epoch,
for every eligible U cell,
record:

Q_C_occ;
Q_S_occ;
Q_C_margin;
Q_S_margin;

base lambda_C;
base lambda_S;

transformed lambda_C;
transformed lambda_S;

whether recruitment fired;

joined state.

For the long-run favored side report:

mean active same-side lambda increment;

mean opposing-side lambda suppression;

favored-side recruitment rate
inside core radius;

adverse-side recruitment rate
inside core radius;

the same two rates outside core radius.

For ACTIVE_MARGIN_RECRUIT
and PUSH_PULL,
stratify favored-side recruitment
by Q_margin quartile.

Expected direction:

higher same-side Q_margin
should produce higher same-side recruitment.

COUNTER-PULSE REGENERATION

Preserve A41 trajectory measurement.

For every biased adverse burst report:

favored committed fraction at pulse onset;

minimum favored committed fraction;

favored committed fraction at burst end;

recovery latency to pre-pulse fraction,
or NEVER.

A42's central mechanistic test is:

does active recruitment raise
the burst-end favored committed fraction
above BASE / exclusion-only?

CORE-ADJACENT TURNOVER

At each biased adverse-pulse onset,
freeze the favored survivor-core identities.

During the burst,
for eligible U cells within radius 3
of that frozen core report:

opportunities;

favored-side recruitment;

adverse-side recruitment;

H recruitment;

no recruitment.

This replaces inference from final majority
with direct population-turnover accounting.

PUSH-PULL SYNERGY

For each D value report:

paired BASE biased oscillators;

broken by OCCUPANCY_EXCLUSION;

broken by ACTIVE_MARGIN_RECRUIT;

broken by PUSH_PULL;

broken by both single mechanisms;

broken only by PUSH_PULL.

A PUSH_PULL-only break is:

a BASE oscillator
that remains oscillatory under both:

OCCUPANCY_EXCLUSION;

and ACTIVE_MARGIN_RECRUIT;

but is non-oscillatory under PUSH_PULL.

This is the preregistered synergy signature.

TRUE REVERSAL COST

Preserve:

reversal acquisition;

old-majority loss latency;

new-majority acquisition;

old-side M at reversal onset;

M-to-zero latency;

signed-B zero-cross latency.

Additionally,
instrument every eligible U recruitment opportunity
within radius 3 of the frozen old-side reversal core.

For each post-reversal epoch report:

opportunities;

old-side recruitments;

new-side recruitments;

H recruitments;

no recruitment.

This measurement is required
at opportunity resolution.

It repairs the A41 instrumentation gap.

Report median latency
until new-side recruitment rate
within radius 3 of the old core
exceeds old-side recruitment rate.

If it never occurs:

NEVER.

This diagnostic is frozen before F42.

MOAT / DEADLOCK CHECKS

Preserve A41:

C/S/U trajectory;

midpoint ring snapshot;

frozen core mask;

final-eight-epoch
min(C_fraction,S_fraction);

U fraction;

majority changes;

largest C domain;

largest S domain;

C/S interface count.

No distance-decay rescue arm
is added inside A42.

A42 ACTIVE-MARGIN INFORMATION GAIN

TRUE iff at least one ACTIVE_MARGIN_RECRUIT arm:

reduces biased-periodic oscillation
versus paired BASE;

breaks at least 25%
of paired BASE biased oscillators;

raises mean burst-end favored committed fraction
above paired BASE;

shows higher favored recruitment
in high-Q_margin than low-Q_margin neighborhoods;

retains reversal acquisition >= 80%;

retains aggregate service >= 90%
of paired BASE;

and balanced false-majority <= 10%.

A42 PUSH-PULL QUALIFICATION

D2_PUSH_PULL or D3_PUSH_PULL
is A42-QUALIFIED iff all are true:

1. overall oscillation <= 5%;

2. biased-periodic oscillation <= 10%;

3. breaks at least 50%
   of paired BASE biased oscillators;

4. biased-periodic oscillation
   is lower than paired OCCUPANCY_EXCLUSION;

5. biased-periodic oscillation
   is lower than paired ACTIVE_MARGIN_RECRUIT;

6. at least one paired BASE oscillator
   is broken only by PUSH_PULL
   and by neither single mechanism;

7. balanced false-majority <= 10%;

8. false C dominance
   does not exceed paired BASE;

9. false S dominance
   does not exceed paired BASE;

10. reversal acquisition >= 80%;

11. median old-majority loss <= 4 epochs;

12. aggregate service >= 90%
    of paired BASE;

13. recruitment remains nondegenerate;

14. mean burst-end favored committed fraction
    is greater than paired BASE;

15. all integrity probes pass.

A42 PUSH-PULL INFORMATION GAIN

TRUE iff at least one PUSH_PULL arm:

reduces biased-periodic oscillation
versus both paired single mechanisms;

breaks at least 25%
of paired BASE biased oscillators;

has at least one PUSH_PULL-only oscillator break;

raises burst-end favored committed fraction
versus BASE;

retains reversal acquisition >= 80%;

retains >= 90% paired BASE service;

and balanced false-majority <= 10%.

MARGIN-VS-OCCUPANCY INTERPRETATION

A42 must not overclaim
if OCCUPANCY recruitment exceeds MARGIN recruitment.

Under the frozen definitions:

Q_occ >= Q_margin pointwise.

Therefore OCCUPANCY is generally
a stronger-amplitude intervention.

If MARGIN wins despite lower amplitude,
that is strong evidence
that evidence-depth selectivity adds value.

If OCCUPANCY wins,
A42 can say only:

the frozen occupancy field
was more effective.

It cannot by itself prove
that evidence depth is intrinsically redundant.

NO COMMON-RANDOM-NUMBER CLAIM

Arms remain deterministic
but use arm-domain-separated random streams,
consistent with the existing lineage.

Paired oscillator-break counts
therefore mean matched world identity,
not identical stochastic draws.

Small differences of one or two worlds
must not be interpreted as strong causal evidence.

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
recruitment radius = 3.

P12:
core field radius = 3.

P13:
ETA = 1/2.

P14:
pool normalization = 160.

P15:
A34 contradiction suppression unchanged.

P16:
A35 H hazards unchanged.

P17:
A36 niche mechanics unchanged.

P18:
D2 refractory = 2.

P19:
D3 refractory = 3.

P20:
all arms use SUBTRACTIVE_SLOW defection.

P21:
rho exactly 3/4.

P22:
B starts at zero.

P23:
B updates every epoch for every cell.

P24:
SUBTRACTIVE pressure reads M_pre.

P25:
BASE recruitment unchanged.

P26:
OCCUPANCY_EXCLUSION exactly matches A41.

P27:
ACTIVE_OCCUPANCY adds exactly ETA*Q_same_occ.

P28:
ACTIVE_MARGIN adds exactly ETA*Q_same_margin.

P29:
PUSH_PULL exactly composes
ACTIVE_MARGIN then OCCUPANCY_EXCLUSION.

P30:
lambda_H unchanged in every arm.

P31:
no new gain exists.

P32:
no new radius exists.

P33:
no distance kernel exists.

P34:
no new threshold exists.

P35:
no A37 lineage state exists.

P36:
no future environment enters B or Q.

P37:
no centralized confidence scalar exists.

P38:
true-reversal recruitment diagnostic
is opportunity-resolved.

P39:
two complete primary sweeps byte-identical.

RESEARCH DISCIPLINE

Mechanical fake-world validation
must pass twice byte-identically
before F42.

F42 must exist
before fresh A42 worlds are derived.

The 384-world primary manifest
must be bound after F42
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

A41 built a fence.

The fence really did
keep some of the attacking side
from moving in near the old core.

But the old side still emptied out.

A42 adds the missing half.

A surviving core can now say:

come back over here.

The experiment asks:

is a fence enough?

is a magnet enough?

or does the organism need both
at the same time?

The most important outcome is not
whether recruitment simply gets stronger.

It is whether:

the core loses fewer allies
during a short attack;

the opposition rebuilds more slowly;

the old side refills nearby uncertain space;

the oscillator stops closing its cycle;

and the organism can still change sides
when the world genuinely changes.

A41:
hold the line.

A42:
bring reinforcements.

PUSH_PULL:
hold the line
while bringing reinforcements.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-F42 PRIMARY MANIFEST BINDING

DATE:
2026-09-22.

F42:
24582ea6b6b8ec5f4e3f21a5b8b5c1a0ef94f05a

PRIMARY SEED:
A42-F42-24582ea6b6b8ec5f4e3f21a5b8b5c1a0ef94f05a-PRIMARY

WORLD COUNT:
384.

WORLD SHAPE:
48 contexts x 8 replicas.

PRIMARY WORLD MANIFEST SHA256:
fb9e97ac025cdbe605d381807e6756050c072dd047ee60d179e5921744346dce

STATUS:
BOUND BEFORE ANY PRIMARY ARM EXECUTION.

The manifest was derived from the frozen F42 source
after F42 existed.

No arm outcome,
population metric,
qualification result,
or scientific comparison
was observed before this binding.

The canonical DG-1R-05 primary is not consumed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


A42 PRIMARY CLOSURE

DATE:
2026-09-22.

F42:
24582ea6b6b8ec5f4e3f21a5b8b5c1a0ef94f05a

MANIFEST-BINDING COMMIT:
6fba8f2c1dabcd34bdf26c11f272a2a2dcb73146

PRIMARY SEED:
A42-F42-24582ea6b6b8ec5f4e3f21a5b8b5c1a0ef94f05a-PRIMARY

PRIMARY WORLD MANIFEST SHA256:
fb9e97ac025cdbe605d381807e6756050c072dd047ee60d179e5921744346dce

PRIMARY OUTPUT SHA256:
8ac5b6bc5508db1b0b7bbf34814db77f3d0da715661bb6db8cce9c48c610cbfb

PRIMARY RUNS:
2.

PRIMARY OUTPUT BYTES:
58813.

BYTE IDENTICAL:
true.

P39:
PASS.

All other executable integrity probes:
PASS.

A42_ACTIVE_MARGIN_INFORMATION_GAIN:
FALSE.

A42_PUSH_PULL_INFORMATION_GAIN:
FALSE.

QUALIFICATION

D2_PUSH_PULL:
NOT QUALIFIED.

D3_PUSH_PULL:
NOT QUALIFIED.

TECHNICAL EVIDENCE

D2 BASE SUBTRACTIVE SLOW:
aggregate service 235632;
harm rate 16.15%;
overall oscillation 9.64%;
biased-periodic oscillation 90.62%;
balanced false-majority 3.12%;
reversal acquisition 91.41%;
median old-majority loss 2 epochs;
false C dominance 17.75%;
false S dominance 14.08%;
mean favored committed fraction
72.04% at adverse-pulse onset
to 26.99% at burst end;
core-adjacent favored recruitment 12.19%;
core-adjacent adverse recruitment 9.77%.

D2 OCCUPANCY EXCLUSION:
aggregate service 236004;
harm rate 15.36%;
overall oscillation 10.68%;
biased-periodic oscillation 100.00%;
balanced false-majority 0.00%;
reversal acquisition 92.19%;
median old-majority loss 2 epochs;
burst end favored fraction 26.07%;
core-adjacent favored recruitment 11.98%;
core-adjacent adverse recruitment 6.89%.

D2 ACTIVE OCCUPANCY RECRUIT:
aggregate service 247496;
harm rate 15.36%;
overall oscillation 11.46%;
biased-periodic oscillation 87.50%;
balanced false-majority 0.00%;
reversal acquisition 99.22%;
median old-majority loss 2 epochs;
burst end favored fraction 29.12%;
core-adjacent favored recruitment 24.24%;
core-adjacent adverse recruitment 8.49%.

D2 ACTIVE MARGIN RECRUIT:
aggregate service 239327;
harm rate 15.89%;
overall oscillation 12.50%;
biased-periodic oscillation 100.00%;
balanced false-majority 0.00%;
reversal acquisition 96.09%;
median old-majority loss 2 epochs;
burst end favored fraction 27.49%;
core-adjacent favored recruitment 17.42%;
core-adjacent adverse recruitment 8.88%.

D2 PUSH_PULL:
aggregate service 240544;
harm rate 15.89%;
overall oscillation 9.11%;
biased-periodic oscillation 87.50%;
balanced false-majority 0.00%;
reversal acquisition 96.88%;
median old-majority loss 2 epochs;
false C dominance 20.12%;
false S dominance 15.49%;
burst end favored fraction 28.67%;
core-adjacent favored recruitment 17.44%;
core-adjacent adverse recruitment 6.45%.

D3 BASE SUBTRACTIVE SLOW:
aggregate service 230816;
harm rate 16.67%;
overall oscillation 10.42%;
biased-periodic oscillation 93.75%;
balanced false-majority 0.00%;
reversal acquisition 88.28%;
median old-majority loss 2 epochs;
false C dominance 17.16%;
false S dominance 12.68%;
mean favored committed fraction
65.91% at pulse onset
to 25.50% at burst end;
core-adjacent favored recruitment 12.10%;
core-adjacent adverse recruitment 10.00%.

D3 OCCUPANCY EXCLUSION:
aggregate service 230782;
harm rate 14.84%;
overall oscillation 9.38%;
biased-periodic oscillation 93.75%;
balanced false-majority 0.00%;
reversal acquisition 88.28%;
median old-majority loss 2 epochs;
burst end favored fraction 26.02%;
core-adjacent favored recruitment 11.01%;
core-adjacent adverse recruitment 7.93%.

D3 ACTIVE OCCUPANCY RECRUIT:
aggregate service 241300;
harm rate 16.67%;
overall oscillation 11.20%;
biased-periodic oscillation 93.75%;
balanced false-majority 0.00%;
reversal acquisition 93.75%;
median old-majority loss 2 epochs;
burst end favored fraction 29.08%;
core-adjacent favored recruitment 23.68%;
core-adjacent adverse recruitment 9.90%.

D3 ACTIVE MARGIN RECRUIT:
aggregate service 235252;
harm rate 15.89%;
overall oscillation 10.42%;
biased-periodic oscillation 90.62%;
balanced false-majority 0.00%;
reversal acquisition 91.41%;
median old-majority loss 2 epochs;
burst end favored fraction 27.45%;
core-adjacent favored recruitment 16.47%;
core-adjacent adverse recruitment 9.15%.

D3 PUSH_PULL:
aggregate service 235495;
harm rate 16.67%;
overall oscillation 9.64%;
biased-periodic oscillation 100.00%;
balanced false-majority 0.00%;
reversal acquisition 91.41%;
median old-majority loss 2 epochs;
false C dominance 18.34%;
false S dominance 13.62%;
burst end favored fraction 27.34%;
core-adjacent favored recruitment 17.09%;
core-adjacent adverse recruitment 7.69%.

BIASED-PERIODIC CONTEXT DETAIL

D2 ACTIVE OCCUPANCY:
44 = 6/8 oscillatory;
45 = 6/8;
46 = 8/8;
47 = 8/8.

D2 ACTIVE MARGIN:
44 = 8/8;
45 = 8/8;
46 = 8/8;
47 = 8/8.

D2 PUSH_PULL:
44 = 7/8;
45 = 5/8;
46 = 8/8;
47 = 8/8.

D3 ACTIVE OCCUPANCY:
44 = 6/8;
45 = 8/8;
46 = 8/8;
47 = 8/8.

D3 ACTIVE MARGIN:
44 = 7/8;
45 = 7/8;
46 = 8/8;
47 = 7/8.

D3 PUSH_PULL:
44 = 8/8;
45 = 8/8;
46 = 8/8;
47 = 8/8.

PAIRED OSCILLATOR BREAKS

D2:
paired BASE biased oscillators = 29;
broken by OCCUPANCY_EXCLUSION = 0;
broken by ACTIVE_MARGIN_RECRUIT = 0;
broken by PUSH_PULL = 2;
PUSH_PULL-only breaks = 2.

D3:
paired BASE biased oscillators = 30;
broken by OCCUPANCY_EXCLUSION = 1;
broken by ACTIVE_MARGIN_RECRUIT = 2;
broken by PUSH_PULL = 0;
PUSH_PULL-only breaks = 0.

The D2 PUSH_PULL-only breaks satisfy
the preregistered existence test for synergy cases,
but 2/29 is far below
the required 25% information-gain
and 50% qualification break rates.

ACTIVE-RECRUITMENT MECHANISM

The positive recruitment mechanism is strongly active.

D2 ACTIVE MARGIN:
high-Q favored recruitment 28.69%;
low-Q favored recruitment 3.28%.

D3 ACTIVE MARGIN:
high-Q favored recruitment 27.37%;
low-Q favored recruitment 3.53%.

D2 ACTIVE OCCUPANCY:
high-Q favored recruitment 36.21%;
low-Q favored recruitment 4.16%.

D3 ACTIVE OCCUPANCY:
high-Q favored recruitment 36.25%;
low-Q favored recruitment 4.56%.

Thus survivor-core topology
strongly changes which side
nearby U cells join.

As preregistered,
OCCUPANCY is the higher-amplitude field
because Q_occ >= Q_margin pointwise.

Its stronger recruitment effect
therefore does not establish
that margin information is redundant.

COUNTER-PULSE REGENERATION

Active recruitment improves
favored-side refill.

D2:
BASE burst end 26.99%;
ACTIVE MARGIN 27.49%;
ACTIVE OCCUPANCY 29.12%;
PUSH_PULL 28.67%.

D3:
BASE 25.50%;
ACTIVE MARGIN 27.45%;
ACTIVE OCCUPANCY 29.08%;
PUSH_PULL 27.34%.

Therefore the magnet is real.

But even the strongest refill arm
leaves only about 29%
of the population
committed to the favored side
at adverse-burst end.

The regeneration gain is too small
to prevent cycle closure.

PUSH-PULL ATTRIBUTION

PUSH_PULL does not show
consistent macro synergy.

In D2,
PUSH_PULL and ACTIVE_OCCUPANCY
both reach 87.50%
biased-periodic oscillation,
with two PUSH_PULL-only matched-world breaks.

In D3,
PUSH_PULL worsens to 100.00%
while ACTIVE_MARGIN reaches 90.62%.

PUSH_PULL does improve
the local turnover ratio:

D2 PUSH_PULL
favored 17.44% / adverse 6.45%;

D3 PUSH_PULL
favored 17.09% / adverse 7.69%.

But the multiplicative exclusion term
also attenuates the complete recruitment intensity
toward a side
where opposing committed occupancy is present.

The net local improvement
does not translate into
stable population-level cycle breaking.

TRUE REVERSAL

All active and PUSH_PULL arms
retain reversal acquisition well above 80%.

D2:
ACTIVE MARGIN 96.09%;
ACTIVE OCCUPANCY 99.22%;
PUSH_PULL 96.88%.

D3:
ACTIVE MARGIN 91.41%;
ACTIVE OCCUPANCY 93.75%;
PUSH_PULL 91.41%.

Median old-majority loss remains
2 epochs in every arm.

The repaired opportunity-resolved diagnostic
reports median latency
until new-side recruitment near the frozen old core
exceeds old-side recruitment:

D2 active / push-pull arms:
4 epochs.

D3 active / push-pull arms:
5 epochs.

Thus A42 does not fail
because active recruitment makes
the organism unable to reverse.

QUALIFICATION FAILURE

No A42 arm approaches
the frozen oscillation thresholds.

No PUSH_PULL arm
breaks at least 25%
of paired BASE biased oscillators.

D2 and D3 PUSH_PULL
also increase false C / false S dominance
relative to paired BASE,
violating the no-worse false-dominance guard.

Therefore:

A42_ACTIVE_MARGIN_INFORMATION_GAIN = FALSE.

A42_PUSH_PULL_INFORMATION_GAIN = FALSE.

D2_PUSH_PULL = NOT QUALIFIED.

D3_PUSH_PULL = NOT QUALIFIED.

CAUSAL INTERPRETATION

A42 separates three facts.

First:

positive core recruitment is real.

A surviving committed neighborhood
can act as a local magnet,
and nearby uncertain cells
join that side at much higher rates.

Second:

positive recruitment provides
real population refill,
but not enough.

The strongest active recruitment arms
raise adverse-burst end commitment
by only a few percentage points,
from roughly 25-27%
to roughly 29%.

Third:

combining barrier plus magnet
does not produce a robust nonlinear rescue
under the frozen composition.

A42 therefore closes
the simple periphery-turnover interval:

exclusion alone is insufficient;

active recruitment alone is insufficient;

their direct push-pull composition
is insufficient.

The remaining bottleneck
is increasingly concentrated
inside the surviving committed core itself.

At pulse onset,
the favored population can be large.

By pulse end,
even with active local refill,
most of that commitment has disappeared.

The next justified experiment
should therefore test
whether committed veterans
can reinforce one another
so that the core's own persistence
depends on local same-side core density.

That is a distinct causal mechanism
from:

individual evidence-depth persistence;

periphery exclusion;

and active recruitment.

PLAIN-SPEAK INTERPRETATION

A42 gave the core a recruiting voice.

It worked.

When strong committed cells were nearby,
uncertain cells were much more likely
to join them.

The strongest recruitment arm
roughly doubled
same-side recruitment near the core.

But the organism still kept flipping.

The reason is now clearer.

The fence from A41
can keep some attackers out.

The magnet from A42
can bring some allies back.

Using both at once
improves the local neighborhood.

But while all of that is happening,
too much of the original committed population
is still disappearing during the bad pulse.

By the end of the pulse,
the favored side is still down
around only one quarter to three tenths
of the population.

So we have learned that
the problem is not simply:

keep enemies out;

or:

recruit allies faster.

The core itself
needs to behave more like a core.

The next clean question is:

can veteran cells reinforce one another
so a sufficiently dense cluster
survives as a unit
instead of each cell
fighting the pulse mostly on its own?

A41:
hold the line.

A42:
bring reinforcements.

Neither is enough.

A43 should test:

keep the core together.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
