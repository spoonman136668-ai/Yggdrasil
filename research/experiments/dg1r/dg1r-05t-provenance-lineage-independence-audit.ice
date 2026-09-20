TITLE: DG-1R-05T — Provenance-Lineage Independence Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / DETECTION-AND-AUTHORIZATION ONLY / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / PROVENANCE LINEAGE
BRANCH: dg1a-ar
PARENT: DG-1R-05S

PURPOSE

DG-1R-05S showed that a four-slot distributed quorum can safely govern role migration
under an independent-witness assumption.

Its correlated-forgery holdout also showed the remaining weakness:

four nominally separate witnesses can all be wrong together.

DG-1R-05T asks:

CAN THE ORGANISM
DISTINGUISH
FOUR DIFFERENT WITNESS HOLDERS
FROM
FOUR GENUINELY INDEPENDENT EVIDENCE LINEAGES?

The experiment is detection / authorization only.

No repair.
No role migration.
No state mutation.

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

QUORUM SLOTS

Carry forward the four logical evidence slots from DG-1R-05S:

DEMAND_A
DEMAND_B
PEER_A
PEER_B

All four slots are required for the candidate authorization decision.

A witness holder ID and a provenance lineage are separate concepts.

Different holder IDs do not imply independent lineage.

PROVENANCE ROOTS

Freeze eight synthetic immutable root labels:

R0
R1
R2
R3
R4
R5
R6
R7

A witness lineage is represented by an 8-bit ancestry mask.

Bit k = 1 means the witness ultimately depends on root Rk.

This bitmask is a synthetic exact lineage representation for this audit.

05T does not claim that the final implementation must store an 8-bit mask.

It isolates the logic of evidence independence before provenance compression is considered.

LINEAGE INDEPENDENCE

Two witnesses are LINEAGE-DISJOINT iff:

ancestry_mask_A AND ancestry_mask_B = 0.

A four-slot quorum is independently qualified iff:

- all four required slots are present;
- all four holder IDs are distinct;
- every lineage mask is nonzero;
- all six slot pairs are lineage-disjoint.

This is deliberately conservative.

If two witnesses share any causal root,
they are not counted as independent for this quorum.

METHODS

1. HEADCOUNT4

Authorize when at least four affirmative witness holders are present.

Ignores holder identity and lineage.

2. DISTINCT_HOLDER4

Authorize when four distinct affirmative holder IDs are present.

Ignores lineage.

3. LINEAGE_DISJOINT4

Authorize only under the frozen lineage-independence rule above.

No weighting.
No confidence threshold.
No majority override.
No source may fill two effective lineage slots.

TRUTH LABELS

TRUE_INDEPENDENT_QUORUM:

all four witness lineages are pairwise disjoint.

DUPLICATED_PROVENANCE:

two or more witnesses share at least one root.

MISSING_PROVENANCE:

one required slot is absent.

FALSE_QUORUM_AUTHORIZATION:

a method authorizes while the ground-truth four-slot ancestry is not pairwise disjoint.

SAFE_ABSTAIN:

method refuses a non-independent or incomplete quorum.

PRIMARY AUDIT A — EXHAUSTIVE SINGLE-ROOT ASSIGNMENTS

Each slot receives exactly one of the eight roots.

Enumerate every ordered assignment:

8^4
=
4096 cases.

Exactly:

8 P 4
=
1680

have four distinct roots and are TRUE_INDEPENDENT_QUORUM.

The remaining:

2416

contain duplicated provenance.

All four holder IDs remain distinct in every case.

Primary signals:

CLEAN_SINGLE_ROOT_ACCEPTANCE

TRUE iff LINEAGE_DISJOINT4 authorizes all 1680 independent cases.

DUPLICATE_SINGLE_ROOT_REJECTION

TRUE iff LINEAGE_DISJOINT4 authorizes zero of the 2416 duplicated-root cases.

DISTINCT_HOLDER_FALSE_QUORUM_EXPOSED

TRUE iff DISTINCT_HOLDER4 authorizes at least one duplicated-root case.

PRIMARY AUDIT B — PARTIAL ANCESTRY OVERLAP

Start from every clean ordered four-root assignment in Audit A.

For each of the six unordered slot pairs:

add the same extra ancestry root
to both witnesses in that pair.

Choose the numerically smallest root not already used by the four baseline slots.

The two affected witness masks now partially overlap
while their original distinct roots remain.

Total:

1680 clean assignments
x
6 slot pairs
=
10080 cases.

Primary signal:

PARTIAL_OVERLAP_REJECTION

TRUE iff LINEAGE_DISJOINT4 authorizes zero cases.

PRIMARY AUDIT C — DESCENDANT INFLATION

For each root R0 through R7:

construct affirmative descendant populations of size:

1,
2,
4,
8,
16,
32.

Every descendant has:

- a distinct holder ID;
- the same one-root ancestry mask.

HEADCOUNT4 may see a large crowd.

The effective independent lineage count remains one.

Primary signals:

DESCENDANT_INFLATION_REJECTED

TRUE iff LINEAGE_DISJOINT4 never authorizes any same-root descendant population.

HEADCOUNT_INFLATION_EXPOSED

TRUE iff HEADCOUNT4 authorizes at least one population whose effective lineage count is one.

PRIMARY AUDIT D — LINEAGE-PRESERVING HOLDER ROTATION

For every clean Audit A assignment:

replace all four holder IDs with new distinct IDs.

Preserve ancestry masks exactly.

The authorization result must remain unchanged.

Primary signal:

HOLDER_ROTATION_PRESERVES_AUTHORITY

TRUE iff every clean case remains authorized by LINEAGE_DISJOINT4.

This tests that authority follows evidence lineage,
not permanent cell identity.

PRIMARY AUDIT E — LOST INDEPENDENT ROOT / MISSING SLOT

For every clean Audit A assignment:

remove each one of the four required witness slots in turn.

Total:

1680
x
4
=
6720 cases.

Primary signal:

MISSING_ROOT_ABSTAINS

TRUE iff LINEAGE_DISJOINT4 authorizes zero cases.

No surviving source may be promoted to two votes.

PRIMARY AUDIT F — COMPOUND BUT DISJOINT LINEAGE

Use all eight provenance roots.

Partition them into four ordered,
pairwise-disjoint two-root ancestry masks.

Each slot therefore has two ancestors,
but no root is shared across slots.

Enumerate all ordered pair partitions:

8! / (2!^4)
=
2520 cases.

Primary signal:

COMPOUND_DISJOINT_ACCEPTANCE

TRUE iff LINEAGE_DISJOINT4 authorizes all 2520 cases.

This prevents the rule from degenerating into:

"only singleton ancestry is trusted."

PRIMARY AUDIT G — COPIED WITNESS THROUGH MANY CELLS

For each of the four quorum slots:

choose one one-root evidence lineage.

Replicate that exact evidence through:

1,
2,
4,
8,
16

distinct holder cells.

The replicated descendants do not create additional independent lineage.

The other three quorum slots are absent.

Primary signal:

COPY_FANOUT_NOT_COUNTED_AS_QUORUM

TRUE iff LINEAGE_DISJOINT4 never authorizes.

NEGATIVE CONTROLS

HEADCOUNT4 and DISTINCT_HOLDER4 are not candidate architectures.

They exist to demonstrate:

- raw vote count can be inflated by descendants;
- distinct cell IDs can conceal common ancestry.

CORRELATED / METADATA FORGERY BOUNDARY

Holdout only.

Not a required success.

H1 — SELF-REPORTED LINEAGE FORGERY

Ground truth:

all four witnesses descend from the same root.

Reported lineage metadata:

four pairwise-disjoint singleton roots.

LINEAGE_DISJOINT4 receives only the reported metadata.

Record:

FORGED_LINEAGE_FALSE_AUTHORIZATION.

This failure is expected to remain possible.

H2 — ONE WITNESS HIDES A SHARED ROOT

Ground truth:

DEMAND_A and DEMAND_B share one root.

All other slot lineages are disjoint.

DEMAND_B falsely omits the shared root from its reported ancestry mask.

If the reported masks become pairwise disjoint,
record:

SINGLE_LINEAGE_LIE_FAILURE.

This directly tests whether lineage metadata may be self-certified.

H3 — HONEST LINEAGE METADATA

Repeat H1 and H2 with truthful ancestry masks.

Primary expectation:

abstain.

ARCHITECTURAL BOUNDARY

05T tests lineage-aware consensus assuming provenance metadata is readable.

It does NOT establish that provenance metadata is trustworthy.

A positive 05T result plus a positive metadata-forgery holdout
would justify the next experiment:

non-self-certifying lineage attestation.

PRIMARY LINEAGE SIGNAL

PROVENANCE_INDEPENDENCE_GAIN

TRUE iff all are TRUE:

CLEAN_SINGLE_ROOT_ACCEPTANCE
AND
DUPLICATE_SINGLE_ROOT_REJECTION
AND
PARTIAL_OVERLAP_REJECTION
AND
DESCENDANT_INFLATION_REJECTED
AND
HOLDER_ROTATION_PRESERVES_AUTHORITY
AND
MISSING_ROOT_ABSTAINS
AND
COMPOUND_DISJOINT_ACCEPTANCE
AND
COPY_FANOUT_NOT_COUNTED_AS_QUORUM

and

zero FALSE_QUORUM_AUTHORIZATION
occurs for LINEAGE_DISJOINT4
across primary Audits A through G.

FORGED_LINEAGE_FALSE_AUTHORIZATION
and
SINGLE_LINEAGE_LIE_FAILURE
are reported separately as boundary signals.

MECHANICAL CONTROLS

Harness MUST assert:

- exactly eight provenance roots;
- exactly four required quorum slots;
- exact six unordered slot pairs;
- Audit A case count = 4096;
- clean Audit A count = 1680;
- duplicated Audit A count = 2416;
- Audit B case count = 10080;
- Audit E case count = 6720;
- Audit F case count = 2520;
- all primary clean holder IDs are distinct;
- lineage masks are nonzero where present;
- pairwise-disjoint test is exact bitwise AND = 0;
- no state mutation;
- truth labels evaluator-only.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary lineage case begins do not alter:

- root count;
- ancestry-mask semantics;
- quorum-slot definitions;
- holder-ID rules;
- independence definition;
- audit families;
- truth labels;
- primary signals;
- metadata-forgery holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

We already proved that four separate witnesses are safer than one.

Now we are asking whether they are actually four witnesses.

Imagine four cells all say:

"yes."

If all four learned that answer from the same damaged ancestor,
that is not four independent votes.

It is one bad source being repeated four times.

So each piece of evidence gets a small ancestry label in this experiment.

If two witnesses share any source in their family tree,
they do not count as independent for this decision.

We will deliberately make:

- large crowds copied from one source;
- different cell IDs with the same ancestry;
- witnesses that overlap only partway in their ancestry;
- healthy witness rotation where the holder changes but the evidence lineage does not.

We will also lie about the ancestry labels on purpose.

That last test is important.

If a witness can simply claim:

"I came from somewhere independent,"

then provenance has become another self-certified health signal,
which would recreate the same circularity we have been removing.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
