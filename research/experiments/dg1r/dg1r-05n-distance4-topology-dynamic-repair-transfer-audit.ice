TITLE: DG-1R-05N — Distance-4 Topology Dynamic Repair Transfer Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE DYNAMIC TRANSFER AUDIT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / REPAIR TRANSFER
BRANCH: dg1a-ar
PARENT: DG-1R-05M

PURPOSE

DG-1R-05M found a unique topology in its frozen family that achieves:

- GF(2) rank 12;
- zero logical kernel;
- 4096 distinct logical-only syndromes;
- single-region syndrome floor 6;
- two-region syndrome floor 8;
- global minimum positive logical syndrome weight 4;
- maximum pair co-occurrence 2;

under the same 20-check / 80-incidence / 128-bit persistent-state budget.

DG-1R-05N asks:

DOES THAT STRONGER STATIC REPRESENTATION
IMPROVE
THE ALREADY-ESTABLISHED DYNAMIC REPAIR SYSTEM
WITHOUT CHANGING THE DECODER?

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No production modification.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL / NON-EVIDENCE.

DG-1R-05 canonical frozen primary remains UNSPENT.

FROZEN TOPOLOGIES

A. HYPER20_BASELINE

Exact DG-1R-05G/05H/05I baseline:

(0,2,7,9)
(1,3,6,11)
(4,5,9,10)
(2,3,5,8)
(0,1,4,8)
(6,7,8,10)
(2,4,6,11)
(0,3,5,7)
(1,7,10,11)
(1,5,6,9)
(3,8,9,10)
(0,4,8,11)
(0,2,6,10)
(1,3,4,7)
(2,5,7,11)
(2,3,4,10)
(0,1,5,10)
(0,3,9,11)
(1,2,8,9)
(4,6,7,9)

B. DIST3_05L

Exact closed DG-1R-05L selected topology,
derived by:

(1,8,14)
(5,16,11)

from baseline.

Static facts:

rank 12.
kernel 0.
single floor 6.
two floor 8.
global floor 3.
pair co-occurrence 2.

C. DIST4_05M

Exact closed DG-1R-05M selected topology:

(0,2,7,9)
(1,3,6,11)
(4,5,9,10,11)
(2,3,5)
(0,1,4,8)
(6,7,8,10)
(2,4,6)
(0,3,5,6,7)
(1,7,10,11)
(1,5,6,9)
(3,8,9,10)
(0,4,8,11)
(0,2,6,10)
(1,3,4,7)
(2,5,7,8,11)
(2,3,4,10)
(0,1,5,10)
(0,3,9,11)
(1,2,8,9)
(4,7,9)

Static facts:

rank 12.
kernel 0.
single floor 6.
two floor 8.
global floor 4.
pair co-occurrence 2.

PERSISTENT STATE

All topologies:

48 logical bits.

80 integrity bits.

128 persistent bits total.

No added persistent state.

DYNAMICS

Exact DG-1R-05H / authoritative 05I dynamic substrate:

48 logical bits.

MIXED5:
one CA update per external input.

Rule set:

90,
150,
110,
22,
30.

Input-mapped logical blocks:

1,
4,
7,
10.

One mapped logical bit per mapped block per world.

Repair occurs:

before current input overwrite.

Then:

current input overwrite.

Then:

logical CA update.

Then:

all 20 topology-specific integrity checks recomputed.

Pre-damage:

1024 steps.

Post-damage:

32 steps.

DECODER METHODS

1. GREEDY_BASELINE

Exact DG-1R-05H iterative greedy syndrome inference.

For each bit plane independently:

- choose the logical block whose hypothetical flip yields the largest strictly positive syndrome-weight reduction;
- tie by lowest logical block index;
- never select the same logical block twice in one plane;
- up to 4 logical flips per plane;
- stop when no logical flip strictly reduces syndrome weight.

Apply every inferred logical flip.

2. CROSSPLANE2_GATE

Exact authoritative DG-1R-05I confidence gate.

Run the same greedy inference.

For each logical block:

PLANE_SUPPORT =
number of bit planes on which greedy inference proposes a flip.

Apply inferred flips only for blocks with:

PLANE_SUPPORT >=2.

Threshold remains exactly 2.

No new decoder heuristic.

WORLD FAMILY

12 worlds.

Seeds:

20260926060000
through
20260926060011.

No prior DG-1R seed reuse.

Every topology and decoder method receives:

the exact same input sequence,
mapped logical positions,
mixed-rule assignment,
damage-family definition,
and post-damage input sequence
within a world.

DAMAGE FAMILIES

LEGACY FAMILIES

A. LOCAL_DATA2_D6

Block 5.

Logical planes:

0,
1.

B. DISTRIBUTED_DATA2

Blocks:

2,
8.

Logical planes:

0,
1
in each block.

C. DATA2_PLUS_CHECK2_D6

Block 5 logical planes:

0,
1.

Plus:

first two topology-relative incident integrity checks,
bit plane 0.

D. DATA2_PLUS_CHECK3_D7

Block 2 logical planes:

0,
1.

Plus:

first three topology-relative incident integrity checks,
bit plane 0.

E. CHECK4_BIT0_D6

No logical damage.

First four topology-relative incident checks for block 5,
bit plane 0.

F. CHECK4_BIT0_D7

No logical damage.

First four topology-relative incident checks for block 2,
bit plane 0.

G. CHECK4_BITS01_D6

No logical damage.

First four topology-relative incident checks for block 5,
bit planes 0 and 1.

H. SINGLE_DATA1_D6

Block 5.

Logical plane:

0.

STATIC-GEOMETRY CHALLENGE FAMILIES

These masks are frozen from already-closed topology geometry
before 05N dynamic execution.

I. BASE_WEAK4_MASK1106

Logical block set:

1,
4,
6,
10.

This is the lexicographically first weight-4 logical mask
with positive syndrome weight 3 in frozen HYPER20.

Frozen same-plane static syndrome weights:

HYPER20_BASELINE:
3.

DIST3_05L:
5.

DIST4_05M:
5.

For each world choose:

the lowest bit plane
that is not the mapped input bit plane
for any affected mapped block.

Affected mapped blocks are:

1,
4,
10.

At most three bit planes are excluded,
so a safe common bit plane always exists.

Flip that same safe plane in all four listed logical blocks.

J. DIST3_WEAK5_MASK2243

Logical block set:

0,
1,
6,
7,
11.

This is the lexicographically first global-floor-3 mask
in frozen DIST3_05L.

Frozen same-plane static syndrome weights:

HYPER20_BASELINE:
3.

DIST3_05L:
3.

DIST4_05M:
7.

For each world choose:

the lowest bit plane
that is not the mapped input bit plane
for affected mapped blocks:

1,
7.

A safe common bit plane always exists.

Flip that same safe plane in all five listed logical blocks.

K. DIST4_MIN6_MASK249

Logical block set:

0,
3,
4,
5,
6,
7.

This is the lexicographically first global-floor-4 mask
in frozen DIST4_05M.

Frozen same-plane static syndrome weights:

HYPER20_BASELINE:
4.

DIST3_05L:
6.

DIST4_05M:
4.

For each world choose:

the lowest bit plane
that is not the mapped input bit plane
for affected mapped blocks:

4,
7.

A safe common bit plane always exists.

Flip that same safe plane in all six listed logical blocks.

SAFE-PLANE RULE

The safe-plane rule is part of preregistration.

It prevents immediate current-input overwrite
from erasing a challenge lesion bit.

No plane may be selected after observing decoder behavior.

LESION ASSERTIONS

Harness MUST assert per world/topology/family:

- exact logical flip count;
- exact integrity flip count;
- physical uniqueness;
- legacy logical lesions do not overlap current mapped logical positions;
- challenge-family safe plane obeys the frozen mapped-position exclusion;
- topology-relative incident-check families use actual incident checks;
- no integrity index is duplicated.

PRIMARY TELEMETRY

Per topology,
method,
damage family,
and world:

- inferred logical flips;
- applied logical flips;
- abstained inferred flips;
- false inferred logical flips;
- false applied logical flips;
- decoder iterations;
- residual inferred syndrome weight;
- final syndrome weight;
- first-episode plane support;
- logical divergence at horizons:
  1,
  4,
  8,
  16,
  32;
- physical divergence at same horizons;
- logical divergence area;
- physical divergence area;
- sustained exact logical recovery;
- logical recovery time.

FALSE APPLIED LOGICAL FLIP

Exact 05I evaluation definition.

An applied repair bit is FALSE if
its post-correction logical value does not match
the undamaged counterfactual logical bit
immediately before current input overwrite.

This label is evaluation telemetry only.
The decoder never sees it.

PRIMARY TRANSFER SIGNALS

LEGACY_LOGICAL_NO_REGRESSION

TRUE iff for:

LOCAL_DATA2_D6,
DISTRIBUTED_DATA2,
DATA2_PLUS_CHECK2_D6,
DATA2_PLUS_CHECK3_D7,

DIST4_05M under each decoder method has:

median logical divergence area
<=
HYPER20_BASELINE under the same method,

AND

sustained exact logical recovery rate
>=
HYPER20_BASELINE under the same method,

AND

false applied logical flips
<=
HYPER20_BASELINE under the same method.

CHECK_ONLY_NO_REGRESSION

TRUE iff for:

CHECK4_BIT0_D6,
CHECK4_BIT0_D7,
CHECK4_BITS01_D6,

DIST4_05M under each decoder method has:

median logical divergence area
<=
HYPER20_BASELINE under the same method,

AND

false applied logical flips
<=
HYPER20_BASELINE under the same method.

BASE_WEAK_DYNAMIC_GAIN

Evaluate GREEDY_BASELINE on:

BASE_WEAK4_MASK1106.

TRUE iff DIST4_05M has:

median logical divergence area
<
HYPER20_BASELINE,

AND

sustained exact logical recovery rate
>=
HYPER20_BASELINE,

AND

false applied logical flips
<=
HYPER20_BASELINE.

DIST3_WEAK_DYNAMIC_GAIN

Evaluate GREEDY_BASELINE on:

DIST3_WEAK5_MASK2243.

TRUE iff DIST4_05M has:

median logical divergence area
<
DIST3_05L,

AND

sustained exact logical recovery rate
>=
DIST3_05L,

AND

false applied logical flips
<=
DIST3_05L.

DIST4_BOUNDARY_PRESERVED

Evaluate GREEDY_BASELINE on:

DIST4_MIN6_MASK249.

TRUE iff DIST4_05M has:

sustained exact logical recovery rate
>0,

AND

false applied logical flip fraction
<=0.01.

This is a boundary signal,
not a requirement that 05M beat every other topology on its own minimum-distance mask.

DYNAMIC_DISTANCE_TRANSFER

TRUE iff:

LEGACY_LOGICAL_NO_REGRESSION
AND
CHECK_ONLY_NO_REGRESSION
AND
(
BASE_WEAK_DYNAMIC_GAIN
OR
DIST3_WEAK_DYNAMIC_GAIN
).

CROSSPLANE CORRELATED BOUNDARY

CHECK4_BITS01_D6 remains the frozen correlated-integrity adversarial family.

If CROSSPLANE2_GATE still false-repairs healthy logical state,
record the boundary.

No threshold change is allowed.

SINGLE-BIT SENSITIVITY

SINGLE_DATA1_D6 remains a report-only comparison.

The CROSSPLANE2_GATE is already known to trade single-plane logical sensitivity
for one-plane integrity-fault specificity.

05N must report,
not tune around,
that behavior.

MECHANICAL CONTROLS

Harness MUST verify:

- all three frozen topology matrices exactly;
- all three frozen static geometry summaries exactly;
- no-damage control identity for every topology/method/world;
- identical logical pre-damage trajectories across topologies and methods;
- 12 disjoint worlds;
- exact damage-family counts;
- topology-relative incident membership;
- deterministic safe-plane selection.

These controls are NON-EVIDENCE.

REPRODUCIBILITY

Two complete 12-world sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first 05N world begins do not alter:

- topology matrices;
- decoder methods;
- greedy iteration cap;
- cross-plane threshold;
- damage families;
- challenge masks;
- safe-plane rule;
- world seeds;
- horizons;
- metrics;
- transfer signals;
- repair timing.

PLAIN-SPEAK PREREGISTERED QUESTION

We found a much better way to arrange the same backup information.

Now we need to find out whether that actually helps the running system,
not just the math on paper.

So this test takes three layouts:

the original one,
the best distance-3 layout,
and the new distance-4 layout.

They all get the same worlds,
the same damage,
the same repair timing,
and the same old decoder.

We are not giving the new layout a smarter repair algorithm.

We will test the old damage cases,
plus two fault patterns that were specifically weak in the old layouts.

If the distance-4 layout recovers those weak patterns better
without making the normal cases or false-repair cases worse,
then the static topology improvement transfers into real repair behavior.

If it does not,
then the stronger matrix is mostly a coding-theory improvement
and the next bottleneck is the decoder or the dynamics rather than the representation.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05N DISTANCE-4 DYNAMIC REPAIR TRANSFER

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY DAMAGED-SCENARIO EXECUTION.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05n_dynamic_transfer_v1.py

Harness commit:

dd1a39f27eef62e268acd989c6d670590b0d2e36.

Git blob SHA:

e546ffc18579c059514033896398f49ac33863cb.

Source SHA-256:

b0e13fe095d7ec79ed541ffd2b28eafb024274b3168284c323567526d3571623.

Source bytes:

21101.

FROZEN IMPLEMENTATION

The harness carries forward the exact DG-1R-05I dynamic substrate and decoder family,
parameterized only by the three preregistered topology matrices:

- HYPER20_BASELINE;
- DIST3_05L;
- DIST4_05M.

Decoder methods remain exactly:

- GREEDY_BASELINE;
- CROSSPLANE2_GATE with PLANE_SUPPORT >= 2.

No decoder threshold,
repair timing,
CA rule,
mapped-block rule,
damage family,
challenge mask,
safe-plane rule,
world seed,
horizon,
metric,
or primary signal was altered after preregistration.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Exact topology / static-geometry assertions:

PASS.

Scenario-structure validations:

396.

This is:

12 worlds
x
3 topologies
x
11 frozen damage families.

No-damage topology-method controls:

72.

This is:

12 worlds
x
3 topologies
x
2 frozen decoder methods.

For every world,
the complete undamaged 32-step post-prefix logical trajectory was asserted byte-identical across all six topology x decoder configurations.

The 1024-step pre-damage logical state was likewise asserted identical across all topology x decoder configurations.

Static geometry reproduced exactly:

HYPER20_BASELINE:
rank 11;
kernel mask 4095;
single floor 6;
two-region floor 8;
global floor 3;
maximum pair co-occurrence 2;
80 incidences.

DIST3_05L:
rank 12;
kernel free;
single floor 6;
two-region floor 8;
global floor 3;
maximum pair co-occurrence 2;
80 incidences.

DIST4_05M:
rank 12;
kernel free;
single floor 6;
two-region floor 8;
global floor 4;
maximum pair co-occurrence 2;
80 incidences.

All three retain the exact frozen logical-region degree vector:

(7,7,7,7,7,6,6,7,6,7,7,6).

Frozen world seeds:

20260926060000
through
20260926060011.

No primary damaged scenario,
dynamic transfer metric,
repair comparison,
or primary transfer signal
was generated before this freeze.

REPRODUCIBILITY

Execute two complete 12-world primary sweeps from this exact frozen harness.

Serialized output SHA-256 must match exactly.

No RNG change.
No seed substitution.
No post-result tuning.

Once the first damaged primary world begins,
the frozen implementation and preregistered interpretation gates are closed to modification.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
