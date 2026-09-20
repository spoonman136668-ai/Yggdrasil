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


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05V APPEND-ONLY CAUSAL-EDGE COMPLETENESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY REGISTRY CASE.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05v_causal_edge_registry_v1.py

Harness source commit:

259b296da36ab8dd7422abcead1e8e469ae90f29.

Git blob SHA:

0636a715757655149aaab7dd41385f652458bae4.

Source SHA-256:

1232e16f1afb154833c4f34a582c5ffc9303e049ef2e4c31801d7a403437017b.

Source bytes:

15483.

FROZEN IMPLEMENTATION

The harness implements:

- exactly eight provenance roots;
- exactly four registry replicas;
- 3-of-4 edge quorum;
- 3-of-4 generation-seal quorum;
- exact causal edge tuples;
- exact seal tuples;
- replica-local duplicate collapse by event identity;
- child-bundle-only negative control;
- edge-quorum-without-seal timing negative control;
- SEALED_EDGE_REGISTRY candidate rule;
- one-replica withholding;
- partial edge writes;
- partial seal writes;
- duplicate edge fanout;
- stale-generation replay;
- late edge after seal;
- conflicting authoritative seals;
- registry-holder rotation;
- one-replica unavailability;
- DG-1R-05U omitted-parent replay;
- correlated three-replica omission and insertion holdouts;
- two-corrupt-replica control;
- constitutional root-compromise holdout.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Case counts:

A = 8.
B = 28.
C = 56.
D = 56.
E = 112.
F = 56.
G = 56.
H = 224.
I = 32.
J = 56.
K = 28.
L = 36.
M = 112.
N = 56.

No primary registry result,
completeness result,
seal result,
timing result,
or correlated-registry result
was generated before this freeze.

REPRODUCIBILITY

Execute two complete deterministic sweeps from this exact frozen harness.

Serialized output SHA-256 must match exactly.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL CLOSURE — DG-1R-05V APPEND-ONLY CAUSAL-EDGE COMPLETENESS AUDIT

DATE:
2026-09-20.

STATUS:
CLOSED /
REPRODUCIBLE /
APPEND-ONLY COMPLETENESS GAIN POSITIVE /
BUNDLE-COMPLETENESS DEPENDENCY REMOVED /
THREE-REPLICA CORRELATED REGISTRY BOUNDARY PRESERVED /
NON-CANONICAL.

FROZEN PROVENANCE

Preregistration commit:

2a0b6e4aa71df5ef50773b90d467c96c1d46616d.

Harness source commit:

259b296da36ab8dd7422abcead1e8e469ae90f29.

Harness Git blob:

0636a715757655149aaab7dd41385f652458bae4.

Harness source SHA-256:

1232e16f1afb154833c4f34a582c5ffc9303e049ef2e4c31801d7a403437017b.

Harness bytes:

15483.

Freeze commit:

106629d1dcef327f085185644c77c109c751e78b.

PRIMARY EXECUTION

Two complete deterministic frozen sweeps were executed.

Sweep 1 serialized output SHA-256:

1d90729a75f401a96576032ef674146d5fb49295a02afac4928a457020745194.

Sweep 2 serialized output SHA-256:

1d90729a75f401a96576032ef674146d5fb49295a02afac4928a457020745194.

BYTE_IDENTICAL_REPRODUCIBILITY:

TRUE.

MECHANICAL_VALID:

TRUE.

PRIMARY SIGNALS

SINGLE_PARENT_REGISTRY_EXACT:
TRUE.

TWO_PARENT_REGISTRY_UNION_EXACT:
TRUE.

CHILD_OMISSION_IRRELEVANT:
TRUE.

OBSERVER_COLLUSION_BYPASSED_BY_REGISTRY:
TRUE.

ONE_REPLICA_WITHHOLDING_TOLERATED:
TRUE.

PARTIAL_EDGE_WRITE_ABORTS:
TRUE.

PARTIAL_SEAL_WRITE_ABORTS:
TRUE.

DUPLICATE_EDGE_FANOUT_COLLAPSED:
TRUE.

STALE_EDGE_REPLAY_REJECTED:
TRUE.

LATE_EDGE_INVALIDATES_SEAL:
TRUE.

CONFLICTING_SEALS_ABORT:
TRUE.

REGISTRY_HOLDER_ROTATION_PRESERVES_LINEAGE:
TRUE.

ONE_REGISTRY_REPLICA_LOSS_TOLERATED:
TRUE.

REGISTRY_REPRODUCES_05U_WITHOUT_BUNDLE_COMPLETENESS:
TRUE.

APPEND_ONLY_COMPLETENESS_GAIN:
TRUE.

NO_SEAL_TIMING_AMBIGUITY_EXPOSED:
TRUE.

AUDIT A — SINGLE-PARENT REGISTRY

8 / 8 exact.

AUDIT B — TWO-PARENT REGISTRY

28 / 28 exact.

AUDIT C — CHILD OMITS REGISTERED PARENT

Cases:

56.

Child bundle incomplete:

56 / 56.

SEALED_EDGE_REGISTRY exact reconstruction:

56 / 56.

The child's bundle is therefore no longer authoritative for completeness.

AUDIT D — BOTH DG-1R-05U BUNDLE OBSERVERS OMIT THE SAME REGISTERED PARENT

Cases:

56.

Registry exact reconstruction:

56 / 56.

The closed 05U dual-observer omission weakness is bypassed when parent existence is independently recorded at contribution time.

AUDIT E — ONE REGISTRY REPLICA WITHHOLDS AN HONEST EDGE

Cases:

112.

Exact reconstruction:

112 / 112.

A single withholding replica cannot erase a quorum-committed causal edge.

AUDIT F — PARTIAL EDGE WRITE

Cases:

56.

Candidate abstentions:

56 / 56.

A causal contribution present on fewer than three replicas never becomes ACTIVE.

AUDIT G — PARTIAL SEAL WRITE

Cases:

56.

Candidate abstentions:

56 / 56.

Committed edges without a quorum seal do not become an authoritative closed generation.

AUDIT H — DUPLICATE EDGE FANOUT

Cases:

224.

Exact reconstruction:

224 / 224.

Replica-local copies and repeated event copies never create extra registry votes.

AUDIT I — STALE GENERATION EDGE REPLAY

Cases:

32.

Current-generation lineage preserved:

32 / 32.

A stale edge tuple bound to another generation does not contaminate the sealed current generation.

AUDIT J — LATE EDGE AFTER SEAL

Cases:

56.

EDGE_QUORUM_NO_SEAL early incomplete acceptance:

56 / 56.

SEALED_EDGE_REGISTRY abstention after late edge:

56 / 56.

This establishes why edge quorum alone is insufficient.

Without a closure boundary,
a verifier can authorize before all causal edges have arrived.

The generation seal converts that timing ambiguity into an explicit invalid state.

AUDIT K — CONFLICTING AUTHORITATIVE SEALS

Cases:

28.

Abstentions:

28 / 28.

No candidate seal is selected when two quorum-valid closed histories coexist.

AUDIT L — REGISTRY HOLDER ROTATION

Cases:

36.

Verified lineage unchanged:

36 / 36.

Authority follows committed registry history,
not permanent replica-holder identity.

AUDIT M — ONE REGISTRY REPLICA UNAVAILABLE

Cases:

112.

Exact reconstruction from remaining three replicas:

112 / 112.

AUDIT N — DG-1R-05U OMITTED-PARENT FAMILY REPLAY

Cases:

56.

Exact reconstruction:

56 / 56.

The 05U omitted-parent family is recovered without any child-bundle completeness claim.

CORRELATED REGISTRY BOUNDARY

H1 — THREE-REPLICA OMITTING FORK

Cases:

28.

False incomplete lineage authorizations:

28 / 28.

REGISTRY_MAJORITY_OMISSION_FAILURE:

TRUE.

H2 — THREE-REPLICA FALSE EDGE INSERTION

Cases:

28.

False extra-lineage authorizations:

28 / 28.

REGISTRY_MAJORITY_INSERTION_FAILURE:

TRUE.

H3 — TWO CORRUPTED REPLICAS ATTEMPT FALSE HISTORY

Cases:

28.

False authorizations:

0.

TWO_CORRUPT_REPLICAS_SUPPRESSED:

TRUE.

H4 — CONSTITUTIONAL ROOT COMPROMISE

Ordered four-root false-independence cases:

1680.

False independence authorizations:

1680 / 1680.

ROOT_COMPROMISE_FAILURE:

TRUE.

TECHNICAL INTERPRETATION

DG-1R-05V converts lineage completeness from a witness assertion
into a property of committed causal events.

The architecture now distinguishes:

EDGE EXISTENCE

a parent contribution becomes active only after quorum registration;

from

GENERATION CLOSURE

one unique quorum seal must exactly match the current committed parent set.

This removes the specific 05U weakness where the child and both bundle-completeness observers could jointly hide one actual parent.

The candidate also handles:

- one replica withholding;
- one replica loss;
- duplicate copies;
- partial writes;
- partial seals;
- stale generation replay;
- late-arriving edges;
- conflicting closures.

The active boundary is now the registry quorum itself.

A plain 3-of-4 replica threshold still assumes
that three agreeing registry replicas represent three sufficiently independent sources.

The holdouts show that this assumption is unsafe under correlated three-replica history forgery.

The next architectural step should therefore reuse the closed DG-1R-05T / 05U provenance machinery
inside the registry quorum itself.

Registry votes should count by verified evidence lineage,
not merely by replica count.

PLAIN-SPEAK INTERPRETATION

The family-tree problem is getting much cleaner.

A child can no longer hide a parent just by leaving that parent out of its paperwork.

The parent leaves a shared record when it contributes.

And the generation gets sealed only after the registry agrees on the complete committed parent set.

That fixed the exact problem from the last experiment.

It also caught late-arriving parents.

Without the seal,
the system would have accepted an incomplete family tree before the second parent appeared.

With the seal,
the late parent makes the old closure invalid
and the organism stops instead of guessing.

The next weak spot is the registry itself.

Right now three out of four replicas can define history.

If those three are really independent,
that is useful.

If those three are all descendants of one poisoned source,
or are otherwise correlated,
we are back to counting the same evidence several times.

So the next step is straightforward:

THE REGISTRY'S VOTES ALSO NEED PROVENANCE.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05W —

LINEAGE-QUALIFIED REGISTRY QUORUM AUDIT.

Question:

Can registry edge and seal votes be counted by verified provenance lineage
rather than raw replica headcount,
so that several replica holders derived from one causal source
cannot manufacture a false 3-of-4 history quorum?

05W should remain detection / authorization only.

It should test:

- four genuinely independent registry lineages;
- three independent lineages with one replica unavailable;
- three holders copied from one registry root;
- two holders sharing ancestry plus independent others;
- compound but disjoint registry ancestry;
- lineage-preserving registry-holder rotation;
- many descendants of one registry root;
- false 3-of-4 quorum created by same-lineage replicas;
- independently rooted three-replica collusion as an explicit remaining boundary;
- constitutional root-compromise boundary.

No repair,
role migration,
health-memory update,
or production mutation should execute.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
