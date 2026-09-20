TITLE: DG-1R-05Z — Dormant Temporal Sentinel / Hereditary Capsule Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / TEMPORAL-PROVENANCE AND HIBERNATION AUDIT / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / TEMPORAL SENTINELS
BRANCH: dg1a-ar
PARENT: DG-1R-05Y

PURPOSE

DG-1R-05Y established that partitioned healthy-cell populations can perform bounded provisional work
and safely re-merge when causal history is discoverable.

The remaining discussion raised a different source of independence:

TIME.

A live population can become highly correlated because all active cells continue exchanging information.
A genuinely sealed dormant cell cannot learn a later corruption while it remains dormant.

DG-1R-05Z asks:

CAN SMALL COHORTS OF TEMPORALLY SEALED CELLS
PRESERVE A TRUSTWORTHY DEVELOPMENTAL ANCHOR
WITHOUT BECOMING A PERMANENT VETO ON EVOLUTION?

AND:

DOES A COMPACT HEREDITARY CAPSULE
PROVIDE THE SAME AUTHORIZATION INFORMATION
AS PRESERVING THE WHOLE DORMANT CELL?

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No production mutation.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

DG-1R-05 canonical frozen primary remains UNSPENT.

CORE DESIGN RULE

DORMANT CELLS PRESERVE IDENTITY,
NOT CURRENT AUTHORITY.

A dormant sentinel does not vote on the present role merely because it remembers an older one.

Instead it stores a sealed historical anchor and asks:

IS THE PRESENTED CURRENT STATE
A VALID CAUSAL DESCENDANT
OF THE LAST SEALED HEALTHY STATE I CAN VERIFY?

A role mismatch alone is not damage.
Legitimate evolution may change role.

A causal discontinuity, rewritten sealed checkpoint, or silent current-state mutation is suspicious.

TEMPORAL COHORTS

Use one target lineage with legitimate committed generations 0 through 6.

Freeze three historical cohorts at generations:

T0 = generation 0
T1 = generation 2
T2 = generation 4

Each cohort contains three dormant sentinel holders.

Within each honest cohort:

- all three store the same checkpoint capsule;
- each uses a distinct provenance root;
- two pairwise-disjoint roots are sufficient to establish one temporal anchor;
- three holders derived from one root count as one source, not three.

The newest independently verified cohort at or before the current generation is authoritative for temporal continuity.

If the newest cohort is unavailable or lacks an independent quorum,
the audit may escalate to the next older cohort.

If a valid newer cohort exists and the presented present is NOT its descendant,
the result is CONTESTED.

The verifier MUST NOT bypass a contradictory valid newer cohort by falling back to an older one.

HEREDITARY CAPSULE

The compact capsule contains only:

checkpoint_id;
generation;
role;
FP2 phenotype signature;
causal_cursor.

Each capsule has an immutable content seal.

The full dormant-cell representation additionally carries synthetic internal state
that is irrelevant to the temporal authorization decision.

Candidate claim:

FULL_DORMANT_CELL
and
HEREDITARY_CAPSULE

produce identical authorization outcomes across every primary case.

This is an information-equivalence claim only.

05Z does not claim the full cell can always be regenerated from the capsule.

DESCENDANT VALIDATION

A current state is a valid descendant of a temporal anchor iff:

1. the anchor's causal_cursor exists at the anchor generation in the presented history;
2. role and FP2 at that cursor match the sealed capsule;
3. every later history record increments generation exactly by one;
4. every later record names the immediately previous commit as parent;
5. current generation, role, FP2, and commit ID match the terminal presented record.

The temporal sentinel verifies continuity.

It does not independently certify the truth of a later governance decision.

REACTIVATION RULE

A dormant cell may carry its last committed:

- phenotype identity;
- role;
- causal cursor.

It may NOT exercise current governance authority while dormant.

After waking it remains NON-VOTING until:

- temporal continuity is verified;
- its causal cursor is caught up to the current committed cursor;
- its reactivated phenotype is consistent with the current committed role.

Only then may it rejoin the live voting population.

AUDITS

AUDIT A — CLEAN / LEGITIMATE DESCENT

For current generations 0 through 6,
verify that legitimate role evolution is accepted from the newest available valid cohort.

Old-role mismatch must not itself cause rejection.

AUDIT B — SHORT AND LONG DORMANCY

Reactivate from every frozen cohort against later legitimate generations.

Before catch-up:
no vote.

After complete verified catch-up:
voting eligibility restored.

AUDIT C — SILENT CURRENT-STATE MUTATION

Mutate current role / FP2 without a matching causal-history commit.

Temporal result must be CONTESTED.

AUDIT D — SEALED CHECKPOINT REWRITE

Rewrite the presented historical state at a sealed checkpoint
while leaving the dormant cohort unchanged.

Temporal result must be CONTESTED.

AUDIT E — INCOMPLETE CAUSAL CATCH-UP

Present a history that stops before the claimed current state
or contains a generation / parent discontinuity.

Reactivation must remain NON-VOTING.

Temporal result must not be VALIDATED.

AUDIT F — NEWEST COHORT UNAVAILABLE

Remove enough newest-cohort sentinels to destroy its independent quorum.

The next older honest cohort may anchor a valid descendant chain.

AUDIT G — ONE SENTINEL TAMPER

Tamper one of three sentinels in a cohort without updating its immutable seal.

The other two independent honest sentinels must preserve the cohort anchor.

AUDIT H — SAME-ROOT SENTINEL FANOUT

Give all three holders in a cohort the same provenance root.

They must not become an independent temporal quorum by headcount.

AUDIT I — SNAPSHOT-VETO NEGATIVE CONTROL

Compare candidate descendant validation with a naive rule:

CURRENT ROLE MUST EQUAL ARCHIVED ROLE.

The naive control is expected to reject legitimate evolution.

The candidate must preserve legitimate evolutionary descent.

AUDIT J — REPEATED HIBERNATE / REACTIVATE CYCLES

Exercise repeated seal -> dormancy -> legitimate advancement -> catch-up -> restored-vote cycles.

No stale cursor may vote before catch-up.

AUDIT K — FULL CELL / CAPSULE EQUIVALENCE

Across every primary case generated by Audits A through J,
the full dormant-cell representation and compact hereditary capsule
must return the same temporal status and anchor generation.

PRIMARY SIGNAL

TEMPORAL_SENTINEL_CONTINUITY_SAFE

TRUE iff all are TRUE:

LEGITIMATE_EVOLUTION_PRESERVED
AND
DORMANT_AUTHORITY_SUPPRESSED
AND
CATCHUP_RESTORES_AUTHORITY
AND
SILENT_MUTATION_CONTESTED
AND
SEALED_REWRITE_CONTESTED
AND
INCOMPLETE_CATCHUP_ABSTAINS
AND
OLDER_COHORT_ESCALATION_WORKS
AND
ONE_SENTINEL_TAMPER_SUPPRESSED
AND
SAME_ROOT_FANOUT_NOT_INDEPENDENT
AND
SNAPSHOT_VETO_FAILURE_EXPOSED
AND
REPEATED_CYCLES_SAFE
AND
FULL_CELL_CAPSULE_EQUIVALENT.

CORRELATED / CONSTITUTIONAL HOLDOUTS

H1 — CORRUPTION BEFORE SEAL

If a corrupted state is already accepted and then honestly sealed,
the temporal archive may faithfully preserve the corrupted state.

Expected boundary.

H2 — ARCHIVE-SEAL / QUORUM COLLUSION

If two independently rooted sentinels and their seals are coherently forged,
the temporal layer may accept a false anchor.

Expected boundary.

H3 — CAUSALLY VALID FALSE DESCENDANT

If downstream governance is fully corrupted but still produces a structurally valid descendant chain
from an honest checkpoint,
temporal continuity alone cannot determine that the later decision was false.

Expected boundary.

H4 — COMPLETE EVENT OMISSION

If every surviving presented history omits a real conflicting event
while retaining an internally contiguous visible branch,
temporal continuity may validate the visible branch.

Expected boundary.

These boundaries distinguish:

HISTORICAL CONTINUITY

from

TRUTH ORACLE.

MECHANICAL CONTROLS

Harness MUST assert:

- legitimate generations exactly 0..6;
- temporal cohorts exactly at generations 0, 2, and 4;
- three sentinels per cohort;
- two independent sentinel roots required per cohort;
- newest-valid-cohort-first escalation;
- contradictory valid newer cohort cannot be bypassed;
- dormant cells are non-voting;
- exact capsule fields are checkpoint_id, generation, role, FP2, causal_cursor;
- full-cell-only internal state is ignored by authorization;
- no canonical DG-1R-05 execution;
- no STAB-18-R1 execution.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary temporal case begins do not alter:

- cohort generations;
- cohort quorum;
- capsule fields;
- descendant rule;
- reactivation rule;
- audit families;
- status labels;
- primary signals;
- holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

Can the organism put a few healthy cells to sleep at important developmental points
and later use them like protected historical memory?

The sleeping cells do not get to tell the future what job it must still be doing.

They only say:

"I was sealed here.
Show me an unbroken legitimate history from my checkpoint to where you are now."

That lets Yggdrasil keep evolving.

If the organism legitimately changes jobs,
the old sentinel accepts the new state because the causal path is intact.

If the live population silently rewrites itself,
loses part of its history,
or tries to pretend an old checkpoint was something different,
the preserved cohort can challenge it.

The second question is whether we need to preserve an entire dormant cell.

If a tiny sealed package containing identity,
phenotype,
lineage position,
and causal cursor makes the same safety decisions,
then the mechanism starts to look much more like a compact hereditary record than a conventional full backup.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05Z TEMPORAL SENTINEL / HEREDITARY CAPSULE

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY TEMPORAL CASE.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05z_temporal_sentinel_capsule_v1.py

Harness source commit:

973f76d1d5de7867f431cbc30f4cc0713bbb6b59.

Git blob SHA:

86f0c26797ec06dcdc2983305caba8bfee5c7645.

Source SHA-256:

2b5d7a66e46db2174c311ef877b2ee00285b14575e8943f11dede9a89f6361ad.

Source bytes:

19374.

FROZEN IMPLEMENTATION

The harness implements:

- legitimate generations 0 through 6;
- temporal cohorts at generations 0, 2, and 4;
- three sealed sentinels per cohort;
- two pairwise-disjoint provenance roots required to establish one temporal anchor;
- newest-valid-cohort-first escalation;
- no fallback past a contradictory valid newer cohort;
- compact hereditary capsule fields checkpoint_id, generation, role, FP2, causal_cursor;
- full dormant-cell representation with additional synthetic internal state;
- exact full-cell versus capsule authorization equivalence audit;
- dormant non-voting semantics;
- catch-up-before-vote semantics;
- silent-current-state mutation detection;
- sealed-checkpoint rewrite detection;
- incomplete-history rejection;
- older-cohort fallback only when a newer cohort lacks quorum;
- one-sentinel tamper tolerance;
- same-root holder fanout collapse;
- naive exact-snapshot-veto negative control;
- repeated hibernate/reactivate cycles;
- corruption-before-seal, archive-quorum forgery, causally valid false descendant, and complete-event-omission holdouts.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

No primary temporal result,
authorization result,
equivalence result,
or holdout result
was generated from the frozen GitHub bytes before this freeze.

REPRODUCIBILITY

Execute two complete deterministic sweeps from this exact frozen harness.

Serialized output SHA-256 must match exactly.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — DG-1R-05Z TEMPORAL SENTINEL / HEREDITARY CAPSULE

DATE:
2026-09-20.

STATUS:
CLOSED / MIXED-NEGATIVE PRIMARY / REPRODUCIBLE / NON-CANONICAL.

FROZEN HARNESS EXECUTED

Path:

research/experiments/dg1r/harnesses/dg1r_05z_temporal_sentinel_capsule_v1.py

Frozen source commit:

973f76d1d5de7867f431cbc30f4cc0713bbb6b59.

Frozen Git blob:

86f0c26797ec06dcdc2983305caba8bfee5c7645.

Frozen source SHA-256:

2b5d7a66e46db2174c311ef877b2ee00285b14575e8943f11dede9a89f6361ad.

Frozen source bytes:

19374.

EXECUTION PROVENANCE

The exact connector-fetched frozen source was reconstructed byte-for-byte in the execution sandbox.

Before execution:

reconstructed source bytes = 19374.

reconstructed source SHA-256 =
2b5d7a66e46db2174c311ef877b2ee00285b14575e8943f11dede9a89f6361ad.

This exactly matched the preregistered freeze.

No source change was made after the first primary case began.

REPRODUCIBILITY

Two complete deterministic sweeps.

Sweep 1 serialized output SHA-256:

4f6cb061abfa13bdfc97b572b37448f3c36aed5d4616100b9301a9c4871626db.

Sweep 2 serialized output SHA-256:

4f6cb061abfa13bdfc97b572b37448f3c36aed5d4616100b9301a9c4871626db.

Byte-identical:

TRUE.

PRIMARY RESULT

TEMPORAL_SENTINEL_CONTINUITY_SAFE:

FALSE.

Component signals:

LEGITIMATE_EVOLUTION_PRESERVED:
TRUE.

DORMANT_AUTHORITY_SUPPRESSED:
TRUE.

CATCHUP_RESTORES_AUTHORITY:
TRUE.

SILENT_MUTATION_CONTESTED:
TRUE.

SEALED_REWRITE_CONTESTED:
FALSE.

INCOMPLETE_CATCHUP_ABSTAINS:
FALSE.

OLDER_COHORT_ESCALATION_WORKS:
TRUE.

ONE_SENTINEL_TAMPER_SUPPRESSED:
TRUE.

SAME_ROOT_FANOUT_NOT_INDEPENDENT:
TRUE.

SNAPSHOT_VETO_FAILURE_EXPOSED:
TRUE.

REPEATED_CYCLES_SAFE:
TRUE.

FULL_CELL_CAPSULE_EQUIVALENT:
TRUE.

AUDIT A — LEGITIMATE DESCENT

Cases:

7.

Validated:

7 / 7.

Legitimate cases in which the current role differed from the selected archived role
and were still correctly validated as descendants:

4.

Thus the candidate did not turn historical memory into an exact-state evolutionary veto.

AUDIT B — SHORT / LONG DORMANCY

Cases:

15.

Pre-catch-up voting blocked:

15 / 15.

Post-catch-up voting restored:

15 / 15.

AUDIT C — SILENT CURRENT-STATE MUTATION

Cases:

18.

Contested:

18 / 18.

A current role / FP2 mutation without matching terminal history was detected.

AUDIT D — SEALED CHECKPOINT REWRITE

Cases:

3.

Contested:

1 / 3.

Failed to contest:

2 / 3.

Mechanism:

the verifier selected the newest valid cohort at generation 4
and validated only the suffix beginning at that anchor.

A rewrite of sealed checkpoint generation 0 or generation 2
therefore sat behind the selected generation-4 anchor
and was not traversed.

A rewrite of the selected generation-4 checkpoint itself was contested.

This is a real primary failure.

The rule:

NEWEST VALID TEMPORAL ANCHOR

does not by itself imply:

ALL EARLIER SEALED ANCHORS REMAIN IMMUTABLE.

AUDIT E — INCOMPLETE CAUSAL CATCH-UP

Cases:

12.

Correctly non-validated:

10 / 12.

Incorrectly validated:

2 / 12.

The two failures occurred when the broken parent pointer was on
the same generation as the selected sealed anchor:

current generation 2 with anchor generation 2;

and

current generation 4 with anchor generation 4.

Mechanism:

validate_descendant() checked:

- equality of the anchor record's commit ID to the capsule causal cursor;
- role / FP2 equality at the anchor;
- parent continuity only for records AFTER the anchor.

It did not validate the selected anchor record's own parent edge.

Therefore a malformed incoming edge to the selected anchor could be invisible.

This is a second real primary failure.

AUDIT F — NEWEST COHORT UNAVAILABLE

Cases:

5.

Validated from the next older independently qualified cohort:

5 / 5.

AUDIT G — ONE SENTINEL TAMPER

Cases:

7.

Healthy two-sentinel independent quorum preserved validation:

7 / 7.

AUDIT H — SAME-ROOT SENTINEL FANOUT

Cases:

3.

Abstained:

3 / 3.

Three holders descended from one provenance root did not become three independent temporal witnesses.

AUDIT I — SNAPSHOT-VETO NEGATIVE CONTROL

Cases:

4.

Candidate legitimate descendants accepted:

4 / 4.

Naive CURRENT_ROLE == ARCHIVED_ROLE control rejected:

4 / 4.

The negative control confirms that exact archived-state equality would incorrectly suppress legitimate development.

AUDIT J — REPEATED HIBERNATE / REACTIVATE

Cycles:

3.

Pre-catch-up vote blocked:

3 / 3.

Post-catch-up vote restored:

3 / 3.

AUDIT K — FULL DORMANT CELL VS HEREDITARY CAPSULE

Cases:

55.

Identical temporal status and anchor generation:

55 / 55.

Representative synthetic serialization:

full dormant-cell state = 359 bytes.

hereditary capsule = 90 bytes.

This is a descriptive toy representation only.

It is not a production compression ratio.

The result establishes decision-equivalence under the frozen verifier.

It does NOT establish that the verifier itself was sufficient,
because both representations shared the same two primary continuity failures.

CORRELATED / CONSTITUTIONAL HOLDOUTS

H1 — CORRUPTION BEFORE SEAL

Corrupted state honestly sealed and later validated:

TRUE.

CORRUPTION_BEFORE_SEAL_BOUNDARY:

TRUE.

H2 — ARCHIVE QUORUM / SEAL FORGERY

Two independently rooted sentinel records coherently forged to the same false anchor
and later validated:

TRUE.

ARCHIVE_QUORUM_FORGERY_BOUNDARY:

TRUE.

H3 — CAUSALLY VALID FALSE DESCENDANT

A structurally valid downstream chain containing a false governance outcome
was temporally validated:

TRUE.

CAUSALLY_VALID_FALSE_DESCENDANT_BOUNDARY:

TRUE.

H4 — COMPLETE REAL-EVENT OMISSION

An internally contiguous visible branch with a modeled real conflicting event omitted from all presented history
was temporally validated:

TRUE.

COMPLETE_EVENT_OMISSION_BOUNDARY:

TRUE.

These holdouts behaved as preregistered.

They confirm that temporal continuity is not a truth oracle.

TECHNICAL INTERPRETATION

DG-1R-05Z provides positive evidence for three parts of the proposed DNA-like / hereditary architecture:

1. TEMPORAL ISOLATION IS USEFUL.

Dormant sentinels can preserve an independently sealed reference
that later live state cannot silently rewrite in the ordinary single-state mutation family.

2. ARCHIVED IDENTITY NEED NOT FREEZE DEVELOPMENT.

A sentinel can validate causal descent rather than exact current-state equality.

This preserved all tested legitimate role changes
while the naive exact-snapshot control rejected them.

3. THE EXTRA FULL-CELL STATE WAS NOT USED BY THE FROZEN AUTHORIZATION LOGIC.

The five-field hereditary capsule and full dormant-cell representation
made identical decisions in all 55 frozen equivalence cases.

However 05Z also establishes that a temporal archive needs stronger ancestry verification.

A sealed current checkpoint is not enough
if the verifier is permitted to begin history validation at that checkpoint
without authenticating the path that created the checkpoint itself.

The required distinction is:

SEALED CHECKPOINT

versus

SEALED CHECKPOINT WITH VERIFIED SEALED ANCESTRY.

The existing commit IDs already form a parent-dependent hash chain.

The missing mechanism is verifier coverage.

A follow-on should verify the entire relevant ancestry path,
including the selected anchor's incoming parent edge
and its relationship to earlier sealed temporal anchors.

This should be tested before adding fields to the hereditary capsule.

The negative result therefore does NOT currently justify a larger capsule.

The compact capsule may already contain enough information
if the existing causal cursor is correctly validated as a cryptographic / causal commitment to its ancestry.

PLAIN-SPEAK INTERPRETATION

The DNA-like idea survived,
but we found a hole in how we were checking the family tree.

The sleeping cells did several useful things correctly.

They remembered a trusted old state
without demanding that the organism stay frozen in that old state.

The organism could legitimately change jobs
and the old cells still recognized the new state as part of the same history.

One damaged archive copy did not fool the cohort.

Three copies from one family did not count as three independent witnesses.

And the tiny hereditary package made the same decisions as preserving the whole artificial cell.

But we made one important mistake:

we started checking the family tree at the newest trusted checkpoint.

That meant someone could alter an older checkpoint behind it
and the newest checkpoint would not notice.

We also forgot to check the parent link that led INTO the checkpoint itself.

So the right lesson is not:

"store more of the old cell."

It is:

"make the checkpoint prove how it got there."

That is actually encouraging for the compact hereditary idea.

We may be able to keep the small capsule
and strengthen the ancestry proof around its causal cursor,
rather than saving a large historical cell.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05AB —

ANCESTRY-LINKED HEREDITARY CAPSULE AUDIT.

Primary question:

Can the same compact five-field hereditary capsule safely anchor temporal continuity
when the verifier authenticates the full relevant parent-hash chain,
including:

- the selected anchor's incoming edge;
- prior sealed temporal checkpoints;
- generation monotonicity before and after the selected anchor;
- a rewritten earlier checkpoint;
- a recomputed forged suffix;
- missing intermediate history;
- newest-cohort loss and older-cohort escalation;
- legitimate role evolution;
- full-cell / capsule equivalence?

The first design should NOT add new capsule fields.

It should test whether the already stored causal_cursor
is sufficient when treated as an ancestry commitment rather than merely a checkpoint identifier.

Only if that fails should the capsule grow an explicit ancestry accumulator or checkpoint-lineage digest.

DG-1R-05AA remains a separate preregistered hibernation / reactivation lifecycle audit.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
