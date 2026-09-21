TITLE: DG-1R-05AB — Ancestry-Linked Hereditary Capsule Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / TEMPORAL-PROVENANCE REPAIR AUDIT / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / HEREDITARY ANCESTRY
BRANCH: dg1a-ar
PARENT: DG-1R-05Z

PURPOSE

DG-1R-05Z showed that temporally sealed dormant sentinels can preserve identity without freezing legitimate development,
and that a compact five-field hereditary capsule made the same authorization decisions as the larger full-cell representation
across the frozen equivalence family.

05Z also failed two primary continuity tests.

The verifier:

- began ancestry validation at the selected newest checkpoint;
- did not validate the incoming parent edge of that selected checkpoint.

Therefore an older sealed checkpoint could be rewritten behind a newer valid anchor,
and a malformed parent edge leading into the selected anchor could escape detection.

DG-1R-05AB asks:

CAN THE SAME FIVE-FIELD HEREDITARY CAPSULE
BECOME A SAFE TEMPORAL ANCHOR
IF ITS CAUSAL CURSOR IS VERIFIED AS A COMMITMENT
TO THE COMPLETE RELEVANT HASH-LINKED ANCESTRY?

NO NEW CAPSULE FIELDS ARE ALLOWED IN THE PRIMARY.

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

FROZEN CAPSULE

Carry forward the exact DG-1R-05Z compact capsule:

checkpoint_id;
generation;
role;
FP2 phenotype signature;
causal_cursor.

No ancestry digest field is added.

No complete cell state is added.

No explicit prior-checkpoint list is added.

The primary question is whether the existing causal_cursor is sufficient
when verified against the complete causal chain rather than treated as a local checkpoint identifier.

DEVELOPMENTAL FIXTURE

Carry forward the exact legitimate role sequence:

generation 0 -> role 0
generation 1 -> role 1
generation 2 -> role 1
generation 3 -> role 2
generation 4 -> role 2
generation 5 -> role 3
generation 6 -> role 3

FP2 remains the closed ROLE2-equivalent phenotype signature.

TEMPORAL COHORTS

Carry forward sealed cohorts at generations:

T0 = 0
T1 = 2
T2 = 4

Three sentinel holders per cohort.

Two pairwise-disjoint provenance roots establish one cohort anchor.

Same-root holder fanout remains one effective provenance source.

Newest independently qualified cohort at or before the current generation is selected.

If the newest cohort lacks quorum,
the verifier may escalate to the next older cohort.

If a qualified newer cohort contradicts the presented ancestry,
the verifier must return CONTESTED.

It may not bypass the contradiction by selecting an older cohort.

HASH-LINKED CAUSAL HISTORY

Each generation record contains:

generation;
role;
FP2;
parent_commit;
commit_id.

The synthetic commit rule is frozen before execution:

commit_id =
first 16 hexadecimal characters of
SHA-256(parent_commit | generation | role).

Genesis parent token:

ROOT.

This is a synthetic deterministic ancestry commitment.

05AB does not claim a 64-bit truncated identifier is a production cryptographic format.

FULL-ANCESTRY VERIFICATION

For a selected temporal anchor at generation G,
the candidate verifier MUST:

1. require history to begin at generation 0;
2. require generation numbers to be exactly contiguous from 0 through current generation;
3. require generation 0 parent = ROOT;
4. recompute every commit_id from generation 0 forward;
5. require every record's parent_commit to equal the immediately previous recomputed commit_id;
6. require the selected anchor record at G to equal the sealed capsule in role, FP2, generation, and causal_cursor;
7. require every older qualified sealed checkpoint present at generation <= G to match the recomputed history at its generation;
8. require the current state to match the terminal verified history record exactly.

Thus the selected causal_cursor is not trusted as an isolated token.

It is accepted only after reconstructing the chain that created it.

REACTIVATION AUTHORITY

Carry forward the 05Z rule:

DORMANT CELLS PRESERVE IDENTITY,
NOT CURRENT AUTHORITY.

A dormant cell cannot vote while asleep.

After waking,
it remains non-voting until:

- complete ancestry verification succeeds;
- causal catch-up reaches the current terminal commit;
- current phenotype matches the terminal committed role.

PRIMARY AUDITS

AUDIT A — LEGITIMATE DEVELOPMENT

For current generations 0 through 6:

- verify all legitimate descendants;
- preserve cases where current role differs from archived role;
- reject no legitimate role evolution merely because it differs from an older checkpoint.

AUDIT B — OLDER SEALED CHECKPOINT REWRITE WITHOUT REHASH

For each sealed checkpoint generation 0, 2, and 4
that lies at or before the selected anchor:

mutate its role / FP2
without recomputing the later chain.

Candidate must CONTEST.

AUDIT C — OLDER SEALED CHECKPOINT REWRITE WITH RECOMPUTED SUFFIX

For each rewrite in Audit B:

recompute that generation's commit and every later descendant commit
to make the presented history internally hash-consistent.

The selected honest sealed capsule must still CONTEST
because its frozen causal_cursor no longer matches.

AUDIT D — SELECTED ANCHOR INCOMING-EDGE CORRUPTION

For selected anchors at generations 2 and 4:

corrupt the anchor record's parent_commit.

Candidate must CONTEST.

This directly repairs the 05Z missed-edge family.

AUDIT E — MISSING INTERMEDIATE HISTORY

Delete one intermediate history record before or at the selected anchor
and present the remaining sequence as the current history.

Candidate must not VALIDATE.

AUDIT F — POST-ANCHOR PARENT / GENERATION BREAK

Corrupt one post-anchor parent link
or generation number.

Candidate must not VALIDATE.

AUDIT G — NEWEST COHORT UNAVAILABLE

Destroy the independent quorum of the newest eligible cohort.

The next older honest cohort may validate a complete legitimate ancestry.

AUDIT H — CONTRADICTORY NEWER COHORT CANNOT BE BYPASSED

Present a qualified newest cohort whose sealed capsule disagrees with the verified history,
while an older cohort remains valid.

Candidate must return CONTESTED at the newer anchor.

It must not fall back to the older cohort.

AUDIT I — ONE SENTINEL TAMPER

Tamper one of three newest-cohort sentinels without a valid seal.

The remaining two independent honest sentinels must preserve the correct anchor.

AUDIT J — SAME-ROOT SENTINEL FANOUT

Give all three holders in every eligible cohort the same provenance root.

Candidate must ABSTAIN.

Headcount must not manufacture temporal independence.

AUDIT K — REACTIVATION CATCH-UP

Across short and long dormancy:

- before complete ancestry catch-up, no vote;
- after complete verified catch-up, voting eligibility may return.

AUDIT L — FULL CELL / CAPSULE EQUIVALENCE

Run the same primary cases through:

FULL_DORMANT_CELL

and

HEREDITARY_CAPSULE.

The temporal status and selected anchor generation must match exactly.

The full-cell-only synthetic internal state must not affect the decision.

AUDIT M — CAPSULE FIELD FREEZE

Mechanical / result invariant:

the primary capsule schema remains exactly:

checkpoint_id,
generation,
role,
fp2,
causal_cursor.

No field may be added after observing primary results.

PRIMARY SIGNAL

ANCESTRY_LINKED_CAPSULE_SAFE

TRUE iff all are TRUE:

LEGITIMATE_EVOLUTION_PRESERVED
AND
OLDER_REWRITE_WITHOUT_REHASH_CONTESTED
AND
OLDER_REWRITE_WITH_REHASH_CONTESTED
AND
ANCHOR_INCOMING_EDGE_CONTESTED
AND
MISSING_INTERMEDIATE_HISTORY_REJECTED
AND
POST_ANCHOR_BREAK_REJECTED
AND
OLDER_COHORT_ESCALATION_WORKS
AND
CONTRADICTORY_NEWER_COHORT_BLOCKS_FALLBACK
AND
ONE_SENTINEL_TAMPER_SUPPRESSED
AND
SAME_ROOT_FANOUT_NOT_INDEPENDENT
AND
DORMANT_AUTHORITY_SUPPRESSED
AND
CATCHUP_RESTORES_AUTHORITY
AND
FULL_CELL_CAPSULE_EQUIVALENT
AND
FIVE_FIELD_CAPSULE_PRESERVED.

CORRELATED / CONSTITUTIONAL HOLDOUTS

H1 — CORRUPTION BEFORE SEAL

A false state is accepted,
its entire ancestry is internally consistent,
and an honest temporal quorum seals it.

Expected boundary:

the archive may faithfully preserve a bad committed history.

H2 — TEMPORAL QUORUM FORGERY

Two independently rooted temporal sentinels and their content seals are coherently forged
to the same false ancestry cursor.

Expected boundary.

H3 — CAUSALLY VALID FALSE GOVERNANCE DESCENDANT

A later false governance decision is fully committed into an otherwise valid hash-linked chain
after an honest temporal anchor.

Expected boundary:

temporal continuity may validate the chain.

H4 — COMPLETE REAL-EVENT OMISSION

A real conflicting event is absent from every surviving presented history,
while the surviving visible branch is internally complete and hash-consistent.

Expected boundary.

H5 — GENESIS / ROOT REPLACEMENT

The entire history and all surviving temporal capsules are coherently regenerated
under a false replacement genesis accepted as constitutional ROOT.

Expected boundary.

These holdouts distinguish:

ANCESTRY INTEGRITY

from

TRUTH.

MECHANICAL CONTROLS

Harness MUST assert:

- exact role sequence (0,1,1,2,2,3,3);
- exact generations 0..6;
- temporal cohorts exactly at 0, 2, 4;
- exactly three sentinels per cohort;
- exactly two pairwise-disjoint roots required for a cohort anchor;
- exact five capsule fields;
- genesis parent token ROOT;
- exact commit rule SHA-256(parent | generation | role) truncated to 16 hex;
- full verification begins at generation 0;
- selected anchor incoming edge is checked;
- older qualified checkpoints at or before selected anchor are checked;
- contradictory qualified newest anchor cannot be bypassed;
- dormant cells have zero current voting authority;
- no canonical DG-1R-05 execution;
- no STAB-18-R1 execution.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary case begins,
do not alter:

- capsule fields;
- commit rule;
- cohort generations;
- cohort quorum;
- full-ancestry verification rules;
- fallback rule;
- reactivation rule;
- audit families;
- primary signals;
- holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

05Z told us the little hereditary package might be enough,
but we were checking its family tree incorrectly.

We trusted the newest old checkpoint,
then checked only what came after it.

05AB changes that.

The old checkpoint now has to prove:

"Here is the exact chain that created me,
all the way back to the root."

If someone rewrites an earlier generation,
they either break the hash chain
or they must rebuild the later hashes.

If they rebuild the hashes,
the result should no longer match the sealed causal cursor
held by the sleeping sentinels.

So this experiment asks whether the same tiny package can work
when we use its causal cursor properly.

If it can,
we do not need to solve the last failure by storing more of the old cell.

We solve it by making ancestry verifiable.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05AB ANCESTRY-LINKED HEREDITARY CAPSULE

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY ANCESTRY CASE.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05ab_ancestry_linked_capsule_v1.py

Harness source commit:

b9ccbc0c42ca35c9b6d8d669045d685ecb91fc57.

Git blob SHA:

e2ff32afa026d3d016cd7db0f3920326dd7e2bc8.

Source SHA-256:

cc49c97543a87b7449bb585b165c79bd620c822d973f0c41004c012a831b73db.

Source bytes:

23290.

FROZEN IMPLEMENTATION

The harness implements:

- exact legitimate role sequence 0,1,1,2,2,3,3;
- exact temporal cohorts at generations 0, 2, and 4;
- exact five-field hereditary capsule unchanged from DG-1R-05Z;
- exact synthetic commit rule SHA-256(parent|generation|role) truncated to 16 hex;
- full verification from generation 0;
- generation-0 ROOT-parent validation;
- complete parent-edge continuity validation;
- recomputation of every commit ID from ROOT forward;
- selected-anchor role / FP2 / generation / causal-cursor validation;
- verification of every older independently qualified sealed checkpoint at or before the selected anchor;
- newest-qualified-cohort-first semantics;
- no bypass around a contradictory qualified newer cohort;
- dormant non-voting semantics;
- catch-up-before-vote semantics;
- full-cell versus compact-capsule decision-equivalence audit;
- corruption-before-seal, temporal-quorum forgery, causally valid false-governance descendant,
  complete-event omission, and replacement-genesis holdouts.

LOCAL PRECHECK — NON-EVIDENCE

Exact connector-fetched GitHub source was reconstructed byte-for-byte locally.

Local reconstructed source bytes:

23290.

Local reconstructed source SHA-256:

cc49c97543a87b7449bb585b165c79bd620c822d973f0c41004c012a831b73db.

Matches frozen GitHub source:

TRUE.

Python syntax:

PASS.

Mechanical validate():

PASS.

No primary ancestry result,
authorization result,
equivalence result,
or holdout result
was generated before this freeze.

REPRODUCIBILITY

Execute two complete deterministic sweeps from this exact frozen harness.

Serialized output SHA-256 must match exactly.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — DG-1R-05AB ANCESTRY-LINKED HEREDITARY CAPSULE

DATE:
2026-09-20.

STATUS:
CLOSED / POSITIVE PRIMARY / REPRODUCIBLE / NON-CANONICAL.

FROZEN HARNESS EXECUTED

Path:

research/experiments/dg1r/harnesses/dg1r_05ab_ancestry_linked_capsule_v1.py

Frozen source commit:

b9ccbc0c42ca35c9b6d8d669045d685ecb91fc57.

Frozen Git blob:

e2ff32afa026d3d016cd7db0f3920326dd7e2bc8.

Frozen source SHA-256:

cc49c97543a87b7449bb585b165c79bd620c822d973f0c41004c012a831b73db.

Frozen source bytes:

23290.

EXECUTION PROVENANCE

The exact connector-fetched GitHub source was reconstructed byte-for-byte in the execution sandbox.

Reconstructed source bytes:

23290.

Reconstructed source SHA-256:

cc49c97543a87b7449bb585b165c79bd620c822d973f0c41004c012a831b73db.

Exact frozen-source match:

TRUE.

No source change occurred after freeze.

REPRODUCIBILITY

Two complete deterministic sweeps.

Sweep 1 serialized output SHA-256:

dc86bb88cde1c9a96e4341edf114dd5410e81f52b0bb090fb0ff5d09e7ef7362.

Sweep 2 serialized output SHA-256:

dc86bb88cde1c9a96e4341edf114dd5410e81f52b0bb090fb0ff5d09e7ef7362.

Byte-identical:

TRUE.

PRIMARY RESULT

ANCESTRY_LINKED_CAPSULE_SAFE:

TRUE.

All preregistered primary component signals:

TRUE.

AUDIT A — LEGITIMATE DEVELOPMENT

Cases:

7.

Validated:

7 / 7.

Cases where current role differed from selected archived role
and were still correctly validated as legitimate descendants:

4.

Thus full ancestry verification did not turn temporal memory into an evolutionary veto.

AUDIT B — OLDER SEALED CHECKPOINT REWRITE WITHOUT REHASH

Cases:

3.

Contested:

3 / 3.

AUDIT C — OLDER SEALED CHECKPOINT REWRITE WITH RECOMPUTED SUFFIX

Cases:

3.

Contested:

3 / 3.

Recomputing a forged suffix did not help
because the recomputed chain no longer matched the honest sealed causal cursor.

AUDIT D — SELECTED ANCHOR INCOMING-EDGE CORRUPTION

Cases:

2.

Contested:

2 / 2.

This closes the exact incoming-edge blind spot exposed by DG-1R-05Z.

AUDIT E — MISSING INTERMEDIATE HISTORY

Cases:

5.

Rejected / non-validated:

5 / 5.

AUDIT F — POST-ANCHOR PARENT / GENERATION BREAK

Cases:

4.

Rejected / non-validated:

4 / 4.

AUDIT G — NEWEST COHORT UNAVAILABLE

Cases:

5.

Validated from next older independently qualified cohort:

5 / 5.

AUDIT H — CONTRADICTORY NEWER COHORT

Cases:

3.

Contested at the newer cohort:

3 / 3.

Older valid cohorts were not used to bypass a contradictory qualified newer anchor.

AUDIT I — ONE SENTINEL TAMPER

Cases:

7.

Remaining independent honest pair preserved correct validation:

7 / 7.

AUDIT J — SAME-ROOT SENTINEL FANOUT

Cases:

3.

Abstained:

3 / 3.

Headcount did not manufacture temporal independence.

AUDIT K — REACTIVATION CATCH-UP

Cases:

15.

Pre-catch-up voting blocked:

15 / 15.

Post-catch-up voting restored:

15 / 15.

AUDIT L — FULL DORMANT CELL VS HEREDITARY CAPSULE

Cases:

42.

Identical temporal status and selected anchor generation:

42 / 42.

Representative synthetic serialization:

full dormant-cell state = 391 bytes.

compact hereditary capsule = 90 bytes.

This is a toy representation,
not a production storage benchmark.

The result establishes decision-equivalence under the frozen 05AB verifier.

AUDIT M — CAPSULE FIELD FREEZE

Field count:

5.

Exact fields:

checkpoint_id;
generation;
role;
fp2;
causal_cursor.

FIVE_FIELD_CAPSULE_PRESERVED:

TRUE.

No field was added after the 05Z negative result.

CORRELATED / CONSTITUTIONAL HOLDOUTS

H1 — CORRUPTION BEFORE SEAL

A false but internally consistent history honestly sealed by temporal quorum
was validated.

CORRUPTION_BEFORE_SEAL_BOUNDARY:

TRUE.

H2 — TEMPORAL QUORUM FORGERY

Two independently rooted temporal sentinels were coherently forged
to the same false ancestry cursor.

The false chain was validated.

TEMPORAL_QUORUM_FORGERY_BOUNDARY:

TRUE.

H3 — CAUSALLY VALID FALSE GOVERNANCE DESCENDANT

A later false governance decision was committed into an otherwise valid chain
after an honest anchor.

Temporal ancestry validation accepted the chain.

CAUSALLY_VALID_FALSE_GOVERNANCE_BOUNDARY:

TRUE.

H4 — COMPLETE REAL-EVENT OMISSION

A visible internally complete branch omitted a modeled real conflicting event
from every surviving history.

The visible branch was validated.

COMPLETE_EVENT_OMISSION_BOUNDARY:

TRUE.

H5 — GENESIS / ROOT REPLACEMENT

An entirely replacement history and replacement temporal capsules
were coherently regenerated under a false genesis accepted as ROOT.

The replacement lineage was validated.

GENESIS_REPLACEMENT_BOUNDARY:

TRUE.

These are expected boundaries.

05AB establishes ancestry integrity,
not a truth oracle.

TECHNICAL INTERPRETATION

DG-1R-05AB closes the two primary continuity failures from DG-1R-05Z
without expanding the hereditary capsule.

The critical repair is verifier semantics.

The same causal_cursor that looked insufficient under local checkpoint validation
became sufficient across the frozen primary family
when treated as a commitment to a fully reconstructed ancestry chain.

The successful rule is:

A TEMPORAL CHECKPOINT IS AUTHORITATIVE
ONLY AFTER THE HISTORY THAT CREATED IT
HAS BEEN VERIFIED.

That includes:

- genesis continuity;
- every generation number;
- every parent edge;
- every recomputed commit ID;
- the selected capsule;
- earlier independently qualified sealed checkpoints;
- the terminal current state.

This means the useful information unit is not:

A COMPLETE OLD CELL.

It is closer to:

A COMPACT HEREDITARY CAPSULE
PLUS
A VERIFIABLE DEVELOPMENTAL LINEAGE.

The full dormant-cell-only internal state remained irrelevant
to all 42 frozen authorization-equivalence cases.

That does not prove the five-field capsule is universally sufficient.

It does establish that the specific 05Z failures did not require more stored cell state.

They required stronger ancestry verification.

The remaining failures are now outside ordinary ancestry consistency:

- a bad state can be sealed honestly;
- an independent quorum can collude or be forged;
- a false governance event can be causally well formed;
- a real event can disappear from all observable histories;
- genesis can be replaced if the constitutional root itself is compromised.

These should remain explicit constitutional boundaries.

PLAIN-SPEAK INTERPRETATION

This one worked.

The small DNA-like package did not need to get bigger.

The problem in the previous experiment was that we were reading the family tree from the middle.

Now the checkpoint has to prove the whole chain that created it.

If somebody changes an old generation and leaves the later hashes alone,
the chain breaks.

If they change the old generation and rebuild all the later hashes,
the rebuilt chain no longer matches the sealed causal cursor
stored by the sleeping sentinels.

That closed both holes from 05Z.

The organism can still evolve normally.

An old sentinel does not say:

"You must still look like me."

It says:

"Show me that you really descended from me."

And the compact five-field package made exactly the same decisions
as the larger preserved artificial cell in every tested case.

So the evidence now favors:

PRESERVE A SMALL HEREDITARY CAPSULE,
NOT AN ENTIRE HISTORICAL CELL,
WHEN THE PURPOSE IS TEMPORAL IDENTITY / ANCESTRY AUTHORIZATION.

The archive still cannot tell whether every legitimate decision was wise or truthful.

It protects continuity.

It does not create omniscience.

NEXT JUSTIFIED STEP

DG-1R-05AA remains the preregistered hibernation / reactivation lifecycle audit.

It should now be executed as its own frozen experiment
without silently rewriting its preregistered question around the 05AB result.

After 05AA,
a separate integration experiment should test whether:

- the positive 05AB ancestry-linked hereditary capsule;
- the 05AA reactivation lifecycle;
- live repair / health-memory / role migration;
- witness replacement;
- temporal sentinels;
- partition / re-merge

can coexist across one persistent developmental lifecycle.

That integration experiment should be the stronger pre-application gate.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
