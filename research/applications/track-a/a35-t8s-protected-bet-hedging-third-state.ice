TITLE: YGGDRASIL A35 / T8S — Protected Bet-Hedging as a Third Local Recruitment State
DATE: 2026-09-21
STATUS: PREREGISTERED BET-HEDGING MECHANISM EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8S / APPLICATION-A
PARENT: A34 Contradiction-Suppressed Independent Recruitment
BRANCH: dg1a-ar

PURPOSE

A34 showed that smooth multiplicative opposition suppression
is selective but does not create a true distributed deadband.

Even after suppression,
approximately 89-94% of contradictory high-high epochs
still contained recruitment activity.

The distributed-systems reason is structural:

small nonzero per-cell hazards
multiplied across many independently ticking cells
still create persistent population activity.

A35 tests a qualitatively different response to contradiction:

BET-HEDGING AS A REAL LOCAL CELL STATE.

Eligible unresolved cells receive a third competing hazard:

C commitment;

S commitment;

or

H protected unresolved / hedged state.

No centralized confidence score exists.
No global uncertainty gate exists.

A35 asks whether irreducible contradictory evidence
is better represented as population diversification
than as endlessly slowed binary commitment.

SCIENTIFIC MOTIVATION

Microbial bet-hedging and stochastic phenotype switching
can preserve heterogeneous subpopulations
when environments fluctuate
or available information is insufficient for reliable prediction.

Quorum-regulated populations can also remain heterogeneous
rather than converging uniformly.

A35 uses these as design inspirations only.

Its exact three-hazard equations
are synthetic Yggdrasil hypotheses.

FROZEN PARENT

A34 closure:

858c84498f5264bf8ab80975ea038a40d8c03be4.

A35 FREEZE

Let the exact A35 implementation freeze commit be:

F35.

No real A35 world,
hedging event,
hedged-state occupancy,
or scientific result
may be derived before F35 exists.

WORLD SHAPE — UNCHANGED

384 fresh post-F35 trials:

48 contexts
x
8 replicas.

48 cells.

48 epochs.

Initial state:

12 C;
12 S;
24 U.

Environmental families remain structurally identical to A34:

0 stable C advantage;
1 stable S advantage;
2 spatial contradiction;
3 reversal C -> S;
4 reversal S -> C;
5 transient / oscillatory uncertainty.

PULSE ECOLOGY — UNCHANGED

Base sensed pulses,
committed feedback pulses,
3/4 pool decay,
A30 local cross-inhibition,
A31 D2/D3 refractory memory,
and A33 independent stochastic recruitment timing
remain unchanged.

A34 OPPOSITION-SUPPRESSED C/S HAZARDS — UNCHANGED

For eligible U cell i:

SUP_C
=
w_pool * P_C
+
w_local * L_C.

SUP_S symmetrically.

OPP_C
=
w_pool * P_S
+
w_local * L_S.

OPP_S symmetrically.

A34 suppression:

G(x)
=
1
/
(1 + (x / 1/2)^3).

Candidate hazard:

lambda_C
=
ETA
*
SUP_C
*
G(OPP_C).

Stale hazard:

lambda_S
=
ETA
*
SUP_S
*
G(OPP_S).

ETA:

1/2.

Weights remain:

75/25;
50/50;
25/75.

Both D2 and D3 remain.

NEW HEDGED STATE

Add one cell state:

H.

H means:

protected unresolved / bet-hedged.

An H cell:

is not C committed;

is not S committed;

cannot be recruited directly to C or S;

continues sensing its environment;

continues contributing its base C/S pulse;

emits no committed positive-feedback pulse.

Thus H preserves information flow
while withholding commitment.

THIRD COMPETING HAZARD

For every eligible U cell:

lambda_H
=
ETA
*
SUP_C
*
SUP_S.

No new gain parameter is introduced.

The existing ETA = 1/2
sets the scale.

The product is a coincidence signal.

If one side is weak:

lambda_H is small.

If both sides are strong:

lambda_H increases.

Thus contradiction generates
a third local action
without a global high-high threshold.

THREE-WAY COMPETING EVENT

For eligible U cell:

lambda_total
=
lambda_C
+
lambda_S
+
lambda_H.

Event probability in one epoch:

p_fire
=
1 - exp(-lambda_total).

One independent deterministic draw
decides whether an event occurs.

If it occurs,
a second independent deterministic draw
chooses among:

C;
S;
H

in proportion to their hazards.

One cell's event
cannot trigger another cell's event.

HEDGE RELEASE

An H cell has its own independent release hazard:

lambda_release
=
ETA
*
(
1 - min(SUP_C,SUP_S)
).

Interpretation:

when both candidate and stale support remain strong,
H persists longer.

When either side's support weakens,
H becomes easier to release.

If release event fires:

H -> U.

H cannot transition directly to C or S.

It must return to U
and compete again on a later epoch.

No fixed hedge timer exists.

The hedge lifetime is therefore endogenous
to the local support fields.

PRIMARY HEDGE ARMS

D2_H_P75L25.
D2_H_P50L50.
D2_H_P25L75.

D3_H_P75L25.
D3_H_P50L50.
D3_H_P25L75.

PAIRED A34 REFERENCES

D2_R_P75L25.
D2_R_P50L50.
D2_R_P25L75.

D3_R_P75L25.
D3_R_P50L50.
D3_R_P25L75.

Reference arms use exact A34 suppressed C/S hazards
with no H state / hazard.

This isolates the contribution of the third local phenotype.

HEDGE-SPECIFIC METRICS

Report:

U -> H entry count;

H -> U release count;

mean H occupancy;

peak H occupancy;

mean H dwell time;

median H dwell time;

fraction of cells ever entering H;

fraction of trials ever using H.

CONTRADICTION SELECTIVITY

For epochs where:

C_pool >= 48
AND
S_pool >= 48,

report:

H entries;

mean H occupancy fraction;

fraction of contradictory epochs
with at least one H cell;

fraction with no population majority.

Outside contradiction report the same.

Define hedge selectivity ratio:

H entry rate per eligible cell during contradiction
/
H entry rate per eligible cell outside contradiction.

A35 should not merely move cells into H everywhere.

POPULATION DIVERSIFICATION

For every epoch report population fractions:

C;
S;
U;
H;
FC;
FS.

Report Shannon state entropy
across:

C;
S;
U/H combined uncertainty

as external measurement only.

Entropy is not used by the controller.

FAMILY-5 RETEST

For every hedge arm
versus its paired A34 reference report:

paired-reference FAMILY-5 oscillators;

broken oscillators;

new oscillators;

remaining oscillators.

Also report:

mean H occupancy
specifically within FAMILY 5.

REVERSAL COST

For FAMILY 3 / 4 report:

old-majority loss latency;

new-majority acquisition;

trials never acquiring new majority;

H occupancy around the reversal.

This tests whether hedging
becomes excessively indecisive
when the environment truly changes direction.

ATTRACTOR QUALITY

Report:

false C dominance
on S-favoring worlds;

false S dominance
on C-favoring worlds;

final no-majority rate.

PRIMARY QUALIFICATION

A primary hedge arm is BET-HEDGE-QUALIFIED iff all are true:

1. oscillatory fraction <= 0.05;

2. oscillatory fraction
   < paired A34 reference;

3. at least 50% of paired-reference
   FAMILY-5 oscillatory trials are broken;

4. contradiction no-majority fraction >= 0.90;

5. hedge selectivity ratio >= 2.0;

6. median directional coordination
   among C/S recruitment episodes >= 0.80;

7. false C dominance <= 0.05
   among S-favoring worlds;

8. false S dominance <= 0.05
   among C-favoring worlds;

9. reversal acquisition >= 0.80;

10. aggregate service
    >= 90%
    of paired A34 reference;

11. all integrity probes pass.

A35_BET_HEDGE_INFORMATION_GAIN

TRUE iff at least one primary hedge arm:

reduces oscillation;

breaks at least 25%
of paired-reference FAMILY-5 oscillators;

has hedge selectivity >= 2;

increases contradiction no-majority fraction;

retains >= 80% directional coordination;

and retains >= 90% paired-reference service.

This is descriptive only.

No production mechanism is selected.

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
pool decay = 3/4.

P7:
local inhibition R/n/K = 12/3/1/2.

P8:
recruitment radius = 3.

P9:
ETA = 1/2.

P10:
pool normalization = 160.

P11:
D2 = 2 refractory epochs.

P12:
D3 = 3 refractory epochs.

P13:
weights exactly 75/25, 50/50, 25/75.

P14:
A34 C/S suppression K/n = 1/2 / 3.

P15:
lambda_H exactly ETA * SUP_C * SUP_S.

P16:
H release exactly ETA * (1 - min(SUP_C,SUP_S)).

P17:
H emits base pulse only.

P18:
H emits no committed feedback pulse.

P19:
H cannot transition directly to C or S.

P20:
H must release to U before later commitment.

P21:
FC / FS remain recruitment-ineligible.

P22:
one stochastic event cannot change another cell.

P23:
paired references contain no H state.

P24:
no future environment enters current transition.

P25:
no centralized confidence scalar exists.

P26:
two complete primary sweeps byte-identical.

NEGATIVE / LIMIT CONTROLS

N1:
paired A34 suppressed reference.

N2:
post-result hedge-gain tuning invalid.

N3:
post-result release-law tuning invalid.

N4:
changing A34 suppression invalid.

N5:
changing A30 local inhibition invalid.

N6:
changing A31 refractory durations invalid.

INTERPRETATION

If H is selectively occupied during contradiction
and breaks oscillatory worlds,
bet-hedging adds information beyond smooth hazard suppression.

If H fills under all environments,
the product signal is not selective enough.

If H stops oscillation but destroys reversal acquisition,
the protected state is too sticky.

If H improves contradiction handling
but false dominance remains high,
future work must target committed-state persistence.

If H fails entirely,
the remaining oscillatory family may require
spatially distinct subpopulations
rather than a generic protected unresolved phenotype.

PLAIN-SPEAK QUESTION

A34 told each cell:

"if both sides disagree with you,
slow down."

That was not enough.

A35 gives the cell a real third choice:

CANDIDATE.

STALE.

OR:

"I AM NOT CHOOSING YET."

When both sides are strong,
a cell can enter a protected uncertain state.

It keeps listening.

It keeps contributing what it senses.

But it temporarily stops trying to join either camp.

When the conflict weakens,
it comes back out
and can reconsider.

So uncertainty is no longer:

a smaller number;

a slower clock;

or a central label.

It becomes:

A REAL PHENOTYPE IN THE POPULATION.

A35 asks:

CAN YGGDRASIL HEDGE ITS BETS
WHEN THE ENVIRONMENT GENUINELY DOES NOT SUPPORT
ONE CLEAN DECISION?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
