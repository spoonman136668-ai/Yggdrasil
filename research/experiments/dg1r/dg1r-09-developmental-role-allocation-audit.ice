TITLE: DG-1R-09 — Developmental Role Allocation / Specialization Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE ROLE-SPECIALIZATION PILOT
TRACK: DG-1R / SOFTWARE CELLS / DEVELOPMENTAL SPECIALIZATION
BRANCH: dg1a-ar
PARENT: DG-1R-08
PARENT_CLOSURE: e012a79d6049d1c9b1593ff389d02390532a97ab

PURPOSE

DG-1R-08 established:

- 103 dynamic workers + 25 maintenance bits preserve perfect tested repair;
- the additional 39 workers increase median worker-state feature rank by 59.3%;
- current memory / nonlinear task scores remain essentially unchanged.

Therefore:

the bottleneck is:

UTILIZATION
of:
the:
larger:
state space,

not:
raw:
worker count.

DG-1R-09 asks:

CAN:
A:
LABEL-FREE:
DEVELOPMENTAL:
PHASE

ASSIGN:
DIFFERENT:
WORKER:
ROLES

SO THAT:

THE:
EXTRA:
REPRESENTATIONAL:
HEADROOM

BECOMES:

FUNCTIONAL:
TASK:
CAPABILITY

WITHOUT:

SACRIFICING:
THE:
FIVE-STRIPE:
SELF-REPAIR:
GUARANTEE?

BOUNDARY

Synthetic software-only experiment.

No:
living tissue.
No:
wetware.
No:
biological implementation.
No:
production modification.
No:
canonical H191 execution.
No:
STAB-18-R1 execution.

PERSISTENT STATE

128 bits.

All primary methods:

103:
dynamic worker bits.

25:
five-stripe:
Hamming maintenance bits.

No:
inactive:
state.

Repair groups:

worker index mod 5.

Five:
parity bits
per:
stripe.

The:
DG-1R-08:
repair mechanism
remains:
unchanged.

DEVELOPMENTAL PREFIX

Before:
the:
capability stream,

each world receives:

512:
developmental:
binary:
input steps.

These:
512 steps

are:

NOT:
part:
of:
readout:
training.

NOT:
part:
of:
readout:
testing.

NO:
task:
targets

are:
computed
or:
visible

during:
development.

Input mapping:

the:
same:
four:
safe:
worker positions

used:
later
during:
capability /
repair:
evaluation.

BASE DEVELOPMENTAL DYNAMICS

During:
all:
512:
developmental:
steps:

every:
worker

runs:

ordinary:
MIXED5:
dynamics

at:
one:
update
per:
external:
input.

Record:
per-worker:

FLIP_RATE:

fraction:
of:
developmental:
steps
where:
the:
worker's:
state
changes.

ONE_FRACTION:

fraction:
of:
developmental:
steps
where:
state = 1.

LOCAL_DISAGREEMENT:

mean:
fraction
of:
the:
two:
ring neighbors
that:
differ
from:
the:
worker.

No:
task:
label
or:
delay:
target
is:
used.

ROLE COUNTS

After:
the:
512-step:
developmental:
prefix:

freeze:
exactly:

26:
RETENTION:
workers.

26:
RELAY:
workers.

51:
PROCESSOR:
workers.

Total:

103.

Roles:

remain:
fixed

through:
capability
and:
repair:
evaluation.

ROLE PROGRAMS

PROCESSOR

Clock:

update:
every:
external:
step.

Rule:

the:
worker's:
world-specific:
MIXED5:
rule.

Purpose:

ordinary:
nonlinear:
transformation.

RETENTION

Clock:

update:
only:
when:

external_step mod 4 = 3.

Thus:

one:
worker update
per:
four:
external:
inputs.

Rule:

the:
worker's:
world-specific:
MIXED5:
rule.

On:
other:
steps:

hold:
current:
bit.

Purpose:

preserve:
state
longer.

RELAY

Clock:

update:
every:
external:
step.

Rule:

ECA90

using:
the:
current:
left /
center /
right:
worker:
neighborhood.

Purpose:

fast:
additive:
signal:
propagation /
mixing.

All:
workers:

remain:
on:
one:
103-cell:
periodic:
ring.

ROLE ASSIGNMENT METHODS

1.
UNIFORM103

Reference:

all:
103:
workers

PROCESSOR.

Exact:
DG-1R-08:
worker:
dynamics.

Developmental prefix:

still:
executed
for:
fairness,

but:

does NOT:
change:
roles.

2.
RANDOM_ROLE103

26:
RETENTION.

26:
RELAY.

51:
PROCESSOR.

Assignment:

world-specific:
random:
permutation

drawn:
before:
the:
developmental:
prefix

from:
the:
world RNG.

Role counts:

identical
to:
developmental:
method.

Purpose:

control:
for:
heterogeneity
alone.

3.
PERIODIC_ROLE103

26:
RETENTION.

26:
RELAY.

51:
PROCESSOR.

Assignment:

deterministic:
spatial:
interleaving.

Walk:
worker indices:
0..102.

Assign:

RETENTION:
to:
indices
where:
index mod 4 = 0

until:
26:
workers
are:
assigned.

From:
remaining:
workers,

assign:
RELAY:
to:
the:
first:
26:
indices
where:
index mod 4 = 2,

then:
lowest:
remaining:
indices
if:
needed.

All:
remaining:

PROCESSOR.

Purpose:

control:
for:
regular:
spatial:
role mixing.

4.
DEVELOPMENTAL_ROLE103

Use:
the:
512-step:
label-free:
developmental:
telemetry.

Compute:
for:
each:
worker:

PERSISTENCE_SCORE
=
1
-
FLIP_RATE.

RELAY_SCORE
=
FLIP_RATE
*
(
0.5
+
LOCAL_DISAGREEMENT
).

Assignment:

RETENTION:

select:
26:
workers
with:
highest:
PERSISTENCE_SCORE.

Tie:

lower:
worker index.

From:
the:
remaining:
77:

RELAY:

select:
26
with:
highest:
RELAY_SCORE.

Tie:

lower:
worker index.

Remaining:

51:
PROCESSOR.

Purpose:

allow:
the:
organism's:
own:
pre-task:
dynamics

to:
determine:
where:
slow:
state
and:
fast:
relay:
roles
should:
reside.

IMPORTANT:

role assignment
uses:

NO:
readout:
target.

NO:
task:
accuracy.

NO:
held-out:
data.

NO:
damage:
outcome.

NO:
post-development:
adaptation.

CAPABILITY STREAM

After:
role freeze:

continue:
from:
the:
developmental:
organism state.

Then:
generate:

4096:
capability:
input steps.

Training:

64..2111.

2048 rows.

Gap:

448.

Testing:

2560..3583.

1024 rows.

TASKS

D1.
D4.
D8.
D16.
D32.
XOR3_11.
PARITY5.
MOTIF2_12.

Exact:
prior:
DG-1R:
definitions.

READOUT

Worker:
bits
only.

Maintenance:
bits
excluded.

Linear:
ridge.

Alpha:

1e-3.

Bias:

included,
unregularized.

CAPABILITY METRICS

- task medians;
- memory score;
- nonlinear score;
- worker-state entropy;
- worker-feature rank;
- feature-rank fraction.

ROLE TELEMETRY

Per:
world /
role method:

- count:
  each:
  role;
- mean:
  developmental:
  flip rate
  by:
  frozen:
  role;
- mean:
  developmental:
  local disagreement
  by:
  role;
- fraction:
  of:
  mapped:
  input positions
  assigned:
  each:
  role;
- role:
  transition:
  count:
  after:
  freeze:

0:
required.

REPAIR BRANCH

After:
the:
same:
developmental:
prefix
and:
role freeze,

restart:
the:
evaluation:
input stream
from:
its:
first:
step

while:
retaining:
the:
developed:
state /
roles.

Run:

1024:
repair-prefix:
steps.

Damage:

before:
repair input:
1024.

Damage locations:

shared:
first-64:
worker regions:

0..7,
16..23,
32..39,
48..55.

SMALL3:

offsets:
2,
3,
4.

LARGE5:

offsets:
1,
2,
3,
4,
5.

Post-damage:

32:
steps.

Repair:

five-stripe:
Hamming
before:
each:
worker:
evolution step.

ROLE programs:

unchanged
by:
damage.

PRIMARY REPAIR METRICS

h1 /
h32:

exact-worker:
recovery.

exact-full-state:
recovery.

worker-divergence:
area.

Corrected:
data bits.

Out-of-range:
syndrome events.

NO-DAMAGE CONTROL

Duplicate:
undamaged:
clones

must:
remain:
bit-exact.

ENCODING CONTROL

Normal:
coded:
states

must:
be:
syndrome-free
at:
step:
boundaries.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926090000
through:
20260926090007.

No:
prior:
DG-1R:
seed reuse.

PRIMARY COMPARISONS

A.
RANDOM_ROLE103
versus:
UNIFORM103.

Question:

does:
role heterogeneity
alone
help?

B.
PERIODIC_ROLE103
versus:
RANDOM_ROLE103.

Question:

does:
regular:
spatial:
mixing
help
beyond:
random:
roles?

C.
DEVELOPMENTAL_ROLE103
versus:
RANDOM_ROLE103.

Question:

does:
label-free:
developmental:
placement
help
beyond:
the:
same:
role counts?

D.
DEVELOPMENTAL_ROLE103
versus:
UNIFORM103.

Question:

does:
specialization
turn:
state:
headroom

into:
functional:
gain?

FROZEN CLASSIFICATIONS

REPAIR_PRESERVED

A:
role method

passes
if:

SMALL3:
h1 exact-full recovery
>=0.95

AND:

LARGE5:
h1 exact-full recovery
>=0.95

AND:

combined:
h32 exact-full recovery
>=0.95

AND:

no-damage control:
PASS

AND:

encoding control:
PASS.

HETEROGENEITY_GAIN

TRUE
if:

RANDOM_ROLE103
versus:
UNIFORM103

has:

memory score:
median gain
>=0.02

OR:

nonlinear score:
median gain
>=0.02

while:
neither:
score
degrades:
by:
more than:
0.05

AND:

REPAIR_PRESERVED.

SPATIAL_MIXING_GAIN

TRUE
if:

PERIODIC_ROLE103
versus:
RANDOM_ROLE103

has:

memory:
or:
nonlinear:
median gain
>=0.02

with:
the:
other:
score
>= -0.05

AND:

REPAIR_PRESERVED.

DEVELOPMENTAL_PLACEMENT_GAIN

TRUE
if:

DEVELOPMENTAL_ROLE103
versus:
RANDOM_ROLE103

has:

memory:
or:
nonlinear:
median gain
>=0.02

with:
the:
other:
score
>= -0.05

AND:

REPAIR_PRESERVED.

FUNCTIONAL_SPECIALIZATION_SIGNAL

TRUE
if:

DEVELOPMENTAL_ROLE103
versus:
UNIFORM103

has:

memory:
or:
nonlinear:
median gain
>=0.03

AND:

the:
other:
score
does NOT:
degrade
by:
more than:
0.05

AND:

state entropy
>=0.20

AND:

REPAIR_PRESERVED.

LONG_MEMORY_SIGNAL

TRUE
if:

DEVELOPMENTAL_ROLE103:

D16 median
>=0.60

OR:

D32 median
>=0.60.

STRONG DEVELOPMENTAL ROLE SIGNAL

TRUE
if:

FUNCTIONAL_SPECIALIZATION_SIGNAL

AND:

DEVELOPMENTAL_PLACEMENT_GAIN.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-09:
primary:
world,

do not alter:

- developmental prefix length;
- role counts;
- persistence score;
- relay score;
- role programs;
- clocks;
- rules;
- input mapping;
- tasks;
- readout;
- repair mechanism;
- damage family;
- thresholds;
- world family.

REPRODUCIBILITY

Two:
complete:
8-world:
canonical sweeps.

Canonical:
SHA-256
must:
match exactly.

NEXT

If:
STRONG_DEVELOPMENTAL_ROLE_SIGNAL:

proceed to:

DG-1R-10 —
ROLE SWITCHING /
HOMEOSTATIC:
REASSIGNMENT.

Allow:
roles
to:
change
after:
damage /
resource:
pressure

under:
bounded:
local:
rules.

If:
heterogeneity helps
but:
developmental placement
does not:

focus:
on:
role:
mixture /
clock:
ratios

rather:
than:
developmental:
selection.

If:
state rank
remains:
high
but:
task scores
remain:
flat:

the:
next:
bottleneck
is:
information:
routing /
readout:
access

rather:
than:
role:
allocation.

PLAIN-SPEAK PRE-REGISTERED QUESTION

We:
already:
proved:
the:
103-cell:
organism

has:
more:
internal:
room
to:
represent:
things.

But:
the:
extra:
room
is:
not:
helping:
our:
tasks.

So:
now:
we:
stop:
making:
every:
cell
do:
the:
same:
job.

Before:
the:
real:
test,

the:
organism
gets:
512:
steps
to:
develop.

No:
answers.
No:
task:
labels.

We:
just:
watch:
how:
each:
cell
behaves.

Cells:
that:
naturally:
hold:
state
become:
slow:
retention:
cells.

Cells:
that:
change:
a lot
and:
interact:
with:
their:
neighbors
become:
fast:
relay:
cells.

The:
rest
stay:
normal:
processing:
cells.

Then:
we:
freeze:
those:
roles
and:
test:
the:
organism.

A:
random:
organism
gets:
the:
exact:
same:
number
of:
each:
role.

So:
if:
the:
developmental:
version
does:
better,

it:
is:
not:
because:
we:
simply:
added:
different:
cell:
types.

It:
means:
where:
the:
organism
put:
those:
roles
actually:
mattered.

canonical_scientific_execution = false.
stab18_r1_touched = false.
