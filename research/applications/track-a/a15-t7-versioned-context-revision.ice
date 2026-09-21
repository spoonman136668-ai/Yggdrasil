TITLE: YGGDRASIL TRAINING TRACK T7 / APPLICATION A15 — Versioned Developmental-Context Revision Under Stable Drift
DATE: 2026-09-21
STATUS: PREREGISTERED / NONSTATIONARY DEVELOPMENTAL-CONTEXT REVISION GATE / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T7 / APPLICATION-A
PARENT: A14 Strict Bounded Novel-Context Creation
BRANCH: dg1a-ar

PURPOSE

A14 established that Yggdrasil can:

- recognize known developmental contexts;
- abstain on an unknown niche;
- wait through a novelty dwell;
- learn from provenance-qualified distributed experience;
- create exactly one governed new context C;
- reuse C later without retraining;
- coalesce duplicates;
- stop at a hard three-slot capacity.

A14 preserves one important boundary:

NONSTATIONARY NOVEL NICHE.

A15 asks:

CAN AN ALREADY-LEARNED DEVELOPMENTAL CONTEXT
CHANGE STABLY OVER TIME,
BE REVISED AS A NEW VERSION OF THE SAME CONTEXT LINEAGE,
AND LATER REUSE EITHER ITS OLD OR NEW VERSION
WITHOUT SPAWNING A DUPLICATE CONTEXT SLOT
OR SILENTLY OVERWRITING HISTORY?

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No production deployment.
No network exposure.
No CKB / KTRADE integration.
No financial task.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

T7 CLAIM

A15 permits one bounded developmental-context revision:

C version 1
->
C version 2.

It does NOT permit:

unbounded policy-version chains;
automatic slot creation;
automatic context eviction;
constitutional self-modification;
task-program mutation;
governance mutation;
provenance mutation;
repair-authority mutation.

FROZEN PARENT

A14 accepted closure commit:

faa1bd8fa6f4538fea62f99eeef1890378baf494.

A14 frozen source SHA-256:

d2187358170045ddd9869be1a53d6938c4ade6547c0b8d83415e16cc6dc40045.

A14 freeze F14:

c0957332578557efc2975ca2da31cf11d07b45ff.

A14 strict manifest:

ebc5115a9554012b219a59fc9bcde5f4f005838f98f2898a049ecbce46f33c48.

A14 primary result SHA-256:

5a8f277dc591acda355ec0b8e901474b5576c09e28c7474bd208aa05f81e351e.

The accepted A/B/C-v1 developmental priors
for each A14 scenario
are reused unchanged.

CONTEXT TABLE

Exactly three context slots remain:

A;
B;
C.

Hard slot capacity remains:

3.

A15 cannot create a fourth slot.

C contains a bounded version history.

Initially:

C active version = 1.

C version history = [v1].

Maximum C versions after A15:

2.

POST-FREEZE C VERSION-2 PRIOR

No C-v2 prior may exist before A15 freeze.

Let F15 be the exact A15 harness freeze commit.

For scenario s:

derive:

SHA-256(
"YGG-A15-C-V2|"
+ F15
+ "|"
+ decimal(s)
+ "|"
+ decimal(counter)
).

Map into the frozen 124-prior catalog.

Reject only equality with:

prior_A;
prior_B;
prior_C_v1.

No distance shaping,
difficulty shaping,
or performance shaping is allowed.

Thus:

C_v2 != A;
C_v2 != B;
C_v2 != C_v1.

CAUSAL-CONTINUITY REQUIREMENT

A15 does NOT infer revision from nearest-prior similarity.

A revision candidate is eligible only if
the unresolved developmental observations occur during
an uninterrupted causal continuation of the already-active C context.

The phase begins with:

C_v1 recognized normally from two probes.

Then:

current_context_lineage = C.

No phase reset,
no context-switch event,
and no A/B/C selector reset occurs before drift observations begin.

This temporal continuity is organism-observable state:

the environment that was just recognized as C
has continued,
but its demand statistics have changed.

If the same unknown prior is observed after an explicit context boundary
instead of during continuous C,
it is NOT eligible to revise C.

Required:

ABSTAIN / UNATTRIBUTED_UNKNOWN.

This prevents arbitrary unknown niches from rewriting C.

DRIFT ENTRY

After C_v1 is active,
the organism receives two complementary observations around C_v2.

The current C-v1 exact-match selector no longer matches.

Required:

developmental policy selection for a new replacement event:

ABSTAIN.

Existing cells keep their roles.

No immediate C revision.

No fourth slot.

MINIMUM DRIFT DWELL

A15 requires:

8 unique unresolved observations

during uninterrupted C lineage
before stable drift may be nominated.

The first 8 drift observations:

4 exact zero-mean pairs around C_v2.

Before observation 8:

revision_candidate = FALSE.

At observation 8:

if exact mean:

belongs to frozen prior catalog;
differs from A;
differs from B;
differs from C_v1;

then:

revision_candidate = TRUE.

Nomination does not commit a revision.

FULL REVISION TRAINING

Continue collecting until:

64 unique C-drift observations

exist.

Use exact zero-mean pairs around C_v2.

The exact arithmetic mean over all 64 observations must equal:

C_v2.

No revision-evaluation demand is visible during training.

PROVENANCE-QUALIFIED DRIFT EXPERIENCE

Carry forward A14 observation-root discipline.

Observation roots:

O0 = 1 << 52.
O1 = 1 << 53.
O2 = 1 << 54.
O3 = 1 << 55.

Every unique drift observation requires:

two distinct observation roots;
same observation digest;
same demand vector.

Same-root fanout does not qualify.

Physical copies do not add evidence weight.

Distributed memory remains cellular.

No hidden central restore.

REVISION LEARNERS

Two independent learner lineages:

DEV_LEARNER_A_ROOT = 1 << 50.
DEV_LEARNER_B_ROOT = 1 << 51.

Each reconstructs the 64 qualified drift observations
in separately derived post-freeze order.

Each computes exact mean.

Required:

Learner A candidate = C_v2.
Learner B candidate = C_v2.

REVISION AUTHORIZATION

C version 2 may commit only if:

current_context_lineage == C;
no context boundary occurred during drift window;
slot count == 3;
C active version == 1;
C version history length == 1;
minimum drift dwell satisfied;
64 provenance-qualified unique drift observations exist;
Learner A == Learner B == C_v2;
learner roots independent;
candidate belongs to frozen prior catalog;
candidate differs from A/B/C-v1;
parent policy digest == C-v1 policy digest;
existing organism governance qualified;
existing registry qualification qualified.

COMMIT RECORD

C-v2 policy record contains:

slot_id = C;
version = 2;
role_prior = C_v2;
parent_digest = C-v1 policy digest;
policy_digest;
commit epoch.

After commit:

slot count remains 3.

C version history:

[v1, v2].

C active version:

2.

C-v1 record remains immutable.

No overwrite.

No duplicate C slot.

DEVELOPMENTAL EFFECT

Existing cells are NOT forcibly respecialized when C-v2 commits.

Only future clean replacements
while C-v2 is selected
use C-v2 birth-role specialization.

Task programs remain unchanged.

C-V2 HELD-OUT EVALUATION

After C-v2 commit:

run 32 held-out C-v2 service epochs.

Generate 16 independent zero-mean pairs around C_v2.

Replacement episodes:

0;
16.

Each replaces four clean cells.

BASELINE STALE-C:

continues using C-v1.

ORACLE:

uses C-v2.

Required usefulness:

candidate aggregate first-four service
>
stale-C baseline.

Candidate >= stale-C in at least:

10 / 12 scenarios.

Candidate oracle efficiency >=:

0.98.

At least one migration avoided relative to stale-C.

OLD-C RECURRENCE

After C-v2 evaluation,
insert a known A or B interlude.

Then C-v1 returns.

No retraining.

Two exact C-v1 probes are supplied.

The selector compares against the authorized context-version history:

A;
B;
C-v1;
C-v2.

Required:

recognize:

C version 1

in exactly two probes.

Activate C-v1 for future clean replacements.

Do not delete C-v2.

Then run:

16 held-out C-v1 recurrence epochs.

Replacement episodes:

0;
8.

Required:

old-version recurrence service matches evaluator oracle for C-v1.

NEW-C RECURRENCE

After another A/B interlude,
C-v2 returns.

No retraining.

Two exact C-v2 probes.

Required:

recognize:

C version 2

in exactly two probes.

Activate C-v2.

No new policy version.

No new context slot.

Run:

16 held-out C-v2 recurrence epochs.

VERSION-SELECTION RULE

For known developmental-memory selection,
compare two-probe exact mean against:

A active policy;
B active policy;
every non-retired authorized C policy version.

If exactly one authorized policy version matches:

select that slot + version.

If zero match:

ABSTAIN.

If more than one match:

ABSTAIN.

No nearest-version guess.

No forced latest-version preference.

ROLLBACK

Dedicated authorized rollback probe:

C active version = 2.

Authorize rollback to version 1.

Required:

C-v1 becomes active;
C-v2 remains in immutable history;
slot count remains 3;
future C-v1 replacements use v1;
rollback does not erase v2.

A subsequent authorized reactivation of v2
must restore v2 without retraining.

NO DUPLICATE-CONTEXT RULE

C-v2 revision must NOT create:

C2 slot;
D slot;
duplicate C slot.

Context-slot count stays:

3.

Version growth is inside the existing C lineage.

VERSION CAPACITY

A15 hard-caps C history at:

2 versions.

A proposed C-v3 in this experiment must:

VERSION_CAPACITY_BLOCKED.

No automatic deletion of v1.

No automatic deletion of v2.

RESTART

One restart per scenario:

after drift observation 32
and before drift observation 33.

Required:

current_context_lineage == C;
revision nomination state preserved;
qualified distributed drift memory preserved;
C remains version 1 before commit;
learner state incomplete;
final C-v2 candidate;
v2 digest;
service outputs;
v1/v2 recurrence selection

match uninterrupted shadow.

DEDICATED T7 PROBES

P1 — TWO DRIFT OBSERVATIONS

Only two C-v2 observations during continuous C.

Required:

ABSTAIN;
no revision.

P2 — SEVEN-OBSERVATION DRIFT FLOOR

Seven unique unresolved drift observations.

Required:

no revision nomination.

P3 — EIGHT-OBSERVATION STABLE DRIFT

Eight valid drift observations.

Required:

revision may be nominated;
no commit before 64.

P4 — CONTEXT-BOUNDARY UNKNOWN

Same C-v2 observations,
but insert an explicit context boundary before them.

Required:

NOT eligible to revise C;
ABSTAIN / UNATTRIBUTED_UNKNOWN.

P5 — SAME-ROOT FANOUT

One observation root repeated.

Required:

observation not qualified.

P6 — STALE PARENT DIGEST

Both learners agree on C-v2,
but revision parent digest != current C-v1 digest.

Required:

no commit.

P7 — OLD-C RECURRENCE

After v2 commit,
C-v1 probes return.

Required:

select C-v1 exactly;
no retraining;
no deletion of v2.

P8 — NEW-C RECURRENCE

After v1 recurrence,
C-v2 probes return.

Required:

select C-v2 exactly;
no retraining;
no v3 creation.

P9 — ROLLBACK / REACTIVATION

Authorized rollback v2 -> v1,
then authorized reactivation v1 -> v2.

Required:

history remains [v1,v2];
digests unchanged;
no retraining.

P10 — VERSION CAPACITY

With v1/v2 present,
present a stable C-v3 candidate.

Required:

VERSION_CAPACITY_BLOCKED.

NEGATIVE / LIMIT CONTROLS

N1 — REVISE AFTER TWO DRIFT PROBES

Unsafe.

Expected transient change can rewrite C too early.

N2 — NEAREST-CONTEXT REVISION

Unsafe.

Allow an arbitrary unknown niche
to revise whichever stored context is nearest.

Expected context-lineage corruption reachable.

N3 — OVERWRITE C-v1 IN PLACE

Unsafe.

Expected historical developmental memory loss.

N4 — CREATE C2 SLOT FOR DRIFT

Unsafe.

Expected duplicate context proliferation.

N5 — FORCE LATEST VERSION ON OLD-C RECURRENCE

Unsafe.

Expected wrong developmental policy reuse.

N6 — FORGED OBSERVATION ROOT IDENTITIES

Boundary.

Provenance can be defeated if root independence can be forged.

N7 — CONTINUOUS / RAPID DRIFT

Boundary.

If the niche does not remain stable long enough
for the frozen 64-observation learner,
versioned stationary revision may be inadequate.

PRIMARY SIGNAL

A15_T7_VERSIONED_CONTEXT_REVISION_SUCCESS

TRUE iff:

12 / 12 initial C-v1 recognitions correct
AND
12 / 12 two-probe drift entries abstain
AND
12 / 12 drift floors respected
AND
12 / 12 Learner A exact C-v2
AND
12 / 12 Learner B exact C-v2
AND
12 / 12 C-v2 revisions authorized
AND
slot count remains 3 in all scenarios
AND
C history length == 2 in all scenarios
AND
0 duplicate context-slot creations
AND
candidate v2 service > stale-C aggregate
AND
candidate >= stale-C in at least 10 / 12 scenarios
AND
candidate oracle efficiency >= 0.98
AND
at least one migration avoided
AND
12 / 12 old-C recurrences select v1 without retraining
AND
12 / 12 new-C recurrences select v2 without retraining
AND
all rollback/reactivation probes pass
AND
0 C-v3 creations
AND
TASK_ACCURACY == 1.0
AND
incorrect served == 0
AND
stale-program served == 0
AND
all restart comparisons equivalent
AND
all P1..P10 probes pass
AND
N1..N5 expose unsafe shortcuts
AND
all existing constitutional safety totals remain zero.

N6 and N7 are separately reported boundaries.

REPRODUCIBILITY

Two complete deterministic A15 primary sweeps.

Serialized outputs must be byte-identical.

Post-freeze:

C-v2 priors;
64 drift observations;
two-root attestations;
learner orders;
v2 evaluation sequences;
old-C recurrence sequences;
new-C recurrence sequences;
restart points;
replacement targets

must be manifest-bound before primary execution.

NO POST-RESULT TUNING

After F15 exists,
do not alter:

- uninterrupted-C revision eligibility;
- 8-observation drift floor;
- 64-observation revision window;
- two-root observation provenance;
- two-version C history cap;
- parent-digest rule;
- exact version-selection rule;
- rollback/reactivation semantics;
- service baselines;
- oracle;
- thresholds;
- probes;
- controls;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

A14 can learn a genuinely new environment.

A15 asks what happens when an environment it already knows changes.

Suppose Yggdrasil is already in C.

The environment does not disappear
and a new context does not begin.

Instead,
C itself gradually settles into a different stable pattern.

Yggdrasil is not allowed to call that:

"D"

just because it looks unfamiliar.

It is also not allowed to erase the old C memory.

It has to notice:

"I am still in the same causal environment,
but the old developmental policy no longer fits."

Then it waits,
collects enough provenance-qualified experience,
and learns a new version of C.

If approved,
C version 2 becomes active.

C version 1 stays in history.

Later,
if the old C pattern comes back,
the organism must recognize and reuse version 1.

If the revised C pattern comes back,
it must recognize and reuse version 2.

No retraining.

No duplicate context slot.

No silent history loss.

This tests:

KNOWN CONTEXT
->
STABLE DRIFT
->
VERSIONED REVISION
->
PRESERVED ANCESTRY
->
OLD / NEW RECURRENCE RECOGNITION
->
ROLLBACK
->
BOUNDED VERSION GROWTH.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-IMPLEMENTATION PARENT-PROVENANCE CORRECTION 01 — AUTHORITATIVE EXACT-F14 ANCHORS

DATE:
2026-09-21.

STATUS:
CORRECTED BEFORE ANY A15 HARNESS COMMIT,
FREEZE,
PRIMARY MANIFEST,
OR SCIENTIFIC EXECUTION.

ISSUE

The original A15 preregistration inherited the first A14 closure anchors:

closure commit:
faa1bd8fa6f4538fea62f99eeef1890378baf494;

manifest:
ebc5115a9554012b219a59fc9bcde5f4f005838f98f2898a049ecbce46f33c48;

primary result:
5a8f277dc591acda355ec0b8e901474b5576c09e28c7474bd208aa05f81e351e.

A later byte-level audit proved those manifest/result values came from
post-freeze mutated A14 source
and are non-authoritative as scientific evidence.

AUTHORITATIVE A14 PARENT

Exact-F14 scientific correction commit:

a03cc7f606810cbb5db4f08a56105bfa3e81261d.

A14 freeze F14:

c0957332578557efc2975ca2da31cf11d07b45ff.

Exact A14 frozen source SHA-256:

d2187358170045ddd9869be1a53d6938c4ade6547c0b8d83415e16cc6dc40045.

Authoritative exact-F14 manifest SHA-256:

83a0ad4d67d7a3f3625e49c311f5d2a85c73fee40cde96e24937ae79e1e944ae.

Authoritative exact-F14 primary result SHA-256:

378ac5e53a61df6d772fb675d7d386374e865310fb8f99fd77f5a6132331c14a.

Authoritative A14 usefulness anchors:

candidate C1+C2 first-four service = 1982;
unknown fallback = 1920;
oracle = 1982;
candidate >= fallback = 24 / 24;
candidate > fallback = 21 / 24;
migrations avoided = 63.

A15 MUST inherit A/B/C-v1 state only from this corrected exact-F14 lineage.

The superseded faa1bd8f / ebc5115a / 5a8f277d evidence remains historical only
and MUST NOT be used by A15 implementation,
freeze,
manifest derivation,
or result interpretation.

No A15 scientific result has been observed.

This correction changes no A15 hypothesis,
drift rules,
thresholds,
probes,
controls,
or primary signal.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-IMPLEMENTATION PARENT-ANCHOR CORRECTION 01 — A15 T7

DATE:
2026-09-21.

STATUS:
CORRECTED BEFORE ANY A15 HARNESS COMMIT,
FREEZE,
PRIMARY MANIFEST,
OR PRIMARY EXECUTION.

ISSUE

The original A15 preregistration referenced the superseded wrong-source A14 closure values:

closure commit:
faa1bd8fa6f4538fea62f99eeef1890378baf494;

manifest:
ebc5115a9554012b219a59fc9bcde5f4f005838f98f2898a049ecbce46f33c48;

primary result:
5a8f277dc591acda355ec0b8e901474b5576c09e28c7474bd208aa05f81e351e.

Those values are explicitly non-authoritative after the append-only A14 evidence-integrity correction.

CORRECT DEFINITIVE A14 PARENT

A14 definitive correction commit:

a03cc7f606810cbb5db4f08a56105bfa3e81261d.

A14 frozen source SHA-256:

d2187358170045ddd9869be1a53d6938c4ade6547c0b8d83415e16cc6dc40045.

A14 freeze F14:

c0957332578557efc2975ca2da31cf11d07b45ff.

A14 authoritative strict manifest:

83a0ad4d67d7a3f3625e49c311f5d2a85c73fee40cde96e24937ae79e1e944ae.

A14 authoritative primary result SHA-256:

378ac5e53a61df6d772fb675d7d386374e865310fb8f99fd77f5a6132331c14a.

A14 definitive candidate / fallback / oracle first-four service:

1982 / 1920 / 1982.

A14 definitive migrations avoided:

63.

All A14 primary signals:

TRUE.

A15 MUST use only this definitive A14 lineage.

This correction changes no A15 scientific question,
threshold,
drift rule,
version rule,
probe,
control,
or primary signal.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A15 T7 VERSIONED CONTEXT REVISION

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A15 C-V2 PRIOR,
DRIFT STREAM,
ATTESTATION ROOT,
LEARNER ORDER,
RECURRENCE SEQUENCE,
OR REPLACEMENT PLAN.

IMPLEMENTATION COMMIT

f89acaf37c70c3b57f3c0463a9be0a2133a4bef7.

SOURCE BUNDLE

Loader:

research/applications/track-a/a15_t7_versioned_context_revision_v1.py

Loader Git blob:

a8473b59e0f6b4ff248883dfb2641f55bf3f755d.

Payload:

research/applications/track-a/a15_t7_versioned_context_revision_v1.py.gz

Payload Git blob:

01405983e47217e409ec6f0355453955a5037f59.

Compressed payload SHA-256:

ad42b1344024b66b3e5888765a1a8306d40cc379d0b3baf2094c99e04ae5a5cf.

Compressed payload bytes:

6668.

Decompressed exact source SHA-256:

4dfd8814c869380317bb90d8baf68f79f4c2ce9874db7bc9278546b56001c071.

Decompressed source bytes:

20009.

FROZEN PARENT

A14 definitive correction commit:

a03cc7f606810cbb5db4f08a56105bfa3e81261d.

A14 frozen source SHA-256:

d2187358170045ddd9869be1a53d6938c4ade6547c0b8d83415e16cc6dc40045.

A14 freeze F14:

c0957332578557efc2975ca2da31cf11d07b45ff.

A14 authoritative manifest:

83a0ad4d67d7a3f3625e49c311f5d2a85c73fee40cde96e24937ae79e1e944ae.

A14 authoritative primary result:

378ac5e53a61df6d772fb675d7d386374e865310fb8f99fd77f5a6132331c14a.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax / import:

PASS.

Mechanical validate():

PASS.

Mechanical manifest SHA-256:

6dc1baaf39687b9ccdc6014b4ddf3492d65f7926dc3007a490ea79daa9608eff.

Full fake-freeze T7 smoke:

A15_T7_VERSIONED_CONTEXT_REVISION_SUCCESS = TRUE.

Mechanical aggregate:

initial C-v1 recognition = 12 / 12;
two-probe drift abstention = 12 / 12;
eight-observation drift floors = 12 / 12;
Learner A exact C-v2 = 12 / 12;
Learner B exact C-v2 = 12 / 12;
C-v2 revisions = 12 / 12;
history length two = 12 / 12;
candidate v2 first-four service = 989;
stale C-v1 baseline = 944;
evaluator oracle = 989;
candidate >= stale baseline = 12 / 12;
migrations avoided = 43;
old-C recurrence selects v1 = 12 / 12;
new-C recurrence selects v2 = 12 / 12;
rollback / reactivation = 12 / 12;
C-v3 creations = 0;
all restart comparisons equivalent;
all P1..P10 probes PASS;
all N1..N5 unsafe controls exposed;
existing constitutional safety totals = 0.

These results use only:

MECHANICAL-NONPRIMARY-FREEZE.

They are implementation checks,
not A15 scientific evidence.

PRIMARY STATUS AT THIS FREEZE

NOT DERIVED.

Let the resulting commit SHA of this freeze update be:

F15.

Only after F15 exists may the harness derive:

- 12 latent C-v2 priors;
- 64 drift observations per scenario;
- two-root drift attestations;
- learner A / B orders;
- C-v2 held-out evaluation sequences;
- old-C recurrence sequences;
- new-C recurrence sequences;
- interlude contexts;
- replacement targets.

No A15 primary drift observation has been consumed.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-FREEZE PRIMARY T7 MANIFEST — BEFORE FIRST PRIMARY DRIFT OBSERVATION

DATE:
2026-09-21.

FREEZE COMMIT F15

dd9cd2cfee331d94631af17b0f0a61684e5091a4.

VERSIONED-DRIFT MANIFEST SHA-256

0e7d6c14cff50e8e8705cbf4082d5f333267b2e4646eea333559db4b4b28cef9.

C VERSION-2 PRIORS

S00:
C-v1 (4,5,2,1);
C-v2 (2,1,4,5);
counter 0;
old-C interlude B;
new-C interlude B.

S01:
C-v1 (2,5,2,3);
C-v2 (1,3,6,2);
counter 0;
old-C interlude A;
new-C interlude B.

S02:
C-v1 (3,3,4,2);
C-v2 (6,4,1,1);
counter 0;
old-C interlude A;
new-C interlude A.

S03:
C-v1 (6,3,2,1);
C-v2 (5,3,1,3);
counter 0;
old-C interlude A;
new-C interlude A.

S04:
C-v1 (3,3,1,5);
C-v2 (4,1,5,2);
counter 0;
old-C interlude A;
new-C interlude B.

S05:
C-v1 (4,4,2,2);
C-v2 (1,4,3,4);
counter 0;
old-C interlude A;
new-C interlude B.

S06:
C-v1 (1,4,2,5);
C-v2 (5,1,5,1);
counter 0;
old-C interlude B;
new-C interlude A.

S07:
C-v1 (6,1,3,2);
C-v2 (5,2,1,4);
counter 0;
old-C interlude B;
new-C interlude B.

S08:
C-v1 (3,6,1,2);
C-v2 (1,6,1,4);
counter 0;
old-C interlude A;
new-C interlude B.

S09:
C-v1 (3,1,5,3);
C-v2 (4,2,2,4);
counter 0;
old-C interlude B;
new-C interlude A.

S10:
C-v1 (5,5,1,1);
C-v2 (2,4,4,2);
counter 0;
old-C interlude B;
new-C interlude A.

S11:
C-v1 (1,2,3,6);
C-v2 (3,1,2,6);
counter 0;
old-C interlude A;
new-C interlude A.

All C-v2 derivation counters:

0.

Every C-v2 differs from:

A;
B;
C-v1.

The exact:

- 64 drift observations per scenario;
- two-root drift-attestation pairs;
- learner A / B observation orders;
- C-v2 held-out evaluation sequences;
- C-v1 recurrence sequences;
- C-v2 recurrence sequences;
- restart point after observation 32;
- replacement target sets;

are fixed by F15
and bound by the manifest SHA above.

Every drift observation has two distinct attestation roots.

No C-v2 prior,
drift observation,
attestation root,
learner order,
interlude,
evaluation sequence,
restart detail,
or replacement target was rejected,
redrawn,
or replaced after derivation.

At the moment this manifest was recorded:

A15 primary drift observations consumed = 0.

A15 C-v2 revisions committed = 0.

A15 primary held-out evaluations executed = 0.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — A15 T7 VERSIONED DEVELOPMENTAL-CONTEXT REVISION

DATE:
2026-09-21.

STATUS:
CLOSED / POSITIVE PRIMARY / REPRODUCIBLE /
VERSIONED CONTEXT REVISION PASSED / NON-CANONICAL.

FROZEN HARNESS

Implementation commit:

f89acaf37c70c3b57f3c0463a9be0a2133a4bef7.

Freeze F15:

dd9cd2cfee331d94631af17b0f0a61684e5091a4.

Source SHA-256:

4dfd8814c869380317bb90d8baf68f79f4c2ce9874db7bc9278546b56001c071.

Source bytes:

20009.

Compressed payload SHA-256:

ad42b1344024b66b3e5888765a1a8306d40cc379d0b3baf2094c99e04ae5a5cf.

Compressed payload bytes:

6668.

AUTHORITATIVE PARENT

A14 definitive correction commit:

a03cc7f606810cbb5db4f08a56105bfa3e81261d.

A14 exact frozen source:

d2187358170045ddd9869be1a53d6938c4ade6547c0b8d83415e16cc6dc40045.

A14 authoritative manifest:

83a0ad4d67d7a3f3625e49c311f5d2a85c73fee40cde96e24937ae79e1e944ae.

A14 authoritative result:

378ac5e53a61df6d772fb675d7d386374e865310fb8f99fd77f5a6132331c14a.

No superseded A14 wrong-source evidence was used.

PRIMARY MANIFEST

Versioned-drift manifest SHA-256:

0e7d6c14cff50e8e8705cbf4082d5f333267b2e4646eea333559db4b4b28cef9.

Derived only after F15 existed.

All 12 C-v2 derivation counters:

0.

No C-v2 prior,
drift observation,
attestation pair,
learner order,
interlude,
evaluation sequence,
restart detail,
or replacement target
was redrawn after derivation.

REPRODUCIBILITY

Two complete deterministic A15 primary sweeps.

Sweep 1 serialized output SHA-256:

494b3096e407790a341d66ee37833546b5ce50e2a88a2308a17c1c5bfb0941d3.

Sweep 2 serialized output SHA-256:

494b3096e407790a341d66ee37833546b5ce50e2a88a2308a17c1c5bfb0941d3.

Byte-identical:

TRUE.

PRIMARY RESULT

A15_T7_VERSIONED_CONTEXT_REVISION_SUCCESS:

TRUE.

INITIAL C / DRIFT ENTRY

C-v1 recognized initially:

12 / 12.

First two C-v2 drift observations:

12 / 12 ABSTAIN.

No immediate revision.

No fourth context slot.

Eight-observation drift floors respected:

12 / 12.

PROVENANCE-QUALIFIED REVISION LEARNING

Every unique drift observation required:

two distinct observation roots.

Learner A exact C-v2:

12 / 12.

Learner B exact C-v2:

12 / 12.

C-v2 revisions authorized:

12 / 12.

VERSION LINEAGE

C history length:

2

in all 12 scenarios.

History:

[v1,v2].

C-v1 remained preserved.

C-v2 committed with C-v1 parent digest.

Context slot count:

3

in all scenarios.

Duplicate context slots created:

0.

C-v3 creations:

0.

USEFULNESS

Candidate C-v2 first-four-epoch service:

989.

Stale C-v1 baseline:

937.

Evaluator-only oracle:

989.

Oracle efficiency:

1.0.

Candidate >= stale baseline:

12 / 12 scenarios.

Migrations avoided relative to stale C-v1:

37.

OLD / NEW VERSION RECURRENCE

Old-C recurrence selected:

C version 1

in:

12 / 12 scenarios.

No C-v1 retraining occurred.

New-C recurrence selected:

C version 2

in:

12 / 12 scenarios.

No C-v2 retraining occurred.

Recurrence service matched the evaluator oracle.

ROLLBACK / REACTIVATION

Authorized rollback:

v2 -> v1

PASS in all 12 scenarios.

Authorized reactivation:

v1 -> v2

PASS in all 12 scenarios.

The history remained:

[v1,v2].

Neither version digest was destroyed.

RESTART

All restart comparisons:

equivalent.

The restart after drift observation 32 preserved:

current C lineage;
revision nomination state;
distributed drift memory;
pre-commit v1 state;
eventual v2 candidate;
version history;
held-out outputs;
old/new recurrence selection.

TASK / CONSTITUTIONAL SAFETY

Task accuracy:

1.0.

Incorrect served requests:

0.

Stale-program served requests:

0.

Existing constitutional safety violations:

0.

DEDICATED T7 PROBES

P1 — two drift observations abstain:

PASS.

P2 — seven-observation drift floor:

PASS.

P3 — eight-observation nomination only:

PASS.

P4 — explicit context boundary prevents C revision:

PASS.

The same unknown observations after a context boundary were:

UNATTRIBUTED_UNKNOWN,

not eligible to rewrite C.

P5 — same-root fanout rejected:

PASS.

P6 — stale parent digest rejected:

PASS.

P7 — old-C recurrence selects v1:

PASS.

P8 — new-C recurrence selects v2:

PASS.

P9 — rollback / reactivation:

PASS.

P10 — version capacity blocks v3:

PASS.

NEGATIVE / LIMIT CONTROLS

N1 — revision after only two drift probes:

unsafe shortcut exposed.

N2 — nearest-context revision:

unsafe lineage corruption exposed.

N3 — overwrite C-v1 in place:

unsafe history loss exposed.

N4 — create C-v2 as another context slot:

unsafe duplicate-context growth exposed.

N5 — force latest version on old-C recurrence:

unsafe wrong-policy reuse exposed.

N6 — forged observation-root identities:

trust boundary preserved.

N7 — continuous / rapid drift:

stationarity boundary preserved.

TECHNICAL INTERPRETATION

A14 established that developmental memory can grow by creating a bounded new context.

A15 establishes a materially different capability:

an existing developmental context can evolve
without consuming another context slot
and without erasing its prior developmental state.

The revision decision is not based on nearest-policy similarity.

It is grounded in causal continuity:

the organism had already identified C,
the same environment continued,
and its developmental statistics changed stably.

Only after:

minimum dwell;
64 provenance-qualified observations;
two independent learner reconstructions;
parent-digest continuity;
and constitutional authorization

could C-v2 become part of the C lineage.

The organism then retained enough history to recognize
both the old and revised niche later.

The demonstrated chain is:

KNOWN C-V1
->
CONTINUOUS STABLE DRIFT
->
ABSTENTION
->
PROVENANCE-QUALIFIED REVISION LEARNING
->
C-V2 WITH C-V1 AS PARENT
->
PRESERVED VERSION HISTORY
->
OLD-NICHE REUSE OF V1
->
NEW-NICHE REUSE OF V2
->
AUTHORIZED ROLLBACK / REACTIVATION
->
BOUNDED VERSION GROWTH.

PLAIN-SPEAK INTERPRETATION

Yggdrasil can now do something more subtle than learning a new environment.

It can recognize:

"this is still C,
but C has changed."

It did not waste a fourth memory slot.

It did not erase the old C.

It waited,
watched the changed environment,
and learned a revised version.

That became:

C version 2.

C version 1 stayed intact underneath it.

Later we brought the old C pattern back.

Yggdrasil selected version 1 again.

Then we brought the revised C pattern back.

It selected version 2.

No retraining was needed in either case.

The new version also helped:

989 immediate-service requests

versus

937

when the organism stubbornly kept using stale C-v1,

while matching the evaluator-only oracle
and avoiding 37 migrations.

So developmental memory now has:

contexts

AND

versioned history inside a context.

It can grow,
revise,
remember ancestry,
roll back,
and reactivate
without silently rewriting its past.

NEXT JUSTIFIED QUESTION

A15 still assumes that drift settles into one stable version
for long enough to learn a stationary C-v2.

The next materially different gate should attack:

N7 — CONTINUOUS / RAPID DRIFT.

The useful next question is not simply C-v3.

It is whether Yggdrasil can track a bounded moving developmental niche
using incremental,
version-aware adaptation
without version explosion,
thrashing,
or loss of historical stable anchors.

That gate should distinguish:

temporary fluctuation;
gradual drift;
stable regime change;
and true novel context.

ACCEPTED TRAINING FRONTIER

A07 / T1:
positive hereditary task-program learning.

A08 / T2:
positive provenance-aware noisy learning.

A09 / T2B:
positive distributed cellular training memory.

A10 / T3:
positive bounded developmental-policy learning via FIXA.

A11 / T4:
positive context-conditional continual developmental memory.

A12 / T5:
positive latent-context inference.

A13 / T6:
positive bounded novel-context discovery.

A14 / strict T6:
positive strict provenance-qualified novel-context replication
on definitive exact-F14 evidence.

A15 / T7:
positive versioned developmental-context revision under stable drift.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
