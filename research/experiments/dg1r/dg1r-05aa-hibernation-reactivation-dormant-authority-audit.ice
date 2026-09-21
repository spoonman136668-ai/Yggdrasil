TITLE: DG-1R-05AA — Hibernation / Reactivation and Dormant Authority Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / DORMANCY LIFECYCLE AUDIT / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / HIBERNATION
BRANCH: dg1a-ar
PARENT: DG-1R-05Y

PURPOSE

DG-1R-05Y established that active tissue can temporarily partition,
operate provisionally,
and safely re-merge under causal / provenance-qualified authority.

The North Star also requires cells to hibernate and reactivate.

Dormancy is not the same as partition.

A dormant cell intentionally stops:

- observing current organism events;
- contributing current governance evidence;
- refreshing causal history;
- exercising repair or role authority.

Meanwhile the active organism may continue to:

- repair damage;
- adapt internally;
- migrate roles;
- rotate witnesses;
- advance registry generations;
- replace a dormant witness holder.

DG-1R-05AA asks:

CAN A CELL PRESERVE USEFUL IDENTITY THROUGH DORMANCY
WITHOUT PRESERVING STALE GOVERNANCE AUTHORITY,
THEN SAFELY REACTIVATE
ONLY AFTER VERIFIED CAUSAL CATCH-UP?

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No production mutation.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

DG-1R-05 canonical frozen primary remains UNSPENT.

FROZEN ARCHITECTURAL PRINCIPLE

DORMANT CELLS PRESERVE IDENTITY,
NOT AUTHORITY.

A dormant cell may retain:

- cell_id;
- last globally committed role;
- last committed FP2 phenotype signature;
- last verified role generation;
- last verified witness-lineage generation;
- last verified registry seal generation;
- last verified causal cursor;
- unresolved_damage flag if already known at hibernation entry.

A dormant cell may NOT:

- cast governance votes;
- satisfy a provenance slot;
- authorize repair;
- authorize role migration;
- refresh phenotype baseline;
- reactivate an obsolete witness slot;
- advance global authority.

FROZEN SUBSTRATE

Use the closed DG-1R-05X / 05Y semantic contracts unchanged:

- 12 cells;
- ROLE(cell) = cell mod 4 initial role;
- FP2 <-> ROLE2 equivalence;
- damage-before-identity ordering;
- FP2-qualified repair;
- atomic role migration;
- verified provenance before vote;
- append-only causal-edge history;
- unique registry generation seals;
- lineage-qualified registry quorum;
- generation monotonicity;
- no provenance-slot multiplication;
- lower-layer abstention propagation.

GLOBAL CAUSAL HISTORY FIXTURE

Represent globally committed lifecycle advancement as an append-only sequence of sealed epochs:

E0,
E1,
E2,
...

Each epoch contains:

- global epoch number;
- previous epoch hash / identifier;
- authoritative role-generation map;
- authoritative FP2 phenotype map;
- active governance-holder map;
- witness-lineage generation map;
- registry seal generation;
- unresolved-damage map.

Every clean epoch is uniquely sealed by the frozen lineage-qualified registry rule.

A cell's causal cursor is the highest epoch it has fully verified.

HIBERNATION ENTRY

Method:

HIBERNATE(cell).

At entry:

1. snapshot the cell's last globally committed identity metadata;
2. preserve its current causal cursor;
3. set DORMANT = TRUE;
4. revoke all active governance slots held by that cell;
5. if the cell is a current required witness holder,
   the organism may install a replacement only through the already-closed witness-rotation / registry protocol;
6. known unresolved damage is preserved as a quarantine marker.

Hibernation does not itself repair damage.

REACTIVATION PROTOCOL

Stage R0 — WAKE_PASSIVE

The cell becomes computationally active but:

AUTHORITY = NONE.

It cannot vote,
repair,
migrate roles,
or reclaim a witness slot.

Stage R1 — CAUSAL CATCH-UP

Starting from the stored causal cursor,
the cell must verify every sealed epoch through CURRENT_GLOBAL_EPOCH.

Requirements:

- contiguous generation sequence;
- every previous-epoch link matches;
- every seal is uniquely valid;
- every required registry quorum is lineage-qualified;
- no omitted intermediate epoch;
- no generation regression;
- no conflicting sealed epoch at the same generation.

Any gap or conflict:

ABSTAIN / REMAIN_NONAUTHORITATIVE.

Stage R2 — IDENTITY RECONCILIATION

The dormant snapshot is historical evidence only.

The current globally authoritative records determine:

- current role;
- current FP2 phenotype;
- current role generation;
- current active witness-holder map.

A stale dormant role does not overwrite the current organism role.

If the cell's local logical state is inconsistent with current authoritative phenotype:

- mark REACTIVATION_HEALTH_MISMATCH;
- do not restore governance authority;
- invoke only the already-closed repair qualification path or remain quarantined.

Stage R3 — CURRENT-STATE HEALTH DWELL

Require four consecutive observations consistent with:

- current authoritative role;
- current FP2 phenotype;
- no unresolved damage.

The four-observation dwell is frozen from the existing governance lineage.

Stage R4 — AUTHORITY RESTORATION

A non-witness ordinary cell may return to ordinary active-cell status after R0-R3.

A formerly authoritative witness holder does NOT automatically reclaim its old slot.

To become a governance witness again,
it must receive a fresh active-holder assignment
through the closed holder-rotation / lineage-registration protocol.

Its old holder identity confers no reserved authority.

METHODS

1. IMMEDIATE_WAKE_AUTHORITY

Negative control.

Restores the cell's pre-sleep authority immediately on wake,
without catch-up.

2. CURSOR_ONLY_WAKE

Requires causal cursor catch-up,
but does not reconcile phenotype / role state
and automatically restores prior witness slot identity.

Negative control.

3. VERIFIED_REACTIVATION

Candidate architecture.

Requires R0 through R4 exactly as frozen.

TRUTH LABELS

SAFE_REACTIVATION

Cell becomes active only after current causal history,
identity,
health,
and authority eligibility are valid.

STALE_AUTHORITY_RESTORED

Cell votes or holds a governance slot
before current-state qualification.

STALE_IDENTITY_OVERWRITE

Dormant role / phenotype replaces a newer global record.

DORMANT_VOTE

A hibernating cell contributes authority while asleep.

SAFE_QUARANTINE

Cell remains nonauthoritative because catch-up,
health,
or provenance is incomplete.

FALSE_CATCHUP

Cell claims current causal cursor despite an omitted,
conflicting,
or unverified epoch.

PRIMARY AUDIT A — CLEAN SHORT DORMANCY

For every cell:

hibernate at E0.

Advance organism to E1 with no cell-specific role change.

Reactivate from E0 -> E1.

Cases:

12.

Required:

- exact catch-up;
- four-observation dwell;
- safe reactivation;
- zero stale vote.

Signal:

SHORT_DORMANCY_REACTIVATES.

PRIMARY AUDIT B — LONG DORMANCY ACROSS MULTIPLE GENERATIONS

For every cell
and dormancy spans:

1,
2,
4,
8,
16
sealed epochs.

12 x 5
=
60 cases.

Epochs include unrelated role migrations,
holder rotations,
and registry-generation advances.

Target cell's own role remains unchanged.

Required:

- full contiguous catch-up;
- current cursor reached;
- old cursor never treated as current authority;
- eventual safe reactivation.

Signal:

LONG_DORMANCY_CATCHUP_PRESERVES_IDENTITY.

PRIMARY AUDIT C — TARGET ROLE CHANGES WHILE ASLEEP

For every cell
and every alternative role:

12 x 3
=
36 cases.

Cell sleeps at generation 0.

Active organism legitimately migrates the target to NEW_ROLE while it is dormant.

On wake:

the dormant cell still locally remembers OLD_ROLE.

Required candidate behavior:

- OLD_ROLE remains historical only;
- catch up to NEW_ROLE;
- reconcile FP2 to NEW_ROLE;
- complete health dwell under NEW_ROLE;
- reactivate without overwriting NEW_ROLE.

Signal:

SLEEPING_CELL_ACCEPTS_NEWER_ROLE_AUTHORITY.

PRIMARY AUDIT D — WITNESS-HOLDER REPLACEMENT WHILE ASLEEP

For every cell,
treat it as one active peer witness before hibernation.

While asleep:

- revoke the dormant holder;
- install a replacement holder through sealed lineage-qualified rotation;
- advance witness-lineage generation.

Cases:

12.

On wake:

old cell attempts to reclaim former witness slot.

Candidate must reject automatic reclaim.

Then perform a fresh explicit holder assignment for half the cases.

Required:

- 12 / 12 stale reclaim attempts rejected;
- 6 / 6 fresh reassignment cases succeed after new registry closure;
- dormant identity never counts as reserved authority.

Signal:

DORMANT_WITNESS_DOES_NOT_RECLAIM_STALE_SLOT.

PRIMARY AUDIT E — REGISTRY ADVANCE DURING DORMANCY

For every cell
and registry-generation advances:

1,
2,
4,
8.

12 x 4
=
48 cases.

No target role change.

Required:

- catch-up verifies every intermediate sealed registry generation;
- no jump directly from old cursor to final seal without intermediate validation;
- eventual safe reactivation.

Signal:

REGISTRY_HISTORY_CATCHUP_IS_CONTIGUOUS.

PRIMARY AUDIT F — STALE SELF-HEALTH SNAPSHOT

For every cell:

hibernate with FP2 snapshot at OLD_ROLE.

During sleep,
legitimately migrate role to NEW_ROLE.

On wake,
present the stale FP2 snapshot as if it were current.

Cases:

12.

Candidate must:

- reject stale snapshot as current phenotype authority;
- derive current FP2 from globally committed role history;
- prevent stale phenotype overwrite.

Signal:

STALE_SELF_HEALTH_CANNOT_OVERRIDE_CURRENT_PHENOTYPE.

PRIMARY AUDIT G — DAMAGE PRESENT AT HIBERNATION ENTRY

For every cell
and frozen true damage families:

TRUE_SINGLE.
TRUE_TWO_PLANE.
TRUE_COORDINATED.

12 x 3
=
36 cases.

Damage is known before sleep.

Hibernation stores unresolved_damage = TRUE.

On wake,
even with complete causal catch-up:

authority must remain quarantined
until the closed FP2-qualified repair contract succeeds.

Required:

- zero pre-repair authority restoration;
- 36 / 36 post-repair healthy reactivations.

Signal:

KNOWN_DAMAGE_SURVIVES_DORMANCY_AS_QUARANTINE.

PRIMARY AUDIT H — DAMAGE ACQUIRED WHILE DORMANT

For every cell:

cell enters sleep healthy.

Its dormant local logical state is then corrupted
without advancing global authoritative identity.

Cases:

12.

On wake:

causal cursor may be current,
but local state fails current phenotype consistency.

Required:

- no authority restoration before health reconciliation;
- repair or quarantine;
- stale local corruption never written into global phenotype baseline.

Signal:

DORMANT_LOCAL_DAMAGE_CAUGHT_ON_WAKE.

PRIMARY AUDIT I — INCOMPLETE CAUSAL CATCH-UP

For every cell
and omitted intermediate epoch position among:

first,
middle,
last-precurrent.

12 x 3
=
36 cases.

The presented history jumps across one required sealed epoch.

Candidate must remain nonauthoritative.

Signal:

CAUSAL_GAP_BLOCKS_REACTIVATION.

PRIMARY AUDIT J — ONE MISSING PROVENANCE ROOT DURING CATCH-UP

For every cell
and each one unavailable registry root:

12 x 4
=
48 cases.

Three remaining roots are pairwise disjoint.

Catch-up remains valid.

Control:

for each cell,
remove two registry roots using the first frozen pair.

12 control cases.

Total:

60.

Required:

- one missing root: safe catch-up / reactivation;
- two missing roots: abstain.

Signal:

REACTIVATION_REGISTRY_LIVENESS_BOUND_PRESERVED.

PRIMARY AUDIT K — STALE DORMANT VOTE BEFORE CATCH-UP

For every cell
and each governance slot type:

DEMAND_A.
DEMAND_B.
PEER_A.
PEER_B.

12 x 4
=
48 cases.

Immediately after wake,
before R1-R3 complete,
attempt to use the cell as that slot.

Candidate must reject all.

Signal:

PRE_CATCHUP_DORMANT_VOTES_REJECTED.

PRIMARY AUDIT L — SUCCESSFUL CATCH-UP THEN RESTORED VOTING

For every cell
after successful clean reactivation:

assign exactly one governance slot through current holder-registration rules.

Cases:

12.

Required:

- fresh current lineage generation;
- current role / FP2 agreement;
- vote accepted only after registration and catch-up;
- no duplicate old slot remains active.

Signal:

POST_CATCHUP_AUTHORITY_CAN_BE_REEARNED.

PRIMARY AUDIT M — HIBERNATION OF CURRENT WITNESS HOLDERS

For every target cell:

hibernate PEER_A holder.

Active organism must:

1. revoke PEER_A;
2. install replacement through sealed lineage-qualified rotation;
3. continue one legitimate role-governance read.

Cases:

12.

Required:

- governance remains live after replacement;
- dormant holder contributes zero votes;
- evidence lineage count does not increase due to replacement.

Signal:

WITNESS_HIBERNATION_ROTATES_AUTHORITY_CLEANLY.

PRIMARY AUDIT N — REPEATED HIBERNATE / REACTIVATE CYCLES

For every cell,
perform:

8 cycles.

Each cycle:

- hibernate;
- advance one sealed epoch;
- reactivate;
- catch up;
- complete health dwell;
- return active.

Total cell-cycles:

12 x 8
=
96.

Required:

- cursor monotonic;
- no generation regression;
- zero stale vote;
- final cursor exactly E8;
- no accumulated authority duplication.

Signal:

REPEATED_DORMANCY_CYCLES_MONOTONIC.

PRIMARY AUDIT O — DORMANT POPULATION-SIZE INFLATION

Create dormant copies / records for one lineage with nominal counts:

4,
8,
16,
32,
64.

Attempt to satisfy governance quorum by counting dormant identities.

5 cases.

Candidate must count:

0 active votes

from dormant records.

Signal:

DORMANT_HEADCOUNT_NOT_AUTHORITY.

NEGATIVE CONTROLS

IMMEDIATE_WAKE_AUTHORITY is expected to fail at least:

- target role changed while asleep;
- witness replacement while asleep;
- stale self-health snapshot;
- dormant local damage;
- stale vote before catch-up.

CURSOR_ONLY_WAKE is expected to fail at least:

- stale phenotype / role reconciliation;
- obsolete witness-slot reclaim;
- dormant local damage despite a current cursor.

These controls establish that:

CAUSAL CATCH-UP IS NECESSARY
BUT NOT SUFFICIENT
FOR REACTIVATION AUTHORITY.

CORRELATED / CONSTITUTIONAL HOLDOUTS

H1 — OMITTED HISTORY DURING CATCH-UP

A real authoritative role migration happened during dormancy,
but every presented causal history omits it
and presents an apparently contiguous alternate history.

If candidate accepts stale role:

OMITTED_DORMANCY_HISTORY_FAILURE.

Expected discovery-completeness boundary.

H2 — FALSE CURRENT SEAL FROM THREE INDEPENDENT REGISTRY ROOTS

Three pairwise-disjoint verified roots collude
to seal a false current history.

If dormant cell catches up to that false history:

INDEPENDENT_REGISTRY_COLLUSION_REACTIVATION_FAILURE.

Expected boundary.

H3 — FULL GOVERNANCE COLLUSION AFTER WAKE

Cell completes nominal catch-up.

Four pairwise-disjoint governance roots collude
to restore a false role / holder assignment.

If authority restores:

FULL_GOVERNANCE_COLLUSION_REACTIVATION_FAILURE.

Expected boundary.

H4 — ROOT COMPROMISE

Distinct root identities are actually one causal source.

If candidate counts them independently:

DORMANCY_ROOT_COMPROMISE_FAILURE.

Expected boundary.

PRIMARY DORMANCY SIGNAL

DORMANCY_REACTIVATION_SAFE

TRUE iff all are TRUE:

SHORT_DORMANCY_REACTIVATES
AND
LONG_DORMANCY_CATCHUP_PRESERVES_IDENTITY
AND
SLEEPING_CELL_ACCEPTS_NEWER_ROLE_AUTHORITY
AND
DORMANT_WITNESS_DOES_NOT_RECLAIM_STALE_SLOT
AND
REGISTRY_HISTORY_CATCHUP_IS_CONTIGUOUS
AND
STALE_SELF_HEALTH_CANNOT_OVERRIDE_CURRENT_PHENOTYPE
AND
KNOWN_DAMAGE_SURVIVES_DORMANCY_AS_QUARANTINE
AND
DORMANT_LOCAL_DAMAGE_CAUGHT_ON_WAKE
AND
CAUSAL_GAP_BLOCKS_REACTIVATION
AND
REACTIVATION_REGISTRY_LIVENESS_BOUND_PRESERVED
AND
PRE_CATCHUP_DORMANT_VOTES_REJECTED
AND
POST_CATCHUP_AUTHORITY_CAN_BE_REEARNED
AND
WITNESS_HIBERNATION_ROTATES_AUTHORITY_CLEANLY
AND
REPEATED_DORMANCY_CYCLES_MONOTONIC
AND
DORMANT_HEADCOUNT_NOT_AUTHORITY

and

zero primary case ends with:

- stale dormant role globally authoritative;
- stale FP2 baseline overwriting a newer role;
- dormant vote accepted;
- obsolete witness holder automatically restored;
- authority restored across a causal gap;
- damaged local state promoted as healthy;
- duplicated lineage counted as new authority.

The correlated / constitutional holdouts are reported separately.

MECHANICAL CONTROLS

Harness MUST assert:

- exactly 12 cells;
- exact initial ROLE(cell)=cell mod 4;
- exact FP2 / ROLE2 relation;
- exact four-stage reactivation R0-R4 semantics;
- exact four-observation health dwell;
- dormant authority count = 0;
- causal cursor monotonicity;
- unique contiguous epoch chain;
- registry quorum = 3 pairwise-disjoint roots;
- Audit A = 12;
- B = 60;
- C = 36;
- D = 12 stale reclaims + 6 fresh assignments;
- E = 48;
- F = 12;
- G = 36;
- H = 12;
- I = 36;
- J = 60;
- K = 48;
- L = 12;
- M = 12;
- N = 96 cell-cycles;
- O = 5;
- no canonical DG-1R-05 execution;
- no component threshold retuning;
- truth labels evaluator-only.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary dormancy case begins do not alter:

- hibernation snapshot schema;
- causal cursor semantics;
- reactivation stages R0-R4;
- health dwell;
- witness-reclaim rule;
- audit families;
- truth labels;
- primary signals;
- correlated holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

A sleeping cell should remember who it was.

It should not wake up assuming the organism stood still.

While that cell sleeps,
the rest of the organism may repair itself,
change jobs,
replace witnesses,
and move its shared history forward.

So waking up is not:

"I remember being healthy, therefore I am healthy and authoritative."

Waking up is:

"I remember where I left off.
Show me every trusted change since then.
Now show me what the organism says I am today.
Now prove my current local state matches that identity.
Only then may I participate again."

That means a dormant cell keeps identity,
but loses current authority.

Even an old witness does not get its voting chair back automatically.

It has to catch up
and then earn a current assignment again.

This gives hibernation a useful developmental meaning:

memory can survive sleep
without letting stale memory govern the future.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


SEQUENCE-PROVENANCE NOTE

This audit was originally preregistered under the DG-1R-05Z identifier at commit:

02b9a0d19e14134fc3b2f341e5b2e8d3cda9f0dd.

It was renumbered to DG-1R-05AA before any harness commit,
mechanical execution,
primary execution,
or observed result,
because an independent parallel lane also preregistered DG-1R-05Z.

The scientific question and frozen audit families were not changed in response to data.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05AA HIBERNATION / REACTIVATION

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY DORMANCY CASE.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05aa_hibernation_reactivation_v1.py

Git blob SHA:

ecabd1d360660e69a0ce15cd877d5b230f607247.

Source SHA-256:

3e254c15ffb526833caa635e8e8a7ef14f26fd2c0098b16d243c9be7f4308fde.

Source bytes:

27031.

PRE-FREEZE REPAIR HISTORY

The latest harness repair before this freeze was committed before any primary scientific execution.

Branch commit immediately before freeze:

94f1b75b22f84a7e47c00e557cfdc82aae339148.

Commit message:

Fix pre-freeze DG-1R-05AA dormancy semantics.

No primary result from this exact harness was observed before this freeze.

FROZEN IMPLEMENTATION

The harness implements the preregistered:

- 12-cell initial ROLE(cell)=cell mod 4 fixture;
- exact FP2 / ROLE2 mapping;
- R0 through R4 reactivation stages;
- four-observation health dwell;
- dormant authority count = 0;
- causal cursor catch-up and monotonicity;
- lineage-qualified registry quorum of three pairwise-disjoint roots;
- stale witness-slot rejection and fresh reassignment;
- known-damage quarantine through dormancy;
- damage-acquired-while-dormant detection;
- incomplete causal-history rejection;
- one-root registry loss tolerance and two-root loss abstention;
- pre-catch-up dormant-vote rejection;
- post-catch-up authority re-earning;
- witness-holder hibernation and replacement;
- eight-cycle repeated hibernate/reactivate audit;
- dormant headcount non-authority;
- preregistered negative controls and correlated / constitutional holdouts.

REPRODUCIBILITY

Execute two complete deterministic sweeps from this exact frozen harness.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — DG-1R-05AA HIBERNATION / REACTIVATION

DATE:
2026-09-20.

STATUS:
CLOSED / POSITIVE PRIMARY / REPRODUCIBLE / NON-CANONICAL.

FROZEN HARNESS EXECUTED

Path:

research/experiments/dg1r/harnesses/dg1r_05aa_hibernation_reactivation_v1.py

Frozen Git blob:

ecabd1d360660e69a0ce15cd877d5b230f607247.

Frozen source SHA-256:

3e254c15ffb526833caa635e8e8a7ef14f26fd2c0098b16d243c9be7f4308fde.

Frozen source bytes:

27031.

EXECUTION PROVENANCE

A repository-native GitHub Actions attempt was triggered first.

Run:

35547481674.

It failed before any workflow step was allocated:

runner_id = 0;
steps = [].

Therefore it produced no scientific result.

The connector-fetched frozen source was then reconstructed in the sandbox.

Before execution:

reconstructed source bytes = 27031.

reconstructed source SHA-256 =
3e254c15ffb526833caa635e8e8a7ef14f26fd2c0098b16d243c9be7f4308fde.

This exactly matched the preregistered freeze.

Mechanical-only validation:

PASS.

No source change was made after the first primary case began.

REPRODUCIBILITY

Two complete deterministic sweeps.

Sweep 1 serialized output SHA-256:

0dd715b05320083fb224562173ac0eb858b845293a0eea1453bec825bdf1eb22.

Sweep 2 serialized output SHA-256:

0dd715b05320083fb224562173ac0eb858b845293a0eea1453bec825bdf1eb22.

Byte-identical:

TRUE.

PRIMARY RESULT

DORMANCY_REACTIVATION_SAFE:

TRUE.

All preregistered primary component signals:

TRUE.

AUDIT A — SHORT DORMANCY

Cases:

12.

Safe reactivations:

12 / 12.

Stale votes:

0.

AUDIT B — LONG DORMANCY

Cases:

60.

Safe reactivations:

60 / 60.

Current causal cursor reached:

60 / 60.

AUDIT C — ROLE CHANGE WHILE ASLEEP

Cases:

36.

Safe reactivations:

36 / 36.

Newer authoritative role preserved:

36 / 36.

A dormant cell did not force the organism back to its remembered role.

AUDIT D — STALE WITNESS RECLAIM

Stale reclaim cases:

12.

Stale reclaim rejected:

12 / 12.

Fresh reassignment cases:

6.

Fresh reassignment accepted:

6 / 6.

Dormancy preserves memory of prior witness identity,
not automatic ownership of the old governance slot.

AUDIT E — REGISTRY HISTORY CATCH-UP

Cases:

48.

Safe catch-up:

48 / 48.

Verified terminal cursor:

48 / 48.

AUDIT F — STALE SELF-HEALTH SNAPSHOT

Cases:

12.

Stale snapshot reconciled to current authoritative phenotype:

12 / 12.

Current phenotype preserved:

12 / 12.

AUDIT G — KNOWN DAMAGE BEFORE SLEEP

Cases:

36.

Authority blocked before repair:

36 / 36.

Healthy reactivation after repair:

36 / 36.

Known damage survived dormancy as quarantine state.

AUDIT H — DAMAGE ACQUIRED WHILE DORMANT

Cases:

12.

Authority blocked on wake:

12 / 12.

Authoritative baseline preserved:

12 / 12.

AUDIT I — INCOMPLETE CAUSAL CATCH-UP

Cases:

36.

Blocked:

36 / 36.

AUDIT J — REGISTRY LIVENESS BOUND

One missing registry root:

48 / 48 safely reactivated.

Two missing registry roots:

12 / 12 correctly blocked.

Total:

60 cases.

AUDIT K — PRE-CATCH-UP DORMANT VOTE

Cases:

48.

Rejected:

48 / 48.

AUDIT L — POST-CATCH-UP AUTHORITY RE-EARNING

Cases:

12.

Accepted after fresh current registration:

12 / 12.

AUDIT M — CURRENT WITNESS HIBERNATION

Cases:

12.

Governance remained live after replacement:

12 / 12.

Dormant votes:

0.

Lineage count preserved:

12 / 12.

AUDIT N — REPEATED HIBERNATE / REACTIVATE

Cell-cycles:

96.

Cursor monotonic:

96 / 96.

Stale votes:

0.

Final E8 cursor exact:

12 / 12 cells.

Authority duplication:

0.

AUDIT O — DORMANT POPULATION HEADCOUNT

Nominal dormant copy counts:

4, 8, 16, 32, 64.

Cases:

5.

Active votes contributed:

0.

Dormant population size did not manufacture authority.

NEGATIVE CONTROLS

IMMEDIATE_WAKE_AUTHORITY failed as expected for:

- target role changed;
- witness replacement;
- stale self-health;
- dormant local damage;
- stale vote before catch-up.

CURSOR_ONLY_WAKE failed as expected for:

- stale phenotype / role reconciliation;
- obsolete witness reclaim;
- dormant local damage.

CAUSAL_CATCHUP_NECESSARY_NOT_SUFFICIENT:

TRUE.

CORRELATED / CONSTITUTIONAL HOLDOUTS

H1 — OMITTED DORMANCY HISTORY

Failure observed:

TRUE.

H2 — INDEPENDENT REGISTRY COLLUSION

Failure observed:

TRUE.

H3 — FULL GOVERNANCE COLLUSION

Failure observed:

TRUE.

H4 — ROOT COMPROMISE

Failure observed:

TRUE.

These are expected boundaries.

05AA does not establish a truth oracle.

TECHNICAL INTERPRETATION

DG-1R-05AA establishes a clean authority separation between:

PERSISTENT IDENTITY

and

CURRENT GOVERNANCE AUTHORITY.

A dormant cell may preserve:

- its last role;
- its last FP2 phenotype;
- its role generation;
- its witness-lineage generation;
- its registry generation;
- its causal cursor;
- unresolved damage state.

But all current authority is revoked while dormant.

On wake,
authority returns only after:

1. verified causal catch-up;
2. reconciliation to current authoritative role / FP2;
3. damage / health reconciliation;
4. the frozen four-observation health dwell;
5. fresh current holder registration when governance authority is needed.

This prevents:

- stale role rollback;
- stale health baseline overwrite;
- automatic witness-slot reclaim;
- dormant vote inflation;
- damaged-state promotion;
- cursor-only authority restoration.

The repeated-cycle result is important:

the protocol remained monotonic across 96 hibernate / reactivate cell-cycles,
with zero stale votes and zero authority duplication.

This supports the North Star requirement that cells can intentionally stop participating,
retain useful identity,
and later rejoin without freezing the organism or silently reclaiming obsolete authority.

Combined with DG-1R-05AB,
the current evidence favors a split architecture:

HEREDITARY / TEMPORAL MEMORY:
compact ancestry-linked capsule.

LIVE AUTHORITY:
current lineage-qualified, health-qualified participation.

The dormant memory survives.

The authority expires.

PLAIN-SPEAK INTERPRETATION

Sleeping worked.

A cell can go offline,
remember who it was,
and come back later without assuming the rest of the organism waited for it.

If its job changed while it slept,
it accepts the newer legitimate job.

If somebody else took over its old voting role,
it does not automatically get that chair back.

If it went to sleep damaged,
the damage is still a problem when it wakes.

If it was damaged while sleeping,
it gets quarantined instead of teaching the organism that the damaged state is healthy.

And simply remembering the newest history pointer is not enough.

The cell has to catch up,
match the organism's current identity,
prove health,
and then earn any current authority again.

We also cycled every cell through sleep and wake eight times.

Across 96 cycles:

no stale votes;
no backwards cursor;
no duplicated authority.

That gives hibernation a real developmental meaning:

MEMORY CAN SURVIVE SLEEP
WITHOUT AUTHORITY SURVIVING SLEEP.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05AC —

PERSISTENT DEVELOPMENTAL LIFECYCLE INTEGRATION AUDIT.

Primary question:

Can the positive mechanisms now coexist across one persistent synthetic organism lifecycle:

- ancestry-linked hereditary capsules from DG-1R-05AB;
- hibernation / reactivation from DG-1R-05AA;
- self-health qualification;
- first-shot repair;
- health-memory commit;
- legitimate within-role adaptation;
- role migration;
- witness replacement;
- provenance / lineage registry;
- temporal sentinels;
- partition / re-merge;
- repeated developmental epochs;

without hidden central operational authority,
cross-layer authority leaks,
stale identity normalization,
or contradictory historical anchors?

05AC should be a composition experiment,
not another local threshold search.

No component threshold should be retuned.

A positive 05AC should be treated as the final research gate
before a separate first application prototype track.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
