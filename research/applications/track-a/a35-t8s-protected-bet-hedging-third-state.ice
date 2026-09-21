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


PRE-RUN IMPLEMENTATION FREEZE 01 — A35 PROTECTED BET-HEDGING THIRD STATE

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F35-DERIVED WORLD,
HEDGING EVENT,
HEDGED-STATE OCCUPANCY,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

5ebc98b99f80412534846f6289f65073cde3623e.

SOURCE BUNDLE

Loader:

research/applications/track-a/a35_t8s_protected_bet_hedging_third_state_v1.py

Loader Git blob:

429b68b83fe407745627ef32d0a6eb3673e005d8.

Payload:

research/applications/track-a/a35_t8s_protected_bet_hedging_third_state_v1.py.gz

Payload Git blob:

cec77e03bdb1243797024ed767525b32a72fa924.

Decompressed source SHA-256:

073f60c43f16b80e47e359998e8477a2ddf112d5567790ec7729bbc9b39ec030.

Decompressed source bytes:

20483.

Deterministic gzip SHA-256:

a97e157d023b6d7a4a533731400e2758680846dd4c430b741229738040e2abfc.

Compressed payload bytes:

6213.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F35-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized output SHA-256:

405b3f74cc2607e1dcccca5e97c0f443d1d1a3309dede8919ffd9e15420ad5c1.

Mechanical world-manifest SHA-256:

2dcbf6a5612d3e5bf331ef9a376c47c79b5015d257e4b9b5689f0d8f3e6a1438.

All P1-P26 integrity probes:

PASS.

No primary hedge arm qualified.

No primary hedge arm met
A35_BET_HEDGE_INFORMATION_GAIN.

MECHANICAL HEDGE SELECTIVITY

D2_H_P75L25:

2.9100x.

D2_H_P50L50:

2.6982x.

D2_H_P25L75:

2.2399x.

D3_H_P75L25:

2.7833x.

D3_H_P50L50:

2.5266x.

D3_H_P25L75:

2.2673x.

Thus the third state is selectively recruited
during contradiction rather than uniformly.

MECHANICAL CONTRADICTION NO-MAJORITY FRACTION

D2_H_P75L25:

90.13%.

D2_H_P50L50:

86.72%.

D2_H_P25L75:

83.69%.

D3_H_P75L25:

92.33%.

D3_H_P50L50:

90.05%.

D3_H_P25L75:

88.19%.

MECHANICAL OSCILLATION

Hedge arms remained between:

14.58%
and
18.23%.

Thus the third phenotype is nontrivial
but mechanically does not pre-prove
the primary oscillation target.

MECHANICAL ATTRACTOR QUALITY

False-dominance rates remained materially above
the frozen 5% limits in every hedge arm.

Therefore A35 enters primary execution
as a genuinely falsifiable mechanism.

No hedge gain,
release rule,
A34 suppression,
A30 local inhibition,
A31 refractory duration,
qualification threshold,
or information-gain rule
is changed in response.

REAL A35 STATUS

No real F35-derived world exists.

No real hedge event exists.

No real A35 primary outcome exists.

Let the resulting commit SHA be:

F35.

After F35 exists:

1. derive exactly 384 fresh worlds from F35;
2. bind the complete world-manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report all six hedge arms and paired A34 references without post-result tuning.

NO POST-RESULT HEDGE-GAIN TUNING.
NO POST-RESULT RELEASE-LAW TUNING.
NO POST-RESULT SUPPRESSION TUNING.
NO POST-RESULT REFRACTORY CHANGE.
NO POST-RESULT LOCAL-INHIBITION CHANGE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A35 PROTECTED BET-HEDGING THIRD STATE

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A35 ARM EXECUTION,
HEDGE ENTRY,
HEDGE RELEASE,
OR SCIENTIFIC OUTCOME.

F35:

a1fefb2cf0a507f630717be86f57e02e2899efe0.

FROZEN SOURCE SHA-256:

073f60c43f16b80e47e359998e8477a2ddf112d5567790ec7729bbc9b39ec030.

TRIAL COUNT:

384.

STRUCTURE:

48 frozen environmental contexts
x
8 F35-derived replicas.

CELLS:

48.

EPOCHS:

48.

COMPLETE WORLD-MANIFEST SHA-256:

778799b6777e6214f2f19684db24237bbb95853c1a8b5025e97a3874894963fa.

Serialized manifest-wrapper SHA-256:

d23c18e2cf989edf5923e503f1f239a1bab89e42de650475be34230bd7eeb320.

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

Real hedge entries observed:

0.

Real hedge releases observed:

0.

Real hedge occupancy observed:

0.

Real A35 qualification outcomes observed:

0.

The next permitted operation is:

two complete deterministic A35 primary sweeps
using F35 as seed.

NO WORLD REDRAW.
NO HEDGE-LAW CHANGE.
NO RELEASE-LAW CHANGE.
NO SUPPRESSION CHANGE.
NO REFRACTORY CHANGE.
NO LOCAL-INHIBITION CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A35 / T8S PROTECTED BET-HEDGING THIRD STATE

DATE:
2026-09-21.

STATUS:
CLOSED / REPRODUCIBLE MIXED-NEGATIVE MECHANISM RESULT /
THE HEDGED PHENOTYPE WAS REAL AND CONTRADICTION-SELECTIVE
BUT DID NOT BREAK THE PERSISTENT OSCILLATORY FAMILY /
NO PRIMARY ARM QUALIFIED /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

5ebc98b99f80412534846f6289f65073cde3623e.

F35:

a1fefb2cf0a507f630717be86f57e02e2899efe0.

Source SHA-256:

073f60c43f16b80e47e359998e8477a2ddf112d5567790ec7729bbc9b39ec030.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

101f69beae095ac086033292783183980367944c.

World-manifest SHA-256:

778799b6777e6214f2f19684db24237bbb95853c1a8b5025e97a3874894963fa.

Manifest-wrapper SHA-256:

d23c18e2cf989edf5923e503f1f239a1bab89e42de650475be34230bd7eeb320.

PRIMARY REPRODUCIBILITY

Two complete F35-derived scientific sweeps
produced identical canonical JSON.

Primary result-file SHA-256:

d7fe4e72cc4b89a5cad832689adad816c4f81987f9be49d62da9b9126becb2fa.

Sweep 1 used the frozen serial runner.

Sweep 2 used arm-isolated execution
with identical frozen worlds and arm logic.

The arm-isolated runner originally omitted
the serial runner's final newline.
After using a wrapper that emits the same canonical serial framing,
the two complete result files were byte-identical.

Parsed scientific objects were already exactly equal
before that framing correction.

All P1-P26 integrity probes:

PASS.

PRIMARY RESULT

A35_ANY_BET_HEDGE_QUALIFIED:

FALSE.

A35_BET_HEDGE_INFORMATION_GAIN:

FALSE.

HEDGE SELECTIVITY

Every H arm preferentially entered H
during contradiction.

D2_H_P75L25:

2.8773x.

D2_H_P50L50:

2.7675x.

D2_H_P25L75:

2.3274x.

D3_H_P75L25:

2.7360x.

D3_H_P50L50:

2.7186x.

D3_H_P25L75:

2.1768x.

Thus the third state did not behave
as generalized indecision.

It was specifically enriched
when both support fields were simultaneously strong.

HEDGED OCCUPANCY

Mean H occupancy remained small:

approximately:

0.91
to
2.15 cells

out of 48.

Peak H occupancy ranged:

10
to
17 cells.

Mean H dwell time ranged:

approximately 2.93
to
3.41 epochs.

Median H dwell:

2 epochs.

During contradiction,
H occupancy fraction reached approximately:

4.53%
to
12.56%.

Outside contradiction:

approximately:

0.79%
to
1.50%.

This confirms selective protected uncertainty
without population-wide collapse into H.

CONTRADICTION NO-MAJORITY EFFECT

Paired A34-style references
versus H arms:

D2_P25L75:

79.21%
->
83.04%.

D2_P50L50:

80.19%
->
86.68%.

D2_P75L25:

80.54%
->
89.67%.

D3_P25L75:

84.48%
->
88.75%.

D3_P50L50:

86.24%
->
90.81%.

D3_P75L25:

87.17%
->
91.92%.

Thus H consistently increased
the fraction of contradictory epochs
where no side held a population majority.

Two D3 hedge arms exceeded
the frozen 90% contradiction no-majority criterion:

D3_H_P50L50:
90.81%.

D3_H_P75L25:
91.92%.

This is genuine mechanism evidence.

OSCILLATION RESULT

The effect on population oscillation
was real but small.

D2_P25L75:

17.97%
->
16.67%.

D2_P50L50:

16.93%
->
16.15%.

D2_P75L25:

17.19%
->
15.10%.

D3_P25L75:

16.93%
->
15.89%.

D3_P50L50:

16.93%
->
16.15%.

D3_P75L25:

16.67%
->
15.63%.

Every hedge arm remained far above
the frozen qualification ceiling:

5%.

Therefore:

A REAL UNCERTAINTY PHENOTYPE
DID NOT BY ITSELF
STABILIZE THE WHOLE POPULATION.

FAMILY-5 OSCILLATOR RESULT

Paired-reference FAMILY-5 oscillators broken:

D2_H_P25L75:

4 / 40.

D2_H_P50L50:

4 / 39.

D2_H_P75L25:

4 / 36.

D3_H_P25L75:

1 / 34.

D3_H_P50L50:

3 / 35.

D3_H_P75L25:

4 / 36.

Maximum paired-reference break rate:

11.11%.

Frozen information-gain requirement:

at least 25%.

Frozen qualification requirement:

at least 50%.

Thus H did not materially dismantle
the persistent oscillatory family.

DIRECTIONAL COORDINATION

All hedge arms retained strong
C/S directional coordination.

D2 range:

88.57%
to
92.86%.

D3 range:

87.50%
to
94.44%.

So the H state did not destroy
directional organization.

REVERSAL PERFORMANCE

Reversal acquisition remained:

96.88%
to
100%.

Thus the protected state
was not catastrophically sticky.

SERVICE COST

Aggregate service remained within roughly:

97.0%
to
98.7%

of paired A34-style references.

Examples:

D2_H_P25L75:

244673
versus
247929.

D2_H_P75L25:

230914
versus
238002.

D3_H_P50L50:

229831
versus
235088.

The H phenotype therefore imposed
a modest service cost,
not a collapse.

ATTRACTOR QUALITY FAILURE

False final dominance remained high.

Hedge-arm false C dominance:

approximately:

18.97%
to
20.69%.

Hedge-arm false S dominance:

approximately:

15.71%
to
17.14%.

Frozen limits:

<= 5%.

Therefore H improved uncertainty handling
without solving final attractor correctness.

TECHNICAL INTERPRETATION

A35 falsifies the strong hypothesis:

A THIRD PROTECTED UNCERTAINTY STATE
IS SUFFICIENT
TO RESOLVE THE A34 OSCILLATORY FAMILY.

But it supports a narrower architectural claim:

A DISTRIBUTED POPULATION CAN REPRESENT
GENUINE CONTRADICTION
AS A REAL PROTECTED PHENOTYPE
WITHOUT A CENTRAL CONFIDENCE SCORE.

The phenotype is:

selective;
bounded;
short-lived;
information-preserving;
and compatible with reversal.

Its weakness is not that H activates incorrectly.

Its weakness is:

H IS TOO LOCAL AND TOO TEMPORARY
TO CHANGE THE MACROSCOPIC OSCILLATORY ATTRACTOR.

The remaining FAMILY-5 oscillators
largely persist even though individual cells
periodically enter protected uncertainty.

This suggests the next question
should not be:

"make H stronger."

That would be post-hoc gain tuning.

The more principled next question is:

DOES BET-HEDGING NEED
SPATIALLY OR LINEAGE-PERSISTENT SUBPOPULATIONS
RATHER THAN INDEPENDENT TEMPORARY H CELLS?

A35 currently lets each cell hedge independently.

The protected cells do not form:

stable neighborhoods;
lineage-preserved hedged niches;
or coordinated uncertainty domains.

A future experiment should test
whether uncertainty needs spatial / lineage structure
so that a protected subpopulation can persist
through oscillatory forcing
without forcing the whole organism to choose.

PLAIN-SPEAK INTERPRETATION

The third state worked.

Just not enough.

Cells really did learn a new response:

"CANDIDATE."

"STALE."

or:

"I AM STAYING OUT OF THIS FOR NOW."

And they did not choose that third option randomly.

They used it about two to three times more often
when the evidence was genuinely contradictory.

That made the population
less likely to pretend it had a majority
while both sides were shouting.

It did not ruin reversal.

It did not destroy coordination.

It only cost a few percent of service.

So bet-hedging is not a dead end.

But individual cells briefly stepping aside
does not stop the whole population
from falling back into the same oscillatory pattern.

The big clue is:

THE HEDGED CELLS ARE ISOLATED AND TEMPORARY.

They do not yet form
a protected subpopulation
that can survive as a stable alternative
while the rest of the organism fluctuates.

So the next clean question is:

DOES UNCERTAINTY NEED ITS OWN
PERSISTENT LOCAL NICHE OR LINEAGE?

Not a bigger confidence number.

Not a stronger global threshold.

A real subpopulation
whose job is to remain unresolved
until the environment becomes coherent enough
to justify leaving that state.

No autonomous controller is authorized.

DG-1R-05 remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-CLOSURE PACKAGING FIXA 01 — RESTORE EXACT FROZEN A35 PAYLOAD

DATE:
2026-09-21.

STATUS:
PACKAGING-ONLY REPAIR / SCIENTIFIC RESULT UNCHANGED.

After A35 primary closure,
the repository copy of:

research/applications/track-a/a35_t8s_protected_bet_hedging_third_state_v1.py.gz

was found truncated on the repository surface.

The frozen local payload used for the preregistered mechanical and primary executions remained intact.

Restored exact deterministic gzip identity:

bytes:
6213.

SHA-256:
a97e157d023b6d7a4a533731400e2758680846dd4c430b741229738040e2abfc.

Git blob:
8d09369fdd78677bdde7b97ef1ef518fcdea23b4.

Decompressed source identity remains:

bytes:
20483.

SHA-256:
073f60c43f16b80e47e359998e8477a2ddf112d5567790ec7729bbc9b39ec030.

The two real primary sweeps were independently rerun from that exact frozen source after the defect was noticed.

They were byte-identical.

Serialized primary SHA-256:

7f8b0468e91dd5028f9d17a6738a7abd83e916fca03fbae7df72cdce6dbc33a2.

Bound real-world manifest remained exactly:

778799b6777e6214f2f19684db24237bbb95853c1a8b5025e97a3874894963fa.

All P1-P26 integrity probes remained PASS.

No world,
mechanism,
hedge law,
release law,
suppression law,
refractory duration,
metric,
qualification threshold,
interpretation,
or closure result changed.

This repair restores repository executability only.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
