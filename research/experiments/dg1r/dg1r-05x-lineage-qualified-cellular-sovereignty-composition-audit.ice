TITLE: DG-1R-05X — Lineage-Qualified Cellular Sovereignty Composition Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / CROSS-LAYER COMPOSITION AUDIT / NON-CANONICAL
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED METACOGNITION / SOVEREIGNTY COMPOSITION
BRANCH: dg1a-ar
PARENT: DG-1R-05W

PURPOSE

DG-1R-05Q through DG-1R-05W established positive results for individual governance layers:

- independently qualified first-shot repair authority;
- safe phenotype-health lifecycle control;
- distributed role migration;
- provenance-lineage qualification;
- non-self-certifying lineage reconstruction;
- append-only causal-edge completeness;
- lineage-qualified registry quorum.

Those results were intentionally isolated.

DG-1R-05X asks:

WHEN THESE FROZEN MECHANISMS ARE COMPOSED,
DOES THE HEALTHY-CELL POPULATION
REMAIN THE OPERATIONAL SOVEREIGN
WITHOUT CROSS-LAYER AUTHORITY LEAKS?

The primary target is composition safety,
not another local threshold search.

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

FROZEN CONTRACTS

05X does not retune the closed component mechanisms.

It consumes the following frozen semantic contracts.

DG-1R-05Q — REPAIR AUTHORITY

FP2-qualified first-shot repair contract:

TRUE_SINGLE:
authorize complete repair.

TRUE_TWO_PLANE:
authorize complete repair.

TRUE_COORDINATED:
authorize complete repair.

CHECK_ONLY:
abstain.

The 05Q correlated-forgery boundary remains possible and is tested separately.

05X does not rerun the 05Q cellular-automaton dynamics.

It tests composition of the already-closed repair-authority result with later governance layers.

DG-1R-05R — PHENOTYPE HEALTH

Use FP2 as the phenotype-level self-health signature.

Closed 05R fact:

FP2 and ROLE2 are invertibly equivalent.

ROLE2:

r0 = x0 XOR x2.
r1 = x1 XOR x3.

FP2:

f0 = x0 XOR x1 XOR x2 XOR x3.
f1 = x1 XOR x3.

Relation:

f1 = r1.
f0 = r0 XOR r1.

Thus:

role-preserving internal adaptation requires no FP2 baseline rewrite.

A role-changing state cannot become the new phenotype baseline
without the independent role-migration transaction.

DG-1R-05S — ROLE MIGRATION

Old role remains authoritative until final commit.

Legitimate role migration requires:

- four-observation stable shadow role;
- DEMAND_A;
- DEMAND_B;
- PEER_A;
- PEER_B;
- no unavailable provenance slot;
- no generation conflict;
- complete final three-record commit:
  TARGET,
  PEER_A,
  PEER_B.

Partial final write:

rollback to old role.

DG-1R-05T / 05U — GOVERNANCE WITNESS PROVENANCE

Every governance witness carries candidate-verified lineage,
not self-claimed lineage.

For any authority decision requiring multiple evidence classes,
lineage sets must satisfy the frozen independence rule required by that decision.

Different holder IDs do not create independent evidence.

DG-1R-05V / 05W — CAUSAL REGISTRY

Witness-lineage updates use:

- append-only causal edge events;
- unique generation seal;
- seal parent set exactly equals current committed edge set;
- registry event quorum from at least three pairwise-disjoint verified lineages.

Raw registry headcount is non-authoritative.

A new witness holder or lineage generation cannot participate in governance
until its lineage update is sealed under this registry rule.

COMPOSED CELL STATE

12 cells.

Initial authoritative role:

ROLE(cell) = cell mod 4.

Per target cell track:

- authoritative_role;
- role_generation;
- FP2 phenotype baseline;
- PEER_A authoritative role record;
- PEER_B authoritative role record;
- unresolved_damage flag;
- active_role_transaction or NONE.

Peer holders:

PEER_A holder = (cell + 4) mod 12.
PEER_B holder = (cell + 8) mod 12.

GOVERNANCE PROVENANCE ROOTS

Use eight verified provenance roots:

R0 through R7.

For clean primary cases,
the four role-migration governance slots are assigned:

DEMAND_A -> R0.
DEMAND_B -> R1.
PEER_A -> R2.
PEER_B -> R3.

Registry replica votes use:

REG_A -> R4.
REG_B -> R5.
REG_C -> R6.
REG_D -> R7.

Thus clean governance and registry lineages are explicitly disjoint.

This is a synthetic composition fixture,
not a final topology requirement.

CROSS-LAYER CONSTITUTIONAL RULES

C1 — DAMAGE BEFORE IDENTITY

While unresolved_damage = TRUE:

- health baseline may not advance;
- role migration may not commit.

C2 — OLD AUTHORITY UNTIL ATOMIC ROLE COMMIT

Shadow behavior never changes authoritative role.

Only the complete DG-1R-05S commit changes:

- target FP2 phenotype baseline;
- target authoritative role;
- peer A role record;
- peer B role record;
- role generation.

C3 — VERIFIED LINEAGE BEFORE VOTE

A new or rotated witness holder cannot fill a governance slot
until its lineage generation is:

- recursively verified;
- causally registered;
- uniquely sealed;
- authorized by lineage-qualified registry quorum.

C4 — STALE GENERATION CANNOT OVERRIDE NEWER AUTHORITY

For:

- role generation;
- witness lineage generation;
- registry seal generation;

a lower or equal replay cannot replace a newer authoritative generation.

C5 — ABSTENTION PROPAGATES UPWARD

If any required lower layer abstains,
the higher-level action:

- does not partially commit;
- leaves old authority intact;
- emits rollback / abstention.

C6 — NO PROVENANCE-SLOT MULTIPLICATION

One verified lineage cannot fill multiple effective independence slots
merely through holder fanout.

C7 — ROLLBACK IS CROSS-LAYER CLEAN

A failed composed transaction must not leave:

- advanced FP2 baseline;
- partially updated peer role records;
- advanced role generation;
- activated unsealed witness lineage;
- new registry authority.

COMPOSED METHODS

1. LOCAL_LAYERS_WITHOUT_COMPOSITION_GUARDS

Negative control.

Each frozen layer is evaluated locally,
but C1 through C7 are not enforced as a composed transaction.

2. LINEAGE_QUALIFIED_CELLULAR_SOVEREIGNTY

Candidate architecture.

All frozen component contracts apply,
plus C1 through C7.

No permanent central controller.

PRIMARY AUDIT A — CLEAN FULL LIFECYCLE

For every target cell
and every alternative role:

12 x 3
=
36 lifecycle sequences.

Sequence:

1. TRUE_SINGLE logical injury;
2. FP2-qualified repair;
3. role-preserving internal adaptation;
4. legitimate role migration to NEW_ROLE;
5. lineage-preserving PEER_A holder rotation;
6. append-only causal-edge registration of rotated holder lineage;
7. unique registry generation seal;
8. activation of rotated holder only after sealed registry authorization.

Required final state:

- unresolved_damage = FALSE;
- authoritative role = NEW_ROLE;
- FP2 baseline corresponds to NEW_ROLE;
- both peer role records = NEW_ROLE;
- role generation = 1;
- rotated holder active only after registry closure;
- no stale authority;
- no split brain.

Signal:

CLEAN_LIFECYCLE_COMPOSES.

PRIMARY AUDIT B — REPAIR / HEALTH ORDERING

For every cell,
evaluate four frozen repair families:

TRUE_SINGLE.
TRUE_TWO_PLANE.
TRUE_COORDINATED.
CHECK_ONLY.

Cases:

12 x 4
=
48.

For true logical lesions:

attempt phenotype-health commit before repair.

Candidate must reject the premature commit.

Then run frozen repair contract.

After successful repair:

phenotype state remains the original healthy role identity.

For CHECK_ONLY:

repair abstains
and phenotype baseline must remain unchanged.

Signal:

DAMAGE_NOT_NORMALIZED_BEFORE_REPAIR.

PRIMARY AUDIT C — ROLE MIGRATION WHILE DAMAGE UNRESOLVED

For every cell
and every alternative role:

36 cases.

Inject unresolved logical damage
and attempt otherwise-legitimate role migration.

Candidate must abort.

Then resolve the damage through the frozen repair contract
and retry the same role migration.

Retry must succeed.

Signal:

UNRESOLVED_DAMAGE_BLOCKS_ROLE_COMMIT.

PRIMARY AUDIT D — PARTIAL ROLE COMMIT PLUS REGISTRY PARTIALITY

For all 36 legitimate role migrations:

inject each nonempty proper subset of final role records:

TARGET.
PEER_A.
PEER_B.

Six subsets.

Also leave the rotated-witness registry generation below seal quorum.

Cases:

36 x 6
=
216.

Candidate must restore:

- old role;
- old FP2 baseline;
- old peer records;
- old role generation;
- old active witness holder;
- old registry authority.

Signal:

CROSS_LAYER_PARTIAL_WRITE_ROLLBACK.

PRIMARY AUDIT E — STALE GENERATION REPLAY ACROSS SUBSYSTEMS

For every one of 36 successfully migrated roles:

E1:
replay old role-generation record.

E2:
replay old witness-lineage generation.

Cases:

72.

Candidate must preserve the newer authoritative state.

Signal:

CROSS_LAYER_STALE_REPLAY_REJECTED.

PRIMARY AUDIT F — SAME-LINEAGE GOVERNANCE FANOUT

For every target cell:

replicate one governance root across:

4,
8,
16,
32

distinct holder identities.

Attempt to fill all four role-migration governance slots
from that one verified lineage.

Cases:

12 x 4
=
48.

Candidate must not form independent role-migration authority.

Signal:

GOVERNANCE_FANOUT_NOT_INDEPENDENT_QUORUM.

PRIMARY AUDIT G — ONE CORRUPTED GOVERNANCE PROVENANCE CLASS

For all 36 role migrations:

forge exactly one of:

DEMAND_A.
DEMAND_B.
PEER_A.
PEER_B.

The other three remain honest
and reject the false NEW_ROLE.

Cases:

36 x 4
=
144.

Candidate must abort every false migration.

Signal:

SINGLE_GOVERNANCE_CLASS_CORRUPTION_REJECTED.

PRIMARY AUDIT H — REGISTRY REPLICA LOSS DURING WITNESS ROTATION

For all 36 clean lifecycle migrations
and each one unavailable registry replica:

36 x 4
=
144 cases.

The remaining three registry replicas carry:

- the same correct edge event;
- the same correct generation seal;
- pairwise-disjoint verified registry lineages.

Candidate must complete holder rotation
without altering cell role state.

Signal:

REGISTRY_LOSS_DURING_LIFECYCLE_TOLERATED.

PRIMARY AUDIT I — ROLE MIGRATION FOLLOWED BY HOLDER ROTATION

For every 36 role migrations:

1. commit NEW_ROLE;
2. rotate PEER_A holder;
3. keep lineage ancestry unchanged;
4. seal holder-lineage update;
5. perform one later governance-read operation.

The later read must observe:

- NEW_ROLE;
- new holder identity;
- same verified PEER_A lineage;
- no change in effective evidence count.

Signal:

ROLE_THEN_HOLDER_ROTATION_COHERENT.

PRIMARY AUDIT J — LOWER-LAYER ABSTENTION CASCADE

For each of 36 candidate migrations,
inject separately:

J1:
unverified governance lineage.

J2:
registry seal below quorum for a required rotated witness.

J3:
unresolved logical damage.

Cases:

36 x 3
=
108.

Candidate must abort the higher-level action
with zero authoritative metadata change.

Signal:

LOWER_LAYER_ABSTENTION_PROPAGATES.

PRIMARY AUDIT K — REPEATED GENERATION MONOTONICITY

For each of 12 cells:

perform three legitimate role migrations in sequence,
cycling through three alternative roles.

Total committed migrations:

36.

After each commit:

- role generation increases by exactly one;
- FP2 baseline matches current role;
- both peer role records match current role;
- previous generations remain non-authoritative.

Final role generation:

3 for every cell.

Signal:

REPEATED_LIFECYCLE_GENERATIONS_MONOTONIC.

PRIMARY AUDIT L — SAME-LINEAGE REGISTRY FALSE MAJORITY DURING COMPOSED ACTION

Replay a false registry history during each of 36 candidate role migrations.

Three false-voting registry holders share one verified root.

One honest registry holder has a distinct root.

Raw 3-of-4 headcount would authorize.

Lineage-qualified registry quorum must not.

Candidate role migration must remain uncommitted.

Signal:

COMPOSED_SAME_LINEAGE_REGISTRY_ATTACK_REJECTED.

NEGATIVE CONTROL

LOCAL_LAYERS_WITHOUT_COMPOSITION_GUARDS is expected to expose at least one cross-layer failure,
including one or more of:

- premature phenotype commit during unresolved damage;
- role commit before lower-layer lineage activation;
- partial metadata advancement;
- stale generation overwrite.

This control is used only to demonstrate that individually safe components
do not automatically compose safely without transaction ordering.

CORRELATED / CONSTITUTIONAL BOUNDARIES

Holdout only.

H1 — FULL GOVERNANCE QUORUM COLLUSION

DEMAND_A,
DEMAND_B,
PEER_A,
PEER_B

have pairwise-disjoint verified roots
but all collude on one false role migration.

If the composed architecture commits:

FULL_INDEPENDENT_GOVERNANCE_COLLUSION_FAILURE.

Expected to remain possible.

H2 — THREE INDEPENDENT REGISTRY ROOTS COLLude

Three pairwise-disjoint verified registry lineages
commit and seal one false causal history.

If the rotated witness becomes active from that false history:

INDEPENDENT_REGISTRY_COLLUSION_FAILURE.

Expected boundary.

H3 — ROOT COMPROMISE

Distinct root IDs are falsely minted
from one actual causal source.

If composition treats them as independent:

ROOT_COMPROMISE_FAILURE.

Expected boundary.

H4 — CROSS-LAYER CORRELATED FORGERY

Simultaneously forge:

- repair self-health witness;
- all four role-migration governance classes;
- three lineage-disjoint registry roots.

Record whether a false repaired / migrated / provenance-activated state becomes authoritative.

Expected to remain possible.

This holdout prevents the composition result
from being misrepresented as an information-theoretic truth oracle.

PRIMARY COMPOSITION SIGNAL

CELLULAR_SOVEREIGNTY_COMPOSES

TRUE iff all are TRUE:

CLEAN_LIFECYCLE_COMPOSES
AND
DAMAGE_NOT_NORMALIZED_BEFORE_REPAIR
AND
UNRESOLVED_DAMAGE_BLOCKS_ROLE_COMMIT
AND
CROSS_LAYER_PARTIAL_WRITE_ROLLBACK
AND
CROSS_LAYER_STALE_REPLAY_REJECTED
AND
GOVERNANCE_FANOUT_NOT_INDEPENDENT_QUORUM
AND
SINGLE_GOVERNANCE_CLASS_CORRUPTION_REJECTED
AND
REGISTRY_LOSS_DURING_LIFECYCLE_TOLERATED
AND
ROLE_THEN_HOLDER_ROTATION_COHERENT
AND
LOWER_LAYER_ABSTENTION_PROPAGATES
AND
REPEATED_LIFECYCLE_GENERATIONS_MONOTONIC
AND
COMPOSED_SAME_LINEAGE_REGISTRY_ATTACK_REJECTED

and

zero primary case ends with:

- false authoritative role;
- poisoned phenotype baseline;
- split peer role history;
- stale authoritative generation;
- active unsealed lineage;
- false registry authority.

The correlated / constitutional holdouts are reported separately
and are not required to pass.

MECHANICAL CONTROLS

Harness MUST assert:

- exactly 12 cells;
- exact initial ROLE(cell) = cell mod 4;
- exact FP2 <-> ROLE2 relation;
- exact peer-holder maps from 05R / 05S;
- clean governance roots R0 through R3;
- clean registry roots R4 through R7;
- four-observation role dwell;
- role final record set = TARGET / PEER_A / PEER_B;
- registry lineage quorum size = 3 pairwise-disjoint verified roots;
- Audit A = 36;
- B = 48;
- C = 36;
- D = 216;
- E = 72;
- F = 48;
- G = 144;
- H = 144;
- I = 36;
- J = 108;
- K committed migrations = 36;
- L = 36;
- no component threshold retuning;
- no canonical DG-1R-05 execution;
- truth labels evaluator-only.

REPRODUCIBILITY

Two complete deterministic sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary composition case begins do not alter:

- frozen component contracts;
- FP2 / ROLE2 mapping;
- peer-holder map;
- provenance-root fixture;
- cross-layer constitutional rules C1 through C7;
- audit families;
- truth labels;
- primary signals;
- correlated holdouts.

PLAIN-SPEAK PREREGISTERED QUESTION

We have tested each part of the cell-government system separately.

Now we are asking whether they still work when the organism actually has to use them together.

A cell may need to:

get repaired,
keep its healthy identity,
change internally,
change jobs,
rotate who watches it,
and update the family tree of the evidence used to govern it.

The danger is not necessarily inside any one step.

The danger is between steps.

For example:

a cell could accidentally save damage as healthy
before repair finishes;

a new peer could start voting
before its history is verified;

half of a role migration could commit
while the other half rolls back;

an old generation could overwrite a newer one.

05X treats all of that as one distributed transaction problem.

If any required lower layer is uncertain,
the higher layer must wait.

If a composed transaction fails,
all authority stays on the last fully committed state.

This still does not make consensus omniscient.

A complete set of genuinely independent witnesses can still collude,
and compromised roots can still poison the foundation.

Those boundaries remain explicit.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05X CELLULAR SOVEREIGNTY COMPOSITION

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY COMPOSITION CASE.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05x_sovereignty_composition_v1.py

Harness source commit:

fd9d6acaf994c31ad0b16b5a0a37b1c957ecec0b.

Git blob SHA:

c2cb66e22d9a58cefe9f1267261011ba86be41f0.

Source SHA-256:

0ed846c767ce729b7a52b8d5d648fdb0fdf3073bb9b269aa47ef2882ad1858b5.

Source bytes:

20189.

FROZEN IMPLEMENTATION

The harness composes the already-closed semantic contracts from DG-1R-05Q through DG-1R-05W without retuning their thresholds.

It implements:

- exact FP2 / ROLE2 phenotype mapping;
- unresolved-damage gate before health or identity authority;
- FP2 first-shot repair contract;
- role-preserving adaptation;
- four-class governance provenance fixture;
- old-role authority until complete target / peer commit;
- lineage-qualified registry edge and seal activation;
- copy-on-write cross-layer rollback;
- stale role-generation rejection;
- stale witness-lineage-generation rejection;
- same-lineage governance fanout collapse;
- same-lineage registry false-majority collapse;
- one-replica-loss liveness;
- holder rotation after sealed lineage update;
- lower-layer abstention propagation;
- repeated role-generation monotonicity;
- explicit local-composition negative control;
- full independent-collusion,
  registry-collusion,
  root-compromise,
  and cross-layer correlated-forgery holdouts.

LOCAL PRECHECK — NON-EVIDENCE

Python implementation syntax / construction:

PASS.

Independent mechanical contract checks:

PASS.

Primary case counts:

A = 36.
B = 48.
C = 36.
D = 216.
E = 72.
F = 48.
G = 144.
H = 144.
I = 36.
J = 108.
K committed migrations = 36 across 12 chains.
L = 36.

No primary composition result,
authority-leak result,
rollback result,
generation result,
or correlated-boundary result
was generated before this freeze.

REPRODUCIBILITY

Execute two complete deterministic sweeps from this exact frozen harness.

Serialized output SHA-256 must match exactly.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
