TITLE: DG-1R-05G — Compressed Hypergraph Integrity / Multi-Region Witness Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE COMPRESSED-INTEGRITY PILOT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / REPAIR CAPACITY
BRANCH: dg1a-ar
PARENT: DG-1R-05F

RATIONALE

DG-1R-05F established:

- 48 logical bits can coexist with strong sparse integrity under a 128-bit total state budget;
- pairwise SPARSE20 uses 20 four-bit edge-check slots = 80 integrity bits;
- pairwise checks provide 40 total graph-degree / witness-incidence units;
- degree 3 tolerates one bad witness but fails under two correlated bad witnesses;
- selected degree 4 regions safely abstain under two correct versus two wrong witnesses;
- uniform degree 4 is impossible with only 20 pairwise edges.

Before adding time-multiplexed topology, DG-1R-05G tests a lower-complexity question:

CAN:
ONE:
FOUR-BIT:
INTEGRITY SLOT

WITNESS:
MORE:
THAN:
TWO:
LOGICAL:
REGIONS

WITHOUT:
ADDING:
PERSISTENT:
STATE?

A four-region XOR check:

C_abcd
=
A XOR B XOR C XOR D

can reconstruct any one member if the other three logical regions and the check are intact.

Thus:

20:
four-bit:
hyperchecks

x:
4:
incident:
logical regions

=

80:
witness-incidence units

instead of:

40

for:
20:
pairwise:
edges.

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

Logical data:

12:
blocks

x:
4 bits

=

48 bits.

Integrity:

20:
slots

x:
4 bits

=

80 bits.

Total:

128 persistent bits.

No:
hidden:
memory.

No:
task labels.

No:
external repair oracle.

REFERENCE METHOD

PAIR20_MAJORITY_48

Exact:
DG-1R-05F:
SPARSE20:
pairwise:
integrity graph.

Edges:

12-cycle.

6:
opposite-node:
matching:
edges.

2:
extra:
edges:

(0,3)
and:
(6,9).

Repair:

strict:
majority
of:
incident:
pairwise:
reconstruction candidates.

Purpose:

same-capacity:
pairwise:
reference.

HYPERGRAPH

HYPER20_MAJORITY_48.

Frozen:
20:
four-region:
hyperchecks:

(0,2,7,9)
(1,3,6,11)
(4,5,9,10)
(2,3,5,8)
(0,1,4,8)
(6,7,8,10)
(2,4,6,11)
(0,3,5,7)
(1,7,10,11)
(1,5,6,9)
(3,8,9,10)
(0,4,8,11)
(0,2,6,10)
(1,3,4,7)
(2,5,7,11)
(2,3,4,10)
(0,1,5,10)
(0,3,9,11)
(1,2,8,9)
(4,6,7,9)

Frozen properties:

logical-region degree:

block 0: 7
block 1: 7
block 2: 7
block 3: 7
block 4: 7
block 5: 6
block 6: 6
block 7: 7
block 8: 6
block 9: 7
block 10: 7
block 11: 6

Minimum degree:

6.

Maximum degree:

7.

Every:
pair:
of:
logical regions

co-occurs
in:
at most:

2:
hyperchecks.

Total:
witness incidence:

80.

HYPERCHECK ENCODING

For:
hypercheck:
H=(a,b,c,d):

stored:
four-bit:
check:

X_a
XOR:
X_b
XOR:
X_c
XOR:
X_d.

To reconstruct:
target:
b:

candidate
=
stored_check
XOR:
X_a
XOR:
X_c
XOR:
X_d.

Same:
for:
any:
member.

REPAIR RULE

For:
each:
logical:
block:

compute:
all:
incident:
candidate:
vectors.

Group:
identical:
four-bit:
candidates.

Require:

strict majority:

best_count
>
degree / 2.

If:
no:
strict:
majority:

ABSTAIN.

If:
strict:
majority
exists
and:
candidate
differs
from:
current:
logical:
block:

repair:
to:
candidate.

No:
task:
information.

No:
counterfactual:
information
is:
visible:
to:
repair logic.

METHODS

1.
PAIR20_MAJORITY_48.

2.
HYPER20_MAJORITY_48.

3.
HYPER20_UNANIMOUS_48.

Same:
hypergraph.

Repair only if:

all:
incident:
candidates
agree.

Purpose:

high-confidence:
negative /
conservative:
control.

4.
HYPER20_DETECT_ONLY.

Compute:
candidate:
groups
and:
majorities.

Perform:
no:
repair.

Purpose:

representation-only:
control.

DYNAMICS

48:
logical:
data bits

under:

one:
MIXED5:
CA update

per:
external:
input.

Exact:
DG-1R-05F:
input /
dynamics:
style.

Input-mapped:
logical:
blocks:

1,
4,
7,
10.

Pre-damage:

1024:
external:
steps.

Post-damage:

32:
steps.

Repair occurs:

before:
current:
input overwrite
and:
logical:
CA:
update.

After:
logical:
update:

all:
20:
integrity:
slots

are:
recomputed
from:
the:
new:
logical:
state.

WORLD FAMILY

8:
worlds.

Seeds:

20260926057000
through:
20260926057007.

No:
prior:
DG-1R:
seed reuse.

DAMAGE TARGETS

Degree-6 hypergraph target:

block 5.

Degree-7 hypergraph target:

block 2.

Pairwise:
reference target for:
degree-3 comparison:

block 2.

Pairwise:
reference target for:
degree-4 comparison:

block 3.

Harness MUST:
assert:

method-specific:
target degree

before:
scenario:
execution.

DAMAGE FAMILIES

LOCAL_DATA2_D6

Hypergraph:

block 5.

Flip:
logical data bits:

0,
1.

Pair reference:

block 2.

Flip:
logical data bits:

0,
1.

Purpose:

ordinary:
local:
repair.

CHECK2_CORRELATED_D6

No:
logical data:
damage.

Flip:
bit 0

in:
two:
incident:
integrity slots

for:
the:
target:
block.

Hypergraph:

degree 6:
block 5.

Pair reference:

degree 3:
block 2.

Purpose:

can:
healthy:
logical state
resist:
two:
correlated:
bad:
witnesses?

CHECK3_CORRELATED_D6

No:
logical data:
damage.

Flip:
bit 0

in:
three:
incident:
hyperchecks

for:
degree-6:
block 5.

Hypergraph only.

Expected:
3 correct
versus:
3 wrong.

Strict majority:

NONE.

Purpose:

safe:
tie /
abstention:
boundary.

CHECK4_CORRELATED_D6

No:
logical:
damage.

Flip:
bit 0
in:
four:
incident:
hyperchecks

for:
degree-6:
block 5.

Hypergraph only.

Expected:

4 wrong
versus:
2 correct.

Purpose:

frozen:
correlated:
majority:
failure:
boundary.

DATA2_PLUS_CHECK2_D6

Flip:

logical:
data:
bits:
0,
1

in:
degree-6:
target

plus:

bit 0
in:
two:
incident:
integrity:
slots.

Hypergraph:

block 5.

Pair reference:

degree-3:
block 2.

Purpose:

can:
hypergraph:
majority
reconstruct:
damaged:
local:
state

despite:
two:
bad:
integrity:
witnesses?

DATA2_PLUS_CHECK3_D7

Flip:

logical:
data:
bits:
0,
1

in:
degree-7:
target:
block 2

plus:

bit 0
in:
three:
incident:
hyperchecks.

Pair reference:

degree-4:
block 3

with:

logical:
bits:
0,
1

plus:

bit 0
in:
three:
incident:
pairwise:
checks.

Purpose:

test:
4-correct:
versus:
3-wrong:
hypergraph:
majority

against:
the:
pairwise:
degree-4:
limit.

CHECK4_CORRELATED_D7

No:
logical:
data:
damage.

Flip:
bit 0

in:
four:
incident:
hyperchecks

for:
degree-7:
block 2.

Expected:

4 wrong
versus:
3 correct.

Purpose:

degree-7:
correlated-majority:
failure:
boundary.

DISTRIBUTED_LOCAL_DATA2

Flip:
logical:
bits:
0,
1

in:

block 2
and:
block 8.

No:
integrity:
slot:
damage.

Purpose:

parallel:
repair.

LESION ASSERTIONS

Every:
scenario

must:
assert:

- exact:
  logical-data:
  flip count;
- exact:
  integrity-bit:
  flip count;
- unique:
  physical:
  lesion:
  positions;
- no:
  lesion:
  position
  overlaps:
  an:
  input-mapped:
  physical:
  logical:
  bit.

COUNTERFACTUAL METRICS

At:
horizons:

1,
4,
8,
16,
32:

- logical divergence;
- physical divergence;
- exact logical match.

Also:

- logical divergence area;
- physical divergence area;
- sustained exact logical recovery;
- logical recovery time;
- repairs;
- false repairs;
- abstentions;
- candidate-group size;
- winning-vote count.

FALSE REPAIR

A:
proposed:
logical:
repair

is:
FALSE

if:

the:
proposal

does NOT:
match:

the:
undamaged:
counterfactual:
logical:
block

immediately:
before:
repair.

Repair logic:

never:
sees:
this:
label.

PRIMARY SIGNALS

HYPERGRAPH_CAPACITY_SIGNAL

TRUE
if:

HYPER20_MAJORITY_48

on:
DATA2_PLUS_CHECK2_D6:

1.
median:
logical divergence
at:
h1
=
0;

2.
logical divergence area median
=
0;

3.
sustained exact logical recovery
>=0.90;

4.
false repair fraction
<=0.01;

AND:

PAIR20_MAJORITY_48

fails:
at least:
one:
of:
those:
criteria

on:
its:
paired:
degree-3:
scenario.

THREE-WITNESS-TOLERANCE SIGNAL

TRUE
if:

HYPER20_MAJORITY_48

on:
DATA2_PLUS_CHECK3_D7:

median:
logical divergence
at:
h1
=
0

AND:

sustained:
exact:
logical:
recovery
>=0.90

AND:

false repair fraction
<=0.01.

TIE-SAFETY SIGNAL

TRUE
if:

HYPER20_MAJORITY_48

on:
CHECK3_CORRELATED_D6:

repairs
=
0

AND:

false repairs
=
0

AND:

median:
logical divergence
at:
h4
=
0.

CORRELATED-FAULT BOUNDARY

Expected:

CHECK4_CORRELATED_D6

and/or:

CHECK4_CORRELATED_D7

may:
create:
a:
wrong:
strict:
majority.

Report:

false-repair:
fraction

and:
logical:
divergence.

No:
positive:
safety:
claim
may:
be:
made
if:
the:
frozen:
result:
fails.

DISTRIBUTED HYPERGRAPH REPAIR SIGNAL

TRUE
if:

DISTRIBUTED_LOCAL_DATA2:

median:
logical divergence
at:
h4
=
0

AND:

sustained:
exact:
logical:
recovery
>=0.90

AND:

false repair fraction
<=0.01.

COMPRESSION ADVANTAGE

TRUE
if:

HYPER20_MAJORITY_48

shows:

HYPERGRAPH_CAPACITY_SIGNAL
=
TRUE

while:

using:

48:
logical bits.

80:
integrity bits.

128:
total:
persistent bits.

Same:
as:
PAIR20_MAJORITY_48.

IMPORTANT

A:
positive:
result

would NOT:
mean:

hypergraph:
majority
is:
the:
final:
Yggdrasil:
repair:
architecture.

It would show:

PAIRWISE:
INTEGRITY

is:
not:
the:
most:
capacity-efficient:
use

of:
the:
80:
integrity:
bits.

One:
integrity:
cell group

can:
serve:
multiple:
regions

simultaneously.

This:
is:
closer:
to:

compressed:
tissue-wide:
consistency

than:
isolated:
backup:
links.

RELATION TO TIME-MULTIPLEXING

DG-1R-05F proposed:

time-multiplexed:
integrity.

DG-1R-05G deliberately:
tests:
compressed:
static:
integrity
first

because:

if:
the:
same:
persistent:
80:
integrity bits

can:
provide:
substantially:
more:
simultaneous:
witness:
coverage

through:
higher-order:
checks,

then:

temporal:
rotation
may:
not:
be:
the:
next:
necessary:
complexity.

If:
hypergraph:
compression
still:
hits:
an:
insufficient:
correlated-fault:
boundary,

time /
adaptation
remains:
the:
next:
resource axis.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-05G:
scenario:

do not alter:

- hyperedge set;
- pair reference;
- target blocks;
- repair rule;
- lesion geometry;
- thresholds;
- world family;
- metrics.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
experiment
used:
80:
backup:
bits

as:
20:
links
between:
pairs:
of:
regions.

That:
means:
each:
backup:
link
helped:
two:
regions.

But:
one:
XOR:
check
does not:
have:
to:
cover:
only:
two:
regions.

This:
test
lets:
one:
backup:
slot
tie:
four:
regions
together.

Any:
one:
of:
those:
four
can:
be:
reconstructed

if:
the:
other:
three
and:
the:
check
are:
healthy.

So:

without:
adding:
a:
single:
persistent:
bit,

we:
double:
the:
total:
number:
of:
region-to-check:
relationships

from:
40
to:
80.

If:
that:
lets:
a:
region
survive:

two
or:
three:
bad:
witnesses

where:
the:
pairwise:
network
could not,

we:
learn:
that:
the:
important:
resource
is:
not:
just:
how:
many:
backup:
bits
we:
have.

It:
is:
how:
much:
independent:
integrity:
information
each:
backup:
bit
carries.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05G COMPRESSED HYPERGRAPH INTEGRITY

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05G:
WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05g_hypergraph_integrity_v1.py

Harness commit:

21d593e97b12c1eb4cabbd1433b41f85e263d602.

Git blob SHA:

54777d7cbde8549039e72e8b2bc96d09870b6d36.

Remote source SHA-256:

e59b7bc4989f79af8d10d6dabef7e9630df31f070b8af9c749938a91251bded5.

Remote source bytes:

12441.

LOCAL PRECHECK

Python syntax:

PASS.

Hypergraph degree vector:

7,7,7,7,7,6,6,7,6,7,7,6.

Minimum degree:

6.

Maximum degree:

7.

Maximum pair co-occurrence:

2.

PAIR20 reference degrees:

block 2:

3.

block 3:

4.

Lesion:
cardinality /
uniqueness /
input-overlap:
prechecks:

PASS.

No:
DG-1R-05G:
experimental:
world

was:
executed
before:
this:
freeze.

PACKAGING NOTE

The:
local:
pre-transfer:
source

contained:
one:
final:
newline.

GitHub:
stored:
the:
same:
Python:
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
seed,
method,
metric,
or:
experimental:
semantic

changed.

The:
execution copy
was:
aligned
to:
the:
authoritative:
remote:
bytes

before:
execution.

FROZEN WORLD FAMILY

20260926057000..20260926057007.

8 worlds.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

DG-1R-05G:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05G NON-EVIDENCE CLOSURE — COMPRESSED HYPERGRAPH INTEGRITY

DATE:
2026-09-20.

STATUS:
COMPLETE /
STRONG POSITIVE LOCAL CAPACITY RESULT /
POSITIVE TWO-AND-THREE-BAD-WITNESS TOLERANCE /
SAFE TIE ABSTENTION /
NEGATIVE DISTRIBUTED-DATA RESULT /
CORRELATED-MAJORITY BOUNDARY CONFIRMED /
NON-CANONICAL /
NON-EVIDENCE.

FROZEN HARNESS

Git blob SHA:

54777d7cbde8549039e72e8b2bc96d09870b6d36.

Source SHA-256:

e59b7bc4989f79af8d10d6dabef7e9630df31f070b8af9c749938a91251bded5.

Source bytes:

12441.

OUTPUT

RUN 1 SHA-256:

5a8cc9d89aba799fae0b26d459ba9da28540d07b2c84103e076d7ba4b4a3a150.

RUN 2 SHA-256:

5a8cc9d89aba799fae0b26d459ba9da28540d07b2c84103e076d7ba4b4a3a150.

Byte-identical:

PASS.

MECHANICAL VALIDITY

mechanical_valid:

TRUE.

FROZEN SIGNALS

HYPERGRAPH_CAPACITY_SIGNAL:

TRUE.

THREE_WITNESS_TOLERANCE_SIGNAL:

TRUE.

TIE_SAFETY_SIGNAL:

TRUE.

DISTRIBUTED_HYPERGRAPH_REPAIR_SIGNAL:

FALSE.

COMPRESSION_ADVANTAGE:

TRUE.

CORRELATED_FAULT_BOUNDARY_FAMILIES:

CHECK4_CORRELATED_D6.
CHECK4_CORRELATED_D7.

CAPACITY

PAIR20:

48 logical bits.

80 integrity bits.

128 total bits.

40 total witness-incidence units.

HYPER20:

48 logical bits.

80 integrity bits.

128 total bits.

80 total witness-incidence units.

Minimum region degree:

6.

Maximum region degree:

7.

Thus:

the:
same:
80:
integrity bits

double:

simultaneous:
region-to-check:
coverage.

LOCAL DATA REPAIR

HYPER20_MAJORITY_48:

LOCAL_DATA2_D6:

median:
logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

false repairs:

0.

Thus:

ordinary:
local:
data damage

remains:
exactly:
repairable.

TWO BAD WITNESSES PLUS DATA DAMAGE

DATA2_PLUS_CHECK2_D6.

HYPER20:

median:
h1 logical divergence:

0.

median:
logical divergence area:

0.

sustained exact logical recovery:

1.0.

repairs:

8.

false repairs:

0.

PAIR20 degree-3 reference:

median:
h1 logical divergence:

0.020833333333333332.

median:
logical divergence area:

2.666666666666667.

sustained exact recovery:

0.25.

repairs:

8.

false repairs:

8.

false-repair fraction:

1.0.

Thus:

compressed:
four-region:
checks

convert:

the:
same:
80-bit:
integrity budget

from:

degree-3:
pairwise:
failure

to:

exact:
repair
under:
two:
bad:
integrity witnesses.

HYPERGRAPH_CAPACITY_SIGNAL:

PASS.

THREE BAD WITNESSES PLUS DATA DAMAGE

DATA2_PLUS_CHECK3_D7.

HYPER20:

7:
incident:
witnesses.

4:
healthy.

3:
corrupted.

median:
h1 logical divergence:

0.

logical divergence area:

0.

sustained exact logical recovery:

1.0.

false repairs:

0.

THREE_WITNESS_TOLERANCE_SIGNAL:

PASS.

Thus:

degree-7:
hypergraph majority

tolerates:

three:
corrupted:
integrity witnesses

while:
still:
reconstructing:
the:
damaged:
local:
state.

SAFE TIE

CHECK3_CORRELATED_D6.

No:
logical:
data damage.

3:
correct:
candidates.

3:
wrong:
candidates.

Strict majority:

NONE.

Observed:

repairs:

0.

false repairs:

0.

median:
logical divergence area:

0.

sustained exact logical recovery:

1.0.

TIE_SAFETY_SIGNAL:

PASS.

Thus:

the:
repair system

correctly:
refuses:
to:
invent:
a:
repair

when:

evidence
is:
exactly:
split.

CORRELATED MAJORITY BOUNDARY

CHECK4_CORRELATED_D6.

4:
wrong:
witnesses.

2:
correct:
witnesses.

Observed:

repairs:

8.

false repairs:

8.

false-repair fraction:

1.0.

median:
logical divergence area:

3.041666666666667.

CHECK4_CORRELATED_D7.

4:
wrong.

3:
correct.

Observed:

repairs:

8.

false repairs:

8.

false-repair fraction:

1.0.

median:
logical divergence area:

2.666666666666667.

Thus:

hypergraph compression
does NOT:
remove:
the:
fundamental:
majority:
boundary.

A:
wrong:
strict:
majority

still:
drives:
confident:
misrepair.

DISTRIBUTED LOCAL DATA DAMAGE — NEGATIVE RESULT

DISTRIBUTED_LOCAL_DATA2.

Damaged:
logical:
blocks:

2
and:
8.

No:
integrity:
slot:
damage.

PAIR20 reference:

median:
logical divergence area:

0.

sustained exact logical recovery:

1.0.

repairs:

16.

false repairs:

0.

HYPER20:

median:
h1 logical divergence:

0.20833333333333334.

median:
h4 logical divergence:

0.22916666666666669.

median:
h32 logical divergence:

0.27083333333333337.

median:
logical divergence area:

9.583333333333332.

sustained exact logical recovery:

0.

repairs:

16.

false repairs:

16.

false-repair fraction:

1.0.

DISTRIBUTED_HYPERGRAPH_REPAIR_SIGNAL:

FAIL.

WHY THIS HAPPENS

A:
pairwise:
check

couples:
two:
regions.

A:
four-region:
hypercheck

couples:
four:
regions.

That:
compression
creates:
more:
witness:
coverage,

but:

a:
damaged:
logical:
region

also:
contaminates:

candidate:
reconstructions

for:
every:
other:
region
sharing:
its:
hyperchecks.

Under:
multiple:
simultaneous:
logical:
lesions,

healthy:
regions

can:
receive:

multiple:
mutually:
correlated:
wrong:
candidates.

In:
the:
frozen:
two-region:
damage case,

this:
was:
strong:
enough

to:
create:
wrong:
majorities

and:
secondary:
false:
repairs.

Thus:

HYPERGRAPH:
COMPRESSION

trades:

MORE:
LOCAL:
FAULT:
TOLERANCE

for:

LESS:
FAULT:
ISOLATION.

This:
is:
the:
central:
DG-1R-05G:
result.

UNANIMOUS CONTROL

HYPER20_UNANIMOUS_48

avoids:
false:
majority:
repair,

but:

DATA2_PLUS_CHECK2_D6:

repairs:

0.

median:
logical divergence area:

3.677083333333333.

sustained exact logical recovery:

0.

Thus:

requiring:
complete:
agreement

is:
too:
conservative.

DETECT-ONLY CONTROL

HYPER20_DETECT_ONLY

does NOT:
recover:
ordinary:
local:
data damage.

LOCAL_DATA2_D6:

median:
logical divergence area:

3.677083333333333.

sustained exact logical recovery:

0.

Thus:

the:
positive:
local:
result

comes:
from:
active:
reconstruction,

not:
merely:
from:
the:
hypergraph:
representation.

TECHNICAL CONCLUSION

DG-1R-05G establishes:

INTEGRITY:
INFORMATION:
DENSITY

can:
be:
increased

without:

adding:
persistent:
bits.

One:
four-bit:
hypercheck

can:
simultaneously:
support:

four:
logical:
regions.

This:
substantially:
raises:
local:
witness:
fault tolerance.

However:

higher-order:
checks

create:
shared:
failure:
domains.

The:
repair problem
now:
requires:

FAULT:
LOCALIZATION

before:

MAJORITY:
RECONSTRUCTION.

A:
candidate:
should NOT:
be:
trusted
simply:
because:
many:
checks
agree

if:

those:
checks
share:
the:
same:
damaged:
logical:
contributors.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05H —
HYPERGRAPH:
SYNDROME /
FAULT-LOCALIZATION:
AUDIT.

Keep:

48:
logical bits.

80:
integrity bits.

128:
total:
persistent bits.

Keep:

the:
same:
20:
four-region:
hyperchecks.

Do NOT:
change:
the:
representation.

Compare:

1.
NAIVE_MAJORITY:
the:
DG-1R-05G:
reference.

2.
MINIMUM-WEIGHT:
SYNDROME:
DECODER:
information-content:
upper-bound.

Per:
logical:
bit plane,

treat:

12:
logical:
data bits

plus:

20:
stored:
check bits

as:

32:
possible:
fault:
locations.

Use:

the:
20:
hypercheck:
syndromes

to:
search:
the:
lowest-weight:
fault pattern

up:
to:
a:
frozen:
small:
weight:
bound.

Repair only if:

the:
minimum-weight:
explanation

is:

UNIQUE.

Purpose:

ask:
whether:
the:
same:
stored:
integrity:
state

contains:
enough:
information

to:
localize:
distributed:
faults,

even:
though:
naive:
majority
cannot.

3.
ITERATIVE:
SYNDROME:
BIT-FLIP:
decoder.

Purpose:

test:
a:
more:
local /
distributed:
approximation

to:
the:
minimum-weight:
upper bound.

Primary question:

is:
DG-1R-05G's:
distributed:
failure

a:
REPRESENTATION:
LIMIT

or:

a:
DECODER:
LIMIT?

If:

minimum-weight:
decoding
also:
fails:

the:
hypergraph:
does NOT:
contain:
enough:
independent:
information.

If:

minimum-weight:
decoding
succeeds:

but:
iterative:
local:
decoding
fails:

the:
information
exists,

but:

Yggdrasil
needs:
a:
better:
local:
inference:
mechanism.

If:

both:
succeed:

the:
next:
step

is:
developmental:
learning
of:
repair:
message-passing
rather:
than:
more:
redundancy.

PLAIN-SPEAK SUMMARY

We:
found:
a:
real:
win

and:
a:
new:
problem.

By:
making:
each:
backup:
check
cover:
four:
regions
instead:
of:
two,

we:
made:
each:
backup:
bit
work:
harder.

A:
region
could:
survive:

two:
bad:
witnesses

and:
even:
three:
bad:
witnesses

without:
adding:
any:
memory.

That:
is:
a:
big:
efficiency:
gain.

But:

when:
two:
actual:
data:
regions

were:
damaged
at:
the:
same:
time,

their:
errors
leaked:
through:
the:
shared:
hyperchecks

and:
made:
healthy:
regions
look:
wrong.

The:
system
then:
started:
repairing:
healthy:
cells
into:
bad:
states.

So:

more:
connected:
backup:
information

is:
powerful,

but:
also:
more:
contagious.

The:
next:
question
is:

can:
the:
organism
figure:
out:

WHERE:
THE:
DAMAGE:
ACTUALLY:
IS

before:
it:
starts:
repairing?

If:
yes,

we:
may:
keep:
the:
hypergraph's:
high:
efficiency

without:
its:
distributed:
damage:
cascade.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

DG-1R-05G remains:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
