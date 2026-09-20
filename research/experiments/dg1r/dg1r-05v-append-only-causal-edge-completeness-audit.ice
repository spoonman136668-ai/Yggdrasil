TITLE: DG-1R-05V — Append-Only Causal-Edge Completeness Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / DETECTION-AND-AUTHORIZATION ONLY / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / CAUSAL-EDGE REGISTRY
BRANCH: dg1a-ar
PARENT: DG-1R-05U

PURPOSE

DG-1R-05U showed that a child cannot safely certify its own lineage
and that independently issued parent attestations can reconstruct ancestry.

It also exposed the remaining ordinary completeness failure:

if the child and BOTH complete-parent observers collude,
an actual parent can still be omitted from the presented bundle.

DG-1R-05V asks:

CAN CAUSAL PARENT CONTRIBUTIONS
BECOME INDEPENDENTLY DISCOVERABLE EVENTS
SO THE CHILD DOES NOT CONTROL
WHICH PARENTS EXIST IN ITS HISTORY?

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No repair.
No role migration.
No health-memory update.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

DG-1R-05 canonical frozen primary remains UNSPENT.

PROVENANCE ROOTS

Carry forward the exact eight synthetic roots R0 through R7
and the DG-1R-05U recursive parent-certificate verification semantics.

REGISTRY REPLICAS

Use four registry replica slots:

REG_A
REG_B
REG_C
REG_D.

Each replica is a distinct holder.

Replica identity is not treated as proof of arbitrary-correlation independence.

A 3-of-4 quorum is used only for the frozen registry protocol.

Correlated three-replica forgery is tested separately as a boundary.

CAUSAL EDGE EVENT

Every causal parent contribution must register:

parent_id;
child_id;
child_generation;
parent_certificate_generation.

A causal contribution is ACTIVE only after the exact edge event
is present on at least three of the four registry replicas.

A parent contribution that reaches only one or two replicas
is not active and the child generation is not eligible for final lineage authorization.

The child does not choose whether a committed edge is returned by the verifier.

GENERATION SEAL

An append-only edge set alone does not prove that the set is complete at a particular time.

Therefore every child generation requires one registry generation seal.

The seal binds:

child_id;
child_generation;
sorted committed parent-ID set.

A seal is authoritative only when the exact same seal
is present on at least three of the four registry replicas.

The registry-derived parent set is valid only if:

1. every returned parent edge is quorum-committed;
2. exactly one authoritative seal exists for the child generation;
3. the seal's parent-ID set exactly equals the currently quorum-committed edge parent set;
4. every parent certificate verifies under the frozen DG-1R-05U rule.

If any condition fails:

ABSTAIN.

CHILD BUNDLE

The child may still present:

- any parent list;
- any lineage self-claim;
- any observer claims.

Under the candidate method these fields are non-authoritative for completeness.

The candidate lineage is reconstructed only from:

- registry-committed edges;
- registry seal;
- verified parent certificates.

METHODS

1. CHILD_BUNDLE_ONLY

Negative control.

Trust the child's presented parent set.

2. EDGE_QUORUM_NO_SEAL

Use quorum-committed registry edges
but do not require a generation seal.

Negative control.

3. SEALED_EDGE_REGISTRY

Candidate architecture.

Use the complete frozen edge + seal rules above.

PRIMARY AUDIT A — HONEST SINGLE-PARENT REGISTRATION

For each of eight roots:

create one child generation with exactly one causal parent.

Edge appears on all four replicas.

Matching seal appears on all four replicas.

Cases:

8.

Signal:

SINGLE_PARENT_REGISTRY_EXACT.

PRIMARY AUDIT B — HONEST TWO-PARENT REGISTRATION

For every unordered pair of roots:

28 child generations.

Both edges on all four replicas.

Matching seal on all four replicas.

Signal:

TWO_PARENT_REGISTRY_UNION_EXACT.

PRIMARY AUDIT C — CHILD OMITS A REGISTERED PARENT

For every unordered two-root pair
and both choices of omitted child-presented parent:

56 cases.

Registry still contains both committed edges
and a two-parent seal.

Candidate must reconstruct both parents.

Signal:

CHILD_OMISSION_IRRELEVANT.

PRIMARY AUDIT D — BOTH 05U COMPLETE-PARENT OBSERVERS OMIT A REGISTERED PARENT

Replay the 56 DG-1R-05U omitted-parent cases.

Child bundle and both bundle observers report only one parent.

Registry contains both committed parent edges
and the correct two-parent seal.

Signal:

OBSERVER_COLLUSION_BYPASSED_BY_REGISTRY.

TRUE iff candidate reconstructs both parents in all 56 cases.

PRIMARY AUDIT E — ONE REGISTRY REPLICA WITHHOLDS AN HONEST EDGE

For every two-root merge
and each of four choices of withholding replica:

112 cases.

One parent edge is present on exactly three replicas
and absent from the fourth.

Seal is present on all four replicas and names both parents.

Signal:

ONE_REPLICA_WITHHOLDING_TOLERATED.

TRUE iff all 112 reconstruct both parents.

PRIMARY AUDIT F — PARTIAL EDGE WRITE

For every two-root merge:

F1:
one parent edge exists on one replica only.

F2:
one parent edge exists on two replicas only.

The seal claims both parents.

Cases:

56.

Candidate must abstain because one causal contribution never became ACTIVE.

Signal:

PARTIAL_EDGE_WRITE_ABORTS.

PRIMARY AUDIT G — PARTIAL SEAL WRITE

For every honest two-root merge:

G1:
correct seal exists on one replica.

G2:
correct seal exists on two replicas.

Cases:

56.

Edges are fully committed.

Candidate must abstain.

Signal:

PARTIAL_SEAL_WRITE_ABORTS.

PRIMARY AUDIT H — DUPLICATE EDGE FANOUT

For every honest two-root merge:

replicate one exact parent edge many times
within and across replica-local logs.

Duplicate copies must collapse to one logical edge event.

Use duplicate multiplicities:

2,
4,
8,
16.

Cases:

28 x 2 parents x 4 multiplicities
=
224.

Signal:

DUPLICATE_EDGE_FANOUT_COLLAPSED.

PRIMARY AUDIT I — STALE GENERATION EDGE REPLAY

For each root:

construct child generations 1 through 4.

Replay an edge from generation g-1 into generation g.

The replayed tuple does not match the sealed current generation.

Cases:

32.

Signal:

STALE_EDGE_REPLAY_REJECTED.

PRIMARY AUDIT J — LATE EDGE AFTER SEAL

For every single-parent child generation:

first commit one parent edge and a matching one-parent seal.

Then quorum-commit a second parent edge for the same child generation
without replacing the old seal.

Cases:

8 x 7
=
56.

Candidate must abstain because:

current committed edge set != sealed edge set.

Signal:

LATE_EDGE_INVALIDATES_SEAL.

PRIMARY AUDIT K — CONFLICTING QUORUM SEALS

For every two-parent merge:

construct two different authoritative seals
for the same child generation.

Each reaches 3-of-4 replicas.

Cases:

28.

Candidate must abstain.

Signal:

CONFLICTING_SEALS_ABORT.

PRIMARY AUDIT L — HOLDER ROTATION

For every honest registry case from A and B:

change physical holder identities of the four registry replicas
without altering committed edge events,
seal contents,
or replica-vote structure.

Cases:

36.

Signal:

REGISTRY_HOLDER_ROTATION_PRESERVES_LINEAGE.

PRIMARY AUDIT M — ONE REGISTRY REPLICA UNAVAILABLE

Repeat all 28 honest two-parent merges
with each one of four registry replicas unavailable.

Remaining three replicas contain both edges and the seal.

Cases:

112.

Signal:

ONE_REGISTRY_REPLICA_LOSS_TOLERATED.

PRIMARY AUDIT N — REPLAY DG-1R-05U OMITTED-PARENT FAMILY

Use the exact 56 omitted-parent truth cases from 05U.

Derive lineage exclusively from SEALED_EDGE_REGISTRY.

Expected:

56 / 56 exact two-parent reconstruction.

Signal:

REGISTRY_REPRODUCES_05U_WITHOUT_BUNDLE_COMPLETENESS.

NEGATIVE CONTROLS

CHILD_BUNDLE_ONLY is expected to accept incomplete ancestry
when child and bundle observers omit a parent.

EDGE_QUORUM_NO_SEAL is expected to remain vulnerable to timing ambiguity:

a verifier may authorize from the current edge set
before a later causal edge becomes visible.

The generation seal is intended to close that window.

CORRELATED REGISTRY BOUNDARIES

Holdout only.

H1 — THREE-REPLICA OMITTING FORK

An actual parent edge exists in ground truth.

Three registry replicas present a consistent fork that omits it
and quorum-seal the incomplete set.

Record:

REGISTRY_MAJORITY_OMISSION_FAILURE.

Expected to remain possible.

H2 — THREE-REPLICA FALSE EDGE FORGERY

Three replicas invent one extra parent edge
and quorum-seal the forged set.

Record:

REGISTRY_MAJORITY_INSERTION_FAILURE.

Expected to remain possible.

H3 — TWO CORRUPTED REPLICAS

Two replicas attempt omission or insertion.

The two honest replicas preserve the original log.

Under 3-of-4 quorum,
no false edge or false seal may become authoritative.

Primary expectation:

reject / preserve correct lineage.

H4 — CONSTITUTIONAL ROOT COMPROMISE

Carry forward the DG-1R-05U root-of-trust boundary.

A perfect edge registry cannot repair falsely minted root independence.

PRIMARY REGISTRY SIGNAL

APPEND_ONLY_COMPLETENESS_GAIN

TRUE iff all are TRUE:

SINGLE_PARENT_REGISTRY_EXACT
AND
TWO_PARENT_REGISTRY_UNION_EXACT
AND
CHILD_OMISSION_IRRELEVANT
AND
OBSERVER_COLLUSION_BYPASSED_BY_REGISTRY
AND
ONE_REPLICA_WITHHOLDING_TOLERATED
AND
PARTIAL_EDGE_WRITE_ABORTS
AND
PARTIAL_SEAL_WRITE_ABORTS
AND
DUPLICATE_EDGE_FANOUT_COLLAPSED
AND
STALE_EDGE_REPLAY_REJECTED
AND
LATE_EDGE_INVALIDATES_SEAL
AND
CONFLICTING_SEALS_ABORT
AND
REGISTRY_HOLDER_ROTATION_PRESERVES_LINEAGE
AND
ONE_REGISTRY_REPLICA_LOSS_TOLERATED
AND
REGISTRY_REPRODUCES_05U_WITHOUT_BUNDLE_COMPLETENESS

and

zero false primary lineage authorization occurs
under SEALED_EDGE_REGISTRY.

REGISTRY_MAJORITY_OMISSION_FAILURE,
REGISTRY_MAJORITY_INSERTION_FAILURE,
and ROOT_COMPROMISE_FAILURE
are reported separately as constitutional / correlated boundaries.

MECHANICAL CONTROLS

Harness MUST assert:

- exactly eight provenance roots;
- exactly four registry replicas;
- edge quorum = 3;
- seal quorum = 3;
- exact edge tuple fields;
- exact seal fields;
- duplicate edge events collapse by tuple identity;
- no causal parent contribution is ACTIVE below edge quorum;
- no lineage is authorized without one unique authoritative seal;
- seal parent set must equal current quorum-committed edge parent set;
- exact Audit A count = 8;
- B = 28;
- C = 56;
- D = 56;
- E = 112;
- F = 56;
- G = 56;
- H = 224;
- I = 32;
- J = 56;
- K = 28;
- L = 36;
- M = 112;
- N = 56;
- no state mutation;
- truth labels evaluator-only.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary registry case begins do not alter:

- replica count;
- edge quorum;
- seal quorum;
- event tuple;
- seal tuple;
- duplicate-collapse rule;
- generation semantics;
- audit families;
- success signals;
- correlated-registry holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

The last experiment stopped a cell from rewriting its own family tree.

But the system still had to trust two witnesses
to say:

"yes, this folder contains every parent."

Now we remove that job from them.

When a parent contributes evidence,
that contribution has to be written into a shared append-only edge record first.

The child cannot later choose whether that parent appears.

We also add a generation seal.

That seal says:

"this was the complete committed parent set when this generation closed."

If another parent appears later,
or only half the registry saw the parent,
or two different seals exist,
the organism does not guess.

It abstains.

This is still distributed.

There is no permanent central lineage server.

But the edge registry has its own constitutional boundary:

if three of four registry replicas collude on the same false history,
the registry can still lie.

That boundary will be measured explicitly.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
