TITLE: DG-1A-CLR3-H191-P11 — Sleep-Time Patch Consolidation / Merge Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE SLEEP-CONSOLIDATION PILOT / NOT H191 PRIMARY
TRACK: DG-1 / SLEEP CONSOLIDATION / DEVELOPMENTAL PATCH COMPRESSION
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p10-repeated-ood-elastic-patch-reuse-audit.ice

PURPOSE

P8 established:
development can accumulate shared micropatches.

P10 established:
later related OOD capabilities can often reuse
the already-developed shared geometry,
so patch growth is not inherently one-for-one.

P11 asks:

CAN:
THE:
ACCUMULATED:
POST-CORE3:
PATCH FACTORS

BE:
MERGED:
DURING:
SLEEP

INTO:
FEWER:
SHARED:
FIXED-DICTIONARY FACTORS

WITHOUT:
MATERIALLY:
CHANGING:
ANY:
WAKING:
CAPABILITY PREDICTION?

BOUNDARY

NON-EVIDENCE synthetic sleep-consolidation pilot only.

No:
accepted H190 parent.
No:
H191 acceptance claim.
No:
living tissue.
No:
wetware.
No:
production modification.
No:
canonical scientific execution.
No:
STAB-18-R1 execution.

DEVELOPMENTAL PRE-SLEEP ORGANISM

Each world first develops:

- CORE3;
- in-distribution capabilities 3..7
  under the exact P8 trigger rule;
- OOD8..OOD11
  under the exact P10 repeated-OOD rule.

Thus:
the pre-sleep organism contains:

- 8 original CORE3 factors;
- zero or more accumulated developmental patch factors;
- capability decoders frozen at their birth-time supports.

SLEEP INPUT

Sleep consolidation receives ONLY:

- capability distillation coordinates;
- the frozen PRE-SLEEP PREDICTIONS
  produced by each capability on those coordinates;
- fixed factor geometry metadata.

It does NOT receive:

- original task labels;
- original target functions;
- held-out targets;
- capability acceptance labels.

Therefore:

P11 is prediction-state distillation,
not functional replay.

IMMUTABLE CORE

The original 8 CORE3 factors:

must remain:
exactly unchanged.

For every capability:

its coefficients on:
the original 8 CORE3 factors

must remain:
exactly unchanged.

Sleep may change ONLY:

the representation
of:
the post-CORE3 patch contribution.

PRE-SLEEP PATCH SET

Let:

P

be:
the number:
of:
unique:
post-CORE3:
patch factors
in:
the fully developed organism.

These factors are:

the final shared support
minus:
the original:
8 CORE3 factors.

If:

P < 2,

the world is:
NON-COMPRESSIBLE
for:
primary merge evaluation

but:
must still be:
reported.

CONSOLIDATION TARGET

For each capability T:

pre_sleep_prediction_T(x)
=
fixed_core_T(x)
+
old_patch_contribution_T(x).

During sleep:

fixed_core_T(x)

is:
held fixed.

The consolidation learner sees:

old_patch_contribution_T(x)

only through:

pre_sleep_prediction_T(x)
-
fixed_core_T(x).

No:
task target
is exposed.

FIXED CONSOLIDATION DICTIONARY

Same:
parent-center
x
fixed-scale dictionary:

3209 centers
x
sigma:
0.22,
0.44,
0.88.

Exclude:

the:
8 original:
CORE3 factor candidates.

Old patch factors:

remain:
eligible.

Other:
fixed-dictionary factors

are:
also eligible.

No:
new learned center.
No:
new learned sigma.
No:
new physical cell.

SLEEP FIT

Use:

SLEEP_ALPHA = 1e-9.

Reason:

sleep is:
state reconstruction,
not:
noisy task fitting.

Joint recruitment:

choose:
one:
shared:
consolidated patch-factor sequence

across:
all 12:
capabilities.

At:
each factor:

minimize:
mean:
capability-normalized:
distillation mismatch

between:

fixed core
+
current:
consolidated patch prediction

and:

frozen:
pre-sleep prediction.

Tie:

candidate order.

Nested:
consolidation prefixes
are:
used.

BUDGETS

For:
compressible worlds
with:
P >=2:

HALF

K_half
=
max(
1,
floor(P/2)
).

MINUS1

K_minus1
=
P - 1.

Thus:

HALF asks:
for:
at least:
50% patch-geometry compression

when:
P is even

and:
strong compression
generally.

MINUS1 asks:

whether:
even:
one:
patch factor
can:
be removed
without:
meaningful:
prediction loss.

CONTROL — ORIGINAL_PATCH_RECODE

Use:
the original:
P:
patch factors

with:
the same:
fixed core.

Refit:
only:
patch coefficients

from:
pre-sleep predictions.

This control must:
reproduce:
the pre-sleep:
patch state

to:
floating-point:
distillation accuracy.

It validates:
the:
sleep-target:
reconstruction path.

HELD-OUT EVALUATION

Held-out TASK TARGETS
are NOT:
used:
during sleep.

After:
the sleep representation
is frozen,

evaluate:

prediction mismatch
against:
the:
pre-sleep:
held-out predictions.

Metric:

normalized prediction MSE

=
MSE(
post_sleep_prediction,
pre_sleep_prediction
)
/
Var(
pre_sleep_prediction
).

Report:
per capability,
world mean,
world worst.

Also report:

actual:
task-target:
held-out NMSE
before
and:
after sleep

as:
NON-TRAINING:
diagnostic telemetry only.

No:
held-out task target
may:
affect:
recruitment,
budget choice,
or:
acceptance classification.

MEMORY / STRUCTURE

Report:

PRE-SLEEP:

- patch factor count P;
- patch site IDs P;
- patch scale slots P;
- total patch decoder scalars
  actually stored
  across:
  capability birth-time supports.

POST-SLEEP:

for:
HALF
and:
MINUS1:

- consolidated patch factors K;
- patch site IDs K;
- patch scale slots K;
- total consolidated patch decoder scalars;
- geometry reduction fraction;
- decoder-state change fraction.

ACTIVE COMPUTE

Per capability:

PRE-SLEEP:

2 * birth-time:
active factor count.

POST-SLEEP:

16:
core operations

+
2 *:
number:
of:
nonzero:
consolidated patch coefficients

using:
absolute coefficient:
>1e-12
as:
the frozen:
active-zero threshold.

Report:

- oldest capability ops;
- median capability ops;
- newest capability ops;
- change versus pre-sleep.

PRESERVATION

Core factor IDs:

unchanged.

Core scale slots:

unchanged.

Core decoder coefficients:

maximum absolute change:

must be:
0.

No:
old factor:
is:
mutated.

Consolidation creates:

a:
new:
sleep patch representation.

It does NOT:
rewrite:
the:
original:
CORE3 semantics.

WORLD FAMILY

6:
disjoint worlds.

Seeds:

20260925200000
through:
20260925200005.

No:
P0-P10
seed reuse.

PRIMARY METRICS

For:
ORIGINAL_PATCH_RECODE,
HALF,
MINUS1:

- median:
  held-out prediction mismatch
  across capabilities;

- median:
  world mean mismatch;

- median:
  world worst mismatch;

- P90:
  world worst mismatch;

- distillation prediction mismatch;

- task-target:
  held-out NMSE delta
  versus:
  pre-sleep;

- total patch decoder scalars;

- shared patch geometry count;

- per-capability active compute.

CONTROL GATE

ORIGINAL_PATCH_RECODE:

median:
world worst:
held-out prediction mismatch

<=1e-10.

If:
this fails:

P11 is:
MECHANICALLY INVALID

because:
the sleep reconstruction path
cannot:
reproduce:
the original patch state.

HALF CONSOLIDATION SUPPORT

On:
compressible worlds:

HALF is:
STRONG CONSOLIDATION

if:

1.
median:
world mean:
held-out prediction mismatch
<=0.01;

2.
median:
world worst:
held-out prediction mismatch
<=0.02;

3.
P90:
world worst mismatch
<=0.05;

4.
median:
patch geometry reduction
>=40%;

5.
core decoder change
=
0;

6.
median:
newest-capability:
active compute
does NOT:
increase
versus:
pre-sleep.

MINUS1 CONSOLIDATION SUPPORT

If:
HALF
does not:
pass,

MINUS1 is:
USEFUL CONSOLIDATION

if:

1.
median:
world mean mismatch
<=0.01;

2.
median:
world worst mismatch
<=0.02;

3.
core decoder change
=
0;

4.
median:
geometry reduction
>0.

NEGATIVE

If:

control passes

but:

neither:
HALF
nor:
MINUS1

meets:
its:
frozen support criteria,

conclude:

the:
accumulated:
patch geometry

is:
not:
compressible
under:
this:
fixed-dictionary:
prediction-distillation mechanism.

REPRODUCIBILITY

Two:
complete:
6-world:
development-plus-sleep sweeps.

Canonical output bytes
must:
match exactly.

NO POST-RUN TUNING

After:
the first P11 world,

do not alter:

- developmental rules;
- sleep alpha;
- core immutability;
- candidate dictionary;
- HALF budget;
- MINUS1 budget;
- active-zero threshold;
- world family;
- metrics;
- thresholds.

NEXT

If:
HALF
receives:
strong support,

proceed to:

repeated:
wake-learn-sleep cycles

and:
test:
whether:
patch growth remains:
bounded
across:
multiple:
development/consolidation epochs.

If:
only:
MINUS1
works,

test:
gradual:
one-factor-at-a-time:
sleep compaction.

If:
consolidation is:
negative,

retain:
micropatches
and:
investigate:
factor:
sharing metadata
or:
conditional:
activation
rather than:
factor merging.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P11 SLEEP PATCH CONSOLIDATION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P11 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p11_sleep_patch_consolidation_v1.py

Harness commit:

7d0d8ffb0c989ebe5beeda6fafb6c06fd8870849.

Git blob SHA:

ec1ee8e3a53dd68166dd6c9cdc486a20d3dde956.

Source SHA-256:

923a055bbd840f681aeeea33351e4124dbae2340587d59f17a256275c80efa69.

Source bytes:

23460.

DEPENDENCY

Frozen H191-P10 harness Git blob:

736e78364340dd355a8ecd163a2deef29edf1a2a.

Pinned P10 source SHA-256:

9efde966ddf02c4695462af2959555098edfdcc447e6c5c95e26c86c9540d8b4.

LOCAL EXECUTION PRECHECK

The execution copies were verified against:
the exact Git blob SHA
for:
both:
P10
and:
P11.

P11:
Python compile:

PASS.

No:
P11 experimental world
was:
executed
before:
this freeze.

FROZEN NORMALIZATION DETAIL

Capability-normalized:
sleep recruitment mismatch

uses:

MSE(
candidate post-sleep prediction,
frozen pre-sleep prediction
)

divided by:

Var(
frozen pre-sleep prediction
)
+
1e-12.

This:
prevents:
near-zero:
patch residual variance

from:
overweighting:
a capability

while:
keeping:
the metric
anchored
to:
actual:
waking-state distortion.

FROZEN WORLD FAMILY

20260925200000..20260925200005.

6 worlds.

SLEEP_ALPHA:

1e-9.

ACTIVE_ZERO threshold:

1e-12.

REPRODUCIBILITY

Execute:
two complete:
6-world:
development-plus-sleep sweeps.

Canonical output SHA-256
must:
match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
