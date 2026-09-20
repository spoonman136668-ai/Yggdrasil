TITLE: DG-1R-06 — Bounded Local SECDED Redundancy / Nanite Counterfactual Repair Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE REDUNDANCY-AIDED SELF-REPAIR PILOT
TRACK: DG-1R / SOFTWARE CELLS / LOCAL ERROR-CORRECTING HOMEOSTASIS
BRANCH: dg1a-ar
PARENT: DG-1R-05
PARENT_CLOSURE: e89f7b9bf239c44c2612db57af4185f093f63967

PURPOSE

DG-1R-05 established:

- H6 nanites provide real damage containment;
- H6_REPAIR improves containment further;
- neither architecture reliably reconstructs damaged cells
  toward the exact undamaged counterfactual trajectory;
- one-bit local consensus tells a controller that
  a region is unstable,
  but does not carry enough information to infer
  the correct missing state.

DG-1R-06 asks:

CAN:
LOCAL:
REDUNDANT:
DEVELOPMENTAL:
ENCODING

GIVE:
A:
PROGRAMMED:
SOFTWARE NANITE

ENOUGH:
INFORMATION

TO:
RECONSTRUCT:
THE:
CORRECT:
LOCAL:
STATE

WITHOUT:

- increasing:
  the:
  128-bit:
  persistent:
  organism;
- adding:
  hidden:
  history;
- using:
  task labels;
- using:
  an:
  external:
  repair buffer?

BOUNDARY

Synthetic software-only experiment.

No:
living tissue.
No:
wetware.
No:
biological nanotechnology.
No:
production modification.
No:
canonical H191 execution.
No:
STAB-18-R1 execution.

CODING MOTIVATION

Hamming(7,4):

4:
data bits

+
3:
parity bits

can:
locate
and:
correct:

one:
corrupted:
codeword bit.

Adding:
one:
overall:
parity bit

creates:

an:
8-bit:
SECDED:
codeword

that:

- corrects:
  one:
  corrupted bit;
- detects:
  two:
  corrupted bits
  under:
  the:
  assumed:
  error bound.

DG-1R-06 maps:

the:
8th:
overall-parity bit

to:

the:
local:
software-nanite:
check cell.

TOTAL STATE BUDGET

16:
local:
8-cell:
blocks.

Each block:

4:
DATA:
cells.

3:
HAMMING:
parity:
cells.

1:
NANITE /
overall-parity:
cell.

Total:

16 * 8
=
128:
persistent:
bits.

Thus:

64:
evolving:
data bits.

48:
local:
Hamming:
parity bits.

16:
nanite:
overall-parity:
bits.

No:
extra:
persistent:
state.

BLOCK LAYOUT

Within:
each:
8-cell:
block

codeword positions:

1:
P1.

2:
P2.

3:
D1.

4:
P4.

5:
D2.

6:
D3.

7:
D4.

8:
N:
overall parity /
nanite check cell.

HAMMING PARITY

Even parity.

P1 covers:

positions:
1,
3,
5,
7.

P2 covers:

2,
3,
6,
7.

P4 covers:

4,
5,
6,
7.

N:

overall:
even parity
across:

positions:
1..8.

SYNDROME

Before:
normal:
external-step:
evolution,

compute:

S1,
S2,
S4

from:
positions:
1..7

and:

overall:
parity.

syndrome
=
S1
+
2*S2
+
4*S4.

SECDED DECISION

CASE A:

syndrome = 0
and:
overall parity = 0.

No:
detected:
error.

No:
repair.

CASE B:

syndrome != 0
and:
overall parity = 1.

Interpret:

single-bit:
error
inside:
positions:
1..7.

Flip:

the:
syndrome-indicated:
bit.

CASE C:

syndrome = 0
and:
overall parity = 1.

Interpret:

single-bit:
error
in:
N:
overall-parity:
cell.

Flip:

N.

CASE D:

syndrome != 0
and:
overall parity = 0.

Interpret:

detected:
double-bit:
error.

Do NOT:
guess:
a:
correction.

Record:

DETECTED_UNCORRECTABLE.

IMPORTANT MULTI-BIT LIMIT

Three-or-more:
corruptions

are:
OUTSIDE:
SECDED's:
guaranteed:
correction model.

Such:
stress lesions

may:

- be:
  detected;
- be:
  misclassified;
- be:
  miscorrected;
- persist.

They are:
included:
explicitly
to:
measure:
the:
failure boundary.

They must NOT:
be:
presented
as:
errors
SECDED
was:
guaranteed
to:
repair.

HEALTHY DATA DYNAMICS

The:
64:
DATA:
cells

form:

one:
logical:
periodic:
data ring.

Their:
physical:
ordering

is:

block 0:
D1,D2,D3,D4,

then:
block 1:
D1,D2,D3,D4,

...

through:
block 15.

Each:
data cell

has:
one:
world-specific:
MIXED5:
rule

drawn:
from:

90,
150,
110,
22,
30

with:
approximately:
equal:
counts
across:
the:
64-data-cell:
ring.

Data:

evolve:
once:
per:
external:
input.

After:
data evolution:

recompute:

P1,
P2,
P4,
N

for:
every:
block

from:
the:
new:
data state.

Thus:

healthy:
codewords

return:
to:
valid:
SECDED:
form

after:
every:
external:
step.

INPUT MAPPING

8:
fixed:
input-mapped:
DATA:
cells.

Two:
consecutive:
8-cell:
SECDED blocks

form:

one:
16-cell:
input:
compartment.

For:
each:
compartment,

choose:
one:
world-specific:
DATA:
cell

uniformly
from:
the:
8:
available:
data cells.

The:
same:
mapped:
data positions

are used:
for:
all:
SECDED methods
inside:
a:
world.

INPUT RECURRENCE

OVERWRITE.

At:
each:
external:
step:

after:
pre-step:
syndrome handling,

overwrite:

the:
8:
mapped:
DATA:
cells

with:

u_t.

Then:

evolve:
the:
64-data-cell:
ring

once.

Then:

re-encode:
all:
local:
check /
nanite:
bits.

REFERENCE METHODS

1.
RAW64_CODE_PASSIVE

Same:

64-data /
48-parity /
16-nanite:
layout.

Same:
healthy:
encoding.

But:

before:
each:
external:
step:

does NOT:
perform:
syndrome-based:
correction.

It:
only:
records:
the:
syndrome:
telemetry.

Purpose:

local:
redundancy
without:
active:
nanite repair.

2.
SECDED_NANITE

Same:
layout.

Before:
each:
external:
step:

perform:
the:
frozen:
SECDED:
decision
and:
single-error:
correction.

Double-error:
detections:

recorded,
not:
guessed.

3.
SECDED_NANITE_QUARANTINE

Same:
SECDED:
single-error:
correction.

Additionally:

for:
CASE D:
detected:
double-bit:
error

inside:
a:
block,

mark:
that:
block

QUARANTINED
for:
the:
current:
external:
step
only.

Quarantine:

- does NOT:
  reconstruct:
  any:
  data bit;
- does NOT:
  use:
  hidden:
  timer state;
- does NOT:
  persist:
  beyond:
  the:
  current:
  step.

During:
that:
step:

the:
four:
data cells
of:
the:
quarantined:
block

hold:
their:
post-input:
pre-evolution:
values

while:
the:
rest:
of:
the:
64-data:
ring
evolves.

Afterward:

the:
block
is:
re-encoded.

Purpose:

test:
whether:
detection
plus:
one-step:
containment

limits:
multi-bit:
damage
without:
pretending:
to:
know:
the:
lost:
state.

EXTERNAL COMPARISON

Also:
carry forward:

N16_H6_REPAIR

from:
the:
frozen:
DG-1R-05:
parent mechanics

as:
a:
NO-REDUNDANCY:
active-repair:
reference.

It remains:

112:
workers
+
16:
one-bit:
nanites.

Because:
its:
healthy:
state representation
differs
from:
SECDED methods,

absolute:
trajectory metrics

are:
compared:
within:
method
against:
that:
method's:
own:
undamaged:
counterfactual.

Relative:
repair:
signals

are:
reported
across:
methods

with:
the:
representation:
difference
explicitly:
noted.

DAMAGE TIME

After:

1024:
healthy:
external:
steps.

Clone:

REFERENCE:
undamaged.

DAMAGED:
lesioned.

Continue:

32:
future:
external:
steps

with:
identical:
future:
input.

SECDED LESION BLOCKS

Use:

four:
unmapped:
SECDED blocks

chosen:
deterministically:

within:
input compartments:

0,
2,
4,
6,

select:

the:
sibling:
8-cell:
block

that:
does NOT:
contain:
the:
mapped:
input:
data cell.

Thus:

lesions
never:
directly:
overlap:
the:
input:
write.

LESION FAMILIES

SINGLE_DATA1

Flip:

codeword:
position:
3
=
D1.

One:
correctable:
data-bit:
error.

SINGLE_CHECK1

Flip:

codeword:
position:
1
=
P1.

One:
correctable:
check-bit:
error.

DOUBLE_ADJ2

Flip:

positions:
3,
4

=
D1,
P4.

Two:
adjacent:
codeword:
errors.

Within:
SECDED:
double-error:
detection:
regime.

No:
exact:
correction
is:
guaranteed.

CLUSTER3

Flip:

positions:
3,
4,
5

=
D1,
P4,
D2.

Three:
local:
errors.

Outside:
guaranteed:
SECDED:
correction.

CLUSTER5

Flip:

positions:
2,
3,
4,
5,
6.

Five:
local:
errors.

Outside:
guaranteed:
SECDED:
correction.

Do NOT:

flip:
the:
overall-parity /
nanite:
cell

in:
the:
primary:
lesion family.

N16_H6_REPAIR LESION MAPPING

For:
the:
external:
no-redundancy:
reference:

use:
the:
same:
four:
input compartments
and:
unmapped:
sibling:
8-cell:
blocks

under:
DG-1R-05:
mechanics.

Map:
lesion families
to:
worker-only:
damage sizes:

SINGLE_DATA1:
one:
center:
worker.

SINGLE_CHECK1:
one:
adjacent:
worker.

DOUBLE_ADJ2:
two:
adjacent:
workers.

CLUSTER3:
three:
centered:
workers.

CLUSTER5:
five:
centered:
workers.

This:
external:
reference
is:
telemetry.

Primary:
SECDED:
mechanism:
classification

is:
based:
on:
the:
SECDED:
methods
and:
their:
same-layout:
RAW64_CODE_PASSIVE:
control.

PRIMARY METRICS

At:
horizons:

1,
4,
8,
16,
32:

WHOLE_STATE_DIVERGENCE.

DATA_STATE_DIVERGENCE.

CHECK_STATE_DIVERGENCE.

LESION_CODEWORD_DIVERGENCE.

OUTSIDE_LESION_BLOCK_DIVERGENCE.

DAMAGE_SPREAD_COUNT
outside:
the:
lesion:
block.

EXACT_FULL_STATE_MATCH.

EXACT_DATA_STATE_MATCH.

Also:

EXCESS_WHOLE_DIVERGENCE_AREA
over:
32:
steps.

EXCESS_DATA_DIVERGENCE_AREA
over:
32:
steps.

SUSTAINED_FULL_RECOVERY.

SUSTAINED_DATA_RECOVERY.

RECOVERY_TIME_FULL.

RECOVERY_TIME_DATA.

NANITE / ECC TELEMETRY

Per:
scenario:

- single-error:
  corrections;
- parity/nanite:
  corrections;
- detected:
  double errors;
- syndrome:
  nonzero:
  events;
- quarantine:
  block-step:
  count;
- corrections:
  applied:
  to:
  originally:
  damaged:
  positions;
- corrections:
  applied:
  outside:
  originally:
  damaged:
  positions.

The last metric:

MISCORRECTION_OUTSIDE_LESION

is:
critical
for:
multi-bit:
stress.

NO-DAMAGE DETERMINISM CONTROL

For:
every:
method /
world:

two:
identical:
healthy:
clones

continued:
for:
32:
steps

under:
identical:
future:
input.

Required:

max:
whole-state:
divergence

=
0.

SECDED HEALTHY VALIDITY CONTROL

For:
SECDED:
methods /
worlds:

after:
the:
1024-step:
healthy:
prefix

every:
8-bit:
block

must:

have:

syndrome = 0

and:

overall parity = 0.

Required:

PASS.

SINGLE-ERROR MECHANICAL CONTROL

Before:
primary:
world execution,

non-primary:
exhaustive:
codeword sanity

shall:
verify:

for:
all:

16:
possible:
4-bit:
data words

and:

all:
8:
single-bit:
codeword:
corruptions,

SECDED_NANITE:

restores:
the:
exact:
valid:
8-bit:
codeword.

This:
is:
mechanical:
algorithm:
validation,

not:
primary:
evidence.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926060000
through:
20260926060007.

No:
prior:
DG-1R:
seed reuse.

SCENARIOS

4:
lesion blocks

x:

5:
lesion families

=

20:
damage scenarios
per:
method /
world.

Across:

8 worlds:

160:
scenarios
per:
method.

FROZEN PRIMARY SIGNALS

SINGLE_ERROR_RECONSTRUCTION

TRUE
if:

for:
SECDED_NANITE

across:

SINGLE_DATA1
+
SINGLE_CHECK1:

1.
median:
DATA_STATE_DIVERGENCE
at:
h1
=
0;

2.
median:
WHOLE_STATE_DIVERGENCE
at:
h1
=
0;

3.
SUSTAINED_FULL_RECOVERY rate
>=0.95;

4.
median:
EXCESS_WHOLE_DIVERGENCE_AREA

is:
at least:
90% lower

than:
RAW64_CODE_PASSIVE.

This tests:

true:
correct-state:
reconstruction.

DOUBLE_ERROR_CONTAINMENT

TRUE
if:

for:
DOUBLE_ADJ2:

SECDED_NANITE_QUARANTINE

versus:
RAW64_CODE_PASSIVE:

1.
median:
EXCESS_DATA_DIVERGENCE_AREA

is:
at least:
25% lower;

AND:

2.
median:
OUTSIDE_LESION_BLOCK_DIVERGENCE
at:
h16

is:
at least:
25% lower;

AND:

3.
median:
MISCORRECTION_OUTSIDE_LESION
=
0.

MULTIBIT_STRESS_SAFE

TRUE
if:

for:
CLUSTER3
and:
CLUSTER5:

SECDED_NANITE_QUARANTINE

does NOT:

increase:
median:
EXCESS_DATA_DIVERGENCE_AREA

by:
more than:
10%

relative:
to:
RAW64_CODE_PASSIVE

AND:

median:
MISCORRECTION_OUTSIDE_LESION

does NOT:
exceed:

SECDED_NANITE
by:
more than:
1:
correction
per:
scenario.

FULL_REDUNDANCY_AIDED_REPAIR_SIGNAL

TRUE
if:

SINGLE_ERROR_RECONSTRUCTION
is:
TRUE

AND:

DOUBLE_ERROR_CONTAINMENT
is:
TRUE.

IMPORTANT INTERPRETATION

A:
positive:
SINGLE_ERROR_RECONSTRUCTION

means:

redundancy
provided:
the:
missing:
information

needed:
for:
correct:
local:
repair.

It does NOT:
mean:

the:
system
can:
repair:
arbitrary:
large:
lesions.

A:
negative:
CLUSTER3 /
CLUSTER5:
result

is:
expected:
to:
bound:
the:
current:
code's:
repair:
radius.

That:
boundary
is:
scientifically:
useful.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-06:
primary:
damage scenario,

do not alter:

- 4+3+1 block layout;
- Hamming parity equations;
- overall parity;
- syndrome decoder;
- SECDED decision table;
- data-ring dynamics;
- input mapping;
- quarantine rule;
- lesion blocks;
- lesion families;
- horizons;
- metrics;
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

Runtime:
sidecar:
non-canonical.

NEXT

If:
FULL_REDUNDANCY_AIDED_REPAIR_SIGNAL:

test:

spatial:
interleaving /
developmental:
codeword:
geometry

to:
turn:
clustered:
multi-bit:
lesions

into:

separate:
single-bit:
local:
syndromes.

If:
single-error reconstruction
works
but:
double-error containment
fails:

retain:
SECDED
for:
repair

and:
test:

bounded:
erasure:
localization
or:
interleaved:
redundancy.

If:
single-error reconstruction
fails:

the:
implementation:
or:
data-evolution:
integration

is:
mechanically:
inadequate
and:
must:
be:
audited
before:
any:
stronger:
repair:
claim.

PLAIN-SPEAK PRE-REGISTERED QUESTION

DG-1R-05 showed:

the:
nanites
can:
stop:
damage
from:
spreading,

but:
they:
do not:
know:
what:
a:
broken:
cell
used:
to:
be.

So:

DG-1R-06
gives:
each:
small:
local:
region

a:
tiny:
built-in:
error-correcting:
blueprint.

We are:
not:
adding:
memory.

The:
organism
still:
has:
only:
128:
bits.

We are:
spending:
some:
of:
those:
bits
on:
redundancy.

Four:
bits
carry:
the:
local:
working:
state.

Three:
bits
act:
like:
Hamming:
check marks.

The:
eighth:
bit
is:
the:
nanite's:
overall:
parity:
check.

If:
one:
bit:
gets:
damaged,

the:
pattern
of:
check:
failures
should:
tell:
the:
nanite

exactly:
which:
bit
is:
wrong.

That:
would:
finally:
give:
the:
maintenance:
cell

a:
local:
blueprint
for:
correct:
repair.

Then:

we deliberately:
damage:
two,
three,
and:
five:
bits

to:
find:
where:
that:
repair:
ability
breaks.

The:
goal
is:
not:
to:
pretend:
one:
small:
code
can:
heal:
everything.

The:
goal
is:
to:
prove:

whether:
LOCAL:
REDUNDANCY

can:
turn:

"I know:
something:
is:
wrong"

into:

"I know:
what:
this:
specific:
broken:
state
should:
be."

canonical_scientific_execution = false.
stab18_r1_touched = false.
