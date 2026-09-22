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


PRE-FREEZE CLARIFICATION 01 — TEMPORAL NICHE CAUSALITY AND TRACKING

DATE:
2026-09-21.

STATUS:
BOUND BEFORE F36
AND BEFORE ANY REAL F36-DERIVED WORLD EXISTS.

SAME-EPOCH H CAUSALITY

All A36 H-neighborhood modifiers are computed from
the H population present at the start of the cell-transition phase
for that epoch.

A U -> H transition occurring during epoch t
does NOT alter another cell's H_local value
until epoch t+1.

Likewise,
an H release during epoch t
does not retroactively alter another H cell's
release modifier during the same transition phase.

This prevents order-dependent same-epoch H cascades.

NICHE IDENTITY TRACKING

A measured niche is a contiguous periodic-ring H cluster
of size >= 3.

Across adjacent epochs,
a prior niche and current niche
are treated as the same tracked niche
when their cell sets overlap by at least one identity.

When multiple possible matches exist,
matching is deterministic:

largest overlap first;

then stable prior-cluster order;

then stable current-cluster order.

Each cluster may be matched at most once per epoch.

This niche tracking is external measurement only.
It cannot affect cell transitions.

No scientific rule,
qualification threshold,
or controller behavior changes.

No real A36 world exists.


PRE-RUN IMPLEMENTATION FREEZE 01 — A36 SPATIALLY COOPERATIVE PROTECTED HEDGE NICHES

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F36-DERIVED WORLD,
NICHE EVENT,
H CLUSTER,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

e3be3d20e1acb09cdff3b11538f513d650227b78.

SOURCE BUNDLE

Loader:

research/applications/track-a/a36_t8t_spatial_hedge_niches_v1.py

Loader Git blob:

f537b5060fa5f1947cfb4e19cf03d2e9adff5ef6.

Payload:

research/applications/track-a/a36_t8t_spatial_hedge_niches_v1.py.gz

Payload Git blob:

851867455ec978ef679489280bfc8697bade5e55.

Decompressed source SHA-256:

5ff16100fc817a650a74e74d574ee9361de824418c38323c03192493359cd1d3.

Decompressed source bytes:

25158.

Deterministic gzip SHA-256:

216a54bb8e5ed18ae9436d0e07f4e29252d8563f5950ffb75ce478faec34f049.

Compressed payload bytes:

7382.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F36-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized output SHA-256:

45d9a43c5da10523f53612836f96786b17e671f824766f205c3bc296047bdf52.

Mechanical world-manifest SHA-256:

a96fd99a2b1eefb9bcd948e51f1c21ab846478546dbc8ece740f25ef9a33953e.

All P1-P30 integrity probes:

PASS.

No NICHE arm mechanically qualified.

A36_SPATIAL_HEDGE_INFORMATION_GAIN:

FALSE

in the developer-only fake world.

MECHANICAL D2 ISO

oscillation:

13.80%.

contradiction no-majority:

89.98%.

contradiction cluster>=3 fraction:

14.1%.

mean niche lifetime:

1.789 epochs.

MECHANICAL D2 NICHE

oscillation:

14.32%.

contradiction no-majority:

92.52%.

contradiction cluster>=3 fraction:

38.0%.

mean niche lifetime:

3.715 epochs.

Thus combined local entry reinforcement
and release protection materially increased
spatial H coherence and persistence
without mechanically breaking the oscillator family.

MECHANICAL D3 ISO

oscillation:

14.58%.

contradiction no-majority:

92.20%.

contradiction cluster>=3 fraction:

9.5%.

mean niche lifetime:

1.817 epochs.

MECHANICAL D3 RETAIN

oscillation:

13.54%.

contradiction no-majority:

93.79%.

contradiction cluster>=3 fraction:

22.8%.

mean niche lifetime:

3.343 epochs.

paired ISO FAMILY-5 oscillators broken:

5 / 33.

This was the strongest mechanical hint,
but remained below the frozen 25% information-gain requirement.

MECHANICAL D3 NICHE

oscillation:

14.84%.

contradiction no-majority:

94.86%.

contradiction cluster>=3 fraction:

32.3%.

mean niche lifetime:

3.688 epochs.

paired ISO FAMILY-5 oscillators broken:

2 / 33.

MECHANICAL INTERPRETATION

Spatial H cooperation is nontrivial.

It creates:

larger H clusters;
longer-lived H niches;
and more no-majority contradiction epochs.

But the mechanical sweep does not pre-prove
that spatial coherence alters
the persistent oscillatory attractor.

Release protection alone,
especially under D3,
is the strongest mechanistic hint.

No H radius,
entry multiplier,
release multiplier,
refractory duration,
qualification rule,
or information-gain rule
is changed in response.

This is NON-SCIENTIFIC mechanical evidence only.

REAL A36 STATUS

No real F36-derived world exists.

No real H niche outcome exists.

No real A36 primary result exists.

Let the resulting commit SHA be:

F36.

After F36 exists:

1. derive exactly 384 fresh worlds from F36;
2. bind the complete world-manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report ISO / ENTRY / RETAIN / NICHE
   for both D2 and D3 without post-result selection.

NO POST-RESULT H-RADIUS TUNING.
NO POST-RESULT ENTRY-GAIN TUNING.
NO POST-RESULT RELEASE-LAW TUNING.
NO POST-RESULT REFRACTORY CHANGE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A36 SPATIALLY COOPERATIVE PROTECTED HEDGE NICHES

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A36 ARM EXECUTION,
H NICHE EVENT,
OR SCIENTIFIC OUTCOME.

F36:

f8f83007bc9bf5ff64a338ebe3540195086dd593.

FROZEN SOURCE SHA-256:

5ff16100fc817a650a74e74d574ee9361de824418c38323c03192493359cd1d3.

FROZEN GZIP SHA-256:

216a54bb8e5ed18ae9436d0e07f4e29252d8563f5950ffb75ce478faec34f049.

TRIAL COUNT:

384.

STRUCTURE:

48 frozen environmental contexts
x
8 F36-derived replicas.

CELLS:

48.

EPOCHS:

48.

COMPLETE WORLD-MANIFEST SHA-256:

041eba03561ce1b4640f5d9a61ddee7eb86b252efd40d14d79316098d337d4ba.

Serialized manifest-wrapper SHA-256:

05285019e972c0af952d3ca652f1bdc8cf443de59d6b56c03a39a76e2a0ef271.

Serialized manifest-wrapper bytes:

40016.

The bound world identity includes:

context;
replica;
family;
reversal location where applicable;
spatial region where applicable;
full true local-consequence field hash;
full sensed field hash.

PRIMARY STATUS AT MANIFEST BIND

Real ISO outcomes observed:

0.

Real ENTRY outcomes observed:

0.

Real RETAIN outcomes observed:

0.

Real NICHE outcomes observed:

0.

Real A36 qualification outcomes observed:

0.

The next permitted operation is:

two complete deterministic A36 primary sweeps
using F36 as seed.

NO WORLD REDRAW.
NO H-RADIUS CHANGE.
NO ENTRY-REINFORCEMENT CHANGE.
NO RELEASE-PROTECTION CHANGE.
NO REFRACTORY CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A36 / T8T SPATIALLY COOPERATIVE PROTECTED HEDGE NICHES

DATE:
2026-09-21.

STATUS:
CLOSED / REPRODUCIBLE NEGATIVE TARGET RESULT WITH REAL SPATIAL-COHERENCE EFFECT /
H NICHES FORMED AND PERSISTED,
BUT THE TARGET FAMILY-5 OSCILLATORY ATTRACTOR REMAINED /
NO NICHE ARM QUALIFIED /
NO ARM MET A36_SPATIAL_HEDGE_INFORMATION_GAIN /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

e3be3d20e1acb09cdff3b11538f513d650227b78.

F36:

f8f83007bc9bf5ff64a338ebe3540195086dd593.

Source SHA-256:

5ff16100fc817a650a74e74d574ee9361de824418c38323c03192493359cd1d3.

Deterministic gzip SHA-256:

216a54bb8e5ed18ae9436d0e07f4e29252d8563f5950ffb75ce478faec34f049.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

97aea4878019927a8385a5812f1f37c832aa32cd.

World-manifest SHA-256:

041eba03561ce1b4640f5d9a61ddee7eb86b252efd40d14d79316098d337d4ba.

Manifest-wrapper SHA-256:

05285019e972c0af952d3ca652f1bdc8cf443de59d6b56c03a39a76e2a0ef271.

PRIMARY REPRODUCIBILITY

Two complete F36-derived primary sweeps
were byte-identical.

Serialized primary SHA-256:

65fbcc0b69e32d812bffa0ff98c791a0cb239d1730ec94479cb2509b0b5ce96b.

All P1-P30 integrity probes:

PASS.

PRIMARY RESULT

A36_ANY_SPATIAL_HEDGE_QUALIFIED:

FALSE.

A36_SPATIAL_HEDGE_INFORMATION_GAIN:

FALSE.

D2 ISO REFERENCE

Aggregate service:

232062.

Harmful:

61 / 384
=
15.89%.

Oscillation:

58 / 384
=
15.10%.

Contradiction no-majority:

91.79%.

Contradiction epochs with H cluster >= 3:

13.52%.

Mean contradiction largest H cluster:

0.926 cells.

Mean niche lifetime:

1.866 epochs.

FAMILY-5 oscillators:

34.

D2 ENTRY REINFORCEMENT

Aggregate service:

231401.

Harmful:

61 / 384
=
15.89%.

Oscillation:

53 / 384
=
13.80%.

Contradiction no-majority:

90.48%.

Contradiction cluster >= 3:

17.87%.

Mean contradiction largest H cluster:

0.986.

Mean niche lifetime:

1.845 epochs.

FAMILY-5 oscillators broken:

2 / 34.

New FAMILY-5 oscillators:

0.

Service retained:

99.72%.

Interpretation:

entry reinforcement modestly reduced total oscillation,
but did not create long-lived niches
and barely touched the target oscillator family.

D2 RELEASE PROTECTION

Aggregate service:

230005.

Harmful:

62 / 384
=
16.15%.

Oscillation:

55 / 384
=
14.32%.

Contradiction no-majority:

91.73%.

Contradiction cluster >= 3:

28.74%.

Mean contradiction largest H cluster:

1.086.

Mean niche lifetime:

3.319 epochs.

FAMILY-5 oscillators broken:

2 / 34.

New FAMILY-5 oscillators:

1.

Service retained:

99.11%.

Interpretation:

release protection strongly increased niche persistence,
but still only weakly affected the target oscillator family.

D2 FULL NICHE

Aggregate service:

229550.

Harmful:

61 / 384
=
15.89%.

Oscillation:

52 / 384
=
13.54%.

Contradiction no-majority:

92.53%.

Contradiction cluster >= 3:

38.34%.

Contradiction cluster >= 6:

6.88%.

Mean contradiction largest H cluster:

1.285.

Mean niche lifetime:

3.774 epochs.

Maximum niche lifetime:

30 epochs.

Niches surviving >= 4 epochs:

265.

Niches surviving >= 8 epochs:

86.

FAMILY-5 oscillators broken:

2 / 34.

New FAMILY-5 oscillators:

0.

Service retained:

98.92%.

D2_NICHE qualified:

FALSE.

Reason:

oscillation remained:

13.54%

versus required:

<= 5%.

It also broke only:

5.88%

of paired FAMILY-5 oscillators

versus required:

>= 50%.

D3 ISO REFERENCE

Aggregate service:

225325.

Harmful:

62 / 384
=
16.15%.

Oscillation:

57 / 384
=
14.84%.

Contradiction no-majority:

92.60%.

Contradiction cluster >= 3:

9.86%.

Mean contradiction largest H cluster:

0.812.

Mean niche lifetime:

1.831 epochs.

FAMILY-5 oscillators:

30.

D3 ENTRY REINFORCEMENT

Aggregate service:

225028.

Harmful:

64 / 384
=
16.67%.

Oscillation:

59 / 384
=
15.36%.

Contradiction no-majority:

92.98%.

Contradiction cluster >= 3:

13.77%.

Mean niche lifetime:

1.875 epochs.

FAMILY-5 oscillators broken:

0 / 30.

New FAMILY-5 oscillators:

2.

D3 RELEASE PROTECTION

Aggregate service:

223784.

Harmful:

61 / 384
=
15.89%.

Oscillation:

57 / 384
=
14.84%.

Contradiction no-majority:

93.63%.

Contradiction cluster >= 3:

23.30%.

Mean contradiction largest H cluster:

0.918.

Mean niche lifetime:

3.366 epochs.

FAMILY-5 oscillators broken:

0 / 30.

New FAMILY-5 oscillators:

1.

D3 FULL NICHE

Aggregate service:

223963.

Harmful:

58 / 384
=
15.10%.

Oscillation:

51 / 384
=
13.28%.

Contradiction no-majority:

93.88%.

Contradiction cluster >= 3:

30.13%.

Contradiction cluster >= 6:

5.34%.

Mean contradiction largest H cluster:

1.060.

Mean niche lifetime:

3.781 epochs.

Maximum niche lifetime:

26 epochs.

Niches surviving >= 4 epochs:

195.

Niches surviving >= 8 epochs:

69.

FAMILY-5 oscillators broken:

0 / 30.

New FAMILY-5 oscillators:

2.

Service retained:

99.40%.

D3_NICHE qualified:

FALSE.

Reason:

oscillation remained:

13.28%

versus required:

<= 5%.

It broke:

0%

of paired FAMILY-5 oscillators.

MECHANISM ATTRIBUTION

A36 successfully changed
the spatial organization of uncertainty.

Compared with isolated H,
full NICHE arms produced:

more contradiction-time H clusters;

larger contradiction-time H clusters;

roughly twice the mean niche lifetime;

many more niches surviving 4 and 8 epochs.

Therefore the spatial modifier is biologically / dynamically nontrivial.

However:

the target persistent oscillatory family
was essentially invariant.

D2:

34 ISO FAMILY-5 oscillators.

ENTRY / RETAIN / NICHE each broke only:

2.

D3:

30 ISO FAMILY-5 oscillators.

ENTRY / RETAIN / NICHE broke:

0.

The reduction in total oscillation
under D2_NICHE and D3_NICHE
came from other environmental families,
not the persistent FAMILY-5 attractor
that motivated A36.

This is the central negative result.

SPATIAL COHERENCE IS REAL.

SPATIAL COHERENCE IS NOT SUFFICIENT.

The system can form
longer-lived local uncertainty neighborhoods
without altering
the temporal attractor created by oscillatory forcing.

ATTRACTOR QUALITY LIMIT

False final dominance remained far above
the frozen 5% limits.

Representative values:

D2_NICHE false C:

19.39%.

D2_NICHE false S:

15.53%.

D3_NICHE false C:

20.0%.

D3_NICHE false S:

15.98%.

Thus stronger spatial uncertainty structure
did not solve final attractor correctness.

REVERSAL COST

Spatial niche formation did NOT destroy reversal.

Reversal acquisition remained:

D2_NICHE:

94.53%.

D3_NICHE:

96.09%.

Service also remained within approximately:

99%

of paired ISO.

So the failure is not:

"niches are too sticky."

The failure is:

"niches do not survive the right developmental dimension."

TECHNICAL INTERPRETATION

A36 falsifies the hypothesis:

LOCAL SPATIAL COOPERATION ALONE
IS ENOUGH
TO TURN PROTECTED HEDGING
INTO A STABLE ALTERNATIVE ATTRACTOR
UNDER OSCILLATORY FORCING.

A36 gives H:

local nucleation support;

local persistence support;

and genuine multi-epoch clusters.

But those clusters are still:

state-coherent
without being
developmentally inherited.

When a niche dissolves,
its prior uncertainty has no lineage-level claim
on future cells.

A future cell occupying the same region
does not inherit:

"this region has repeatedly remained unresolved."

Thus the protected state can persist
for several epochs
without persisting
through developmental turnover / lineage.

The next justified question is:

DOES UNCERTAINTY NEED
LINEAGE MEMORY?

Not:

more entry gain.

Not:

larger H radius.

Not:

longer universal H lifetime.

Instead:

when an H cell is replaced / gives rise to a successor,
should some bounded local uncertainty state
be inherited by that lineage?

That would test whether
the unresolved phenotype must survive
through developmental succession,
not merely spatial adjacency.

PLAIN-SPEAK INTERPRETATION

The uncertain cells learned
how to form neighborhoods.

That part worked.

Under full niche behavior,
uncertain groups became:

bigger;

more common during contradiction;

and about twice as long-lived.

Some lasted dozens of epochs.

But the stubborn oscillating worlds
barely cared.

For D2,
only 2 of 34 target oscillators were broken.

For D3:

zero of 30.

So the problem is probably not:

"the uncertain cells need more friends nearby."

The clue is that the neighborhood
still has no memory across generations.

If an uncertain cell disappears,
its successor starts fresh.

The location may have been uncertain
again and again,
but that history is not inherited.

So the next question becomes:

CAN AN UNCERTAIN LINEAGE
PASS A SMALL AMOUNT OF ITS STATE
TO ITS SUCCESSOR?

That would make uncertainty
not just spatially persistent,

but developmentally persistent.

No autonomous controller is authorized.

DG-1R-05 remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
