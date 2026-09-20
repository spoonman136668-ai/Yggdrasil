TITLE: DG-1R-05B — Corrected Multi-Bit Local Damage / Parity-Guardian Boundary Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE REPAIR-BOUNDARY PILOT
TRACK: DG-1R / SOFTWARE CELLS / LOCAL REDUNDANCY / ERROR-BOUNDARY CONTROL
BRANCH: dg1a-ar
PARENT: DG-1R-05A

PURPOSE

DG-1R-05A showed:

- local redundancy can convert containment into exact counterfactual repair;
- HAM74_REPAIR_ALWAYS exactly repaired single correctable lesions;
- distributed one-bit-per-block lesions also recovered exactly;
- the intended DOUBLE2_LOCAL boundary test was invalid because the frozen harness flipped only one bit.

DG-1R-05B corrects that boundary.

Primary questions:

1.
Does:
Hamming(7,4):
always-repair

misrepair:
true:
two-bit:
local damage?

2.
Can:
the:
eighth:
same-budget:
local:
controller bit

be:
repurposed
as:

an:
OVERALL:
PARITY:
GUARDIAN

to:
turn:
the:
8-bit:
block
into:

extended:
Hamming(8,4)
SECDED

and:

DETECT:
two-bit:
damage

so:
the:
repair system
can:
ABSTAIN
rather:
than:
confidently:
misrepair?

BOUNDARY

Synthetic software-only pilot.

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

NON-CANONICAL /
NON-EVIDENCE.

DG-1R-05:
canonical frozen primary
remains:
UNSPENT.

TOTAL STATE BUDGET

128:
persistent:
bits.

16:
local:
8-bit:
blocks.

No:
hidden:
memory.

No:
external:
repair:
oracle.

No:
task:
labels.

LOGICAL STATE

64:
logical:
data:
bits.

Each:
8-bit:
physical:
block

represents:

4:
logical:
data:
bits.

METHOD A — HAM74_ALWAYS

Block:

7:
Hamming(7,4):
code bits

plus:

1:
unused /
non-repair:
controller bit.

At:
pre-input:
repair phase:

if:
Hamming syndrome
is:
1..7:

flip:
the:
indicated:
7-bit:
position.

No:
double-error:
detection.

Purpose:

reproduce:
the:
DG-1R-05A:
always-repair:
mechanism

under:
correct:
multi-bit:
lesions.

METHOD B — HAM74_H6_GATE

Block:

7:
Hamming(7,4):
code bits

plus:

1:
H6:
homeostatic:
controller bit.

If:
syndrome !=0:

repair:
only:
when:
the:
controller bit
agrees:
with:
at least:
4:
of:
the:
7:
code bits.

Purpose:

test:
whether:
homeostatic:
gating
reduces:
misrepair
under:
uncorrectable:
multi-bit:
damage.

METHOD C — SECDED84_GUARD

Use:

extended:
Hamming(8,4).

Positions:

1:
p1.

2:
p2.

3:
d1.

4:
p4.

5:
d2.

6:
d3.

7:
d4.

8:
p0:
overall:
even:
parity.

The:
former:
nanite bit

becomes:

PARITY GUARDIAN.

At:
pre-input:
repair phase:

compute:

Hamming syndrome:
s
from:
positions:
1..7.

Compute:

overall parity:
P
across:
all:
8 bits.

Interpretation:

s = 0,
P = 0:

NO ERROR.

s != 0,
P = 1:

SINGLE-BIT:
ERROR
in:
positions:
1..7.

Correct:
the:
syndrome:
position.

s = 0,
P = 1:

SINGLE-BIT:
ERROR
in:
overall:
parity bit.

Correct:
position:
8.

s != 0,
P = 0:

DETECTED:
DOUBLE-BIT:
ERROR.

ABSTAIN.

No:
bit:
is:
changed.

This is:

SECDED:
single-error correction /
double-error detection.

METHOD D — SECDED84_FORCE

Same:
extended:
8-bit:
code.

But:
if:

s !=0,
P =0

for:
a:
detected:
double error,

still:
flip:
the:
syndrome:
position.

Purpose:

negative:
control
showing:
the:
cost
of:
ignoring:
double-error:
uncertainty.

METHOD E — DETECT_ONLY

Use:
SECDED84:
syndrome /
overall parity

but:

never:
repair.

Purpose:

separate:
detection /
coding geometry
from:
actual:
correction.

REPAIR / INPUT ORDER

Frozen:

1.
inspect:
persistent:
pre-input:
codeword;

2.
perform:
allowed:
repair /
abstention;

3.
decode:
logical:
64-bit:
state;

4.
apply:
current:
input overwrite;

5.
one:
logical:
MIXED5:
CA:
update;

6.
re-encode:
all:
local:
blocks;

7.
persist:
the:
new:
8-bit:
codewords.

No:
fresh:
input
is:
visible
to:
the:
repair:
decision.

INPUT MAPPING

Same:
64-logical-bit:
architecture
as:
DG-1R-05A.

8:
fixed:
logical:
input positions.

Damage:
blocks

must:
exclude:
input-mapped:
logical:
blocks.

WORLD FAMILY

8:
worlds.

Seeds:

20260926052000
through:
20260926052007.

No:
prior:
DG-1R:
seed reuse.

PRE-DAMAGE DEVELOPMENT

1024:
external:
input:
steps.

Then:
clone:

REFERENCE.

DAMAGED.

Continue:

32:
post-damage:
steps

under:
identical:
future:
input.

DAMAGE BLOCKS

Use:

0,
4,
8,
12.

Harness MUST:

assert:

actual:
lesion cardinality

equals:
the:
preregistered:
cardinality

before:
any:
scenario
evolves.

DAMAGE FAMILIES

ONE1

Inside:
one:
8-bit:
block:

flip:
physical:
position:
3.

Actual lesion size:

1.

TWO2

Inside:
one:
8-bit:
block:

flip:
physical:
positions:

3,
5.

Actual lesion size:

2.

THREE3

Inside:
one:
8-bit:
block:

flip:
physical:
positions:

2,
3,
5.

Actual lesion size:

3.

PARITY1

SECDED methods only.

Flip:

position:
8:
overall parity guardian.

Actual lesion size:

1.

DISTRIBUTED_TWO2

Choose:
two:
different:
damage blocks.

In:
each:
block:

flip:
positions:
3,
5.

Total:
lesion size:

4.

Purpose:

test:
multiple:
simultaneous:
locally:
uncorrectable:
double errors.

PRIMARY METRICS

Counterfactual:
metrics
at:

1,
4,
8,
16,
32:

- whole-state divergence;
- damaged-site recovery;
- outside-lesion divergence;
- spread count;
- exact-match rate.

Also:

- excess divergence area;
- sustained full-recovery rate;
- recovery time.

REPAIR TELEMETRY

Per:
method /
damage family:

- syndrome-positive count;
- overall-parity-positive count;
- corrections;
- abstentions;
- detected-double count;
- false corrections;
- correction target position histogram.

FALSE CORRECTION

A:
correction
is:
FALSE

if:

the:
flipped:
repair target

already:
matched:
the:
counterfactual:
reference
immediately:
before:
repair.

Repair logic:

never:
sees:
this:
label.

It is:
evaluation:
telemetry only.

ONE-BIT REPAIR INVARIANT

HAM74_ALWAYS
and:
SECDED84_GUARD

should:
retain:
the:
DG-1R-05A:
single-error:
repair behavior.

ONE_BIT_REPAIR_SIGNAL

TRUE
if:

ONE1:

median:
h4:
whole-state divergence
=
0

AND:

full-recovery rate
>=0.90

for:

HAM74_ALWAYS
and:
SECDED84_GUARD.

DOUBLE-ERROR DETECTION SIGNAL

TRUE
if:

on:
TWO2:

SECDED84_GUARD:

1.
detected-double rate
>=0.95;

2.
correction count
=
0
for:
detected:
double errors;

3.
false-correction fraction
<=0.01;

AND:

HAM74_ALWAYS:

false-correction fraction
>=0.50

OR:

median:
excess divergence area
is:
at least:
25%:
higher
than:
SECDED84_GUARD.

ABSTENTION VALUE SIGNAL

TRUE
if:

on:
TWO2
or:
DISTRIBUTED_TWO2:

SECDED84_GUARD

has:

median:
excess divergence area

at least:
25%:
lower

than:
SECDED84_FORCE

AND:

median:
outside-lesion divergence
at:
h8

at least:
25%:
lower.

This tests:

whether:
knowing:
WHEN NOT TO REPAIR

is:
valuable.

TRIPLE-ERROR BOUNDARY

THREE3
is:
expected
to:
expose:
SECDED's:
limit.

Report:

- misclassification;
- false-correction rate;
- divergence.

No:
positive:
repair claim
may:
be:
made
for:
THREE3
unless:
the:
frozen:
metrics
actually:
support it.

PARITY-GUARDIAN SIGNAL

TRUE
if:

SECDED84_GUARD:

- preserves:
  ONE1:
  repair;
- detects:
  TWO2;
- avoids:
  the:
  majority:
  of:
  false:
  corrections
  seen:
  in:
  HAM74_ALWAYS /
  SECDED84_FORCE.

INTERPRETATION

A:
positive:
parity-guardian:
result

would show:

a:
local:
maintenance:
cell

can:
improve:
repair
not:
by:
storing:
task:
memory,

but:
by:
storing:
CHECK:
INFORMATION.

This:
is:
a:
different:
role
from:

compute cell.

memory cell.

homeostatic:
stabilizer.

It is:

INTEGRITY:
GUARDIAN.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-05B:
scenario:

do not alter:

- code definitions;
- syndrome logic;
- parity logic;
- repair order;
- lesion positions;
- lesion cardinalities;
- damage blocks;
- thresholds;
- world family;
- metrics.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Canonical output SHA-256
must:
match exactly.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
experiment
showed:
that:
backup:
information
lets:
the:
nanites
repair:
a:
single:
damaged:
bit
perfectly.

But:
we:
accidentally:
did not:
really:
test:
two:
damaged:
bits
inside:
the:
same:
local:
block.

This:
experiment
fixes:
that.

We also:
give:
one:
version
of:
the:
local:
maintenance:
cell

a:
new:
job.

Instead of:
trying:
to:
remember:
the:
data,

it:
stores:
one:
extra:
integrity:
check.

That:
lets:
the:
block
tell:
the:
difference
between:

"I know:
which:
one:
bit
is:
wrong,
so:
repair it"

and:

"More than:
one:
bit
is:
wrong,
so:
I do NOT:
know:
the:
right:
repair."

If:
that:
works,

we:
will:
have:
evidence
for:
another:
specialized:
cell role:

not:
memory,

not:
computation,

but:

LOCAL:
INTEGRITY:
GUARDIANSHIP.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05B PARITY-GUARDIAN BOUNDARY HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05B:
SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05b_parity_guardian_v1.py

Harness commit:

fee4a543657668efee7f82abb60557502e585606.

Git blob SHA:

30779a50cfd35029581f767408605c0ce3a6478b.

Source SHA-256:

05d11a8e5002940c1b2378ad4b1f3c9fe847d7cbc15729961078943f73297836.

Source bytes:

12500.

LOCAL PRECHECK

Exact:
Git blob:
identity:

PASS.

Python:
syntax:

PASS.

No:
DG-1R-05B:
scenario
was:
executed
before:
this:
freeze.

FROZEN DISTRIBUTED_TWO2 DETAIL

Use:
damage blocks:

0
and:
8.

Inside:
each:

flip:
physical:
positions:

3
and:
5.

Actual total:
lesion cardinality:

4.

FROZEN CARDINALITY ASSERTIONS

ONE1:

1.

TWO2:

2.

THREE3:

3.

PARITY1:

1.

DISTRIBUTED_TWO2:

4.

The:
harness
must:
assert:

- expected:
  lesion:
  cardinality;
- unique:
  lesion:
  indices;
- no:
  lesion:
  index
  overlaps:
  an:
  input-mapped:
  physical:
  position.

FROZEN WORLD FAMILY

20260926052000..20260926052007.

8 worlds.

DG-1R-05 CANONICAL STATUS

Still:

UNSPENT.

DG-1R-05B:

NON-CANONICAL /
NON-EVIDENCE.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

canonical_scientific_execution = false.
stab18_r1_touched = false.


MECHANICAL INVALIDATION 01 — ORIGINAL FROZEN HARNESS

The:
first:
DG-1R-05B:
execution attempt

terminated:
before:
producing:
a:
result

with:

KeyError:
'35'.

Cause:

correction-target:
telemetry

was:
keyed
for:
local:
positions:

1..8

but:
the:
recorder
used:

global:
128-cell:
indices.

This:
affected:

telemetry:
histogram indexing

only.

It did NOT:
change:

- repair:
  target;
- syndrome:
  logic;
- parity:
  logic;
- state:
  evolution;
- lesion:
  geometry;
- classification:
  thresholds.

The:
original:
frozen:
harness

is:

MECHANICALLY INVALID /
NO RESULT.

Its:
execution attempt
must NOT:
be:
interpreted
as:
experimental:
evidence.

FIXA IMPLEMENTATION FREEZE — TELEMETRY-ONLY REPAIR

FixA harness:

research/experiments/dg1r/harnesses/dg1r_05b_parity_guardian_fixa_v1.py

FixA commit:

e54504b75f4e032c368e96825c0d2a714f7256da.

Git blob SHA:

0b69afde3a1fad7d2f7659f9f76d8b53013b1c6b.

Source SHA-256:

b2d828f43ebd31b85c6245b858be90aba1e196f3d7ce9ca03e6576153c9dcf7f.

Source bytes:

12528.

Only:
semantic delta
from:
the:
invalid:
original:

correction-target:
histogram

now:
receives:
the:
local:
codeword:
position

1..8

while:

the:
actual:
state:
correction

continues:
to:
use:
the:
same:
global:
physical:
cell:
index.

Python syntax:

PASS.

No:
complete:
DG-1R-05B:
result
exists
before:
FixA:
execution.

All:
preregistered:
experimental:
semantics /
worlds /
lesions /
metrics /
thresholds

remain:

UNCHANGED.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05B NON-EVIDENCE CLOSURE — MULTI-BIT BOUNDARY / PARITY GUARDIAN

DATE:
2026-09-20.

STATUS:
COMPLETE /
POSITIVE DOUBLE-ERROR DETECTION /
POSITIVE PARITY-GUARDIAN ROLE /
ABSTENTION-ONLY RECOVERY NEGATIVE /
TRIPLE-ERROR BOUNDARY CONFIRMED /
DETECT_ONLY CONTROL INVALIDATED /
NON-CANONICAL /
NON-EVIDENCE.

FIXA HARNESS

research/experiments/dg1r/harnesses/dg1r_05b_parity_guardian_fixa_v1.py

FixA Git blob SHA:

0b69afde3a1fad7d2f7659f9f76d8b53013b1c6b.

FixA source SHA-256:

b2d828f43ebd31b85c6245b858be90aba1e196f3d7ce9ca03e6576153c9dcf7f.

FixA source bytes:

12528.

CANONICAL OUTPUT FOR THIS NON-EVIDENCE PILOT

RUN 1 SHA-256:

2c553f11372107c3555fe82459113872cf8033464d27e01ecfa13a325dea7f44.

RUN 2 SHA-256:

2c553f11372107c3555fe82459113872cf8033464d27e01ecfa13a325dea7f44.

Byte-identical:

PASS.

MECHANICAL VALIDITY

no-damage duplicate trajectories:

PASS.

lesion cardinality assertions:

PASS.

ONE1:

1 actual bit.

TWO2:

2 actual bits.

THREE3:

3 actual bits.

DISTRIBUTED_TWO2:

4 actual bits.

mechanical_valid:

TRUE.

FROZEN SIGNALS

ONE_BIT_REPAIR_SIGNAL:

TRUE.

DOUBLE_ERROR_DETECTION_SIGNAL:

TRUE.

ABSTENTION_VALUE_SIGNAL:

FALSE.

PARITY_GUARDIAN_SIGNAL:

TRUE.

ONE-BIT INVARIANT

HAM74_ALWAYS:

ONE1:
median divergence area:

0.

full recovery rate:

1.0.

h32:
whole-state divergence:

0.

SECDED84_GUARD:

ONE1:
median divergence area:

0.

full recovery rate:

1.0.

h32:
whole-state divergence:

0.

PARITY1:

median divergence area:

0.

full recovery rate:

1.0.

Thus:

the:
overall:
parity guardian
does NOT:
break:
single-error:
repair.

It:
also:
repairs:
damage
to:
its:
own:
integrity:
bit.

TRUE TWO-BIT BOUNDARY

HAM74_ALWAYS:

TWO2:

median divergence area:

2.2734375.

full recovery rate:

0.25.

false-correction fraction:

1.0.

Thus:

plain:
Hamming(7,4)
always-repair

confidently:
miscorrects:
true:
two-bit:
local:
damage.

HAM74_H6_GATE:

TWO2:

median divergence area:

2.48046875.

full recovery rate:

0.1875.

false-correction fraction:

1.0
among:
performed:
corrections.

H6:
abstained:
14:
times
but:
did NOT:
reliably:
identify:
the:
uncorrectable:
boundary.

Thus:

homeostatic:
consensus
is:
not:
a:
substitute
for:
integrity:
information.

SECDED84_GUARD

TWO2:

detected-double count:

32
across:
32:
scenarios.

Detection rate:

100%.

Corrections:

0.

False-correction fraction:

0.

Abstentions:

32.

Thus:

the:
parity guardian
perfectly:
distinguishes:
this:
true:
two-bit:
local:
damage
from:
a:
single:
correctable:
error.

However:

median divergence area:

2.359375.

full recovery rate:

0.25.

h32:
whole-state divergence:

0.0625.

Therefore:

DETECTION
does NOT:
equal:

RECONSTRUCTION.

The:
guardian:
correctly:
knows:

"I do not know
the:
safe:
repair."

It:
does NOT:
possess:
enough:
information

to:
recover:
the:
two:
lost:
bits.

SECDED84_FORCE

TWO2:

detected-double count:

32.

Corrections:

32.

false-correction fraction:

1.0.

median divergence area:

2.578125.

Thus:

ignoring:
the:
double-error:
warning

and:
forcing:
a:
repair

creates:
confident:
miscorrection.

ABSTENTION VALUE

Frozen:
ABSTENTION_VALUE_SIGNAL:

FALSE.

Although:

SECDED84_GUARD
avoids:
false:
correction,

its:
median:
trajectory:
advantage
over:
SECDED84_FORCE

did not:
reach:
the:
frozen:
25%:
threshold.

TWO2:

GUARD AUC:

2.359375.

FORCE AUC:

2.578125.

Distributed TWO2:

GUARD AUC:

5.140625.

FORCE AUC:

4.5.

Thus:

abstention:
prevents:
inventing:
a:
known-wrong:
repair,

but:

the:
unrepaired:
damage
still:
propagates

and:
can:
be:
as:
costly
or:
worse
than:
a:
forced:
miscorrection
on:
some:
trajectories.

This:
is:
a:
critical:
distinction.

DISTRIBUTED TWO-BIT DAMAGE

SECDED84_GUARD:

two:
simultaneous:
double-error:
blocks

produced:

16:
detected-double:
events
across:
8:
world scenarios.

Corrections:

0.

False corrections:

0.

But:

median divergence area:

5.140625.

full recovery rate:

0.

Thus:

local:
uncertainty:
detection
scales:

but:

reconstruction:
does NOT.

TRIPLE-ERROR BOUNDARY

SECDED84_GUARD:

THREE3:

detected-double count:

0.

Corrections:

32.

false-correction fraction:

1.0.

median divergence area:

2.359375.

Thus:

three-bit:
damage
can:
masquerade
as:
a:
single:
correctable:
error
under:
SECDED.

This:
confirms:
the:
expected:
coding:
boundary.

No:
triple-error:
repair:
claim
is:
made.

PARITY-GUARDIAN ROLE

PARITY_GUARDIAN_SIGNAL:

TRUE.

The:
eighth:
same-budget:
local:
bit

adds:
a:
new:
specialized:
role:

INTEGRITY:
GUARDIAN.

It:
does NOT:
store:
task:
memory.

It:
stores:
enough:
check:
information

to:
answer:

SAFE:
TO:
REPAIR?

versus:

LOCAL:
DAMAGE:
EXCEEDS:
MY:
REPAIR:
KNOWLEDGE.

This:
role
is:
mechanistically:
distinct
from:

- computational:
  cells;
- temporal:
  memory:
  cells;
- homeostatic:
  stabilizers;
- repair:
  effectors.

DETECT_ONLY CONTROL DEFECT

The:
preregistered:
DETECT_ONLY:
method

is:
INVALID
as:
a:
detect-without-repair:
control.

Frozen implementation:

routes:
SECDED:
single-error:
states

through:
the:
same:
single-error:
correction
path
as:
SECDED84_GUARD.

Observed:

DETECT_ONLY
therefore:
matches:
GUARD
on:
ONE1 /
PARITY1
and:
double-error:
abstention.

Consequences:

DETECT_ONLY:
results
must NOT:
be:
used
to:
claim:
a:
pure:
detection-only:
control.

This defect:

does NOT:
invalidate:

- HAM74_ALWAYS;
- HAM74_H6_GATE;
- SECDED84_GUARD;
- SECDED84_FORCE;
- ONE1;
- TWO2;
- THREE3;
- PARITY1;
- DISTRIBUTED_TWO2;
- frozen:
  primary:
  parity-guardian:
  classifications.

TECHNICAL CONCLUSION

The:
repair problem
now:
separates
into:
three:
layers.

LAYER 1:

CONTAINMENT.

Previously:
shown
by:
homeostatic:
nanites.

LAYER 2:

LOCAL:
CORRECTABLE:
RECONSTRUCTION.

Shown:
by:
redundant:
Hamming:
state.

LAYER 3:

UNCERTAINTY:
DETECTION.

Shown:
by:
the:
parity guardian.

But:

when:
damage
exceeds:
the:
local:
code's:
correction:
capacity,

the:
organism
still:
needs:

ADDITIONAL:
RECOVERY:
INFORMATION.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05C —
OVERLAPPING:
LOCAL:
REDUNDANCY /
NEIGHBOR:
RECONSTRUCTION:
AUDIT.

Keep:

128:
persistent:
bits.

Do NOT:
simply:
increase:
local:
code:
size.

Instead:

allow:
redundancy:
relations
to:
cross:
neighboring:
local:
blocks.

Question:

when:
one:
local:
block
reports:

DETECTED:
UNSAFE:
TO:
REPAIR,

can:
independent:
neighboring:
consistency:
relations

supply:
enough:
information
to:

- reconstruct:
  a:
  two-bit:
  local:
  lesion;
- validate:
  the:
  proposed:
  repair;
- avoid:
  triple-error:
  confident:
  misrepair?

This moves:
Yggdrasil
from:

isolated:
local:
error-correction

toward:

DISTRIBUTED:
TISSUE-LIKE:
INTEGRITY.

PLAIN-SPEAK SUMMARY

We:
finally:
tested:
real:
two-bit:
damage.

The:
ordinary:
Hamming:
repairer
did:
exactly:
what:
we:
were:
worried
about.

It:
thought:
it:
knew:
which:
bit
was:
wrong,

but:
it:
was:
wrong
every:
time
it:
tried:
to:
repair:
the:
two-bit:
damage.

The:
new:
parity-guardian
did:
better
in:
an:
important:
way.

It:
recognized:

"Two:
things:
are:
wrong.

I:
cannot:
safely:
fix:
this."

It:
refused:
to:
make:
up:
a:
repair.

That:
is:
a:
real:
new:
capability.

But:

refusing:
a:
bad:
repair
does not:
restore:
the:
lost:
information.

So:
the:
next:
problem
is:

where:
does:
the:
extra:
repair:
information
come:
from?

The:
best:
next:
idea
is:
overlapping:
local:
redundancy.

Instead of:
each:
little:
block
being:
alone,

neighboring:
blocks
carry:
some:
independent:
consistency:
information
about:
one:
another.

Then:
if:
one:
block
says:

"I know:
I am:
damaged,
but:
I do not:
know:
the:
repair,"

its:
neighbors
may:
be:
able:
to:
help:
reconstruct:
what:
was:
lost.

That:
starts:
to:
look:
less:
like:
a:
computer:
memory chip

and:
more:
like:
a:
self-checking:
software:
tissue.

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

DG-1R-05B remains:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
