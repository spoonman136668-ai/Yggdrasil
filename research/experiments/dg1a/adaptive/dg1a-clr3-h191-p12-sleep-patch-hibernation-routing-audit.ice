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
