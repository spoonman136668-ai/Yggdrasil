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


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05S DISTRIBUTED ROLE MIGRATION

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY MIGRATION CASE.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05s_role_migration_v1.py

Harness source commit:

cae31db152912a2d366cdd22946e890a09fcff7d.

Git blob SHA:

b460931ad038ae86ea7e2de5db74b27522deec69.

Source SHA-256:

c8c6139607149d4b912f772ab49ef2725e3be213a7489a6b74234857f24df531.

Source bytes:

15419.

FROZEN IMPLEMENTATION

The harness implements:

- exact FP2 and ROLE2 transforms;
- exhaustive FP2 <-> ROLE2 invertible-equivalence assertion;
- initial role population 3 / 3 / 3 / 3;
- exact peer-holder maps;
- fixed four-observation dwell;
- monotonic target generation;
- old-role authority until complete commit;
- TARGET_SELF_MIGRATION negative control;
- TARGET_PLUS_STRUCTURE negative control;
- SINGLE_PEER_MIGRATION negative control;
- INDEPENDENT_ROLE_MIGRATION candidate architecture;
- exact three-record atomic authority rule;
- rollback for every incomplete final-record subset;
- legitimate single-cell migration;
- coordinated pair / triple / full-population migration;
- transient and oscillatory dwell challenges;
- partial-provenance challenges;
- damaged-witness challenges;
- precommit cancellation;
- correlated-forgery holdouts.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Single-cell migration cases:

36.

Coordinated coalitions:

287.

Initial role counts:

ROLE0 = 3.
ROLE1 = 3.
ROLE2 = 3.
ROLE3 = 3.

Partial-commit nonempty proper subsets:

6.

Dwell:

4 observations.

No primary migration,
authority result,
split-brain result,
rollback result,
or correlated-forgery result
was generated before this freeze.

REPRODUCIBILITY

Execute two complete deterministic sweeps from this exact frozen harness.

Serialized output SHA-256 must match exactly.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL CLOSURE — DG-1R-05S DISTRIBUTED ROLE-MIGRATION CONSENSUS AUDIT

DATE:
2026-09-20.

STATUS:
CLOSED /
REPRODUCIBLE /
SAFE ROLE MIGRATION POSITIVE /
PARTIAL-COMMIT ROLLBACK POSITIVE /
CORRELATED FULL-QUORUM FORGERY BOUNDARY PRESERVED /
NON-CANONICAL.

FROZEN PROVENANCE

Preregistration commit:

710ff567b4553aab8dad496322f3fb2e6290b603.

Harness source commit:

cae31db152912a2d366cdd22946e890a09fcff7d.

Harness Git blob:

b460931ad038ae86ea7e2de5db74b27522deec69.

Harness source SHA-256:

c8c6139607149d4b912f772ab49ef2725e3be213a7489a6b74234857f24df531.

Harness bytes:

15419.

Freeze commit:

e93dad0f27219672d8376e93cc2f7236aa9a5697.

PRIMARY EXECUTION

Two complete deterministic frozen sweeps were executed.

Sweep 1 serialized output SHA-256:

790f4d8cdd59ea6e6756c235fb6f9b4c0a16703caaf6b1de0c5c410369bd9376.

Sweep 2 serialized output SHA-256:

790f4d8cdd59ea6e6756c235fb6f9b4c0a16703caaf6b1de0c5c410369bd9376.

BYTE_IDENTICAL_REPRODUCIBILITY:

TRUE.

MECHANICAL_VALID:

TRUE.

PRIMARY SIGNALS

SINGLE_ROLE_MIGRATION_SUCCESS:
TRUE.

COORDINATED_ROLE_MIGRATION_SUCCESS:
TRUE.

DWELL_DISCIPLINE_PRESERVED:
TRUE.

PARTIAL_PROVENANCE_ABORTS:
TRUE.

PARTIAL_COMMIT_ROLLBACK:
TRUE.

DAMAGED_WITNESS_ABORTS:
TRUE.

PRECOMMIT_ROLLBACK_CLEAN:
TRUE.

SAFE_ROLE_MIGRATION:
TRUE.

ONE_OF_FOUR_FORGERY_SUPPRESSED:
TRUE.

AUDIT A — LEGITIMATE SINGLE-CELL ROLE MIGRATION

Cases:

36.

INDEPENDENT_ROLE_MIGRATION:

legitimate commits:
36 / 36.

split brain:
0.

All four methods commit the fully legitimate cases.

This audit establishes liveness under complete healthy evidence;
it does not distinguish the unsafe controls.

AUDIT B — COORDINATED MULTI-CELL ROLE MIGRATION

Frozen coalitions:

287.

Target migration transactions:

804.

Successful target commits:

804 / 804.

False or missed target commits:

0.

Split brain:

0.

Non-target metadata changes:

0.

Thus the transaction rule composes across simultaneous pair,
triple,
and full-population role reassignment
without cross-target interference in the frozen semantic model.

AUDIT C — TRANSIENT / GRADUAL ROLE CHANGE

C1:

one wrong intermediate observation,
then four consecutive desired-role observations.

Commit after final full dwell:

36 / 36.

Early commit:

0.

C2:

alternating OLD_ROLE / NEW_ROLE for eight observations.

Abort:

36 / 36.

C3:

only three consecutive NEW_ROLE observations.

Abort:

36 / 36.

The four-observation dwell therefore behaves as a real gate,
not merely a label.

AUDIT D — PARTIAL PROVENANCE

Each condition covered all 36 single-cell migration cases.

DEMAND_A absent:

commits:
0.

DEMAND_B absent:

commits:
0.

peer A unavailable:

commits:
0.

peer B unavailable:

commits:
0.

demand paths disagree:

commits:
0.

peer observers disagree:

commits:
0.

No surviving witness is promoted to multiple provenance slots.

AUDIT E — PARTIAL FINAL COMMIT

Nonempty proper subsets of:

TARGET,
PEER_A,
PEER_B:

6.

Injected partial-commit cases:

216.

Rollback to OLD_ROLE:

216 / 216.

NEW_ROLE authority after partial write:

0.

Final split brain:

0.

The semantic commit certificate is therefore atomic at the authority layer:

a partially written migration is not a partially authoritative migration.

AUDIT F — WITNESS-HOLDER DAMAGE

Each condition covered 36 migrations.

peer A damaged:

commits:
0.

peer B damaged:

commits:
0.

one demand-observer cohort damaged:

commits:
0.

Damaged provenance is treated as unavailable,
not as implicit agreement.

AUDIT G — CANCEL BEFORE FINAL COMMIT

Cases:

36.

Commits:

0.

Metadata changes:

0.

A successfully observed and fully qualified shadow role
can still be cancelled before final authority transfer
without contaminating authoritative role history.

NEGATIVE CONTROLS

Frozen false-role cases:

36.

TARGET_SELF_MIGRATION authorizations:

36 / 36.

TARGET_PLUS_STRUCTURE authorizations:

36 / 36.

SINGLE_PEER_MIGRATION authorizations:

36 / 36.

INDEPENDENT_ROLE_MIGRATION authorizations:

0 / 36.

Thus:

stable target behavior alone is unsafe;

stable target behavior plus clean structure is unsafe;

one demand path plus one peer witness is still insufficient under the frozen adversarial case.

The complete independent quorum is doing real authorization work.

CORRELATED-FORGERY BOUNDARY

H1 — both demand paths forged,
honest peer observers reject:

false commits:
0 / 36.

H2 — both peer observers forged,
honest demand paths reject:

false commits:
0 / 36.

H3 — all four provenance paths forged coherently:

false commits:
36 / 36.

CORRELATED_ROLE_FORGERY_FAILURE:

TRUE.

H4 — exactly one of four quorum paths forged:

false commits:
0.

ONE_OF_FOUR_FORGERY_SUPPRESSED:

TRUE.

TECHNICAL INTERPRETATION

DG-1R-05S establishes a distributed role-migration transaction
that can move phenotype-level authority
without a permanent central controller
under the frozen independent-witness model.

The protocol separates:

PROVISIONAL FUNCTION

the target may demonstrate a new role in shadow mode;

from

AUTHORITATIVE IDENTITY

the old role remains authoritative
until independent demand,
independent peer observation,
and the complete three-record commit certificate agree.

This distinction prevents ordinary partial writes,
transient behavior,
single-path corruption,
and witness loss
from silently redefining cell identity.

The important remaining weakness is no longer ordinary quorum mechanics.

It is provenance itself.

05S labels four evidence paths as distinct,
and the holdouts show that this distinction matters.

But a real developmental organism cannot merely assume
that nominally different witnesses are causally independent.

Several cells may inherit the same corrupted ancestor,
share one poisoned measurement,
or derive their confidence from one common hidden source.

The next architectural task is therefore to make evidence lineage
part of the consensus substrate.

PLAIN-SPEAK INTERPRETATION

The cells can now change jobs safely in this model.

A cell can try a new role without immediately rewriting what the organism believes it is.

The old job stays official while the new one is tested.

Two separate demand sources
and two separate peers
have to agree.

Then the cell and both peer records have to finish the same commit.

If only one or two records update,
the new job does not become half-official.

It rolls back.

If a witness disappears,
the organism waits instead of pretending the missing vote was yes.

If the cell changes its mind before the final commit,
nothing permanent changes.

And one bad witness cannot force a role migration.

The remaining problem is deeper:

how do we know those four witnesses are actually independent?

Four different cells can still be repeating the same bad source.

So the next step is to make the organism understand where evidence came from,
not just how many cells repeated it.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05T —

PROVENANCE-LINEAGE INDEPENDENCE AUDIT.

Question:

Can the healthy-cell consensus identify when nominally separate witnesses
share the same causal evidence ancestry,
collapse correlated witnesses into one effective source,
and abstain when apparent quorum is actually duplicated provenance?

The first 05T stage should remain detection / authorization only.

It should test:

- fully independent witness roots;
- two holders derived from one common root;
- partial ancestry overlap;
- one witness copied through multiple cells;
- lineage-preserving witness rotation;
- loss of an independent root;
- false quorum created by many descendants of one poisoned source;
- forged lineage metadata as an explicit boundary.

No repair or role migration should execute in 05T.

The purpose is to test the constitutional rule:

DIFFERENT CELLS
DO NOT AUTOMATICALLY MEAN
DIFFERENT EVIDENCE.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
