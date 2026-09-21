TITLE: YGGDRASIL A36 / T8T — Spatially Cooperative Protected Hedge Niches
DATE: 2026-09-21
STATUS: PREREGISTERED SPATIAL BET-HEDGING EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8T / APPLICATION-A
PARENT: A35 Protected Bet-Hedging Third State
BRANCH: dg1a-ar

PURPOSE

A35 proved that a real protected H phenotype is:

selective under contradiction;
information-preserving;
compatible with reversal;
and able to increase no-majority behavior.

But isolated temporary H cells did not break
the persistent FAMILY-5 oscillatory attractor.

A35's closure therefore raised a structural question:

DOES UNCERTAINTY NEED
A COHERENT PROTECTED SUBPOPULATION
RATHER THAN INDEPENDENT TEMPORARY H CELLS?

A36 tests spatial cooperation only.

It does NOT increase a global hedge gain.
It does NOT change the environmental worlds.
It does NOT add a centralized uncertainty detector.

Instead,
nearby H cells can:

make H entry locally easier;

make H release locally harder;

or both.

The resulting protected niche must emerge
from cell-local neighborhood state.

FROZEN PARENT

A35 scientific closure:

ccd6878cd25161c9bf39054c7ed2a427761d68ca.

A35 packaging-only repair:

8059d76b42a7fd79e1241e8cfb885581abf75dbc.

A35 primary result:

no arm qualified;
no arm met A35_BET_HEDGE_INFORMATION_GAIN.

A35 isolated-H oscillation remained approximately:

15% to 17%.

A35 H selectivity remained approximately:

2.18x to 2.88x.

A35 showed that H itself is meaningful,
but not spatially persistent enough
to alter the macro-attractor.

PARENT ARM SELECTION FOR MECHANISM TEST

A36 carries forward only the P75L25
pool/local weighting for both:

D2;
D3.

This is NOT a production selection.

It is a preregistered mechanism-development choice.

Rationale:

within each refractory duration,
the P75L25 hedge arm produced
the strongest or near-strongest contradiction selectivity
and strong contradiction no-majority behavior.

A36 is testing spatial organization,
not re-sweeping A35's pool/local ratio.

FROZEN PARENT CONSTANTS

Population:

48 cells.

Epochs:

48.

Initial state:

12 C;
12 S;
24 U.

Pool decay:

3/4.

Local cross-inhibition:

R = 12;
n = 3;
K = 1/2.

Recruitment local radius:

3.

ETA:

1/2.

Pool normalization:

160.

A34 C/S suppression:

K_SUPP = 1/2;
N_SUPP = 3.

Pool/local recruitment weights:

3/4;
1/4.

Refractory durations:

D2;
D3.

A35 base hedge entry:

lambda_H_base
=
ETA
*
SUP_C
*
SUP_S.

A35 base H release:

lambda_release_base
=
ETA
*
(
1 - min(SUP_C,SUP_S)
).

A36 FREEZE

Let the exact A36 implementation freeze commit be:

F36.

No real A36 world,
niche event,
H cluster,
or scientific result
may be derived before F36 exists.

WORLD SHAPE

384 fresh post-F36 trials:

48 contexts
x
8 replicas.

48 cells.

48 epochs.

Environmental families remain structurally identical to A35:

0 stable C advantage;
1 stable S advantage;
2 spatial contradiction;
3 reversal C -> S;
4 reversal S -> C;
5 transient / oscillatory uncertainty.

All exact worlds are fresh and F36-derived.

LOCAL HEDGE-DENSITY FIELD

For cell i define:

H_local(i,t)

as the fraction of cells
in radius:

R_H = 3

around i
that are currently in state H.

Neighborhood includes i itself
when i is H.

H_local is local population state.

It is NOT confidence.

It is NOT computed from future outcome.

SPATIAL ENTRY REINFORCEMENT

When enabled:

lambda_H
=
lambda_H_base
*
(
1 + H_local
).

Thus:

no nearby H:
exact A35 hedge-entry hazard.

dense local H:
at most 2x A35 hedge-entry hazard.

There is no additional gain parameter.

SPATIAL RELEASE PROTECTION

When enabled:

lambda_release
=
lambda_release_base
*
(
1 - H_local
).

Thus:

isolated H:
release remains near A35 behavior.

locally dense H:
release becomes progressively slower.

A fully H-local neighborhood
has zero release hazard for that epoch.

No fixed niche lifetime exists.

ARMS

For D2:

D2_ISO:
exact A35 isolated-H reference.

D2_ENTRY:
entry reinforcement only.

D2_RETAIN:
release protection only.

D2_NICHE:
entry reinforcement
+
release protection.

For D3:

D3_ISO;
D3_ENTRY;
D3_RETAIN;
D3_NICHE

defined identically.

Exactly eight primary/comparator arms.

No post-result selection is permitted.

NO GLOBAL HEDGE COORDINATOR

A36 has no:

global H threshold;
global H conversion event;
global niche timer;
global H quorum gate.

Every H event remains cell-local.

SPATIAL NICHE METRICS

At every epoch,
identify contiguous H runs
on the periodic ring.

Report:

H cell count;

number of H clusters;

largest H cluster;

mean nonzero H cluster size;

fraction of H cells belonging
to a cluster of size >= 3;

fraction belonging
to a cluster of size >= 6.

TRACKED NICHE LIFETIME

A niche exists when
a contiguous H cluster has size >= 3.

Across epochs,
two niches are the same tracked niche
if their cell sets overlap by at least one cell.

Report:

niche birth count;

niche death count;

mean niche lifetime;

median niche lifetime;

maximum niche lifetime;

number surviving >= 4 epochs;

number surviving >= 8 epochs.

These are external measurements only.

They do not alter controller behavior.

CONTRADICTION COHERENCE

During high-high contradiction:

C_pool >= 48
AND
S_pool >= 48,

report:

mean H occupancy;

mean largest H cluster;

fraction of contradiction epochs
with an H cluster >= 3;

fraction with H cluster >= 6;

fraction with no C/S population majority.

Outside contradiction report same.

Define spatial niche selectivity:

rate of contradiction epochs with H cluster >=3
/
rate of noncontradiction epochs with H cluster >=3.

FAMILY-5 RETEST

For ENTRY / RETAIN / NICHE
versus its exact ISO duration reference report:

ISO FAMILY-5 oscillators;

broken oscillators;

new oscillators;

remaining oscillators.

Also report:

mean largest H cluster;

mean H occupancy;

niche lifetime

within FAMILY 5 only.

REVERSAL COST

For FAMILY 3 / 4 report:

old-majority loss latency;

new-majority acquisition;

failure to acquire new majority;

peak H occupancy around reversal;

maximum H cluster around reversal.

This tests whether spatial H domains
become too sticky during a real regime change.

ATTRACTOR QUALITY

Report:

false C dominance
on S-favoring worlds;

false S dominance
on C-favoring worlds;

final no-majority rate.

PRIMARY QUALIFICATION

D2_NICHE or D3_NICHE
is SPATIAL-HEDGE-QUALIFIED iff all are true:

1. oscillatory fraction <= 0.05;

2. oscillatory fraction < paired ISO;

3. at least 50% of paired ISO
   FAMILY-5 oscillators are broken;

4. contradiction no-majority fraction >= 0.90;

5. spatial niche selectivity >= 2.0;

6. at least 50% of contradiction epochs
   contain an H cluster of size >= 3;

7. false C dominance <= 0.05
   among S-favoring worlds;

8. false S dominance <= 0.05
   among C-favoring worlds;

9. reversal acquisition >= 0.80;

10. aggregate service
    >= 90%
    of paired ISO;

11. all integrity probes pass.

A36_SPATIAL_HEDGE_INFORMATION_GAIN

TRUE iff at least one ENTRY / RETAIN / NICHE arm:

reduces oscillation versus paired ISO;

breaks at least 25%
of paired ISO FAMILY-5 oscillators;

increases mean largest H cluster
during contradiction;

has spatial niche selectivity >= 2;

retains reversal acquisition >= 0.80;

and retains >= 90% paired-ISO service.

This is descriptive only.

No production mechanism is selected.

MECHANISM ATTRIBUTION

If ENTRY helps but RETAIN does not:

niche nucleation / recruitment is the useful mechanism.

If RETAIN helps but ENTRY does not:

persistence of already-hedged cells is the useful mechanism.

If only NICHE helps:

the spatial phenotype requires
both nucleation and persistence.

If all three fail despite larger H clusters:

spatial coherence alone is insufficient.

If niches suppress oscillation
but destroy reversal:

the niche becomes pathological persistence.

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
A35 pulse ecology unchanged.

P7:
pool decay = 3/4.

P8:
A30 local inhibition R/n/K = 12/3/1/2.

P9:
A33 recruitment radius = 3.

P10:
ETA = 1/2.

P11:
pool normalization = 160.

P12:
A34 suppression K/n = 1/2 / 3.

P13:
pool/local weighting fixed at 75/25.

P14:
D2 exactly 2 refractory epochs.

P15:
D3 exactly 3.

P16:
base H entry exactly ETA*SUP_C*SUP_S.

P17:
base H release exactly ETA*(1-min(SUP_C,SUP_S)).

P18:
H neighborhood radius exactly 3.

P19:
ENTRY multiplier exactly 1 + H_local.

P20:
RETAIN multiplier exactly 1 - H_local.

P21:
ISO has neither spatial modifier.

P22:
ENTRY has only entry modifier.

P23:
RETAIN has only release modifier.

P24:
NICHE has both.

P25:
H still emits base pulse only.

P26:
H still cannot transition directly to C or S.

P27:
one stochastic event cannot change another cell.

P28:
no future environment enters current transition.

P29:
no centralized confidence scalar exists.

P30:
two complete primary sweeps byte-identical.

NEGATIVE / LIMIT CONTROLS

N1:
D2_ISO.

N2:
D3_ISO.

N3:
post-result H-radius tuning invalid.

N4:
post-result reinforcement-gain tuning invalid.

N5:
post-result release-law tuning invalid.

N6:
changing pool/local weighting invalid.

N7:
changing refractory duration invalid.

INTERPRETATION

A36 is not asking whether
cells should hedge MORE.

It asks whether hedging must be
SPATIALLY SELF-SUPPORTING.

If a few isolated cells temporarily opt out,
the rest of the population may still oscillate.

A coherent protected neighborhood
could persist through several contradictory cycles
and preserve a stable unresolved subpopulation.

If that changes the oscillator attractor,
uncertainty has acquired spatial organization.

If not,
the next hypothesis is lineage persistence:
uncertainty may need to survive through cell replacement /
developmental inheritance rather than neighborhood cooperation alone.

PLAIN-SPEAK QUESTION

A35 gave individual cells permission to say:

"I AM NOT CHOOSING YET."

That helped,
but each cell was mostly on its own.

A36 asks what happens
when uncertain cells can support nearby uncertain cells.

One hedged cell
can make it a little easier
for a neighbor to hedge.

A group of hedged cells
can make it a little harder
for members of that group to leave too quickly.

Nothing tells the whole population:

"be uncertain."

A protected uncertain neighborhood
has to form from local interactions.

The question is:

DOES UNCERTAINTY BECOME MORE USEFUL
WHEN IT CAN FORM A REAL NICHE
INSTEAD OF APPEARING AS SCATTERED TEMPORARY CELLS?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
