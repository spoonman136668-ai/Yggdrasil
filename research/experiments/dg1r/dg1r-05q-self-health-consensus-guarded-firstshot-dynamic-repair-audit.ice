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
