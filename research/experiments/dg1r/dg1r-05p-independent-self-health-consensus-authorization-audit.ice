TITLE: DG-1R-05P — Independent Self-Health Fingerprint Consensus Authorization Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / DETECTION-AND-AUTHORIZATION ONLY / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / HEALTHY-CELL CONSENSUS
BRANCH: dg1a-ar
PARENT: DG-1R-05O

PURPOSE

DG-1R-05N showed that stronger syndrome geometry does not automatically transfer into repair behavior.

DG-1R-05O showed why a naive coordinated decoder is unsafe:

a multi-cell coalition can lower syndrome weight
while pointing first toward healthy logical cells,
and integrity-only faults can attract apparently useful logical repairs.

DG-1R-05P asks:

CAN A COMPACT,
INDEPENDENT SELF-HEALTH WITNESS
TURN RAW COALITION AGREEMENT
INTO A SAFER AUTHORIZATION SIGNAL?

The test adds no repair mutation.

It evaluates detection and authorization only.

No candidate may alter logical state.

ARCHITECTURAL HYPOTHESIS

A logical repair coalition should not become authoritative solely because it improves the shared integrity syndrome.

Authorization should require agreement between at least two distinct evidence classes:

1. DISTRIBUTED INTEGRITY GEOMETRY
   — the frozen DIST4_05M syndrome;

2. CELL SELF-HEALTH HISTORY
   — a compact temporal fingerprint stored independently from the current logical block.

The fingerprint is not treated as infallible.

Its purpose is to test whether a small independent witness can reject
false syndrome descents
and provide bit-plane-specific support for true damage.

FROZEN REPRESENTATION

Use exact closed DG-1R-05M topology:

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

Frozen facts:

rank 12.
logical kernel 0.
single-region syndrome floor 6.
two-region syndrome floor 8.
global logical syndrome floor 4.
maximum pair co-occurrence 2.
80 integrity incidences.

BASE PERSISTENT STATE

48 logical bits.
80 integrity bits.

128 bits total.

SELF-HEALTH FINGERPRINT FAMILY

Each logical block contains four bit planes:

x0,x1,x2,x3.

A stored fingerprint is computed from the undamaged block state
and retained until the next normal state-commit boundary.

At authorization time,
the current block is fingerprinted again.

The observed fingerprint delta is:

stored_fingerprint XOR current_fingerprint.

Use one nested frozen linear family.

Fingerprint row 0:

x0 XOR x1 XOR x2 XOR x3.

Fingerprint row 1:

x1 XOR x3.

Fingerprint row 2:

x2 XOR x3.

Fingerprint row 3:

x3.

FP1 uses row 0 only.

FP2 uses rows 0 through 1.

FP3 uses rows 0 through 2.

FP4 uses rows 0 through 3.

The four-row transform is full rank.

Therefore FP4 is an exact four-bit temporal witness.

RESOURCE COST

FP0:

0 added bits per block.
0 added bits organism-wide.
128 total persistent bits.

FP1:

1 added bit per block.
12 added bits.
140 total persistent bits.

FP2:

2 added bits per block.
24 added bits.
152 total persistent bits.

FP3:

3 added bits per block.
36 added bits.
164 total persistent bits.

FP4:

4 added bits per block.
48 added bits.
176 total persistent bits.

05P makes no claim that these bits are the final implementation budget.

The purpose is to establish the detection / authorization value curve
before any repacking or budget tradeoff experiment.

PROVENANCE ASSUMPTION

The integrity syndrome and the temporal fingerprint are separate witness classes.

Multiple checks inside the integrity graph
do not count as multiple independent provenance classes.

Multiple fingerprint bits derived from the same stored cell history
do not count as multiple independent provenance classes.

Thus FP4 provides more information,
not four independent votes.

The primary uncorrelated audit assumes:

integrity corruption does not also alter the stored fingerprint.

Explicit correlated-forgery holdouts violate that assumption on purpose
and must be reported as a boundary.

COORDINATED CANDIDATE GENERATOR

Operate independently on each bit plane.

For a nonzero DIST4_05M syndrome:

enumerate logical block masks of Hamming weight 1 through 6.

A candidate is DESCENDING iff applying that candidate to the logical explanation
strictly lowers syndrome weight.

Order candidates by:

1. smallest candidate Hamming weight;
2. largest syndrome-weight reduction;
3. numerically smallest 12-bit candidate mask.

COORD6_SYNDROME_ONLY

Select the first candidate under that frozen ordering.

No fingerprint restriction.

FP CONSENSUS METHODS

Methods:

FP1_CONSENSUS
FP2_CONSENSUS
FP3_CONSENSUS
FP4_CONSENSUS.

For each method,
candidate search uses the same frozen COORD6 ordering,
but a candidate is eligible only if the combined proposed bit-plane flips
are compatible with the observed per-block fingerprint deltas.

For every block touched by a proposed repair:

predicted fingerprint delta from the proposed bit-plane flips
must equal
the observed fingerprint delta.

AND

the observed fingerprint delta must be nonzero.

For every block with a nonzero observed fingerprint delta:

the final combined proposal must explain that delta exactly.

A zero fingerprint delta is not affirmative self-health evidence for a repair.

If no candidate set satisfies both:

- strict syndrome descent;
- exact fingerprint-delta compatibility;

the method ABSTAINS.

For single-plane families,
this reduces to a bounded coalition search over that plane.

For targeted two-plane families,
candidate proposals from both affected syndrome planes are combined
before fingerprint compatibility is evaluated.

No repair is applied.

TRUTH LABELS

SAFE_AUTHORIZATION:

every proposed logical bit is actually damaged.

COMPLETE_AUTHORIZATION:

the proposal exactly equals all damaged logical bits
visible in the evaluated syndrome planes.

FALSE_AUTHORIZATION:

at least one proposed logical bit is healthy.

ABSTAIN:

no authorization.

The evaluator knows ground truth.

The detector does not.

PRIMARY AUDIT A — EXHAUSTIVE SINGLE-PLANE LOGICAL MASKS

For each bit plane 0 through 3:

evaluate all 4095 nonzero 12-block logical masks
on that same plane.

This yields:

16380 logical fault cases.

For each method record:

- complete authorization count;
- safe partial authorization count;
- false authorization count;
- abstention count;
- candidate coalition size;
- syndrome reduction;
- fingerprint resource cost.

This audit tests whether
self-health filtering can recover truth-aligned coordinated descent
without using an oracle.

PRIMARY AUDIT B — EXHAUSTIVE CHECK-ONLY SAFETY

For each bit plane independently,
evaluate every check-only integrity pattern of weight 1 through 4.

Per plane:

20 weight-1 patterns.
190 weight-2 patterns.
1140 weight-3 patterns.
4845 weight-4 patterns.

6195 per plane.

24780 total check-only cases.

No logical bit is damaged.

Any logical authorization is therefore FALSE_AUTHORIZATION.

Primary specificity signal:

INDEPENDENT_CHECK_ONLY_SPECIFICITY_B

TRUE for fingerprint depth B
iff FPB_CONSENSUS produces:

zero FALSE_AUTHORIZATION

across all 24780 uncorrelated check-only cases.

PRIMARY AUDIT C — FROZEN 05N COORDINATION CHALLENGES

Evaluate the three exact single-plane logical masks:

BASE_WEAK4_MASK1106:
blocks 1,4,6,10.

DIST3_WEAK5_MASK2243:
blocks 0,1,6,7,11.

DIST4_MIN6_MASK249:
blocks 0,3,4,5,6,7.

Run on each bit plane 0 through 3.

Primary signal:

CHALLENGE_COORDINATION_RECOVERY_B

TRUE iff FPB_CONSENSUS:

- produces COMPLETE_AUTHORIZATION
  for all 12 challenge-plane cases;
- produces zero FALSE_AUTHORIZATION.

PRIMARY AUDIT D — INTRA-CELL MULTI-PLANE HEALTH RESOLUTION

For every logical block:

evaluate all nonzero four-bit intra-block damage patterns.

This is:

12 blocks
x
15 nonzero plane masks
=
180 cases.

Integrity syndrome is generated on every damaged plane.

Record authorization by fingerprint depth.

Stratify by intra-block damage weight:

1,
2,
3,
4.

Expected resource interpretation is frozen but not a pass criterion:

FP1 has only one parity bit
and may miss even-weight intra-block changes.

FP2 adds a second direction.

FP3 has three independent hash coordinates
but remains compressive.

FP4 is exact.

Primary signals:

SINGLE_PLANE_CELL_HEALTH_B
TWO_PLANE_CELL_HEALTH_B
THREE_PLANE_CELL_HEALTH_B
FOUR_PLANE_CELL_HEALTH_B

TRUE iff FPB_CONSENSUS produces complete authorization
with zero false authorization
for every case in that stratum.

PRIMARY AUDIT E — CROSS-PLANE HEALTH ALIAS HOLDOUT

For every block and ordered pair of distinct planes (a,b):

damage the logical bit on plane a.

On plane b,
inject the first four topology-relative incident integrity-check faults for that block.

The logical block is unhealthy because of plane a.

The integrity-only syndrome on plane b may tempt a logical repair on a healthy bit plane.

Total:

12 blocks
x
4 choices of a
x
3 choices of b
=
144 cases.

Primary signal:

PLANE_ALIAS_SUPPRESSION_B

TRUE iff FPB_CONSENSUS:

- never authorizes a logical flip on healthy plane b;
- may authorize the true plane-a repair or abstain.

This directly tests whether block-level "I am unhealthy"
is incorrectly reused as authority for the wrong bit plane.

CORRELATED FORGERY BOUNDARY

This is a holdout boundary,
not a required success.

Construct two explicit correlated classes.

F1 — LOGICAL_PLUS_FINGERPRINT_ERASURE

For each single-bit logical fault,
also alter the stored fingerprint
so that the observed fingerprint delta becomes zero.

This models corruption of both:

- current logical state;
- its self-health history.

F2 — CHECK_ONLY_PLUS_FALSE_FINGERPRINT_SUPPORT

Use check-only patterns that generate a COORD6 logical candidate.

Alter stored fingerprints on the proposed healthy logical blocks
so their observed fingerprint deltas exactly match the false proposal.

This models an integrity fault plus a coordinated false self-health witness.

Record:

CORRELATED_FORGERY_FAILURE_B

TRUE iff any false authorization or unsafe miss occurs.

This signal is expected to remain possible.

05P must not reinterpret correlated-forgery failure
as a reason to count the two corrupted paths as independent evidence.

CONSENSUS SIGNAL

INDEPENDENT_CONSENSUS_GAIN_B

TRUE iff all are TRUE:

INDEPENDENT_CHECK_ONLY_SPECIFICITY_B
AND
CHALLENGE_COORDINATION_RECOVERY_B
AND
PLANE_ALIAS_SUPPRESSION_B

AND

the method has zero false authorization
across primary audits A through E.

The intra-cell weight-stratified signals are reported separately
to expose resource / sensitivity tradeoffs.

No fingerprint depth is declared preferred in advance.

Selection,
if justified later,
must be based on the frozen result table
and a separately documented resource tradeoff.

MECHANICAL CONTROLS

Harness MUST assert:

- exact DIST4_05M topology;
- exact static geometry;
- exact nested fingerprint rows;
- FP4 transform rank = 4;
- exact resource totals 128,140,152,164,176;
- exact logical case counts;
- exact check-only case counts;
- exact challenge masks;
- exact cross-plane alias case count;
- candidate bound = 6;
- candidate ordering exactly as frozen;
- no logical mutation;
- no repair application;
- truth labels are evaluator-only.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary case begins do not alter:

- topology;
- fingerprint rows;
- fingerprint depth definitions;
- candidate bound;
- candidate ordering;
- compatibility rule;
- truth labels;
- primary case families;
- signals;
- correlated-forgery holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

The last experiment showed that a group of cells can make the shared warning look better
and still be the wrong group.

So now each cell gets a tiny independent memory of what it looked like
before the suspected damage.

The repair coalition does not get permission merely because the global checks agree.

The cells it wants to change must also be able to say:

"Yes — the exact bits you think changed
match my own independent health record."

We will test one,
two,
three,
and four bits of that self-health memory per cell.

We will not repair anything yet.

We are only asking whether the consensus is trustworthy enough
to authorize a repair.

We will also deliberately corrupt both evidence paths
to prove that agreement is not the same thing as independence.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05P SELF-HEALTH CONSENSUS AUTHORIZATION

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY AUTHORIZATION CASE.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05p_self_health_consensus_v1.py

Harness source commit:

052f3cc00dcaccf9abd8c4e0df7003900bcded74.

Git blob SHA:

f8975a8fe5f87c62bf0c1f3af90a3a0cef241a98.

Source SHA-256:

41dfa288ffc542d1bc536ca676ad8f34712338c3f73d66e05949b68c14901259.

Source bytes:

15319.

IMPLEMENTATION ALIGNMENT

The frozen harness implements:

- exact DIST4_05M topology;
- COORD6 candidate masks of Hamming weight 1 through 6;
- candidate ordering by smallest coalition size, largest syndrome reduction, then numeric mask;
- FP1 through FP4 nested temporal fingerprint rows exactly as preregistered;
- exact per-block fingerprint-delta compatibility;
- combined multi-plane proposals before fingerprint compatibility;
- detection / authorization only;
- no logical repair mutation.

For multi-plane cases, the implementation deterministically enumerates active planes in ascending plane index and the already-frozen per-plane COORD6 candidate order. This resolves combination traversal only; it does not alter candidate eligibility, fingerprint compatibility, or any success signal.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Exact static geometry:

rank 12;
kernel count 0;
single-region floor 6;
two-region floor 8;
global logical floor 4;
maximum pair co-occurrence 2;
80 incidences;
exact degree vector
(7,7,7,7,7,6,6,7,6,7,7,6).

Fingerprint transform ranks:

FP1 = 1.
FP2 = 2.
FP3 = 3.
FP4 = 4.

Exact resource totals:

FP0 = 128.
FP1 = 140.
FP2 = 152.
FP3 = 164.
FP4 = 176.

Frozen case counts mechanically asserted:

Audit A = 16380.
Audit B = 24780.
Audit C = 12.
Audit D = 180.
Audit E = 144.

Candidate bound:

6 logical blocks.

Candidate masks within bound:

2509.

No primary authorization case,
truth-performance result,
specificity result,
challenge result,
alias result,
or correlated-forgery result
was generated before this freeze.

REPRODUCIBILITY

Two complete deterministic frozen sweeps.

Serialized output SHA-256 must match exactly.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
