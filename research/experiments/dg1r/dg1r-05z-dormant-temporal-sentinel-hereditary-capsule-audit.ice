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
