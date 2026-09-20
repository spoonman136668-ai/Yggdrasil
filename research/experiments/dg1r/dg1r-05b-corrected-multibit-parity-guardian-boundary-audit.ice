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
