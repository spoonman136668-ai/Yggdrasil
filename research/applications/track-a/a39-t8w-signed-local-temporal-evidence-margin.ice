TITLE: YGGDRASIL A39 / T8W — Signed Local Temporal Evidence Margin
DATE: 2026-09-21
STATUS: PREREGISTERED SIGNED-TEMPORAL-HYSTERESIS EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8W / APPLICATION-A
PARENT: A38 Heterogeneous Temporal Response Timescales
MECHANISM PARENT: A36 Spatially Cooperative Protected Hedge Niches
BRANCH: dg1a-ar

PURPOSE

A38 localized the remaining temporal failure more precisely.

Slower opposition-only integration
reduces reaction to the first adverse epoch,
but repeated two- and three-epoch counter-pulses
still drive substantial committed-cell defection.

The strongest A38 arm:

D3 SLOW

reduced overall oscillation to:

10.94%.

But biased-periodic oscillation remained:

25 / 32
=
78.13%.

The key limitation is structural:

A38 remembers recent OPPOSITION.

It does not preserve
the accumulated SUPPORT
that preceded that opposition.

A39 tests:

SIGNED LOCAL TEMPORAL EVIDENCE MARGIN.

A long period of same-side support
builds local state.

Opposing evidence must first consume that state
before committed-cell retreat becomes likely.

No centralized confidence score exists.

FROZEN PARENTS

A36 closure:

fc1e79598729a1cb755759ab5e668c58ab23c0ec.

A38 closure:

07270ec44cbb6748227bb2a321f04cc8e7fb273d.

A38 TARGET DIAGNOSTIC

Biased-periodic contexts:

44;
45;
46;
47.

A38 D3 SLOW oscillators:

context 44:
8 / 8.

context 45:
8 / 8.

context 46:
6 / 8.

context 47:
3 / 8.

D3 SLOW adverse-burst defection:

after first adverse epoch:
14.39%.

after second:
32.21%.

after third:
46.01%.

Therefore simply increasing rho
is not the justified next mechanism.

A39 FREEZE

Let the exact A39 implementation freeze commit be:

F39.

No real A39 world,
signed-margin state,
defection,
or scientific result
may be derived before F39 exists.

WORLD SHAPE

384 fresh post-F39 trials:

48 contexts
x
8 replicas.

48 cells.

48 epochs.

Environmental families remain structurally identical
to A38.

No developmental turnover exists.

PARENT ORGANISM

A39 uses the full A36 NICHE organism:

A29 pulse ecology;

A30 local cross-inhibition architecture;

A31 refractory memory;

A34 contradiction-suppressed independent recruitment;

A35 H protected uncertainty phenotype;

A36 spatial H entry reinforcement
and release protection.

Both:

D2;
D3

refractory durations remain.

No A37 lineage mark exists.

LOCAL SIGNED EVIDENCE

For cell i at epoch t define:

L_C(i,t)

as the fraction of cells
within frozen local radius 12
that emitted at least one C pulse.

L_S(i,t)

symmetrically.

Define instantaneous signed local evidence:

E(i,t)
=
L_C(i,t)
-
L_S(i,t).

Range:

-1 <= E <= 1.

Every cell carries one signed temporal margin:

B(i,t).

For memory coefficient rho:

B(i,t)
=
rho * B(i,t-1)
+
(1-rho) * E(i,t).

Initial margin:

B(i,-1) = 0.

The margin updates:

every epoch;

for every cell;

regardless of current phenotype.

Thus a cell can carry
recent local evidence history
across phenotype transitions.

B is local dynamical state.

It is NOT:

a probability;

a confidence score;

or a global statistic.

STATE-ALIGNED OPPOSING PRESSURE

For a C-committed cell:

PRESSURE_C
=
max(0, -B).

For an S-committed cell:

PRESSURE_S
=
max(0, B).

If the signed margin still favors
the current committed side:

opposing pressure is zero.

If the signed margin reverses sign:

pressure grows continuously
with the magnitude of that reversal.

DEFECTION LAW

The A30 Hill persistence law remains:

p_stay
=
1
/
(
1 + (PRESSURE / K)^3
).

K remains:

1/2.

No new defection threshold
or gain parameter is introduced.

This means:

support builds a positive margin;

opposition spends it;

and defection begins only
after accumulated local evidence
actually favors the other side.

REFERENCE — ONE-SIDED OPPOSITION TRACE

A39 carries forward
the exact A38 SLOW trace as reference:

rho = 3/4.

For C:

O_C
=
rho * O_C_prev
+
(1-rho) * L_S.

For S symmetrically.

p_stay uses O
through the same Hill law.

This reference is named:

OPP_SLOW.

SIGNED TEMPORAL ARMS

SIGNED_MEDIUM:

rho = 1/2.

SIGNED_SLOW:

rho = 3/4.

No additional rho values are tested.

SIGNED_FAST is not a primary arm
because rho = 0
reduces to instantaneous local signed evidence
and does not test temporal credit.

ARMS

D2_OPP_SLOW.
D2_SIGNED_MEDIUM.
D2_SIGNED_SLOW.

D3_OPP_SLOW.
D3_SIGNED_MEDIUM.
D3_SIGNED_SLOW.

Exactly six arms.

The primary mechanism candidate is:

SIGNED_SLOW.

SIGNED_MEDIUM is a preregistered timescale control,
not a post-result fallback.

SUPPORT-CREDIT METRICS

For every committed cell and every biased-periodic counter-pulse:

record B at:

one epoch before pulse onset;

after adverse epoch 1;

after adverse epoch 2;

after adverse epoch 3
when present.

Report by arm:

median pre-pulse margin;

median margin after 1/2/3 adverse epochs;

fraction still same-sign after 1/2/3;

fraction crossing zero after 1/2/3.

This directly measures
whether prior support survives
short counter-pulses.

DEFECTION PHASE

Report committed-cell defection fraction
after adverse epoch:

1;
2;
3

for biased-periodic contexts.

Also report:

margin-crossed-zero rate

versus:

actual defection rate.

BIASED-PERIODIC PRIMARY TARGET

Contexts:

44;
45;
46;
47.

Report:

oscillation per context;

overall biased-periodic oscillation;

majority-change count;

service.

BALANCED-PERIODIC CONTROL

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

A39 must not solve biased pulse chasing
by forcing one side
under genuinely balanced evidence.

TRUE REVERSAL COST

For FAMILY 3 / 4 report:

old-majority loss latency;

new-majority acquisition;

failure to reverse;

signed-margin zero-crossing latency
after environmental reversal.

This measures the cost
of accumulated support credit
when the world genuinely changes.

MARGIN SATURATION / STICKINESS

Report:

fraction of committed-cell epochs
with:

|B| >= 0.75.

Report:

trials where old majority
survives > 4 epochs after true reversal.

This detects pathological inertia.

PRIMARY POPULATION METRICS

For every arm report:

aggregate service;

harm rate;

oscillation;

biased-periodic oscillation;

balanced-periodic false-majority;

false C dominance;

false S dominance;

contradiction no-majority;

reversal acquisition;

median old-majority loss;

directional coordination;

H occupancy;

niche prevalence.

PRIMARY QUALIFICATION

D2_SIGNED_SLOW or D3_SIGNED_SLOW
is SIGNED-MARGIN-QUALIFIED iff all are true:

1. overall oscillatory fraction <= 0.05;

2. biased-periodic oscillatory fraction <= 0.10;

3. oscillation < paired OPP_SLOW;

4. at least 50%
   of paired OPP_SLOW biased-periodic oscillators
   are broken;

5. balanced-periodic false-majority <= 0.10;

6. false C dominance <= 0.05
   among S-favoring worlds;

7. false S dominance <= 0.05
   among C-favoring worlds;

8. reversal acquisition >= 0.80;

9. median old-majority loss latency
   on true reversals <= 4 epochs;

10. aggregate service
    >= 90%
    of paired OPP_SLOW;

11. all integrity probes pass.

A39_SIGNED_MARGIN_INFORMATION_GAIN

TRUE iff at least one SIGNED arm:

reduces overall oscillation
versus paired OPP_SLOW;

breaks at least 25%
of paired OPP_SLOW biased-periodic oscillators;

reduces adverse-epoch-2 defection
relative to OPP_SLOW;

retains reversal acquisition >= 0.80;

and retains >= 90%
paired-reference service.

This is descriptive only.

MECHANISM ATTRIBUTION

If SIGNED_MEDIUM succeeds
but SIGNED_SLOW becomes sticky:

signed balance is useful
but long memory is excessive.

If SIGNED_SLOW succeeds:

support credit earns
a local temporal-hysteresis role.

If both signed arms reduce pulse chasing
but destroy true reversal:

support credit is too inertial
as formulated.

If both fail while preserving margins:

the remaining oscillator
is not caused by committed-cell retreat alone.

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
A33 recruitment radius = 3.

P12:
ETA = 1/2.

P13:
pool normalization = 160.

P14:
A34 suppression unchanged.

P15:
A35 H hazards unchanged.

P16:
A36 niche mechanics unchanged.

P17:
D2 refractory = 2.

P18:
D3 refractory = 3.

P19:
OPP_SLOW rho = 3/4.

P20:
SIGNED_MEDIUM rho = 1/2.

P21:
SIGNED_SLOW rho = 3/4.

P22:
signed E exactly L_C - L_S.

P23:
B starts at zero.

P24:
B updates every epoch for every cell.

P25:
C pressure exactly max(0,-B).

P26:
S pressure exactly max(0,B).

P27:
B affects committed-state defection only.

P28:
recruitment does not read B.

P29:
H entry / release do not read B.

P30:
no A37 lineage state exists.

P31:
no future environment enters B.

P32:
no centralized confidence scalar exists.

P33:
two complete primary sweeps byte-identical.

NEGATIVE / LIMIT CONTROLS

N1:
OPP_SLOW exact one-sided A38 reference.

N2:
SIGNED_MEDIUM.

N3:
post-result rho tuning invalid.

N4:
post-result pressure transform tuning invalid.

N5:
post-result support / opposition weighting invalid.

N6:
changing H / recruitment mechanics invalid.

INTERPRETATION

A38 showed that
remembering opposition longer
is not enough.

A39 tests whether
the cell must remember
which side has actually been winning.

A signed local state
naturally creates temporal hysteresis.

The cell does not ask:

"how confident am I?"

Its local internal state
simply remains on one side of zero
until opposing evidence
has accumulated enough
to reverse it.

PLAIN-SPEAK QUESTION

A38 gave cells
a slower opposition meter.

A39 gives them
a balance.

Support puts weight
on one side.

Opposition puts weight
on the other.

If a cell has been supported
for a long time,
a short bad burst
should spend some of that support
without instantly changing its mind.

If the world really changes,
opposition keeps accumulating
until the balance actually flips.

The question is:

CAN YGGDRASIL REMEMBER
NOT JUST THAT OPPOSITION HAPPENED,

BUT WHICH SIDE
HAS BEEN WINNING OVER TIME?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-IMPLEMENTATION CLARIFICATION 01 — REVERSAL MARGIN CROSSING

DATE:
2026-09-21.

STATUS:
BOUND BEFORE IMPLEMENTATION FREEZE
AND BEFORE ANY REAL F39-DERIVED WORLD EXISTS.

REVERSAL COHORT

On a FAMILY 3 / 4 true reversal,
capture the identities of cells
that are committed to the OLD environmental side
at the start of the reversal epoch,
before that epoch's defection decisions.

For each captured cell in a SIGNED arm,
record the first epoch at which
its signed margin crosses to the new side:

old C:
B <= 0.

old S:
B >= 0.

Per-trial signed-margin zero-crossing latency
is the median latency
among captured cells that cross.

If none cross before trial end:

NEVER.

This diagnostic is external measurement only.

Newly recruited cells after reversal
cannot enter the crossing cohort.

No controller rule,
rho,
pressure transform,
qualification threshold,
or information-gain criterion changes.

No F39 exists yet.
