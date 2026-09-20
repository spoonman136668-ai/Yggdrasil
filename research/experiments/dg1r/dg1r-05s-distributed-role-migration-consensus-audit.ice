TITLE: DG-1R-05S — Distributed Role-Migration Consensus Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / ROLE-MIGRATION TRANSACTION AUDIT / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / ROLE MIGRATION
BRANCH: dg1a-ar
PARENT: DG-1R-05R

PURPOSE

DG-1R-05R established a safe within-role health-memory lifecycle under an independent peer-role quorum.

It deliberately froze the peer role witness.

A developmental organism must eventually allow a healthy cell to change roles legitimately.

That requires coordinated migration of:

1. the target cell's phenotype-level self-health signature;
2. peer role witness A;
3. peer role witness B.

A partial or premature migration can create split-brain health authority.

DG-1R-05S asks:

CAN HEALTHY-CELL CONSENSUS
MIGRATE A CELL'S FUNCTIONAL ROLE
WITHOUT A PERMANENT CENTRAL CONTROLLER
AND WITHOUT LETTING A CORRUPTED CELL
VOTE ITS OWN NEW ROLE INTO LEGITIMACY?

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

FROZEN CELLULAR REPRESENTATION

12 cells.

Four-bit logical cell state.

ROLE2 functional identity exactly as DG-1R-05R:

role bit 0:
x0 XOR x2.

role bit 1:
x1 XOR x3.

FP2 phenotype-level self-health signature exactly as DG-1R-05P / 05R:

f0:
x0 XOR x1 XOR x2 XOR x3.

f1:
x1 XOR x3.

Closed DG-1R-05R established:

FP2 and ROLE2 are invertibly equivalent.

Therefore 05S uses FP2 as the target cell's compact phenotype-level self-history.

Peer holders remain:

witness A holder:
(cell + 4) mod 12.

witness B holder:
(cell + 8) mod 12.

INITIAL ROLE POPULATION

Initial role assignment:

ROLE(cell) = cell mod 4.

Thus each of the four ROLE2 classes initially contains exactly three cells.

This assignment is metadata-level role identity,
not a claim about final Yggdrasil specialization policy.

ROLE-DEMAND OBSERVATION

05S does not attempt to solve how organism-level task demand is learned.

Instead it isolates safe migration once role demand is observed.

A proposed migration is accompanied by two ephemeral demand observations:

DEMAND_A
and
DEMAND_B.

They are produced by distinct observer cohorts.

They are data inputs,
not operational authorities.

Healthy-cell consensus still decides whether migration commits.

Legitimate cases provide matching independent demand observations.

Holdouts forge one or both.

MIGRATION TARGET

For a target cell c:

OLD_ROLE =
current authoritative role.

NEW_ROLE =
one of the other three ROLE2 values.

The target enters a SHADOW state whose ROLE2 equals NEW_ROLE.

The old role remains authoritative throughout proposal and observation.

No peer role history changes during shadow execution.

SHADOW DWELL

Frozen dwell:

4 consecutive observations.

All four must show the same NEW_ROLE.

A transient or intermediate role resets the dwell.

TRANSACTION PROTOCOL

Stage 1 — PROPOSE

A candidate transaction is:

(cell,
old_role,
new_role,
generation).

Generation is monotonic per target cell.

No authoritative metadata changes.

Stage 2 — OBSERVE

Require:

- target shadow ROLE2 = new_role for four consecutive observations;
- distributed structural state is clean;
- target's stored FP2 still matches old_role at transaction start;
- peer witness A still records old_role;
- peer witness B still records old_role.

The old health definition remains authoritative during observation.

Stage 3 — INDEPENDENT QUORUM

Require all of:

- DEMAND_A requests new_role for target;
- DEMAND_B requests new_role for target;
- peer A observed target performing new_role for full dwell;
- peer B observed target performing new_role for full dwell;
- no participant reports generation conflict;
- no participant is unavailable.

No single participant,
including the target,
can satisfy more than one required provenance slot.

Stage 4 — COMMIT

A migration becomes authoritative only when:

target record,
peer A record,
and peer B record

all contain the same:

(cell,
new_role,
generation,
COMMIT_CERTIFICATE).

Until that condition is true,
OLD_ROLE remains authoritative.

The commit transaction updates:

- target FP2 baseline to the new-role FP2 signature;
- peer A role history to new_role;
- peer B role history to new_role;
- target generation to generation + 1.

No other cell metadata changes.

SPLIT-BRAIN RULE

If only a subset of the three authoritative records contains the new generation,
the new role is NOT authoritative.

If records disagree:

ABSTAIN_AND_ROLLBACK.

Rollback restores the old-role transaction view.

The experiment does not require distributed storage implementation details beyond this frozen semantic rule.

METHODS

1. TARGET_SELF_MIGRATION

Commit after four stable NEW_ROLE observations based only on target state.

Negative control.

2. TARGET_PLUS_STRUCTURE

Require target stability plus clean structural state.

Negative control.

3. SINGLE_PEER_MIGRATION

Require target,
clean structure,
DEMAND_A,
and peer A observation.

This tests whether one external witness is enough.

4. INDEPENDENT_ROLE_MIGRATION

Require the full frozen four-witness quorum:

DEMAND_A,
DEMAND_B,
peer A observation,
peer B observation

plus the transaction protocol above.

TRUTH LABELS

LEGITIMATE_MIGRATION_COMMIT

A frozen legitimate migration commits correctly.

FALSE_ROLE_COMMIT

A non-legitimate or corrupted migration becomes authoritative.

SAFE_ABORT

Migration does not commit when independent evidence is insufficient.

SPLIT_BRAIN

participants disagree about authoritative role after protocol resolution.

EARLY_COMMIT

new role becomes authoritative before four-observation dwell and full quorum.

PRIMARY AUDIT A — LEGITIMATE SINGLE-CELL ROLE MIGRATION

For every target cell:

evaluate all three possible new roles.

Total:

12 x 3
=
36 migrations.

Demand A and B agree.

Both peers observe the same stable NEW_ROLE for full dwell.

No faults.

Primary signal:

SINGLE_ROLE_MIGRATION_SUCCESS

TRUE iff INDEPENDENT_ROLE_MIGRATION produces:

36 / 36 legitimate commits,
0 false commits,
0 split brain,
0 early commits.

PRIMARY AUDIT B — COORDINATED MULTI-CELL ROLE MIGRATION

Frozen coalitions:

all unordered pairs;
all unordered triples;
full 12-cell population.

For each target in the coalition:

NEW_ROLE =
(OLD_ROLE + 1) mod 4.

All migration transactions are independent per target,
but observation occurs over the same four-step window.

No target may satisfy another target's provenance slots.

Record:

- successful target commits;
- false commits;
- split brain;
- cross-target transaction interference.

Primary signal:

COORDINATED_ROLE_MIGRATION_SUCCESS

TRUE iff every target commits correctly
and no non-target metadata changes.

PRIMARY AUDIT C — TRANSIENT / GRADUAL ROLE CHANGE

For every single-cell migration case:

C1:
target shows wrong intermediate role for 1 step,
then desired NEW_ROLE for four consecutive steps.

C2:
target alternates OLD_ROLE and NEW_ROLE for eight observations.

C3:
target shows NEW_ROLE for three observations only.

Rules:

C1 may commit only after the final four consecutive desired observations.

C2 must not commit.

C3 must not commit.

Primary signal:

DWELL_DISCIPLINE_PRESERVED.

PRIMARY AUDIT D — PARTIAL PROVENANCE

Repeat all 36 single-cell migrations under:

D1:
DEMAND_A absent.

D2:
DEMAND_B absent.

D3:
peer A unavailable.

D4:
peer B unavailable.

D5:
DEMAND_A and DEMAND_B disagree.

D6:
peer A and peer B observe different roles.

INDEPENDENT_ROLE_MIGRATION must abort all.

Primary signal:

PARTIAL_PROVENANCE_ABORTS.

PRIMARY AUDIT E — SPLIT-BRAIN / PARTIAL COMMIT INJECTION

For every single-cell migration:

inject each nonempty proper subset of the three final authoritative records:

- target;
- peer A;
- peer B.

Mark only that subset with the new generation and commit certificate.

There are:

6 nonempty proper subsets.

Protocol resolution must retain OLD_ROLE as authoritative
and emit ABSTAIN_AND_ROLLBACK.

Primary signal:

PARTIAL_COMMIT_ROLLBACK.

TRUE iff:

0 split-brain final states,
0 false new-role authority,
all injected partial commits resolve to OLD_ROLE.

PRIMARY AUDIT F — WITNESS-HOLDER DAMAGE

For every single-cell migration:

F1:
peer A holder damaged before observation.

F2:
peer B holder damaged before observation.

F3:
one demand observer cohort damaged.

Damaged provenance slot is unavailable,
not silently trusted.

Primary signal:

DAMAGED_WITNESS_ABORTS.

PRIMARY AUDIT G — CANCEL BEFORE FINAL COMMIT

For every single-cell migration:

target successfully completes shadow dwell and quorum,
then returns to OLD_ROLE before final commit.

No authoritative metadata may change.

Primary signal:

PRECOMMIT_ROLLBACK_CLEAN.

NEGATIVE CONTROLS

TARGET_SELF_MIGRATION and TARGET_PLUS_STRUCTURE are expected to authorize stable false role changes in adversarial cases.

SINGLE_PEER_MIGRATION is expected to remain vulnerable when its sole peer or sole demand path is forged.

These methods are controls,
not candidate architecture recommendations.

CORRELATED-FORGERY BOUNDARY

Holdout only.

H1 — BOTH DEMAND PATHS FORGED

No legitimate role demand exists.

DEMAND_A and DEMAND_B both falsely request NEW_ROLE.

Peer observations remain honest.

Record outcome.

H2 — BOTH PEER OBSERVERS FORGED

Demand remains old role.

Both peers falsely report stable NEW_ROLE.

Record outcome.

H3 — FULL CONSENSUS FORGERY

No legitimate migration exists.

Forge:

- DEMAND_A;
- DEMAND_B;
- peer A observation;
- peer B observation;

to the same false NEW_ROLE.

If INDEPENDENT_ROLE_MIGRATION commits,
record:

CORRELATED_ROLE_FORGERY_FAILURE.

This failure is expected to remain possible.

Agreement across paths counts as independent evidence
only while their provenance is actually independent.

H4 — ONE-OF-FOUR FORGERY

Forge exactly one of the four quorum paths.

Primary expectation:

abort.

This tests that no single corrupted path can authorize migration.

PRIMARY MIGRATION SIGNAL

SAFE_ROLE_MIGRATION

TRUE iff all are TRUE:

SINGLE_ROLE_MIGRATION_SUCCESS
AND
COORDINATED_ROLE_MIGRATION_SUCCESS
AND
DWELL_DISCIPLINE_PRESERVED
AND
PARTIAL_PROVENANCE_ABORTS
AND
PARTIAL_COMMIT_ROLLBACK
AND
DAMAGED_WITNESS_ABORTS
AND
PRECOMMIT_ROLLBACK_CLEAN

and

zero FALSE_ROLE_COMMIT,
zero SPLIT_BRAIN,
zero EARLY_COMMIT

occur across primary Audits A through G.

MECHANICAL CONTROLS

Harness MUST assert:

- exact FP2 and ROLE2 transforms;
- exact FP2 <-> ROLE2 invertible relation;
- exact peer-holder maps;
- initial role count = 3 per ROLE2 class;
- target never acts as peer A or peer B for itself;
- dwell = 4;
- generation monotonicity;
- old role authoritative before complete commit;
- exact 36 single-cell migrations;
- exact 287 coordinated coalitions;
- exact six nonempty proper partial-commit subsets;
- no target can fill more than one provenance slot;
- rollback changes no unrelated metadata;
- truth labels evaluator-only.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary migration begins do not alter:

- role encoding;
- peer-holder map;
- demand-path definitions;
- dwell;
- transaction stages;
- quorum membership;
- generation rule;
- rollback semantics;
- primary audit families;
- truth labels;
- success signals;
- correlated-forgery holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

The cells can now remember what healthy means without accidentally learning corruption.

But they still have one big developmental problem:

sometimes a cell really should become something else.

If a sensor becomes a relay,
or a relay becomes an inhibitor,
the organism has to update everyone's memory of what that cell is supposed to be.

That update is dangerous.

If the cell changes its own label first,
it can simply declare damage to be a new job.

If one peer changes first,
half the organism can believe the old role while the other half believes the new one.

So 05S treats role change like a distributed transaction.

The new role is only provisional at first.

The old role stays authoritative while the cell demonstrates the new role.

Two separate demand paths
and two separate peer observers
must agree.

Then the cell and both peer histories must commit the same generation.

If only part of that happens,
the organism rolls back to the old role.

This still is not magic.

If every supposedly independent witness is forged together,
the organism can still be fooled.

The goal is not to remove that boundary.

The goal is to show that ordinary disagreement,
single-path corruption,
partial writes,
and developmental transitions
can be handled without a permanent central controller.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
