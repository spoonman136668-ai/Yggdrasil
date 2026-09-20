TITLE: DG-1R-05Q — Self-Health Consensus Guarded First-Shot Dynamic Repair Transfer Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-CANONICAL DYNAMIC REPAIR AUDIT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED AUTHORITY / DYNAMIC REPAIR
BRANCH: dg1a-ar
PARENT: DG-1R-05P

PURPOSE

DG-1R-05P established a positive NON-CANONICAL authorization result under an independent-witness model.

Raw coordinated syndrome descent was unsafe.
Self-health-qualified consensus eliminated false authorization across the frozen primary static audits,
while preserving an explicit correlated-forgery boundary.

DG-1R-05Q asks:

DOES THAT AUTHORIZATION SIGNAL
TRANSFER INTO ACTUAL DYNAMIC REPAIR
WHEN HEALTHY-CELL CONSENSUS
IS THE SOLE AUTHORITY FOR THE FIRST REPAIR ACTION?

This experiment intentionally tests one repair decision only.

It does not yet define:
- fingerprint refresh;
- repeated-episode authority;
- long-term drift accumulation;
- hibernation/reactivation health-history policy.

That larger lifecycle question is deferred.

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No production modification.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

DG-1R-05 canonical frozen primary remains UNSPENT.

FROZEN REPRESENTATION

Use exact closed DG-1R-05M DIST4 topology:

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

SELF-HEALTH VARIANTS

Carry forward the exact DG-1R-05P nested fingerprint family.

Fingerprint row 0:

x0 XOR x1 XOR x2 XOR x3.

Fingerprint row 1:

x1 XOR x3.

Fingerprint row 2:

x2 XOR x3.

Fingerprint row 3:

x3.

FP1 uses row 0.

FP2 uses rows 0 through 1.

FP3 uses rows 0 through 2.

FP4 uses rows 0 through 3.

Resource totals remain:

FP0:
128 total persistent bits.

FP1:
140 total persistent bits.

FP2:
152 total persistent bits.

FP3:
164 total persistent bits.

FP4:
176 total persistent bits.

The fingerprint remains ONE provenance class regardless of depth.

Four fingerprint bits do not become four independent witnesses.

FINGERPRINT COMMIT SEMANTICS

For every damaged episode:

1. run the undamaged 1024-step prefix;
2. immediately before damage,
   compute and store the selected fingerprint for every logical block;
3. inject the frozen damage;
4. at the first post-damage repair opportunity,
   compare current logical blocks against that stored pre-damage fingerprint;
5. authorize or abstain;
6. if authorized,
   apply the authorized logical repair;
7. disable all further repair for the remaining 32-step episode.

The stored fingerprint is not refreshed during the episode.

Because no second repair decision is allowed,
05Q does not test or assume any fingerprint refresh policy.

DYNAMICS

Carry forward exact DG-1R-05N substrate:

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

Order at each post-damage step:

repair opportunity,
then current input overwrite,
then logical CA update,
then recompute all 20 integrity checks.

Only the first post-damage step has repair enabled.

Pre-damage:

1024 steps.

Post-damage:

32 steps.

WORLD FAMILY

12 worlds.

Seeds:

20260926061000
through
20260926061011.

No prior DG-1R seed reuse.

Every method within a world receives the exact same:

- input sequence;
- mapped logical positions;
- mixed-rule assignment;
- damage family;
- post-damage input sequence.

METHODS

1. NO_REPAIR

Never applies a repair.

2. GREEDY_FIRSTSHOT

Exact DG-1R-05H one-block greedy inference,
but only at the first post-damage repair opportunity.

For each bit plane independently:

- choose the logical block whose flip gives the largest strictly positive syndrome-weight reduction;
- tie by lowest block index;
- do not select the same block twice in one plane;
- up to 4 logical flips per plane;
- stop when no logical flip strictly reduces syndrome weight.

Apply every inferred first-shot logical flip.

No later repair.

3. CROSSPLANE2_FIRSTSHOT

Run the exact same first-shot greedy inference.

For each logical block:

PLANE_SUPPORT =
number of bit planes on which greedy inference proposes a flip.

Apply inferred flips only for blocks with:

PLANE_SUPPORT >= 2.

No later repair.

4. COORD6_SYNDROME_FIRSTSHOT

Carry forward exact DG-1R-05P syndrome-only candidate generator.

For each nonzero syndrome plane:

enumerate logical block masks of Hamming weight 1 through 6.

A candidate is eligible iff it strictly lowers syndrome weight.

Frozen ordering:

1. smallest candidate Hamming weight;
2. largest syndrome-weight reduction;
3. numerically smallest 12-bit candidate mask.

For each active plane,
select the first candidate under that ordering.

For multi-plane lesions,
combine the per-plane proposals.

No fingerprint restriction.

Apply the combined first-shot proposal.

No later repair.

5 through 8. FP1_FIRSTSHOT, FP2_FIRSTSHOT, FP3_FIRSTSHOT, FP4_FIRSTSHOT

Use exact 05P candidate generator and frozen ordering.

For each active syndrome plane,
candidate search is identical to COORD6_SYNDROME_FIRSTSHOT.

A combined multi-plane proposal is eligible only if
the predicted per-block fingerprint delta
exactly equals
the observed stored-versus-current fingerprint delta.

For every touched block:

observed fingerprint delta must be nonzero.

For every block with nonzero observed fingerprint delta:

the final combined proposal must explain that delta exactly.

If no compatible proposal exists:

ABSTAIN.

If a proposal exists:

the healthy-cell consensus authorization is the sole repair authority.

Apply exactly that proposal.

No later repair.

No oracle.
No truth label enters the detector.

DAMAGE FAMILIES

Carry forward the exact DG-1R-05N eleven primary families.

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

Plus first two topology-relative incident integrity checks,
bit plane 0.

D. DATA2_PLUS_CHECK3_D7

Block 2 logical planes:

0,
1.

Plus first three topology-relative incident integrity checks,
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

I. BASE_WEAK4_MASK1106

Logical blocks:

1,
4,
6,
10.

Use exact DG-1R-05N safe-plane rule.

J. DIST3_WEAK5_MASK2243

Logical blocks:

0,
1,
6,
7,
11.

Use exact DG-1R-05N safe-plane rule.

K. DIST4_MIN6_MASK249

Logical blocks:

0,
3,
4,
5,
6,
7.

Use exact DG-1R-05N safe-plane rule.

SAFE-PLANE RULE

For challenge families:

choose the lowest bit plane
that is not the mapped input bit plane
for any affected mapped block.

No plane may be selected after observing decoder behavior.

CORRELATED-FORGERY HOLDOUTS

These are boundary tests,
not required successes.

CF1 — LOGICAL_PLUS_FINGERPRINT_ERASURE

Use SINGLE_DATA1_D6.

For each FP depth,
alter the stored fingerprint so that
the observed fingerprint delta for block 5 becomes zero
at the first repair opportunity.

No syndrome or logical state is otherwise altered.

This asks whether corruption of:

- current logical state;
- its self-health history

can suppress authorization.

Expected possible boundary:

FP consensus may abstain,
allowing the logical lesion to persist.

CF2 — CHECK_ONLY_PLUS_FALSE_FINGERPRINT_SUPPORT

Use CHECK4_BIT0_D6.

Before FP authorization,
compute the frozen COORD6_SYNDROME_FIRSTSHOT false logical proposal.

Alter the stored fingerprints of the proposed healthy blocks
so their observed fingerprint deltas exactly support that false proposal.

No logical bit is initially damaged.

This asks whether coordinated corruption of:

- integrity evidence;
- temporal self-health evidence

can create false repair authority.

Expected possible boundary:

false authorization remains possible.

05Q must not reinterpret CF1 or CF2
as evidence that the two corrupted witness paths were independent.

LESION ASSERTIONS

Harness MUST assert per world and family:

- exact logical flip count;
- exact integrity flip count;
- physical uniqueness;
- topology-relative incident membership;
- no duplicated integrity index;
- legacy logical lesions do not overlap current mapped logical positions;
- challenge safe plane obeys the frozen exclusion rule;
- stored fingerprint is computed before damage;
- no method modifies the stored fingerprint;
- exactly one repair opportunity occurs.

PRIMARY TELEMETRY

Per method,
family,
and world:

- proposed logical flips;
- applied logical flips;
- abstention;
- false proposed logical flips;
- false applied logical flips;
- complete first-shot correction;
- safe partial first-shot correction;
- first-shot syndrome weight before repair;
- first-shot syndrome weight after repair;
- first-shot fingerprint compatibility;
- first-shot candidate coalition size by plane;
- first-shot plane support for greedy methods;
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

Use exact evaluator-only definition:

an applied repair bit is FALSE if
its post-correction logical value does not match
the undamaged counterfactual logical bit
immediately before current input overwrite.

The detector never sees this label.

PRIMARY SIGNAL 1 — LEGACY_LOGICAL_PRESERVATION_B

For:

LOCAL_DATA2_D6,
DISTRIBUTED_DATA2,
DATA2_PLUS_CHECK2_D6,
DATA2_PLUS_CHECK3_D7,

TRUE for FPB_FIRSTSHOT iff:

- zero false applied logical flips;
- median logical divergence area <= CROSSPLANE2_FIRSTSHOT;
- sustained exact logical recovery rate >= CROSSPLANE2_FIRSTSHOT.

PRIMARY SIGNAL 2 — CHECK_ONLY_SPECIFICITY_B

For:

CHECK4_BIT0_D6,
CHECK4_BIT0_D7,
CHECK4_BITS01_D6,

TRUE for FPB_FIRSTSHOT iff:

- zero applied logical flips;
- zero false applied logical flips;
- median logical divergence area = 0.

PRIMARY SIGNAL 3 — SINGLE_BIT_RECOVERY_B

For SINGLE_DATA1_D6:

TRUE for FPB_FIRSTSHOT iff:

- complete first-shot correction in all 12 worlds;
- zero false applied logical flips;
- median logical divergence area = 0;
- sustained exact logical recovery rate = 1.0.

PRIMARY SIGNAL 4 — CHALLENGE_DYNAMIC_RECOVERY_B

For:

BASE_WEAK4_MASK1106,
DIST3_WEAK5_MASK2243,
DIST4_MIN6_MASK249,

TRUE for FPB_FIRSTSHOT iff:

- complete first-shot correction in all 36 challenge-world cases;
- zero false applied logical flips;
- median logical divergence area = 0 for each family;
- sustained exact logical recovery rate = 1.0 for each family.

PRIMARY SIGNAL 5 — FIRSTSHOT_AUTHORITY_TRANSFER_B

TRUE iff all are TRUE:

LEGACY_LOGICAL_PRESERVATION_B
AND
CHECK_ONLY_SPECIFICITY_B
AND
SINGLE_BIT_RECOVERY_B
AND
CHALLENGE_DYNAMIC_RECOVERY_B

AND

FPB_FIRSTSHOT has zero false applied logical flips
across all eleven primary damage families.

RESOURCE / SENSITIVITY REPORT

Do not preselect a fingerprint depth.

Report for FP1 through FP4:

- total persistent-state bits;
- primary signals;
- total applied repairs;
- abstentions;
- complete corrections;
- false applied flips.

05Q does not choose a final fingerprint depth.

Selection requires a later explicit resource tradeoff.

CORRELATED BOUNDARY SIGNALS

CF1_ERASURE_FAILURE_B:

TRUE iff fingerprint erasure causes
any unsafe miss
relative to the uncorrupted SINGLE_DATA1_D6 case.

CF2_FORGED_SUPPORT_FAILURE_B:

TRUE iff forged fingerprint support causes
any false applied logical repair
on initially healthy logical state.

These are expected to remain possible.

They are not part of FIRSTSHOT_AUTHORITY_TRANSFER_B.

MECHANICAL CONTROLS

Harness MUST verify:

- exact DIST4_05M topology;
- exact static geometry;
- exact 05P fingerprint rows and ranks;
- exact resource totals;
- exact 05P candidate bound and ordering;
- exact 05N dynamics and repair timing;
- 12 disjoint worlds;
- exact primary damage families;
- exact safe-plane rule;
- exact one-shot repair count;
- stored fingerprint computed before lesion;
- no fingerprint refresh;
- identical undamaged trajectories across all methods;
- no-damage identity;
- no detector access to truth labels.

These are NON-EVIDENCE.

REPRODUCIBILITY

Two complete 12-world sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary damaged world begins do not alter:

- topology;
- dynamics;
- repair timing;
- one-shot policy;
- fingerprint rows;
- candidate bound;
- candidate ordering;
- compatibility rule;
- damage families;
- challenge masks;
- safe-plane rule;
- world seeds;
- metrics;
- primary signals;
- correlated-forgery holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

05P showed that the cells can make a trustworthy repair decision
when their shared warning agrees with their own separate health memory.

05Q lets that consensus actually act once.

The cells get one chance,
immediately after damage,
to decide whether a repair is authorized.

If they authorize it,
that repair happens.

Then all repair is turned off
for the rest of the episode.

That keeps this experiment clean.

We are testing:

"Was the healthy-cell consensus right enough
to be the sole authority for this action?"

We are not yet testing:

"How should cells keep rewriting their health history forever?"

If the first-shot consensus repairs the difficult multi-cell injuries,
keeps the already-solved cases healthy,
and refuses false repairs from backup-check damage,
then distributed healthy-cell authority has transferred
from a static permission test
into an actual organism-level action.

We will still deliberately corrupt both evidence paths
to preserve the known constitutional boundary:

agreement is trustworthy only when its provenance is actually independent.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05Q FIRST-SHOT CONSENSUS REPAIR

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY DAMAGED WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05q_firstshot_dynamic_v1.py

Harness source commit:

42200edc88a5f05fcfd9dad60af8e6569ab8fc60.

Git blob SHA:

57c79ba365e4f3443d1c34322aec096cd8a9050d.

Source SHA-256:

6f6bb827f97352a45c47aa4932beeb4a505c83b06c1b3d81285c708b36e701ee.

Source bytes:

23938.

FROZEN IMPLEMENTATION

The harness carries forward:

- exact DIST4_05M topology;
- exact MIXED5 dynamics;
- 1024-step undamaged prefix;
- 32-step post-damage episode;
- repair before current input overwrite;
- exact DG-1R-05N primary damage families and safe-plane rule;
- exact DG-1R-05P fingerprint rows;
- exact DG-1R-05P COORD6 candidate bound and ordering;
- one first-shot repair opportunity only;
- no fingerprint refresh;
- no later repair.

Methods:

- NO_REPAIR;
- GREEDY_FIRSTSHOT;
- CROSSPLANE2_FIRSTSHOT;
- COORD6_SYNDROME_FIRSTSHOT;
- FP1_FIRSTSHOT;
- FP2_FIRSTSHOT;
- FP3_FIRSTSHOT;
- FP4_FIRSTSHOT.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Exact DIST4 static geometry:

rank 12;
kernel count 0;
single-region floor 6;
two-region floor 8;
global logical floor 4;
maximum pair co-occurrence 2;
80 incidences;
degree vector
(7,7,7,7,7,6,6,7,6,7,7,6).

Fingerprint ranks:

FP1 = 1.
FP2 = 2.
FP3 = 3.
FP4 = 4.

Resource totals:

FP0 = 128.
FP1 = 140.
FP2 = 152.
FP3 = 164.
FP4 = 176.

COORD6 candidate masks:

2509.

Lesion validations:

132.

This is:

12 worlds
x
11 frozen primary damage families.

No-damage controls:

96.

This is:

12 worlds
x
8 methods.

Every no-damage method applied zero logical repair
and remained byte-identical to its undamaged reference trajectory.

Repair opportunities per damaged episode:

1.

The harness explicitly asserts the expected FP1 parity alias:

damage to planes 0 and 1 of one cell
produces zero FP1 delta,
while FP2 retains nonzero evidence.

Frozen world seeds:

20260926061000
through
20260926061011.

No primary damaged world,
dynamic repair result,
primary transfer signal,
or correlated-forgery outcome
was generated before this freeze.

REPRODUCIBILITY

Execute two complete frozen 12-world sweeps.

Serialized output SHA-256 must match exactly.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL CLOSURE — DG-1R-05Q SELF-HEALTH CONSENSUS GUARDED FIRST-SHOT DYNAMIC REPAIR

DATE:
2026-09-20.

STATUS:
CLOSED /
REPRODUCIBLE /
FP2+ FIRST-SHOT AUTHORITY TRANSFER POSITIVE /
FP1 SAFE-BUT-UNDERINFORMED /
CORRELATED-FORGERY BOUNDARY PRESERVED /
NON-CANONICAL.

FROZEN PROVENANCE

Preregistration commit:

31e0c02812483f799a43fb724ba9737b991e3823.

Harness source commit:

42200edc88a5f05fcfd9dad60af8e6569ab8fc60.

Harness Git blob:

57c79ba365e4f3443d1c34322aec096cd8a9050d.

Harness source SHA-256:

6f6bb827f97352a45c47aa4932beeb4a505c83b06c1b3d81285c708b36e701ee.

Harness bytes:

23938.

Freeze commit:

e4e96b3ef65d442a01067a43bd94b7ec1d6e098e.

PRIMARY EXECUTION

Two complete frozen 12-world sweeps were executed.

Sweep 1 serialized output SHA-256:

8ca80d49fc87c730c28aff46e5f12fe9c4601bcfa218f357a17be0f0ce9f2ed9.

Sweep 2 serialized output SHA-256:

8ca80d49fc87c730c28aff46e5f12fe9c4601bcfa218f357a17be0f0ce9f2ed9.

BYTE_IDENTICAL_REPRODUCIBILITY:

TRUE.

MECHANICAL_VALID:

TRUE.

PRIMARY SIGNALS — FP1

LEGACY_LOGICAL_PRESERVATION:

FALSE.

CHECK_ONLY_SPECIFICITY:

TRUE.

SINGLE_BIT_RECOVERY:

TRUE.

CHALLENGE_DYNAMIC_RECOVERY:

TRUE.

ZERO_FALSE_APPLIED_PRIMARY:

TRUE.

FIRSTSHOT_AUTHORITY_TRANSFER:

FALSE.

PRIMARY SIGNALS — FP2

LEGACY_LOGICAL_PRESERVATION:

TRUE.

CHECK_ONLY_SPECIFICITY:

TRUE.

SINGLE_BIT_RECOVERY:

TRUE.

CHALLENGE_DYNAMIC_RECOVERY:

TRUE.

ZERO_FALSE_APPLIED_PRIMARY:

TRUE.

FIRSTSHOT_AUTHORITY_TRANSFER:

TRUE.

PRIMARY SIGNALS — FP3

All five signals above:

TRUE.

PRIMARY SIGNALS — FP4

All five signals above:

TRUE.

FP1 FAILURE MECHANISM

The frozen local and distributed legacy logical lesions damage planes 0 and 1 together.

Under FP1,
the sole fingerprint row is:

x0 XOR x1 XOR x2 XOR x3.

A simultaneous flip of planes 0 and 1 therefore contributes:

1 XOR 1
=
0.

The self-health witness reports zero delta.

As frozen,
zero fingerprint delta is not affirmative repair evidence.

Therefore FP1 correctly ABSTAINS rather than guessing.

Across the four two-plane legacy logical families,
FP1 produced:

48 / 48 abstentions.

It produced:

0 false applied logical flips.

This is a sensitivity failure,
not a specificity failure.

FP1 dynamic examples:

LOCAL_DATA2_D6:

complete first-shot correction:
0 / 12.

abstain:
12 / 12.

median logical divergence area:

2.697916666666667.

sustained exact logical recovery rate:

0.25.

DISTRIBUTED_DATA2:

complete first-shot correction:
0 / 12.

abstain:
12 / 12.

median logical divergence area:

4.885416666666666.

sustained exact logical recovery rate:

0.0.

FP2 / FP3 / FP4 LEGACY LOGICAL RESULT

For all four frozen legacy logical families,
FP2,
FP3,
and FP4 each produced:

complete first-shot correction:
12 / 12 per family.

false applied logical flips:
0.

median logical divergence area:
0.

sustained exact logical recovery rate:
1.0.

Thus FP2 is the minimum tested fingerprint depth
that carries enough information
for every frozen two-plane legacy injury.

CHECK-ONLY SPECIFICITY

For:

CHECK4_BIT0_D6,
CHECK4_BIT0_D7,
CHECK4_BITS01_D6,

all FP depths produced:

applied logical flips:
0.

false applied logical flips:
0.

median logical divergence area:
0.

Thus even FP1 retained the principal specificity gain
against integrity-only false repair.

For comparison:

GREEDY_FIRSTSHOT false-applied logical flips across the three families:

12,
12,
24.

CROSSPLANE2_FIRSTSHOT still false-repaired CHECK4_BITS01_D6:

24 false applied logical flips.

COORD6_SYNDROME_FIRSTSHOT likewise produced:

12,
12,
24

false applied logical flips.

SINGLE-BIT RECOVERY

SINGLE_DATA1_D6:

FP1,
FP2,
FP3,
FP4:

complete first-shot correction:
12 / 12.

false applied logical flips:
0.

median logical divergence area:
0.

sustained exact logical recovery rate:
1.0.

CROSSPLANE2_FIRSTSHOT:

complete first-shot correction:
0 / 12.

abstain:
12 / 12.

median logical divergence area:

2.7916666666666665.

Thus self-health qualification recovered the single-plane sensitivity
that the cross-plane support gate intentionally sacrificed.

COORDINATED CHALLENGE RECOVERY

For:

BASE_WEAK4_MASK1106,
DIST3_WEAK5_MASK2243,
DIST4_MIN6_MASK249,

every FP depth produced:

complete first-shot correction:
12 / 12 per family.

false applied logical flips:
0.

median logical divergence area:
0.

sustained exact logical recovery rate:
1.0.

This is the dynamic transfer that DG-1R-05N lacked.

The exact same coordinated lesions
that trapped the one-step greedy decoder
were repaired completely
when syndrome geometry was qualified by independent self-health evidence.

RAW COORD6 CONTROL

COORD6_SYNDROME_FIRSTSHOT demonstrated why the fingerprint gate matters.

BASE_WEAK4_MASK1106:

complete:
0 / 12.

false applied logical flips:
24.

median logical divergence area:

9.208333333333334.

DIST3_WEAK5_MASK2243:

complete:
0 / 12.

false applied logical flips:
12.

median logical divergence area:

7.968749999999999.

DIST4_MIN6_MASK249:

complete:
12 / 12.

false applied logical flips:
0.

Thus larger coordinated search can cross a plateau,
but without independent health evidence
it can cross it in the wrong direction.

RESOURCE / SENSITIVITY RESULT

FP1:

total persistent bits:
140.

primary abstentions:
84.

applied logical repairs:
192.

complete primary corrections:
84.

false applied primary flips:
0.

FP2:

total persistent bits:
152.

primary abstentions:
36.

applied logical repairs:
312.

complete primary corrections:
132.

false applied primary flips:
0.

FP3:

total persistent bits:
164.

primary abstentions:
36.

applied logical repairs:
312.

complete primary corrections:
132.

false applied primary flips:
0.

FP4:

total persistent bits:
176.

primary abstentions:
36.

applied logical repairs:
312.

complete primary corrections:
132.

false applied primary flips:
0.

Within the frozen 05Q family,
FP2 is the minimum depth that attains full first-shot authority transfer.

This is NOT a final depth selection.

DG-1R-05P already established a broader intra-cell resolution frontier:

FP2 does not resolve every possible two-plane intra-cell pattern.

FP3 resolves every tested one-,
two-,
and three-plane intra-cell pattern
but not the all-four-plane change.

FP4 resolves the complete four-plane cell state exactly.

Therefore 05Q establishes:

minimum depth for this dynamic family = FP2,

not:

globally sufficient organism health memory = FP2.

CORRELATED-FORGERY BOUNDARY

CF1 — LOGICAL PLUS FINGERPRINT ERASURE

For every FP depth:

12 / 12 abstentions.

CF1_ERASURE_FAILURE:

TRUE.

Median logical divergence area:

2.7916666666666665.

Thus when logical damage and its temporal self-health evidence
are coherently corrupted together,
the authority mechanism can miss the lesion.

CF2 — CHECK-ONLY PLUS FORGED FINGERPRINT SUPPORT

For every FP depth:

false applied logical flips:
12.

CF2_FORGED_SUPPORT_FAILURE:

TRUE.

Median logical divergence area:

2.7916666666666665.

Thus forged agreement across both witness classes
can create false authority.

The constitutional boundary is preserved:

agreement is evidence only to the extent
that the contributing provenance classes are actually independent.

TECHNICAL INTERPRETATION

DG-1R-05Q establishes the first dynamic transfer
from independently-qualified healthy-cell consensus
to an actual logical repair action.

The result separates three properties:

1. SEARCH REACHABILITY

COORD6 can cross multi-cell plateaus
that defeat the frozen one-block greedy decoder.

2. AUTHORIZATION SPECIFICITY

COORD6 alone is unsafe.

Independent temporal self-health evidence
removes the false first-shot repairs
across the frozen primary family.

3. HEALTH-WITNESS INFORMATION DEPTH

One self-health bit is not enough
when two changed planes alias to the same fingerprint.

Two bits are enough for every primary dynamic lesion in 05Q.

Broader 05P coverage still justifies retaining FP3 and FP4
as candidates for later lifecycle testing.

Most importantly,
the successful FP methods have no central oracle.

The repair authority is the qualified cell population itself.

The immutable requirement is only constitutional:

a repair coalition may exercise authority
when its shared structural evidence
and an independently-provenanced self-health witness
are mutually compatible.

PLAIN-SPEAK INTERPRETATION

The cells were allowed to act for real this time.

Not repeatedly.
Just once,
right after the injury.

When they only followed the shared warning system,
they could make confident but wrong group repairs.

When they also had to match their own separate health memory,
the false repairs disappeared in the normal test family.

And the difficult multi-cell injuries
that the old repairer could see but could not solve
were fixed immediately.

One bit of health memory per cell was too crude.

Two damaged parts inside the same cell could cancel each other out
and make that cell look healthy.

Two bits per cell were enough for every injury in this particular dynamic test.

That does not mean two bits are enough forever.

Our earlier exhaustive test already found cell-damage patterns
where deeper fingerprints carry information that FP2 loses.

The bigger result is this:

HEALTHY-CELL CONSENSUS DID FUNCTION
AS THE SOLE OPERATIONAL AUTHORITY
FOR A REAL REPAIR ACTION,

with no central repair oracle,

as long as the consensus was qualified
by genuinely independent self-health evidence.

And when we deliberately corrupted both evidence paths,
the organism could still be fooled.

That is exactly the boundary we wanted to preserve.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05R —

CONSENSUS-GATED HEALTH-MEMORY COMMIT AND DRIFT AUDIT.

The remaining architectural problem is lifecycle.

05Q deliberately avoided fingerprint refresh.

A real developmental organism cannot keep one old health snapshot forever.

Its cells must be able to change legitimately,
specialize,
learn,
reorganize,
hibernate,
reactivate,
and then update what "healthy me" means.

But an unsafe refresh rule can absorb corruption into the health record
and permanently redefine damage as normal.

05R should therefore test:

- normal clean evolution followed by health-memory refresh;
- abrupt damage immediately before a proposed refresh;
- slow internal drift;
- legitimate coordinated adaptation;
- independent-quorum-gated refresh versus self-only refresh;
- whether corrupted cells can poison the next health baseline;
- abstention when refresh provenance is not independently sufficient.

No repeated repair policy should be added
until health-memory commit itself is shown not to normalize corruption.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
