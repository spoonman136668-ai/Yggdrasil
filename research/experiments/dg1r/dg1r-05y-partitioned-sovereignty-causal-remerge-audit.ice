TITLE: DG-1R-05Y — Partitioned Sovereignty and Causal Re-Merge Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / PARTITION-AND-MERGE GOVERNANCE AUDIT / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / PARTITIONED SOVEREIGNTY
BRANCH: dg1a-ar
PARENT: DG-1R-05X

PURPOSE

DG-1R-05X established that the closed governance layers compose safely under explicit cross-layer transaction ordering.

A developmental organism must also survive temporary communication partitions.

During isolation:

- healthy sub-populations may still observe local damage;
- role demand may change;
- witnesses may rotate;
- causal histories may advance.

But a disconnected partition cannot prove that no concurrent valid history exists elsewhere.

DG-1R-05Y asks:

CAN TEMPORARILY DISCONNECTED HEALTHY CELL POPULATIONS
MAKE BOUNDED PROVISIONAL DECISIONS
AND LATER RE-MERGE
WITHOUT POPULATION-SIZE AUTHORITY,
STALE OVERWRITE,
PROVENANCE DOUBLE-COUNTING,
OR PERMANENT SPLIT BRAIN?

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No production mutation.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

DG-1R-05 canonical frozen primary remains UNSPENT.

FROZEN COMPOSED SUBSTRATE

Use the closed DG-1R-05X semantic contracts unchanged:

- FP2 / ROLE2 phenotype mapping;
- damage-before-identity ordering;
- FP2-qualified repair authority;
- role-preserving within-role adaptation;
- four-class governance provenance;
- atomic role commit;
- verified lineage before vote;
- append-only causal-edge registry;
- unique generation seal;
- lineage-qualified registry quorum;
- stale-generation rejection;
- abstention propagation;
- no provenance-slot multiplication.

05Y does not retune component thresholds.

PARTITION FIXTURE

12 cells.

Partition A:

cells 0 through 5.

Partition B:

cells 6 through 11.

Pre-partition global commit:

BASE0.

Both partitions begin from the exact same authoritative snapshot:

- role generation 0 for every cell;
- ROLE(cell) = cell mod 4;
- FP2 baseline matches role;
- peer role records match role;
- witness lineage generation 0;
- registry seal generation 0.

PARTITION-SCOPED PROVENANCE

Clean independent partition fixture:

Partition A governance roots:

R0,R1,R2,R3.

Partition B governance roots:

R4,R5,R6,R7.

Each partition therefore has a complete internally disjoint four-class governance fixture.

This allows 05Y to test bounded provisional governance without assuming one side must remain inert.

A separate shared-ancestry audit deliberately violates inter-partition independence.

PROVISIONAL AUTHORITY

While disconnected:

a locally valid partition event may become:

PARTITION_PROVISIONAL.

It may update that partition's working view.

It does NOT become GLOBAL_AUTHORITATIVE.

Every provisional event records:

- event_id;
- partition_id;
- parent_global_commit;
- target cell;
- operation type;
- target generation before;
- target generation after;
- verified provenance root set;
- registry seal generation;
- exact causal parent event IDs.

No event may erase its pre-partition global ancestor.

MERGE AUTHORITY

On reconnection,
the merge engine consumes both partition histories plus BASE0.

Population size,
holder count,
and raw event count are non-authoritative.

Frozen merge rules:

M1 — COMMON ANCESTOR REQUIRED

Every candidate event must descend from the last common globally committed history.

M2 — STALE HISTORY LOSES TO A VERIFIED DESCENDANT

If one candidate history is a strict verified causal ancestor of the other for the same target,
the descendant supersedes the ancestor.

M3 — CONCURRENT NON-CONFLICTING EVENTS COMMUTE

Concurrent events affecting different targets may merge
when each event independently satisfies its frozen local governance and registry contracts.

M4 — CONCURRENT SAME-TARGET IDENTICAL OUTCOME COALESCES

If both partitions independently reach the same target role,
same target generation,
and same phenotype state from the same common ancestor,
the merge may coalesce the duplicate outcome.

The two histories remain two causal paths,
but they do not create two authority votes.

M5 — CONCURRENT SAME-TARGET CONFLICT DOES NOT USE MAJORITY

If concurrent valid histories produce different authoritative outcomes
for the same target generation:

- neither provisional branch wins by partition size;
- neither wins by event count;
- neither wins by holder count.

The target returns to the last common globally committed state
and requires a fresh post-merge governance transaction.

Other non-conflicting targets may still merge.

M6 — SHARED PRE-PARTITION PROVENANCE IS COUNTED ONCE

Evidence copied into both partitions before disconnection
remains one lineage.

Partition separation does not mint independence.

M7 — INSUFFICIENT LOCAL ROOTS CANNOT MINT ELIGIBLE PROVISIONAL AUTHORITY

A partition event lacking its required independent governance or registry roots
is recorded only as:

LOCAL_OBSERVATION.

It is ineligible for merge authority.

M8 — MERGE COMMIT IS ATOMIC PER TARGET

A target's merged authority updates:

- role / phenotype;
- peer role history;
- target generation;
- relevant witness lineage generation;
- registry seal generation

as one target-scoped transaction.

Failure restores that target to the last common committed state.

M9 — GLOBAL GENERATION MONOTONICITY

A merged lower or equal replay cannot overwrite a newer global generation.

M10 — PROVISIONAL STATUS CLEARS ONLY AFTER MERGE RESOLUTION

After reconnection,
every provisional event becomes exactly one of:

- MERGED_GLOBAL;
- SUPERSEDED;
- COALESCED;
- ROLLED_BACK_CONFLICT;
- REJECTED_STALE;
- REJECTED_INELIGIBLE.

No unresolved provisional event may silently remain authoritative.

METHODS

1. POPULATION_MAJORITY_MERGE

Negative control.

Conflicts are resolved in favor of the partition with more nominal holders.

If equal,
use event count,
then lexicographic partition ID.

2. CAUSAL_PROVENANCE_MERGE

Candidate architecture.

Uses M1 through M10.

PRIMARY AUDIT A — CLEAN PARTITION / NO MUTATION

One split / rejoin case.

Neither partition changes state.

Required result:

exact BASE0 restoration,
zero synthetic events,
zero generation change,
zero split brain.

Signal:

CLEAN_PARTITION_REJOINS_EXACTLY.

PRIMARY AUDIT B — ONE-SIDED LEGITIMATE PROVISIONAL ACTION

For every cell:

B1:
TRUE_SINGLE repair.

12 cases.

B2:
one role-preserving internal adaptation.

12 cases.

B3:
each of three legitimate alternative-role migrations.

36 cases.

Total:

60.

Only the partition containing the target acts.

Required result:

eligible provisional event merges globally exactly once.

Signal:

ONE_SIDED_PROVISIONAL_ACTION_MERGES.

PRIMARY AUDIT C — COMPATIBLE CHANGES ON BOTH PARTITIONS

For every target pair:

one target from A,
one target from B.

6 x 6
=
36 cases.

Both partitions perform a legitimate +1 role migration on their own target.

The two concurrent events affect different targets.

Required result:

both merge,
regardless of which partition history is presented first.

Signal:

DISJOINT_CONCURRENT_EVENTS_COMMUTE.

PRIMARY AUDIT D — CONFLICTING SAME-TARGET ROLE MIGRATION

For every cell:

choose ordered pair of distinct alternative roles.

Three alternatives per base role.

3 x 2
=
6 ordered conflicts per cell.

12 x 6
=
72 cases.

Partition A provisional history and Partition B provisional history
both descend from BASE0
but propose different generation-1 roles for the same target.

Required candidate result:

- target rolls back to BASE0 role;
- target global generation remains 0;
- conflict marked ROLLED_BACK_CONFLICT;
- fresh post-merge transaction required;
- zero split brain.

Population majority control is expected to choose one branch.

Signal:

CONCURRENT_ROLE_CONFLICT_ABSTAINS.

PRIMARY AUDIT E — IDENTICAL CONCURRENT SAME-TARGET OUTCOME

For every cell
and every alternative role:

36 cases.

Both partitions independently reach the same role and generation
from BASE0.

Required result:

one global role-generation-1 outcome.

Two histories do not count as two authority votes.

Signal:

IDENTICAL_CONCURRENT_OUTCOME_COALESCES.

PRIMARY AUDIT F — SHARED-ANCESTOR PROVENANCE FANOUT ACROSS PARTITIONS

For every cell,
replicate one pre-partition governance root into both partitions
through holder counts:

4,
8,
16,
32.

12 x 4
=
48 cases.

Attempt to construct a four-slot merge quorum from descendants of that one root.

Required result:

no independent merge quorum.

Signal:

PARTITIONING_DOES_NOT_MULTIPLY_PROVENANCE.

PRIMARY AUDIT G — ASYMMETRIC ROOT LOSS

For each partition
and each one missing governance root:

2 x 4
=
8 cases.

The affected partition attempts one legitimate role migration.

Its event lacks a complete independent local governance fixture.

Required result:

LOCAL_OBSERVATION only.

Merge authority:

REJECTED_INELIGIBLE.

Signal:

INSUFFICIENT_PARTITION_ROOTS_CANNOT_MINT_AUTHORITY.

PRIMARY AUDIT H — STALE PARTITION REPLAY

For every cell:

first establish a merged global generation-1 role change.

Then reconnect a stale partition replaying the BASE0 generation-0 role.

12 cases.

Required result:

global generation 1 preserved.

Signal:

STALE_PARTITION_REPLAY_REJECTED.

PRIMARY AUDIT I — PROVISIONAL EVENT WITHOUT REGISTRY CLOSURE

For each partition
and every one unavailable registry root while the other three remain disjoint:

2 x 4
=
8 cases.

Control case with two unavailable roots per partition:

2 x 6
=
12 cases.

Total:

20.

Three independent registry roots:

event may remain eligible.

Only two:

event is ineligible.

Signal:

PARTITION_REGISTRY_LIVENESS_BOUND_PRESERVED.

PRIMARY AUDIT J — NON-CONFLICTING MERGE WITH ONE CONFLICTING TARGET

For every target in A
and every target in B:

36 cases.

Create:

- one valid role migration on A target;
- one valid role migration on B target;
- an additional concurrent conflicting role migration for the A target from the other partition.

Required result:

- B target merges successfully;
- A target rolls back to BASE0;
- no global transaction-wide loss of the non-conflicting B event.

Signal:

TARGET_SCOPED_CONFLICT_ISOLATION.

PRIMARY AUDIT K — STALE EVENT ORDER / INPUT PERMUTATION

For the 36 compatible two-partition cases from Audit C:

evaluate both presentation orders:

A then B.
B then A.

72 merge presentations.

Required result:

byte-identical final authoritative state.

Signal:

MERGE_ORDER_INDEPENDENT_FOR_COMMUTING_EVENTS.

PRIMARY AUDIT L — PROVISIONAL STATUS EXHAUSTIVENESS

Collect every primary provisional event emitted by Audits B through K.

After merge resolution:

every event must have exactly one terminal merge status.

No event may remain:

PARTITION_PROVISIONAL.

Signal:

NO_DANGLING_PROVISIONAL_AUTHORITY.

NEGATIVE CONTROL

POPULATION_MAJORITY_MERGE is expected to fail Audit D.

Partition sizes are intentionally allowed to differ in the control fixture:

A control population weight = 7.
B control population weight = 5.

The larger side is not more causally correct.

This negative control demonstrates why organism authority cannot be reduced to headcount after partition.

CORRELATED / CONSTITUTIONAL HOLDOUTS

Holdout only.

H1 — BOTH PARTITIONS FULLY COLLude ON THE SAME FALSE OUTCOME

Each partition has internally disjoint verified roots.

Both create the same false generation-1 role.

If candidate merge coalesces it:

DUAL_PARTITION_INDEPENDENT_COLLUSION_FAILURE.

Expected boundary.

H2 — ROOT COMPROMISE SPANS BOTH PARTITIONS

Reported root sets are disjoint,
but all roots descend from one actual causal source.

If merge treats them as independent:

PARTITION_ROOT_COMPROMISE_FAILURE.

Expected boundary.

H3 — FORGED COMMON ANCESTOR

Both partitions present a false parent_global_commit
that never belonged to the authoritative history.

If the merge accepts descendants of that false base:

FORGED_COMMON_ANCESTOR_FAILURE.

Expected boundary unless an external immutable global-commit anchor is assumed.

H4 — CROSS-PARTITION CAUSAL-LOG OMISSION

A valid conflicting event existed during isolation
but every causal registry path available at merge omits it.

If the remaining history merges as though the conflict never existed:

OMITTED_PARTITION_EVENT_FAILURE.

Expected boundary.

This preserves the distinction between:

MERGE LOGIC SAFETY

and

COMPLETE DISCOVERY OF ALL REAL-WORLD EVENTS.

PRIMARY PARTITION SIGNAL

PARTITIONED_SOVEREIGNTY_REMERGES

TRUE iff all are TRUE:

CLEAN_PARTITION_REJOINS_EXACTLY
AND
ONE_SIDED_PROVISIONAL_ACTION_MERGES
AND
DISJOINT_CONCURRENT_EVENTS_COMMUTE
AND
CONCURRENT_ROLE_CONFLICT_ABSTAINS
AND
IDENTICAL_CONCURRENT_OUTCOME_COALESCES
AND
PARTITIONING_DOES_NOT_MULTIPLY_PROVENANCE
AND
INSUFFICIENT_PARTITION_ROOTS_CANNOT_MINT_AUTHORITY
AND
STALE_PARTITION_REPLAY_REJECTED
AND
PARTITION_REGISTRY_LIVENESS_BOUND_PRESERVED
AND
TARGET_SCOPED_CONFLICT_ISOLATION
AND
MERGE_ORDER_INDEPENDENT_FOR_COMMUTING_EVENTS
AND
NO_DANGLING_PROVISIONAL_AUTHORITY

and

zero primary case ends with:

- split brain;
- stale generation authority;
- headcount-selected conflicting authority;
- duplicated provenance counted as independent;
- ineligible local observation promoted globally.

The correlated / constitutional holdouts are reported separately.

MECHANICAL CONTROLS

Harness MUST assert:

- 12 cells;
- exact A = 0..5;
- exact B = 6..11;
- exact BASE0 roles;
- exact partition root fixtures;
- exact M1 through M10 semantics;
- Audit A = 1;
- B = 60;
- C = 36;
- D = 72;
- E = 36;
- F = 48;
- G = 8;
- H = 12;
- I = 20;
- J = 36;
- K = 72 merge presentations;
- population majority control weights 7 and 5;
- no canonical DG-1R-05 execution;
- no component threshold retuning;
- truth labels evaluator-only.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary partition case begins do not alter:

- partition membership;
- provisional-event schema;
- merge rules M1 through M10;
- population-control weights;
- audit families;
- status labels;
- primary signals;
- correlated holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

What happens if the organism gets cut in half by communication failure?

Both halves may still be healthy enough to do useful work.

We do not want them frozen forever.

But we also do not want each half declaring itself the new whole organism.

So 05Y gives each side provisional authority.

A partition can repair local damage or prepare a role change
when it still has the independent evidence required by the existing rules.

But those decisions are marked provisional until the organism reconnects.

When the halves meet again:

- newer verified descendants beat stale history;
- changes to different cells can merge;
- two copies of the same outcome become one outcome;
- conflicting changes to the same cell do not get decided by which side has more cells.

A conflict returns that cell to the last common committed state
and asks for a fresh whole-organism decision.

That is slower than picking a winner.

It is also much safer.

The important principle is:

A DISCONNECTED MAJORITY IS NOT THE ORGANISM.

Causal history and independent provenance,
not population size,
decide what can become globally authoritative after reconnection.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
