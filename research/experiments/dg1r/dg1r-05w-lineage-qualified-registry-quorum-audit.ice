TITLE: DG-1R-05W — Lineage-Qualified Registry Quorum Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / DETECTION-AND-AUTHORIZATION ONLY / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / REGISTRY QUORUM PROVENANCE
BRANCH: dg1a-ar
PARENT: DG-1R-05V

PURPOSE

DG-1R-05V established that append-only causal-edge registration plus a quorum generation seal
removes child-bundle completeness as an authority problem.

Its remaining ordinary weakness is the registry quorum itself.

A raw 3-of-4 threshold assumes that three agreeing replica holders
represent three sufficiently independent evidence sources.

DG-1R-05W asks:

CAN REGISTRY VOTES
BE COUNTED BY VERIFIED PROVENANCE LINEAGE
RATHER THAN REPLICA HEADCOUNT
SO SAME-LINEAGE HOLDERS
CANNOT MANUFACTURE A FALSE HISTORY QUORUM?

BOUNDARY

Synthetic software only.

No repair.
No role migration.
No health-memory update.
No production mutation.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

DG-1R-05 canonical frozen primary remains UNSPENT.

ROOTS AND VERIFIED LINEAGE

Carry forward the exact eight synthetic provenance roots R0 through R7.

05W consumes VERIFIED lineage masks.

It does not use registry-holder self-claimed ancestry.

The ordinary lineage-authenticity mechanism is the closed DG-1R-05U result.

Root compromise remains a separate explicit boundary.

REGISTRY REPLICAS

Four registry replica slots:

REG_A
REG_B
REG_C
REG_D.

Each vote consists of:

replica slot;
event identity;
verified lineage mask.

An event identity may be either:

- one causal EDGE tuple;
- one generation SEAL tuple.

05W does not distinguish their quorum arithmetic.

It tests the voting substrate shared by both.

METHODS

1. HEADCOUNT3

Authorize an event when any three replica slots vote for the same event.

Negative control.

2. DISTINCT_HOLDER3

Authorize when three distinct replica-holder IDs vote for the same event.

Negative control.

3. LINEAGE_QUORUM3

Candidate architecture.

Authorize an event iff among the voting replicas
there exists a subset of at least three votes
whose verified lineage masks are:

- nonzero;
- pairwise disjoint.

Thus three holders descended from one provenance root
count as one effective source,
not three.

A four-vote event may authorize from any qualifying three-vote subset.

No weighting.
No majority-by-descendant-count.
No self-claimed lineage.

PRIMARY AUDIT A — EXHAUSTIVE FOUR-REPLICA SINGLE-ROOT ASSIGNMENTS

Assign one singleton root lineage to each of the four replica slots.

Ordered assignments:

8^4
=
4096.

All four replicas vote for the same event.

Ground-truth qualified quorum exists iff at least three distinct roots are represented.

Frozen expected counts:

fewer than three distinct roots:
400.

at least three distinct roots:
3696.

Signals:

SINGLE_ROOT_QUORUM_EXACT

TRUE iff LINEAGE_QUORUM3:

- authorizes all 3696 qualified assignments;
- abstains on all 400 unqualified assignments.

HEADCOUNT_DUPLICATION_EXPOSED

TRUE iff HEADCOUNT3 authorizes at least one unqualified assignment.

PRIMARY AUDIT B — THREE SAME-ROOT HOLDERS PLUS ONE OTHER ROOT

Choose:

shared root;
different root;
which replica slot carries the different root.

Cases:

8 x 7 x 4
=
224.

All four replicas vote.

Effective independent roots:

2.

Signal:

TRIPLE_DESCENDANT_FALSE_QUORUM_REJECTED

TRUE iff LINEAGE_QUORUM3 abstains on all 224.

PRIMARY AUDIT C — TWO ROOTS DUPLICATED AS TWO PAIRS

Choose two roots
and assign two replica slots to each.

Cases:

C(8,2) x C(4,2)
=
168.

Effective independent roots:

2.

Signal:

PAIR_DUPLICATION_REJECTED.

PRIMARY AUDIT D — THREE INDEPENDENT ROOTS PLUS ONE DUPLICATE

Exactly three distinct singleton roots are represented across four voting replicas.

Cases:

2016.

Signal:

THREE_ROOT_LIVENESS_PRESERVED

TRUE iff LINEAGE_QUORUM3 authorizes all 2016.

PRIMARY AUDIT E — ONE REPLICA UNAVAILABLE WITH THREE INDEPENDENT ROOTS

Choose three distinct roots
for three available replica slots.

Choose unavailable slot.

Cases:

C(8,3) x 3! x 4
=
1344.

Signal:

ONE_REPLICA_LOSS_WITH_INDEPENDENT_QUORUM

TRUE iff all 1344 authorize.

PRIMARY AUDIT F — COMPOUND BUT DISJOINT REGISTRY LINEAGES

Three available registry votes.

Each vote carries exactly two provenance roots.

All three two-root masks are pairwise disjoint.

One registry replica is unavailable.

Enumerate ordered three-pair partitions of six chosen roots from eight.

Cases:

C(8,6)
x
6! / (2!^3)
=
2520.

Signal:

COMPOUND_DISJOINT_REGISTRY_ACCEPTANCE

TRUE iff all 2520 authorize.

This prevents the rule from degenerating into:

"only singleton registry ancestry counts."

PRIMARY AUDIT G — PARTIAL ANCESTRY OVERLAP

Begin with three pairwise-disjoint voting lineage masks.

Inject one shared root into one pair of registry masks.

The event still has three distinct replica holders.

Cases are exhaustively generated from the Audit F family
for every unordered pair of the three voting slots.

Signal:

PARTIAL_REGISTRY_OVERLAP_REJECTED

TRUE iff LINEAGE_QUORUM3 never authorizes the corrupted three-vote set.

PRIMARY AUDIT H — LINEAGE-PRESERVING REGISTRY HOLDER ROTATION

For every qualified Audit A assignment:

replace all physical holder IDs
while preserving:

- replica slot;
- verified lineage mask;
- event identity.

Cases:

3696.

Signal:

REGISTRY_HOLDER_ROTATION_PRESERVES_QUORUM

TRUE iff every decision is unchanged.

PRIMARY AUDIT I — DESCENDANT FANOUT CANNOT CREATE REGISTRY QUORUM

Choose one provenance root.

Replicate its event vote through:

3,
4,
8,
16

distinct holder identities.

Map descendants onto the four registry slots
with repeated lineage.

No other root lineage is present.

Cases:

8 roots x 4 fanout levels
=
32.

Signal:

REGISTRY_DESCENDANT_FANOUT_NOT_QUORUM

TRUE iff LINEAGE_QUORUM3 never authorizes.

PRIMARY AUDIT J — REPLAY DG-1R-05V FALSE MAJORITY WITH SHARED LINEAGE

Recreate the 05V majority-omission and majority-insertion pattern,
but assign the three false-voting registry replicas
to the SAME verified provenance root.

The honest fourth replica uses a different root.

Cases:

8 shared false roots
x
7 honest roots
x
2 false-history classes
=
112.

Primary signal:

SAME_LINEAGE_REGISTRY_MAJORITY_COLLAPSED

TRUE iff LINEAGE_QUORUM3 never authorizes the false three-replica history.

NEGATIVE CONTROLS

HEADCOUNT3 and DISTINCT_HOLDER3 are expected to authorize:

- same-root triples;
- two-pair duplicated lineages;
- descendant fanout when three or more distinct holders are present.

They are not candidate architectures.

CORRELATED / CONSTITUTIONAL BOUNDARIES

H1 — THREE GENUINELY DISJOINT REGISTRY ROOTS COLLude

Three registry replicas have pairwise-disjoint verified roots.

All three vote for the same false history.

A fourth honest replica rejects it.

If LINEAGE_QUORUM3 authorizes:

INDEPENDENT_THREE_ROOT_COLLUSION_FAILURE.

This failure is expected to remain possible.

Provenance independence is not proof of honesty.

H2 — CONSTITUTIONAL ROOT COMPROMISE

Three registry root certificates have distinct root IDs
but all originate from one actual causal source.

If LINEAGE_QUORUM3 authorizes:

ROOT_COMPROMISE_FAILURE.

Expected boundary.

H3 — VERIFIED-LINEAGE METADATA FORGERY

A registry holder presents a self-claimed disjoint mask
different from its candidate-verified lineage.

Candidate must use only the verified mask.

Primary expectation:

self-claim has zero effect.

Signal:

REGISTRY_SELF_CLAIM_IGNORED.

PRIMARY QUORUM SIGNAL

LINEAGE_QUALIFIED_REGISTRY_GAIN

TRUE iff all are TRUE:

SINGLE_ROOT_QUORUM_EXACT
AND
TRIPLE_DESCENDANT_FALSE_QUORUM_REJECTED
AND
PAIR_DUPLICATION_REJECTED
AND
THREE_ROOT_LIVENESS_PRESERVED
AND
ONE_REPLICA_LOSS_WITH_INDEPENDENT_QUORUM
AND
COMPOUND_DISJOINT_REGISTRY_ACCEPTANCE
AND
PARTIAL_REGISTRY_OVERLAP_REJECTED
AND
REGISTRY_HOLDER_ROTATION_PRESERVES_QUORUM
AND
REGISTRY_DESCENDANT_FANOUT_NOT_QUORUM
AND
SAME_LINEAGE_REGISTRY_MAJORITY_COLLAPSED
AND
REGISTRY_SELF_CLAIM_IGNORED

and

zero false primary registry authorization occurs under LINEAGE_QUORUM3.

INDEPENDENT_THREE_ROOT_COLLUSION_FAILURE
and
ROOT_COMPROMISE_FAILURE
are reported separately as boundaries.

MECHANICAL CONTROLS

Harness MUST assert:

- exactly eight roots;
- exactly four registry slots;
- quorum size = 3 lineage-disjoint votes;
- exact pairwise-disjoint bitmask rule;
- Audit A count = 4096;
- Audit A qualified count = 3696;
- Audit A unqualified count = 400;
- Audit B count = 224;
- Audit C count = 168;
- Audit D count = 2016;
- Audit E count = 1344;
- Audit F count = 2520;
- Audit H count = 3696;
- Audit I count = 32;
- Audit J count = 112;
- holder identity does not alter verified lineage;
- self-claimed lineage is never used by candidate;
- no state mutation;
- truth labels evaluator-only.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary quorum case begins do not alter:

- root count;
- registry slot count;
- quorum size;
- lineage-mask semantics;
- pairwise-disjoint rule;
- audit families;
- truth labels;
- primary signals;
- correlated holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

The registry fixed the problem of a child hiding its parents.

Now the registry itself has to prove that three votes are really three sources.

Three different machines are not automatically three independent witnesses.

They might all be copies of the same bad history.

So 05W makes the registry use the same lesson the cells learned earlier:

count ancestry,
not heads.

If three registry replicas all descend from the same source,
their three "yes" votes count like one source.

If three truly separate lineages agree,
the event can still reach quorum.

This does not make the registry infallible.

Three genuinely independent sources can still all be wrong or malicious together.

And falsely minted root identities can still poison the foundation.

Those boundaries remain explicit.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
