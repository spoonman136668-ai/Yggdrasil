TITLE: DG-1R-05D — Neighbor-Inconsistency Trigger / Syndrome-Blind Repair Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE DISTRIBUTED-DIAGNOSIS PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED INTEGRITY / SELF-DIAGNOSIS
BRANCH: dg1a-ar
PARENT: DG-1R-05C

PURPOSE

DG-1R-05C showed:

- overlapping neighbor redundancy can exactly reconstruct two-bit and four-bit local data loss;
- distributed separated lesions can be repaired in parallel;
- two-sided agreement prevents false repair when one recovery channel is damaged;
- a three-data-bit lesion remained unrepaired because its local Hamming syndrome was zero.

The three-bit failure was therefore:

not:
missing:
repair information,

but:

missing:
damage:
triggering.

DG-1R-05D asks:

CAN:
NEIGHBOR:
INCONSISTENCY

DIAGNOSE:
A:
LOCALLY:
SILENT:
CORRUPTION

AND:
TRIGGER:
REPAIR

WITHOUT:
CREATING:
UNACCEPTABLE:
FALSE:
REPAIRS?

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

STATE BUDGET

Exact:
DG-1R-05C:
tissue representation.

128:
persistent bits.

48:
logical:
data bits.

12:
logical:
blocks
x
4:
data bits.

Local:
Hamming(7,4)
storage:

84 bits.

Neighbor:
cross-block:
XOR checks:

44 bits.

Total:

128.

LOGICAL DYNAMICS

Exact:
DG-1R-05C:

one:
MIXED5:
CA update
per:
external input
over:
48:
logical:
bits.

Pre-damage:

1024 steps.

Post-damage:

32 steps.

METHOD 1 — SYNDROME_TRIGGER

Exact:
DG-1R-05C:
TISSUE74_XOR_BOTH.

For:
an:
interior:
block:

compute:

local:
Hamming:
syndrome.

Compute:

left:
neighbor-derived:
candidate.

Compute:

right:
neighbor-derived:
candidate.

Repair only if:

local syndrome
!=0

AND:

left candidate
==
right candidate.

Purpose:

frozen:
parent:
reference.

METHOD 2 — NEIGHBOR_TRIGGER

For:
every:
interior:
block:

decode:
current:
local:
data.

Derive:

left candidate.

Derive:

right candidate.

If:

left candidate
==
right candidate

AND:

current local data
!=
neighbor candidate,

then:

repair:
the:
local:
data
to:
the:
neighbor:
candidate

regardless:
of:
local:
Hamming:
syndrome.

Thus:

neighbor:
consensus

can:
flag:
a:
locally:
silent:
corruption.

If:

left candidate
!=
right candidate:

ABSTAIN.

METHOD 3 — HYBRID_TRIGGER

Repair if:

A.
local syndrome
!=0
AND
left == right;

OR:

B.
local syndrome
==0
AND
left == right
AND
current != left.

This is:
operationally:
equivalent:
to:
NEIGHBOR_TRIGGER
for:
repair decisions,

but:

telemetry
must:
separate:

SYNDROME-LED repairs

from:

SYNDROME-BLIND:
neighbor-led:
repairs.

Purpose:

make:
the:
mechanistic:
path
explicit.

METHOD 4 — ONE_SIDE_TRIGGER

For:
an:
interior:
block:

derive:
left:
neighbor:
candidate.

If:

current local
!=
left candidate:

repair:
to:
left candidate

regardless:
of:
syndrome.

Purpose:

negative:
confidence:
control.

METHOD 5 — DETECT_ONLY

Compute:

- local syndrome;
- left candidate;
- right candidate;
- current mismatch;
- left/right agreement.

Perform:

NO:
repair.

Purpose:

representation /
diagnostic:
control.

REPAIR ORDER

1.
inspect:
persistent:
pre-input:
local:
and:
cross:
state;

2.
perform:
allowed:
diagnosis /
repair /
abstention;

3.
decode:
logical:
48-bit:
state;

4.
apply:
current:
input;

5.
one:
logical:
MIXED5:
update;

6.
recompute:
local:
Hamming:
codewords;

7.
recompute:
neighbor:
XOR:
checks.

INPUT MAPPING

Exact:
DG-1R-05C.

Mapped blocks:

1,
3,
5,
7,
9,
11.

Primary damage blocks:

2,
6,
10.

DAMAGE FAMILIES

Harness MUST:
assert:
actual:
lesion:
cardinality.

THREE_DATA3_SILENT

Inside:
one:
primary:
damage:
block

flip:

d1,
d2,
d3

at:
Hamming:
physical:
positions:

3,
5,
6.

Actual lesion size:

3.

Frozen property:

local:
Hamming:
syndrome
=
0.

Purpose:

primary:
syndrome-blind:
repair target.

TWO_DATA2

Flip:

d1,
d2.

Actual lesion size:

2.

Purpose:

confirm:
ordinary:
neighbor reconstruction
remains:
intact.

LEFT_CHECK1_ONLY

No:
local:
data damage.

Flip:

left:
cross-check:
bit
for:
d1.

Actual lesion size:

1.

Expected:

left candidate
!=
right candidate.

Two-sided:
methods
should:
ABSTAIN.

ONE_SIDE_TRIGGER
is:
expected:
to:
risk:
false repair.

BOTH_CHECK1_CORRELATED

No:
local:
data damage.

Flip:

left:
cross-check:
bit
for:
d1

AND:

right:
cross-check:
bit
for:
d1.

Actual lesion size:

2.

This:
creates:

two:
independent:
reconstruction:
channels

that:
now:
agree
on:
the:
same:
WRONG:
d1:
value.

Purpose:

test:
the:
boundary
of:
two-source:
consensus.

This is:

CORRELATED:
INTEGRITY:
DAMAGE.

DATA3_PLUS_LEFT_CHECK1

Flip:

local:
d1,
d2,
d3

plus:

left:
cross-check:
d1.

Actual lesion size:

4.

Purpose:

test:
whether:
the:
two-sided:
method
abstains
when:

the:
block
is:
silent-corrupt

and:

one:
reconstruction:
source
is:
also:
damaged.

DISTRIBUTED_SILENT3

Simultaneously:

block 2:
d1,d2,d3.

block 10:
d1,d2,d3.

Actual lesion size:

6.

Purpose:

test:
parallel:
syndrome-blind:
diagnosis.

PRIMARY METRICS

Counterfactual:
physical
and:
logical:
divergence
at:

1,
4,
8,
16,
32.

Also:

- logical:
  divergence area;
- physical:
  divergence area;
- sustained:
  exact:
  logical:
  recovery;
- recovery time;
- repair count;
- false repair count;
- abstentions;
- syndrome-led repairs;
- syndrome-blind repairs;
- neighbor:
  agreement count;
- neighbor:
  disagreement count.

FALSE REPAIR

A:
proposed:
logical:
repair vector

is:
FALSE

if:

it:
does NOT:
match:
the:
counterfactual:
reference:
logical:
block

immediately:
before:
repair.

Repair logic:

never:
sees:
this:
evaluation:
label.

SYNDROME-BLIND REPAIR SIGNAL

TRUE
if:

on:
THREE_DATA3_SILENT:

NEIGHBOR_TRIGGER
or:
HYBRID_TRIGGER

has:

1.
median:
logical divergence
at:
h1
=
0;

2.
sustained:
exact logical recovery
>=0.90;

3.
false repair fraction
<=0.01;

4.
median:
logical divergence area
=
0.

DISTRIBUTED SELF-DIAGNOSIS SIGNAL

TRUE
if:

on:
DISTRIBUTED_SILENT3:

HYBRID_TRIGGER

has:

median:
logical divergence
at:
h4
=
0

AND:

sustained:
exact logical recovery
>=0.75.

ONE-SOURCE DAMAGE SAFETY

TRUE
if:

on:
LEFT_CHECK1_ONLY:

HYBRID_TRIGGER:

false repair count
=
0

AND:

median:
logical divergence
at:
h4
=
0.

CORRELATED-CONSENSUS FAILURE

Flag:
a:
two-sided:
method

if:

on:
BOTH_CHECK1_CORRELATED:

false repair fraction
>0.10.

This:
is:
expected
to:
bound:
the:
two-neighbor:
consensus:
model.

It tests:

whether:
two:
matching:
integrity:
channels

can:
still:
fail
under:
correlated:
damage.

PRIMARY INTERPRETATION

A:
positive:
syndrome-blind:
result
would show:

damage:
diagnosis

does NOT:
need:
to:
originate
inside:
the:
damaged:
region.

Healthy:
neighbors

can:
identify:

"your:
state
is:
inconsistent
with:
the:
state
we:
both:
independently:
expect."

A:
correlated-consensus:
failure

would:
show:

agreement:
alone
is:
not:
absolute:
proof.

The:
next:
architecture
would:
need:

- more:
  independent:
  witnesses;
- confidence:
  weighting;
- spatial:
  diversity;
- or:
  repair:
  quorum.

WORLD FAMILY

8:
worlds.

Seeds:

20260926054000
through:
20260926054007.

No:
prior:
DG-1R:
seed reuse.

NO POST-RUN TUNING

After:
the:
first:
scenario:

do not alter:

- trigger definitions;
- cross-check relations;
- damage geometry;
- damage blocks;
- thresholds;
- world family;
- metrics.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
software tissue
could:
repair:
a:
damaged:
block

if:
the:
block
knew:
it:
was:
damaged.

But:
one:
three-bit:
damage pattern
fooled:
the:
block's:
own:
check.

The:
block
thought:
it:
was:
fine.

Its:
neighbors,
however,
both:
had:
enough:
information
to:
see:

"Your:
four:
data bits
do not:
match:
what:
both:
of:
us
say:
they:
should:
be."

This:
experiment
lets:
the:
neighbors
trigger:
the:
repair.

We:
also:
damage:
the:
neighbor:
checks
themselves.

One:
bad:
neighbor
should:
cause:
disagreement
and:
make:
the:
tissue
refuse:
to:
guess.

But:
if:
both:
neighbor:
checks
are:
damaged
in:
the:
same:
way,

they:
may:
agree
on:
the:
same:
wrong:
answer.

That:
tests:
how:
far:
two-source:
consensus
can:
be:
trusted.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05D SYNDROME-BLIND NEIGHBOR DIAGNOSIS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05D:
SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05d_syndrome_blind_v1.py

Harness commit:

c0e249b58bdeaebc6a4bfab5588d343922875ca8.

Git blob SHA:

3b908ac1f6d0fe70b319174be7be9e109a8ee95b.

Source SHA-256:

58786992dbb9c7ca11e16ca9e68df0617a0abb35b8cd5e208696291c880aea91.

Source bytes:

11012.

LOCAL PRECHECK

Exact:
Git blob:
identity:

PASS.

Python:
syntax:

PASS.

No:
DG-1R-05D:
scenario
was:
executed
before:
this:
freeze.

FROZEN WORLD FAMILY

20260926054000..20260926054007.

8 worlds.

FROZEN DAMAGE FAMILIES

THREE_DATA3_SILENT.

TWO_DATA2.

LEFT_CHECK1_ONLY.

BOTH_CHECK1_CORRELATED.

DATA3_PLUS_LEFT_CHECK1.

DISTRIBUTED_SILENT3.

DG-1R-05 CANONICAL STATUS

Still:

UNSPENT.

DG-1R-05D:

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


MECHANICAL INVALIDATION 01 — ORIGINAL DG-1R-05D HARNESS

The:
first:
execution attempt

terminated:
before:
any:
result
because:

the:
physical-state:
encode()
helper

was:
shadowed
by:
the:
JSON:
encode()
helper.

Observed failure:

TypeError:
ndarray
is:
not:
JSON serializable.

This:
is:
a:
mechanical:
name-collision
defect.

No:
DG-1R-05D:
result
was:
produced.

No:
experimental:
parameter
or:
state:
transition:
semantics
are:
changed
by:
FixA.

FIXA FREEZE

Harness:

research/experiments/dg1r/harnesses/dg1r_05d_syndrome_blind_fixa_v1.py

FixA commit:

cc0d4e92d4eefce87e414fbceb8f11c086cd2cc3.

Git blob SHA:

d2bdec439f9f6d4573ddd264fbfd1fe1e5bd3f5e.

Source SHA-256:

57557eb12e025e90e59c64fb513c0dbe97028e8bab4a7db09d528cc7879161fb.

Source bytes:

11027.

Only:
semantic delta:

NONE.

Only:
implementation delta:

rename:
JSON:
serializer
from:
encode()

to:
encode_json().

Python syntax:

PASS.

All:
preregistered:
worlds,
lesions,
trigger rules,
repair rules,
thresholds,
and:
metrics

remain:
unchanged.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN PACKAGING CORRECTION 01 — REMOTE BYTE IDENTITY

DATE:
2026-09-20.

STATUS:
CORRECTED BEFORE:
THE:
FIRST:
DG-1R-05D:
SCENARIO.

The:
previous:
freeze entry

recorded:
the:
local:
pre-transfer:
source identity

including:
one:
final:
newline.

The:
GitHub:
contents transfer

stored:
the:
same:
source

without:
that:
final:
newline.

No:
Python:
token,
statement,
constant,
branch,
metric,
seed,
or:
experimental:
semantic

changed.

AUTHORITATIVE REMOTE HARNESS

research/experiments/dg1r/harnesses/dg1r_05d_syndrome_blind_v1.py

Git blob SHA:

3b908ac1f6d0fe70b319174be7be9e109a8ee95b.

Remote source SHA-256:

ab319072aca730b9d8bae4ae65e37298269ad1e5b9fb3dbe04d9c0f088597dd5.

Remote source bytes:

11011.

The:
execution copy

was:
aligned
to:
these:
exact:
remote:
bytes

before:
any:
scenario:
execution.

No:
DG-1R-05D:
scenario
was:
executed
before:
this:
correction.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN PACKAGING CORRECTION 02 — AUTHORITATIVE FIXA IDENTITY

DATE:
2026-09-20.

STATUS:
CORRECTED BEFORE:
THE:
FIRST:
DG-1R-05D:
SCENARIO.

The:
previous:
packaging correction
incorrectly:
named:
the:
mechanically invalid:
original:
harness

as:
the:
authoritative:
execution source.

That:
was:
a:
documentation:
error only.

AUTHORITATIVE EXECUTABLE

research/experiments/dg1r/harnesses/dg1r_05d_syndrome_blind_fixa_v1.py

FixA commit:

cc0d4e92d4eefce87e414fbceb8f11c086cd2cc3.

Git blob SHA:

d2bdec439f9f6d4573ddd264fbfd1fe1e5bd3f5e.

Source SHA-256:

57557eb12e025e90e59c64fb513c0dbe97028e8bab4a7db09d528cc7879161fb.

Source bytes:

11027.

The:
execution copy

matches:
the:
frozen:
FixA:
source SHA-256
and:
byte count.

The:
invalid:
original:
dg1r_05d_syndrome_blind_v1.py

must NOT:
be:
executed
or:
interpreted
as:
DG-1R-05D:
evidence.

No:
DG-1R-05D:
scenario
was:
executed
before:
this:
correction.

No:
world,
lesion,
trigger,
repair,
metric,
threshold,
or:
classification
changed.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05D NON-EVIDENCE CLOSURE — SYNDROME-BLIND DISTRIBUTED SELF-DIAGNOSIS

DATE:
2026-09-20.

STATUS:
COMPLETE /
STRONG POSITIVE SYNDROME-BLIND REPAIR /
STRONG POSITIVE DISTRIBUTED SELF-DIAGNOSIS /
ONE-SOURCE DAMAGE SAFETY PASS /
CORRELATED-CONSENSUS FAILURE CONFIRMED /
NON-CANONICAL /
NON-EVIDENCE.

FIXA HARNESS

Git blob SHA:

d2bdec439f9f6d4573ddd264fbfd1fe1e5bd3f5e.

Source SHA-256:

57557eb12e025e90e59c64fb513c0dbe97028e8bab4a7db09d528cc7879161fb.

Source bytes:

11027.

OUTPUT

RUN 1 SHA-256:

9f37eaac2ba8a98e1cbd64a06e7da5d2f5223c1e234ce5ca393c969395bc0c60.

RUN 2 SHA-256:

9f37eaac2ba8a98e1cbd64a06e7da5d2f5223c1e234ce5ca393c969395bc0c60.

Byte-identical:

PASS.

MECHANICAL VALIDITY

mechanical_valid:

TRUE.

FROZEN SIGNALS

SYNDROME_BLIND_REPAIR_SIGNAL:

TRUE.

Signal methods:

NEIGHBOR_TRIGGER.
HYBRID_TRIGGER.

DISTRIBUTED_SELF_DIAGNOSIS_SIGNAL:

TRUE.

ONE_SOURCE_DAMAGE_SAFETY:

TRUE.

CORRELATED_CONSENSUS_FAILURE_METHODS:

NEIGHBOR_TRIGGER.
HYBRID_TRIGGER.

PRIMARY SILENT-LESION RESULT

THREE_DATA3_SILENT:

local:
Hamming syndrome:

0.

SYNDROME_TRIGGER:

median:
logical divergence area:

2.2395833333333335.

sustained:
exact logical recovery:

0.2916666666666667.

repairs:

0.

NEIGHBOR_TRIGGER:

median:
logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

h1:
logical divergence:

0.

syndrome-blind repairs:

24.

false-repair fraction:

0.

HYBRID_TRIGGER:

same:
primary:
recovery result.

Thus:

healthy:
neighboring:
regions

can:
diagnose
and:
repair:

damage
that:
the:
damaged:
region's:
own:
integrity:
check

cannot:
see.

The:
damage:
signal
can:
originate
outside:
the:
damaged:
region.

DISTRIBUTED SILENT DAMAGE

DISTRIBUTED_SILENT3:

two:
separate:
blocks

each:
receive:
the:
three-bit:
syndrome-zero:
lesion.

HYBRID_TRIGGER:

median:
logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

h1:
logical divergence:

0.

syndrome-blind repairs:

16.

false-repair fraction:

0.

Thus:

distributed:
self-diagnosis

operates:
in:
parallel.

ONE BAD RECOVERY CHANNEL

LEFT_CHECK1_ONLY:

one:
left:
cross-check:
bit
is:
damaged.

HYBRID_TRIGGER:

repairs:

0.

false repairs:

0.

logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

The:
two:
neighbor:
candidates
disagree.

The:
tissue
does:
NOT:
guess.

ONE_SOURCE_DAMAGE_SAFETY:

PASS.

LOCAL DAMAGE + ONE BAD RECOVERY CHANNEL

DATA3_PLUS_LEFT_CHECK1:

the:
local:
block
has:
silent:
three-data-bit:
damage

and:

the:
left:
recovery:
channel
is:
also:
damaged.

HYBRID_TRIGGER:

repairs:

0.

median:
logical divergence area:

2.2395833333333335.

sustained:
exact logical recovery:

0.2916666666666667.

Interpretation:

two-sided:
validation

correctly:
refuses:
an:
unsafe:
repair,

but:

with:
only:
two:
witnesses,

one:
damaged:
witness
removes:
the:
quorum
needed:
for:
reconstruction.

CORRELATED TWO-WITNESS FAILURE

BOTH_CHECK1_CORRELATED:

the:
local:
data
is:
healthy.

Both:

left
and:
right:
cross-check:
bits

for:
d1

are:
flipped.

Thus:

both:
neighbor:
channels

agree
on:
the:
same:
wrong:
candidate.

HYBRID_TRIGGER:

repairs:

24.

syndrome-blind repairs:

24.

false-repair fraction:

1.0.

median:
logical divergence area:

1.9166666666666665.

sustained:
exact logical recovery:

0.4583333333333333.

NEIGHBOR_TRIGGER:

same:
false-repair:
boundary.

Thus:

TWO:
AGREEING:
WITNESSES

are:
not:
proof
when:

the:
witnesses
can:
share:
correlated:
damage.

ONE-SIDE CONTROL

ONE_SIDE_TRIGGER:

LEFT_CHECK1_ONLY:

false-repair fraction:

1.0.

DATA3_PLUS_LEFT_CHECK1:

false-repair fraction:

1.0.

This:
reconfirms:

single-source:
repair
is:
not:
sufficiently:
safe.

CORE MECHANISTIC CONCLUSION

DG-1R-05D establishes:

DAMAGE:
DIAGNOSIS

can:
be:
DISTRIBUTED.

A:
region
does NOT:
need:
to:
recognize
its:
own:
damage

if:

independent:
neighbors
can:
detect:
that:
its:
state
is:
inconsistent
with:
the:
state
they:
expect.

This:
adds:
a:
new:
architectural:
role:

EXTERNAL:
LOCAL:
WITNESSES.

However:

two:
witnesses
create:
a:
new:
failure mode:

CORRELATED:
CONSENSUS:
ERROR.

If:
both:
witness:
channels
are:
damaged
in:
the:
same:
way,

the:
tissue
can:
confidently:
repair:
healthy:
state
into:
wrong:
state.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05E —
MULTI-WITNESS:
REPAIR:
QUORUM /
CORRELATED-FAULT:
TOLERANCE AUDIT.

Same:

128-bit:
physical:
budget.

Use:

a:
smaller:
logical:
tissue

so:
each:
logical:
region

can:
have:
multiple:
spatially:
diverse:
integrity:
witnesses.

Candidate:

8:
logical:
blocks

x:
4:
data bits

=
32:
logical:
data bits.

Local:
Hamming(7,4):

56 bits.

Nearest-neighbor:
XOR:
ring:

8 edges
x:
4 bits

=
32 bits.

Second-neighbor:
XOR:
ring:

8 edges
x:
4 bits

=
32 bits.

Subtotal:

120 bits.

Remaining:

8 bits

for:
one:
integrity:
guardian /
confidence:
bit
per:
logical:
block.

Each:
block
can:
receive:
multiple:
independent:
candidate:
reconstructions

from:

- left-1;
- right-1;
- left-2;
- right-2.

Test:

3-of-4:
repair:
quorum

versus:

2-of-2:
consensus.

Primary question:

can:
spatially:
diverse:
repair:
witnesses

tolerate:

one:
or:
two:
corrupted:
integrity:
channels

without:

false:
reconstruction?

PLAIN-SPEAK SUMMARY

We:
fixed:
the:
blind spot.

The:
damaged:
block
does not:
have:
to:
know:
it:
is:
damaged.

Its:
neighbors
can:
notice:

"Your:
state
does not:
match:
what:
we:
both:
say:
it:
should:
be."

That:
repaired:
the:
previously:
invisible:
three-bit:
damage
perfectly.

It:
also:
worked:
when:
two:
different:
blocks
were:
silently:
damaged
at:
the:
same:
time.

But:
we:
found:
the:
next:
weakness.

If:
one:
neighbor:
is:
wrong,

the:
two:
neighbors
disagree

and:
the:
system
safely:
refuses:
to:
guess.

If:
both:
neighbors
are:
wrong
in:
the:
same:
way,

they:
agree
on:
the:
same:
bad:
answer.

Then:
the:
repairer
can:
damage:
a:
healthy:
block.

So:
the:
next:
step
is:
a:
repair:
quorum.

Instead:
of:
two:
witnesses,

give:
each:
region
several:
spatially:
different:
witnesses

and:
require:
a:
strong:
majority
before:
repair.

That:
costs:
more:
redundancy

and:
therefore:
more:
logical:
capacity,

but:
it:
tests:
whether:
the:
software:
tissue
can:
become:
fault-tolerant
against:
damage
to:
its:
repair:
network
itself.

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

DG-1R-05D remains:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05D NON-EVIDENCE CLOSURE — SYNDROME-BLIND NEIGHBOR DIAGNOSIS

DATE:
2026-09-20.

STATUS:
COMPLETE /
STRONG POSITIVE SYNDROME-BLIND REPAIR /
POSITIVE DISTRIBUTED SELF-DIAGNOSIS /
POSITIVE ONE-WITNESS SAFETY /
CORRELATED TWO-WITNESS FAILURE CONFIRMED /
NON-CANONICAL /
NON-EVIDENCE.

AUTHORITATIVE FIXA

research/experiments/dg1r/harnesses/dg1r_05d_syndrome_blind_fixa_v1.py

Git blob SHA:

d2bdec439f9f6d4573ddd264fbfd1fe1e5bd3f5e.

Source SHA-256:

57557eb12e025e90e59c64fb513c0dbe97028e8bab4a7db09d528cc7879161fb.

Source bytes:

11027.

REPRODUCIBILITY

RUN 1 SHA-256:

9f37eaac2ba8a98e1cbd64a06e7da5d2f5223c1e234ce5ca393c969395bc0c60.

RUN 2 SHA-256:

9f37eaac2ba8a98e1cbd64a06e7da5d2f5223c1e234ce5ca393c969395bc0c60.

Byte-identical:

PASS.

MECHANICAL VALIDITY

no-damage duplicate trajectories:

PASS.

all lesion-cardinality assertions:

PASS.

mechanical_valid:

TRUE.

FROZEN SIGNALS

SYNDROME_BLIND_REPAIR_SIGNAL:

TRUE.

Signal methods:

NEIGHBOR_TRIGGER.
HYBRID_TRIGGER.

DISTRIBUTED_SELF_DIAGNOSIS_SIGNAL:

TRUE.

ONE_SOURCE_DAMAGE_SAFETY:

TRUE.

CORRELATED_CONSENSUS_FAILURE_METHODS:

NEIGHBOR_TRIGGER.
HYBRID_TRIGGER.

PRIMARY SILENT-CORRUPTION RESULT

THREE_DATA3_SILENT:

local:
Hamming syndrome

is:

0.

Therefore:

SYNDROME_TRIGGER

cannot:
see:
the:
damage.

SYNDROME_TRIGGER:

median:
h1 logical divergence:

0.08333333333333333.

median:
logical divergence area:

2.2395833333333335.

sustained exact logical recovery:

0.2916666666666667.

No:
repair
was:
triggered.

By contrast:

NEIGHBOR_TRIGGER:

median:
h1 logical divergence:

0.

median:
h4 logical divergence:

0.

median:
h32 logical divergence:

0.

logical divergence area:

0.

sustained exact logical recovery:

1.0.

repairs:

24
across:
24 scenarios.

syndrome-blind repairs:

24.

false repairs:

0.

HYBRID_TRIGGER:

identical:
repair quality.

median:
h1 logical divergence:

0.

logical divergence area:

0.

sustained exact logical recovery:

1.0.

syndrome-blind repairs:

24.

false repairs:

0.

Thus:

healthy:
neighboring:
integrity relations

can:
diagnose
and:
repair:

a:
local:
corruption

that:
the:
damaged:
region's:
own:
Hamming:
syndrome

cannot:
detect.

TRUE TWO-DATA RECONSTRUCTION

TWO_DATA2:

NEIGHBOR_TRIGGER:

logical divergence area:

0.

sustained exact recovery:

1.0.

repairs:

24.

false repairs:

0.

HYBRID_TRIGGER:

logical divergence area:

0.

sustained exact recovery:

1.0.

repairs:

24.

false repairs:

0.

These:
repairs
were:

syndrome-led

because:

the:
local:
Hamming:
syndrome

was:
nonzero

and:

the:
two:
neighbor:
reconstruction:
channels

agreed.

DISTRIBUTED SILENT DAMAGE

DISTRIBUTED_SILENT3:

two:
simultaneously:
silent-corrupted:
blocks.

NEIGHBOR_TRIGGER:

median:
h1 logical divergence:

0.

median:
h4 logical divergence:

0.

median:
h32 logical divergence:

0.

logical divergence area:

0.

sustained exact logical recovery:

1.0.

repairs:

16
across:
8 worlds.

false repairs:

0.

HYBRID_TRIGGER:

same:
zero-divergence:
result.

Thus:

syndrome-blind:
neighbor diagnosis

operates:
in:
parallel
across:
spatially:
separate:
damaged:
regions.

ONE-WITNESS DAMAGE SAFETY

LEFT_CHECK1_ONLY:

one:
neighbor:
cross-check:
channel
is:
damaged.

HYBRID_TRIGGER:

repairs:

0.

false repairs:

0.

median:
h4 logical divergence:

0.

sustained exact logical recovery:

1.0.

The:
two:
neighbor:
candidates

disagree,

so:

the:
two-sided:
logic

does NOT:
invent:
a:
repair.

ONE_SOURCE_DAMAGE_SAFETY:

PASS.

ONE-SIDED NEGATIVE CONTROL

ONE_SIDE_TRIGGER:

LEFT_CHECK1_ONLY:

repairs:

24.

false repairs:

24.

false-repair fraction:

1.0.

median:
logical divergence area:

1.9166666666666665.

Thus:

one:
witness

is:
not:
enough.

A:
single:
corrupted:
integrity:
channel

can:
drive:
confident:
wrong:
repair.

CORRELATED TWO-WITNESS FAILURE

BOTH_CHECK1_CORRELATED:

both:
left
and:
right:
cross-check:
channels

are:
flipped
for:
the:
same:
logical:
bit.

They:
therefore:
agree

on:
the:
same:
wrong:
candidate.

NEIGHBOR_TRIGGER:

repairs:

24.

false repairs:

24.

false-repair fraction:

1.0.

median:
h1 logical divergence:

0.041666666666666664.

median:
logical divergence area:

1.9166666666666665.

sustained exact logical recovery:

0.4583333333333333.

HYBRID_TRIGGER:

same:
false-repair:
boundary.

Thus:

two-source:
agreement

is:
NOT:
absolute:
proof.

Correlated:
integrity damage

can:
manufacture:
a:
false:
consensus.

DATA PLUS ONE-WITNESS DAMAGE

DATA3_PLUS_LEFT_CHECK1:

the:
local:
block

is:
silent-corrupted

and:

one:
neighbor:
reconstruction:
channel

is:
also:
damaged.

Two-sided:
neighbor methods:

do NOT:
repair.

Median:
logical divergence area:

2.2395833333333335.

Sustained exact recovery:

0.2916666666666667.

Interpretation:

the:
system:
correctly:
refuses
to:
guess

but:

cannot:
reconstruct
without:
a:
sufficient:
quorum
of:
healthy:
witnesses.

TECHNICAL CONCLUSION

DG-1R-05D adds:

a:
fourth:
distinct:
integrity mechanism.

Previously:

1.
HOMEOSTATIC CONTAINMENT.

2.
LOCAL REDUNDANT RECONSTRUCTION.

3.
LOCAL UNCERTAINTY DETECTION.

Now:

4.
EXTERNAL:
NEIGHBOR:
DIAGNOSIS.

A:
damaged:
region

does NOT:
need:
to:
know:
that:
it:
is:
damaged.

Independent:
neighboring:
state relations

can:
detect:

"your:
state
does:
not:
match
what:
we:
both:
expect."

This:
is:
a:
strong:
software-tissue:
signal.

But:

the:
failure boundary
is:
equally:
important.

TWO:
witnesses

can:
both:
be:
wrong

in:
the:
same:
way.

Therefore:

CONSENSUS
must:
be:
treated
as:
a:
confidence:
mechanism,

not:

truth.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05E —
SPARSE:
THREE-WITNESS:
QUORUM /
CORRELATED-DAMAGE:
AUDIT.

Keep:

128:
persistent:
bits.

Keep:

48:
logical:
data bits.

Keep:

84:
local:
Hamming:
bits.

Keep:

44:
cross-integrity:
bits.

Do NOT:
add:
memory.

Rewire:

the:
same:
11:
four-bit:
cross-check:
relations

into:
a:
sparse:
graph

where:

the:
primary:
damage:
blocks:

2,
6,
10

each:
have:

three:
direct:
independent:
witness:
neighbors.

Use:

3-source:
quorum.

Primary question:

can:

2-of-3:
healthy:
witness:
agreement

repair:

- silent:
  local:
  corruption;
- silent:
  corruption:
  plus:
  one:
  bad:
  witness;

while:

correctly:
bounding:
the:
case
where:

two:
of:
three:
witnesses

are:
correlated:
wrong?

This:
tests:

FAULT-TOLERANT:
REPAIR QUORUM

under:

the:
same:
128-bit:
state budget.

PLAIN-SPEAK SUMMARY

This:
was:
a:
good:
result.

We:
damaged:
three:
data bits
in:
a:
way
that:
fooled:
the:
damaged:
block's:
own:
error check.

The:
block
thought:
it:
was:
healthy.

But:

its:
two:
neighbors

both:
had:
independent:
information
about:
what:
that:
block's:
data
should:
look:
like.

When:
both:
neighbors
agreed,

the:
system
repaired:
the:
silent:
damage
perfectly.

It:
also:
repaired:
two:
separate:
silent-damaged:
blocks
at:
the:
same:
time.

When:
only:
one:
neighbor's:
check
was:
damaged,

the:
two:
neighbors
disagreed,

so:
the:
system
refused:
to:
guess.

That:
was:
safe.

The:
failure:

if:
both:
neighbors
were:
damaged
in:
the:
same:
way,

they:
agreed
on:
the:
same:
wrong:
answer.

The:
system
then:
made:
a:
confident:
bad:
repair.

So:

two:
witnesses
are:
much:
better
than:
one,

but:
they:
are:
not:
enough
against:
correlated:
damage.

The:
next:
test
is:
three:
witnesses

inside:
the:
same:
128-bit:
budget.

Then:

one:
bad:
witness
should:
lose:
the:
vote.

That:
moves:
Yggdrasil
toward:
a:
distributed:
self-checking:
software:
tissue

where:

repair:
decisions

come:
from:
local:
quorum,

not:
a:
central:
controller.

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

DG-1R-05D remains:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
