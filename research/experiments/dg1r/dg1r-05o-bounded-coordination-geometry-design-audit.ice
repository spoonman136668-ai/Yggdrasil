TITLE: DG-1R-05O — Bounded Coordination Geometry Design Audit
DATE: 2026-09-20
STATUS: CLOSED / EXPLORATORY DESIGN ANALYSIS / NON-PRIMARY
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / COORDINATED INFERENCE
BRANCH: dg1a-ar
PARENT: DG-1R-05N

PURPOSE

DG-1R-05N established a reproducible negative dynamic-transfer result.

The DIST4_05M topology produces stronger static syndrome evidence,
but the frozen single-block greedy decoder cannot cross the local minima / plateaus
created by the preregistered multi-region lesions.

Before constructing a multi-block repair decoder,
DG-1R-05O maps a narrower design question:

WHEN A BOUNDED COALITION OF LOGICAL CELLS
CAN REDUCE SYNDROME WEIGHT,
DOES THE FIRST AVAILABLE DESCENT
ACTUALLY POINT TOWARD DAMAGED CELLS?

STATUS BOUNDARY

This audit is EXPLORATORY.

The core coordination-radius hypothesis was inspected after 05N closure
before this dedicated harness was formalized.

Therefore 05O is not represented as blinded confirmatory evidence.

Its role is design selection:
prevent an unsafe coordinated-repair experiment from being mistaken for an evidence-independent authority mechanism.

Synthetic software only.
No living tissue.
No wetware.
No canonical H191 execution.
No STAB-18-R1 execution.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05o_coordination_geometry_v1.py

Harness commit:

de1ebf7a94db4bfbd298ff77585ffb67a3a30e95.

Git blob:

11a349552a6e3ee7c7c5d0a7dfa407729d9c24d6.

Source SHA-256:

2c3d59e9c2539589f82db141131cc530196b64fb73762dc15b72fec50921e189.

Source bytes:

5148.

The three topology matrices were mechanically compared against
the exact closed DG-1R-05N topology definitions.

HYPER20_BASELINE:

MATCH.

DIST3_05L:

MATCH.

DIST4_05M:

MATCH.

METHOD

For every nonzero 12-block logical fault mask,
and for every frozen topology:

1. compute the logical syndrome;
2. search candidate logical coalitions in increasing size from 1 through 4 blocks;
3. identify the first coalition size at which any candidate strictly reduces syndrome weight;
4. classify all improving candidates at that first radius as:

TRUE_ONLY_FIRST_DESCENT:
every improving coalition flips only actually damaged logical blocks;

MIXED_FIRST_DESCENT:
both truth-aligned and false coalitions improve the syndrome;

FALSE_ONLY_FIRST_DESCENT:
every improving coalition includes at least one healthy logical block;

NO_DESCENT_LE4:
no coalition of up to four logical blocks strictly reduces syndrome weight.

For the three frozen 05N challenge masks,
search continues through all 12 blocks
to locate both:

- the first descent of any kind;
- the first truth-aligned descent.

Separately,
for every integrity-only check pattern of weights 1 through 4,
search logical coalitions of size <=4
and record whether healthy logical state is attracted toward a logical repair.

REPRODUCIBILITY

Two complete deterministic sweeps.

Output SHA-256 A:

282caaf426ec742afd765c7abc16be7e67e6b336d6184a7872e0dc7aba04eaa5.

Output SHA-256 B:

282caaf426ec742afd765c7abc16be7e67e6b336d6184a7872e0dc7aba04eaa5.

BYTE_IDENTICAL:

TRUE.

RESULTS — LOGICAL FIRST DESCENT

HYPER20_BASELINE:

TRUE_ONLY_FIRST_DESCENT:
444.

MIXED_FIRST_DESCENT:
3106.

FALSE_ONLY_FIRST_DESCENT:
534.

NO_DESCENT_LE4:
10.

ZERO_SYNDROME:
1.

DIST3_05L:

TRUE_ONLY_FIRST_DESCENT:
316.

MIXED_FIRST_DESCENT:
3192.

FALSE_ONLY_FIRST_DESCENT:
569.

NO_DESCENT_LE4:
18.

DIST4_05M:

TRUE_ONLY_FIRST_DESCENT:
247.

MIXED_FIRST_DESCENT:
3218.

FALSE_ONLY_FIRST_DESCENT:
611.

NO_DESCENT_LE4:
19.

Because DIST4_05M is full-rank,
it has no nonzero zero-syndrome logical mask.

For DIST4_05M,
out of 4095 nonzero logical masks:

TRUE_ONLY_FIRST_DESCENT:

247 / 4095
=
6.031746 percent.

MIXED_FIRST_DESCENT:

3218 / 4095
=
78.583639 percent.

FALSE_ONLY_FIRST_DESCENT:

611 / 4095
=
14.920635 percent.

NO_DESCENT_LE4:

19 / 4095
=
0.463980 percent.

Thus a bounded syndrome descent is usually not a unique truth direction.

RESULTS — FROZEN CHALLENGE MASKS ON DIST4_05M

BASE_WEAK4_MASK1106

Damaged logical blocks:

1,4,6,10.

Syndrome weight:

5.

First ANY improving coalition:

radius 2.

Unique first improving coalition:

7,8.

Syndrome reduction:

1.

Truth aligned:

FALSE.

First truth-aligned improving coalition:

radius 4.

Coalition:

1,4,6,10.

Syndrome reduction:

5.

This means a naive pair-lookahead decoder would discover a false downhill move
before the actual four-cell repair.

DIST3_WEAK5_MASK2243

Damaged logical blocks:

0,1,6,7,11.

Syndrome weight:

7.

First ANY improving coalition:

radius 2.

Number of improving radius-2 coalitions:

4.

Best recorded reduction:

2.

Example best coalition:

1,4.

Truth aligned:

FALSE.

First truth-aligned improving coalition:

radius 4.

Two truth-aligned radius-4 candidates exist.

Best recorded example:

0,1,7,11.

Reduction:

1.

Again,
a smaller false coalition appears before a truth-aligned repair direction.

DIST4_MIN6_MASK249

Damaged logical blocks:

0,3,4,5,6,7.

Syndrome weight:

4.

First ANY improving coalition:

radius 6.

First truth-aligned improving coalition:

radius 6.

Unique exact coalition:

0,3,4,5,6,7.

Reduction:

4.

No <=4 coalition escapes this lesion.

RESULTS — INTEGRITY-ONLY LOGICAL ATTRACTION

For DIST4_05M:

integrity-only weight 1:

0 / 20 patterns attract a <=4 logical descent.

integrity-only weight 2:

0 / 190 patterns attract a <=4 logical descent.

integrity-only weight 3:

58 / 1140 patterns attract a <=4 logical descent.

All 58 first attract at radius 4.

integrity-only weight 4:

2487 / 4845 patterns attract a <=4 logical descent.

This is:

51.331269 percent.

First-attraction radius distribution:

radius 1:
340.

radius 3:
260.

radius 4:
1887.

For comparison,
weight-4 integrity-only attraction counts were:

HYPER20_BASELINE:
2607 / 4845.

DIST3_05L:
2334 / 4845.

DIST4_05M:
2487 / 4845.

TECHNICAL INTERPRETATION

05O rules out a tempting but unsafe conclusion from 05N.

The correct response to a one-step greedy local minimum is not simply:

"allow two,
three,
or four cells to move together whenever syndrome weight falls."

On DIST4_05M,
the first bounded downhill coalition is truth-only for only about 6 percent
of all nonzero logical masks.

For most masks,
the first descent is ambiguous.

For nearly 15 percent,
every first-radius improving coalition is false.

The exact 05N weak masks demonstrate the issue directly:

a false two-cell repair can look locally better
before the true four- or five-cell lesion has a truth-aligned downhill path.

Integrity-only faults create the complementary problem:

healthy logical tissue can also present apparently attractive multi-cell repair directions.

This is consistent with DG-1R-05J:

syndrome geometry is evidence,
not independent truth.

A larger search radius increases reachability,
but it does not create provenance.

PLAIN-SPEAK INTERPRETATION

We found out why simply letting more cells vote on a repair is dangerous.

Imagine the warning system says something is wrong.

With the old repairer,
no single cell can make the warning smaller,
so it does nothing.

It is tempting to say:

"Fine. Let pairs or groups of cells try together."

But in the stronger 05M layout,
the first pair that makes the warning look better can be two perfectly healthy cells.

For one of our known injuries,
the wrong two cells look helpful
before the real four damaged cells do.

And backup-check damage can create the same trap
even when the logical cells are completely healthy.

So a coalition becoming more internally consistent
does not prove that coalition is correct.

This directly supports the emerging Yggdrasil governance rule:

healthy-cell consensus can be operational authority,
but "healthy" and "independent witness" must be established separately from raw agreement.

A crowd of cells repeating evidence from the same damaged source
is not a trustworthy quorum.

ARCHITECTURAL CONSEQUENCE

Do not authorize a coordinated logical repair solely because:

- more cells agree;
- a larger coalition lowers syndrome weight;
- a coalition has high internal confidence;
- multiple witnesses share the same underlying provenance.

The next experiment should introduce an explicit distinction between:

AGREEMENT

and

INDEPENDENT SUPPORT.

Candidate authority should be qualified by witness provenance,
health evidence,
and abstention under correlated ambiguity.

This is not a central-controller requirement.

It is a constitutional rule for distributed authority.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05P —

INDEPENDENCE-QUALIFIED HEALTHY-CELL CONSENSUS AUDIT.

Question:

Can a distributed cell population use compact health,
confidence,
temporal consistency,
and witness-provenance signals
to distinguish:

- a genuinely damaged logical coalition;
- an attractive but false logical descent;
- an integrity-only false alarm;
- correlated witnesses that should count as one source rather than many;

while preserving abstention when evidence is not independently sufficient?

The first 05P stage should be detection / authorization only.

No repair mutation should occur until the consensus signal itself
has demonstrated calibrated specificity and sensitivity.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
