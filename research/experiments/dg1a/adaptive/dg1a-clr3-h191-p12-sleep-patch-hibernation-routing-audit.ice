TITLE: DG-1A-CLR3-H191-P12 — Sleep-Time Patch Hibernation / Conditional Activation Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE SLEEP-ROUTING PILOT / NOT H191 PRIMARY
TRACK: DG-1 / SLEEP HIBERNATION / CONDITIONAL PATCH ACTIVATION
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p11-sleep-patch-consolidation-merge-audit.ice

PURPOSE

P11 established:

- the sleep reconstruction path is mechanically valid;
- accumulated developmental patch factors are NOT safely compressible
  into one smaller globally shared fixed-dictionary basis;
- patch reuse therefore does NOT imply global mergeability.

P12 asks:

CAN:
THE:
FULL:
DEVELOPMENTAL:
PATCH GEOMETRY

REMAIN:
STORED

WHILE:

EACH:
CAPABILITY

ACTIVATES:
ONLY:
THE:
SMALL:
SUBSET:
OF:
PATCH FACTORS
IT:
ACTUALLY:
NEEDS?

BOUNDARY

NON-EVIDENCE synthetic sleep-routing pilot only.

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

PRE-SLEEP ORGANISM

Exact P11 developmental precursor:

- CORE3;
- P8-style in-distribution additions 3..7;
- P10-style OOD8..OOD11 additions.

Thus:

the final pre-sleep organism contains:

- 8 immutable CORE3 factors;
- P accumulated developmental patch factors;
- capability decoders frozen at birth-time support.

SLEEP INPUT

For each capability:

sleep receives ONLY:

- distillation coordinates;
- frozen pre-sleep predictions;
- fixed geometry metadata.

Sleep does NOT receive:

- task labels;
- original task targets;
- held-out task targets;
- acceptance labels.

IMMUTABLE STRUCTURE

The following remain exactly frozen:

- all 8 CORE3 factor IDs;
- all CORE3 scale slots;
- all P developmental patch factor IDs;
- all patch scale slots;
- all core decoder coefficients.

P12 performs:

NO:
factor deletion.

NO:
factor replacement.

NO:
factor movement.

NO:
new factor creation.

Thus:

shared geometry count
is:
identical
before
and:
after sleep.

PATCH TARGET

For each capability T:

pre_sleep_prediction_T(x)
=
fixed_core_T(x)
+
patch_contribution_T(x).

Sleep reconstructs:

patch_contribution_T(x)

from:

pre_sleep_prediction_T(x)
-
fixed_core_T(x).

The fixed core:

never changes.

GLOBAL PATCH POOL

Every capability may choose from:

the final:
P-factor:
developmental patch pool.

This includes:

patches that were learned
after:
that capability's birth.

A later patch
may therefore become:

a reusable:
sleep-time feature

for:
an earlier capability

only if:
it improves:
prediction-state reconstruction.

This changes:

routing metadata
and:
patch decoder coefficients,

not:
shared geometry.

SLEEP_ALPHA

1e-9.

ACTIVE_ZERO THRESHOLD

absolute coefficient:

>1e-12.

CONTROL

ORIGINAL_BIRTH_RECODE

For each capability:

use:
exactly:
the patch factors
that were active
when:
that capability
was frozen.

Refit ONLY:

patch coefficients

from:
pre-sleep prediction state.

Core coefficients:

unchanged.

Control gate:

median:
world-worst:
held-out prediction mismatch

<=1e-10.

If:
control fails,

P12 is:
MECHANICALLY INVALID.

CONDITIONAL ROUTING

For each capability independently:

greedily recruit:

a nested:
patch-factor sequence

from:
the:
final global:
P-factor patch pool.

Scoring uses ONLY:

that capability's:
distillation:
patch-contribution:
reconstruction mismatch.

Tie:

global patch-pool order.

No:
cross-capability:
shared routing constraint.

BUDGETS PER CAPABILITY

Let:

B_T

be:
the number:
of:
birth-time:
patch factors

for:
capability T.

HALF_ACTIVE

If:
B_T = 0:

K_T = 0.

If:
B_T >0:

K_T
=
max(
1,
floor(B_T/2)
).

MINUS1_ACTIVE

K_T
=
max(
0,
B_T - 1
).

Thus:

the budgets are:
capability-specific.

A capability
with:
no:
pre-sleep patch state

cannot:
gain:
active:
patch compute
during:
sleep.

ROUTING FIT

After:
selecting:
K_T patch factors,

fit:
only:
their:
patch coefficients

using:
SLEEP_ALPHA.

Core coefficients:

remain:
exactly:
unchanged.

HELD-OUT EVALUATION

Held-out task targets
are:
never:
used:
during:
routing.

After:
the routing state
is frozen,

measure:

normalized:
prediction mismatch

against:
the:
pre-sleep:
held-out prediction.

Also report:

task-target:
held-out NMSE delta

as:
diagnostic telemetry only.

No:
task target
may:
affect:
routing,
budget,
or:
classification.

STRUCTURE / MEMORY

Shared patch geometry:

unchanged:
P factors.

Report:

- P patch IDs;
- P scale slots;
- per-capability:
  pre-sleep:
  active patch count;
- post-sleep:
  active patch count;
- total:
  pre-sleep:
  patch decoder scalars;
- total:
  post-sleep:
  stored active patch coefficients;
- routing:
  index-count metadata;
- active-count reduction fraction.

ACTIVE COMPUTE

Per capability:

16:
CORE3 operations

+
2 *:
active patch-factor count.

Report:

- oldest capability ops;
- median capability ops;
- newest capability ops;
- total:
  active patch evaluations
  across:
  all capabilities;
- reduction:
  versus:
  pre-sleep.

WORLD FAMILY

6:
disjoint worlds.

Seeds:

20260925300000
through:
20260925300005.

No:
P0-P11
seed reuse.

PRIMARY METRICS

For:

ORIGINAL_BIRTH_RECODE,
HALF_ACTIVE,
MINUS1_ACTIVE:

- capability-median:
  held-out prediction mismatch;
- world-mean:
  held-out prediction mismatch;
- world-worst:
  held-out prediction mismatch;
- P90:
  world-worst mismatch;
- distillation mismatch;
- task-target:
  NMSE delta;
- total:
  active patch coefficients;
- total:
  active patch evaluations;
- oldest:
  median:
  newest:
  capability ops;
- active patch-count reduction fraction.

Also report:

- fraction:
  of capabilities
  whose:
  routed subset
  contains:
  at least one:
  patch learned:
  after:
  that capability's birth;

- fraction:
  of routed patch selections
  that:
  are:
  later-born:
  cross-capability reuse.

HALF_ACTIVE STRONG SUPPORT

If:
control passes,

HALF_ACTIVE is:

STRONG HIBERNATION

if:

1.
median:
world-mean:
held-out prediction mismatch
<=0.01;

2.
median:
world-worst:
held-out prediction mismatch
<=0.02;

3.
P90:
world-worst mismatch
<=0.05;

4.
median:
active patch-count reduction
>=40%;

5.
core decoder change
=
0;

6.
median:
total:
active patch evaluations
decreases
versus:
pre-sleep;

7.
median:
newest capability:
active compute
does NOT:
increase.

MINUS1_ACTIVE SUPPORT

If:
HALF_ACTIVE
does not:
pass,

MINUS1_ACTIVE is:

USEFUL HIBERNATION

if:

1.
median:
world-mean mismatch
<=0.01;

2.
median:
world-worst mismatch
<=0.02;

3.
median:
active patch-count reduction
>0;

4.
core decoder change
=
0;

5.
median:
total:
active patch evaluations
decreases.

NEGATIVE

If:
control passes
but:
neither:
HALF_ACTIVE
nor:
MINUS1_ACTIVE
meets:
its:
frozen support criteria,

conclude:

the:
current:
patch factors
must:
remain:
largely:
active
for:
prediction-state preservation

under:
this:
conditional-routing mechanism.

REPRODUCIBILITY

Two:
complete:
6-world:
development-plus-routing sweeps.

Canonical output bytes
must:
match exactly.

NO POST-RUN TUNING

After:
the first P12 world,

do not alter:

- developmental rules;
- global patch pool;
- routing candidate pool;
- sleep alpha;
- active-zero threshold;
- HALF_ACTIVE budgets;
- MINUS1_ACTIVE budgets;
- core immutability;
- world family;
- metrics;
- thresholds.

NEXT

If:
HALF_ACTIVE
receives:
strong support,

the next experiment should:

combine:
conditional patch hibernation

with:
a:
small:
dynamic:
software-cell /
ReCA:
router

that predicts:
which:
stored patch subset
to:
wake
from:
local:
state.

If:
only:
MINUS1_ACTIVE
works,

test:
gradual:
one-factor:
hibernation
across:
repeated:
sleep cycles.

If:
P12 is:
negative,

retain:
birth-time:
active support
and:
move:
the:
ReCA research line
to:
temporal:
memory substrate
rather than:
patch routing.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P12 CONDITIONAL PATCH HIBERNATION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P12 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p12_sleep_patch_hibernation_routing_v1.py

Harness commit:

141509179e9c6c91c38e36509ffd27b0734f2372.

Git blob SHA:

37086c14a28ef5ae7085463e154f1efc4f4f203f.

Source SHA-256:

17585ed7fcbc2411393e02e8c9f9da1db9f2a6783b4e2e10829f3e9bee055296.

Source bytes:

13614.

DEPENDENCIES

H191-P11 harness Git blob:

ec1ee8e3a53dd68166dd6c9cdc486a20d3dde956.

H191-P11 source SHA-256:

923a055bbd840f681aeeea33351e4124dbae2340587d59f17a256275c80efa69.

H191-P10 harness Git blob:

736e78364340dd355a8ecd163a2deef29edf1a2a.

H191-P10 source SHA-256:

9efde966ddf02c4695462af2959555098edfdcc447e6c5c95e26c86c9540d8b4.

LOCAL EXECUTION PRECHECK

P10,
P11,
and:
P12

execution copies
were:
verified
against:
their:
Git blob identities.

P12:
Python compile:

PASS.

No:
P12 experimental world
was:
executed
before:
this freeze.

FROZEN WORLD FAMILY

20260925300000..20260925300005.

6 worlds.

GLOBAL PATCH POOL

Final:
developmental:
post-CORE3:
patch geometry.

No:
geometry deletion.

No:
new:
geometry creation.

Routing is:
per-capability.

SLEEP_ALPHA:

1e-9.

ACTIVE_ZERO:

1e-12.

REPRODUCIBILITY

Execute:
two complete:
6-world:
development-plus-routing sweeps.

Canonical output SHA-256
must:
match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
