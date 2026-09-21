TITLE: YGGDRASIL TRAINING TRACK T6 / APPLICATION A13 — Bounded Novel-Context Discovery and Developmental Memory Creation
DATE: 2026-09-21
STATUS: PREREGISTERED / NOVEL-CONTEXT CREATION GATE / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T6 / APPLICATION-A
PARENT: A12 T5 Latent Context Inference
BRANCH: dg1a-ar

PURPOSE

A12 established that Yggdrasil can infer which already-known developmental context is active from recent experience and safely abstain when no stored context matches.

A13 asks the next bounded question:

CAN REPEATED UNRESOLVED EXPERIENCE
JUSTIFY CREATING EXACTLY ONE NEW DEVELOPMENTAL CONTEXT MEMORY,
LEARN ITS DEVELOPMENTAL PRIOR,
AND LATER RECOGNIZE / REUSE THAT NEW CONTEXT,
WITHOUT CREATING DUPLICATE OR SPURIOUS CONTEXTS?

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

T6 CLAIM

A13 permits at most:

three developmental context slots total.

The inherited A and B slots are frozen known memories.

A13 may create:

exactly one additional slot C

if and only if novelty evidence satisfies the frozen discovery / learning / governance rules.

A13 does NOT permit:

unbounded context proliferation;
constitutional self-modification;
task-program mutation;
governance mutation;
provenance mutation;
automatic hidden slot creation from one surprising observation.

FROZEN PARENT

A12 accepted closure commit:

974e6731a593d7ea5ce98023c6cad9343f681f84.

A12 source SHA-256:

628c23f8319aa0e429a5c0e4dd8b0007e1346a799428c1678d33189dda10bdfd.

A12 freeze F12:

3308697f2594212be565639bc57c0179e83e831a.

A12 latent-context manifest:

502009818ea9d6e57089a91424e7cf399e7c5e95024a9623816e733c58c3f63a.

A12 accepted primary result:

8e1ec460942bd5a486bc4420c8e5e24334599d08a97bc10e385e92b938df0fda.

The A/B stored developmental priors for every scenario are reused unchanged.

HARD SLOT CAPACITY

MAX_CONTEXT_SLOTS = 3.

Initial slots:

A;
B.

Available novel slot capacity:

1.

After C is created:

no fourth slot may be created.

POST-FREEZE NOVEL PRIOR C

No primary C prior may exist before A13 freeze.

Let F13 be the exact A13 harness freeze commit.

For each scenario s:

derive:

SHA-256(
"YGG-A13-NOVEL-PRIOR|"
+ F13
+ "|"
+ decimal(s)
+ "|"
+ decimal(counter)
).

Map into the frozen 124-prior catalog.

Reject only equality with:

prior_A
or
prior_B.

No distance shaping,
difficulty shaping,
or performance shaping is allowed.

NOVELTY DISCOVERY

Known-context inference carries forward A12:

two unique symmetric observations;
exact mean comparison against all currently authorized slots.

On first C encounter:

the two-probe exact mean equals neither A nor B.

Required:

ABSTAIN.

A novel slot may NOT be created from those two probes.

MINIMUM NOVELTY DWELL

After the initial unresolved two probes,
the organism receives:

16 additional unique developmental observations

from the same unresolved niche.

These are 8 exact zero-mean pairs around latent prior C.

Thus novelty evidence consists of:

18 unique observations total

before any slot-creation proposal.

The first two discovery probes are NOT reused as training equations for the C-prior learner.

The 16 dwell observations are the C training set.

NOVELTY STABILITY REQUIREMENT

Split the 16 dwell observations into:

first 8;
second 8.

Each half must have exact arithmetic mean equal to the same valid catalog prior.

Required:

mean(first 8) == mean(second 8) == candidate_C.

If the two halves disagree:

ABSTAIN;
no slot creation.

This prevents one transient mean shift from immediately creating a context.

DISTRIBUTED NOVELTY MEMORY

The 16 C training observations are stored as distributed causal observation shards.

Each unique observation has two physical copies in separate six-cell neighborhoods.

Physical copies do not increase evidence weight.

No hidden central restore.

If every copy of one not-yet-consumed C observation is lost:

the learner must abstain.

NOVELTY LEARNERS

Two independent developmental learner lineages:

NOVEL_LEARNER_A_ROOT = 1 << 52.
NOVEL_LEARNER_B_ROOT = 1 << 53.

Each independently reconstructs the 16 unique C dwell observations from distributed memory in a separately derived post-freeze order.

Each computes:

candidate_C = exact arithmetic mean of 16 unique observations.

A candidate is valid only if:

all four role totals are divisible by 16;
candidate_C belongs to the frozen 124-prior catalog;
candidate_C differs from every existing authorized slot.

CONTEXT-SLOT AUTHORIZATION

Creation of slot C requires:

Learner A candidate == Learner B candidate;
learner roots independent;
candidate valid;
candidate novel relative to A and B;
free slot capacity == 1;
existing organism governance qualified;
existing registry qualification qualified.

The slot record contains:

slot id C;
version 1;
role prior;
parent context-table digest;
slot digest;
commit epoch.

After commit:

context-table capacity becomes full at 3.

The C slot is versioned and reversible.

PRIMARY PHASE PLAN

Each scenario has six phases:

P0:
known context A or B, post-freeze derived.

P1:
first novel C encounter:
2 unresolved probes;
16 novelty-dwell training observations;
authorize C;
then 16 held-out C service epochs.

P2:
the other known context from P0.

P3:
C return #1:
2 probes;
no C retraining;
16 held-out C service epochs.

P4:
a known A/B context derived post-freeze.

P5:
C return #2:
2 probes;
no C retraining;
16 held-out C service epochs.

The selector never receives the phase labels.

KNOWN-CONTEXT CHOICE

For P0:

derive one bit from:

SHA-256(
"YGG-A13-KNOWN-START|"
+ F13
+ "|"
+ decimal(s)
).

0 -> A.
1 -> B.

P2 uses the opposite known context.

P4 derives a fresh bit from:

SHA-256(
"YGG-A13-KNOWN-RETURN|"
+ F13
+ "|"
+ decimal(s)
).

C TRAINING OBSERVATIONS

For pair k = 0..7:

derive distinct roles a,b from:

SHA-256(
"YGG-A13-C-TRAIN|"
+ F13
+ "|"
+ decimal(s)
+ "|"
+ decimal(k)
).

Generate:

C + delta;
C - delta.

Each half of four pairs is independently zero-mean around C.

Thus:

first 8 mean = C;
second 8 mean = C;
all 16 mean = C.

HELD-OUT C SERVICE

After slot creation
and on each C return:

generate 16 service epochs
as 8 independently derived zero-mean pairs around C.

No C service observation enters the C learner.

REPLACEMENT EPISODES

Every service phase has replacements at:

service epoch 0;
service epoch 8.

Each episode replaces four clean cells.

Replacement target sets are post-freeze deterministic.

If context selection is ABSTAIN:

replacement is deferred.

After C is authorized:

C replacement cells use slot C exactly as A/B replacements use their slots.

BASELINES

BASELINE A — PERMANENT UNKNOWN

Never create C.

Whenever C occurs:

use baseline developmental prior (3,3,3,3).

BASELINE B — DUPLICATE-CONTEXT CREATOR

Create a new context slot on every unresolved C return.

This unsafe baseline reaches capacity / duplicate proliferation.

BASELINE C — ORACLE

Evaluator-only.

Knows C prior immediately and uses it from first C service phase.

PRIMARY METRICS

Per scenario report:

A prior;
B prior;
latent C prior;
initial novelty probe mean;
first-half novelty mean;
second-half novelty mean;
learner A C candidate;
learner B C candidate;
C slot creation;
slot count;
C slot digest;
C return inference results;
duplicate-slot attempts;
replacement assignments;
candidate / permanent-unknown / oracle service;
migrations;
incorrect outputs;
stale-program service;
restart equivalence.

PRIMARY REQUIRED DISCOVERY SIGNALS

12 / 12 first two C probes:

ABSTAIN relative to A/B.

12 / 12 first-half C means exact.

12 / 12 second-half C means exact.

12 / 12 learner A exact C prior.

12 / 12 learner B exact C prior.

12 / 12 learner agreement.

12 / 12 C slot creations.

Final context-slot count:

3 in every scenario.

Duplicate C slot creations:

0.

RETURN RECOGNITION

C return phases:

24 total.

24 / 24 must infer existing C slot after exactly two probes.

C retraining observations on returns:

0.

No new slot may be proposed on a recognized C return.

USEFULNESS

Across C service phases:

candidate first-four-epoch service
>
permanent-unknown baseline aggregate.

Candidate >= permanent-unknown in at least:

30 / 36 C service phases.

Candidate oracle efficiency >=:

0.97.

At least one migration avoided relative to permanent-unknown.

TASK / SAFETY

TASK_ACCURACY == 1.0.

incorrect served requests == 0.

stale-program served requests == 0.

Existing constitutional safety totals remain zero.

RESTART

Restart after 8 of 16 C dwell observations.

Required after restart:

distributed novelty memory preserved;
no C slot exists yet;
learner remains incomplete;
remaining 8 observations produce same C candidate;
C slot digest;
replacement assignments;
service metrics

match uninterrupted shadow.

DEDICATED T6 PROBES

P1 — TWO UNKNOWN PROBES ONLY

Required:

ABSTAIN;
no slot creation.

P2 — UNSTABLE NOVELTY

First 8 observations average to one valid prior.
Second 8 average to another.

Required:

ABSTAIN;
no slot creation.

P3 — DUPLICATE MEMORY FANOUT

Replicate one C observation to all cells.

Required:

candidate C unchanged.

P4 — LOST UNIQUE C OBSERVATION

Delete all copies of one not-yet-consumed C training observation.

Required:

learner incomplete;
no C slot.

P5 — ONE NOVELTY LEARNER

Only learner A returns candidate C.

Required:

no C slot.

P6 — GOVERNANCE UNAVAILABLE

Both learners agree on C.

Governance unavailable.

Required:

no C slot.

P7 — C RETURN COALESCENCE

After C exists,
return to C.

Required:

recognize existing C;
do not create C2.

P8 — SLOT CAPACITY

After A/B/C are authorized,
present another stable novel D niche.

Required:

ABSTAIN / CAPACITY-BLOCKED;
slot count remains 3.

P9 — AUTHORIZED C RETIREMENT

Evaluator-controlled reversible probe.

Authorize retirement of C.

Required:

slot count returns to 2;
A/B unchanged;
future C is again unknown until relearned.

NEGATIVE / LIMIT CONTROLS

N1 — CREATE SLOT AFTER TWO UNKNOWN PROBES

Unsafe.

Expected spurious-context creation reachable.

N2 — CREATE SLOT FROM ONE LEARNER

Unsafe.

False context authority reachable.

N3 — PHYSICAL COPY COUNT AS NOVELTY SUPPORT

Unsafe.

Replication can create false stability.

N4 — UNBOUNDED SLOT CREATION

Unsafe.

Repeated unresolved observations can proliferate contexts without limit.

N5 — COHERENTLY FORGED NOVELTY STREAM

Boundary.

If the observation stream is coherently forged to mimic a stable new niche,
the learner can create a false but internally consistent context.

PRIMARY SIGNAL

A13_T6_BOUNDED_NOVEL_CONTEXT_DISCOVERY_SUCCESS

TRUE iff:

12 / 12 first-C encounters abstain after two probes
AND
12 / 12 stable two-half novelty checks pass
AND
12 / 12 learner A exact C
AND
12 / 12 learner B exact C
AND
12 / 12 C slots authorized
AND
slot count == 3 in all scenarios
AND
duplicate C slot creations == 0
AND
24 / 24 C returns recognize existing C without retraining
AND
candidate C-service aggregate > permanent-unknown baseline
AND
candidate >= permanent-unknown in at least 30 / 36 C service phases
AND
candidate oracle efficiency >= 0.97
AND
at least one migration avoided
AND
TASK_ACCURACY == 1.0
AND
incorrect served requests == 0
AND
stale-program served requests == 0
AND
all restart comparisons equivalent
AND
all P1..P9 probes pass
AND
N1..N4 expose unsafe behavior
AND
all existing constitutional safety totals remain zero.

N5 is separately reported as an observation-truth boundary.

REPRODUCIBILITY

Two complete deterministic A13 primary sweeps.

Serialized outputs must be byte-identical.

Post-freeze:

C priors;
known-phase choices;
C training pairs;
C service pairs;
replacement targets;
restart details

must be manifest-bound before primary execution.

NO POST-RESULT TUNING

After F13 exists,
do not alter:

- three-slot hard capacity;
- 18-observation novelty dwell;
- 16-observation C training set;
- 8+8 stability check;
- novelty learner roots;
- exact-mean learner;
- slot authorization;
- C return logic;
- slot coalescence;
- retirement probe;
- baselines;
- oracle;
- thresholds;
- probes;
- controls;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

A12 can recognize environments it already remembers.

If nothing matches,
it correctly says:

"I don't know this environment."

A13 asks what happens next.

A new environment has to stay unfamiliar long enough
and produce a stable pattern before Yggdrasil may create a new developmental memory for it.

Two surprising observations are not enough.

The organism must watch the new niche,
store those experiences across its cells,
and have two independent learners derive the same new developmental prior.

Then governance still has to approve adding the new memory.

After that,
when the new niche comes back,
Yggdrasil should recognize it as the same place
instead of creating another copy.

And once A,
B,
and C fill the three allowed slots,
a fourth unknown niche cannot silently expand memory forever.

So A13 tests:

UNKNOWN EXPERIENCE
->
SAFE ABSTENTION
->
STABLE NOVELTY
->
LEARNED NEW DEVELOPMENTAL MEMORY
->
GOVERNED SLOT CREATION
->
LATER RECOGNITION / REUSE
->
NO DUPLICATE OR UNBOUNDED CONTEXT GROWTH.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A13 T6 BOUNDED NOVEL-CONTEXT DISCOVERY

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A13 C PRIOR,
NOVELTY-DWELL STREAM,
SERVICE SEQUENCE,
OR REPLACEMENT PLAN.

IMPLEMENTATION COMMIT

c25ca70bb8013f4b6671372b9c22c262baaa50bd.

SOURCE BUNDLE

Loader:

research/applications/track-a/a13_t6_novel_context_v1.py

Loader Git blob:

6b2f1cffc049a603dbcb5f4b7581d43e5a683e05.

Payload:

research/applications/track-a/a13_t6_novel_context_v1.py.gz

Payload Git blob:

a92d1a9944bd1f5c82e024b84143fe6c4ec4b40f.

Compressed payload SHA-256:

bd50f3068d0751647d4e1caa3ab8b295f8c72f0836ed93edb1e3be6c3041250d.

Compressed payload bytes:

4994.

Decompressed exact source SHA-256:

f373a8f8a60eff9c26ffe0793da844a946d8bb9916f79eb66ab9d5971cf5a561.

Decompressed source bytes:

13510.

FROZEN PARENT

A12 source SHA-256:

628c23f8319aa0e429a5c0e4dd8b0007e1346a799428c1678d33189dda10bdfd.

A12 freeze F12:

3308697f2594212be565639bc57c0179e83e831a.

A12 latent-context manifest:

502009818ea9d6e57089a91424e7cf399e7c5e95024a9623816e733c58c3f63a.

A12 accepted result:

8e1ec460942bd5a486bc4420c8e5e24334599d08a97bc10e385e92b938df0fda.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

A/B parent priors reproduced:

PASS.

Mechanical C priors distinct from A/B:

12 / 12.

Mechanical first-half 8-observation C means exact:

12 / 12.

Mechanical second-half 8-observation C means exact:

12 / 12.

Full non-primary T6 smoke used only:

MECHANICAL-NONPRIMARY-FREEZE.

Mechanical smoke summary:

12 / 12 first-C two-probe encounters abstained;
12 / 12 C priors learned exactly;
12 / 12 final slot counts = 3;
0 duplicate C slots;
24 / 24 C returns recognized without retraining;
candidate C first-four service = 1436;
permanent-unknown baseline = 1416;
evaluator oracle = 1436;
candidate >= baseline in 30 / 36 C service phases;
37 migrations avoided;
all restart checks equivalent;
all T6 probes PASS;
all unsafe controls exposed;
existing constitutional safety totals = 0.

Two pre-freeze implementation defects were caught and repaired before this freeze:

undefined local scenario references in the restart / C-commit path.

Those repairs changed only local variable references.

No primary result had been observed.

PRIMARY STATUS AT THIS FREEZE

NOT DERIVED.

Let the resulting commit SHA of this freeze update be F13.

Only after F13 exists may the harness derive:

- 12 latent C developmental priors;
- known-context phase choices;
- 16 C novelty-dwell observations per scenario;
- C service sequences;
- replacement targets.

No primary A13 novelty observation has been consumed.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-FREEZE PRIMARY T6 MANIFEST — BEFORE FIRST PRIMARY NOVELTY OBSERVATION

DATE:
2026-09-21.

FREEZE COMMIT F13

6810864daae9578da9e5de3ac59acdfc659d17d7.

NOVEL-CONTEXT MANIFEST SHA-256

920b71bd9dd01ae631ba13994e8fe83705eb1f212c708875b41087ffe8a8a5af.

LATENT C PRIORS

S00:
C (1,1,4,6).

S01:
C (5,1,4,2).

S02:
C (5,5,1,1).

S03:
C (2,1,5,4).

S04:
C (1,4,2,5).

S05:
C (1,5,2,4).

S06:
C (1,4,1,6).

S07:
C (1,3,6,2).

S08:
C (4,1,3,4).

S09:
C (4,2,1,5).

S10:
C (1,5,5,1).

S11:
C (6,1,1,4).

All C derivation counters:

0.

Every C prior differs from both inherited A and B priors.

The exact:

- known-context phase choices;
- first C probe pairs;
- 16 C novelty-dwell observations per scenario;
- C return probes;
- C service sequences;
- replacement target sets;

are fixed by F13
and bound by the manifest SHA above.

No C prior,
novelty observation,
service sequence,
or replacement target was rejected,
redrawn,
or replaced after derivation.

At the moment this manifest was recorded:

A13 primary novelty observations consumed = 0.
A13 C slots created = 0.
A13 primary service phases executed = 0.

canonical_scientific_execution = false.
stab18_r1_touched = false.
