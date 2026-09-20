TITLE: DG-1R-05U — Non-Self-Certifying Lineage Attestation Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / DETECTION-AND-AUTHORIZATION ONLY / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / PROVENANCE ATTESTATION
BRANCH: dg1a-ar
PARENT: DG-1R-05T

PURPOSE

DG-1R-05T established that lineage-aware quorum can separate:

different holders

from

different causal evidence sources.

It also established the decisive boundary:

a single witness can recreate a false independent quorum
if it is allowed to omit one shared ancestor from its own lineage metadata.

DG-1R-05U asks:

CAN A WITNESS'S LINEAGE
BE RECONSTRUCTED
FROM OTHER PARTICIPANTS' ATTESTATIONS
SO THE WITNESS CANNOT ERASE ITS OWN ANCESTRY?

The experiment remains detection / authorization only.

No repair.
No role migration.
No health-memory update.
No persistent production mutation.

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

DG-1R-05 canonical frozen primary remains UNSPENT.

PROVENANCE ROOTS

Carry forward the eight synthetic roots:

R0 through R7.

Each honest root has one immutable root certificate:

root_id;
certified ancestry mask = 1 << root_id;
generation = 0.

The root certificate is treated as part of the tiny constitutional substrate for this audit.

Root compromise is tested separately as an explicit boundary.

DERIVED LINEAGE CERTIFICATE

A derived witness generation contains:

child_id;
generation;
presented parent IDs;
child self-claimed lineage mask;
parent edge attestations;
observer A parent-set attestation;
observer B parent-set attestation.

The child self-claimed lineage mask is never authoritative under the candidate method.

PARENT EDGE ATTESTATION

Every presented causal parent must issue an edge attestation binding:

parent ID;
child ID;
child generation.

A presented parent without its parent-issued edge attestation is invalid.

COMPLETE PARENT-SET OBSERVERS

Two distinct observer slots independently attest the complete set of causal parent IDs
for the child generation.

The observer attestations bind:

child ID;
child generation;
sorted complete parent-ID set.

The observers do not author the lineage mask.

They attest only:

"these are all causal parents for this generation."

This is the mechanism that can detect an omitted parent.

The two observer slots are distinct from:

- the child;
- every presented parent;
- each other.

05U models the observer attestations as exact booleans / bound tuples.

It does not claim a final cryptographic implementation.

VERIFIED LINEAGE

For an honest root certificate:

verified lineage =
immutable root mask.

For a derived certificate under the candidate method:

1. verify generation is greater than every presented parent generation;
2. verify every presented parent certificate recursively;
3. verify every presented parent supplied a valid edge attestation for this child generation;
4. verify observer A and observer B attest the same complete parent set;
5. verify the observer parent set exactly equals the presented parent set;
6. compute verified lineage as bitwise OR of verified parent lineages.

The child self-claimed lineage mask is ignored.

METHODS

1. SELF_DECLARED_LINEAGE

Accept child self-claimed ancestry mask.

Negative control.

2. INCLUDED_PARENT_ONLY

Ignore child self-claim,
verify only the presented parent certificates and presented edge attestations,
then OR their verified lineages.

Does NOT verify that the presented parent set is complete.

This is expected to remain vulnerable to omitted-parent attacks.

3. DUAL_OBSERVED_PARENTSET

Use the complete candidate verification rule above.

This is the candidate architecture.

TRUTH MODEL

Every case separately records:

actual causal parent set.

The evaluator derives true ancestry by recursively unioning the actual parent lineages.

The verifier sees only the presented certificate bundle.

PRIMARY AUDIT A — IMMUTABLE ROOT CERTIFICATES

Verify all eight honest roots.

Primary signal:

ROOT_CERTIFICATES_VALID

TRUE iff DUAL_OBSERVED_PARENTSET reconstructs all eight exact singleton root masks.

PRIMARY AUDIT B — SINGLE-PARENT INHERITANCE CHAINS

For each root:

build a chain of depths 1 through 8.

Every derived generation has exactly one causal parent.

Total derived certificates:

8 roots
x
8 depths
=
64.

Each child deliberately carries a misleading arbitrary self-claimed mask
that is not used by the candidate verifier.

Primary signal:

SINGLE_PARENT_INHERITANCE_EXACT

TRUE iff all 64 candidate verifications reconstruct exactly the original root ancestry.

PRIMARY AUDIT C — HONEST TWO-PARENT MERGES

For every unordered pair of distinct roots:

create one child with both roots as causal parents.

Cases:

C(8,2)
=
28.

Both parent edges are present.

Both observers attest the exact two-parent set.

Primary signal:

TWO_PARENT_UNION_EXACT

TRUE iff all 28 candidate verifications return the exact two-root union.

PRIMARY AUDIT D — CHILD OMITS ONE ACTUAL PARENT

For every unordered two-root parent pair:

test both choices of omitted parent.

Actual parent set:

two roots.

Presented parent set:

one root.

Truthful observer A and B still attest the complete two-parent set.

Cases:

28
x
2
=
56.

Primary signals:

OMITTED_PARENT_REJECTED

TRUE iff DUAL_OBSERVED_PARENTSET rejects all 56.

INCLUDED_PARENT_OMISSION_EXPOSED

TRUE iff INCLUDED_PARENT_ONLY accepts at least one incomplete lineage.

PRIMARY AUDIT E — MISSING PARENT EDGE ATTESTATION

For every unordered two-root merge:

remove each one of the two parent edge attestations in turn.

Cases:

56.

Both observers still attest the correct full parent set.

Primary signal:

MISSING_PARENT_EDGE_REJECTED

TRUE iff candidate verification rejects all 56.

PRIMARY AUDIT F — ONE OBSERVER DISAGREES

For every unordered two-root merge:

F1:
observer A reports only parent 0;
observer B reports both parents.

F2:
observer B reports only parent 1;
observer A reports both parents.

Cases:

56.

Primary signal:

SINGLE_OBSERVER_CORRUPTION_REJECTED

TRUE iff candidate verification rejects all 56.

No one observer is promoted to sole complete-parent authority.

PRIMARY AUDIT G — STALE CERTIFICATE REPLAY / GENERATION MONOTONICITY

For each root:

build an honest four-generation chain.

For each current generation 1 through 4:

present a certificate whose generation is not greater than its parent generation
or replay the previous generation as the current certificate.

Total frozen replay / monotonicity cases:

32.

Primary signal:

STALE_OR_NONMONOTONIC_REJECTED

TRUE iff candidate verification rejects all 32.

PRIMARY AUDIT H — LINEAGE-PRESERVING HOLDER ROTATION

For every one of the 64 honest single-parent chain certificates:

change the current holder ID
without changing:

- child certificate;
- parent edge attestations;
- observer parent-set attestations;
- generation;
- lineage.

Primary signal:

HOLDER_ROTATION_PRESERVES_VERIFIED_LINEAGE

TRUE iff all 64 verified lineage masks remain unchanged.

PRIMARY AUDIT I — PARENT SELF-CLAIM TAMPER

For every root:

build a two-generation chain.

Tamper the intermediate parent's self-claimed lineage mask
to a different root.

Do not alter its valid parent certificate,
edge attestation,
or observers.

Cases:

8.

Primary signal:

PARENT_SELF_CLAIM_IGNORED

TRUE iff the final child's candidate verified lineage still equals the true original root in all eight cases.

PRIMARY AUDIT J — REPRODUCE DG-1R-05T SINGLE-ROOT QUORUM

Rebuild all 4096 ordered four-slot single-root assignments from DG-1R-05T.

Each slot's witness lineage must be obtained from a one-generation attested child certificate,
not a self-declared mask.

Feed only candidate-verified masks into the frozen DG-1R-05T pairwise-disjoint quorum rule.

Expected ground-truth counts remain:

1680 independent.
2416 duplicated provenance.

Primary signal:

ATTESTED_LINEAGE_REPRODUCES_05T

TRUE iff:

- all 1680 independent assignments authorize;
- all 2416 duplicated assignments abstain;
- zero false quorum authorization occurs.

PRIMARY AUDIT K — COMPOUND DISJOINT QUORUM

Rebuild the 2520 ordered two-root pair partitions from DG-1R-05T.

Each quorum witness is a correctly attested two-parent child.

Feed candidate-verified masks into the same frozen pairwise-disjoint quorum rule.

Primary signal:

ATTESTED_COMPOUND_DISJOINT_ACCEPTANCE

TRUE iff all 2520 authorize with zero false authorization.

NEGATIVE CONTROLS

SELF_DECLARED_LINEAGE and INCLUDED_PARENT_ONLY are controls.

Expected vulnerabilities:

SELF_DECLARED_LINEAGE:
child may invent or erase ancestry directly.

INCLUDED_PARENT_ONLY:
child cannot forge included parent lineage,
but may hide an unpresented causal parent.

CORRELATED / ATTESTATION-FORGERY BOUNDARY

Holdout only.

H1 — BOTH COMPLETE-PARENT OBSERVERS COLLude WITH CHILD

Use every 56 omitted-parent case from Audit D.

Alter observer A and observer B
so both falsely attest the incomplete presented parent set.

The omitted actual parent remains outside the bundle.

Record:

DUAL_OBSERVER_COLLUSION_FAILURE.

This failure is expected to remain possible.

H2 — ONE OBSERVER COLLUDES

Repeat Audit D with only one observer falsely matching the incomplete parent set.

The other observer remains truthful.

Primary expectation:

reject.

H3 — ROOT CERTIFICATE COMPROMISE

Ground truth:

four witness roots all descend from one physical / causal source.

Constitutional root certificates falsely mint them as four distinct immutable roots.

If the later lineage system accepts the false independence,
record:

ROOT_COMPROMISE_FAILURE.

This is an explicit root-of-trust boundary.

05U must not reinterpret root compromise as an ordinary child-lineage failure.

PRIMARY ATTESTATION SIGNAL

NON_SELF_CERTIFYING_LINEAGE_GAIN

TRUE iff all are TRUE:

ROOT_CERTIFICATES_VALID
AND
SINGLE_PARENT_INHERITANCE_EXACT
AND
TWO_PARENT_UNION_EXACT
AND
OMITTED_PARENT_REJECTED
AND
MISSING_PARENT_EDGE_REJECTED
AND
SINGLE_OBSERVER_CORRUPTION_REJECTED
AND
STALE_OR_NONMONOTONIC_REJECTED
AND
HOLDER_ROTATION_PRESERVES_VERIFIED_LINEAGE
AND
PARENT_SELF_CLAIM_IGNORED
AND
ATTESTED_LINEAGE_REPRODUCES_05T
AND
ATTESTED_COMPOUND_DISJOINT_ACCEPTANCE

and

zero false primary lineage authorization occurs under DUAL_OBSERVED_PARENTSET.

DUAL_OBSERVER_COLLUSION_FAILURE
and
ROOT_COMPROMISE_FAILURE
are reported separately as constitutional boundaries.

MECHANICAL CONTROLS

Harness MUST assert:

- exactly eight roots;
- root generation = 0;
- child generation must exceed every parent generation;
- child self-claimed mask is ignored by candidate verification;
- every presented parent requires an edge attestation;
- both complete-parent observers must agree;
- observer parent set must equal presented parent set;
- verified child lineage is OR of verified parent lineages;
- Audit B count = 64;
- Audit C count = 28;
- Audit D count = 56;
- Audit E count = 56;
- Audit F count = 56;
- Audit G count = 32;
- Audit H count = 64;
- Audit I count = 8;
- Audit J count = 4096;
- Audit K count = 2520;
- no state mutation;
- truth labels evaluator-only.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary attestation case begins do not alter:

- root count;
- certificate fields;
- generation rule;
- parent-edge rule;
- observer count;
- complete-parent-set rule;
- lineage union rule;
- primary audit families;
- success signals;
- correlated-forgery holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

The last test taught us that knowing ancestry is useful,
but letting a cell write its own ancestry is unsafe.

So now the cell does not get to decide where its evidence came from.

Every parent that actually contributed evidence has to leave a receipt.

And two other observers independently record the complete parent list for that generation.

The child's ancestry is then rebuilt from those records.

If the child says:

"I only had one parent,"

but the observers saw two,
the lineage is rejected.

If one observer lies,
the other can stop the commit.

If both observers and the child collude,
the system can still be fooled.

And if the tiny immutable root certificates themselves are compromised,
everything downstream can inherit a false history.

Those are intended boundaries,
not things we will hide.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05U NON-SELF-CERTIFYING LINEAGE ATTESTATION

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY ATTESTATION CASE.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05u_lineage_attestation_v1.py

Harness source commit:

2ae3243ddb402c3796b566baa35a320a2c0231a9.

Git blob SHA:

46f782ba8160eadaee8ef37774570a9e4c8f5b60.

Source SHA-256:

6a1bc53d7c061f62d0b9820a5a911503f6557cf1592036e4184d3bfe8515db5b.

Source bytes:

15159.

FROZEN IMPLEMENTATION

The harness implements:

- exactly eight immutable synthetic root certificates;
- recursive parent-issued edge attestations;
- two complete-parent-set observer attestations;
- child self-claimed lineage ignored by candidate verification;
- INCLUDED_PARENT_ONLY and SELF_DECLARED_LINEAGE negative controls;
- exact recursive lineage union;
- strict generation monotonicity;
- holder rotation independent of lineage identity;
- omitted-parent, missing-edge, observer-disagreement, replay, and self-claim tamper audits;
- exact DG-1R-05T 4096 single-root quorum replay;
- exact 2520 compound-disjoint quorum replay;
- dual-observer collusion holdout;
- one-observer collusion holdout;
- constitutional root-compromise holdout.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Roots:

8.

Quorum slots:

4.

Audit B:
64.

Audit C:
28.

Audit D:
56.

Audit E:
56.

Audit F:
56.

Audit G:
32.

Audit H:
64.

Audit I:
8.

Audit J:
4096.

Audit K:
2520.

No primary attestation result,
lineage authorization result,
omission result,
replay result,
or forgery result
was generated before this freeze.

REPRODUCIBILITY

Execute two complete deterministic sweeps from this exact frozen harness.

Serialized output SHA-256 must match exactly.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL CLOSURE — DG-1R-05U NON-SELF-CERTIFYING LINEAGE ATTESTATION AUDIT

DATE:
2026-09-20.

STATUS:
CLOSED /
REPRODUCIBLE /
NON-SELF-CERTIFYING LINEAGE GAIN POSITIVE /
DG-1R-05T QUORUM REPRODUCED /
DUAL-OBSERVER COLLUSION BOUNDARY PRESERVED /
ROOT-OF-TRUST BOUNDARY PRESERVED /
NON-CANONICAL.

FROZEN PROVENANCE

Preregistration commit:

153f6fd07fc24778b8ac4dc45f2b41ae9c5e7665.

Harness source commit:

2ae3243ddb402c3796b566baa35a320a2c0231a9.

Harness Git blob:

46f782ba8160eadaee8ef37774570a9e4c8f5b60.

Harness source SHA-256:

6a1bc53d7c061f62d0b9820a5a911503f6557cf1592036e4184d3bfe8515db5b.

Harness bytes:

15159.

Freeze commit:

08c9f73e1220eb80aa946e0f0339e81ab0f5b0cb.

PRIMARY EXECUTION

Two complete deterministic frozen sweeps were executed.

Sweep 1 serialized output SHA-256:

c1d92a4f99dddbf9869438f99d521f567a48edca67afa1409f9a0f0daaaa3761.

Sweep 2 serialized output SHA-256:

c1d92a4f99dddbf9869438f99d521f567a48edca67afa1409f9a0f0daaaa3761.

BYTE_IDENTICAL_REPRODUCIBILITY:

TRUE.

MECHANICAL_VALID:

TRUE.

PRIMARY SIGNALS

ROOT_CERTIFICATES_VALID:
TRUE.

SINGLE_PARENT_INHERITANCE_EXACT:
TRUE.

TWO_PARENT_UNION_EXACT:
TRUE.

OMITTED_PARENT_REJECTED:
TRUE.

INCLUDED_PARENT_OMISSION_EXPOSED:
TRUE.

MISSING_PARENT_EDGE_REJECTED:
TRUE.

SINGLE_OBSERVER_CORRUPTION_REJECTED:
TRUE.

STALE_OR_NONMONOTONIC_REJECTED:
TRUE.

HOLDER_ROTATION_PRESERVES_VERIFIED_LINEAGE:
TRUE.

PARENT_SELF_CLAIM_IGNORED:
TRUE.

ATTESTED_LINEAGE_REPRODUCES_05T:
TRUE.

ATTESTED_COMPOUND_DISJOINT_ACCEPTANCE:
TRUE.

NON_SELF_CERTIFYING_LINEAGE_GAIN:
TRUE.

ONE_OBSERVER_COLLUSION_REJECTED:
TRUE.

AUDIT A — ROOT CERTIFICATES

8 / 8 immutable synthetic root certificates reconstructed exactly.

AUDIT B — SINGLE-PARENT INHERITANCE

64 / 64 derived certificates reconstructed the original root lineage exactly.

The child self-claimed lineage was deliberately misleading and had no authority.

AUDIT C — TWO-PARENT MERGES

28 / 28 honest two-root unions reconstructed exactly.

AUDIT D — OMITTED ACTUAL PARENT

Cases:

56.

DUAL_OBSERVED_PARENTSET rejects:

56 / 56.

INCLUDED_PARENT_ONLY accepts the incomplete presented lineage:

56 / 56.

SELF_DECLARED_LINEAGE accepts:

56 / 56.

Thus verifying only included parents is insufficient.

Completeness is the critical property.

AUDIT E — MISSING PARENT EDGE

Cases:

56.

Candidate rejects:

56 / 56.

AUDIT F — ONE COMPLETE-PARENT OBSERVER DISAGREES

Cases:

56.

Candidate rejects:

56 / 56.

No one observer becomes sole parent-set authority.

AUDIT G — STALE / NONMONOTONIC GENERATION

Cases:

32.

Candidate rejects:

32 / 32.

AUDIT H — HOLDER ROTATION

64 / 64 verified lineage masks remained unchanged.

Authority follows attested lineage,
not permanent holder identity.

AUDIT I — PARENT SELF-CLAIM TAMPER

Cases:

8.

Final verified lineage remained exact:

8 / 8.

A parent's self-declared ancestry therefore cannot poison descendants
when recursive verification ignores self-claims.

AUDIT J — DG-1R-05T SINGLE-ROOT QUORUM REPLAY

Cases:

4096.

True independent authorizations:

1680.

Duplicated-provenance abstentions:

2416.

False authorizations:

0.

The attested lineage system reproduces the closed 05T result exactly.

AUDIT K — COMPOUND DISJOINT QUORUM

Cases:

2520.

Authorizations:

2520 / 2520.

False authorizations:

0.

Compound ancestry remains acceptable when the reconstructed root sets are actually disjoint.

ATTESTATION-FORGERY BOUNDARY

H1 — CHILD PLUS BOTH COMPLETE-PARENT OBSERVERS COLLude TO OMIT ONE ACTUAL PARENT

Cases:

56.

False candidate authorizations:

56 / 56.

DUAL_OBSERVER_COLLUSION_FAILURE:

TRUE.

If every mechanism responsible for parent-set completeness lies together,
the omitted parent is still removable from the presented history.

H2 — ONLY ONE COMPLETE-PARENT OBSERVER COLLUDES

Cases:

56.

False authorizations:

0.

Rejects:

56 / 56.

One corrupted completeness witness is insufficient.

H3 — CONSTITUTIONAL ROOT CERTIFICATES MINT FALSELY INDEPENDENT ROOTS FROM ONE ACTUAL CAUSAL SOURCE

Ordered four-root cases:

1680.

False independence authorizations:

1680 / 1680.

ROOT_COMPROMISE_FAILURE:

TRUE.

This is a root-of-trust boundary,
not an ordinary child-certificate failure.

TECHNICAL INTERPRETATION

DG-1R-05U removes witness self-certification from ordinary lineage reconstruction.

A child cannot:

- rewrite an included parent's lineage;
- invent a lower-generation ancestry chain;
- omit an included parent's edge;
- override one honest complete-parent observer;
- poison descendants by changing only its own lineage field.

The candidate verifier reconstructs ancestry from externally issued evidence.

The remaining weakness is now sharply localized:

PARENT-SET COMPLETENESS.

The verifier can prove that every presented parent is valid.

It cannot prove that an unpresented causal parent never existed
when all completeness observers collude with the child.

This suggests a better architecture than adding more observers indefinitely:

make causal parent edges independently discoverable.

Instead of asking a child bundle to contain every parent,
and asking observers to certify that the bundle is complete,
a parent contribution should create an append-only edge record indexed by:

(child_id,
child_generation).

Lineage reconstruction can then obtain the complete parent set
from the independently maintained edge index.

This converts completeness from:

A CLAIM ABOUT A BUNDLE

into:

A QUERY OVER COMMITTED CAUSAL EVENTS.

The constitutional root boundary remains separate.

Even a perfect lineage graph cannot recover truth
if its root identities were falsely minted as independent at genesis.

PLAIN-SPEAK INTERPRETATION

We solved the problem of a cell rewriting its own family tree.

The child can lie about its ancestry now,
and the verifier ignores that lie.

Its parents leave receipts,
and two other witnesses check the parent list.

That worked perfectly in the normal tests.

It also reproduced the previous provenance-quorum result exactly.

But we found the next weak spot very clearly.

If the child and BOTH people responsible for saying
"this is the complete parent list"
lie together,
they can still erase a parent from history.

So adding a third,
fourth,
or fifth person to remember the list is probably the wrong direction.

A better rule is:

WHEN A PARENT CONTRIBUTES,
THE CONTRIBUTION ITSELF LEAVES A RECORD
THAT THE CHILD CANNOT HIDE LATER.

Then ancestry is rebuilt by looking up the recorded parent events,
not by trusting the child to hand us a complete folder.

There is also one final constitutional boundary underneath all of this:

if the organism starts by falsely declaring one source to be four independent roots,
everything downstream can faithfully preserve a false history.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05V —

APPEND-ONLY CAUSAL-EDGE COMPLETENESS AUDIT.

Question:

Can every causal parent contribution be committed to a distributed append-only edge index
so that lineage reconstruction discovers all parents for a child generation
without relying on child-supplied completeness?

05V should remain detection / authorization only.

It should test:

- honest single-parent edge registration;
- honest multi-parent registration;
- child omission of a registered parent;
- observer omission after edge registration;
- one registry replica withholding an edge;
- partial registry writes;
- duplicate edge fanout;
- stale-generation edge replay;
- conflicting child-generation forks;
- holder rotation;
- recovery from one unavailable registry replica;
- correlated registry-majority forgery as an explicit boundary;
- replay of DG-1R-05U omitted-parent cases using registry-derived parent sets.

No repair,
role migration,
or health-memory update should execute.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
