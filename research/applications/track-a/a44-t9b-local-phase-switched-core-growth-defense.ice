TITLE: YGGDRASIL A44 / T9B — Local Phase-Switched Core Growth and Cooperative Defense
DATE: 2026-09-22
STATUS: PREREGISTERED PHASE-DEPENDENT LOCAL-SIGNALING EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T9B / APPLICATION-A
PARENT: A43 Cooperative Veteran-Core Reinforcement
DIAGNOSTIC PARENT: A43 6:2 vs 5:3 Residual Failure
BRANCH: dg1a-ar

A43 CLOSURE

acff6603ffb599a5115f521d5ade066189d28264.

A43 RESIDUAL DIAGNOSIS

8bd011fb024616bf5211a704b30dadd54e28d334.

A43 RESULT

MARGIN_REINFORCE produced
the first TRUE cooperative information gain.

It reduced biased-periodic oscillation:

D2:
96.88% -> 53.12%.

D3:
93.75% -> 46.88%.

It preserved:

0% balanced false-majority;

87.50-89.84% true reversal;

2-epoch old-majority loss.

It raised favored burst-end commitment
from about 25%
to about 42-45%.

But residual failure is concentrated
in 5:3 biased worlds.

6:2 contexts 44/45
are nearly solved.

5:3 contexts 46/47
remain largely oscillatory.

The 5:3 worlds enter challenge
with smaller cores,
lower own M,
and lower cooperative Q.

They survive adverse epoch 1
almost completely,
lose substantial structure on epoch 2,
and collapse on epoch 3.

A44 QUESTION

Can the same local core
use two already-demonstrated behaviors
at different local evidence phases?

When local evidence supports a commitment:

grow the core
through active margin-weighted recruitment.

When local evidence challenges a commitment:

hold the core together
through A43 margin-weighted cooperative reinforcement.

No cell may read
the hidden environment phase.

The mode switch must be inferred
only from current local evidence.

F44 FREEZE

Let the exact A44 implementation freeze commit be:

F44.

No real A44 world,
population outcome,
or scientific result
may be derived before F44 exists.

WORLD SHAPE

384 fresh post-F44 trials.

48 contexts x 8 replicas.

48 cells.
48 epochs.

Environmental families remain structurally identical
to A43.

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

Preserve A40-A43 exactly.

rho = 3/4.

At epoch start:

B_pre(i,t)
=
signed state carried from epoch t-1.

For C:

M_i = max(0,B_pre_i).

For S:

M_i = max(0,-B_pre_i).

Current local evidence
uses the already-frozen radius-12 densities:

L_C(i,t);

L_S(i,t).

LOCAL MODE

For a C-committed cell i:

SUPPORT
iff
L_C > L_S.

CHALLENGE
iff
L_S > L_C.

NEUTRAL
iff
L_C = L_S.

For an S-committed cell i:

SUPPORT
iff
L_S > L_C.

CHALLENGE
iff
L_C > L_S.

NEUTRAL
iff
L_C = L_S.

This local mode is diagnostic and causal.

It does not read:

context ID;
family ID;
future evidence;
true unsensed environment;
global majority;
or a centralized confidence score.

BASE COMMITTED-STATE LAW

Preserve A40:

PRESSURE_BASE
=
max(0,L_op-M_i).

p_stay
=
1/(1+(PRESSURE/(1/2))^3).

K = 1/2.
n = 3.

A43 COOPERATIVE FIELD

Use the exact A43 margin field.

Before any committed-cell defection,
freeze the currently committed C/S identities.

For C-committed i:

Q_margin_same(i)
=
(1/6)
*
sum over 0 < ring_distance(i,j) <= 3
of
1[state_j=C]
*
max(0,B_pre_j).

For S:

Q_margin_same(i)
=
(1/6)
*
sum over neighbors
1[state_j=S]
*
max(0,-B_pre_j).

Self is excluded.

Radius = 3.

No new gain exists.

CHALLENGE-GATED DEFENSE

In PHASE_SWITCH:

if committed cell i is in CHALLENGE mode:

PRESSURE
=
max(
0,
L_op
-
M_i
-
Q_margin_same(i)
).

If i is SUPPORT or NEUTRAL:

PRESSURE
=
PRESSURE_BASE.

All defection decisions
then use the unchanged Hill law.

Thus cooperative reinforcement
is activated only
when current local evidence
opposes the commitment.

SUPPORT-GATED ACTIVE RECRUITMENT

After committed-state defection,
freeze the surviving C/S core.

For each surviving committed emitter j,
use its beginning-of-epoch M_j.

A C survivor j emits
positive C recruitment signal
only if j's current local mode
is SUPPORT.

An S survivor emits
positive S recruitment signal
only if its local mode
is SUPPORT.

For eligible U cell i:

Q_C_support(i)
=
(1/6)
*
sum over surviving C neighbors j
within ring radius 3
of
1[j is SUPPORT]
*
max(0,B_pre_j).

Q_S_support(i)
=
(1/6)
*
sum over surviving S neighbors j
within radius 3
of
1[j is SUPPORT]
*
max(0,-B_pre_j).

Then:

lambda_C'
=
lambda_C
+
ETA * Q_C_support.

lambda_S'
=
lambda_S
+
ETA * Q_S_support.

lambda_H'
=
lambda_H.

Frozen:

ETA = 1/2.

No new recruitment gain exists.

NEUTRAL MODE

A neutral committed cell:

does not receive
cooperative A44 challenge reinforcement;

does not emit
A44 support recruitment.

It still follows
all ordinary A40/A34/A36 dynamics.

CONTROL MECHANISMS

A43_MARGIN_REINFORCE:

A43 margin cooperative reinforcement
is always available
through the pressure law,
exactly as frozen in A43.

A42_ACTIVE_MARGIN_RECRUIT:

A42 margin-weighted active recruitment
is always available
from surviving committed neighbors,
with BASE SUBTRACTIVE_SLOW defection.

ALWAYS_COMBINED:

A43 MARGIN_REINFORCE
plus
A42 ACTIVE_MARGIN_RECRUIT
operate every epoch,
without phase gating.

PHASE_SWITCH:

support-gated active recruitment;

challenge-gated margin reinforcement.

This comparison distinguishes:

component effects;

simple simultaneous composition;

and true local phase dependence.

ARMS

Exactly ten arms.

D2:

D2_BASE_SUBTRACTIVE_SLOW;
D2_MARGIN_REINFORCE;
D2_ACTIVE_MARGIN_RECRUIT;
D2_ALWAYS_COMBINED;
D2_PHASE_SWITCH.

D3:

D3_BASE_SUBTRACTIVE_SLOW;
D3_MARGIN_REINFORCE;
D3_ACTIVE_MARGIN_RECRUIT;
D3_ALWAYS_COMBINED;
D3_PHASE_SWITCH.

No OCCUPANCY reinforcement.

No OCCUPANCY exclusion.

No A41 field.

No MEDIUM arm.

All arms use rho = 3/4.

PRIMARY TARGET

Biased-periodic contexts:

44;
45;
46;
47.

Report each context separately.

A44 gives special diagnostic emphasis
to residual 5:3 contexts:

46;
47.

This does not change
the qualification population.

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

A44 must not solve
the 5:3 oscillator
by freezing an old majority
under balanced evidence.

PHASE-CLASSIFICATION MEASUREMENTS

For every committed cell epoch report:

state;
local mode:
SUPPORT / CHALLENGE / NEUTRAL;

own M;
Q_margin_same;
base pressure;
transformed pressure.

For every arm report:

fraction of committed-cell epochs
in each mode;

fraction of CHALLENGE epochs
with pressure reduction;

mean pressure reduction
during CHALLENGE;

mean pressure reduction
during SUPPORT.

For PHASE_SWITCH,
support-mode pressure reduction
must be exactly zero.

SUPPORT-PHASE CORE GROWTH

For biased contexts,
during each favored support interval report:

favored committed fraction
at support-interval start;

favored committed fraction
at support-interval end;

net favored committed growth;

number of favored U recruitments;

mean Q_support;

mean active recruitment increment.

For contexts 46/47,
compare PHASE_SWITCH directly with:

BASE;

MARGIN_REINFORCE;

ACTIVE_MARGIN_RECRUIT;

ALWAYS_COMBINED.

PRE-CHALLENGE READINESS

At every biased adverse-pulse onset report:

favored committed fraction;

mean favored-side M;

mean same-side Q_margin;

largest favored contiguous domain;

fraction of favored committed cells
with same-side neighbor count >=5.

This tests whether support-gated recruitment
actually improves the weak pre-pulse state
observed in 46/47.

ADVERSE-BURST SURVIVAL

Preserve A43:

onset-cohort persistence
after adverse epochs 1, 2, 3.

Stratify by:

neighbor count <=2;

3-4;

>=5.

For 5:3 contexts,
epoch-3 persistence
is a primary mechanism diagnostic.

COUNTER-PULSE TRAJECTORY

Preserve:

favored committed fraction at pulse onset;

minimum favored fraction;

burst-end favored fraction;

recovery latency to pre-pulse fraction,
or NEVER.

A44's central 5:3 mechanism test is:

does PHASE_SWITCH
enter the three-epoch challenge
with a stronger core

and

retain more of it
through adverse epoch 3?

TRUE REVERSAL COST

Preserve:

reversal acquisition;

old-majority loss latency;

new-majority acquisition;

old-side M at reversal onset;

M-to-zero latency;

signed-B zero-cross latency.

Additionally report:

fraction of old-side committed-cell epochs
classified SUPPORT / CHALLENGE / NEUTRAL
during the first four post-reversal epochs.

A healthy local switch
should move old-side cells
predominantly into CHALLENGE
under sustained reversed evidence.

This is the anti-oracle
and anti-stickiness diagnostic.

BALANCED-MODE DYNAMICS

For contexts 40-43 report:

fraction SUPPORT;

fraction CHALLENGE;

fraction NEUTRAL;

mean consecutive SUPPORT run length;

mean consecutive CHALLENGE run length.

This tests whether local phase switching
creates an accidental stable phase
under balanced periodic evidence.

PRIMARY POPULATION METRICS

For every arm report:

aggregate service;
harm rate;
overall oscillation;
biased-periodic oscillation;
5:3 biased oscillation;
6:2 biased oscillation;
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

A44 PHASE INFORMATION GAIN

TRUE iff at least one PHASE_SWITCH arm:

reduces 5:3 biased-periodic oscillation
versus paired A43 MARGIN_REINFORCE;

breaks at least 25%
of paired MARGIN_REINFORCE
5:3 oscillators;

raises pre-challenge favored committed fraction
in contexts 46/47
versus paired MARGIN_REINFORCE;

raises adverse-epoch-3 core persistence
in contexts 46/47
versus paired MARGIN_REINFORCE;

retains reversal acquisition >=80%;

retains aggregate service >=90%
of paired BASE;

and balanced false-majority <=10%.

A44 PHASE-SPECIFIC INFORMATION GAIN

TRUE iff PHASE_SWITCH
shows a benefit not explained
by simple simultaneous composition.

At least one D arm must satisfy:

5:3 biased-periodic oscillation
<
paired ALWAYS_COMBINED;

and

reversal acquisition
>= paired ALWAYS_COMBINED - 5 percentage points;

and

balanced false-majority
<=10%.

This is the preregistered test
of phase dependence itself.

A44 QUALIFICATION

D2_PHASE_SWITCH
or
D3_PHASE_SWITCH

is A44-QUALIFIED iff all are true:

1. overall oscillation <=5%;

2. biased-periodic oscillation <=10%;

3. 5:3 biased-periodic oscillation <=10%;

4. breaks at least 50%
   of paired BASE biased-periodic oscillators;

5. breaks at least 50%
   of paired A43 MARGIN_REINFORCE
   5:3 oscillators;

6. balanced false-majority <=10%;

7. false C dominance
   does not exceed paired BASE;

8. false S dominance
   does not exceed paired BASE;

9. reversal acquisition >=80%;

10. median old-majority loss <=4 epochs;

11. aggregate service >=90%
    of paired BASE;

12. recruitment remains nondegenerate;

13. pre-challenge favored fraction
    in 46/47 exceeds
    paired MARGIN_REINFORCE;

14. epoch-3 core persistence
    in 46/47 exceeds
    paired MARGIN_REINFORCE;

15. all integrity probes pass.

FAILURE ATTRIBUTION

If ALWAYS_COMBINED succeeds
but PHASE_SWITCH does not:

the two behaviors are useful,
but phase gating discards
needed signaling time.

If PHASE_SWITCH succeeds
and ALWAYS_COMBINED does not:

local timing of behavior
is causally important.

If both succeed similarly:

the combination matters,
but phase dependence
adds little.

If both improve pre-pulse core depth
but 5:3 epoch-3 collapse remains:

the remaining failure is
inside challenge endurance,
not support-phase growth.

If epoch-3 survival improves
but reversal becomes sticky:

challenge reinforcement
persists too strongly
under true environmental change.

If 46 improves but 47 does not,
or vice versa:

directional asymmetry
must be audited before any new mechanism.

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
cooperative/recruitment field radius = 3.

P12:
self excluded from cooperative Q.

P13:
ETA = 1/2.

P14:
pool normalization = 160.

P15:
A34 base recruitment unchanged.

P16:
A35 H hazards unchanged.

P17:
A36 niche mechanics unchanged.

P18:
D2 refractory = 2.

P19:
D3 refractory = 3.

P20:
rho exactly 3/4.

P21:
B starts at zero.

P22:
B updates every epoch for every cell.

P23:
local mode reads only current L_C/L_S
and current commitment.

P24:
no context/family/global-phase label
enters local mode.

P25:
no future environment enters mode.

P26:
MARGIN_REINFORCE control
matches A43.

P27:
ACTIVE_MARGIN_RECRUIT control
matches A42.

P28:
ALWAYS_COMBINED
is exact simultaneous composition.

P29:
PHASE_SWITCH recruitment
uses only SUPPORT emitters.

P30:
PHASE_SWITCH cooperative reduction
applies only to CHALLENGE targets.

P31:
NEUTRAL adds neither A44 behavior.

P32:
lambda_H unchanged.

P33:
no new gain exists.

P34:
no new radius exists.

P35:
no distance kernel exists.

P36:
no new threshold exists.

P37:
no A37 lineage state exists.

P38:
no centralized confidence scalar exists.

P39:
two complete primary sweeps byte-identical.

RESEARCH DISCIPLINE

Mechanical fake-world validation
must pass twice byte-identically
before F44.

F44 must exist
before fresh A44 worlds are derived.

The 384-world primary manifest
must be bound after F44
and before primary arm execution.

No post-result
rho,
radius,
gain,
kernel,
threshold,
mode rule,
arm,
qualification,
or world-family tuning.

PLAIN-SPEAK QUESTION

A43 found the first real cooperative core.

It survives a two-hit attack.

It usually dies on the third hit.

And the three-hit worlds
start the fight weaker.

A44 gives the core
two local behaviors.

When the evidence around a veteran
still supports its commitment:

recruit.

Use the calm period
to build a bigger,
deeper-supported core.

When the evidence turns against it:

reinforce.

Stop spending effort
on growth
and help the existing core
hold itself together.

No one tells the cell
what phase the world is in.

It decides from
what it can see locally.

The test is:

CAN THE CORE
BUILD WHILE CONDITIONS SUPPORT IT,

THEN SWITCH TO DEFENSE
FAST ENOUGH TO SURVIVE
THE THIRD HIT,

WITHOUT BECOMING
THE FROZEN OCCUPANCY CORE
THAT CAN NEVER CHANGE ITS MIND?

A41:
hold the line.

A42:
bring reinforcements.

A43:
keep the core together.

A44:
grow when supported;
defend when challenged.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F44 AMENDMENT 01 — ACTIVE-RECRUITMENT NORMALIZATION PARITY

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F44
AND BEFORE ANY A44 SCIENTIFIC OUTCOME.

ISSUE FOUND DURING IMPLEMENTATION AUDIT

The A44 preregistration wrote
support-gated Q_support with denominator 6,
while the exact frozen A42 ACTIVE_MARGIN_RECRUIT control
uses the existing radius-3 core_field normalization:

sum across offsets -3..+3
divided by 7.

For an eligible U target,
the center position contributes zero,
but it remains part of the frozen A42 denominator.

Leaving PHASE_SWITCH at /6
would give it a larger active-recruitment amplitude
than ACTIVE_MARGIN_RECRUIT and ALWAYS_COMBINED,
confounding phase timing with gain.

CORRECTION

For PHASE_SWITCH only,
replace the preregistered /6 support-field denominator
with the exact A42 active-margin normalization:

Q_C_support(i)
=
(1/7)
*
sum over offsets d=-3..+3
of
1[state_j=C]
*
1[j is SUPPORT]
*
max(0,B_pre_j).

Q_S_support(i)
=
(1/7)
*
sum over offsets d=-3..+3
of
1[state_j=S]
*
1[j is SUPPORT]
*
max(0,-B_pre_j).

Because target i is eligible U,
its own center contribution is necessarily zero.

No radius changes.
No gain changes.
ETA remains 1/2.
No new state exists.

RATIONALE

This amendment makes:

ACTIVE_MARGIN_RECRUIT;
ALWAYS_COMBINED;
PHASE_SWITCH

use the same active-recruitment amplitude.

Therefore the PHASE_SWITCH versus ALWAYS_COMBINED comparison
tests local phase gating,
not an accidental normalization difference.

All other A44 preregistered equations,
arms,
thresholds,
qualification rules,
and integrity probes remain unchanged.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
