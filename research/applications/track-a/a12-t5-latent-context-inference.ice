TITLE: YGGDRASIL TRAINING TRACK T5 / APPLICATION A12 — Latent Context Inference and Developmental Memory Selection
DATE: 2026-09-21
STATUS: PREREGISTERED / LATENT-CONTEXT DEVELOPMENTAL GATE / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T5 / APPLICATION-A
PARENT: A11 T4 Context-Conditional Developmental Memory
BRANCH: dg1a-ar

PURPOSE

A11 established that Yggdrasil can learn,
retain,
and reuse multiple developmental policies
when the current environmental context identifier is explicitly supplied.

A11's main remaining boundary is therefore:

CONTEXT IDENTITY ITSELF.

A12 asks:

CAN THE ORGANISM INFER
WHICH STORED DEVELOPMENTAL MEMORY CURRENTLY APPLIES
FROM RECENT EXPERIENCE ALONE,
WITHOUT BEING HANDED CONTEXT_A OR CONTEXT_B?

And:

CAN IT ABSTAIN WHILE THE EVIDENCE IS INSUFFICIENT
RATHER THAN GUESSING A DEVELOPMENTAL POLICY?

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

T5 CLAIM

A12 does not learn new developmental priors.

It uses the already-established two-slot developmental-memory architecture from A11.

A12 trains/tests:

latent context recognition;
safe developmental-memory selection;
abstention under ambiguity.

It does NOT permit:

new context-slot creation;
constitutional self-modification;
task-program mutation;
governance mutation;
provenance mutation;
repair-authority mutation.

FROZEN PARENT

A11 accepted closure commit:

b26595bd740a8414546e4832a7ee6e2431bec393.

A11 source SHA-256:

a45e4b74b0d2f2c8981da7f94bde4e9072048109226854a881162ecb47f9d235.

A11 freeze F11:

77874019c9f8cc8716873161f920e249a07ec4fa.

A11 context-development manifest:

b0e00f29d36637a1365ab2407678aacf232ac4f4cf05d387f68af975a5b4bedd.

A11 primary result SHA-256:

21e3ae20cad080cd65c138722d96079f27c6d2d4479fd3506f2dd40c06f32c05.

The A11 learned A/B role priors for each scenario are reused unchanged.

No A12 evaluator may replace or modify those priors.

HIDDEN CONTEXT

The organism has two stored slots:

A;
B.

During A12 primary evaluation:

the environment does NOT supply the slot name.

For each phase,
the evaluator knows:

hidden_context in {A,B}.

The developmental selector does not.

The selector may receive only:

recent observed demand vectors;
the two already-authorized stored developmental priors.

It may NOT receive:

phase index;
F12;
hidden sequence;
future demand;
replacement plan;
evaluator context label;
oracle selection.

POST-FREEZE HIDDEN CONTEXT SEQUENCE

Let F12 be the exact A12 harness freeze commit.

Each scenario contains:

6 hidden-context phases.

For scenario s and counter c:

derive six context bits from:

SHA-256(
"YGG-A12-HIDDEN-CONTEXTS|"
+ F12
+ "|"
+ decimal(s)
+ "|"
+ decimal(c)
).

Map each selected bit:

0 -> A;
1 -> B.

Accept the six-phase sequence only if:

both A and B appear
AND
the sequence contains at least 3 context switches.

Otherwise increment counter.

This rejection rule is frozen before F12.

No difficulty shaping beyond the explicit switch-count requirement is allowed.

CONTEXT PROBE OBSERVATIONS

At the start of each hidden phase,
before any replacement event,
the organism receives exactly:

2 context-probe demand observations.

For scenario s,
phase q,
hidden prior p:

derive distinct roles a,b from:

SHA-256(
"YGG-A12-CONTEXT-PROBE|"
+ F12
+ "|"
+ decimal(s)
+ "|"
+ decimal(q)
).

Let:

delta[a] = +1;
delta[b] = -1;
all others = 0.

Probe 0:

p + delta.

Probe 1:

p - delta.

Therefore:

(probe0 + probe1) / 2 = p.

The selector is not told this hidden p.

INFERENCE RULE

The selector keeps a phase-local observation buffer.

Before 2 unique probe observations exist:

ABSTAIN.

After exactly 2 unique probe observations:

compute exact arithmetic mean by role.

Compare that mean to the two stored developmental priors.

If the mean equals exactly one stored prior:

select that slot.

If it equals neither:

ABSTAIN.

If it equals both:

ABSTAIN.

A11 guarantees A prior != B prior in every scenario,
so correct primary probes should identify one unique slot.

No nearest-neighbor,
rounding,
or forced tie-break is allowed.

CONTEXT-INFERENCE MEMORY

Probe observations are stored as causal observation records.

Duplicate physical copies do not count as additional observations.

The phase-local inference buffer resets at phase transition.

The authorized developmental slots do not reset.

SERVICE EVALUATION

After context inference,
each phase runs:

16 held-out service epochs.

The exact sequence is generated as 8 exact zero-mean demand pairs
around the hidden prior.

For scenario s,
phase q,
pair k:

derive distinct a,b from:

SHA-256(
"YGG-A12-SERVICE-PAIR|"
+ F12
+ "|"
+ decimal(s)
+ "|"
+ decimal(q)
+ "|"
+ decimal(k)
).

Use:

p + delta;
p - delta.

No service demand is exposed before inference.

REPLACEMENT EPISODES

Within each 16-epoch service phase:

replacement episode at service epoch 0;
replacement episode at service epoch 8.

Each episode replaces exactly four clean cells.

Targets derived from:

SHA-256(
"YGG-A12-REPLACEMENT|"
+ F12
+ "|"
+ decimal(s)
+ "|"
+ decimal(q)
+ "|"
+ decimal(episode)
).

Replacement cells:

inherit no role;
inherit no developmental probe observation;
inherit no stale training memory;
inherit only the current authoritative task program after role selection.

If context inference is ABSTAIN:

replacement is deferred until a context is selected.

Primary probes should resolve before service epoch 0.

BASELINES

BASELINE A — STICKY LAST CONTEXT

Use the developmental policy selected in the previous phase.

For phase 0:

use baseline prior (3,3,3,3).

The baseline does not inspect context probes.

This represents failure to recognize environmental change.

BASELINE B — RANDOM SLOT

Evaluator-only deterministic unsafe baseline.

Choose A/B from one post-freeze hash bit per phase.

BASELINE C — ORACLE CONTEXT

Evaluator-only.

Receives hidden context immediately.

Uses the correct stored prior.

This is the ceiling.

PRIMARY METRICS

Per scenario / phase report:

hidden context;
probe vectors;
inferred context;
inference latency;
abstentions;
selected policy digest;
replacement targets;
replacement role assignments;
candidate first-four-epoch service;
sticky-baseline first-four-epoch service;
oracle first-four-epoch service;
candidate migrations;
sticky-baseline migrations;
incorrect outputs;
stale-program service.

PRIMARY INFERENCE REQUIREMENTS

72 / 72 hidden phases inferred correctly.

0 incorrect context selections.

Inference latency:

exactly 2 probe observations in all primary phases.

No replacement event occurs before successful inference.

CONTEXT-SWITCH REQUIREMENTS

Every scenario:

both A and B present.

Every scenario:

at least 3 switches.

At least one scenario:

contains A -> B -> A.

At least one scenario:

contains B -> A -> B.

USEFULNESS REQUIREMENTS

Across all hidden phases:

candidate first-four-epoch service
>
sticky-last-context baseline aggregate.

Candidate service >= sticky baseline in at least:

60 / 72 phases.

Candidate oracle efficiency >=:

0.98.

At least one migration avoided relative to sticky baseline.

TASK / SAFETY

TASK_ACCURACY == 1.0.

incorrect served requests == 0.

stale-program served requests == 0.

Existing constitutional safety totals remain zero.

RESTART

Run one restart after probe 0
and before probe 1
in one derived phase per scenario.

Required:

the single remembered probe survives;
the selector remains ABSTAIN after restart until probe 1 arrives;
the final inferred context,
replacement assignments,
service outputs,
and metrics
match uninterrupted shadow exactly.

DEDICATED T5 PROBES

P1 — ONE PROBE ONLY

Supply probe 0 only.

Required:

ABSTAIN.

P2 — EXACT TWO-PROBE IDENTIFICATION

Supply the valid symmetric pair.

Required:

select correct stored slot.

P3 — DUPLICATE FIRST PROBE

Replicate probe 0 many times.

Required:

still only one unique observation;
ABSTAIN.

P4 — UNKNOWN NICHE

Supply two observations whose exact mean equals neither A nor B prior.

Required:

ABSTAIN.

P5 — AMBIGUOUS MEMORY

Evaluator-only control where both stored slots are temporarily made identical.

Required:

ABSTAIN.

P6 — CONTEXT SWITCH

Finish one phase under A,
then begin B.

Required:

phase-local probe buffer resets;
prior A remains stored;
no assumption that previous slot remains active.

P7 — RESTART MID-INFERENCE

Restart after first unique probe.

Required:

one-probe state survives;
still ABSTAIN;
second probe completes same inference as uninterrupted shadow.

P8 — NO FORCED EXISTING-CELL REWRITE

Selecting a new context slot must not rewrite roles of existing cells.

Only clean replacements use newly selected developmental memory.

NEGATIVE / LIMIT CONTROLS

N1 — STICKY LAST CONTEXT

Expected performance loss on context switches.

N2 — FORCE GUESS AFTER ONE PROBE

Unsafe.

A single perturbed observation need not uniquely identify the context.

Expected false context selection reachable.

N3 — NEAREST-PRIOR GUESS FOR UNKNOWN NICHE

Unsafe.

Expected incorrect reuse of a known developmental memory
when the current niche is actually unknown.

N4 — FORGED CONTEXT PROBE

Boundary.

If the observation stream itself is coherently forged
to have the exact mean of the wrong stored prior,
the selector can choose the wrong context.

This is an observation-truth boundary.

N5 — NEW THIRD CONTEXT

Boundary.

A12 must ABSTAIN.

It may not create a third developmental slot.

PRIMARY SIGNAL

A12_T5_LATENT_CONTEXT_INFERENCE_SUCCESS

TRUE iff:

72 / 72 phases inferred correctly
AND
0 incorrect context selections
AND
all primary inference latencies == 2
AND
no replacement occurs before inference
AND
candidate aggregate first-four service > sticky baseline
AND
candidate >= sticky baseline in at least 60 / 72 phases
AND
candidate oracle efficiency >= 0.98
AND
at least one migration is avoided
AND
TASK_ACCURACY == 1.0
AND
incorrect served requests == 0
AND
stale-program served requests == 0
AND
all restart comparisons equivalent
AND
all P1..P8 probes pass
AND
N1..N3 expose unsafe behavior as preregistered
AND
all existing constitutional safety totals remain zero.

N4 and N5 are separately reported boundaries.

REPRODUCIBILITY

Two complete deterministic A12 primary sweeps.

Serialized outputs must be byte-identical.

Post-freeze:

hidden context sequences;
probe pairs;
service sequences;
restart phases;
replacement targets

must be manifest-bound before primary execution.

NO POST-RESULT TUNING

After F12 exists,
do not alter:

- six phases;
- minimum three switches;
- two-probe inference rule;
- exact-mean equality;
- phase-local inference reset;
- stored A/B developmental priors;
- service sequence;
- replacement schedule;
- baselines;
- oracle;
- thresholds;
- probes;
- controls;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

A11 could remember two developmental habits,
but somebody still had to tell it:

"we are in A now"

or

"we are in B now."

A12 removes that label.

At the beginning of each phase,
Yggdrasil sees what the environment is asking for.

After one observation,
it is not allowed to guess.

After two complementary observations,
it can compare the observed pattern with the developmental memories it already knows.

If exactly one old developmental memory matches,
it activates that one.

If nothing matches,
it waits.

Then clean replacement cells use the selected developmental memory.

So the new chain is:

EXPERIENCE
->
INFER CURRENT NICHE
->
SELECT STORED DEVELOPMENTAL MEMORY
->
FUTURE CELLS DEVELOP APPROPRIATELY.

This is the first step where the organism chooses its own developmental context
instead of being handed the context label.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A12 T5 LATENT CONTEXT INFERENCE

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A12 HIDDEN CONTEXT SEQUENCE,
PROBE PAIR,
SERVICE SEQUENCE,
RESTART PHASE,
OR REPLACEMENT PLAN.

IMPLEMENTATION COMMIT

c1d281dbacfeafd6ed2f859e2845b67ae5894672.

SOURCE BUNDLE

Loader:

research/applications/track-a/a12_t5_latent_context_inference_v1.py

Loader Git blob:

55dfab23b8331ef1f52dd514bc5c8127fc05ee02.

Payload:

research/applications/track-a/a12_t5_latent_context_inference_v1.py.gz

Payload Git blob:

2efd6e324211d734717f33aa3cda11e435f239dc.

Compressed payload SHA-256:

1897e52ea301bb980480a9970e1ac3385d7c8eb8ca62bd1eab9afcca7cf55e9d.

Compressed payload bytes:

4539.

Decompressed source SHA-256:

628c23f8319aa0e429a5c0e4dd8b0007e1346a799428c1678d33189dda10bdfd.

Decompressed source bytes:

12683.

FROZEN PARENT

A11 source SHA-256:

a45e4b74b0d2f2c8981da7f94bde4e9072048109226854a881162ecb47f9d235.

A11 freeze F11:

77874019c9f8cc8716873161f920e249a07ec4fa.

A11 context-development manifest:

b0e00f29d36637a1365ab2407678aacf232ac4f4cf05d387f68af975a5b4bedd.

A11 accepted result SHA-256:

21e3ae20cad080cd65c138722d96079f27c6d2d4479fd3506f2dd40c06f32c05.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Scenarios:

12.

Hidden phases:

72.

Every mechanical scenario:

contains both A and B
and at least 3 switches.

One-probe inference:

ABSTAIN.

Two-probe exact-mean inference:

correct unique slot.

Full non-primary T5 smoke used only:

MECHANICAL-NONPRIMARY-FREEZE.

Mechanical smoke summary:

72 / 72 phases inferred correctly;
0 incorrect context selections;
all inference latencies = 2;
no replacement before successful inference;
candidate first-four service = 2908;
sticky-context baseline = 2843;
evaluator oracle = 2908;
candidate >= sticky baseline in 67 / 72 phases;
candidate > sticky baseline in 32 / 72 phases;
81 migrations avoided;
all restart checks equivalent;
all T5 probes PASS;
unsafe one-probe / nearest-prior controls exposed;
existing constitutional safety totals = 0.

These outcomes use a fake mechanical freeze label only.

They are implementation checks.

They are NOT A12 scientific evidence.

PRIMARY STATUS AT THIS FREEZE

NOT DERIVED.

Let the resulting commit SHA of this freeze update be F12.

Only after F12 exists may the harness derive:

- 12 six-phase hidden context sequences;
- 72 two-observation context probes;
- 72 held-out service sequences;
- 12 restart phases;
- 144 replacement target sets.

No primary A12 context observation has been consumed.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
