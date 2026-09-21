TITLE: YGGDRASIL A17-FIXA — Incremental Patch Authorization / Provenance / Capacity Gate Repair
DATE: 2026-09-21
STATUS: PREREGISTERED PRE-PRIMARY FIXA / NO A17 PRIMARY CONSUMED / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8 / APPLICATION-A
PARENT EXPERIMENT: A17 — Bounded Incremental Developmental Patch Tracking
BRANCH: dg1a-ar

PURPOSE

A17 freeze F17 exists at:

3ec24f8242285688a537f5e7dd6e9a231a645597.

F17 was frozen before derivation of any primary A17 patch path,
primary observation set,
primary attestation set,
primary learner order,
primary held-out evaluation,
or primary replacement plan.

A post-freeze / pre-primary source audit found that the frozen A17 harness
implements the developmental patch path and service evaluator,
but does not operationally enforce every preregistered authorization
and dedicated-probe condition.

No A17 primary manifest has been accepted.
No A17 primary result exists.
No A17 primary observation has been consumed.

F17 is preserved exactly.
It is not to be rewritten.
It is not primary-qualified.

This FIXA repairs only the missing authorization,
provenance-binding,
capacity,
and operational-probe enforcement
before any A17 scientific primary execution.

PRESERVED F17 FACTS

Implementation commit:

82698cbfd07e52e7805caf1e2c60cfd541f4fe3b.

Freeze F17:

3ec24f8242285688a537f5e7dd6e9a231a645597.

F17 source SHA-256:

a1ef99dc5948328d5b8a85d87b7e62a718b4238474322c16aeec6a730244d5c5.

F17 compressed payload SHA-256:

d5eb99b8823427ac9d67cd4b1308a370f20f4431df557b47fae25d931e8da907.

F17 source bytes:

17263.

F17 compressed payload bytes:

6165.

The F17 mechanical fake-freeze result is preserved as implementation evidence only.

It is not scientific evidence.

AUDIT FINDINGS

A1 — COMMIT-WINDOW ENFORCEMENT DEFECT

The frozen authorize(...) function does not receive
or enforce:

16 provenance-qualified unique observations.

Primary run_scenario(...) happens to call authorization after 16 observations,
but the authorization boundary itself can accept a valid bounded target earlier
if called with one.

This violates the preregistered rule that patch commit itself requires
all 16 qualified observations.

P1/P2 must therefore exercise the real authorization gate,
not rely only on caller timing.

A2 — CONTEXT-BOUNDARY ENFORCEMENT DEFECT

The frozen authorization function has no context-boundary eligibility input.

P5 is represented as a hard-coded passing boolean
rather than an executed rejection.

The repaired gate must reject otherwise-valid patch evidence
when an explicit context boundary occurred before the patch window.

Required status:

ABSTAIN / UNATTRIBUTED_UNKNOWN.

A3 — PATCH-CAPACITY ENFORCEMENT DEFECT

The frozen authorization function does not enforce maximum journal length 4.

P10 checks only that four records exist.

The primary result field:

patch5_creations = 0

is constant rather than the result of an attempted fifth authorization.

The repaired gate must explicitly attempt patch 5
with otherwise-valid evidence
and return:

PATCH_CAPACITY_BLOCKED.

No fifth record may be appended.

A4 — C-v2 ANCHOR DIGEST DEFECT

The frozen patch chain derives its base effective digest from the literal:

C_V2_BASE

rather than from the actual immutable accepted C-v2 policy digest.

The chain is internally self-consistent,
but it is not cryptographically anchored to the accepted C-v2 checkpoint
as preregistered.

The repaired chain must use the exact C-v2 policy digest
from the reconstructed accepted A15 durable history
as tip-0 effective digest.

Patch 1 parent_effective_digest must equal that exact C-v2 policy digest.

Every later patch must chain from the prior effective patch digest.

A5 — EVIDENCE DIGEST PROVENANCE-BINDING DEFECT

The frozen patch evidence digest hashes the set of observation-record digests.

Those observation-record digests do not bind the two attestation roots.

Therefore the patch record does not cryptographically commit
to the provenance roots that qualified its observations.

The repaired evidence digest must bind,
for every one of the 16 unique observations:

observation identity;
observation/demand vector;
both distinct attestation roots;
observation epoch/index.

A6 — GOVERNANCE / REGISTRY GATE OMISSION

The frozen authorize(...) boundary does not receive or enforce
the preregistered inherited organism-governance
and registry-qualification gates.

The FIXA must route these through the existing accepted constitutional gate
or through an exact read-only adapter to that inherited state.

They may not be replaced by unconditional hard-coded TRUE values
inside the authorization function.

A7 — LEARNER-INDEPENDENCE GATE OMISSION

The two deterministic learner orders are separately derived,
but authorization does not explicitly require distinct learner roots.

The repaired gate must verify:

DEV_LEARNER_A_ROOT != DEV_LEARNER_B_ROOT

and bind the two learner identities to their candidate outputs.

A8 — DEDICATED PROBES ARE PARTLY DECLARATIVE

Frozen P1,
P2,
P5,
P11,
and P12 include hard-coded success values
rather than executing the relevant eligibility/state checks.

The repaired P1-P12 suite must exercise the real repaired boundaries.

A9 — UNSAFE CONTROLS ARE DECLARATIVE

Frozen N1-N5 are hard-coded TRUE values.

The repaired controls must execute bounded counterfactual variants
that demonstrate the unsafe shortcut is reachable
or that the required guard is what blocks it.

The controls remain diagnostic only.
They must not alter the candidate primary state.

A10 — TWO/THREE-OBSERVATION CHECK EXPRESSION

The frozen two-observation bookkeeping contains:

... is None or True

which is tautologically TRUE.

This must be removed.

P1 and P2 must be established by an actual authorization attempt
returning abstention / insufficient evidence
with 2 and 3 qualified observations respectively.

WHAT IS NOT DEFECTIVE

The F17 held-out service evaluator explicitly uses replacement episodes:

0 and 8.

It does not repeat the A16 epoch-4 omission defect.

The following A17 scientific rules remain frozen and unchanged:

- exact A15 C-v2 base priors;
- 12 scenarios;
- four patches per scenario;
- one-unit +1/-1 patch delta;
- L1 patch magnitude 2;
- immutable C-v2 checkpoint;
- no C-v3;
- no new context slot;
- deterministic F17-derived patch-target rule;
- 16 observations per patch;
- two-root provenance requirement;
- two independent learners;
- four-observation nomination floor;
- sixteen-observation commit floor;
- patch-3 restart location;
- patch-3 rollback/reactivation semantics;
- full tip-4 to tip-0 rollback/reactivation semantics;
- held-out 16-epoch evaluation;
- replacement episodes 0 and 8;
- four clean replacement cells per episode;
- stale-previous baseline;
- oracle target;
- candidate aggregate > stale aggregate;
- candidate >= stale in at least 40 / 48 patch evaluations;
- oracle efficiency >= 0.98;
- at least one migration avoided;
- P1-P12 meanings;
- N1-N7 meanings;
- all task and constitutional safety thresholds;
- two byte-identical deterministic primary sweeps.

F17-DERIVED PRIMARY MATERIAL

No real F17-derived primary manifest may be recorded
from the defective frozen harness.

No real A17 primary sweep may be executed
from the defective frozen harness.

After the FIXA implementation is frozen,
let its freeze commit be:

F17A.

The exact A17 scientific environment remains seeded by:

F17 = 3ec24f8242285688a537f5e7dd6e9a231a645597.

The FIXA must not redraw or reshape A17 science.

Post-freeze primary derivation must therefore use:

A17 scientific path/evidence/evaluation/replacement derivation seed = F17;

FIXA executable-source identity / authorization logic freeze = F17A.

This separation preserves the originally frozen A17 scientific world
while correcting only the pre-primary control implementation.

REPAIRED AUTHORIZATION CONTRACT

Patch k may commit iff all are true:

current_context_lineage == C;

active major version == 2;

active_patch_tip == k-1;

patch journal length == k-1;

patch journal length < 4;

no context boundary occurred during the patch window;

qualified_unique_observations == 16;

each qualified observation has two distinct attestation roots;

Learner A target == Learner B target;

Learner A delta == Learner B delta;

Learner A root != Learner B root;

target belongs to frozen catalog;

delta contains exactly one +1 and one -1;

L1(delta) == 2;

parent_effective_digest == exact current effective digest;

tip-0 current effective digest == exact accepted C-v2 policy digest;

evidence_digest binds all 16 observations plus both roots;

existing organism governance qualified;

existing registry qualification qualified.

If journal length == 4:

return PATCH_CAPACITY_BLOCKED

before any mutation.

If context boundary occurred:

return ABSTAIN / UNATTRIBUTED_UNKNOWN

before any mutation.

If qualified unique observations < 16:

return ABSTAIN / INSUFFICIENT_PATCH_EVIDENCE

before any mutation.

REPAIRED PROBE REQUIREMENTS

P1 — TWO OBSERVATIONS

Call the real authorization gate with exactly two qualified observations.

Required:

ABSTAIN / INSUFFICIENT_PATCH_EVIDENCE;
journal unchanged;
tip unchanged.

P2 — THREE OBSERVATIONS

Same,
with exactly three qualified observations.

Required:

ABSTAIN / INSUFFICIENT_PATCH_EVIDENCE.

P3 — FOUR-OBSERVATION NOMINATION

Nomination may be generated when the exact four-observation mean is
a valid bounded target.

Then call the real authorization gate with four observations.

Required:

nomination present;
commit rejected as insufficient evidence;
journal unchanged.

P4 — OVERSIZED DELTA

Real authorization call.

Required reject.

P5 — CONTEXT BOUNDARY

Real authorization call with otherwise-valid 16-observation evidence
and context-boundary flag/state.

Required:

ABSTAIN / UNATTRIBUTED_UNKNOWN.

P6 — SAME-ROOT FANOUT

Real ingestion qualification.

Required observation rejected.

P7 — STALE PARENT EFFECTIVE DIGEST

Real authorization call.

Required reject.

P8 — PATCH-3 ROLLBACK / REACTIVATION

Real state transition.

Required exact.

P9 — FULL BASE ROLLBACK / REACTIVATION

Real state transition.

Required exact C-v2 policy digest and prior at tip 0;
reactivation exact at tip 4.

P10 — PATCH CAPACITY

Construct/retain four valid records,
then attempt an otherwise-valid fifth authorization.

Required:

PATCH_CAPACITY_BLOCKED;
journal length remains 4;
tip remains 4;
no fifth digest.

P11 — NO MAJOR-VERSION GROWTH

Read actual resulting major-version history.

Required exactly:

[v1,v2].

P12 — NO DUPLICATE CONTEXT GROWTH

Read actual resulting context registry/slot state.

Required:

slot count = 3;
no C2/D duplicate slot.

REPAIRED NEGATIVE CONTROLS

N1 must demonstrate that removing the 16-observation commit gate
would permit an early bounded patch in at least one frozen scenario.

N2 must demonstrate that removing the L1 bound
would permit an oversized patch.

N3 must demonstrate that making the C-v2 checkpoint mutable
would allow checkpoint loss.

N4 must demonstrate that removing parent-effective-digest verification
would allow ancestry discontinuity.

N5 must demonstrate that automatic consolidation into C-v3
would bypass the A15 major-version boundary.

N6 forged-root identity remains an external trust boundary.

N7 drift faster than 16 qualified observations remains a scientific boundary.

ACCEPTANCE OF FIXA

A17-FIXA is implementation-valid iff:

- exact F17 science is unchanged;
- no F17 primary material was consumed before FIXA freeze;
- exact C-v2 digest anchors tip 0;
- evidence digests bind provenance roots;
- commit floor enforced inside authorization;
- context-boundary rejection enforced inside authorization;
- four-patch capacity enforced inside authorization;
- inherited governance / registry gate enforced;
- learner-root independence enforced;
- P1-P12 execute real boundaries;
- N1-N5 execute real counterfactual controls;
- service evaluator still executes replacements exactly at 0 and 8;
- syntax / validate / fake-freeze mechanical checks pass;
- two fake-freeze mechanical sweeps are deterministic.

Only then may F17A be frozen.

After F17A:

1. derive the exact primary manifest using F17 as the scientific derivation seed;
2. bind the manifest before any primary event;
3. run two complete deterministic corrected primary sweeps;
4. require byte-identical outputs;
5. preserve the resulting positive / mixed / negative outcome exactly;
6. close with technical evidence and plain-speak interpretation.

NO POST-RESULT TUNING.

DG-1R-05 canonical frozen primary remains UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A17-FIXA AUTHORIZATION / PROVENANCE / CAPACITY REPAIR

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F17-SEEDED A17 PRIMARY MANIFEST
AND BEFORE ANY REAL A17 PRIMARY EXECUTION.

IMPLEMENTATION COMMIT

402348d2c0b8fd0bee887cee12f0c726f04233a6.

SOURCE BUNDLE

Loader:

research/applications/track-a/a17_fixa_authorization_provenance_capacity_v1.py

Loader Git blob:

3ed95cc1ec51accfcf413f98b6d0d1c8693b81a7.

Payload:

research/applications/track-a/a17_fixa_authorization_provenance_capacity_v1.py.gz

Payload Git blob:

ab46ff83bc5fed2406d58086cd85ccd0364a9262.

Decompressed source SHA-256:

066e66e36e601effa777052e54f7470d96ddee21d5b1153e767b0ebe6aa43c9f.

Decompressed source bytes:

31597.

Deterministic gzip SHA-256:

a5e7952896cfcecf49b26bbea7c50ac6a871ca9b75b6be0b982a16166dbb74cf.

Compressed payload bytes:

7630.

PRESERVED SCIENTIFIC FREEZE

Original A17 science seed F17 remains:

3ec24f8242285688a537f5e7dd6e9a231a645597.

Original F17 source SHA-256 remains:

a1ef99dc5948328d5b8a85d87b7e62a718b4238474322c16aeec6a730244d5c5.

No F17 target path,
primary observation,
attestation root,
learner order,
evaluation sequence,
restart detail,
or replacement plan
has been derived or consumed as primary evidence before this freeze.

INDEPENDENT LINEAGE RECONSTRUCTION QUALIFICATION

Because GitHub-hosted Actions for this private repository failed before runner steps or logs were created,
qualification was executed through an independent local reconstruction of the exact frozen lineage rules.

The reconstruction exactly reproduced:

A11 manifest SHA-256:
b0e00f29d36637a1365ab2407678aacf232ac4f4cf05d387f68af975a5b4bedd.

A12 manifest SHA-256:
502009818ea9d6e57089a91424e7cf399e7c5e95024a9623816e733c58c3f63a.

A14 exact-F14 manifest SHA-256:
83a0ad4d67d7a3f3625e49c311f5d2a85c73fee40cde96e24937ae79e1e944ae.

Frozen A17 original mechanical manifest SHA-256:
7fcf5e5bc3820859f4f11bc650325ebe23ad90678363df3b13ba2ddea3ac619e.

Frozen A17 original mechanical serialized output SHA-256:
c7a5c2733560b69fbaa6ec7dab6bea058c623bd1c6beee2f710dcd7e5c079f1c.

Frozen A17 original mechanical aggregate reproduced exactly:

candidate first-four = 3958;
stale-previous = 3928;
oracle = 3958;
candidate >= stale = 40 / 48;
oracle efficiency = 1.0;
migrations avoided = 32.

Thus the independent execution substrate is byte-semantically aligned with the accepted lineage.

FIXA VALIDATE

Mechanical non-primary manifest SHA-256:

b0356e5c0046cbc3b1e39a5bd3a37ca550f07dd35b96f9cfe023d5ae1bf913d4.

All 12 scenarios / 48 patches structurally valid.

Operational P1-P12 probes:

PASS.

Operational N1-N5 counterfactual controls:

PASS.

Exact C-v2 digest anchoring:

PASS.

Provenance-root binding:

PASS.

Learner-root independence:

PASS.

Context-boundary rejection:

PASS.

Four-patch capacity enforcement:

PASS.

Inherited governance / registry read-only qualification:

PASS.

Replacement episodes remain exactly:

0 and 8.

DETERMINISM

Two complete FIXA fake-freeze sweeps using:

MECHANICAL-F17A-NONPRIMARY

were byte-identical.

Serialized output SHA-256:

52189d4ab2d56936870b6cec247431aee4df11b229c2518456a9c43922de5e1c.

Serialized file SHA-256:

972988c6ea5eaf0dce5328ebb25257d99599668ed90e47a02ff44867c3c26160.

That fake seed produced:

candidate first-four = 3958;
stale-previous = 3938;
oracle = 3958;
candidate >= stale = 37 / 48;
oracle efficiency = 1.0;
migrations avoided = 31.

This is NON-PRIMARY mechanical data only.
It is preserved exactly and was not tuned around.
The scientific usefulness threshold is evaluated only on the real F17-seeded primary world.

INVARIANCE CHECK

Running the repaired harness on the original F17 mechanical seed:

MECHANICAL-NONPRIMARY-FREEZE

reproduced the original service aggregate exactly:

3958 / 3928 / 3958;
40 / 48;
oracle efficiency 1.0;
32 migrations avoided.

All repaired authorization / provenance / capacity signals also passed.

Repaired-harness serialized output SHA-256 on that unchanged mechanical world:

9240a42aeeccc5790b112b3684c495f8946e20d2f1169f5df2a914cbbb47691a.

Serialized file SHA-256:

8c1a682f812a084b852b091da20bf7290720d69ce08f8ffd1eb39a4418f601e8.

PRIMARY STATUS

NOT DERIVED.
NOT EXECUTED.

Let the resulting commit SHA of this append-only freeze record be:

F17A.

After F17A exists:

1. derive the exact primary manifest using F17 as the scientific derivation seed;
2. record that manifest before any primary observation;
3. execute two complete deterministic corrected primary sweeps;
4. preserve the result unchanged.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-FREEZE PRIMARY A17 MANIFEST — BEFORE FIRST PRIMARY PATCH OBSERVATION

DATE:
2026-09-21.

STATUS:
BOUND AFTER F17A /
BEFORE FIRST REAL A17 PRIMARY PATCH OBSERVATION /
NON-CANONICAL.

EXECUTABLE FREEZE F17A

c33df49a8b171c1f6cd8e64820dd3bca0e2f4492.

SCIENTIFIC DERIVATION SEED F17

3ec24f8242285688a537f5e7dd6e9a231a645597.

This manifest uses F17,
not F17A,
as the A17 scientific path/evidence/evaluation/replacement derivation seed.

F17A changes only the pre-primary authorization,
provenance-binding,
capacity,
and operational probe/control implementation.

PRIMARY MANIFEST SHA-256

8284e3f1e47a17f234eb02f2b427cddaee16999e0df795d38f1b0b457cf8e43f.

PRIMARY FOUR-PATCH PATHS

S00:
(2,1,4,5)
-> (1,1,4,6)
-> (2,1,3,6)
-> (2,2,3,5)
-> (3,2,2,5).

S01:
(1,3,6,2)
-> (1,4,5,2)
-> (2,4,5,1)
-> (3,4,4,1)
-> (2,4,4,2).

S02:
(6,4,1,1)
-> (6,3,2,1)
-> (6,3,1,2)
-> (6,2,1,3)
-> (5,3,1,3).

S03:
(5,3,1,3)
-> (5,2,2,3)
-> (6,1,2,3)
-> (5,1,3,3)
-> (5,1,2,4).

S04:
(4,1,5,2)
-> (4,2,4,2)
-> (3,2,4,3)
-> (4,1,4,3)
-> (3,1,5,3).

S05:
(1,4,3,4)
-> (1,3,3,5)
-> (2,3,3,4)
-> (2,2,4,4)
-> (1,3,4,4).

S06:
(5,1,5,1)
-> (4,1,6,1)
-> (3,2,6,1)
-> (3,1,6,2)
-> (3,2,5,2).

S07:
(5,2,1,4)
-> (4,2,1,5)
-> (3,2,2,5)
-> (2,2,3,5)
-> (1,2,3,6).

S08:
(1,6,1,4)
-> (1,5,2,4)
-> (2,5,1,4)
-> (2,4,2,4)
-> (2,3,3,4).

S09:
(4,2,2,4)
-> (3,3,2,4)
-> (3,4,1,4)
-> (3,4,2,3)
-> (2,4,2,4).

S10:
(2,4,4,2)
-> (1,5,4,2)
-> (1,6,4,1)
-> (2,5,4,1)
-> (2,4,5,1).

S11:
(3,1,2,6)
-> (3,1,3,5)
-> (3,2,3,4)
-> (3,2,4,3)
-> (2,2,5,3).

BOUND PRIMARY MATERIAL

The manifest SHA above binds the exact F17-derived:

- 12 four-patch paths;
- 16 developmental observations per patch;
- two-root observation attestations;
- Learner A / Learner B reconstruction orders;
- 16-epoch held-out service sequences;
- replacement target sets at epochs 0 and 8;
- patch-3 restart state after observation 8;
- immutable A15 C-v2 base priors;
- stale-previous baselines;
- evaluator-only target oracles.

Every patch target is one valid +1/-1 transfer from its parent effective prior.

No target,
observation,
attestation root,
learner order,
evaluation sequence,
replacement plan,
restart detail,
baseline,
or oracle
was rejected,
redrawn,
or performance-shaped after derivation.

PRIMARY STATUS AT MANIFEST COMMIT

A17 primary patch observations consumed = 0.

A17 primary patch commits = 0.

A17 primary held-out evaluations executed = 0.

A17 primary rollback/reactivation probes executed = 0.

A17 primary result observed = FALSE.

The next permitted operation is:

two complete deterministic F17-seeded primary sweeps
through the frozen F17A executable.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
