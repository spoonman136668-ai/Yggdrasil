TITLE: DG-1R-05C — Confidence-Gated Local Quarantine / Damage-Containment Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE QUARANTINE PILOT
TRACK: DG-1R / SOFTWARE CELLS / CONFIDENCE-AWARE HOMEOSTASIS
BRANCH: dg1a-ar
PARENT: DG-1R-05B

PURPOSE

DG-1R-05B established:

- SECDED local confidence preserves exact single-bit repair;
- distributed correctable lesions are repaired exactly;
- two-bit local damage is classified ambiguous and repair abstains;
- abstention prevents false repair but does not prevent
  the ambiguous local state from influencing future dynamics;
- three-bit damage remains an adversarial confidence boundary.

DG-1R-05C asks:

CAN:
AMBIGUOUS:
LOCAL:
STATE

BE:
QUARANTINED

WITHOUT:

- adding hidden state;
- adding memory;
- globally freezing the organism;
- guessing a repair?

CORE PRINCIPLE

Use:

the:
existing:
invalid /
ambiguous:
SECDED:
codeword

itself
as:

the:
quarantine:
marker.

No:
extra:
persistent:
flag.

No:
timer.

No:
external:
repair:
state.

TOTAL STATE

128 persistent bits.

16 local:
SECDED(8,4):
blocks.

64 logical:
data bits.

64 local:
redundancy /
confidence bits.

LOGICAL DYNAMICS

64 logical data bits.

One periodic:
MIXED5:
logical:
CA ring.

One:
logical:
CA update
per:
external:
input.

INPUT MAPPING

Same:
DG-1R-05B:
mapped block family.

Mapped blocks:

1,
2,
5,
7,
10,
11,
13,
14.

Damage blocks:

not:
directly:
input-mapped.

METHODS

1.
SECDED84_REPAIR_ABSTAIN

Exact:
DG-1R-05B:
primary:
reference.

Single:
correctable:
errors:

repair.

Double:
ambiguous:
errors:

abstain,

then:
decode /
evolve /
re-encode:
normally.

Purpose:

shows:
spread
when:
ambiguity
is:
recognized
but:
not:
isolated.

2.
SECDED84_QUARANTINE_REFLECT

Primary candidate.

Pre-input:

classify:
every:
8-bit:
block.

Single:
correctable:

repair.

Ambiguous:
double:

DO NOT:
repair.

Mark:
the:
block

quarantined
for:
this:
step

solely:
because:
its:
persistent:
codeword

remains:
SECDED:
ambiguous.

QUARANTINED BLOCK

- do not:
  overwrite:
  its:
  logical:
  data
  from:
  external:
  input;
- do not:
  update:
  its:
  four:
  logical:
  data:
  cells;
- do not:
  re-encode:
  its:
  physical:
  8-bit:
  codeword.

Thus:

the:
ambiguous:
physical:
codeword

remains:
present

and:
continues:
to:
signal:
quarantine

without:
hidden:
state.

HEALTHY-NEIGHBOR BOUNDARY

For:
a:
healthy:
logical:
cell

whose:
left
or:
right:
neighbor

lies:
inside:
a:
quarantined:
block:

replace:
that:
neighbor:
input

with:

the:
healthy:
cell's:
own:
current:
bit.

Interpretation:

REFLECTIVE /
SELF:
boundary.

The:
healthy:
cell

does NOT:
read:
uncertain:
quarantined:
state.

Healthy:
cells
otherwise:

use:
their:
normal:
MIXED5:
rule.

3.
SECDED84_QUARANTINE_GUARD1

Secondary candidate.

Same:
as:
QUARANTINE_REFLECT

plus:

the:
one:
healthy:
logical:
cell
immediately:
adjacent
to:
each:
side
of:
a:
quarantined:
block

holds:
its:
current:
state

instead:
of:
updating.

Purpose:

test:
whether:
a:
one-cell:
guard band

further:
reduces:
damage spread

or:
simply:
creates:
unnecessary:
healthy-state:
divergence.

4.
SECDED84_BLIND_SYNDROME

Negative:
repair:
control.

Uses:
SECDED:
encoding

but:
blindly:
repairs:
syndrome:
position

even:
on:
ambiguous:
double:
damage.

DAMAGE FAMILY

SINGLE1_LOCAL.

PARITY1_LOCAL.

DOUBLE2_LOCAL.

TRIPLE3_LOCAL.

DISTRIBUTED3.

DISTRIBUTED5.

Exact:
DG-1R-05B:
lesion:
locations.

PRIMARY TARGET FAMILY

DOUBLE2_LOCAL.

Reason:

05B:
can:
identify:
this:
family
as:
ambiguous

but:
cannot:
reconstruct:
it.

COUNTERFACTUAL FRAMEWORK

Pre-damage:

1024 steps.

Post-damage:

32 steps.

Undamaged:
reference

and:
damaged:
clone

receive:
identical:
future:
inputs.

Metrics:
at:

1,
4,
8,
16,
32.

METRICS

- whole-state divergence;
- damaged-site recovery;
- outside-lesion divergence;
- spread count;
- excess divergence area;
- full recovery rate;
- recovery time.

QUARANTINE TELEMETRY

- ambiguous block classifications;
- quarantine block-steps;
- distinct blocks quarantined;
- reflective-boundary substitutions;
- guard-cell holds;
- single-error corrections;
- false corrections.

CORRECTABLE-PRESERVATION GATE

For:
SINGLE1_LOCAL,
PARITY1_LOCAL,
DISTRIBUTED3,
DISTRIBUTED5:

a:
quarantine candidate

must:
preserve:

- full recovery rate = 1.0;
- median excess divergence area = 0;
- false corrections = 0.

If:
not:

quarantine:
damages:
healthy:
repair behavior.

DOUBLE-CONTAINMENT SIGNAL

Relative to:
SECDED84_REPAIR_ABSTAIN
on:
DOUBLE2_LOCAL,

a:
quarantine candidate
passes
if:

1.
median:
outside-lesion divergence
at:
h8

is:
at least:
50%:
lower;

2.
median:
outside-lesion divergence
at:
h16

is:
at least:
50%:
lower;

3.
median:
outside-lesion divergence
at:
h32

does NOT:
exceed:
the:
plain:
abstention:
reference;

4.
median:
excess divergence area

is:
at least:
25%:
lower;

5.
false corrections
=
0.

STRONG QUARANTINE

TRUE
if:

CORRECTABLE-PRESERVATION

and:

DOUBLE-CONTAINMENT SIGNAL

and:

DOUBLE2_LOCAL:
median:
outside-lesion divergence
at:
h16
<=0.02.

OVER-QUARANTINE COST

For:
DOUBLE2_LOCAL:

report:

- total:
  reflective:
  substitutions;
- total:
  guard:
  holds;
- difference:
  between:
  whole-state:
  divergence
  and:
  outside-lesion:
  divergence.

QUARANTINE_GUARD1

is:
inferior
to:
REFLECT

if:

it:
does NOT:
materially:
improve:
outside-lesion:
containment

but:
increases:
healthy:
whole-state:
divergence.

TRIPLE3

Boundary telemetry only.

SECDED:
may:
misclassify:
three-bit:
damage
as:
a:
single:
correctable:
error.

No:
quarantine:
guarantee
is:
claimed.

Report:
whether:
the:
triple:
family

bypasses:
quarantine

and:
how:
far:
it:
spreads.

INTERPRETATION

A:
positive:
result

would establish:
a:
four-mode:
local:
maintenance:
architecture:

HEALTHY:
evolve.

CORRECTABLE:
repair.

AMBIGUOUS:
quarantine.

BEYOND-CONFIDENCE:
escalate /
remain:
future:
research.

No:
global:
scheduler
or:
central:
repair:
oracle
is:
introduced.

WORLD FAMILY

8 worlds.

Seeds:

20260926053000
through:
20260926053007.

No:
prior:
DG-1R:
seed reuse.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Outputs:
must:
match
byte-for-byte.

NEXT

If:
STRONG QUARANTINE:

DG-1R-05D:

test:
higher-level:
reconstruction
of:
quarantined:
blocks

using:
neighbor:
redundancy /
developmental:
pattern constraints

without:
hidden:
history.

If:
quarantine:
contains:
damage
but:
never:
recovers:
the:
block:

that:
is:
still:
a:
useful:
homeostatic:
role.

The:
system
has:
learned:
the:
difference
between:

REPAIR

and:

ISOLATE.

Long term:

replace:
human-designed:
SECDED /
fixed:
quarantine

with:
developmentally:
emergent:
confidence
and:
containment:
roles.

PLAIN-SPEAK PRE-REGISTERED QUESTION

We:
can:
now:
tell:

this:
damage
is:
safe:
to:
repair

versus:

this:
damage
is:
ambiguous.

The:
next:
question
is:

what:
should:
the:
organism
do
when:
it:
does:
not:
know:
the:
right:
repair?

This:
test
does:
not:
let:
it:
guess.

Instead:

the:
damaged:
local:
area
stops:
talking:
to:
healthy:
neighbors.

The:
rest:
of:
the:
organism
keeps:
running.

The:
damaged:
block
stays:
marked:
as:
uncertain

using:
the:
same:
bits
that:
already:
show:
its:
parity:
is:
wrong.

No:
extra:
memory
is:
added.

If:
that:
works,

Yggdrasil
gets:
a:
much:
more:
biological:
maintenance:
pattern:

small:
damage:

FIX IT.

uncertain:
damage:

ISOLATE IT.

do:
not:
freeze:
the:
whole:
organism.

canonical_scientific_execution = false.
stab18_r1_touched = false.


SUPERSESSION NOTE — UNEXECUTED ALTERNATE BRANCH

DATE:
2026-09-20.

STATUS:
NOT EXECUTED /
SUPERSEDED AS:
PRIMARY 05C FRONTIER.

This:
quarantine:
preregistration

was:
never:
implemented,
frozen,
or:
executed.

Its:
preregistered:
seed family:

20260926053000..007

was:
subsequently:
used
by:

DG-1R-05C —
OVERLAPPING:
NEIGHBOR:
RECONSTRUCTION,

which:
was:
implemented,
frozen,
executed,
and:
closed.

Therefore:

this:
alternate:
quarantine:
draft

must NOT:
be:
executed
with:
its:
original:
seed family.

If:
revisited:

it:
requires:
a:
fresh:
experiment ID,
fresh:
disjoint:
seeds,
and:
a:
new:
pre-run:
freeze.

No:
result
is:
claimed
for:
this:
draft.

canonical_scientific_execution = false.
stab18_r1_touched = false.
